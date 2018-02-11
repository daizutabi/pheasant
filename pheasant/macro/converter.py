import logging
import re

from ..utils import read_source
from .config import config

logger = logging.getLogger(__name__)


def initialize():
    pass


def convert(source):
    source = read_source(source)
    return convert_macro(source)


def convert_macro(source):
    return '\n'.join(renderer(source))


def renderer(source):
    macros = {}

    def replace(m):
        macro = m.group(1)
        return macros.get(macro, 'XXX')

    re_match = re.compile('^' + config['tag_pattern'] + ':(.+)$')
    re_sub = re.compile(config['tag_pattern'])
    lines = source.split('\n')
    for line in lines:
        m = re_match.match(line)
        if m:
            macros[m.group(1)] = m.group(2).strip()
        else:
            yield re_sub.sub(replace, line)
