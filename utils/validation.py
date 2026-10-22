"""Functions to validate the format of objects."""

from typing import Callable, Dict, Tuple, Optional, Any

def assertion_fail(
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
