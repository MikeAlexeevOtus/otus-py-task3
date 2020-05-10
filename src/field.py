import datetime

UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}

DATE_FMT = '%d.%m.%Y'


class ValidationError(ValueError):
    pass


class Field(object):
    """descriptor class for field validation"""

    def __init__(self, required=True, nullable=False, name=None):
        self.required = required
        self.nullable = nullable
        self.name = name

    def __get__(self, obj, objtype):
        return obj.__dict__.get(self.name)

    def __set__(self, obj, val):
        self._validate(val)
        obj.__dict__[self.name] = val

    def _validate(self, val):
        if val is None and not self.nullable:
            # basic validation
            # more checks in subclasses
            raise ValidationError('field "{}" can\'t be null'.format(self.name))

    def __repr__(self):
        return (
            '<{type} name: "{name}", '
            'required: {required} , '
            'nullable: {nullable}>'
        ).format(
            type=type(self),
            name=self.name,
            required=self.required,
            nullable=self.nullable
        )


class CharField(Field):
    def _validate(self, val):
        super(CharField, self)._validate(val)
        if val is None:
            return
        elif not isinstance(val, basestring):
            raise ValidationError('field "{}" must be a string'.format(self.name))


class ArgumentsField(Field):
    def _validate(self, val):
        super(ArgumentsField, self)._validate(val)
        if val is None:
            return
        elif not isinstance(val, dict):
            raise ValidationError('field "{}" must be a dict'.format(self.name))


class EmailField(CharField):
    def _validate(self, val):
        super(EmailField, self)._validate(val)
        if val is None:
            return
        elif '@' not in val:
            raise ValidationError('field "{}" must be a valid email addr'.format(self.name))


class PhoneField(Field):
    STRLEN = 11
    FIRST_CHAR = '7'

    def _validate(self, val):
        super(PhoneField, self)._validate(val)
        if val is None:
            return

        err = 'field "{}" must be an integer or string, 11 chars len starting with 7'.format(self.name)
        if not isinstance(val, (int, basestring)):
            raise ValidationError(err)

        val = str(val)
        if any([
                not val.isdigit(),
                len(val) != self.STRLEN,
                val[0] != self.FIRST_CHAR,
        ]):
            raise ValidationError(err)


class DateField(CharField):
    def __set__(self, obj, val):
        self._validate(val)
        obj.__dict__[self.name] = self._parse_date(val)

    def _parse_date(self, val):
        if val:
            return datetime.datetime.strptime(val, DATE_FMT)

    def _validate(self, val):
        super(DateField, self)._validate(val)
        if val is None:
            return

        try:
            self._parse_date(val)
        except ValueError:
            raise ValidationError('field "{}" must be a string in format "DD.MM.YYYY"'.format(self.name))


class BirthDayField(DateField):
    MAX_AGE = 70

    def _validate(self, val):
        super(BirthDayField, self)._validate(val)
        if val is None:
            return

        birth_dt = datetime.datetime.strptime(val, DATE_FMT)
        if datetime.date.today().year - birth_dt.year > self.MAX_AGE:
            raise ValidationError('age more than {} years in field "{}"'.format(self.MAX_AGE, self.name))


class GenderField(Field):
    def _validate(self, val):
        super(GenderField, self)._validate(val)
        if val is None:
            return

        possible_values = sorted(GENDERS.keys())
        err = 'field "{}" must be an integer, one of {}'.format(
            self.name,
            ', '.join(str(i) for i in possible_values)
        )

        if not isinstance(val, int) or val not in possible_values:
            raise ValidationError(err)


class ClientIDsField(Field):
    def _validate(self, val):
        super(ClientIDsField, self)._validate(val)
        if val is None:
            return

        err = 'field "{}" must be a list of non-negative integers'.format(self.name)
        if not isinstance(val, list) or not val:
            raise ValidationError(err)

        for id_ in val:
            if not isinstance(id_, int) or id_ < 0:
                raise ValidationError(err)
