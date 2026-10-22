"""Factory functions for common HTTP response bodies."""

def err(msg: str):
    """Returns a dict with 'status' = 'err' and 'message' = `msg`."""
    return {
        'status': 'err',
        'message': msg
    }