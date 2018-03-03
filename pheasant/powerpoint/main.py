import os
import re
import sys
import tempfile

import inflection

# import xlwings as xw
from .table import create_table
from .utils import rgb

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None
try:
    from PIL import Image
except ImportError:
    Image = None

platform = 'win' if sys.platform.startswith('win') else 'mac'

if platform == 'win':
    import pywintypes
    from win32com.client import constants, gencache
    gencache.EnsureModule(
        '{2DF8D04C-5BFA-101B-BDE5-00AA0044DE52}', 0, 2, 1,
        bForDemand=True)  # Office 9
    gencache.EnsureModule(
        '{00020813-0000-0000-C000-000000000046}', 0, 1, 3,
        bForDemand=True)  # Excel 9
else:
    pass


class Collection:
    def __init__(self, parent, type):
        self.parent = parent
        self.type = type
        self.api = getattr(parent.api, self.__class__.__name__)

    def __call__(self, index):
        return self.type.from_collection(self, index)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return list(self)[index]
        if index < 0:
            index = len(self) + index
        return self(index + 1)

    def __len__(self):
        return self.api.Count

    def __getattr__(self, item):
        item = inflection.camelize(item)
        return getattr(self.api, item)

    def __iter__(self):
        for index in range(len(self)):
            yield self[index]

    def __repr__(self):
        clsname = self.__class__.__name__
        items = ', '.join(map(repr, self))
        return f'{clsname}([{items}])'


class Element:
    def __init__(self, api, parent=None):
        self.api = api
        self.parent = parent

    @property
    def name(self):
        try:
            return self.api.Name
        except pywintypes.com_error:
            return ''

    @classmethod
    def from_collection(cls, collection, index=None):
        if index is None:
            index = len(collection)
        return cls(collection.api(index), parent=collection.parent)

    def select(self):
        self.api.Select()

    def delete(self):
        self.api.Delete()


class PowerPoint:
    def __init__(self):
        self.api = gencache.EnsureDispatch('PowerPoint.Application')

    def __repr__(self):
        return f'<PowerPoint App ({id(self)})>'

    @property
    def presentations(self):
        return Presentations(self)

    @property
    def presentation(self):
        return self.presentations.active

    @property
    def slides(self):
        return self.presentation.slides

    @property
    def slide(self):
        return self.slides.active

    @property
    def shapes(self):
        return self.slide.shapes

    @property
    def tables(self):
        return self.slide.tables

    def add_picture(self, *args, **kwargs):
        return self.slide.shapes.add_picture(*args, **kwargs)

    def add_frame(self, *args, **kwargs):
        return self.slide.shapes.add_frame(*args, **kwargs)

    def add_range(self, *args, **kwargs):
        return self.slide.shapes.add_range(*args, **kwargs)

    def add_chart(self, *args, **kwargs):
        return self.slide.shapes.add_chart(*args, **kwargs)

    def add_label(self, *args, **kwargs):
        return self.slide.shapes.add_label(*args, **kwargs)

    def add_shape(self, *args, **kwargs):
        return self.slide.shapes.add_shape(*args, **kwargs)

    def add_table(self, *args, **kwargs):
        return self.slide.shapes.add_table(*args, **kwargs)


class Presentations(Collection):
    def __init__(self, parent):
        super().__init__(parent, Presentation)

    def open(self, filename, read_only=True, untitled=False, with_window=True):
        filename = os.path.abspath(filename)
        prs = self.api.Open(
            filename,
            ReadOnly=read_only,
            Untitled=untitled,
            WithWindow=with_window)
        return Presentation(prs, parent=self.parent)

    def add(self, with_window=True):
        prs = self.api.Add(WithWindow=with_window)
        return Presentation(prs, parent=self.parent)

    def close(self):
        self.api.Close()

    @property
    def active(self):
        return Presentation(
            self.parent.api.ActiveWindow.Presentation, parent=self.parent)


class Presentation(Element):
    def __repr__(self):
        return f'<Presentation [{self.name}]>'

    @property
    def slides(self):
        return Slides(self)

    @property
    def name(self):
        return self.api.Name.replace('.pptx', '')

    def close(self):
        self.api.Close()


