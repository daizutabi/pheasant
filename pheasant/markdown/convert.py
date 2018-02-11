from markdown import Markdown

markdown_converter = Markdown(extensions=['fenced_code', 'tables'])


CLASS = '__CLASS'

fenced_code_converter = Markdown(extensions=['fenced_code', 'codehilite'],
                                 extension_configs={'codehilite':
                                                    {'css_class': CLASS}})


def markdown_convert(source, extensions=None):
    if extensions is None:
        return markdown_converter.convert(source)
    else:
        converter = Markdown(extensions=extensions)
        return converter.convert(source)


def fenced_code_convert(source, cls='codehilite'):
    source = fenced_code_converter.convert(source)
    return source.replace(CLASS, cls)
