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

_SCHEMA_SQL = SCHEMA_PATH.read_text(encoding="utf-8")  # NOSONAR
_DEV_DATA_SQL = DEV_DATA_PATH.read_text(encoding="utf-8")  # NOSONAR


def get_connection() -> PgConnection:
    return psycopg2.connect(DATABASE_URL)


def init_db() -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(_SCHEMA_SQL)
        connection.commit()


def reset_db() -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS students CASCADE;")
            cursor.execute(_SCHEMA_SQL)
            cursor.execute(_DEV_DATA_SQL)
        connection.commit()
