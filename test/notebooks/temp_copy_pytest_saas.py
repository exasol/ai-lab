import os

import pytest
from exasol.saas.client import openapi
from exasol.saas.client.api_access import (
    OpenApiAccess,
    create_saas_client,
    timestamp_name,
)


def _env(var: str) -> str:
    result = os.environ.get(var)
    if result:
        return result
    raise RuntimeError(f"Environment variable {var} is empty.")


@pytest.fixture(scope="session")
def saas_host() -> str:
    return _env("SAAS_HOST")


@pytest.fixture(scope="session")
def saas_pat() -> str:
    return _env("SAAS_PAT")


@pytest.fixture(scope="session")
def saas_account_id() -> str:
    return _env("SAAS_ACCOUNT_ID")


@pytest.fixture(scope="session")
def database_name():
    return timestamp_name('NBTEST')


@pytest.fixture(scope="session")
def api_access(saas_host, saas_pat, saas_account_id) -> OpenApiAccess:
    with create_saas_client(saas_host, saas_pat) as client:
        yield OpenApiAccess(client, saas_account_id)


@pytest.fixture(scope="session")
def saas_database(
    request, api_access, database_name
) -> openapi.models.database.Database:
    """
    Note: The SaaS instance database returned by this fixture initially
    will not be operational. The startup takes about 20 minutes.
    """
    db_id = request.config.getoption("--saas-database-id")
    keep = request.config.getoption("--keep-saas-database")
    if db_id:
        yield api_access.get_database(db_id)
        return
    with api_access.database(database_name, keep) as db:
        yield db


@pytest.fixture(scope="session")
def operational_saas_database_id(api_access, saas_database) -> str:
    db = saas_database
    with api_access.allowed_ip():
        api_access.wait_until_running(db.id)
        yield db.id
