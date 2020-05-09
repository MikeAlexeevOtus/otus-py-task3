#! encoding: utf-8
import unittest

from request_object import (
    Field,
    ValidationError,
    ArgumentsField,
    BirthDayField,
    CharField,
    ClientIDsField,
    DateField,
    EmailField,
    GenderField,
    PhoneField,
)

from utils import cases


class TestFields(unittest.TestCase):
    @cases([
        Field,
        ArgumentsField,
        BirthDayField,
        CharField,
        ClientIDsField,
        DateField,
        EmailField,
        GenderField,
        PhoneField,
    ])
    def test_nullable(self, cls):
        field = cls(nullable=True)
        field._validate(None)

        field = cls(nullable=False)
        with self.assertRaisesRegexp(ValidationError, "can't be null"):
            field._validate(None)

    @cases(['', u'', 'abc', u'фыва'])
    def test_charfield_allowed(self, value):
        field = CharField()
        field._validate(value)

    @cases([CharField, EmailField])
    @cases([0, 42, {}, []])
    def test_charfield_forbidden(self, cls, value):
        field = EmailField()
        with self.assertRaisesRegexp(ValidationError, "must be a string"):
            field._validate(value)

    @cases(['abcd@abcd', u'фыва@фыва'])
    def test_email_allowed(self, value):
        field = EmailField()
        field._validate(value)

    @cases(['abcd', u'фыва', '', u''])
    def test_email_forbidden(self, value):
        field = EmailField()
        with self.assertRaisesRegexp(ValidationError, "must be a valid email addr"):
            field._validate(value)
