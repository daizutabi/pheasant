import os

template_file = os.path.join(os.path.dirname(__file__),
                             'templates/number.jinja2')
config = {'pages': [], 'template_file': template_file,
          'kind': {'figure': {'prefix': 'Figure', 'class': 'pheasant-figure'},
                   'table': {'prefix': 'Table', 'class': 'pheasant-table'}
                   }
          }
