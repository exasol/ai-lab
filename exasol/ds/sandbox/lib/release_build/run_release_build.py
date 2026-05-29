import logging
import os

from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.config import ConfigObject
from exasol.ds.sandbox.lib.dss_docker import (
    DEFAULT_ORG_AND_REPOSITORY,
    DssDockerImage,
    DockerRegistry,
    PASSWORD_ENV,
    USER_ENV,
)
from exasol.ds.sandbox.lib.export_vm.vm_disk_image_format import VmDiskImageFormat
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType
from exasol.ds.sandbox.lib.run_create_vm import run_create_vm

LOG = get_status_logger(LogType.RELEASE_BUILD)
DEFAULT_RELEASE_USER = "release_user"
RELEASE_PASSWORD_ENV = "RELEASE_DEFAULT_PASSWORD"


def _docker_registry(publish: bool) -> DockerRegistry | None:
    if not publish:
        return None

    registry_user = os.getenv(USER_ENV)
    if not registry_user:
        raise RuntimeError(f"Environment variable {USER_ENV} must be set when publishing a release build.")

    registry_password = os.getenv(PASSWORD_ENV)
    if registry_password is None:
        raise RuntimeError(f"Environment variable {PASSWORD_ENV} must be set when publishing a release build.")

    return DockerRegistry(registry_user, registry_password)


def _release_default_password() -> str:
    password = os.getenv(RELEASE_PASSWORD_ENV)
    if not password:
        raise RuntimeError(
            f"Environment variable {RELEASE_PASSWORD_ENV} must be set for release builds."
        )
    return password


def run_start_release_build(
        config: ConfigObject,
        aws_access: AwsAccess,
        publish: bool = False,
        repository: str = DEFAULT_ORG_AND_REPOSITORY,
        asset_id: str | None = None,
) -> None:
    release_asset_id = asset_id or config.ai_lab_version
    logging.info(
        "run_start_release_build for repository %s and asset id %s",
        repository,
        release_asset_id,
    )
    registry = _docker_registry(publish)
    run_create_vm(
        aws_access=aws_access,
        ec2_instance_type="t2.medium",
        ec2_source_ami=None,
        ec2_key_file=None,
        ec2_key_name=None,
        default_password=_release_default_password(),
        vm_image_formats=VmDiskImageFormat.default_formats(),
        asset_id=AssetId(release_asset_id),
        configuration=config,
        user_name=os.getenv("AWS_USER_NAME", DEFAULT_RELEASE_USER),
        make_ami_public=publish,
    )
    creator = DssDockerImage(repository, release_asset_id)
    creator.registry = registry
    creator.create()
