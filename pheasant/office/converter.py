import logging
import os

from . import powerpoint
from ..utils import escaped_splitter, read_source
from .common import get_shape_by_title
from .config import config

logger = logging.getLogger(__name__)


def initialize():
    pass


def convert(source):
    from ..converters import get_source_file
    source_file = get_source_file()
    root = os.path.dirname(source_file)
    return ''.join(exporter(source, root))


def exporter(source, root=None):
    if root is None:
        root = os.path.dirname(source)

    for splitted in office_object_splitter(source):
        if isinstance(splitted, str):
            yield splitted
        else:
            alt = splitted['alt']
            abspath = get_abspath(root, splitted['path'])
            data = export_shape(abspath, splitted['tag'])
            yield f'![{alt}]({data})'


def get_abspath(root, path):
    abspath = os.path.abspath(os.path.join(root, path))
    if os.path.exists(abspath):
        return abspath

    for directory in config['file_dirs']:
        abspath = os.path.abspath(os.path.join(root, directory, path))
        if os.path.exists(abspath):
            return abspath
        abspath = os.path.abspath(os.path.join(directory, path))
        if os.path.exists(abspath):
            return abspath
    else:
        raise OSError(f'File not found: {path}')


def export_shape(path, tag, format='png', use_cache=True):
    if use_cache and (path, tag) in config['shape_data']:
        return config['shape_data'][(path, tag)]

    # PowerPoint
    prs = powerpoint.open(path)
    shape = get_shape_by_title(prs, 'Slides', tag)
    data = powerpoint.export_shape(shape, format=format)
    data = f'data:image/{format};base64,{data}'

    config['shape_data'][(path, tag)] = data
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
