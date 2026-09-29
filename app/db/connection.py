import psycopg
from psycopg.rows import dict_row
from contextlib import contextmanager
from app.config import settings


@contextmanager
def get_db_connection():
    conn = psycopg.connect(
        settings.database_url,
        row_factory=dict_row,
        autocommit=True
    )
    try:
        yield conn
    finally:
        conn.close()


def execute_schema():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            with open("app/db/schema.sql", "r") as f:
                cur.execute(f.read())


def execute_seed():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            with open("app/db/seed.sql", "r") as f:
                cur.execute(f.read())