import unittest

import mock
from redis.exceptions import ConnectionError

from storage import Storage
from utils import mock_redis


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
