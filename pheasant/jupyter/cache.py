

def memoize(func):
    current_source_file = None
    # current_source = []
    # current = {'source_file': None, 'source_code': []}
    # cache = {}

    def deco(cell, kernel_name):
        nonlocal current_source_file
        from ..converters import get_source_file
        source_file = get_source_file()
        if current_source_file != source_file:
            pass
        return func(cell, kernel_name)

    return deco
