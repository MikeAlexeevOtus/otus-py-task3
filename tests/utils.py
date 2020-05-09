import sys
import functools
import datetime
import contextlib

import mock


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


@contextlib.contextmanager
def mock_today(return_value):
    orig_date = datetime.date
    # taken from https://stackoverflow.com/a/25652721
    with mock.patch('datetime.date') as mock_date:
        mock_date.today.return_value = return_value
        mock_date.side_effect = lambda *args, **kw: orig_date(*args, **kw)
        yield


@contextlib.contextmanager
def mock_redis(mock_redis_instance):
    with mock.patch('redis.Redis', return_value=mock_redis_instance):
        yield
