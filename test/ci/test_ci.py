import os
import time

from datetime import datetime

import paramiko
import pytest

import fabric
import requests

from invoke import Responder

from exasol.ds.sandbox.lib.ansible.ansible_access import AnsibleAccess
from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.config import default_config_object, SLC_VERSION
from exasol.ds.sandbox.lib.run_create_vm import run_create_vm
from exasol.ds.sandbox.lib.setup_ec2.run_setup_ec2 import run_lifecycle_for_ec2, \
    EC2StackLifecycleContextManager

import string
import random

from exasol.ds.sandbox.lib.tags import DEFAULT_TAG_KEY


def generate_random_password(length) -> str:
    return ''.join(random.sample(string.ascii_letters, length))


def change_password(host: str, user: str, curr_pass: str, new_password: str) -> None:
    with fabric.Connection(host, user=user,
                           connect_kwargs={"password": curr_pass}) as con:
        prompts = ((r"Current password: ", f"{curr_pass}\n"),
                   (r"New password: ", f"{new_password}\n"),
                   (r"Retype new password: ", f"{new_password}\n"))
        responders = [Responder(pattern=prompt, response=response) for prompt, response in prompts]
        res = con.run("uname",
                      watchers=responders,
                      pty=True)
        assert res.ok


@pytest.fixture(scope="session")
def new_ec2_from_ami():
    """
    This fixtures starts the EC-2 instance, runs all setup, exports the AMI,
    then starts another EC-2 instance, based on the new AMI, then changes the password (which is expired),
    and finally  returns that EC-2 name together with the new temporary password.
    """
    # Create default_password (the one burned into the AMI) and the new password (which will be set during first login)
    # We use different sizes of both in order to avoid equality of both!
    default_password = generate_random_password(length=12)
    new_password = generate_random_password(length=14)
    # both passwords differ in length, so it can't happen that both are equal.
    # However, just as a safeguard check for inequality.
    assert default_password != new_password
    aws_access = AwsAccess(aws_profile=None)
    user_name = os.getenv("AWS_USER_NAME")
    asset_id = AssetId("ci-test-{suffix}-{now}".format(now=datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),
                                                       suffix=SLC_VERSION),
                       stack_prefix="stack",
                       ami_prefix="ami")
    run_create_vm(aws_access, None, None,
                  AnsibleAccess(), default_password, tuple(), asset_id,
                  default_config_object, user_name, make_ami_public=False)

    # Use the ami_name to find the AMI id (alternatively we could use the tag here)
    amis = aws_access.list_amis(filters=[{'Name': 'name', 'Values': [asset_id.ami_name]}])
    assert len(amis) == 1
    ami = amis[0]

    lifecycle_generator = run_lifecycle_for_ec2(aws_access, None, None, asset_id=asset_id,
                                                ami_id=ami.id, user_name=user_name)

    try:
        with EC2StackLifecycleContextManager(lifecycle_generator, default_config_object) as ec2_data:
            ec2_instance_description, key_file_location = ec2_data
            assert ec2_instance_description.is_running

            status = aws_access.get_instance_status(ec2_instance_description.id)
            while status.initializing:
                time.sleep(10)
                status = aws_access.get_instance_status(ec2_instance_description.id)
            assert status.ok
            time.sleep(10)
            change_password(host=ec2_instance_description.public_dns_name, user='ubuntu',
                            curr_pass=default_password, new_password=new_password)
            yield ec2_instance_description.public_dns_name, new_password, default_password
    finally:
        # Cleanup: We need to unregister the AMI and the snapshot
        # (the rest was removed automatically by deleting the cloudformation stack)
        aws_access.deregister_ami(ami.id)
        # Find snapshot by the tag
        snapshots = aws_access.list_snapshots(filters=[{'Name': f'tag:{DEFAULT_TAG_KEY}',
                                                        'Values': [asset_id.tag_value]}])
        assert len(snapshots) == 1
        aws_access.remove_snapshot(snapshots[0].id)


