from win32com.client import constants

from .utils import rgb


def set_border_cell(cell, pos, width=1, color=0, line_style='-', visible=True):
    pos = getattr(constants, 'ppBorder' + pos[0].upper() + pos[1:])
    border = cell.Borders(pos)
    border.Visible = visible
    if not visible:
        return
    border.Weight = width
    border.ForeColor.RGB = color
    if line_style == '-.':
        border.DashStyle = constants.msoLineDash


def set_border(table, start, end, edge_width=2, inside_width=1, edge_color=0,
               inside_color=rgb(140, 140, 140), edge_line_style='-',
               inside_line_style='-'):

    if inside_width:
        kwargs = dict(width=inside_width, color=inside_color,
                      line_style=inside_line_style)
        for row in range(start[0], end[0] + 1):
            for column in range(start[1], end[1]):
                cell = table.Cell(row, column)
                set_border_cell(cell, 'right', **kwargs)
        for column in range(start[1], end[1] + 1):
            for row in range(start[0], end[0]):
                cell = table.Cell(row, column)
                set_border_cell(cell, 'bottom', **kwargs)

    if edge_width:
        kwargs = dict(width=edge_width, color=edge_color,
                      line_style=edge_line_style)
        for row in range(start[0], end[0] + 1):
            cell = table.Cell(row, start[1])
            set_border_cell(cell, 'left', **kwargs)
            cell = table.Cell(row, end[1])
            set_border_cell(cell, 'right', **kwargs)
        for column in range(start[1], end[1] + 1):
            cell = table.Cell(start[0], column)
            set_border_cell(cell, 'top', **kwargs)
            cell = table.Cell(end[0], column)
            set_border_cell(cell, 'bottom', **kwargs)


def set_fill(table, start, end, fill):
    for row in range(start[0], end[0] + 1):
        for column in range(start[1], end[1] + 1):
            cell = table.Cell(row, column)
            cell.Shape.Fill.ForeColor.RGB = fill


def set_font(table, start, end, size=10):
    for row in range(start[0], end[0] + 1):
        for column in range(start[1], end[1] + 1):
            cell = table.cell(row, column)
            print(cell)
