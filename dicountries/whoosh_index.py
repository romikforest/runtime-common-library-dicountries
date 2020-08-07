"""Whoosh based country search index"""

import asyncio
import logging
import os
import threading
from datetime import datetime

import pytz
from fuzzywuzzy import fuzz
from unidecode import unidecode
from whoosh import index
from whoosh.analysis import StandardAnalyzer
from whoosh.fields import (
    STORED,
    TEXT,
    Schema
)
from whoosh.filedb.filestore import (
    FileStorage,
    RamStorage,
    copy_storage
)
from whoosh.index import (
    EmptyIndexError,
    FileIndex
)
from whoosh.qparser import (
    QueryParser,
    syntax
)
from whoosh.query import FuzzyTerm

from .loader import (
    create_basename_by_name_super_index,
    load_post_process_country_mapping
)
from .utils import reorder_name

logger = logging.getLogger('dicountries')
logging.basicConfig(format='%(levelname)s  dicountries: %(message)s')

COUNTRY_IX_VER = 1  # change this if you've changed the index schema
# , so old index will not be loaded in the k8s pod
DEFAULT_MAX_SEARCH_CACHE = 1000  # Max size of the country cache.

OrGroup = syntax.OrGroup.factory(0.9)


def _clean_name(name):
    """Preprocess names before indexing

    Args:
        name (str): name to preprocess

    Returns:
        str: preprocessed name

    """
    return unidecode(name or '').strip().replace('(', ' ').replace(')', ' ')


def _clean_name2(name):
    """Preprocess names before additional sorting

    Args:
        name (str): name to preprocess

    Returns:
        str: preprocessed name

    """
    return unidecode(name or '').strip().replace('(', ' ').replace(')', ' ')


