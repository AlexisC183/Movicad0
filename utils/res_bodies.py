"""Factory functions for common HTTP response bodies."""

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
