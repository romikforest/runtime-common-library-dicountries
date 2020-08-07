"""Base type hints, used by dicountries library."""

# from typing import List, Dict, Union, Recursive
# JSONType = Union[None, bool, float, str, List['JSONType'], Dict[str, 'JSONType']]

from typing import (
    Any,
    MutableMapping,
    MutableSequence,
    Sequence,
    Union
)

try:
    from typing import Literal  # type: ignore # pylint: disable=no-name-in-module
except ImportError:
    from typing_extensions import Literal  # type: ignore # pylint: disable=no-name-in-module

JSONType = Any
"""Type hint for json objects"""

DictDB = MutableMapping[str, MutableMapping[str, str]]
"""Type hint for dict-like databases"""

ListDB = MutableSequence[MutableMapping[str, str]]
"""Type hint for list-like databases"""

SimpleDB = Union[ListDB, DictDB]
"""Type hint for simple databases (dict-like or list-like)"""

Index = MutableMapping[str, str]
"""Type hint for dict indexes"""

StringMap = MutableMapping[str, str]
"""Type hint for string-string map"""

FieldsDescription = Union[str, Sequence[str]]
"""Type hint for fields descripton (fild name or sequence of field names)"""

SplitPolicies = Literal['None', 'sort', 'split']
"""Split policies:

    * **None** - do nothing, just add to index as is
    * **sort** - refine second_field value
    * **split** - split value by commas and use them all as possible search values
"""