class CountryIndex:  # pylint: disable=too-many-instance-attributes
    """
    Country index class.
    Can be used to index ISO and synonyms country databases and normalize/refine countries
    (to not use synonym country names or country names with typo in data analysis).
    Indexing can be done simultaneously with country name normalizing

    Args:
            index_path: path to save index. Default is f'indexes/countries_{COUNTRY_IX_VER}'.
                Is used to load index on startup which is saved every time it is rebuilt.
                The inmemory copy of the index is used for normalizing and refining.
                The on disk index allows to start normalize names immediately on
                application startup. If index exists it will be rebuilt by
                calling `refresh` method explicitly
            post_process_country_map: a map to postprocess normalized names (None or empty map
                if no postprocessing required)
            use_async (bool): use asyncio and threads to search and index simultaneously
            max_search_cache: max search cache size. If `max_search_cache` is reached the cache
                will be cleared and reinitialized

    Attributes:
        post_process_country_map: mapping to postprocess country names or None
        simple_index_lock (threading.Lock): lock object for the `simple_index` attribute
        simple_index: mapping based on source country iso and synonym databases for direct search
            (without fuzzy search)
        ix_lock (threading.Lock): lock object for the `ix` attribute
        ix: whoosh index
        version: class version (determines backup format)
        path: backup path, default: f'indexes/countries_{COUNTRY_IX_VER}'
        last_update_lock (threading.Lock): lock object for the `last_update` attribute
        last_update: last update time
        update_lock (threading.Lock): lock object for the index refreshing
        search_cache: mapping for the country searching cache (not saved to disk)
        max_search_cache (int): max search cache size. If cache riches this size it will be
            reinitialized.
    """

    schema = Schema(decoded_country=TEXT(phrase=False,
                                         analyzer=StandardAnalyzer(
                                             stoplist=frozenset(
                                                 ['and', 'is', 'it', 'an', 'as', 'at', 'have', 'in',
                                                  'yet', 'if',
                                                  'from', 'for', 'when', 'by', 'to', 'you', 'be',
                                                  'we', 'that', 'may',
                                                  'not', 'with', 'tbd', 'a', 'on', 'your', 'this',
                                                  'of', 'will',
                                                  'can', 'the', 'or', 'are']))),
                    country=STORED(),
                    basecountry=STORED(),
                    )
    """whoosh search schema"""

    class CountryTermClass(FuzzyTerm):
        """Class controls number of typo mistakes as dependency on the term length

        Args:
                fieldname: a name of the field the score will be calculated for
                text: the content of the `fieldname`
                boost: boost factor
                maxdist: the max levenshtein distance for the term
                prefixlength: the unchangeable prefix length
                constantscore (bool): use constant score
        """

        def __init__(self,  # pylint: disable=too-many-arguments
                     fieldname,
                     text,
                     boost=1.0,
                     maxdist=2,
                     prefixlength=0,
                     constantscore=False):
            maxdist = 3
            if len(text) < 4:
                maxdist = 0
            elif len(text) < 11:
                maxdist = 1
            elif len(text) < 16:
                maxdist = 2

            super().__init__(fieldname, text, boost, maxdist, prefixlength, constantscore)

    def __init__(self, index_path=None, post_process_country_map=None, use_async=False,
                 max_search_cache=DEFAULT_MAX_SEARCH_CACHE):
        if post_process_country_map is None:
            self.post_process_country_map = load_post_process_country_mapping()
        else:
            self.post_process_country_map = post_process_country_map
        self.simple_index_lock = threading.Lock()
        self.simple_index = None
        self.ix_lock = threading.Lock()
        self.ix = None
        self.version = COUNTRY_IX_VER
        if not index_path:
            self.path = f'indexes/countries_{COUNTRY_IX_VER}'
        else:
            self.path = index_path
        self.last_update_lock = threading.Lock()
        self.last_update = None
        self.update_lock = threading.Lock()
        self.search_cache = {}
        self.max_search_cache = max_search_cache

        if use_async:
            asyncio.get_event_loop().run_in_executor(None, self.restore_backuped_index)
        else:
            self.restore_backuped_index()
        if not self.ix:
            if use_async:
                asyncio.get_event_loop().run_in_executor(None, self.refresh)
            else:
                self.refresh()

    def post_process_name(self, name, postprocess=True):
        """Postprocess names after whoosh searching.

        Example:
            Names, normalized accordingly ISO standard names can be transformed accordingly to
            some mapping to have more beautiful names for some countries as di team desires
            The postprocessing actually is done if the `postprocess` flag is True

        Args:
            name (str): name to postprocess
            postprocess: flag showing if postprocessing should be really applied

        Returns:
            str: postprocessed or unchanged `name` value depending on the `postprocess` value

        """
        if not postprocess:
            return name
        if name in self.post_process_country_map:
            return self.post_process_country_map[name]
        return name

    def get_backup_path(self):
        """Get backup path where index is saved on disk

        Returns:
            str: backup path

        """
        return self.path

    def get_index(self):
        """Get whoosh index (thread safe)

        Returns:
            whoosh index

        """
        with self.ix_lock:
            return self.ix

    def create_whoosh_ram_index(self):
        """Create inmemory whoosh index

        Returns:
            Empty inmemory whoosh index

        """

        storage = RamStorage()
        return FileIndex.create(storage, self.schema, 'MAIN')

    def backup_index(self):
        """Backup whoosh index in on disk file"""
        os.makedirs(self.path, exist_ok=True)
        with self.ix_lock:
            if self.ix:
                with FileStorage(self.path) as file_storage:
                    copy_storage(self.ix.storage, file_storage)

    async def restore_backuped_index_async(self):
        """Restore whoosh index from a file on disk to memory. Asynchronous version."""
        asyncio.get_event_loop().run_in_executor(None, self.restore_backuped_index)

    def restore_backuped_index(self):
        """Restore whoosh index from a file on disk to memory. Synchronous version."""
        with self.simple_index_lock:
            if not self.simple_index:
                self.simple_index = create_basename_by_name_super_index()
        os.makedirs(self.path, exist_ok=True)
        try:
            saved_ix = index.open_dir(self.path)
        except EmptyIndexError:
            return
        cur_ix = self.create_whoosh_ram_index()
        copy_storage(saved_ix.storage, cur_ix.storage)
        with self.ix_lock:
            self.ix = cur_ix

    def refresh(self, update_datetime=None):
        """Refresh whoosh country index. Synchronous version.

        Args:
            update_datetime (datetime): last refresh time to control if a new refresh is required

        """
        self._refresh(update_datetime=update_datetime)

    async def refresh_async(self, update_datetime=None):
        """Refresh whoosh country index. Asynchronous version.

        Args:
            update_datetime (datetime): last refresh time to control if a new refresh is required

        """
        asyncio.get_event_loop().run_in_executor(None, self._refresh, update_datetime)

    def _refresh(self, update_datetime=None):
        """Refresh whoosh index. Internal implementation.

        Args:
            update_datetime (datetime): last refresh time to control if a new refresh is required

        """

        with self.update_lock:
            if update_datetime:
                with self.last_update_lock:
                    if self.last_update and self.last_update > update_datetime:
                        # logger.info(f'No need to update countries. '
                        # f'Index updated on {self.last_update}.')
                        return
            logger.info('* Updating indices for countries...')

            logger.info('* Load countries information...')
            data = create_basename_by_name_super_index()
            with self.simple_index_lock:
                self.simple_index = data

            logger.info('* Parse countries information...')
            new_ix = self.create_whoosh_ram_index()
            writer = new_ix.writer()

            for k, v in data.items():
                mapped_data = {}
                mapped_data['country'] = k
                mapped_data['decoded_country'] = _clean_name(k)
                mapped_data['basecountry'] = v
                writer.add_document(**mapped_data)

            logger.info('* Save countries information...')
            writer.commit()

            with self.ix_lock:
                self.ix = new_ix

            self.backup_index()

            with self.last_update_lock:
                self.last_update = datetime.utcnow().replace(tzinfo=pytz.timezone('utc'))

    def normalize_country_detailed(self, name, limit=None):
        """Detailed country normalization.
        Return whoosh index possible variants for the name and their rates

        Args:
            name (str): country name to normalize
            limit: How many results should be searched (None to find all possible results)

        Raises:
            RuntimeError: if it is called during the reindexation process

        Note:
            The result scoring can be very bad if the `limit` value differ from `None`

        """
        cur_ix = self.get_index()
        if not cur_ix:
            raise RuntimeError('Reindexation proccess')

        country = _clean_name(name)
        query = ''
        if country:
            query += f' decoded_country:({country})'
        query = query.strip()
        # logger.debug(f'query: {query}')
        if not query:
            return 0, []

        with cur_ix.searcher() as s:
            qp = QueryParser('decoded_country', schema=self.schema, termclass=self.CountryTermClass)
            q = qp.parse(query)
            results = s.search(q, limit=None)
            if not results:
                qp = QueryParser('decoded_country', schema=self.schema,
                                 termclass=self.CountryTermClass,
                                 group=OrGroup)
                q = qp.parse(query)
                results = s.search(q, limit=None)
            results = [dict(basecountry=hit['basecountry'],
                            country=hit['country'],
                            # rate=hit.score,
                            rate=fuzz.token_sort_ratio(
                                _clean_name2(name),
                                _clean_name2(hit['country'])
                            )  # rate=hit.score
                            ) for hit in results]
            results = sorted(results, key=lambda k: k['rate'], reverse=True)
            results_len = len(results)
            try:
                limit = int(limit)
            except (ValueError, TypeError):
                limit = None
            if limit:
                results = results[:limit]
            return results_len, results

    def normalize_country(self, name, postprocess=True):
        """Country name normalization.

        Only the variant with max rate will be returned.

        If `postprocess` is True additional name postprocessing will be done.
        E.g. ISO name mapping to more desired by di team names

        Args:
            name (str): name to normalize
            postprocess: flag showing if postprocessing should be applied

        Returns:
            str: normalized and possibly postprocessed country name

        """

        name = name.strip()
        with self.simple_index_lock:
            if self.simple_index:
                if name in self.simple_index:
                    return self.post_process_name(self.simple_index[name], postprocess)
                if name.capitalize() in self.simple_index:
                    return self.post_process_name(self.simple_index[name.capitalize()], postprocess)
        logger.info('! Use whoosh index for %s', name)
        if name in self.search_cache:
            result = self.search_cache[name]
        else:
            result = self.normalize_country_detailed(name)
            if not result[0]:
                logger.info('! missed %s', name)
                result = self.post_process_name(name, postprocess)
            else:
                result = result[1][0].get('basecountry')
                result = self.post_process_name(result or name, postprocess)
            if len(self.search_cache) > self.max_search_cache:
                self.search_cache = {}  # Reinit cache to protect memory (atacks?)
            self.search_cache[name] = result
        return result

    def refine_country(self, name):
        """Country name normalization.

        Additional name refining will be done comparing with simple `normalize` version
        (using reorder_name function from the `country.utils` module).

        Example:
            If the normalized name is "Korea, Republic of" the return value
            will be "Republic of Korea".
            Only the variant with max rate will be returned.

            If `postprocess` is True additional name postprocessing will be done.
            E.g. ISO name mapping to more desired by di team names

        Args:
            name (str): Name to normalize and refine

        """

        name = self.normalize_country(name, postprocess=False)
        if name in self.post_process_country_map:
            return self.post_process_country_map[name]
        return reorder_name(name)
