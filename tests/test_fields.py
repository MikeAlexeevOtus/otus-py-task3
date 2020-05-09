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
        cls(nullable=True)._validate(None)

        with self.assertRaisesRegexp(ValidationError, "can't be null"):
            cls(nullable=False)._validate(None)

    @cases(['', u'', 'abc', u'фыва'])
    def test_charfield_allowed(self, value):
        CharField()._validate(value)

    @cases([CharField, EmailField, BirthDayField, DateField])
    @cases([0, 42, {}, []])
    def test_charfield_forbidden(self, cls, value):
        with self.assertRaisesRegexp(ValidationError, "must be a string"):
            cls()._validate(value)

    @cases(['abcd@abcd', u'фыва@фыва'])
    def test_email_allowed(self, value):
        EmailField()._validate(value)

    @cases(['abcd', u'фыва', '', u''])
    def test_email_forbidden(self, value):
        with self.assertRaisesRegexp(ValidationError, "must be a valid email addr"):
            EmailField()._validate(value)

    @cases([{}, {1: 10}, {'abc': 'x'}])
    def test_arguments_allowed(self, value):
        ArgumentsField()._validate(value)

    @cases(['', 0, 10, 'abc', [], [1, 2], ])
    def test_arguments_forbidden(self, value):
        with self.assertRaisesRegexp(ValidationError, "must be a dict"):
            ArgumentsField()._validate(value)

    @cases(['10.10.2020', '07.07.2020', '5.5.2020', '5.05.2020'])
    def test_datetime_allowed(self, value):
        DateField()._validate(value)

    @cases([DateField, BirthDayField])
    @cases(['10102020', '10.10', '10-10-2020',
            '32.10.2020', '15.13.2020', '005.05.2020'])
    def test_datetime_forbidden(self, cls, value):
        with self.assertRaisesRegexp(ValidationError, "must be a string in format"):
            cls()._validate(value)
