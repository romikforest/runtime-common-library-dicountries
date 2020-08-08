# flake8: noqa

import subprocess

from dicountries.loader import create_basename_by_name_super_index
from dicountries.whoosh_index import CountryIndex

#############################################################

# merged_index = create_basename_by_name_super_index()
# print(merged_index.get('Antigua And Barbuda'))
country_index = CountryIndex()
# country_index.refresh()
# print(country_index.normalize_country('GDD Russia'))

# print(country_index.normalize_country('Russia'))

# print(country_index.normalize_country_detailed('Algeria'))
# exit()

# print(country_index.normalize_country_detailed('Bosnia And Herzegowina'))
# exit()

# # print_index(merged_index)
# for k, w in merged_index.items():
#     if k.lower().startswith('b'):
#         print(f'{k}: {w}')

# ====
# with open('dicountries/data/user_country_list.txt', 'rt', encoding='utf-8') as f:
with open('dicountries/data/country_list.txt', 'rt', encoding='utf-8') as f:
    lines = f.readlines()

for line in lines:
    line = line.strip()

    base = country_index.normalize_country(line)
    # base = country_index.refine_country(line)

    # if line != base:
    #    print(f'Normalize: {line}: {base}')
    #    # subprocess.run(["python", "corrector.py", line, base])

    if line == 'Zimbawe':
        break

    # if line != base:
    #     print(f'{line}: {base}')

    print(f'{line}: {base}')

# print(country_index.normalize_country('Зимбабу'))
# print(country_index.normalize_country('Åland'))
# print(country_index.normalize_country('Antigua And Barbuda'))

# print(country_index.normalize_country_detailed('Åland'))
# print(country_index.normalize_country_detailed('Antigua And Barbuda'))
# 'South Georgia and South Sandwich Islands'

#############################################################

# print(merged_index.get('Puerto Rico'))

# print_index(merged_index)
# print(len(merged_index))

# main_country_db = load_main_country_db()
# main_country_a3_by_name_index = create_index(main_country_db, 'a3', 'name')
#
# reverse_merged_index = reverse_index(merged_index)
#
# with open('data/country_mapping.json', 'rt', encoding='utf-8') as f:
#     country_mapping = json.load(f)
#
# for item in country_mapping:
#     if item not in reverse_merged_index:
#         print(item)
#
# print('===')
# print(merged_index.get('Northern Mariana Islands'))


##############################################################

# # print(main_country_db)
#
#
# # print(get_keys(main_country_db))
# # print(main_country_db.get('US'))
#
# # print(get_keys(country_region_db))
# # print(get_keys(country_old_db))
#
# main_country_name_by_a2_index = create_index(main_country_db, 'name', 'a2')
# # print(main_country_name_by_a2_index.get('US'))
# # # print(main_country_name_a2_index)
# # print('===')
#
# # main_country_a2_by_common_index = create_index(main_country_db, 'a2', 'common')
# # for item in main_country_a2_by_common_index:
# #     print(item)
# # print('===')
#
# #main_country_a2_by_all_names_index = create_index(main_country_db, 'a2', ['name', 'official', 'common'])
# # print_index(main_country_a2_by_all_names_index)
# #print('===')
# #print_names_with_comma(main_country_a2_by_all_names_index, 'sort')
#
# # parent_index = create_index(country_region_db, 'name', 'parent')
# # print_index(parent_index)
# #
# # comment_index = create_index(country_old_db, 'comment', 'a2')
# # print_index(comment_index)
#
# country_region_name_by_code_index = create_index(country_region_db, 'name', 'code')
# # print_names_with_comma(country_region_name_by_code_index)
# # print(country_region_name_by_code_index)
#
# country_old_name_by_a2_index = create_index(country_old_db, 'name', 'a2')
# # #print_names_with_comma(country_old_name_by_a2_index)
# # print(country_old_name_by_a2_index)
#
# # region_and_old_index = merge_indexes([country_region_name_by_code_index, country_old_name_by_a2_index])
# # print(len(country_region_name_by_code_index))
# # print(len(country_old_name_by_a2_index))
# # print(len(region_and_old_index))
# # #print_index(region_and_old_index)
#
# add_base_country(country_region_db, 'code', 'base')
# # # print_index(country_region_db)
# region_index = create_index(country_region_db, 'base', 'name')
# # print_index(region_index)
# chained_index = chain_indexes(region_index, main_country_name_by_a2_index)
# # print_index(main_country_name_by_a2_index)
# print('===')
# print_index(chained_index)
# print(len(chained_index))
#
# country_region_code_by_name_index = create_index(country_region_db, 'code', 'name')
# parent_index = create_index(country_region_db, 'name', 'parent')
# # print_index(parent_index)
# reverse_parent_index = create_index(country_region_db, 'parent', 'name')
# reverse_base_index = create_index(country_region_db, 'base', 'name')
# base_index = create_index(country_region_db, 'name', 'base')
# print_index(chain_indexes(reverse_parent_index, main_country_name_by_a2_index))
# print('===')
# #print_index(chain_indexes(base_index, parent_index, reverse_parent_index, main_country_name_by_a2_index))
# print_index(reverse_parent_index)
#
#
# for k, v in reverse_parent_index.items():
#
#     print(f'{k}: {v}: {main_country_name_by_a2_index.get(get_main_code(v))}: {country_region_code_by_name_index[k]}: {main_country_name_by_a2_index.get(get_main_code(country_region_code_by_name_index[k]))}')
#
# print(main_country_name_by_a2_index.get(get_main_code(country_region_code_by_name_index['Rizal'])))
