try:
    import win32com.client
except ImportError:
    pass

apps = {}


def get_application(name):
    if name not in apps:
        obj = win32com.client.gencache.EnsureDispatch(f'{name}.Application')
        apps[name] = obj
    return apps[name]


def quit(name):
    if name in apps:
        apps[name].Quit()
        del apps[name]


def extract_shape_with_title(obj, collection_name):
    """
    extract shapes with title from all collection of a object.

    parameters
    ----------
    obj : office object (presentation or workbook)

    yield
    ------
    (title, i, js) : tuple
        title : title of shape
        i : slide or worksheet number
        js : list of index of shape from shapes collection.
             if len(js) > 1, shape is grouped.
    """
    def extract(shape, i, js):
        if len(js) == 1:  # top-level shape, not grouped.
            # TODO: cache shape's dimension (left, top, left+width, top+height)
            pass

        if shape.Title:
            yield shape.Title, i, js
        try:
            for k, shape in enumerate(shape.GroupItems):
                yield from extract(shape, i, js + [k + 1])
        except Exception:
            pass

    for i, element in enumerate(getattr(obj, collection_name)):
        for j, shape in enumerate(element.Shapes):
            yield from extract(shape, i + 1, [j + 1])


def get_shape_by_title(obj, collection_name, title):
    # abspath = obj.FullName

    # TODO: use cache

    for title_, i, js in extract_shape_with_title(obj, collection_name):
        if title_ == title:
            shape = get_shape_from_index(obj, collection_name, i, js)

            # TODO: find overlapped shapes

            return shape


def get_shape_from_index(obj, collection_name, i, js):
    shape = getattr(obj, collection_name)(i).Shapes(js[0])
    if len(js) == 1:
        return shape
    else:
        for k in js[1:]:
            shape = shape.GroupItems(k)
        return shape
