"""Functions to validate the format of objects."""

from typing import Callable, Dict, Tuple, Optional, Any, Literal
from utils import constants
import base64
import re

def class_fail(
    obj: Any,
    validators: Dict[str, Tuple[Callable[[Any], bool], Callable[[], Any]]]
) -> Optional[Any]:
    """
    Executes validators in order. 
    Short-circuits on the first failure and returns the invocation.
    Returns None if all validations pass.
    """
    for field_name, (pred, suppl) in validators.items():
        if hasattr(obj, field_name):
            value = getattr(obj, field_name)
            if not pred(value):
                return suppl()
    return None


def vars_fail(
    *val_pred_suppl_tuples: Tuple[
        Any,
        Callable[[Any], bool],
        Callable[[], Any]
    ]
) -> Optional[Any]:
    """
    For each tuple applies the predicate on the object and invokes the supplier on the first false test.
    Returns None if all validations pass.
    """
    for (val, pred, suppl) in val_pred_suppl_tuples:
        if not pred(val):
            return suppl()
    return None

def validate_file(
    data_uri: str,
    byte_max_size: int,
    media_type_pattern: str = '.+/.+'
) -> tuple[Literal[True], dict] | tuple[Literal[False], str]:
    """Checks whether `data_uri` is valid according to `media_type_pattern` and `byte_max_size`.
    Returns a success bool and the result from parsing the data URI."""
    if not re.match(f'data:{ media_type_pattern };base64,', data_uri):
        return (False, 'URI de archivo no válida')
    
    [meta, data] = data_uri.split(',')
    media_type = meta[5:meta.index(';')]

    try:
        bytes = base64.b64decode(data)
    except Exception:
        return (False, 'Cadena Base64 de archivo no válida')

    if len(bytes) > byte_max_size:
        return (False, f'El archivo no puede exceder los { byte_max_size / constants.MEGABYTE } MB')

    return (True, {
        'media_type': media_type,
        'content': memoryview(bytes)
    })
    