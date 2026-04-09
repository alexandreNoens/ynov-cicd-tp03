import os
from pathlib import Path

import psycopg2
from psycopg2.extensions import connection as PgConnection

ROOT_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT_DIR / "sql" / "provisioning.sql"
DEV_DATA_PATH = ROOT_DIR / "sql" / "dev-data.sql"
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres"
)


def get_connection() -> PgConnection:
    return psycopg2.connect(DATABASE_URL)


def _execute_sql_script(connection: PgConnection, script: str) -> None:
    with connection.cursor() as cursor:
        cursor.execute(script)


def init_db() -> None:
    with get_connection() as connection:
        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        _execute_sql_script(connection, schema)
        connection.commit()


def reset_db() -> None:
    with get_connection() as connection:
        _execute_sql_script(
            connection, "DROP TABLE IF EXISTS students CASCADE;"
        )
        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        _execute_sql_script(connection, schema)
        dev_data = DEV_DATA_PATH.read_text(encoding="utf-8")
        _execute_sql_script(connection, dev_data)
        connection.commit()
