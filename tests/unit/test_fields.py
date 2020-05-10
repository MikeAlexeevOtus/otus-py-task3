#! encoding: utf-8
import unittest
import datetime

from field import (
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

from utils import cases, patch_today


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
        # can set None
        cls(nullable=True)._validate(None)

        # can't set None
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

    @cases(['10.10.2020', '07.07.1020', '5.5.2020', '5.05.2020'])
    def test_datetime_allowed(self, value):
        DateField()._validate(value)

    @cases([DateField, BirthDayField])
    @cases(['10102020', '10.10', '10-10-2020', '2020.03.10', 'abcd',
            '32.10.2020', '15.13.2020', '005.05.2020'])
    def test_datetime_forbidden(self, cls, value):
        with self.assertRaisesRegexp(ValidationError, "must be a string in format"):
            cls()._validate(value)

    @cases(['01.01.1935', '01.01.2000', '01.01.2030'])
    def test_birthdate_allowed(self, value):
        with patch_today(datetime.date(2000, 1, 1)):
            BirthDayField()._validate(value)

    def test_birthdate_forbidden(self):
        with patch_today(datetime.date(2000, 1, 1)), \
                self.assertRaisesRegexp(ValidationError, "age more than"):
            BirthDayField()._validate('31.12.1929')

    @cases([0, 1, 2])
    def test_gender_allowed(self, value):
        GenderField()._validate(value)

    @cases([-1, 0.0, 3, 3.0, 'abc', '', [], ])
    def test_gender_forbidden(self, value):
        with self.assertRaisesRegexp(ValidationError, "must be an integer, one of"):
            GenderField()._validate(value)

    @cases([
        '71234567891',
        71234567891
    ])
    def test_phone_allowed(self, value):
        PhoneField()._validate(value)

    @cases([
        123,
        -1,
        0,
        '7123456789',
        7123456789,
        'not-a-number',
        61234567891,
    ])
    def test_phone_forbidden(self, value):
        with self.assertRaisesRegexp(ValidationError, "must be an integer or string, 11 chars"):
            PhoneField()._validate(value)

    @cases([
        [0, 1],
        [3],
    ])
    def test_clientids_allowed(self, value):
        ClientIDsField()._validate(value)

    @cases([
        [],
        {},
        '',
        [''],
        [1, None],
        [2, -1],
    ])
    def test_clientids_forbidden(self, value):
        with self.assertRaisesRegexp(ValidationError, "must be a list of non-negative"):
            ClientIDsField()._validate(value)
