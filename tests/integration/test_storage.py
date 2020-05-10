import unittest

import mock
from redis.exceptions import ConnectionError

from storage import Storage
from utils import mock_redis, start_redis, stop_redis


class TestStorageOffline(unittest.TestCase):
    def test_get_cache_timeout(self):
        storage = Storage()
        self.assertEqual(storage.cache_get('key'), None)

    def test_get_timeout_fails(self):
        storage = Storage()
        with self.assertRaisesRegexp(ConnectionError, "gave up"):
            storage.get('key')

    def test_get_cache_timeout_retries(self):
        mock_r = mock.Mock()
        mock_r.get.side_effect = ConnectionError()
        with mock_redis(mock_r):
            storage = Storage()
            storage.cache_get('key')

        self.assertEqual(mock_r.get.call_count, 5)

    def test_get_timeout_retries(self):
        mock_r = mock.Mock()
        mock_r.get.side_effect = ConnectionError()
        with mock_redis(mock_r), \
                self.assertRaisesRegexp(ConnectionError, "gave up"):
            storage = Storage()
            storage.get('key')

        self.assertEqual(mock_r.get.call_count, 5)


class TestStorageOnline(unittest.TestCase):
    REDIS_PORT = 15000

    def setUp(self):
        self._container_id = start_redis(self.REDIS_PORT)

    def tearDown(self):
        stop_redis(self._container_id)

    def test_get_cache(self):
        storage = Storage(port=self.REDIS_PORT)
        storage.cache_set('key1', 'val1', 60)
        storage.cache_set('key2', 'val2', 60)

        self.assertEqual(storage.cache_get('key1'), 'val1')
        self.assertEqual(storage.cache_get('key2'), 'val2')
        self.assertEqual(storage.cache_get('not-set'), None)
