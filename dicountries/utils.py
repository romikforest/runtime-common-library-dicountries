

def get_main_code(code):
    return code.split('-')[0]


def reorder_name(name):
    if not ',' in name:
        return name
    name = name.split(',')
    name = [ n.strip() for n in name ]
    name = name[1:] + [ name[0] ]
    name = ' '.join(name)
    return name
