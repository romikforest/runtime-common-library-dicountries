"""Some useful utils used by other modules."""


def get_main_code(code: str) -> str:
    """Get code of the main country.

    Args:
        code: a dash delimited country code and region code

    Returns:
        a main country code

    Example:
        If `code` has value "GT-SO" value "GT" will be returned

    """
    return code.split('-')[0]


def reorder_name(name: str) -> str:
    """Reorder `name` splitting by comma.

    Args:
        name: name possible containing comma

    Returns:
        refined name

    Example:
        If `name` is *"Korea, Republic of"* the return value will be *"Republic of Korea"*

    """
    if ',' not in name:
        return name
    name = name.split(',')
    name = [n.strip() for n in name]
    name = name[1:] + [name[0]]
    name = ' '.join(name)
    return name
