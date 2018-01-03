from .common import get_application


def open(path):
    app = get_application('PowerPoint')

    for prs in app.Presentations:
        if prs.FullName == path:
            return prs
    else:
        prs = app.Presentations.Open(path, ReadOnly=True, Untitled=False,
                                     WithWindow=False)
        return prs
