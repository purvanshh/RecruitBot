import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from contextlib import contextmanager
import logging
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


def execute_schema():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            with open("app/db/schema.sql", "r") as f:
                cur.execute(f.read())
    logger.info("Database schema executed")


def execute_seed():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            with open("app/db/seed.sql", "r") as f:
                cur.execute(f.read())
    logger.info("Database seed data executed")