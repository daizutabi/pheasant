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
    shape : shape
    """
    def extract(shape):
        if shape.Title:
            yield shape
        try:
            for shape in shape.GroupItems:
                yield from extract(shape)
        except Exception:
            pass

    for element in getattr(obj, collection_name):
        for shape in element.Shapes:
            yield from extract(shape)


def get_shape_by_title(obj, collection_name, title):
    for shape in extract_shape_with_title(obj, collection_name):
        if shape.Title == title:
            return shape
