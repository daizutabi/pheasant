"""Decorators are provided to control run-export process."""

import logging
import os
from functools import wraps

from pheasant.jupyter.config import config

logger = logging.getLogger('mkdocs')


def memoize(func):
    """
    Store the execute-export results in cache.

    If a code is changed, the following markdown results are deleted
    and will be execute later.
    """
    cache = {}

    @wraps(func)
    def decorator(code, *args, **kwargs):
        from pheasant.converters import get_source_file
        source_file = get_source_file()
        counter = config.setdefault('run_counter', 0)
        config['run_counter'] += 1

        code_markdown = cache.get(source_file, [])
        if len(code_markdown) >= counter + 1:
            code_before, markdown = code_markdown[counter]
            if code == code_before:
                return markdown

        if source_file:
            msg = f'Running code: {os.path.basename(source_file)}:{counter}'
            logger.debug(msg)

        markdown = func(code, *args, **kwargs)

        cache[source_file] = code_markdown[:counter] + [(code, markdown)]
        return markdown

    return decorator
