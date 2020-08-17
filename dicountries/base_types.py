"""Base type hints, used by dicountries library."""

# from typing import List, Dict, Union, Recursive
# JSONType = Union[None, bool, float, str, List['JSONType'], Dict[str, 'JSONType']]

from typing import Any, MutableMapping, MutableSequence, Sequence, Union

try:
    from typing import Literal  # type: ignore # pylint: disable=no-name-in-module
except ImportError:
    from typing_extensions import Literal  # type: ignore # pylint: disable=no-name-in-module

#: Type hint for json objects
JSONType = Any

#: Type hint for dict-like databases
DictDB = MutableMapping[str, MutableMapping[str, str]]

#: Type hint for list-like databases
ListDB = MutableSequence[MutableMapping[str, str]]

#: Type hint for simple databases (dict-like or list-like)
SimpleDB = Union[ListDB, DictDB]

#: Type hint for dict indexes
Index = MutableMapping[str, str]

#: Type hint for string-string map
StringMap = MutableMapping[str, str]

#: Type hint for fields descripton (fild name or sequence of field names)
FieldsDescription = Union[str, Sequence[str]]

#: Split policies:
#:
#:     * **None** - do nothing, just add to index as is
#:     * **sort** - refine second_field value
#:     * **split** - split value by commas and use them all as possible search values
#:
SplitPolicies = Literal['None', 'sort', 'split']
