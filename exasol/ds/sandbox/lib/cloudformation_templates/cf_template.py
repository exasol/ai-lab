from dataclasses import dataclass
from typing import Dict, Optional

from exasol.ds.sandbox.lib.render_template import TemplateRenderer
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess


@dataclass(frozen=True)
class CfTemplateSpec:
    cf_stack_name: str
    template: str
    outputs: Dict[str, str]


class CfTemplate:
    def __init__(self, aws_access: Optional[AwsAccess], spec: CfTemplateSpec):
        self._aws = aws_access
        self.spec = spec
        self._template_renderer = TemplateRenderer()

    @property
    def stack_name(self) -> str:
        return self.spec.cf_stack_name

    def cloudformation_template(self, **kwargs) -> str:
        return self._template_renderer.render(
            self.spec.template,
            **self.spec.outputs,
            **kwargs,
        )

    def setup(self, **kwargs) -> None:
        rendered = self.cloudformation_template(**kwargs)
        self._aws.upload_cloudformation_stack(rendered, self.stack_name)

    def stack_output(self, mnemonic: str):
        """
        For the specified mnemonic look up the output key in the spec of the
        current CfTemplate. Then search on AWS for a stack with the name of
        the current CfTemplate and if found for an output with the key as
        retrieved before.

        Raise a RuntimeError in case either there is no stack with the current
        name or if the stack does not contain an output with the retrieved
        key.
        """
        try:
            stacks = self._aws.describe_stacks()
            stack = next(
                s for s in stacks
                if s.name == self.stack_name
            )
        except StopIteration:
            raise RuntimeError(f"Stack {self.stack_name} not found")
        key = self.spec.outputs[mnemonic]
        outputs = [o for o in stack.outputs if o.output_key == key]
        if len(outputs) != 1:
            raise RuntimeError(
                f"Output key '{key}' in output for "
                f"stack {self.stack_name} not found or non-uniq")
        return outputs[0].output_value
