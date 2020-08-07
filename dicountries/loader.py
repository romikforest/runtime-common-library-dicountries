"""Loader for text and json databases"""

import json
from typing import List

from .base_types import (
    JSONType,
    StringMap
)
from .dict_index import (
    DictDB,
    Index,
    add_base_country,
    chain_indexes,
    create_dict_db,
    create_index,
    merge_indexes,
    normalize_keys
)


def get_json_data(file_name: str) -> JSONType:
    """Load some json data saved with the package as string

    Args:
        file_name: a path to json file

    Returns:
        Loaded json content

    Note:
        This functions supports any package location, including zipfiles and so on.
        It uses `pkgutil` functions to load data from the `data` package subdirectory

    """
    import pkgutil  # pylint: disable=import-outside-toplevel

    from .metadata import name  # pylint: disable=import-outside-toplevel

    data = pkgutil.get_data(name, f'data/{file_name}') or b''
    return json.loads(data.decode('utf-8'))


main_country_key_map: StringMap = dict(
    alpha_2='a2',
    alpha_3='a3',
    numeric='num',
    official_name='official',
    common_name='common',
)
"""Mapping for main_country db field names
{'common', 'name', 'a3', 'a2', 'num', 'official'}
"""

country_region_key_map: StringMap = dict()
"""Mapping for country_region db field names
{'parent', 'code', 'name', 'type'}
"""

country_old_key_map: StringMap = dict(
    alpha_2='a2',
    alpha_3='a3',
    alpha_4='a4',
    numeric='num',
)
"""Mapping for former countries db field names
{'withdrawal_date', 'num', 'name', 'a2', 'comment', 'a4', 'a3'}
"""


def load_main_country_db() -> DictDB:
    """Load main country database (ISO3166-1)

    Returns:
        main country dict database

    """
    return create_dict_db(
        normalize_keys(get_json_data('iso3166-1.json')['3166-1'], main_country_key_map), 'a2')


def load_country_region_db() -> DictDB:
    """Load country region database (ISO3166-2)

    Returns:
        main country region dict database

    """
    country_region_db = create_dict_db(
        normalize_keys(get_json_data('iso3166-2.json')['3166-2'], country_region_key_map), 'code')
    add_base_country(country_region_db, 'code', 'base')
    main_country_db = load_main_country_db()
    main_country_a3_by_a2_index = create_index(main_country_db, 'a3', 'a2')
    for v in country_region_db.values():
        if v.get('base'):
            base3 = main_country_a3_by_a2_index.get(v['base'])
            if base3:
                v['base3'] = base3
    return country_region_db


def load_country_old_db() -> DictDB:
    """Load former country database (ISO3166-3)

    Returns:
        former country dict database

    """
    return create_dict_db(
        normalize_keys(get_json_data('iso3166-3.json')['3166-3'], country_old_key_map), 'a3', True)


def create_basename_by_name_super_index() -> Index:
    """Process ISO and synonyms database to have a basename by name index

    Returns:
        combined country (main, region, former), synonym index

    """
    # pylint: disable=too-many-locals
    main_country_db = load_main_country_db()
    country_region_db = load_country_region_db()
    country_old_db = load_country_old_db()

    main_country_name_by_a3_index = create_index(main_country_db, 'name', 'a3')

    country_region_base3_by_name_index = create_index(country_region_db, 'base3', 'name',
                                                      policy='sort',
                                                      remove_doubles=True)
    country_region_basename_by_name_index = chain_indexes(country_region_base3_by_name_index,
                                                          main_country_name_by_a3_index)

    main_country_a3_by_allname_index = create_index(main_country_db, 'a3',
                                                    ['name', 'common', 'official'],
                                                    policy='sort')
    main_country_basename_by_name = chain_indexes(main_country_a3_by_allname_index,
                                                  main_country_name_by_a3_index)

    country_old_name_by_a3_index = create_index(country_old_db, 'name', 'a3')
    country_old_a3_by_name_index = create_index(country_old_db, 'a3', 'name', policy='sort')
    country_old_basename_by_name_index = chain_indexes(country_old_a3_by_name_index,
                                                       country_old_name_by_a3_index)

    index_list: List[Index] = []
    index_list.append(country_old_basename_by_name_index)
    index_list.append(country_region_basename_by_name_index)
    index_list.append(main_country_basename_by_name)
    merged_index = merge_indexes(index_list)

    country_synonyms = get_json_data('country_mapping.json')

    for k, v in country_synonyms.items():
        merged_index[k] = k
        for entry in v:
            # if not entry in merged_index:
            merged_index[entry] = k

    return merged_index


def load_post_process_country_mapping() -> StringMap:
    """Load di post process index that can be used to correct some ugly ISO names
    to desired names the di teem likes more

    Returns:
        country name mapping (dict)

    """
    return get_json_data('post_process_country_mapping.json')


def save_index(index: Index, path: str) -> None:
    """Save index to a file

    Args:
        index: dict index
        path: path to save index to

    """
    with open(path, 'wt', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False)


def restore_index(path: str) -> Index:
    """Load index from file

    Args:
        path: path to load index from

    Returns:
        json index (dict-like object)

    """
    with open(path, 'rt', encoding='utf-8') as f:
        return json.load(f)
