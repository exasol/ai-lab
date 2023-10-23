import io
from abc import ABC
from typing import Tuple

import pandas as pd

from exasol.ds.sandbox.lib.asset_printing.printing_factory import PrintingFactory, TablePrinter, \
    TextPrinter, TextObject


class MarkdownTablePrinter(TablePrinter, ABC):

    def __init__(self, title: str, target: io.TextIOBase):
        self.title = title
        self.columns = list()
        self.rows = list()
        self.target = target

    def add_column(self, title: str, **argv):
        self.columns.append(title)

    def add_row(self, *args):
        self.rows.append(tuple(args))

    def finish(self):
        df = pd.DataFrame(self.rows, columns=self.columns)
        print(f'#### {self.title}\n{df.to_markdown()}', file=self.target)


class MarkdownTextPrinter(TextPrinter, ABC):

    def print(self, text_objects: Tuple[TextObject, ...]):
        pass


class MarkdownPrintingFactory(PrintingFactory, ABC):

    def __init__(self, target: io.TextIOBase):
        self.target = target

    def create_table_printer(self, title: str):
        return MarkdownTablePrinter(title, self.target)

    def create_text_printer(self):
        return MarkdownTextPrinter()
