import html
import os
import re


def convert(source):
    re_compile = re.compile(r'(src="data:.*?;base64).*?"/>',
                            re.DOTALL | re.MULTILINE)
    source = re_compile.sub(r'\1"/>', source)
    source = html.escape(source)
    source = source.replace('```', ' ```')
    source = f'<pre>{source}</pre>'
    return source
