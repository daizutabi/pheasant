SITENAME = 'Pelican Example'
SITEURL = 'https://example.com'
TIMEZONE = 'Asia/Tokyo'

RELATIVE_URLS = True
PLUGINS = ['pheasant']

PHEASANT = {
    'jupyter': {'kernel_name': {'python': 'python3'}},
    'number': {'enabled': True, 'level': 2}
}
