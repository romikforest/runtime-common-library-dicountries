# (generated with --quick)

from typing import Any, Coroutine, Dict, MutableMapping, Optional, Tuple, Type, Union

StringMap = MutableMapping[str, str]

COUNTRY_IX_VER: int
DEFAULT_MAX_SEARCH_CACHE: int
EmptyIndexError: Any
FileIndex: Any
FileStorage: Any
FuzzyTerm: Any
OrGroup: Any
QueryParser: Any
RamStorage: Any
STORED: Any
Schema: Any
StandardAnalyzer: Any
TEXT: Any
asyncio: module
copy_storage: Any
datetime: Type[datetime.datetime]
fuzz: module
logger: logging.Logger
logging: module
os: module
pytz: module
syntax: module
threading: module
unidecode: Any
whoosh: module

class CountryIndex:
    CountryTermClass: type
    __doc__: str
    ix: Any
    ix_lock: threading.Lock
    last_update: Optional[datetime.datetime]
    last_update_lock: threading.Lock
    max_search_cache: int
    path: str
    post_process_country_map: MutableMapping[str, str]
    schema: Any
    search_cache: Union[Dict[str, Any], MutableMapping[str, str]]
    simple_index: Optional[MutableMapping[str, str]]
    simple_index_lock: threading.Lock
    update_lock: threading.Lock
    version: int
    def __init__(self, index_path: Optional[str] = ..., post_process_country_map: Optional[MutableMapping[str, str]] = ..., use_async: bool = ..., max_search_cache: int = ...) -> None: ...
    def _refresh(self, update_datetime: datetime.datetime = ...) -> None: ...
    def backup_index(self) -> None: ...
    def create_whoosh_ram_index(self) -> Any: ...
    def get_backup_path(self) -> str: ...
    def get_index(self) -> Any: ...
    def normalize_country(self, name: str, postprocess: bool = ...) -> str: ...
    def normalize_country_detailed(self, name: str, limit: Optional[int] = ...) -> Tuple[int, list]: ...
    def post_process_name(self, name: str, postprocess: bool = ...) -> str: ...
    def refine_country(self, name: str) -> str: ...
    def refresh(self, update_datetime: datetime.datetime = ...) -> None: ...
    def refresh_async(self, update_datetime: datetime.datetime = ...) -> Coroutine[Any, Any, None]: ...
    def restore_backuped_index(self) -> None: ...
    def restore_backuped_index_async(self) -> Coroutine[Any, Any, None]: ...

def _clean_name(name: str) -> str: ...
def _clean_name2(name: str) -> str: ...
def create_basename_by_name_super_index() -> MutableMapping[str, str]: ...
def load_post_process_country_mapping() -> MutableMapping[str, str]: ...
def reorder_name(name: str) -> str: ...
