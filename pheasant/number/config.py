config = {
    'template_file': 'basic.jinja2',
    'kind': ['header', 'figure', 'table', 'code'],
    'tag_file': '.pheasant-number.json',
    'tag_pattern': r'\{#(\S+?)#\}',
    'class': 'pheasant-{kind}',
    'id': 'pheasant-{tag}',
    'relpath_function': None,
    'level': 2,  # numbering level. 0 for multiple pages, 2 for h2 etc.
    'markdown_extensions': [],
}