@pytest.mark.skipif(os.environ.get('DSS_RUN_CI_TEST') != 'true',
                    reason="CI test need to be activated by env variable DSS_RUN_CI_TEST")
def test_exaslct_with_ec2_based_on_new_ami(new_ec2_from_ami):
    """
    This test validates that exaslct is correctly working on the EC-2 instance, which was launched from the
    newly created AMI.
    """
    ec2_instance, password, _ = new_ec2_from_ami
    with fabric.Connection(ec2_instance, user='ubuntu',
                           connect_kwargs={"password": password}) as con:
        with con.cd("script-languages-release"):
            cmd = "./exaslct build --flavor-path ./flavors/python-3.8-minimal-EXASOL-6.2.0"
            result = con.run(cmd)
            assert result.ok
            assert result.return_code == 0


@pytest.mark.skipif(os.environ.get('DSS_RUN_CI_TEST') != 'true',
                    reason="CI test need to be activated by env variable DSS_RUN_CI_TEST")
def test_jupyter_with_ec2_based_on_new_ami(new_ec2_from_ami):
    """
    This test validates that Jupyterlab is correctly working on the EC-2 instance, which was launched from the
    newly created AMI.
    """
    ec2_instance, password, _ = new_ec2_from_ami
    http_conn = requests.get(f"http://{ec2_instance}:8888/lab")
    assert http_conn.status_code == 200


@pytest.mark.skipif(os.environ.get('DSS_RUN_CI_TEST') != 'true',
                    reason="CI test need to be activated by env variable DSS_RUN_CI_TEST")
def test_password_changed_on_new_ami(new_ec2_from_ami):
    """
    This test validates that the password has been changed by trying to login via ssh using the old password
    (which must fail) and by using the new password (which must succeed).
    """
    ec2_instance, password, old_password = new_ec2_from_ami
    with pytest.raises(paramiko.ssh_exception.AuthenticationException):
        with fabric.Connection(ec2_instance, user='ubuntu',
                               connect_kwargs={"password": old_password}) as con:
            con.run("uname")

    with fabric.Connection(ec2_instance, user='ubuntu',
                           connect_kwargs={"password": password}) as con:
        con.run("uname")


@pytest.mark.skipif(os.environ.get('DSS_RUN_CI_TEST') != 'true',
                    reason="CI test need to be activated by env variable DSS_RUN_CI_TEST")
def test_jupyter_password_message_shown(new_ec2_from_ami):
    """
    This test validates that the motd password message for Jupyterlab is working as expected.
    """
    ec2_instance, password, old_password = new_ec2_from_ami

    motd_message_watermark = "/bin/jupyter server password"

    # 1. Initially the jupyter password message is expected to appear in the welcome message
    with fabric.Connection(ec2_instance, user='ubuntu',
                           connect_kwargs={"password": password}) as con:
        result = con.run("cat /var/run/motd.dynamic")
        assert result.ok
        assert motd_message_watermark in result.stdout

    # 2. Now we create a new password for jupyterlab
    random_jupyter_password = generate_random_password(12)
    with fabric.Connection(ec2_instance, user='ubuntu',
                           connect_kwargs={"password": password}) as con:
        prompts = ((r"Enter password: ", f"{random_jupyter_password}\n"),
                   (r"Verify password: ", f"{random_jupyter_password}\n"))
        responders = [Responder(pattern=prompt, response=response) for prompt, response in prompts]
        res = con.run("./jupyterenv/bin/jupyter server password",
                      watchers=responders,
                      pty=True)
        assert res.ok

    # 3. On the next login, the update message for the Jupyter password must not appear!
    with fabric.Connection(ec2_instance, user='ubuntu',
                           connect_kwargs={"password": password}) as con:
        result = con.run("cat /var/run/motd.dynamic")
        assert result.ok
        assert motd_message_watermark not in result.stdout
