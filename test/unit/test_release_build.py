from unittest.mock import patch

import pytest

from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.dss_docker import DEFAULT_ORG_AND_REPOSITORY
from exasol.ds.sandbox.lib.release_build.run_release_build import (
    RELEASE_PASSWORD_ENV,
    run_start_release_build,
)


@patch("exasol.ds.sandbox.lib.release_build.run_release_build.run_create_vm")
@patch("exasol.ds.sandbox.lib.release_build.run_release_build.DssDockerImage")
def test_release_build_without_publish(
        dss_docker_image_mock,
        run_create_vm_mock,
        test_config,
        monkeypatch,
):
    monkeypatch.setenv(RELEASE_PASSWORD_ENV, "release-default-password")
    aws_access = AwsAccess(None)
    run_start_release_build(test_config, aws_access)

    run_create_vm_mock.assert_called_once()
    run_create_vm_kwargs = run_create_vm_mock.call_args.kwargs
    assert run_create_vm_kwargs["aws_access"] is aws_access
    assert isinstance(run_create_vm_kwargs["asset_id"], AssetId)
    assert run_create_vm_kwargs["asset_id"].tag_value == test_config.ai_lab_version
    assert run_create_vm_kwargs["make_ami_public"] is False
    assert run_create_vm_kwargs["default_password"] == "release-default-password"
    assert run_create_vm_kwargs["user_name"] == "release_user"
    dss_docker_image_mock.assert_called_once_with(
        DEFAULT_ORG_AND_REPOSITORY,
        test_config.ai_lab_version,
    )
    creator = dss_docker_image_mock.return_value
    assert creator.registry is None
    creator.create.assert_called_once_with()


@patch("exasol.ds.sandbox.lib.release_build.run_release_build.run_create_vm")
@patch("exasol.ds.sandbox.lib.release_build.run_release_build.DockerRegistry")
@patch("exasol.ds.sandbox.lib.release_build.run_release_build.DssDockerImage")
def test_release_build_with_publish(
        dss_docker_image_mock,
        docker_registry_mock,
        run_create_vm_mock,
        test_config,
        monkeypatch,
):
    monkeypatch.setenv(RELEASE_PASSWORD_ENV, "release-default-password")
    monkeypatch.setenv("DOCKER_REGISTRY_USER", "release-user")
    monkeypatch.setenv("DOCKER_REGISTRY_PASSWORD", "release-password")
    monkeypatch.setenv("AWS_USER_NAME", "oidc-release-user")
    aws_access = AwsAccess(None)

    run_start_release_build(test_config, aws_access, publish=True, repository="example/release")

    run_create_vm_mock.assert_called_once()
    assert run_create_vm_mock.call_args.kwargs["user_name"] == "oidc-release-user"
    assert run_create_vm_mock.call_args.kwargs["aws_access"] is aws_access
    assert run_create_vm_mock.call_args.kwargs["make_ami_public"] is True
    dss_docker_image_mock.assert_called_once_with("example/release", test_config.ai_lab_version)
    docker_registry_mock.assert_called_once_with("release-user", "release-password")
    creator = dss_docker_image_mock.return_value
    assert creator.registry == docker_registry_mock.return_value
    creator.create.assert_called_once_with()


@patch("exasol.ds.sandbox.lib.release_build.run_release_build.run_create_vm")
@patch("exasol.ds.sandbox.lib.release_build.run_release_build.DssDockerImage")
def test_release_build_with_asset_override(
        dss_docker_image_mock,
        run_create_vm_mock,
        test_config,
        monkeypatch,
):
    monkeypatch.setenv(RELEASE_PASSWORD_ENV, "release-default-password")
    aws_access = AwsAccess(None)

    run_start_release_build(test_config, aws_access, asset_id="manual-release")

    run_create_vm_kwargs = run_create_vm_mock.call_args.kwargs
    assert run_create_vm_kwargs["aws_access"] is aws_access
    assert isinstance(run_create_vm_kwargs["asset_id"], AssetId)
    assert run_create_vm_kwargs["asset_id"].tag_value == "manual-release"
    dss_docker_image_mock.assert_called_once_with(
        DEFAULT_ORG_AND_REPOSITORY,
        "manual-release",
    )


@pytest.mark.parametrize(
    ("missing_env", "expected_message"),
    [
        (RELEASE_PASSWORD_ENV, f"Environment variable {RELEASE_PASSWORD_ENV} must be set"),
        ("DOCKER_REGISTRY_USER", "Environment variable DOCKER_REGISTRY_USER must be set"),
        ("DOCKER_REGISTRY_PASSWORD", "Environment variable DOCKER_REGISTRY_PASSWORD must be set"),
    ],
)
@patch("exasol.ds.sandbox.lib.release_build.run_release_build.run_create_vm")
@patch("exasol.ds.sandbox.lib.release_build.run_release_build.DssDockerImage")
def test_release_build_publish_requires_registry_credentials(
        dss_docker_image_mock,
        run_create_vm_mock,
        test_config,
        monkeypatch,
        missing_env,
        expected_message,
):
    monkeypatch.setenv(RELEASE_PASSWORD_ENV, "release-default-password")
    monkeypatch.setenv("DOCKER_REGISTRY_USER", "release-user")
    monkeypatch.setenv("DOCKER_REGISTRY_PASSWORD", "release-password")
    aws_access = AwsAccess(None)
    monkeypatch.delenv(missing_env)

    with pytest.raises(RuntimeError, match=expected_message):
        run_start_release_build(test_config, aws_access, publish=True)

    run_create_vm_mock.assert_not_called()
    dss_docker_image_mock.return_value.create.assert_not_called()
