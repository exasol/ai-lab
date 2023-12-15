import abc
from typing import Optional, Tuple
from enum import Enum


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
    def __init__(self, text: str):
        self.text = text


class HighlightedTextObject(TextObject):
    pass


class TitleTextObject(TextObject):
    pass


class CodeBlockTextObject(TextObject):
    pass


class TextPrinter(abc.ABC):
    @abc.abstractmethod
    def print(self, text_objects: Tuple[TextObject, ...]):
        pass


class PrintingFactory(abc.ABC):

    @abc.abstractmethod
    def create_table_printer(self, title: str) -> TablePrinter:
        pass

    @abc.abstractmethod
    def create_text_printer(self, console_only: bool = False) -> TextPrinter:
        pass
