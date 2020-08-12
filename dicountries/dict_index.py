"""Some operations on list and dict databases and indexes loaded from text and json files."""

import logging
from copy import copy
from typing import List, Set, Tuple, Union, cast

from .base_types import DictDB, FieldsDescription, Index, ListDB, SimpleDB, SplitPolicies, StringMap
from .utils import reorder_name

# try:
#     from typing import Final  # type: ignore # isort: ignore # pylint: disable=no-name-in-module
# except ImportError:
#     from typing_extensions import Final  # type: ignore # pylint: disable=no-name-in-module

REPORT_TEMPLATE_KEY_ADDED = 'Key has already been added to the index [%s] (Old: [%s], New: [%s])'
REPORT_TEMPLATE_THERE_IS_FIELD = 'There is a field [%s] in the index (%s)'
REPORT_TEMPLATE_MERGE_WARNING = 'Index merge warning: key [%s] present in both ([%s, %s], [%s, %s])'
REPORT_TEMPLATE_RECORDS_WITHOUT_FIELDS = (
    'There were records without filed [{%s}] in `add_base_country`'
)
REPORT_TEMPLATE_RECORDS_WITHOUT_DASH = (
    'There were records without dash in the filed [{%s}] in `add_base_country`'
)

logger = logging.getLogger('dicountries')
logging.basicConfig(format='%(levelname)s  dicountries: %(message)s')


def get_keys(db: SimpleDB) -> Set[str]:
    """Get unique keys from a list-like or dict like database.

    Args:
        db: database

    Returns:
        A set of unique indexes

    """
    keys: Set[str] = set()
    if isinstance(db, list):
        db = cast(ListDB, db)
        for item in db:
            for key in item:
                keys.add(key)
    else:
        db = cast(DictDB, db)
        for v in db.values():
            for key in v:
                keys.add(key)
    return keys


def normalize_keys(db: ListDB, key_mapping: StringMap) -> ListDB:
    """Normalize database keys.

    Create a new list database on base of `db` list database transforming keys
    accordingly to the `key_mapping` mapping.

    Args:
        db: incoming list database
        key_mapping: desired key mapping

    Returns:
        normalized list database

    """
    new_db: ListDB = []
    for item in db:
        new_item: StringMap = {}
        for key, value in item.items():
            new_key = key_mapping.get(key, key)
            new_item[new_key] = value
        new_db.append(new_item)
    return new_db


def create_dict_db(db: ListDB, field_name: str, allow_doubles: bool = False) -> DictDB:
    """Transform a list country database to a dict country database.

    Args:
        db: incoming list database
        field_name: name of the value field to be used as dict key field
        allow_doubles: raise an error (False) or just log a warning and save the first
            found key if same equal keys were found (True)

    Returns:
        dict country database

    Raises:
        RuntimeError: If key has already been added to the index and `allow_doubles` is False

    """
    new_db: DictDB = {}
    for item in db:
        key = item[field_name]
        if key in new_db:
            if allow_doubles:
                logger.warning(REPORT_TEMPLATE_KEY_ADDED, key, new_db[key], item)
            else:
                raise RuntimeError(REPORT_TEMPLATE_KEY_ADDED % key, new_db[key], item)
        else:
            new_db[key] = item
    return new_db


def create_index(  # noqa: C901
    db: SimpleDB,
    first_field: str,
    second_fields: FieldsDescription,
    policy: SplitPolicies = 'None',
    remove_doubles: bool = False,
) -> Index:
    """Create a new dict index for list-like or dict-like database db.

    Args:
        db: database
        first_field: field name whish value should be found by second_fields values
            if there are no first_field in some db records a warning
            `Attention: non complete index` will be logged
        second_fields: field name or list of filed names that database will be searched on
        policy: what to do if a comma sign found inside a value of some second_fields:

            * **None** - do nothing, just add to index as is
            * **sort** - refine second_field value
            * **split** - split value by commas and use them all as possible search values

        remove_doubles: remove all indexing if two values found (True) or use the first
            found value in the index

    Returns:
        a new dict index

    """
    index: Index = {}
    doubles: Set[str] = set()
    skipped_first: bool = False

    def process_item(item: StringMap) -> None:  # pylint: disable=too-many-branches
        nonlocal skipped_first, doubles, index

        first = item.get(first_field)
        if first is None:
            skipped_first = True
            return
        for field in second_fields:
            second = item.get(field)
            if second is None:
                return
            if second in index:
                logger.warning(REPORT_TEMPLATE_THERE_IS_FIELD, second, item)
                doubles.add(second)
            else:
                has_comma = ',' in second
                if has_comma and policy == 'sort':
                    index[cast(str, second)] = cast(str, first)
                    second = reorder_name(second)
                    if second in index:
                        logger.warning(REPORT_TEMPLATE_THERE_IS_FIELD, second, item)
                        doubles.add(second)
                    else:
                        index[cast(str, second)] = cast(str, first)

                elif has_comma and policy == 'split':
                    index[cast(str, second)] = cast(str, first)
                    for entry in second.split(','):
                        if entry in index:
                            entry = entry.strip()
                            logger.warning(REPORT_TEMPLATE_THERE_IS_FIELD, entry, item)
                            doubles.add(entry)
                        else:
                            index[cast(str, entry)] = cast(str, first)
                else:
                    index[cast(str, second)] = cast(str, first)

    if not isinstance(second_fields, list):
        second_fields = cast(str, second_fields)
        second_fields = [second_fields]
    if isinstance(db, list):
        db = cast(ListDB, db)
        for item in db:
            process_item(item)
    else:
        db = cast(DictDB, db)
        for v in db.values():
            process_item(v)

    if remove_doubles:
        for double in doubles:
            del index[double]

    if skipped_first:
        logger.warning('Attention: non complete index')
    return index


