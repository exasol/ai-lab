import contextlib
import os.path
import pickle
import traceback
from pathlib import Path

from exasol_script_languages_developer_sandbox.lib.cf_stack import CloudformationStack
from exasol_script_languages_developer_sandbox.lib.key_file_manager import KeyFileManager
from test.aws_local_stack_access import AwsLocalStackAccess
import multiprocessing as mp


def create_key_pair_and_serialize(tmp_location: Path, q: mp.Queue):
    try:
        aws_access = AwsLocalStackAccess(None)
        key_file_manager = KeyFileManager(aws_access, None, None)
        key_file_manager.create_key_if_needed()
        q.put(key_file_manager.key_name)
        q.put(key_file_manager.key_file_location)
        with open(tmp_location, "wb") as f:
            pickle.dump(key_file_manager, f)
    except Exception as e:
        traceback.print_exc()
        raise e


def test_keypair_manager_with_local_stack(tmp_path, local_stack):
    """
    Test that serialization and deserialization of KeyFileManager work!
    """
    tmp_file = Path(tmp_path) / "key_file_manager.data"
    q = mp.Queue()
    p = mp.Process(target=create_key_pair_and_serialize, args=(tmp_file, q))
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


def create_cloudformation_stack_and_serialize(tmp_location_key_manager: Path, tmp_location_cloudformation: Path,
                                              q: mp.Queue):
    try:
        aws_access = AwsLocalStackAccess(None)
        key_file_manager = KeyFileManager(aws_access, None, None)
        key_file_manager.create_key_if_needed()
        with open(tmp_location_key_manager, "wb") as f:
            pickle.dump(key_file_manager, f)
        cloudformation = CloudformationStack(aws_access, key_file_manager.key_name, aws_access.get_user(), None)
        cloudformation.upload_cloudformation_stack()
        with open(tmp_location_cloudformation, "wb") as f:
            pickle.dump(cloudformation, f)
        q.put(cloudformation.stack_name)
        q.put(cloudformation.get_ec2_instance_id())
    except Exception as e:
        traceback.print_exc()
        raise e


def test_cloudformation_stack_with_local_stack(tmp_path, local_stack):
    """
    Test that serialization and deserialization of CloudformationStack work!
    """
    tmp_file_key_file = Path(tmp_path) / "key_file_manager.data"
    tmp_file_cloud_formation = Path(tmp_path) / "cloudformation.data"
    q = mp.Queue()
    p = mp.Process(target=create_cloudformation_stack_and_serialize,
                   args=(tmp_file_key_file, tmp_file_cloud_formation, q))
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
