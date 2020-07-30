from .metadata import version as __version__
from .whoosh_patches import *

def _need_import():
    import __main__
    return __main__.__file__ != 'setup.py'

if _need_import():
    from .dict_index import *
    from .loader import *
    from .utils import *
    from .whoosh_index import *
