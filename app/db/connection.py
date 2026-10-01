import logging
from contextlib import contextmanager

from psycopg import ClientCursor
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.config import settings

logger = logging.getLogger(__name__)

_pool: ConnectionPool | None = None


def get_connection_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            conninfo=settings.database_url,
            min_size=1,
            max_size=10,
            kwargs={"row_factory": dict_row, "autocommit": True}
        )
        logger.info("Database connection pool initialized")
    return _pool


def close_connection_pool():
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None
        logger.info("Database connection pool closed")


@contextmanager
def get_db_connection():
    pool = get_connection_pool()
    conn = pool.getconn()
    try:
        yield conn
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        pool.putconn(conn)


def _execute_sql_file(path: str) -> None:
    """Run a multi-statement SQL file via the simple query protocol."""
    with open(path, "r", encoding="utf-8") as f:
        script = f.read()
    with get_db_connection() as conn:
        # ClientCursor uses the simple query protocol, which allows
        # multiple statements (needed for schema/seed scripts that
        # contain string literals with semicolons).
        with ClientCursor(conn) as cur:
            cur.execute(script)


def execute_schema():
    _execute_sql_file("app/db/schema.sql")
    logger.info("Database schema executed")


def execute_seed():
    _execute_sql_file("app/db/seed.sql")
    logger.info("Database seed data executed")
