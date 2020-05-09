import unittest


from request_object import (
    Field,
    ValidationError,
)
from utils import cases


class TestFields(unittest.TestCase):
    def test_nullable_forbidden(self):
        field = Field(nullable=False)
        field._validate(0)   # any not-None value

        with self.assertRaisesRegexp(ValidationError, "can't be null"):
            field._validate(None)

    def test_nullable_allowed(self):
        field = Field(nullable=True)
        field._validate(0)   # any not-None value
        field._validate(None)
