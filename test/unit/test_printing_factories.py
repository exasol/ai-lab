import importlib
from contextlib import redirect_stdout
from io import StringIO

import exasol.ds.sandbox.lib.asset_printing.rich_console_printer
from exasol.ds.sandbox.lib.asset_printing.mark_down_printer import MarkdownPrintingFactory
from exasol.ds.sandbox.lib.asset_printing.printing_factory import TextObject
from inspect import cleandoc


def test_markdown_text():
    with StringIO() as buf:
        factory = MarkdownPrintingFactory(buf)
        printer = factory.create_text_printer(console_only=False)
        printer.print((TextObject("Hello"),))
        actual = buf.getvalue()
    assert actual == "Hello\n\n"


def test_printing_markdown(tmp_path):
    test_file = tmp_path / "test.md"
    with open(test_file, "w") as f:
        factory = MarkdownPrintingFactory(f)
        table_printer = factory.create_table_printer("test-table")
        table_printer.add_column("col-1")
        table_printer.add_column("col-2")
        table_printer.add_row("a", "b")
        table_printer.add_row("c", "d")
        table_printer.finish()
        text_printer = factory.create_text_printer(console_only=True)
        text_printer.print((TextObject("this text won't be printed"),))
    with open(test_file, "r") as f:
        text = cleandoc(f.read())
        expected_text = cleandoc("""
#### test-table
|    | col-1   | col-2   |
|---:|:--------|:--------|
|  0 | a       | b       |
|  1 | c       | d       |""")
        assert text == expected_text


def test_printing_rich():
    with StringIO() as buf, redirect_stdout(buf):
        # Need to reload the module here as it already might have been loaded by pytest for another test,
        # in which case sys.stdout was already loaded too
        m = importlib.reload(exasol.ds.sandbox.lib.asset_printing.rich_console_printer)

        factory = m.RichConsolePrintingFactory()
        table_printer = factory.create_table_printer("test-table")
        table_printer.add_column("col-1")
        table_printer.add_column("col-2")
        table_printer.add_row("a", "b")
        table_printer.add_row("c", "d")
        table_printer.finish()
        text_printer = factory.create_text_printer(console_only=True)
        text_printer.print((TextObject("this text will be printed"),))
        output = cleandoc(buf.getvalue())
        expected_output = cleandoc(
            # this line is expected to end with 4 space characters
            "test-table    "
            """
┏━━━━━━━┳━━━━━━━┓
┃ col-1 ┃ col-2 ┃
┡━━━━━━━╇━━━━━━━┩
│ a     │ b     │
│ c     │ d     │
└───────┴───────┘
this text will be printed""")

    assert output == expected_output
