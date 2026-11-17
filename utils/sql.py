"""Common SQL operations."""

from typing import Any, Iterable
from utils import constants

def set_deleted(conn, entity: str, id: int):
    """Sets the row of `entity` with `id` as deleted."""
    with conn.cursor() as c:
        c.execute(
            f'update { entity } set deleted = true ' +
            'where id = %s',
            [id]
        )
        conn.commit()

def get_init_cursor_pos(
    conn,
    unsorted_sql: str,
    column: str,
    param_vals: Iterable[Any] = []
) -> int:
    """
    Executes `unsorted_sql` consisting on a set of integers to determine a cursor to paginate a last-to-first query.
    `column` is the column name of the set.
    """
    with conn.cursor() as c:
        c.execute(
            f'{ unsorted_sql } order by { column } desc limit 1',
            param_vals
        )
        max_id_row = c.fetchone()

        if max_id_row:
            return max_id_row[0] + 1
        return constants.FINAL_CURSOR_POS

def fetch_paginated(
    conn,
    unsrt_unpg_sql: str,
    sort_column: str,
    param_vals: Iterable[Any] = [],
    cursor_pos: int = 1
) -> list[tuple[Any, ...]]:
    """
    Executes `unsrt_unpg_sql`, sorted descending by `sort_column`.
    Returns paginated results.
    Note: WHERE is assumed to be in the SQL string.
    """
    with conn.cursor() as c:
        c.execute(
            f'{ unsrt_unpg_sql } and { sort_column }' +
            ' < %s' +
            f' order by { sort_column } desc limit { constants.PAGE_SIZE }',
            [val for val in param_vals] + [cursor_pos]
        )
        return c.fetchall()
    