class Slides(Collection):
    def __init__(self, parent):
        super().__init__(parent, Slide)

    def add(self, index=None, layout=None):
        if index is None:
            index = self.api.Count + 1
        if layout is None:
            try:
                layout = self.api(index - 1).CustomLayout
            except pywintypes.com_error:
                layout = constants.ppLayoutTitleOnly

        if isinstance(layout, int):
            slide = self.api.Add(index, layout)
        else:
            slide = self.api.AddSlide(index, layout)

        return Slide(slide, parent=self.parent)

    @property
    def active(self):
        api = self.parent.parent.api
        index = api.ActiveWindow.Selection.SlideRange.SlideIndex
        return self(index)


class Slide(Element):
    def __repr__(self):
        prs = self.parent.name
        title = self.title or f'({self.name})'
        return f'<Slide [{prs}]{title}>'

    @property
    def title(self):
        shapes = list(self.shapes)
        if shapes:
            return shapes[0].text
        else:
            return ''

    @title.setter
    def title(self, text):
        shapes = list(self.shapes)
        if shapes:
            shapes[0].text = text

    @property
    def shapes(self):
        return Shapes(self)

    @property
    def tables(self):
        return Tables(self)


class Shapes(Collection):
    def __init__(self, parent):
        super().__init__(parent, Shape)

    # for matplotlib
    def add_picture(self,
                    fig=None,
                    left=0,
                    top=0,
                    width=None,
                    scale=1,
                    dpi=None):
        if fig is None:
            fig = plt.gcf()
        elif not hasattr(fig, 'savefig'):
            fig = fig.figure

        def func(path):
            path = os.path.abspath(path)

            # To keep the original size of figure, width is set to 300.
            if width is None:
                width_ = 300
                scale_ = scale
            else:
                width_ = width
                scale_ = None
            with Image.open(path) as image:
                size = image.size
            height_ = width_ * size[1] / size[0]

            shape = self.api.AddPicture(
                FileName=path,
                LinkToFile=False,
                SaveWithDocument=True,
                Left=left,
                Top=top,
                Width=width_,
                Height=height_)

            if scale_:
                shape.ScaleWidth(scale, 1)
                shape.ScaleHeight(scale, 1)
            return Shape(shape, parent=self.parent)

        if isinstance(fig, str):
            return func(fig)
        else:
            with tempfile.TemporaryDirectory() as directory:
                path = os.path.join(directory, 'a.png')
                fig.savefig(path, dpi=dpi, bbox_inches='tight')
                return func(path)

    def add_frame(self, df, left=None, top=None, **kwargs):
        pass
        # TODO: Write df to excel sheet
        # excel = xw.App(visible=False)
        # book = excel.books(1)
        # sheet = book.sheets(1)
        # range.api.Copy()

        # self.parent.api.Select()
        # n = len(self)
        # api = self.parent.parent.parent.api
        # api.CommandBars.ExecuteMso('PasteSourceFormatting')
        # while len(self) == n:  # wait for creating a table
        #     pass
        # book.api.CutCopyMode = False  # Don't show confirm message
        # excel.quit()
        # excel.kill()
        #
        # shape = Shape.from_collection(self)  # type: Shape
        # if left:
        #     shape.left = left
        # if top:
        #     shape.top = top
        #
        # shape.table.clean()
        # shape.table.minimize_height()
        #
        # return shape

    def add_range(self,
                  range_,
                  data_type=2,
                  left=None,
                  top=None,
                  width=None,
                  height=None):
        """

        Parameters
        ----------
        range_ : xlwings.Range
        data_type : int
            0: ppPasteDefault
            1: ppPasteBitmap
            2: ppPasteEnhancedMetafile
            4: ppPasteGIF
            8: ppPasteHTML
            5: ppPasteJPG
            3: ppPasteMetafilePicture
            10: ppPasteOLEObject
            6: ppPastePNG
            9: ppPasteRTF
            11: ppPasteShape
            7: ppPasteText
        left, top, width, height: int, optional
            Dimension of the shape

        Returns
        -------
        Shape
        """
        range_.api.Copy()
        shape = self.api.PasteSpecial(data_type)
        # range.sheet.book.api.CutCopyMode = False
        shape.LockAspectRatio = 0
        if left:
            shape.Left = left
        if top:
            shape.Top = top
        if width:
            shape.Width = width
        if height:
            shape.Height = height

        return Shape(shape, parent=self.parent)

    def add_chart(self, chart, left=None, top=None, width=None, height=None):
        """
        Parameters
        ----------
        chart : Chart of xlwings
        left, top, width, height: int, optional
            Dimension of shape

        Returns
        -------
        Shape
        """
        if isinstance(chart, list):
            charts = chart
            left_ = charts[0].left
            top_ = charts[0].top
            shapes = []
            for chart in charts:
                shape = self.add_chart(
                    chart,
                    left=chart.left - left_ + left,
                    top=chart.top - top_ + top,
                    width=width,
                    height=height)
                shapes.append(shape)
            return shapes

        chart.api[0].Copy()
        shape = self.api.Paste()
        if left:
            shape.Left = left
        if top:
            shape.Top = top
        if width:
            shape.Width = width
        if height:
            shape.Height = height

        return Shape(shape, parent=self.parent)

    def add_label(self, text, left, top, width=72, height=72, **kwargs):
        orientation = 1  # msoTextOrientationHorizontal
        shape = self.api.AddLabel(orientation, left, top, width, height)
        shape = Shape(shape, parent=self.parent)
        shape.text = text
        shape.set_style(**kwargs)
        return shape

    def add_shape(self, type, left, top, width, height, text=None, **kwargs):
        shape = self.api.AddShape(type, left, top, width, height)
        shape = Shape(shape, parent=self.parent)
        if text:
            shape.text = text
        shape.set_style(**kwargs)
        return shape

    def add_table(self,
                  df,
                  left=None,
                  top=None,
                  width=None,
                  height=None,
                  merge=True,
                  **kwargs):
        table = create_table(
            self,
            df,
            left=100,
            top=100,
            width=300,
            height=300,
            merge=merge,
            **kwargs)
        shape = table.table
        if width:
            table.width = width
        if height:
            table.height = height
        if left is not None:
            shape.left = left
        if top is not None:
            shape.top = top

        return table


