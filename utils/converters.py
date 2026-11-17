"""Functions to convert from one form to another."""

import base64

def try_int(s: str):
    """Returns `s` as integer; None if failed."""
    try:
        return int(s)
    except ValueError:
        return None

def memoryview_to_b64(mv: memoryview):
    """Returns `mv` as a Base64 string."""
    return base64.b64encode(mv.tobytes())
