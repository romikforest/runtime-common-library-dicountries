"""DICOUNTRIES
A library for country name refining and normalization.
To prevent typo errors and using country name synonyms during data analysis.
Normalization is based on `ISO3166 <https://en.wikipedia.org/wiki/ISO_3166>`_
database and country name synonyms from Wikipedia

Installation::

    % python -m pip install -U pip
    % python -m pip install -U dicountries

Usage example::

    from dicountries.whoosh_index import CountryIndex

    country_index = CountryIndex()
    country_index.refresh()

    print(country_index.normalize_country('Russia'))
    print(country_index.normalize_country('Korea, Republic of'))
    print(country_index.refine_country('Korea, Republic of'))

"""

# flake8: noqa: F401, F403

from dicountries.metadata import version as __version__


def _need_import():
    import inspect  # pylint: disable=import-outside-toplevel

    import __main__  # pylint: disable=import-outside-toplevel

    stack = inspect.stack(0)
    try:
        for entry in stack:
            if hasattr(entry, 'function') and entry.function == 'load_metadata':
                return False
    finally:
        del stack
    return __main__.__file__ != 'setup.py'


if _need_import():
    from dicountries.whoosh_patches import *  # isort:skip
    from dicountries.base_types import *
    from dicountries.dict_index import *
    from dicountries.loader import *
    from dicountries.utils import *
    from dicountries.whoosh_index import *
