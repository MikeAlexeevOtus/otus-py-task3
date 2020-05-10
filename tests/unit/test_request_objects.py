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
        {'account': None, 'login': None, 'token': None, 'arguments': [], 'method': 'abc'},
    ])
    def test_validation_fail(self, data):
        mr = MethodRequest(data)
        self.assertTrue(mr.get_validation_errors())

    @cases([
        {'account': None, 'login': None, 'token': None, 'arguments': None, 'method': 'abc'},
        {'account': None, 'login': None, 'token': None, 'arguments': None, 'method': 'abc', 'other_field': 123},
        {'account': 'abc', 'login': 'abc', 'token': 'token', 'arguments': {'arg1': 'val1'}, 'method': 'abc'},
    ])
    def test_validation_pass(self, data):
        mr = MethodRequest(data)
        self.assertFalse(mr.get_validation_errors())


class TestOnlineScoreRequest(unittest.TestCase):
    @cases([
        {},
        '',
        {'phone': None, 'email': None, 'first_name': None, 'last_name': None, 'birthday': None, 'gender': None},
        {'phone': 123, 'email': 'x@otus.ru'},
        {'phone': 71234567891, 'email': 'abc'},
        {'phone': None, 'email': None, 'first_name': 'x', 'last_name': 'y', 'birthday': '10.10.2010', 'gender': 3},
    ])
    def test_validation_fail(self, data):
        osr = OnlineScoreRequest(data)
        self.assertTrue(osr.get_validation_errors())

    @cases([
        {'phone': 71234567891, 'email': 'x@otus.ru'},
        {'first_name': 'x', 'last_name': 'y'},
        {'birthday': '10.10.2010', 'gender': 2},
        {'phone': 71234567891, 'email': 'x@otus.ru', 'first_name': 'x', 'last_name': 'y', 'birthday': '10.10.2010', 'gender': 1},
    ])
    def test_validation_pass(self, data):
        osr = OnlineScoreRequest(data)
        self.assertFalse(osr.get_validation_errors())
