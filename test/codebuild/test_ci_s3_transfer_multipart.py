import os
import pytest

from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.aws_access.aws_access import (
    AwsAccess,
    Progress,
)
from exasol.ds.sandbox.lib.cloudformation.s3_buckets import VmBucket


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
def test_s3_transfer_multipart(sample_file):
    aws = AwsAccess(None)
    bucket = VmBucket.s3_bucket(aws).id
    s3_key = f"{AssetId.BUCKET_PREFIX}-itest-sample-file"
    s3_key2 = f"{s3_key}-copy"
    progress = Progress("4 MB")
    try:
        aws.upload_large_s3_object(
            bucket,
            source=str(sample_file),
            dest=s3_key,
            progress=progress,
        )
        progress.reset()
        aws.copy_large_s3_object(
            bucket=bucket,
            source=s3_key,
            dest=s3_key2,
            progress=progress,
        )
    finally:
        aws.delete_s3_object(bucket, s3_key)
        aws.delete_s3_object(bucket, s3_key2)
