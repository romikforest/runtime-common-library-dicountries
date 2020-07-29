import asyncio
from fuzzywuzzy import fuzz
import os
import pytz
import threading
from threading import Thread
from unidecode import unidecode
from whoosh import index
from whoosh.fields import *
from whoosh.index import EmptyIndexError
from whoosh.query import FuzzyTerm
from whoosh.qparser import QueryParser
from whoosh.scoring import FunctionWeighting

from .loader import (
    create_basename_by_name_super_index,
    load_post_process_country_mapping
    # restore_index,
    # save_index
)
from .utils import reorder_name

COUNTRY_IX_VER = 1  # change this if you've changed the index schema, so old index will not be loaded in the k8s pod
MAX_SEARCH_CACHE = 1000

# def run_async(corofn, *args):
#     loop = asyncio.new_event_loop()
#     try:
#         coro = corofn(*args)
#         asyncio.set_event_loop(loop)
#         return loop.run_until_complete(coro)
#     finally:
#         loop.close()

class CountryIndex:

    schema = Schema(decoded_country=TEXT(phrase=True),
                    country=STORED(),
                    basecountry=STORED(),
                    )

    class CountryTermClass(FuzzyTerm):
        def __init__(self, fieldname, text, boost=1.0, maxdist=2, prefixlength=0, constantscore=False):
            if len(text) < 4: # 4
                super().__init__(fieldname, text, boost, 0, prefixlength, constantscore)
            elif len(text) < 7:
                super().__init__(fieldname, text, boost, 2, prefixlength, constantscore)
            elif len(text) < 12:
                super().__init__(fieldname, text, boost, 3, prefixlength, constantscore)
            else:
                super().__init__(fieldname, text, boost, 4, prefixlength, constantscore)

    def __init__(self, index_path=None, post_process_country_map=None, use_async=False): # simple_index_path=None
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
        # if not simple_index_path:
        #     self.simple_path = f'indexes/simple_countries'
        # else:
        #     self.simple_path = simple_index_path
        self.last_update_lock = threading.Lock()
        self.last_update = None
        self.update_lock = threading.Lock()
        self.search_cache = {}

        if use_async:
            asyncio.get_event_loop().run_in_executor(None, self.restore_backuped_index)
        else:
            self.restore_backuped_index()
        if not self.ix:
            if use_async:
                asyncio.get_event_loop().run_in_executor(None, self.refresh)
            else:
                self.refresh()

        # thread = Thread(target=self.restore_backuped_index)
        # thread.start()
        # thread.join()

    def clean_name(self, name):
        return unidecode(name or '').strip().replace('(', ' ').replace(')', ' ')

    def clean_name2(self, name):
        return unidecode(name or '').strip().replace('(', ' ').replace(')', ' ')

    def post_process_name(self, name, postprocess=True):
        if not postprocess:
            return name
        if name in self.post_process_country_map:
            return self.post_process_country_map[name]
        return name

    def get_backup_path(self):
        return self.path

    def get_index(self):
        with self.ix_lock:
            return self.ix

    def create_whoosh_ram_index(self):
        from whoosh.filedb.filestore import RamStorage
        from whoosh.index import FileIndex

        storage = RamStorage()
        return FileIndex.create(storage, self.schema, 'MAIN')

    def backup_index(self):
        from whoosh.filedb.filestore import copy_storage, FileStorage
        os.makedirs(self.path, exist_ok=True)
        # os.makedirs(self.simple_path, exist_ok=True) # Needs simple_index_lock
        # if self.simple_index:
        #     save_index(self.simple_index, os.path.join(self.simple_path, 'index.json'))
        with self.ix_lock:
            if self.ix:
                with FileStorage(self.path) as file_storage:
                    copy_storage(self.ix.storage, file_storage)


    async def restore_backuped_index_async(self):
        asyncio.get_event_loop().run_in_executor(None, self.restore_backuped_index)


    def restore_backuped_index(self):
        # simple_path = os.path.join(self.simple_path, 'index.json')
        # if os.path.isfile(simple_path):
        #     self.simple_index = restore_index(simple_path)
        with self.simple_index_lock:
            if not self.simple_index:
                self.simple_index = create_basename_by_name_super_index()
        from whoosh.filedb.filestore import copy_storage
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
        self._refresh()

    async def refresh_async(self, update_datetime=None):
        asyncio.get_event_loop().run_in_executor(None, self._refresh, update_datetime)

    def _refresh(self, update_datetime=None):
        from datetime import datetime

        with self.update_lock:
            if update_datetime:
                with self.last_update_lock:
                    if self.last_update and self.last_update > update_datetime:
                        # print(f'No need to update countries. Index updated on {self.last_update}.')
                        return
            print('* Updating indices for countries...')

            print('* Load countries information...')
            data = create_basename_by_name_super_index()
            with self.simple_index_lock:
                self.simple_index = data

            print(f'* Parse countries information...')
            new_ix = self.create_whoosh_ram_index()
            writer = new_ix.writer()

            # await asyncio.sleep(0)
            for k, v in data.items():
                # await asyncio.sleep(0)
                mapped_data = {}
                mapped_data['country'] = k
                mapped_data['decoded_country'] = self.clean_name(k)
                mapped_data['basecountry'] = v
                writer.add_document(**mapped_data)

            print(f'* Save countries information...')
            # await asyncio.sleep(0)
            writer.commit()
            # await asyncio.sleep(0)

            with self.ix_lock:
                self.ix = new_ix

            # await asyncio.sleep(0)
            self.backup_index()
            # await asyncio.sleep(0)

            with self.last_update_lock:
                self.last_update = datetime.utcnow().replace(tzinfo=pytz.timezone('utc'))


    def normalize_country_detailed(self, name, limit=None):
        cur_ix = self.get_index()
        if not cur_ix:
            raise RuntimeError('Reindexation proccess')

        country = self.clean_name(name)
        query = ''
        if country:
            query += f' decoded_country:({country})'
        query = query.strip()
        # print(f'query: {query}')
        if not query:
            return 0, []

        with cur_ix.searcher() as s:
            qp = QueryParser('decoded_country', schema=self.schema, termclass=self.CountryTermClass)
            q = qp.parse(query)
            results = s.search(q, limit=None)
            results = [dict(basecountry=hit['basecountry'],
                            country=hit['country'],
                            # rate=hit.score,
                            rate=fuzz.token_sort_ratio(
                                    self.clean_name2(name),
                                    self.clean_name2(hit['country'])
                                ) # rate=hit.score
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
        name = name.strip()
        with self.simple_index_lock:
            if self.simple_index:
                if name in self.simple_index:
                    return self.post_process_name(self.simple_index[name], postprocess)
                if name.capitalize() in self.simple_index:
                    return self.post_process_name(self.simple_index[name.capitalize()], postprocess)
        print(f'! Use whoosh index for {name}')
        if name in self.search_cache:
            result = self.search_cache[country]
        else:
            result = self.normalize_country_detailed(name)
            if not result[0]:
                print(f'! missed {name}')
                result = self.post_process_name(name, postprocess)
            else:
                result = result[1][0].get('basecountry')
                result = self.post_process_name(result or name, postprocess)
            if len(self.search_cache) > MAX_SEARCH_CACHE:
                self.search_cache = {} # Reinit cache to protect memory (atacks?)
            self.search_cache[name] = result
        return result

    def refine_country(self, name):
        name = self.normalize_country(name, postprocess=False)
        if name in self.post_process_country_map:
            return self.post_process_country_map[name]
        return reorder_name(name)
