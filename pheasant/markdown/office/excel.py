from .common import get_application


def open(path):
    app = get_application('Excel')

    for book in app.Workbooks:
        if book.FullName == path:
            return book
    else:
        book = app.Workbooks.Open(path, ReadOnly=True)
        return book
