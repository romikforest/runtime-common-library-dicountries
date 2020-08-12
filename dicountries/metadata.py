"""Package metadata aggregation."""
import os

# pylint: disable=invalid-name

version_file = os.path.join(os.path.dirname(__file__), 'version.py')
if os.path.isfile(version_file):
    from .version import __version__ as version  # pylint: disable=import-error # type: ignore
else:
    version = 'dev'

name = 'dicountries'
lib_copyright = '2020, SoftwareONE'
author = 'Koptev, Roman'
description = 'Common library to normalize country names for DI project'
lib_license = 'SWO'
url = 'https://swodataintelligence@dev.azure.com/swodataintelligence/Data%20Intelligence%20Scrum/_git/runtime-common-library-dicountries'  # pylint: disable=line-too-long # noqa E501
author_email = 'roman.koptev@softwareone.com'
