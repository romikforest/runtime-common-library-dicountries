# (generated with --quick)

from typing import Any, List, MutableMapping, MutableSequence, Sequence, Union

DictDB = MutableMapping[str, MutableMapping[str, str]]
Index = MutableMapping[str, str]
StringMap = MutableMapping[str, str]

JSONType: Any
country_old_key_map: MutableMapping[str, str]
country_region_key_map: MutableMapping[str, str]
json: module
main_country_key_map: MutableMapping[str, str]

def add_base_country(db: Union[MutableMapping[str, MutableMapping[str, str]], MutableSequence[MutableMapping[str, str]]], source_field: str, dest_field: str) -> None: ...
def chain_indexes(*indexes: Union[List[MutableMapping[str, str]], MutableMapping[str, str]]) -> MutableMapping[str, str]: ...
def create_basename_by_name_super_index() -> MutableMapping[str, str]: ...
def create_dict_db(db: MutableSequence[MutableMapping[str, str]], field_name: str, allow_doubles: bool = ...) -> MutableMapping[str, MutableMapping[str, str]]: ...
def create_index(db: Union[MutableMapping[str, MutableMapping[str, str]], MutableSequence[MutableMapping[str, str]]], first_field: str, second_fields: Union[str, Sequence[str]], policy = ..., remove_doubles: bool = ...) -> MutableMapping[str, str]: ...
def get_json_data(file_name: str) -> Any: ...
def load_country_old_db() -> MutableMapping[str, MutableMapping[str, str]]: ...
def load_country_region_db() -> MutableMapping[str, MutableMapping[str, str]]: ...
def load_main_country_db() -> MutableMapping[str, MutableMapping[str, str]]: ...
def load_post_process_country_mapping() -> MutableMapping[str, str]: ...
def merge_indexes(*indexes: Union[List[MutableMapping[str, str]], MutableMapping[str, str]]) -> MutableMapping[str, str]: ...
def normalize_keys(db: MutableSequence[MutableMapping[str, str]], key_mapping: MutableMapping[str, str]) -> MutableSequence[MutableMapping[str, str]]: ...
def restore_index(path: str) -> MutableMapping[str, str]: ...
def save_index(index: MutableMapping[str, str], path: str) -> None: ...
