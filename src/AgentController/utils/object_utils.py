"""
Project:
Author:
"""


def is_object_has_method(obj, method_name):
    assert isinstance(method_name, str)
    maybe_method = getattr(obj, method_name, None)
    return callable(maybe_method)

def is_valid(obj):
    if( obj is None or not obj):
        return False
    else:
        return True

__all__ = ['is_object_has_method']
