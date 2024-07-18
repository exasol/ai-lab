
from exasol.ds.sandbox.lib.render_template import render_template


LOG = get_status_logger(LogType.VM_BUCKET)


class OutputKey(Enum):
    BucketId = "BucketId"
    ExportRoleId = "ExportRoleId"
    CfDistributionId = "CfDistributionId"
    CfDistributionDomainName = "CfDistributionDomainName"


class S3Bucket:
    def __init__(self, stack_name: str, template: str):
        self.stack_name = stack_name
        self.template = template

    # create_vm_bucket_cf_template
    def cloudformation_template(self, waf_webacl_arn: str) -> str:
        # All output keys (class OutputKey) are parameters in the template.
        # Simply map the output key enums values to themselves and pass them
        # to jinja.  Thus, we ensure that the AWS output keys in the
        # cloudformation match with the values the dict.
        return render_template(
            self.template, # "vm_bucket_cloudformation.jinja.yaml",
            acl_arn=waf_webacl_arn,
            path_in_bucket=AssetId.BUCKET_PREFIX,
            **self._output_keys_dict,
        )

    # _find_vm_bucket_stack_output
    def _stack_output(self, aws_access: AwsAccess, output_key: OutputKey):
        stack = [stack for stack in aws_access.describe_stacks() if stack.name == self.stack_name]
        if len(stack) != 1:
            raise RuntimeError(f"stack {self.stack_name} not found")
        output = [output for output in stack[0].outputs if output.output_key == output_key.value]
        if len(output) != 1:
            raise RuntimeError(f"Output key '{output_key}' in output for stack {self.stack_name} not found")
        return output[0].output_value

    # run_setup_vm_bucket
    def setup(self, aws_access: AwsAccess, config: ConfigObject) -> None:
        acl_arn = find_acl_arn(aws_access, config)
        yml = self.cloudformation_template(acl_arn)
        aws_access.upload_cloudformation_stack(yml, self.stack_name)
        LOG.info(f"Deployed cloudformation stack {self.stack_name}")

    def find_vm_bucket(self, aws_access: AwsAccess) -> str:
        return self._stack_output(aws_access, OutputKey.VMBucketId)

    def find_url_for_bucket(self, aws_access: AwsAccess) -> str:
        return self._stack_output(aws_access, OutputKey.CfDistributionDomainName)

    def find_vm_import_role(self, aws_access: AwsAccess) -> str:
        return self._stack_output(aws_access, OutputKey.VMExportRoleId)

