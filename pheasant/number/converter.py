import json
import logging
import os

from jinja2 import Environment, FileSystemLoader

from .config import config
from .header import convert as convert_header
from .reference import convert as convert_reference

logger = logging.getLogger(__name__)


def initialize():
    config['pages'] = []
    default_directory = os.path.join(os.path.dirname(__file__), 'templates')
    template_directory, template_file = os.path.split(config['template_file'])
    env = Environment(
        loader=FileSystemLoader([template_directory, default_directory]),
        autoescape=False
    )
    config['template'] = env.get_template(template_file)


def convert(source):
    from ..converters import get_source_file
    source_file = get_source_file()
    if source_file not in config['pages']:
        config['pages'].append(source_file)

    page_index = [config['pages'].index(source_file) + 1]
    logger.info(f'Page index for {source_file}: {page_index}')

    tag = {}
    source, tag = convert_header(source, tag, page_index)
    for key in tag:
        tag[key].update(path=source_file)

    if os.path.exists(config['tag_file']):
        with open(config['tag_file'], 'r') as file:
            tag_all = json.load(file)
    else:
        tag_all = {}

    tag_all.update(tag)

    if os.path.exists(config['tag_file']):
        os.remove(config['tag_file'])
    with open(config['tag_file'], 'w') as file:
        json.dump(tag_all, file)

    for key in tag_all:
        id = tag_all[key]
        relpath = os.path.relpath(id['path'], os.path.dirname(source_file))
        relpath = relpath.replace('\\', '/')
        if config['relpath_function']:
            relpath = config['relpath_function'](relpath)
        else:
            relpath = relpath.replace('.ipynb', '')  # for MkDocs
        id['ref'] = '#'.join([relpath, tag_all[key]['id']])

    source = convert_reference(source, tag_all)

    return source
