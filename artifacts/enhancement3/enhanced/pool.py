import logging
import os

from psycopg_pool import ConnectionPool, PoolTimeout

logger = logging.getLogger(__name__)


def _build_pool() -> ConnectionPool:
    """
    Build the connection pool, failing loudly and with a clear log
    message if DATABASE_URL is missing or the pool cannot be created,
    instead of crashing later with an unrelated-looking error.
    """
    try:
        database_url = os.environ["DATABASE_URL"]
    except KeyError:
        logger.critical("DATABASE_URL environment variable is not set.")
        raise

    try:
        return ConnectionPool(conninfo=database_url)
    except Exception:
        logger.critical("Failed to create the database connection pool.")
        raise


pool = _build_pool()


def get_connection():
    """
    Acquire a connection from the pool, with a clear, logged error if
    the pool is exhausted or unavailable, rather than letting a raw
    psycopg_pool exception surface to the caller.

    Use this via `with get_connection() as conn:` anywhere a query
    module needs a connection; it wraps the same pool.connection()
    context manager with error handling.
    """
    try:
        return pool.connection()
    except PoolTimeout:
        logger.exception("Timed out waiting for a database connection.")
        raise
    except Exception:
        logger.exception("Unexpected error acquiring a database connection.")
        raise
