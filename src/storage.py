import time
import copy
import functools
import logging

import redis
from redis.exceptions import ConnectionError


class Storage(object):
    RETRY_INTERVAL_SEC = 1
    RETRY_N = 5
    DEFAULT_REDIS_OPTS = {
        'socket_timeout': 10,
        'socket_connect_timeout': 10,
    }

    def __init__(self, redis_opts=None):
        redis_opts = redis_opts or {}
        redis_kwargs = copy.deepcopy(self.DEFAULT_REDIS_OPTS)
        redis_kwargs.update(redis_opts)

        self._redis = redis.Redis(**redis_kwargs)

    def _retry(raise_=True):
        def decorator(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                self = args[0]
                for i in range(self.RETRY_N):
                    logging.debug('try to %s', f.__name__)
                    try:
                        return f(*args, **kwargs)
                    except Exception as e:
                        logging.warning('catched error "%s", retry "%s"', e, f.__name__)
                        time.sleep(self.RETRY_INTERVAL_SEC)

                if raise_:
                    raise ConnectionError('gave up after {} retries'.format(self.RETRY_N))
            return wrapper
        return decorator

    @_retry(raise_=False)
    def cache_get(self, key):
        return self._redis.get(key)

    @_retry(raise_=False)
    def cache_set(self, key, value):
        self._redis.set(key, value)

    @_retry(raise_=True)
    def get(self, key):
        return self._redis.get(key)

    @_retry(raise_=True)
    def set(self, key, value):
        self._redis.set(key, value)
