import os
import pytest

from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.aws_access.aws_access import (
    AwsAccess,
    Progress,
)
from exasol.ds.sandbox.lib.vm_bucket.vm_dss_bucket import find_vm_bucket


@pytest.fixture
def sample_size_kb():
    return 1024 * 16


@pytest.fixture
def sample_file(tmp_path, sample_size_kb):
    """
    Create a sample file of size 6 MB for transfer to S3 bucket.
    """
    file = tmp_path / "sample-file.txt"
    one_kb = "123456789 " * 102 + "1234"
    file.write_text(one_kb * sample_size_kb)
    yield file
    file.unlink()


@pytest.mark.skipif(os.environ.get('DSS_RUN_CI_TEST') != 'true',
                    reason="CI test need to be activated by env variable DSS_RUN_CI_TEST")
def test_s3_transfer_multipart(sample_file, sample_size_kb):
    aws = AwsAccess(None)
    source = sample_file
    bucket = find_vm_bucket(aws)
    s3_key = f"{AssetId.BUCKET_PREFIX}-itest-sample-file"
    progress = Progress("1 MB")
    try:
        aws.transfer_to_s3(
            bucket=bucket,
            source=source,
            dest=s3_key,
            callback=progress.report,
        )
    finally:
        aws.delete_s3_object(bucket, s3_key)
