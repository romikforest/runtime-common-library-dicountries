import json
import os

from .dict_index import (
    add_base_country,
    chain_indexes,
    create_dict_db,
    create_index,
    merge_indexes,
    normalize_keys
)

DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')


# {'common', 'name', 'a3', 'a2', 'num', 'official'}
main_country_key_map = dict(
    alpha_2 = 'a2',
    alpha_3 = 'a3',
    numeric = 'num',
    official_name = 'official',
    common_name = 'common',
)

# {'parent', 'code', 'name', 'type'}
country_region_key_map = dict(

)

# {'withdrawal_date', 'num', 'name', 'a2', 'comment', 'a4', 'a3'}
country_old_key_map = dict(
    alpha_2 = 'a2',
    alpha_3 = 'a3',
    alpha_4 = 'a4',
    numeric = 'num',
)

def load_main_country_db():
    with open(os.path.join(DATA_DIR, 'iso3166-1.json'), 'rt', encoding='utf-8') as f:
        return create_dict_db(normalize_keys(json.load(f)['3166-1'], main_country_key_map), 'a2')

def load_country_region_db():
    with open(os.path.join(DATA_DIR, 'iso3166-2.json'), 'rt', encoding='utf-8') as f:
        country_region_db = create_dict_db(normalize_keys(json.load(f)['3166-2'], country_region_key_map), 'code')
        add_base_country(country_region_db, 'code', 'base')
        main_country_db = load_main_country_db()
        main_country_a3_by_a2_index = create_index(main_country_db, 'a3', 'a2')
        for k, v in country_region_db.items():
            if v.get('base'):
                base3 = main_country_a3_by_a2_index.get(v['base'])
                if base3:
                    v['base3'] = base3
        return country_region_db

def load_country_old_db():
    with open(os.path.join(DATA_DIR, 'iso3166-3.json'), 'rt', encoding='utf-8') as f:
        return create_dict_db(normalize_keys(json.load(f)['3166-3'], country_old_key_map), 'a3', True)

def create_basename_by_name_super_index():
    main_country_db = load_main_country_db()
    country_region_db = load_country_region_db()
    country_old_db = load_country_old_db()

    main_country_name_by_a3_index = create_index(main_country_db, 'name', 'a3')

    country_region_base3_by_name_index = create_index(country_region_db, 'base3', 'name', policy='sort',
                                                      remove_doubles=True)
    country_region_basename_by_name_index = chain_indexes(country_region_base3_by_name_index,
                                                          main_country_name_by_a3_index)

    main_country_a3_by_allname_index = create_index(main_country_db, 'a3', ['name', 'common', 'official'],
                                                    policy='sort')
    main_country_basename_by_name = chain_indexes(main_country_a3_by_allname_index, main_country_name_by_a3_index)

    country_old_name_by_a3_index = create_index(country_old_db, 'name', 'a3')
    country_old_a3_by_name_index = create_index(country_old_db, 'a3', 'name', policy='sort')
    country_old_basename_by_name_index = chain_indexes(country_old_a3_by_name_index, country_old_name_by_a3_index)

    index_list = []
    index_list.append(country_old_basename_by_name_index)
    index_list.append(country_region_basename_by_name_index)
    index_list.append(main_country_basename_by_name)
    merged_index = merge_indexes(index_list)

    with open(os.path.join(DATA_DIR, 'country_mapping.json'), 'rt', encoding='utf-8') as f:
        country_synonyms = json.load(f)

    for k, v in country_synonyms.items():
        merged_index[k] = k
        for entry in v:
            # if not entry in merged_index:
            merged_index[entry] = k

    return merged_index

def load_post_process_country_mapping():
    with open(os.path.join(DATA_DIR, 'post_process_country_mapping.json'), 'rt', encoding='utf-8') as f:
        return json.load(f)

def save_index(index, path):
    with open(path, 'wt', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False)

def restore_index(path):
    with open(path, 'rt', encoding='utf-8') as f:
        return json.load(f)