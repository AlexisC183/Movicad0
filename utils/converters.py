"""Functions to convert from one form to another."""

def try_int(s: str):
    """Returns `s` as integer; None if failed."""
    try:
        return int(s)
    except ValueError:
        return None
