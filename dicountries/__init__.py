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

from .metadata import version as __version__


def _need_import():
    import __main__  # pylint: disable=import-outside-toplevel

    return __main__.__file__ != 'setup.py'


if _need_import():
    from .whoosh_patches import *  # isort:skip
    from .base_types import *
    from .dict_index import *
    from .loader import *
    from .utils import *
    from .whoosh_index import *
