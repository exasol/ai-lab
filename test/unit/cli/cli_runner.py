import click
import os
from unittest import mock
from click.testing import CliRunner as ClickCli

# import logging
# LOG = logging.getLogger(__name__)
# LOG.setLevel(logging.INFO)

class CliRunner():
    def __init__(self, command: click.Command, debug: bool = False, env = {}):
        self._command = command
        self.debug = debug
        self.result = None
        self.env = env

    def run(self, *args):
        def command_line():
            yield self._command.name
            yield from args

        with mock.patch.dict(os.environ, self.env):
            self.result = ClickCli().invoke(self._command, args)
        if self.debug:
            cstr = " ".join(command_line())
            print(
                f'Command "{cstr}"'
                f'\n terminated with exit code {self.result.exit_code}'
                f'\n output: >{self.result.output}<'
            )
        return self

    @property
    def output(self):
        return self.result.output

    @property
    def failed(self):
        return self.result.exit_code != 0

    @property
    def succeeded(self):
        return self.result.exit_code == 0
