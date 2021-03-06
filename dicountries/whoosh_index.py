"""Whoosh based country search index."""

import asyncio
import logging
import os
import threading
from datetime import datetime
from typing import Any, List, Optional, Tuple, cast

import pytz
import whoosh
from fuzzywuzzy import fuzz
from unidecode import unidecode
from whoosh.analysis import StandardAnalyzer
from whoosh.fields import STORED, TEXT, Schema
from whoosh.filedb.filestore import FileStorage, RamStorage, copy_storage
from whoosh.index import EmptyIndexError, FileIndex
from whoosh.qparser import QueryParser, syntax
from whoosh.query import FuzzyTerm

from .base_types import StringMap
from .loader import create_basename_by_name_super_index, load_post_process_country_mapping
from .utils import reorder_name

logger = logging.getLogger('dicountries')
logging.basicConfig(format='%(levelname)s  dicountries: %(message)s')

COUNTRY_IX_VER = 1  # change this if you've changed the index schema,
# so old index will not be loaded in the Kubernetes pod

DEFAULT_MAX_SEARCH_CACHE = 1000  # Max size of the country cache.

OrGroup = syntax.OrGroup.factory(0.9)


def _clean_name(name: str) -> str:
    """Preprocess names before indexing.

    Args:
        name: name to preprocess

    Returns:
        preprocessed name

    """
    return unidecode(name or '').strip().replace('(', ' ').replace(')', ' ')


def _clean_name2(name: str) -> str:
    """Preprocess names before additional sorting.

    Args:
        name: name to preprocess

    Returns:
        preprocessed name

    """
    return unidecode(name or '').strip().replace('(', ' ').replace(')', ' ')


