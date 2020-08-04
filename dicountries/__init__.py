"""DICOUNTRIES
A library for country name refining and normalization.
To prevent typo errors and using country name synonyms during data analysis.
Normalization is based on ISO3166 database and country name synonyms from Wikipedia
"""

from .metadata import version as __version__


def _need_import():
    import __main__
    return __main__.__file__ != 'setup.py'


if _need_import():
    from .whoosh_patches import *  # Should be the first import
    from .dict_index import *
    from .loader import *
    from .utils import *
    from .whoosh_index import *
