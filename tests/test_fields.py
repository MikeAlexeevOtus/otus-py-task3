#! encoding: utf-8
import unittest


from request_object import (
    Field,
    CharField,
    ValidationError,
)
from utils import cases


class TestFields(unittest.TestCase):
    def test_nullable_forbidden(self):
        field = Field(nullable=False)
        field._validate(0)   # any not-None value

        with self.assertRaisesRegexp(ValidationError, "can't be null"):
            field._validate(None)

    @cases([
        0,  # any not-None value
        None
    ])
    def test_nullable_allowed(self, value):
        field = Field(nullable=True)
        field._validate(value)

    @cases([None, '', u'', 'abc', u'фыва'])
    def test_charfield_allowed(self, value):
        field = CharField(nullable=True)
        field._validate(value)

    @cases([0, 42, {}, []])
    def test_charfield_forbidden(self, value):
        field = CharField(nullable=True)
        with self.assertRaisesRegexp(ValidationError, "must be a string"):
            field._validate(value)
