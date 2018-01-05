import logging
import os

from ..office import powerpoint
from ..utils import escaped_splitter, read_source
from .common import get_shape_by_title

logger = logging.getLogger(__name__)


def initialize():
    pass


def convert(source):
    from ..converters import get_source_file
    source_file = get_source_file()
    directory = os.path.dirname(source_file)
    return ''.join(exporter(source, directory))


def exporter(source: str, directory):
    for splitted in office_object_splitter(source):
        if isinstance(splitted, str):
            yield splitted
        else:
            alt = splitted['alt']
            path = os.path.join(directory, splitted['path'])
            path = os.path.abspath(path)
            data = export_shape(path, splitted['tag'])
            yield f'![{alt}]({data})'


def export_shape(path, tag, format='png'):
    # PowerPoint
    prs = powerpoint.open(path)
    shape = get_shape_by_title(prs, 'Slides', tag)
    data = powerpoint.export_shape(shape, format=format)
    data = f'data:image/{format};base64,{data}'
    return data


def office_object_splitter(source: str):
    """
    ![alt](path_to_office_file#shape_title)
    """
    source = read_source(source)
    pattern_escape = r'(^```(.*?)^```$)|(^~~~(.*?)^~~~$)'
    pattern = r'!\[(?P<alt>.+?)\]\((?P<path>.+?\.(xlsx|pptx))#(?P<tag>.+?)\)'

    for splitted in escaped_splitter(pattern, pattern_escape, source):
        if isinstance(splitted, str):
            yield splitted
        else:
            yield splitted.groupdict()
