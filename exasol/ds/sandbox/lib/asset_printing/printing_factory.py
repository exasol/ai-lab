import abc
from typing import Tuple


class TablePrinter(abc.ABC):
    @abc.abstractmethod
    def add_column(self, title: str, **argv):
        pass

    @abc.abstractmethod
    def add_row(self, *args):
        pass

    @abc.abstractmethod
    def finish(self):
        pass


class TextObject(abc.ABC):
    def __init__(self, text: str, highlight_key: bool = False):
        self.text = text
        self.highlight_key = highlight_key


class HighlightedTextObject(TextObject):
    def __init__(self, text: str):
        super().__init__(text, True)


class TextPrinter(abc.ABC):
    @abc.abstractmethod
    def print(self, text_objects: Tuple[TextObject, ...]):
        pass


class PrintingFactory(abc.ABC):

    @abc.abstractmethod
    def create_table_printer(self, title: str) -> TablePrinter:
        pass

    @abc.abstractmethod
    def create_text_printer(self) -> TextPrinter:
        pass

