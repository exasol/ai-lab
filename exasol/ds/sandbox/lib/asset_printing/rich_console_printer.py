from abc import ABC
from typing import Tuple

import rich.table
from rich.console import Console
from rich.text import Text

from exasol.ds.sandbox.lib.asset_printing.printing_factory import PrintingFactory, TablePrinter, \
    TextPrinter, TextObject


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

    def print(self, text_objects: Tuple[TextObject, ...]):
        text = Text()
        for text_object in text_objects:
            if text_object.highlight_key:
                text.append(text_object.text, style="italic blue")
            else:
                text.append(text_object.text)
        console = Console()
        console.print(text)


class RichConsolePrintingFactory(PrintingFactory, ABC):

    def create_table_printer(self, title: str):
        return RichConsoleTablePrinter(title)

    def create_text_printer(self):
        return RichConsoleTextPrinter()
