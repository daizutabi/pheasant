import re
from collections import OrderedDict
from dataclasses import field
from typing import Any, Dict, Iterator, Match, Optional, Pattern

from pheasant.core.base import (Base, Cell, Render, Splitter, get_render_name,
                                make_cell_class, rename_pattern)
from pheasant.core.decorator import Decorator


class Parser(Base):
    patterns: Dict[str, str] = field(default_factory=dict)
    renders: Dict[str, Render] = field(default_factory=OrderedDict)
    cell_classes: Dict[str, type] = field(default_factory=dict)
    pattern: Optional[Pattern] = None
    decorator: Optional[Decorator] = None

    def __post_repr__(self):
        return len(self.patterns)

    def register(self, pattern: str, render: Render, render_name: str = "") -> type:
        if not render_name:
            render_name = get_render_name(render)
        cell_class = make_cell_class(pattern, render, render_name)
        self.cell_classes[render_name] = cell_class
        pattern = rename_pattern(pattern, render_name)
        self.patterns[render_name] = pattern
        self.renders[render_name] = render
        return cell_class

    def parse(self, source: str, decorate=None) -> Iterator[str]:
        splitter = self.split(source)
        next(splitter)
        for cell in splitter:
            if cell.match:
                cell.output = "".join(
                    cell.render(context=cell.context, splitter=splitter, parser=self)
                )
            else:
                cell.output = cell.source
            if decorate:
                decorate(cell)
            elif self.decorator:
                self.decorator.decorate(cell)

            yield cell.output

    def split(self, source: str) -> Splitter:
        """Split the source into a cell and yield it."""
        if not self.patterns:
            raise ValueError("No pattern registered")
        elif self.pattern is None:
            self.pattern = re.compile(
                "|".join(self.patterns.values()), re.MULTILINE | re.DOTALL
            )

        def get(cell, attr=None):
            if attr is None:
                return cell
            else:
                return getattr(cell, attr)

        cursor = 0
        attr = yield
        for match in self.pattern.finditer(source):
            start, end = match.start(), match.end()
            if cursor < start:
                attr = yield get(Cell(source[cursor:start], None, ""), attr)
            attr = yield get(self.resolve(match), attr)
            cursor = end
        if cursor < len(source):
            yield get(Cell(source[cursor:], None, ""), attr)

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
        cell : dataclass instance
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
        source = context.pop("_source")  # FIXME: context["_source"] is better?
        return self.cell_classes[render_name](source, match, "", context)
