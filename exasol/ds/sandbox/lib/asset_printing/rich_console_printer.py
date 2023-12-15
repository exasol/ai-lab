from abc import ABC
from typing import Optional, Tuple

import rich.table
from rich.console import Console
from rich.text import Text

from exasol.ds.sandbox.lib.asset_printing.printing_factory import (
    CodeBlockTextObject,
    HighlightedTextObject,
    PrintingFactory,
    TextObject,
    TablePrinter,
    TitleTextObject,
    TextPrinter,
)


class RichConsoleTablePrinter(TablePrinter, ABC):
    def __init__(self, title: str):
        self.table = rich.table.Table(title=title)

    def add_column(self, title: str, **argv):
        self.table.add_column(title, **argv)

    def add_row(self, *args):
        self.table.add_row(*args)

    def finish(self):
        console = Console()
        console.print(self.table)


class RichConsoleTextPrinter(TextPrinter, ABC):

    def _style(self, obj: TextObject) -> Optional[str]:
        if isinstance(obj, TitleTextObject):
            return "italic", "\n\n"
        if isinstance(obj, HighlightedTextObject):
            return "italic blue", ""
        if isinstance(obj, CodeBlockTextObject):
            return "cyan", ""
        return None, None

    def print(self, text_objects: Tuple[TextObject, ...]):
        text = Text()
        for text_object in text_objects:
            style, suffix = self._style(text_object)
            if style is None:
                text.append(text_object.text)
            else:
                text.append(text_object.text + suffix, style=style)
        console = Console()
        console.print(text)


class RichConsolePrintingFactory(PrintingFactory, ABC):

    def create_table_printer(self, title: str):
        return RichConsoleTablePrinter(title)

    def create_text_printer(self, console_only: bool = False):
        return RichConsoleTextPrinter()
