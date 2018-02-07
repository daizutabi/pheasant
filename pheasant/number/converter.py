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

    abspath = os.path.abspath(config['template_file'])
    template_directory, template_file = os.path.split(abspath)
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

    if config['level'] == 0:
        page_index = [config['pages'].index(source_file) + 1]
    else:
        page_index = config['level']
    logger.info(f'Page index for {source_file}: {page_index}')

    label = {}
    source, label = convert_header(source, label, page_index)
    for key in label:
        label[key].update(path=source_file)

    if os.path.exists(config['label_file']):
        with open(config['label_file'], 'r') as file:
            label_all = json.load(file)
    else:
        label_all = {}

    label_all.update(label)

    if os.path.exists(config['label_file']):
        os.remove(config['label_file'])
    with open(config['label_file'], 'w') as file:
        json.dump(label_all, file)

    for key in label_all:
        id = label_all[key]
        relpath = os.path.relpath(id['path'], os.path.dirname(source_file))
        relpath = relpath.replace('\\', '/')
        if config['relpath_function']:
            relpath = config['relpath_function'](relpath)
        else:
            relpath = relpath.replace('.ipynb', '')  # for MkDocs
        id['ref'] = '#'.join([relpath, label_all[key]['id']])

    source = convert_reference(source, label_all)

    return source
