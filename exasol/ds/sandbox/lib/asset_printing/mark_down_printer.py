import io
import pandas as pd

from abc import ABC
from typing import Optional, Tuple
from inspect import cleandoc

from exasol.ds.sandbox.lib.asset_printing.printing_factory import (
    CodeBlockTextObject,
    HighlightedTextObject,
    TitleTextObject,
    PrintingFactory,
    TablePrinter,
    TextObject,
    TextPrinter,
)


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
    def __init__(self, target: io.TextIOBase):
        self.target = target

    def _format(self, obj: TextObject) -> Optional[str]:
        if isinstance(obj, TitleTextObject):
            return f'#### {obj.text}\n'
        if isinstance(obj, CodeBlockTextObject):
            return cleandoc(f"""
            ```shell
            {obj.text}
            ```
            """)
        return f'{obj.text}\n'

    def print(self, text_objects: Tuple[TextObject, ...]):
        for text_object in text_objects:
            print(self._format(text_object), file=self.target)


class NullPrinter(TextPrinter):
    def print(self, text_objects: Tuple[TextObject, ...]):
        pass


class MarkdownPrintingFactory(PrintingFactory, ABC):
    def __init__(self, target: io.TextIOBase):
        self.target = target

    def create_table_printer(self, title: str):
        return MarkdownTablePrinter(title, self.target)

    def create_text_printer(self, console_only: bool = False):
        if console_only:
            return NullPrinter()
        return MarkdownTextPrinter(self.target)
