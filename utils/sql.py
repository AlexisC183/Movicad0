"""Common SQL operations."""

def set_deleted(conn, entity: str, id: int):
    """Sets the row of `entity` with `id` as deleted."""
    with conn.cursor() as c:
        c.execute(
            f'update { entity } set deleted = true ' +
            'where id = %s',
            [id]
        )
        conn.commit()
