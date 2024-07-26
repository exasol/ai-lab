from dataclasses import dataclass
from typing import Dict, Optional

from exasol.ds.sandbox.lib.render_template import render_template
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess

from exasol.ds.sandbox.lib.logging import get_status_logger, LogType
LOG = get_status_logger(LogType.S3_BUCKETS)


@dataclass(frozen=True)
class CfTemplateSpec:
    cf_stack_name: str
    template: str
    outputs: Dict[str, str]


class CfTemplate:
    def __init__(self, aws_access: Optional[AwsAccess], spec: CfTemplateSpec):
        self._aws = aws_access
        self.spec = spec

    @property
    def stack_name(self) -> str:
        return self.spec.cf_stack_name

    def cloudformation_template(self, **kwargs) -> str:
        return render_template(
            self.spec.template,
            **self.spec.outputs,
            **kwargs,
        )

    def setup(self, **kwargs) -> None:
        rendered = self.cloudformation_template(**kwargs)
        # LOG.warning(f'upload disabled to prevent accidentally creating AWS resources')
        # return
        self._aws.upload_cloudformation_stack(rendered, self.stack_name)

    def stack_output(self, index: str):
        try:
            stack = next(
                s for s in self._aws.describe_stacks()
                if s.name == self.stack_name
            )
        except StopIteration:
            raise RuntimeError(f"Stack {self.stack_name} not found")
        key = self.spec.outputs[index]
        outputs = [o for o in stack.outputs if o.output_key == key]
        if len(outputs) != 1:
            raise RuntimeError(
                f"Output key '{key}' in output for "
                f"stack {self.stack_name} not found or non-uniq")
        return outputs[0].output_value

