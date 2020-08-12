# (generated with --quick)

import dicountries.whoosh_index
from typing import Any, List, MutableMapping, MutableSequence, Sequence, Set, Type, TypeVar, Union

DictDB = MutableMapping[str, MutableMapping[str, str]]
Index = MutableMapping[str, str]
ListDB = MutableSequence[MutableMapping[str, str]]
StringMap = MutableMapping[str, str]

COUNTRY_IX_VER: int
CountryIndex: Type[dicountries.whoosh_index.CountryIndex]
DEFAULT_MAX_SEARCH_CACHE: int
EmptyIndexError: Any
FieldsDescription: Type[Union[str, Sequence[str]]]
FileIndex: Any
FileStorage: Any
FuzzyTerm: Any
JSONType: Any
Literal: Any
OrGroup: Any
QueryParser: Any
REPORT_TEMPLATE_KEY_ADDED: str
REPORT_TEMPLATE_MERGE_WARNING: str
REPORT_TEMPLATE_RECORDS_WITHOUT_DASH: str
REPORT_TEMPLATE_RECORDS_WITHOUT_FIELDS: str
REPORT_TEMPLATE_THERE_IS_FIELD: str
RamStorage: Any
STORED: Any
Schema: Any
SimpleDB: Type[Union[MutableMapping[str, MutableMapping[str, str]], MutableSequence[MutableMapping[str, str]]]]
SplitPolicies: Any
StandardAnalyzer: Any
TEXT: Any
__version__: Any
asyncio: module
copy_storage: Any
country_old_key_map: MutableMapping[str, str]
country_region_key_map: MutableMapping[str, str]
datetime: Type[datetime.datetime]
fuzz: module
json: module
logger: logging.Logger
logging: module
main_country_key_map: MutableMapping[str, str]
os: module
pytz: module
syntax: module
threading: module
unidecode: Any
whoosh: module

_T = TypeVar('_T')

def _need_import() -> bool: ...
def add_base_country(db: Union[MutableMapping[str, MutableMapping[str, str]], MutableSequence[MutableMapping[str, str]]], source_field: str, dest_field: str) -> None: ...
def chain_indexes(*indexes: Union[List[MutableMapping[str, str]], MutableMapping[str, str]]) -> MutableMapping[str, str]: ...
def copy(x: _T) -> _T: ...
def create_basename_by_name_super_index() -> MutableMapping[str, str]: ...
def create_dict_db(db: MutableSequence[MutableMapping[str, str]], field_name: str, allow_doubles: bool = ...) -> MutableMapping[str, MutableMapping[str, str]]: ...
def create_index(db: Union[MutableMapping[str, MutableMapping[str, str]], MutableSequence[MutableMapping[str, str]]], first_field: str, second_fields: Union[str, Sequence[str]], policy = ..., remove_doubles: bool = ...) -> MutableMapping[str, str]: ...
def get_json_data(file_name: str) -> Any: ...
def get_keys(db: Union[MutableMapping[str, MutableMapping[str, str]], MutableSequence[MutableMapping[str, str]]]) -> Set[str]: ...
def get_main_code(code: str) -> str: ...
def load_country_old_db() -> MutableMapping[str, MutableMapping[str, str]]: ...
def load_country_region_db() -> MutableMapping[str, MutableMapping[str, str]]: ...
def load_main_country_db() -> MutableMapping[str, MutableMapping[str, str]]: ...
def load_post_process_country_mapping() -> MutableMapping[str, str]: ...
def merge_indexes(*indexes: Union[List[MutableMapping[str, str]], MutableMapping[str, str]]) -> MutableMapping[str, str]: ...
def normalize_keys(db: MutableSequence[MutableMapping[str, str]], key_mapping: MutableMapping[str, str]) -> MutableSequence[MutableMapping[str, str]]: ...
def print_index(index: MutableMapping[str, str]) -> None: ...
def print_names_with_comma(index: MutableMapping[str, str], policy = ...) -> None: ...
def reorder_name(name: str) -> str: ...
def restore_index(path: str) -> MutableMapping[str, str]: ...
def reverse_index(index: MutableMapping[str, str]) -> MutableMapping[str, str]: ...
def save_index(index: MutableMapping[str, str], path: str) -> None: ...
