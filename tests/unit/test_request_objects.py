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
        {'account': None, 'login': None},
        {'account': None, 'login': 123, 'token': None, 'arguments': None, 'method': 'abc'},
    ])
    def test_validation_fail(self, data):
        mr = MethodRequest(data)
        self.assertTrue(mr.get_validation_errors())

    @cases([
        {'account': None, 'login': None, 'token': None, 'arguments': None, 'method': 'abc'},
        {'account': None, 'login': None, 'token': None, 'arguments': None, 'method': 'abc', 'other_field': 123},
    ])
    def test_validation_pass(self, data):
        mr = MethodRequest(data)
        self.assertFalse(mr.get_validation_errors())
