import itertools
from typing import Any, Dict

from pandas.io.formats.excel import ExcelFormatter

from .utils import rgb


class CellFormatter:
    def __init__(self, df, index=True):
        self.df = df
        try:
            self.columns_levels = len(df.columns.levels)
        except AttributeError:
            self.columns_levels = 1
        try:
            self.index_levels = len(df.index.levels)
        except AttributeError:
            self.index_levels = 1
        if not index:
            self.index_levels = 0
        self.columns_name_col = self.index_levels - 1
        self.index_name_row = self.columns_levels - 1
        if self.columns_levels > 1:
            self.index_name_row += 1

    def get_type(self, row, col):
        if row > self.index_name_row and col > self.columns_name_col:
            return ContainerStyle.VALUE
        elif row > self.index_name_row and col <= self.columns_name_col:
            return ContainerStyle.INDEX
        elif row == self.index_name_row and col <= self.columns_name_col:
            return ContainerStyle.INDEX_NAME
        elif row < self.columns_levels and col > self.columns_name_col:
            return ContainerStyle.COLUMNS
        elif row < self.columns_levels and col == self.columns_name_col:
            return ContainerStyle.COLUMNS_NAME

    def get_cell(self, cell):
        return Cell(cell, self.get_type(cell.row, cell.col))


class Cell:
    def __init__(self, cell, type):
        self.row = cell.row + 1
        self.col = cell.col + 1
        self.val = cell.val
        self.merge_row = cell.mergestart
        self.merge_col = cell.mergeend
        if self.merge_row is not None:
            self.merge_row += 1
        if self.merge_col is not None:
            self.merge_col += 1
        self.type = type


class ContainerStyle:
    VALUE = 10
    INDEX_NAME = 1
    INDEX = 2
    COLUMNS_NAME = 3
    COLUMNS = 4

    style: Dict[str, Any] = {}
    style['bold'] = {
        VALUE: False,
        INDEX: True,
        INDEX_NAME: True,
        COLUMNS_NAME: True,
        COLUMNS: True
    }
    style['fill'] = {
        VALUE: rgb(255, 255, 255),
        INDEX: rgb(255, 255, 230),
        INDEX_NAME: rgb(255, 255, 180),
        COLUMNS: rgb(230, 255, 255),
        COLUMNS_NAME: rgb(180, 255, 255)
    }
    style['inside_border'] = {
        VALUE: True,
        INDEX: True,
        INDEX_NAME: True,
        COLUMNS_NAME: True,
        COLUMNS: True
    }
    style['around_border'] = {
        VALUE: True,
        INDEX: True,
        INDEX_NAME: True,
        COLUMNS_NAME: True,
        COLUMNS: True
    }
    style['horizontal_alignment'] = {
        VALUE: 'center',
        INDEX: 'center',
        INDEX_NAME: 'center',
        COLUMNS_NAME: 'center',
        COLUMNS: 'center'
    }

    @classmethod
    def get_style(cls, type):
        style_dict = {}
        for key in cls.style:
            style_dict[key] = cls.style[key][type]
        return style_dict


class Container:
    def __init__(self, row_min, row_max, col_min, col_max, type):
        self.row_min = row_min
        self.row_max = row_max
        self.col_min = col_min
        self.col_max = col_max
        self.type = type
        self.style = ContainerStyle.get_style(type)


class CellContainer:
    def __init__(self,
                 df,
                 merge_cells=True,
                 index=True,
                 index_name=True,
                 columns_name=True):
        self.nrows = 0
        self.ncols = 0
        self.cells = []
        self.containers = []

        index_name_offset = 0 if columns_name else -1
        index_offset = 0 if columns_name and index_name else -1

        formatter = ExcelFormatter(df, merge_cells=merge_cells, index=index)
        cell_formatter = CellFormatter(df, index=index)
        for cell in formatter.get_formatted_cells():
            cell = cell_formatter.get_cell(cell)
            if cell.type == ContainerStyle.COLUMNS_NAME:
                if not columns_name:
                    continue
            elif cell.type == ContainerStyle.INDEX_NAME:
                if not index_name:
                    continue
                cell.row += index_name_offset
                if cell.merge_row is not None:
                    cell.merge_row += index_name_offset
            elif (cell.type == ContainerStyle.INDEX
                  or cell.type == ContainerStyle.VALUE):
                cell.row += index_offset
                if cell.merge_row is not None:
                    cell.merge_row += index_offset

            self.cells.append(cell)
            self.nrows = max(self.nrows, cell.row)
            self.ncols = max(self.ncols, cell.col)
        self.groupby()

    def groupby(self):
        self.containers = []
        self.cells = sorted(self.cells, key=lambda cell: cell.type)
        for type, group in itertools.groupby(
                self.cells, key=lambda cell: cell.type):
            row_min = 1e8
            row_max = 0
            col_min = 1e8
            col_max = 0
            for cell in group:
                row_min = min(row_min, cell.row)
                row_max = max(row_max, cell.merge_row
                              if cell.merge_row else cell.row)
                col_min = min(col_min, cell.col)
                col_max = max(col_max, cell.merge_col
                              if cell.merge_col else cell.col)
            container = Container(row_min, row_max, col_min, col_max, type)
            self.containers.append(container)
