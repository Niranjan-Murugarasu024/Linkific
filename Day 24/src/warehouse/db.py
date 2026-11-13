from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from warehouse.config import connect


@contextmanager
def database_connection() -> Iterator:
    connection = connect()
    try:
        yield connection
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
