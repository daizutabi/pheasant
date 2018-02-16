from itertools import product

import numpy as np

from .format import CellContainer, ContainerStyle
from .style import set_border, set_border_cell, set_fill

try:
    import pandas as pd
except ImportError:
    pd = None
try:
    from win32com.client import constants
except ImportError:
    constants = None



def empty_frame(index, columns, columns_name, index_name):

    def multiindex(index):
        if isinstance(index[0], str):
            return [[i] for i in index]
        else:
            return list(np.array(index).T)

    index = ['a', 'b']
    columns = [['x', 'y', 'a'], ['x', 'y', 'b']]
    index = multiindex(index)
    columns = multiindex(columns)
    index

    empty = np.zeros((len(index[0]), len(columns[0])), dtype=str)
    empty

    df = pd.DataFrame()
    df.columns = list(np.array(columns).T.T)

    df.columns = columns
    df.index = np.array(index)


def create_table(obj, df, left=100, top=100, width=100, height=100,
                 merge=True, index=True, index_name=True, columns_name=True,
                 border_style=None, font_size=10):
    """Create a table from DataFrame."""
    # nrows, ncols = df.shape
    # columns_level = len(df.columns.levels)
    # index_level = len(df.index.levels)
    # blank_row = 1 if df.columns.names else 0
    cell_container = CellContainer(df, merge_cells=merge, index=index,
                                   index_name=index_name,
                                   columns_name=columns_name)
    shape = obj.AddTable(cell_container.nrows, cell_container.ncols,
                         left, top, width, height)
    table = shape.Table

    from .main import Shape
    shape = Shape(shape, parent=obj.parent)

    for cell in shape.table.cells():
        cell.shape.size = font_size

    clear(table)

    # column_width = {}

    for cell in cell_container.cells:
        table_cell = table.Cell(cell.row, cell.col)
        if hasattr(table_cell, 'Shape'):
            text_frame = table_cell.Shape.TextFrame
            text_range = text_frame.TextRange
            text_range.Text = str(cell.val)
            # text_range.Font.Size = font_size
            text_range.Font.Bold = ContainerStyle.style['bold'][cell.type]
            text_range.ParagraphFormat.Alignment = constants.ppAlignCenter
            text_frame.VerticalAnchor = constants.msoAnchorMiddle

        if merge and cell.merge_row is not None and cell.merge_col is not None:
            merge_cell = table.Cell(cell.merge_row, cell.merge_col)
            table_cell.Merge(merge_cell)

    for container in cell_container.containers:
        start = (container.row_min, container.col_min)
        end = (container.row_max, container.col_max)
        border_style = border_style or {}
        set_border(table, start, end, **border_style)
        fill = container.style['fill']
        set_fill(table, start, end, fill)

    shape.table.minimize_height()

    return table


def clear(table):
    table.FirstCol = False
    table.FirstRow = False
    table.HorizBanding = False

    nrows = len(table.Columns(1).Cells)
    ncols = len(table.Rows(1).Cells)
    for row, column in product(range(nrows), range(ncols)):
        cell = table.Cell(row + 1, column + 1)
        if row == 0:
            set_border_cell(cell, 'top', visible=False)
        if column == 0:
            set_border_cell(cell, 'left', visible=False)
        set_border_cell(cell, 'right', visible=False)
        set_border_cell(cell, 'bottom', visible=False)
        cell.Shape.Fill.Visible = False


# def _prepare_frame():
#     df = pd.DataFrame([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])
#     df.index = [['a', 'a', 'a', 'a'], ['x', 'y', 'y', 'z']]
#     df.columns = [['A', 'B', 'B'], ['s', 't', 't']]
#     df.index.names = ['i1', 'i2']
#     df.columns.names = ['c1', 'c2']
#     return df


# def main():
#     pp = xv.PowerPoint()
#
#     df = _prepare_frame()
#
#     for table in pp.tables:
#         table.parent.api.Delete()
#
#     shape = create_table(pp.slide.shapes, df,
#                          left=200, top=100, width=300, height=200,
#                          columns_name=True, index_name=False)
#
#     return shape.table
#
#
# if __name__ == '__main__':
#     table = main()
#
#     text_frame = table.cell(1, 4).shape.api.TextFrame
#     text_range = table.cell(1, 4).shape.api.TextFrame.TextRange
#     text_range.ParagraphFormat.Alignment = constants.ppAlignCenter
#     # text_range.BoundWidth
#     text_frame.VerticalAnchor = constants.msoAnchorMiddle
#
#     table.parent.parent.parent.api.PageSetup.SlideWidth
#     table.parent.parent.parent.api.PageSetup.SlideHeight
