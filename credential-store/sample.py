from sqlcipher3 import dbapi2 as sqlite3
import logging
from typing import Optional


_logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO, format="%(message)s")


class Secrets:
    def __init__(self, db_file: str) -> None:
        self.db_file = db_file
        self.master_password = None
        self.table_name = "secrets"
        self._con = None
        self._cur = None

    def connection(self) -> sqlite3.Connection:
        if self._con is None:
            self._con = sqlite3.connect(self.db_file)
            self._use_master_password()
            self.create_table()
        return self._con

    def _use_master_password(self) -> None:
        if self.master_password is not None:
            # print(f'using master password {self.master_password}')
            self.cursor().execute(f"PRAGMA key = '{self.master_password}'")

    def cursor(self) -> sqlite3.Cursor:
        if self._cur is None:
            self._cur = self.connection().cursor()
        return self._cur

    def encrypt_database(cur: sqlite3.Cursor) -> None:
        self._use_master_password()

    def has_table(self, name: str) -> bool:
        cur = self.cursor()
        res = cur.execute("SELECT * FROM sqlite_master where name = ?", [name])
        return True if res and res.fetchone() else False

    # key represents a system, service, or application
    def create_table(self) -> None:
        if self.has_table("secrets"):
            return
        _logger.info(f'Creating table "{self.table_name}".')
        self.cursor().execute(
            f"CREATE TABLE {self.table_name} (key, user, password)"
        )
        self.connection().commit()

    def save_credentials(self, key: str, user: str, password: str) -> None:
        cur = self.cursor()
        res = cur.execute(f"SELECT * FROM {self.table_name} WHERE key=?", [key])
        if res and res.fetchone():
            cur.execute(
                f"UPDATE {self.table_name} SET user=?, password=? WHERE key=?",
                [user, password, key])
        else:
            cur.execute(
                f"INSERT INTO {self.table_name} VALUES (?, ?, ?)",
                [key, user, password])
        self.connection().commit()

    def get_credentials(self, key: str) -> Optional[list[str]]:
        res = self.cursor().execute(
            f"SELECT user, password FROM {self.table_name} WHERE key=?",
            [key])
        return res.fetchone() if res else None


def sample_usage():
    secrets = Secrets("mydb.db")
    secrets.master_password = "my secret master password"
    secrets.save_credentials("aws", "user-a", "pwd-a")
    c = secrets.get_credentials("aws")
    print(f'{c}')


if __name__ == "__main__":
    sample_usage()
