"""Factory functions for common HTTP response bodies."""

from typing import Any

def err(msg: str):
    """Returns a dict with 'status' = 'err' and 'message' = `msg`."""
    return {
        'status': 'err',
        'message': msg
    }

def log_err(e: Exception):
    """Returns a dict with a generic error message to expose to clients, while printing `e`."""
    print(e)
    return err('No se pudieron obtener o guardar datos')

def no_account():
    """Returns a dict with a message of deleted account."""
    return err('Su cuenta ha sido eliminada. No se puede proseguir.')

def ok(data: Any = None):
    """Returns a dict with 'status' = 'ok' and optionally the supplied `data`."""
    body = { 'status': 'ok' }
    if data is not None:
        body['data'] = data
    return body