class Shape(Element):
    def __repr__(self):
        parent = repr(self.parent)
        parent = parent[parent.index(' ') + 1:-1]
        name = self.text[:20] or f'({self.name})'
        return f'<Shape {parent}!{name}>'

    @property
    def left(self):
        return self.api.Left

    @left.setter
    def left(self, value):
        prs = self.parent.parent
        if value == 'center':
            value = (prs.api.PageSetup.SlideWidth - self.width) // 2
        elif value < 0:
            value = prs.api.PageSetup.SlideWidth - self.width + value
        self.api.Left = value

    @property
    def top(self):
        return self.api.Top

    @top.setter
    def top(self, value):
        prs = self.parent.parent
        if value == 'center':
            value = (prs.api.PageSetup.SlideHeight - self.height) // 2
        elif value < 0:
            value = prs.api.PageSetup.SlideHeight - self.height + value
        self.api.Top = value

    @property
    def width(self):
        return self.api.Width

    @width.setter
    def width(self, value):
        self.api.Width = value

    @property
    def height(self):
        return self.api.Height

    @height.setter
    def height(self, value):
        self.api.Height = value

    @property
    def table(self):
        if self.api.HasTable:
            return Table(self.api.Table, parent=self)

    @property
    def text_range(self):
        return self.api.TextFrame.TextRange

    @property
    def text(self):
        try:
            return self.text_range.Text
        except pywintypes.com_error:
            return ''

    @text.setter
    def text(self, value):
        self.text_range.Text = value

    @property
    def font(self):
        return self.text_range.Font

    @property
    def size(self):
        return self.font.Size

    @size.setter
    def size(self, value):
        self.font.Size = value

    @property
    def bold(self):
        return self.font.Bold

    @bold.setter
    def bold(self, value):
        self.font.Bold = value

    @property
    def italic(self):
        return self.font.Italic

    @italic.setter
    def italic(self, value):
        self.font.Italic = value

    @property
    def color(self):
        return self.font.Color.RGB

    @color.setter
    def color(self, value):
        self.font.Color.RGB = rgb(value)

    @property
    def fill_color(self):
        return self.api.Fill.ForeColor.RGB

    @fill_color.setter
    def fill_color(self, value):
        self.api.Fill.ForeColor.RGB = rgb(value)

    @property
    def line_color(self):
        return self.api.Line.ForeColor.RGB

    @line_color.setter
    def line_color(self, value):
        self.api.Line.ForeColor.RGB = rgb(value)

    @property
    def line_weight(self):
        return self.api.Line.Weight

    @line_weight.setter
    def line_weight(self, value):
        self.api.Line.Weight = value

    def set_style(self,
                  size=None,
                  bold=None,
                  italic=None,
                  color=None,
                  fill_color=None,
                  line_color=None,
                  line_weight=None):
        if size is not None:
            self.size = size
        if bold is not None:
            self.bold = bold
        if italic is not None:
            self.italic = italic
        if color is not None:
            self.color = color
        if fill_color is not None:
            self.fill_color = fill_color
        if line_color is not None:
            self.line_color = line_color
        if line_weight is not None:
            self.line_weight = line_weight


