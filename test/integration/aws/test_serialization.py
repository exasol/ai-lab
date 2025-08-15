import contextlib
import multiprocessing as mp
import os.path
import pickle
import traceback

from pathlib import Path

from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.setup_ec2.cf_stack import CloudformationStack
from exasol.ds.sandbox.lib.setup_ec2.key_file_manager import KeyFileManager
from test.aws.local_stack_access import AwsLocalStackAccess

def create_key_pair_and_serialize(
        aws_key_id: str,
        aws_secret_key: str,
        tmp_location: Path, q: mp.Queue, default_asset_id: AssetId):
    try:
        aws = AwsLocalStackAccess(aws_key_id, aws_secret_key)
        key_file_manager = KeyFileManager(aws, None, None, default_asset_id.tag_value)
        key_file_manager.create_key_if_needed()
        q.put(key_file_manager.key_name)
        q.put(key_file_manager.key_file_location)
        with open(tmp_location, "wb") as f:
            pickle.dump(key_file_manager, f)
    except Exception as e:
        traceback.print_exc()
        raise e


def test_keypair_manager_with_local_stack(tmp_path, local_stack_aws_access, default_asset_id):
    """
    Test that serialization and deserialization of KeyFileManager works
    """
    tmp_file = Path(tmp_path) / "key_file_manager.data"
    q = mp.Queue()
    p = mp.Process(
        target=create_key_pair_and_serialize,
        args=(
            local_stack_aws_access.key_id,
            local_stack_aws_access.secret_key,
            tmp_file,
            q,
            default_asset_id,
        ))
    p.start()
    p.join()
    assert p.exitcode == 0
    key_name = q.get()
    key_file_location = q.get()

    with open(tmp_file, "rb") as f:
        with contextlib.closing(pickle.load(f)) as key_file_manager:
            restored_key_name = key_file_manager.key_name
            restored_key_file_location = key_file_manager.key_file_location

    assert key_name == restored_key_name
    assert key_file_location == restored_key_file_location
    assert os.path.exists(restored_key_file_location) is False


def create_cloudformation_stack_and_serialize(
        aws_key_id: str,
        aws_secret_key: str,
        tmp_location_key_manager: Path,
        tmp_location_cloudformation: Path,
        q: mp.Queue,
        default_asset_id: AssetId,
        test_dummy_ami_id: str,
        test_ec2_instance_type: str,
):
    try:
        aws = AwsLocalStackAccess(aws_key_id, aws_secret_key)
        key_file_manager = KeyFileManager(aws, None, None, default_asset_id.tag_value)
        key_file_manager.create_key_if_needed()
        with open(tmp_location_key_manager, "wb") as f:
            pickle.dump(key_file_manager, f)
        stack = CloudformationStack(
            aws_access=aws,
            ec2_key_name=key_file_manager.key_name,
            user_name=aws.get_user(),
            asset_id=default_asset_id,
            ami_id=test_dummy_ami_id,
            instance_type=test_ec2_instance_type,
        )
        stack.upload_cloudformation_stack()
        with open(tmp_location_cloudformation, "wb") as f:
            pickle.dump(stack, f)
        q.put(stack.stack_name)
        q.put(stack.get_ec2_instance_id())
    except Exception as e:
        traceback.print_exc()
        raise e


def test_cloudformation_stack_with_local_stack(
        tmp_path,
        local_stack_aws_access,
        default_asset_id,
        test_dummy_ami_id,
        test_ec2_instance_type,
):
    """
    This test verifies serialization and deserialization of
    CloudformationStack.
    """
    tmp_file_key_file = Path(tmp_path) / "key_file_manager.data"
    tmp_file_cloud_formation = Path(tmp_path) / "cloudformation.data"
    q = mp.Queue()
    p = mp.Process(
        target=create_cloudformation_stack_and_serialize,
        args=(
            local_stack_aws_access.key_id,
            local_stack_aws_access.secret_key,
            tmp_file_key_file,
            tmp_file_cloud_formation,
            q,
            default_asset_id,
            test_dummy_ami_id,
            test_ec2_instance_type,
        ))
    p.start()
    p.join()
    assert p.exitcode == 0
    stack_name = q.get()
    ec2_instance_id = q.get()

    with open(tmp_file_cloud_formation, "rb") as f:
        with contextlib.closing(pickle.load(f)) as cloudformation:
            restored_stack_name = cloudformation.stack_name
            restored_ec2_instance_id = cloudformation.get_ec2_instance_id()

    assert stack_name == restored_stack_name
    assert ec2_instance_id == restored_ec2_instance_id
