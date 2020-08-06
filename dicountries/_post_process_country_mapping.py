"""This is a helper file. It generates the data/post_process_country_mapping.json file"""

from typing import Dict

POST_PROCESS_COUNTRY_MAPPING: Dict[str, str] = {
    # "United States": "UUU"
}

import json
import os

DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')

with open(os.path.join(DATA_DIR, 'post_process_country_mapping.json'), 'wt', encoding='utf8') as f:
    json.dump(POST_PROCESS_COUNTRY_MAPPING, f, indent=2, ensure_ascii=False)
