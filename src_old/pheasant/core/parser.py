import re
from collections import OrderedDict
from dataclasses import field
from typing import Any, Callable, Dict, List, Match, Optional, Pattern, Union

from pheasant.core.base import (Base, Cell, Render, Splitter, get_render_name,
                                make_cell_class, rename_pattern)
from pheasant.core.decorator import Decorator


class Parser(Base):
    patterns: Dict[str, str] = field(default_factory=dict, init=False)
    renders: Dict[str, Render] = field(default_factory=OrderedDict, init=False)
    cell_classes: Dict[str, type] = field(default_factory=dict, init=False)
    pattern: Optional[Pattern] = field(default=None, init=False)
    decorator: Optional[Decorator] = field(default=None, init=False)

    def __post_repr__(self):
        return len(self.patterns)

    def register(self, pattern: str, render: Render, render_name: str = "") -> type:
        if not render_name:
            render_name = get_render_name(render)
        cell_class = make_cell_class(pattern, render, render_name)
        self.cell_classes[render_name] = cell_class
        pattern = rename_pattern(pattern, render_name)
        self.renders[render_name] = render
        self.patterns[render_name] = pattern
        self.pattern = None  # Delete the pattern compiled before.
        return cell_class

    def parse(self, source: str, decorate: Union[Callable, bool] = True) -> str:
        """Parse the source and deligate the process to a render function.

        Parameters
        ----------
        source
            Source text
        decorate
            If True, parser's decorator is used to decorate the cell with output
            from the renders. If callable, `decorate` directly decorates the cell.

        Returns
        -------
        str
            Rendered and decorated output text.
        """
        splitter = self.split(source)

        def iterator():
            for cell in splitter:
                if cell.match:
                    cell.output = cell.parse(splitter, self)
                else:
                    cell.output = cell.source
                if callable(decorate):
                    decorate(cell)
                elif decorate is True and self.decorator:
                    self.decorator.decorate(cell)
                yield cell.output

        return "".join(iterator())

    def parse_from_cell(self, cell: Any, splitter: Splitter, decorate=True) -> str:
        cell.output = cell.parse(splitter, self)
        if decorate is True and self.decorator:
            self.decorator.decorate(cell)
        return cell.output

    def compile(self):
        self.pattern = re.compile(
            "|".join(self.patterns.values()), re.MULTILINE | re.DOTALL
        )

    def split(self, source: str) -> Splitter:
        """Split the source into a cell and yield it.

        This function returns a Splitter generator. This generator can receive a
        source through `send` method to return the source you get from generator.
        """
        if not self.pattern:
            self.compile()

        def resplit(rework: Optional[str]) -> Splitter:
            if rework is not None:
                yield  # Yields None as a return value for send method.
                yield from self.split(rework)  # Then, yields the same source again.

        cursor = 0
        for match in self.pattern.finditer(source):  # type: ignore
            start, end = match.start(), match.end()
            if cursor < start:
                rework = yield Cell(source[cursor:start], None, "")
                yield from resplit(rework)
            rework = yield self.resolve(match)
            yield from resplit(rework)
            cursor = end
        if cursor < len(source):
            rework = yield Cell(source[cursor:], None, "")
            yield from resplit(rework)

    def resolve(self, match: Match[str]) -> Any:  # Acually, Any is Cell-based instance.
        """Resolve a Match object and return a dataclass instance called `cell`.

        Returned cell contains the required and helpful information for
        rendering the match object such as render's name, render function,
        the groups of the match object as a context, etc.

        Parameters
        ----------
        match
            A match object.

        Returns
        -------
        cell : Cell dataclass instance
        """
        groupdict = match.groupdict()
        render_name = ""

        def rename_for_render(key):
            nonlocal render_name
            if "___" in key:
                return key.split("___")[-1]
            else:
                render_name = key
                return "_source"

        context = {
            rename_for_render(key): value
            for key, value in groupdict.items()
            if value is not None
        }
        source = context["_source"]
        return self.cell_classes[render_name](source, match, "", context)

    def findall(self, source: str) -> List:
        if not self.pattern:
            self.compile()

        return self.pattern.findall(source)  # type: ignore