class Tables:
    def __init__(self, slide):
        tables = [shape.table for shape in slide.shapes]
        self._tables = [table for table in tables if table is not None]

    def __getitem__(self, item):
        return self._tables[item]

    def __len__(self):
        return len(self._tables)

    def __iter__(self):
        return iter(self._tables)

    def __call__(self, index):
        return self[index - 1]

    def __repr__(self):
        clsname = self.__class__.__name__
        items = ', '.join(map(repr, self))
        return f'{clsname}([{items}])'


class Table(Element):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = None

    def __len__(self):
        return len(self.rows)

    def __iter__(self):
        rows, columns = self.shape

        def row_iter(row):
            for column in range(columns):
                yield self.cell(row + 1, column + 1)

        for row in range(rows):
            yield row_iter(row)

    def __call__(self, i, j):
        return self.cell(i, j)

    def __repr__(self):
        parent = repr(self.parent)
        parent = parent[parent.index(' ') + 1:-1]
        return f'<Table {parent}{self.shape}>'

    def cell(self, i, j=None):
        if j is None:
            n = len(self.columns)
            i, j = (i - 1) // n + 1, (i - 1) % n + 1
        return Cell(self.api.Cell(i, j), parent=self)

    def options(self, type):
        self.type = type
        return self

    @property
    def shape(self):
        return len(self.rows), len(self.columns)

    @property
    def left(self):
        return self.parent.left

    @left.setter
    def left(self, value):
        self.parent.left = value

    @property
    def top(self):
        return self.parent.top

    @top.setter
    def top(self, value):
        self.parent.top = value

    @property
    def value(self):
        values = [[cell.text for cell in row] for row in self]
        if self.type:
            values = self.type(values)
            self.type = None
        return values

    def items(self):
        for row in self:
            for cell in row:
                yield cell.text, cell

    def cells(self, row=None, column=None, start=None, dropna=True):
        if row is not None or column is not None:
            yield from self.cells_with_label(row, column, start, dropna)
        else:
            for _, cell in self.items():
                yield cell

    def cells_with_label(self, row, column, start=None, dropna=True):
        """Yield the cell with labeled row and/or column.

        Parameters
        ----------
        row : int
            Row index for label. If 0, no label used.
        column : int
            Column index for label. If 0, no label used.
        start : tuple, optional
            Start cell for loop.
        dropna : bool, optional
            If ture, cell without value is skipped during loop.

        Yields
        -------
        (cell, row_label, column_label)
        """
        if start is None:
            start = (row + 1, column + 1)

        value = self.value
        column_labels = value[row - 1] if row else [None] * len(value[0])
        row_labels = ([row_value[column - 1] for row_value in value]
                      if column else [None] * len(value))

        for i, row in enumerate(self):
            if i < start[0] - 1:
                continue
            for j, cell in enumerate(row):
                if j < start[1] - 1:
                    continue
                if not dropna or (row_labels[i] and column_labels[j]):
                    yield cell, row_labels[i], column_labels[j]

    def row(self, index):
        """Yield a cell from a row.

        Parameters
        ----------
        index : int
            Row index

        Yields
        -------
        cell
        """
        for column in range(self.shape[1]):
            yield self.cell(index, column + 1)

    def column(self, index):
        """Yield a cell from a column.

        Parameters
        ----------
        index : int
            Column index

        Yields
        -------
        cell
        """
        for row in range(self.shape[0]):
            yield self.cell(row + 1, index)

    def apply(self, func, *args, pattern=None, **kwargs):
        """Apply a function to each cell.

        Parameters
        ----------
        func : callable
        args
        pattern
        kwargs
        """
        if isinstance(pattern, str):
            match = re.compile(pattern).match
        else:
            match = None

        for cell in self.cells():
            if match and not match(cell.value):
                continue
            func(cell, *args, **kwargs)

    def clean(self):
        """Convert the zenkaku space to normal space."""
        rows, columns = self.shape
        for row in range(rows):
            for column in range(columns):
                cell = self.cell(row + 1, column + 1)
                if cell.text == '\u3000':
                    cell.text = ''

    def minimize_height(self):
        for row in self.rows:
            row.height = 1

    @property
    def columns(self):
        return Columns(self)

    @property
    def rows(self):
        return Rows(self)

    @property
    def width(self):
        return [column.width for column in self.columns]

    @width.setter
    def width(self, value):
        if isinstance(value, list):
            for column, width in zip(self.columns, value):
                column.width = width
        else:
            self.parent.width = value

    @property
    def height(self):
        return [row.height for row in self.rows]

    @height.setter
    def height(self, value):
        if isinstance(value, list):
            for row, height in zip(self.rows, value):
                row.height = value
        else:
            self.parent.height = value


