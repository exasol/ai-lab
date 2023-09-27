from dataclasses import dataclass
from sqlcipher3 import dbapi2 as sqlcipher
import logging
import os
from typing import Optional, Union


_logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO, format="%(message)s")


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
            if not os.path.exists(self.db_file):
                _logger.info(f"Creating file {self.db_file}")
            self._con = sqlcipher.connect(self.db_file)
            self._use_master_password()
            self.create_tables()
        return self._con

    def _use_master_password(self) -> None:
        """
        If database is unencrypted then this method encrypts it.
        If database is already encrypted then this method enables to access the data.
        """
        if self.master_password is not None:
            sanitized = self.master_password.replace("'", "\\'")
            self.cursor().execute(f"PRAGMA key = '{sanitized}'")

    def cursor(self) -> sqlcipher.Cursor:
        if self._cur is None:
            self._cur = self.connection().cursor()
        return self._cur

    def has_table(self, name: str) -> bool:
        res = self.cursor().execute("SELECT * FROM sqlite_master where name = ?", [name])
        return True if res and res.fetchone() else False

    # key represents a system, service, or application
    def create_table(self, table: Table) -> None:
        if self.has_table(table.name):
            return
        _logger.info(f'Creating table "{table.name}".')
        columns = " ,".join(table.columns)
        self.cursor().execute(f"CREATE TABLE {table.name} (key, {columns})")
        self.connection().commit()

    def create_tables(self) -> None:
        for table in (SECRETS_TABLE, CONFIG_ITEMS_TABLE):
            self.create_table(table)

    def _save_data(self, table: Table, key: str, data: list[str]) -> "Secrets":
        cur = self.cursor()
        res = cur.execute(f"SELECT * FROM {table.name} WHERE key=?", [key])
        if res and res.fetchone():
            columns = ", ".join(f"{c}=?" for c in table.columns)
            cur.execute(
                f"UPDATE {table.name} SET {columns} WHERE key=?",
                data + [key])
        else:
            columns = ", ".join("?" for c in table.columns)
            cur.execute(
                f"INSERT INTO {table.name} VALUES (?, {columns})",
                [key] + data)
        self.connection().commit()
        return self

    # def save_config_item(self, key: str, item: str) -> None:
    #     self._save_data(CONFIG_ITEMS_TABLE, key, [item])
    #
    # def save_credentials(self, key: str, user: str, password: str) -> None:
    #     self._save_data(SECRETS_TABLE, key, [user, password])

    def save(self, key: str, data: Union[str, Credentials]) -> "Secrets":
        if isinstance(data, str):
            return self._save_data(CONFIG_ITEMS_TABLE, key, [data])
        if isinstance(data, Credentials):
            return self._save_data(SECRETS_TABLE, key, [data.user, data.password])
        raise Exception("Unsupported type of data: " + type(data).__name__)

    def _get_data(self, table: Table, key: str) -> Optional[list[str]]:
        columns = ", ".join(table.columns)
        res = self.cursor().execute(
            f"SELECT {columns} FROM {table.name} WHERE key=?",
            [key])
        return res.fetchone() if res else None

    def get_credentials(self, key: str) -> Optional[Credentials]:
        row = self._get_data(SECRETS_TABLE, key)
        return Credentials(row[0], row[1]) if row else None

    def get_config_item(self, key: str) -> Optional[str]:
        row = self._get_data(CONFIG_ITEMS_TABLE, key)
        return row[0] if row else None


# def sample_usage():
#     secrets = Secrets("mydb.db", master_password="my secret master password")
#
#     c = secrets.get_credentials("aws")
#     print(f'old value of aws credentials {c}')
#     secrets.save("aws", Credentials("user-a", "pwd-aaa"))
#     c = secrets.get_credentials("aws")
#     print(f'aws credentials: {c}')
#
#     c = secrets.get_config_item("url")
#     print(f'old value of config item "url" {c}')
#     secrets.save("url", "http://def")
#     c = secrets.get_config_item("url")
#     print(f'config item url: {c}')
#
#
# if __name__ == "__main__":
#     sample_usage()
