import re

flags = re.MULTILINE | re.DOTALL
FENCED_CODE_PATTERN = re.compile(r"^```(\S+)(.*?)\n(.*?)\n```\n", flags)
ESCAPE_PATTEN = re.compile(r"^~~~(\S*)(.*?)\n(.*?)\n~~~\n", flags)