def print_index(index: Index) -> None:
    """Print index content.

    Args:
        index: dict index to print to stdout

    """
    for k, v in index.items():
        print(f'{k}: {v}')


def print_names_with_comma(index: Index, policy: SplitPolicies = 'None') -> None:
    """Print names with commas in the index keys.

    Args:
        index: a dict index to print keys with coma
        policy: what to do if a comma sign found inside some key:

            * **None**: do nothing, just print unchanged
            * **sort**: refine second_field value
            * **split**: split value by commas and use them all as possible search values

    """
    for k, v in index.items():
        if ',' in k:
            print(f'{k}: {v}')
            if policy == 'sort':
                print(reorder_name(k))
            elif policy == 'split':
                for item in k.split(','):
                    print(item.strip())


def merge_indexes(*indexes: Union[Index, List[Index]]) -> Index:
    """Create a new combined index from several indexes (combine key-value pairs from all of them).

    Args:
        indexes: several indexes as separate parameters or a list of indexes (one parameter)

    Returns:
        a new dict index

    """
    if len(indexes) == 1:
        indexes = cast(Tuple[List[Index]], indexes[0])
    indexes = cast(List[Index], indexes)
    super_index: Index = indexes[0]
    for next_index in indexes[1:]:
        for k, v in next_index.items():
            if k in super_index:
                logger.warning(REPORT_TEMPLATE_MERGE_WARNING, k, k, super_index[k], k, v)
            super_index[k] = v
    return super_index


def chain_indexes(*indexes: Union[Index, List[Index]]) -> Index:
    """Chain several indexes.

    Create a new combined index from several indexes applying indexation sequentially
    to every index in the list
    (keys from the first one and corresponding values from the last one).

    Args:
        indexes: several indexes as separate parameters or a list of indexes (one parameter)

    Returns:
        a new dict index

    """
    if len(indexes) == 1:
        indexes = cast(Tuple[List[Index]], indexes[0])
    indexes = cast(List[Index], indexes)
    super_index: Index = copy(indexes[0])
    for next_index in indexes[1:]:
        for k, v in copy(super_index).items():
            if v not in next_index:
                del super_index[k]
            else:
                super_index[k] = next_index[v]
    return super_index


def reverse_index(index: Index) -> Index:
    """Reverse an index (keys become values and values became keys).

    Args:
        index: a dict index

    Returns:
        a dict index

    """
    return {v: k for k, v in index.items()}


def add_base_country(db: SimpleDB, source_field: str, dest_field: str) -> None:
    """Add base country field to database.

    Add a field with base country part using `dest_field` description
    for the list-like or dict like database `db` records.

    Args:
        db: processed database
        source_field: a field to be splitted to base country and region name
        dest_field: a field name to save the base country information.

    Example:
        If some `source_field` has value "GT-SO" then
        value "GT" will be saved as the value of the `dest_field`.

    """
    no_source: bool = False
    no_dash: bool = False

    def process_item(item):
        nonlocal no_source, no_dash
        source = item.get(source_field)
        if source:
            if '-' in source:
                source = source.split('-')[0]
            else:
                no_dash = True
            item[dest_field] = source
        else:
            no_source = True

    if isinstance(db, list):
        db = cast(ListDB, db)
        for item in db:
            process_item(item)
    else:
        db = cast(DictDB, db)
        for v in db.values():
            process_item(v)
    if no_source:
        logger.warning(REPORT_TEMPLATE_RECORDS_WITHOUT_FIELDS, source_field)
    if no_dash:
        logger.warning(REPORT_TEMPLATE_RECORDS_WITHOUT_DASH, source_field)
