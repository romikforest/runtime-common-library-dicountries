from .utils import reorder_name

def get_keys(db):
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
    index = {}
    for item in db:
        key = item[field_name]
        if key in index:
            if allow_doubles:
                print(f'Key has already been added to the index [{key}] (Old: [{index[key]}, New: [{item}])')
            else:
                raise RuntimeError(f'Key has already been added to the index [{key}] (Old: [{index[key]}, New: [{item}])')
        else:
            index[key] = item
    return index


def create_index(db, first_field, second_fields, policy='None', remove_doubles=False):
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
                print(f'There is a field [{second}] in the index ({item})')
                doubles.add(second)
            else:
                has_comma = ',' in second
                if has_comma and policy == 'sort':
                    index[second] = first
                    second = reorder_name(second)
                    if second in index:
                        print(f'There is a field [{second}] in the index ({item})')
                        doubles.add(second)
                    else:
                        index[second] = first

                elif has_comma and policy == 'split':
                    index[second] = first
                    for entry in second.split(','):
                        if entry in index:
                            entry = entry.strip()
                            print(f'There is a field [{entry}] in the index ({item})')
                            doubles.add(entry)
                        else:
                            index[entry] = first
                else:
                    index[second] = first



    index = {}
    doubles = set()
    skipped_first = False
    if not isinstance(second_fields, list):
        second_fields = [ second_fields ]
    if isinstance(db, list):
        for item in db:
            process_item(item)
    else:
        for k, v in db.items():
            process_item(v)

    if remove_doubles:
        for double in doubles:
            del index[double]

    if skipped_first:
        print('Attention: non complete index')
    return index


def print_index(index):
    for k, v in index.items():
        print(f'{k}: {v}')


def print_names_with_comma(index, policy='None'):
    for k, v in index.items():
        if ',' in k:
            print(f'{k}: {v}')
            if policy == 'sort':
                print(reorder_name(k))
            elif policy == 'split':
                for item in k.split(','):
                    print(item.strip())


def merge_indexes(*indexes):
    if len(indexes) == 1:
        indexes = indexes[0]
    super_index = indexes[0].copy()
    for next_index in indexes[1:]:
        for k, v in next_index.items():
            if k in super_index:
                print(f'Index merge warning: key [{k}] present in both ([{k}, {super_index[k]}], [{k}, {v}])')
            super_index[k] = v
    return super_index


def chain_indexes(*indexes):
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
    return {v: k for k, v in index.items()}


def add_base_country(db, source_field, dest_field):
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
        print(f'Warning. There were records without filed [{source_field}] in `add_base_country`')
    if no_dash:
        print(f'Warning. There were records without dash in the filed [{source_field}] in `add_base_country`')
