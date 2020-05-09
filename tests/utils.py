import sys
import functools


def cases(cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in cases:
                new_args = args + (c if isinstance(c, tuple) else (c,))
                try:
                    f(*new_args)
                except Exception:
                    # Reraise exception with modified error message
                    # This is py2 solution. For py3 use raise from
                    type_, value, traceback = sys.exc_info()
                    raise type_, 'Error in case {}: {}'.format(c, value), traceback
        return wrapper
    return decorator
