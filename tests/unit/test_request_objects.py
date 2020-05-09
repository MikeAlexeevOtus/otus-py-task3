import unittest

from request_object import (
    MethodRequest,
    OnlineScoreRequest,
    RequestObject
)
from utils import cases, mock_today


class TestMethodRequest(unittest.TestCase):
    @cases([
        {},
        '',
        dict(account=None, login=None),
    ])
    def test_validation_fail(self, data):
        mr = MethodRequest(data)
        self.assertTrue(mr.get_validation_errors())

    @cases([
        dict(account=None, login=None, token=None, arguments=None, method='abc'),
        dict(account=None, login=None, token=None, arguments=None, method='abc', other_field=10)
    ])
    def test_validation_pass(self, data):
        mr = MethodRequest(data)
        self.assertFalse(mr.get_validation_errors())
