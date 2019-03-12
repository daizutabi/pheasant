import re

flags = re.MULTILINE | re.DOTALL
BACKQUOTE_CODE_PATTERN = re.compile(
    r"^(?P<pre>`{3,})(\S*)(.*?)\n(.*?)\n(?P=pre)\n", flags
)
TILDE_CODE_PATTEN = re.compile(r"^(?P<pre>~{3,})(\S*?)(.*?)\n(.*?)\n(?P=pre)\n", flags)

INLINE_CODE_PATTERN = re.compile(r"\{\{(.+?)\}\}")
