import re

from markdown import Markdown
from pelican import signals
from pelican.readers import MarkdownReader

from pheasant.core.pheasant import Pheasant

HEADER_PATTERN = re.compile(r"<[hH][1-6]")


class PheasantReader(MarkdownReader):
    enabled = True

    file_extensions = ["md"]

    converter = Pheasant()

    def read(self, source_path):
        """Parse content and metadata of markdown and notebook files"""
        self.converter.convert_from_files([source_path])
        text = self.converter.pages[source_path].output
        self._source_path = source_path
        self._md = Markdown(**self.settings["MARKDOWN"])
        content = self._md.convert(text)
        content = "\n".join(
            [self.converter.pages[source_path].meta["extra_html"], content]
        )
        if hasattr(self._md, "Meta"):
            metadata = self._parse_metadata(self._md.Meta)
        else:
            metadata = {}

        match = HEADER_PATTERN.search(content)
        if match:
            abstract = content[:match.start()]
            if abstract.strip():
                metadata["abstract"] = abstract
        return content, metadata


def add_reader(readers):
    readers.reader_classes["md"] = PheasantReader


def register():
    signals.readers_init.connect(add_reader)
