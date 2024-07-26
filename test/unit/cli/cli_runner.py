import click
from click.testing import CliRunner as ClickCli

# import logging
# LOG = logging.getLogger(__name__)
# LOG.setLevel(logging.INFO)

class CliRunner():
    def __init__(self, command: click.Command, debug: bool = False):
        self._command = command
        self.debug = debug
        self.result = None

    def run(self, *args):
        def command_line():
            yield self._command.name
            yield from args

        self.result = ClickCli().invoke(self._command, args)
        if self.debug:
            cstr = " ".join(command_line())
            print(
                f'Command "{cstr}"'
                f'\n terminated with exit code {self.result.exit_code}'
                f'\n output: >{self.result.output}<'
            )
        return self

    def failed(self, output: str = None):
        """
        Return True, if CLI execution failed, i.e. exit_code is != 0.  If
        output is specified, then the specified string must be contained in
        the output created while running the CLI.
        """
        matches = output is None or output in self.result.output
        return self.result.exit_code != 0 and matches

    def succeeded(self, output: str = None):
        """
        Return True, if CLI execution was successful, i.e. exit_code is 0.
        If output is specified, then the specified string must be contained in
        the output created while running the CLI.
        """
        matches = output is None or output in self.result.output
        return self.result.exit_code == 0 and matches


