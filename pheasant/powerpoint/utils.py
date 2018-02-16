try:
    import matplotlib
except ImportError:
    matplotlib = None
try:
    import pandas as pd
except ImportError:
    pd = None


def rgb(color, green=None, blue=None):
    """Returns int value for RGB.

    Parameters
    ----------
    color : int, list, or str
    green: int
    blue: int

    Examples
    --------
    >>> rgb(4)
    4
    >>> rgb([100, 200, 40])
    2672740
    >>> rgb('pink')
    13353215
    >>> rgb('#123456')
    5649426
    """
    if green is not None:
        red = color
    elif isinstance(color, int):
        return color
    elif isinstance(color, str):
        color = matplotlib.colors.cnames.get(color, color)
        if not color.startswith('#') or len(color) != 7:
            raise ValueError('colorが文字列のときは，#xxxxxxの形式．')
        red = int(color[1:3], 16)
        green = int(color[3:5], 16)
        blue = int(color[5:7], 16)
    else:
        red, green, blue = color

    return red + green * 256 + blue * 256 * 256


def get_sheet(book, name):
    try:
        return book.sheets[name]
    except Exception:
        return book.sheets.add(name, after=book.sheets(book.sheets.count))


def get_chart(book, name):
    for sheet in book.sheets:
        try:
            return sheet.charts(name)
        except Exception:
            continue


def get_range(book, name, title=False):
    for sheet in book.sheets:
        try:
            range_ = sheet.names(name).refers_to_range
            if title:
                start = range_[0, 0].offset(-1, 0)
                if start.value:
                    return sheet.range(start, range_[-1, -1])
            else:
                return range_
        except Exception:
            continue


def copy_chart(book_from, sheet_to, name):
    chart = get_chart(book_from, name)
    # chart.api[1].ChartArea.Copy()
    chart.api[0].Copy()
    # sheet_to.api.Paste()
    # sheet_to.activate()
    # sheet_to.range('A1').api.Select()
    sheet_to.api.PasteSpecial(Format='PNG', Link=False, DisplayAsIcon=False)
    sheet_to.pictures[-1].name = name


def copy_range(book_from, sheet_to, name, title=False):
    range_ = get_range(book_from, name.replace('-', '__'), title=title)
    range_.api.CopyPicture()  # Appearance:=xlScreen, Format:=xlPicture)
    # sheet_to.activate()
    # sheet_to.range('A1').api.Select()
    sheet_to.api.Paste()
    sheet_to.pictures[-1].name = name.replace('__', '-')