class CountryIndex:  # pylint: disable=too-many-instance-attributes
    """Country index class.

    Can be used to index ISO and synonyms country databases and normalize/refine countries
    (to not use synonym country names or country names with typo in data analysis).
    Indexing can be done simultaneously with country name normalizing.

    Args:
            index_path: path to save index. Default is **f'indexes/countries_{COUNTRY_IX_VER}'**.
                Is used to load index on startup which is saved every time it is rebuilt.
                The inmemory copy of the index is used for normalizing and refining.
                The on disk index allows to start normalize names immediately on
                app startup. If index exists it will be rebuilt by
                calling the :py:meth:`refresh` method explicitly
            post_process_country_map: a mapping to postprocess normalized names (None or empty map
                if no postprocessing required)
            use_async: use asyncio and threads to search and index simultaneously
            max_search_cache: max search cache size. If ``max_search_cache`` is reached the cache
                will be cleared and reinitialized

    Usage example::

        from dicountries.whoosh_index import CountryIndex

        country_index = CountryIndex()
        country_index.refresh()

        print(country_index.normalize_country('Russia'))
        print(country_index.normalize_country('Korea, Republic of'))
        print(country_index.refine_country('Korea, Republic of'))

    """

    #: A mapping to postprocess country names or None.
    post_process_country_map: StringMap

    #: threading.Lock: Lock object for the :py:attr:`simple_index` attribute.
    simple_index_lock: threading.Lock

    #: mapping based on source country iso and synonym databases
    #: for direct search (without fuzzy search).
    simple_index: Optional[StringMap]

    #: threading.Lock: lock object for the :py:attr:`ix` attribute.
    ix_lock: threading.Lock

    #: whoosh index.
    ix: whoosh.index.Index

    #: class version (determines backup format).
    version: int

    #: str: backup path (default **f'indexes/countries_{COUNTRY_IX_VER}'**).
    path: str

    #: threading.Lock: lock object for the :py:attr:`last_update` attribute.
    last_update_lock: threading.Lock

    #: last update time.
    last_update: Optional[datetime]

    #: threading.Lock: lock object for the index refreshing.
    update_lock: threading.Lock

    #: mapping for the country searching cache (not saved to disk).
    search_cache: StringMap

    #: max search cache size. If cache reaches this size it will is reinitialized.
    max_search_cache: int

    def __init__(
        self,
        index_path: Optional[str] = None,
        post_process_country_map: Optional[StringMap] = None,
        use_async: bool = False,
        max_search_cache: int = DEFAULT_MAX_SEARCH_CACHE,
    ):
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

    #: whoosh search schema
    schema = Schema(
        decoded_country=TEXT(
            phrase=False,
            analyzer=StandardAnalyzer(
                stoplist=frozenset(  # exclude us from standard stopwords
                    [
                        'and',
                        'is',
                        'it',
                        'an',
                        'as',
                        'at',
                        'have',
                        'in',
                        'yet',
                        'if',
                        'from',
                        'for',
                        'when',
                        'by',
                        'to',
                        'you',
                        'be',
                        'we',
                        'that',
                        'may',
                        'not',
                        'with',
                        'tbd',
                        'a',
                        'on',
                        'your',
                        'this',
                        'of',
                        'will',
                        'can',
                        'the',
                        'or',
                        'are',
                    ]
                )
            ),
        ),
        country=STORED(),
        basecountry=STORED(),
    )

    class CountryTermClass(FuzzyTerm):
        """Class controls number of typo mistakes as dependency on the term length.

        Args:
                fieldname: a name of the field the score will be calculated for
                text: the content of the ``fieldname``
                boost: boost factor
                maxdist: the max levenshtein distance for the term
                prefixlength: the unchangeable prefix length
                constantscore: use constant score
        """

        def __init__(  # pylint: disable=too-many-arguments
            self,
            fieldname: str,
            text: str,
            boost: float = 1.0,
            maxdist: int = 2,
            prefixlength: int = 0,
            constantscore: bool = False,
        ):
            del maxdist
            maxdist: int = 3
            if len(text) < 4:
                maxdist = 0
            elif len(text) < 11:
                maxdist = 1
            elif len(text) < 16:
                maxdist = 2

            super().__init__(fieldname, text, boost, maxdist, prefixlength, constantscore)

    def post_process_name(self, name: str, postprocess: bool = True) -> str:
        """Postprocess names after whoosh searching.

        Example:
            Names, normalized accordingly ISO standard names can be transformed accordingly to
            some mapping to have more beautiful names for some countries as di team desires
            The postprocessing actually is done if the ``postprocess`` flag is **True**.

        Args:
            name: name to postprocess
            postprocess: flag showing if postprocessing should be really applied

        Returns:
            postprocessed or unchanged ``name`` value depending on the ``postprocess`` value

        """
        if not postprocess:
            return name
        if name in self.post_process_country_map:
            return self.post_process_country_map[name]
        return name

    def get_backup_path(self) -> str:
        """Get backup path where index is saved on disk.

        Returns:
            backup path

        """
        return self.path

    def get_index(self) -> whoosh.index.Index:
        """Get whoosh index (thread safe).

        Returns:
            whoosh index

        """
        with self.ix_lock:
            return self.ix

    def create_whoosh_ram_index(self) -> whoosh.index.Index:
        """Create inmemory whoosh index.

        Returns:
            Empty inmemory whoosh index

        """
        storage = RamStorage()
        return FileIndex.create(storage, self.schema, 'MAIN')

    def backup_index(self) -> None:
        """Backup whoosh index in on disk file."""
        os.makedirs(self.path, exist_ok=True)
        with self.ix_lock:
            if self.ix:
                with FileStorage(self.path) as file_storage:
                    copy_storage(self.ix.storage, file_storage)

    async def restore_backuped_index_async(self) -> None:
        """Restore whoosh index from a file on disk to memory. Asynchronous version."""
        asyncio.get_event_loop().run_in_executor(None, self.restore_backuped_index)

    def restore_backuped_index(self) -> None:
        """Restore whoosh index from a file on disk to memory. Synchronous version."""
        with self.simple_index_lock:
            if not self.simple_index:
                self.simple_index = create_basename_by_name_super_index()
        os.makedirs(self.path, exist_ok=True)
        try:
            saved_ix = whoosh.index.open_dir(self.path)
        except EmptyIndexError:
            return
        cur_ix = self.create_whoosh_ram_index()
        copy_storage(saved_ix.storage, cur_ix.storage)
        with self.ix_lock:
            self.ix = cur_ix

    def refresh(self, update_datetime: datetime = None) -> None:
        """Refresh whoosh country index. Synchronous version.

        Args:
            update_datetime: last refresh time to control if a new refresh is required

        """
        self._refresh(update_datetime=update_datetime)

    async def refresh_async(self, update_datetime: datetime = None) -> None:
        """Refresh whoosh country index. Asynchronous version.

        Args:
            update_datetime: last refresh time to control if a new refresh is required

        """
        asyncio.get_event_loop().run_in_executor(None, self._refresh, update_datetime)

    def _refresh(self, update_datetime: datetime = None):
        """Refresh whoosh index. Internal implementation.

        Args:
            update_datetime: last refresh time to control if a new refresh is required

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

    def normalize_country_detailed(
        self, name: str, limit: Optional[int] = None
    ) -> Tuple[int, List[Any]]:
        """Detailed country normalization.

        Args:
            name: country name to normalize
            limit: How many results should be searched (None to find all possible results)

        Raises:
            RuntimeError: if it is called during the reindexation process

        Returns:
            All possible variants from the whoosh index for the name and their rates.

        Note:
            The result scoring can be bad if the ``limit`` value differ from **None**

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
                qp = QueryParser(
                    'decoded_country',
                    schema=self.schema,
                    termclass=self.CountryTermClass,
                    group=OrGroup,
                )
                q = qp.parse(query)
                results = s.search(q, limit=None)
            results = [
                dict(
                    basecountry=hit['basecountry'],
                    country=hit['country'],
                    # rate=hit.score,
                    rate=fuzz.token_sort_ratio(
                        _clean_name2(name), _clean_name2(hit['country'])
                    ),  # rate=hit.score
                )
                for hit in results
            ]
            results = sorted(results, key=lambda k: k['rate'], reverse=True)
            results_len = len(results)
            try:
                limit = int(cast(int, limit))
            except (ValueError, TypeError):
                limit = None
            if limit:
                results = results[:limit]
            return results_len, results

    def normalize_country(self, name: str, postprocess: bool = True) -> str:
        """Country name normalization.

        Only the variant with max rate will be returned.

        If ``postprocess`` is True additional name postprocessing will be done.
        E.g. ISO name mapping to more desired by di team names

        Args:
            name: name to normalize
            postprocess: flag showing if postprocessing should be applied

        Returns:
            normalized and possibly postprocessed country name

        """
        name = name.strip()
        with self.simple_index_lock:
            if self.simple_index:
                if name in self.simple_index:
                    return self.post_process_name(self.simple_index[name], postprocess)
                if name.capitalize() in self.simple_index:
                    return self.post_process_name(self.simple_index[name.capitalize()], postprocess)
        logger.info('! Use whoosh index for %s', name)
        result: str
        if name in self.search_cache:
            result = self.search_cache[name]
        else:
            results = self.normalize_country_detailed(name)
            if not results[0]:
                logger.info('! missed %s', name)
                result = self.post_process_name(name, postprocess)
            else:
                result = results[1][0].get('basecountry')
                result = self.post_process_name(result or name, postprocess)
            if len(self.search_cache) > self.max_search_cache:
                self.search_cache = {}  # Reinit cache to protect memory (atacks?)
            self.search_cache[name] = result
        return result

    def refine_country(self, name: str) -> str:
        """Country name normalization and refining.

        Additional name refining will be done comparing with simple
        :py:meth:`normalize_country` version
        (using :py:func:`dicountries.utils.reorder_name`).

        Example:
            If the normalized name is **Korea, Republic of** the return value
            will be **Republic of Korea**.
            Only the variant with max rate will be returned.

            If ``postprocess`` is True additional name postprocessing will be done.
            E.g. ISO name mapping to more desired by di team names.

        Args:
            name: Country name to normalize and refine

        Returns:
            Normalized and possibly refined country name

        """
        name = self.normalize_country(name, postprocess=False)
        if name in self.post_process_country_map:
            return self.post_process_country_map[name]
        return reorder_name(name)
