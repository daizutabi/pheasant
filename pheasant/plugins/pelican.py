from markdown import Markdown
from pelican import signals
from pelican.readers import MarkdownReader
from pheasant.converters import convert


class PheasantReader(MarkdownReader):
    enabled = True

    file_extensions = ['md', 'ipynb']

    def read(self, source_path):
        """Parse content and metadata of markdown and notebook files"""
        config = self.settings.get('PHEASANT', {'jupyter': {}})
        text = convert(source_path, config)

        self._source_path = source_path
        self._md = Markdown(**self.settings['MARKDOWN'])
        content = self._md.convert(text)

        if hasattr(self._md, 'Meta'):
            metadata = self._parse_metadata(self._md.Meta)
        else:
            metadata = {}

        return content, metadata


def add_reader(readers):
    readers.reader_classes['md'] = PheasantReader
    readers.reader_classes['ipynb'] = PheasantReader


def register():
    signals.readers_init.connect(add_reader)
