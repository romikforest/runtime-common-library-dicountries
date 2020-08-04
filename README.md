<header><font size="+12">DiCountries introduction</font></header>

# About

Country name normalization for DataIntelligence project

**Author:** *Koptev, Roman ([roman.koptev@softwareone.com](mailto:roman.koptev@softwareone.com))*

**Copyright ©:** *2020, SoftwareONE*

# Quick start

## Installation

To use the module from this repository you need to have a working [python](https://www.python.org/)
installation (version >= 3.6.0) with pre-installed [pip](https://pypi.org/project/pip/) package installer.
I suppose you can run the python and pip executables using `python` and `pip` commands. Depending on
your setup you may have to run them like `python3` and `pip3` or using other aliases. The recommended
way to install these scripts is to execute commands like:

```shell script
python -m install -U pip
python -m install -U dicountries 
```

In order to access the azure artifact feed you need to set up your pip to use appropriate indices.
E.g. you can set `PIP_EXTRA_INDEX_URL` environment variable like:

```shell script
export PIP_EXTRA_INDEX_URL="https://di_libraries:<access token>@pkgs.dev.azure.com/swodataintelligence/71b5c973-6f2c-42b7-a0a9-8af59f1bf7ee/_packaging/di_libraries_test/pypi/simple/"
```

or you can add a file pip.ini (Windows) or pip.conf (Mac/Linux) to your virtualenv
with the content like this:

```ini
[global]
extra-index-url=https://di_libraries:<access token>@pkgs.dev.azure.com/swodataintelligence/71b5c973-6f2c-42b7-a0a9-8af59f1bf7ee/_packaging/di_libraries_test/pypi/simple/
```

The template `<access token>` should be substituted with your valid access token that
should have **Packaging Read** access rights. You can create this token in your AzureDevOps account.

## Usage

A simple usage example:

```python
from dicountries.whoosh_index import CountryIndex

country_index = CountryIndex()
country_index.refresh()

print(country_index.normalize_country('Россия'))
print(country_index.refine_country('Korea, Republic of'))
```

The expected output will have lines like these in the end:

```
Russian Federation
Republic of Korea
```

The function `normalize_country` returns a normalized country name if possible
(looking in country indexes and using fuzzy search),
otherwise it returns the country name from the incoming parameter.

This function will try to return the country name accordingly to the ISO 3166 standard.
But if a substitution for this name is determined in the file
`post_process_country_mapping.json` in the package's data directory that
substitution will be returned.

You can force to not use substitutions from the `post_process_country_mapping.json`
using the input parameter `postprocess=False`:

```python
print(country_index.normalize_country('Россия', postprocess=False))

```

The function `refine_country` will return the same value as the `normalize_country`,
but if there is a comma \[,\] in the returned name it will recombine the name so that
the part after the comma will precede the part before the comma. The comma will be
deleted.

You can also do this transformation on any string using function `reorder_name(name)`
from the `dicountries.utils` module.

Every time you run this script it will create a subdirectory `indexes` in
the current working directory to backup indexes there. You can pass the index
directory explicitly to the `CountryIndex` constructor like this:

```python
country_index = CountryIndex(index_path="<Your index directory>")
```

If you don't want the index being rebuilded every time the script is runnig
just ommit the line:

```python
country_index.refresh()
```

Without this line the index will be rebuilded only if it does not exist, otherwise
it will be read from the index directory (it's faster).

If you want the index to be updated as a background process or you want to have
asyncio integration you can pass the parameter `use_async=True` to the `CountryIndex`
constructor. Also there is an async function for index refreshig:

```python
await country_index.refresh_async()
```

The search process is normally optimized and uses a cache. You can control the size of
the cache using the `max_search_cache` parameter, e.g.:

```python
country_index = CountryIndex(max_search_cache=1000)
```

During the normalization the search process usually checks the cache first. If some
country is not found in the cache more complicated techniques will be used.
Every found country is placed to the simple cache, but if the cache riches
`max_search_cache` size it will be reinitialized and the search process will start
from scratch.



