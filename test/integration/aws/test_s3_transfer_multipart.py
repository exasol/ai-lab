import os
import pytest

from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.vm_bucket.vm_dss_bucket import find_vm_bucket

from dataclasses import dataclass

@dataclass
class Progress:
    bytes: int = 0

    def report(self, bytes: int):
        self.bytes += bytes
        display = round(self.bytes / 1024 / 1024)
        print(f'\rTransferred {display} MB ...', flush=True, end="")


@pytest.fixture
def sample_file(tmp_path):
    """
    Create a sample file of size 6 MB for transfer to S3 bucket.
    """
    file = tmp_path / "sample-file.txt"
    one_kb = "123456789 " * 102 + "1234"
    file.write_text(one_kb * 1024 * 6)
    yield file
    file.unlink()


@pytest.mark.skipif(
    os.environ.get('DSS_RUN_S3_TEST') != 'true',
    reason="Tests accessing real S3 buckets need to be activated by env variable DSS_RUN_S3_TEST")
def test_s3_transfer_multipart(sample_file):
    aws = AwsAccess(aws_profile="ci4_mfa")
    source = sample_file
    bucket = find_vm_bucket(aws)
    s3_key = f"{AssetId.BUCKET_PREFIX}-itest-sample-file"
    progress = Progress()
    print("")
    try:
        aws.transfer_to_s3(
            bucket=bucket,
            source=source,
            dest=s3_key,
            callback=progress.report,
        )
    finally:
        aws.delete_s3_object(bucket, s3_key)
