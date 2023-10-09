import contextlib
import logging
import os
from dataclasses import dataclass
from sqlcipher3 import dbapi2 as sqlcipher
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


class InvalidPassword(Exception):
    """Signal potentially incorrect master password."""


class Secrets:
    def __init__(self, db_file: str, master_password: str) -> None:
        self.db_file = db_file
        self._master_password = master_password
        self._con = None

    def close(self) -> None:
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
        if db_file_found:
            self._verify_access()
            return

        def create_table(table: Table) -> None:
            _logger.info(f'Creating table "{table.name}".')
            columns = " ,".join(table.columns)
            with self._cursor() as cur:
                cur.execute(f"CREATE TABLE {table.name} (key, {columns})")

        for table in (SECRETS_TABLE, CONFIG_ITEMS_TABLE):
            create_table(table)

    def _use_master_password(self) -> None:
        """
        If database is unencrypted then this method encrypts it.
        If database is already encrypted then this method enables to access the data.
        """
        if self._master_password is not None:
            sanitized = self._master_password.replace("'", "\\'")
            with self._cursor() as cur:
                cur.execute(f"PRAGMA key = '{sanitized}'")

    def _verify_access(self):
        try:
            with self._cursor() as cur:
                cur.execute("SELECT * FROM sqlite_master")
        except sqlcipher.DatabaseError as ex:
            print(f'exception {ex}')
            if str(ex) == "file is not a database":
                raise InvalidPassword(
                    cleandoc(
                    f"""
                    Cannot access
                    database file {self.db_file}.
                    This also happens if master password is incorrect.
                    """)
                ) from ex
            else:
                raise ex

    @contextlib.contextmanager
    def _cursor(self) -> sqlcipher.Cursor:
        cur = self.connection().cursor()
        try:
            yield cur
            self.connection().commit()
        except:
            self.connection().rollback()
            raise
        finally:
            cur.close()

    def _save_data(self, table: Table, key: str, data: list[str]) -> "Secrets":
        def entry_exists(cur) -> None:
            res = cur.execute(
                f"SELECT * FROM {table.name} WHERE key=?",
                [key])
            return res and res.fetchone()

        def update(cur) -> None:
            columns = ", ".join(f"{c}=?" for c in table.columns)
            cur.execute(
                f"UPDATE {table.name} SET {columns} WHERE key=?",
                data + [key])

        def insert(cur) -> None:
            columns = ",".join(table.columns)
            value_slots = ", ".join("?" for c in table.columns)
            cur.execute(
                (
                    f"INSERT INTO {table.name}"
                    f" (key,{columns})"
                    f" VALUES (?, {value_slots})"
                ),
                [key] + data)

        with self._cursor() as cur:
            if entry_exists(cur):
                update(cur)
            else:
                insert(cur)
        return self

    def save(self, key: str, data: Union[str, Credentials]) -> "Secrets":
        """key represents a system, service, or application"""
        if isinstance(data, str):
            return self._save_data(CONFIG_ITEMS_TABLE, key, [data])
        if isinstance(data, Credentials):
            return self._save_data(SECRETS_TABLE, key, [data.user, data.password])
        raise Exception("Unsupported type of data: " + type(data).__name__)

    def _data(self, table: Table, key: str) -> Optional[list[str]]:
        columns = ", ".join(table.columns)
        with self._cursor() as cur:
            res = cur.execute(
                f"SELECT {columns} FROM {table.name} WHERE key=?",
                [key])
            return res.fetchone() if res else None

    def credentials(self, key: str) -> Optional[Credentials]:
        row = self._data(SECRETS_TABLE, key)
        return Credentials(row[0], row[1]) if row else None

    def config(self, key: str) -> Optional[str]:
        row = self._data(CONFIG_ITEMS_TABLE, key)
        return row[0] if row else None
