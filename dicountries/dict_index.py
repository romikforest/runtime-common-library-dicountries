"""
Some operations on list and dict databases and indexes loaded from text and json files
"""

from .utils import reorder_name
import logging

logger = logging.getLogger('dicountries')
logging.basicConfig(format='%(levelname)s  dicountries: %(message)s')


def get_keys(db):
    """Get unique keys from a list-like or dict like database

    Args:
        db: database

    Returns:
        A set of unique indexes

    """
    keys = set()
    if isinstance(db, list):
        for item in db:
            for key in item:
                keys.add(key)
    else:
        for k, v in db.items():
            for key in v:
                keys.add(key)
    return keys


def normalize_keys(db, map):
    """Create a new list database on base of `db` list database transforming keys
    accordingly to the `map` mapping

    Args:
        db: incoming list database
        map: desired key mapping

    Returns:
        normalized database

    """
    new_db = []
    for item in db:
        new_item = {}
        for key, value in item.items():
            new_key = map.get(key)
            if not new_key:
                new_key = key
            new_item[new_key] = value
        new_db.append(new_item)
    return new_db


def create_dict_db(db, field_name, allow_doubles=False):
    """Transform a list country database to a dict country database

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
    index = {}
    for item in db:
        key = item[field_name]
        if key in index:
            if allow_doubles:
                logger.warning(f'Key has already been added to the index [{key}] (Old: [{index[key]}, New: [{item}])')
            else:
                raise RuntimeError(
                    f'Key has already been added to the index [{key}] (Old: [{index[key]}, New: [{item}])')
        else:
            index[key] = item
    return index


def create_index(db, first_field, second_fields, policy='None', remove_doubles=False):
    """Create a new dict index for list-like or dict-like database db

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

    def process_item(item):
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
                logger.warning(f'There is a field [{second}] in the index ({item})')
                doubles.add(second)
            else:
                has_comma = ',' in second
                if has_comma and policy == 'sort':
                    index[second] = first
                    second = reorder_name(second)
                    if second in index:
                        logger.warning(f'There is a field [{second}] in the index ({item})')
                        doubles.add(second)
                    else:
                        index[second] = first

                elif has_comma and policy == 'split':
                    index[second] = first
                    for entry in second.split(','):
                        if entry in index:
                            entry = entry.strip()
                            logger.warning(f'There is a field [{entry}] in the index ({item})')
                            doubles.add(entry)
                        else:
                            index[entry] = first
                else:
                    index[second] = first

    index = {}
    doubles = set()
    skipped_first = False
    if not isinstance(second_fields, list):
        second_fields = [second_fields]
    if isinstance(db, list):
        for item in db:
            process_item(item)
    else:
        for v in db.values():
            process_item(v)

    if remove_doubles:
        for double in doubles:
            del index[double]

    if skipped_first:
        logger.warning('Attention: non complete index')
    return index


def print_index(index):
    """Print index content

    Args:
        index: dict index to print to stdout

    """
    for k, v in index.items():
        print(f'{k}: {v}')


def print_names_with_comma(index, policy='None'):
    """Print names with commas in the index keys:

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


def merge_indexes(*indexes):
    """Create a new combined index from several indexes (combine key-value pairs from all of them)

    Args:
        indexes: several indexes as separate parameters or a list of indexes (one parameter)

    Returns:
        a new dict index

    """
    if len(indexes) == 1:
        indexes = indexes[0]
    super_index = indexes[0].copy()
    for next_index in indexes[1:]:
        for k, v in next_index.items():
            if k in super_index:
                logger.warning(f'Index merge warning: key [{k}] present in both ([{k}, {super_index[k]}], [{k}, {v}])')
            super_index[k] = v
    return super_index


def chain_indexes(*indexes):
    """Create a new combined index from several indexes applying indexation sequentially to every index in the list
    (keys from the first one and corresponding values from the last one)

    Args:
        indexes: several indexes as separate parameters or a list of indexes (one parameter)

    Returns:
        a new dict index

    """
    if len(indexes) == 1:
        indexes = indexes[0]
    super_index = indexes[0].copy()
    for next_index in indexes[1:]:
        for k, v in super_index.copy().items():
            if v not in next_index:
                del super_index[k]
            else:
                super_index[k] = next_index[v]
    return super_index


def reverse_index(index):
    """Reverse an index (keys become values and values became keys)

    Args:
        index: a dict index

    Returns:
        a dict index

    """
    return {v: k for k, v in index.items()}


def add_base_country(db, source_field, dest_field):
    """Add a field with base country part using `dest_field` description
    for the list-like or dict like database `db` records

    Args:
        db: processed database
        source_field: a field to be splitted to base country and region name
        dest_field: a field name to save the base country information.

         Example:
             If some `source_field` has value "GT-SO" then
             value "GT" will be saved as the value of the `dest_field`

    """

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

    no_source = False
    no_dash = False
    if isinstance(db, list):
        for item in db:
            process_item(item)
    else:
        for k, v in db.items():
            process_item(v)
    if no_source:
        logger.warning(f'There were records without filed [{source_field}] in `add_base_country`')
    if no_dash:
        logger.warning(f'There were records without dash in the filed [{source_field}] in `add_base_country`')