class Columns(Collection):
    def __init__(self, parent):
        super().__init__(parent, Column)


class Column(Element):
    @property
    def width(self):
        return self.api.Width

    @width.setter
    def width(self, value):
        self.api.Width = value


class Rows(Collection):
    def __init__(self, parent):
        super().__init__(parent, Row)


class Row(Element):
    @property
    def height(self):
        return self.api.Height

    @height.setter
    def height(self, value):
        self.api.Height = value


class Cell(Element):
    def __repr__(self):
        parent = repr(self.parent.parent)
        parent = parent[parent.index(' ') + 1:-1]
        return f'<Cell {parent}>'

    @property
    def shape(self):
        return Shape(self.api.Shape, parent=self)

    @property
    def text(self):
        return self.shape.text

    @text.setter
    def text(self, value):
        self.shape.text = value

    @property
    def value(self):
        return self.text

    @value.setter
    def value(self, value):
        self.text = value

    @property
    def left(self):
        return self.shape.left

    @property
    def top(self):
        return self.shape.top

    @property
    def width(self):
        return self.shape.width

    @property
    def height(self):
        return self.shape.height

    def align(self, shape, pos=(0, 0)):
        x, y = pos
        shape.left = (2 * self.left + (self.width - shape.width) * (1 + x)) / 2
        shape.top = (2 * self.top + (self.height - shape.height) * (1 - y)) / 2

    def add_label(self, text, pos=(-0.98, 0.98), **kwargs):
        shapes = self.parent.parent.parent.shapes
        shape = shapes.add_label(text, 100, 100, **kwargs)
        self.align(shape, pos=pos)

    def add_picture(self, fig=None, scale=0.98, pos=(0, 0), **kwargs):
        slide = self.parent.parent.parent
        shape = slide.shapes.add_picture(
            fig=fig, width=self.width * scale, **kwargs)
        self.align(shape, pos=pos)

    def add_frame(self, df, pos=(0, 0), font_size=7, **kwargs):
        slide = self.parent.parent.parent
        shape = slide.shapes.add_frames(df, font_size=font_size, **kwargs)
        self.align(shape, pos=pos)


def _prepare_frame():
    import pandas as pd
    df = pd.DataFrame([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])
    df.index = [['a', 'a', 'a', 'a'], ['x', 'y', 'y', 'z']]
    df.columns = [['A', 'B', 'B'], ['s', 't', 't']]
    df.index.names = ['i1', 'i2']
    df.columns.names = ['c1', 'c2']
    return df
