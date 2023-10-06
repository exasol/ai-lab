from dataclasses import dataclass
from sqlcipher3 import dbapi2 as sqlcipher
import logging
import os
from typing import Optional, Union
from inspect import cleandoc


_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Table:
    name: str
    columns: list[str]


SECRETS_TABLE = Table("secrets", ["user", "password"])
CONFIG_ITEMS_TABLE = Table("config_items", ["item"])


@dataclass(frozen=True)
class Credentials:
    user: str
    password: str


class PotentiallyIncorrectMasterPassword(Exception):
    """Signal potentially incorrect master password."""


class Secrets:
    def __init__(self, db_file: str, master_password: str) -> None:
        self.db_file = db_file
        self.master_password = master_password
        self._con = None
        self._cur = None

    def close(self) -> None:
        if self._cur is not None:
            self._cur.close()
            self._cur = None
        if self._con is not None:
            self._con.close()
            self._con = None

    def connection(self) -> sqlcipher.Connection:
        if self._con is None:
            db_file_found = os.path.exists(self.db_file)
            if not db_file_found:
                _logger.info(f"Creating file {self.db_file}")
            self._con = sqlcipher.connect(self.db_file)
            self._use_master_password()
            self._initialize(db_file_found)
        return self._con

    def _initialize(self, db_file_found: bool) -> None:
        def create_table(table: Table) -> None:
            _logger.info(f'Creating table "{table.name}".')
            columns = " ,".join(table.columns)
            self._cursor().execute(f"CREATE TABLE {table.name} (key, {columns})")
            self.connection().commit()

        if db_file_found:
            self._verify_access()
            return
        for table in (SECRETS_TABLE, CONFIG_ITEMS_TABLE):
            create_table(table)

    def _use_master_password(self) -> None:
        """
        If database is unencrypted then this method encrypts it.
        If database is already encrypted then this method enables to access the data.
        """
        if self.master_password is not None:
            sanitized = self.master_password.replace("'", "\\'")
            self._cursor().execute(f"PRAGMA key = '{sanitized}'")

    def _verify_access(self):
        try:
            self._cursor().execute("SELECT * FROM sqlite_master")
        except sqlcipher.DatabaseError as ex:
            print(f'exception {ex}')
            if str(ex) == "file is not a database":
                raise PotentiallyIncorrectMasterPassword(
                    cleandoc(
                    f"""
                    Cannot access
                    database file {self.db_file}.
                    This also happens if master password is incorrect.
                    """)
                )
            else:
                raise ex

    def _cursor(self) -> sqlcipher.Cursor:
        if self._cur is None:
            self._cur = self.connection().cursor()
        return self._cur

    def _save_data(self, table: Table, key: str, data: list[str]) -> "Secrets":
        cur = self._cursor()
        res = cur.execute(f"SELECT * FROM {table.name} WHERE key=?", [key])
        if res and res.fetchone():
            columns = ", ".join(f"{c}=?" for c in table.columns)
            cur.execute(
                f"UPDATE {table.name} SET {columns} WHERE key=?",
                data + [key])
        else:
            columns = ",".join(table.columns)
            value_slots = ", ".join("?" for c in table.columns)
            cur.execute(
                f"INSERT INTO {table.name} (key,{columns}) VALUES (?, {value_slots})",
                [key] + data)
        self.connection().commit()
        return self

    # def save_config_item(self, key: str, item: str) -> None:
    #     self._save_data(CONFIG_ITEMS_TABLE, key, [item])
    #
    # def save_credentials(self, key: str, user: str, password: str) -> None:
    #     self._save_data(SECRETS_TABLE, key, [user, password])

    def save(self, key: str, data: Union[str, Credentials]) -> "Secrets":
        """key represents a system, service, or application"""
        if isinstance(data, str):
            return self._save_data(CONFIG_ITEMS_TABLE, key, [data])
        if isinstance(data, Credentials):
            return self._save_data(SECRETS_TABLE, key, [data.user, data.password])
        raise Exception("Unsupported type of data: " + type(data).__name__)

    def _data(self, table: Table, key: str) -> Optional[list[str]]:
        columns = ", ".join(table.columns)
        res = self._cursor().execute(
            f"SELECT {columns} FROM {table.name} WHERE key=?",
            [key])
        return res.fetchone() if res else None

    def credentials(self, key: str) -> Optional[Credentials]:
        row = self._data(SECRETS_TABLE, key)
        return Credentials(row[0], row[1]) if row else None

    def config(self, key: str) -> Optional[str]:
        row = self._data(CONFIG_ITEMS_TABLE, key)
        return row[0] if row else None
