from exasol.nb_connector.secret_store import Secrets
from exasol.nb_connector.itde_manager import (
    bring_itde_up,
    take_itde_down
)
from exasol.nb_connector.connections import open_pyexasol_connection
from notebook_test_utils import set_log_level_for_libraries

set_log_level_for_libraries()

def test_itde(tmp_path):
    store_path = tmp_path / 'tmp_config.sqlite'
    store_password = "password"
    secrets = Secrets(store_path, master_password=store_password)
    bring_itde_up(secrets)
    try:
        con = open_pyexasol_connection(secrets)
        try:
            result = con.execute("select 1").fetchmany()
            assert result[0][0] == 1
        finally:
            con.close()
    finally:
        take_itde_down(secrets)

