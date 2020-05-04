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


class FieldInitializerMetaclass(type):
    def __init__(cls, name, bases, dct):
        cls._fields = []

        for field_name, field in cls.__dict__.items():
            if not isinstance(field, (Field, DictField)):
                continue

            field.name = field_name
            cls._fields.append(field)


class Field(object):
    def __init__(self, required=True, nullable=False):
        self.required = required
        self.nullable = nullable

    def __get__(self, obj, objtype):
        return obj.__dict__[self.name]

    def __set__(self, obj, val):
        self._validate(val)
        obj.__dict__[self.name] = val

    def _validate(self, val):
        if val is None and not self.nullable:
            raise ValidationError('field "{}" can\'t be null'.format(self.name))


class DictField(Field):
    def _validate(self, val):
        super(DictField, self)._validate(val)
        if val is None:
            return
        elif not isinstance(val, dict):
            raise ValidationError('field "{}" must be a dict'.format(self.name))


class CharField(Field):
    def _validate(self, val):
        super(CharField, self)._validate(val)
        if val is None:
            return
        elif not isinstance(val, basestring):
            raise ValidationError('field "{}" must be a string'.format(self.name))


class ArgumentsField(DictField):
    pass


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
    def _validate(self, val):
        super(DateField, self)._validate(val)
        if val is None:
            return

        try:
            datetime.datetime.strptime(val, DATE_FMT)
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

        if val not in possible_values:
            raise ValidationError(err)


class ClientIDsField(Field):
    def _validate(self, val):
        super(ClientIDsField, self)._validate(val)
        if val is None:
            return

        err = 'field "{}" must be a list of integers'.format(self.name)
        if not isinstance(val, list):
            raise ValidationError(err)

        for id_ in val:
            if not isinstance(id_, int):
                raise ValidationError(err)


class RequestObject(object):
    __metaclass__ = FieldInitializerMetaclass

    def __init__(self, data):
        self._errors = []
        for field in self._fields:
            if field.required and field.name not in data:
                self._errors.append('field "{}" is required'.format(field.name))
                continue

            try:
                setattr(self, field.name, data.get(field.name))
            except ValidationError as e:
                self._errors.append(str(e))

        try:
            self._validate()
        except ValidationError as e:
            self._errors.append(str(e))

    def _validate(self):
        """default nop implementation"""

    def get_validation_errors(self):
        return self._errors

    def asdict(self):
        data = {}
        for field in self._fields:
            data[field.name] = getattr(self, field.name)

        return data


class ClientsInterestsRequest(RequestObject):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)

    @property
    def nclients(self):
        if self.get_validation_errors():
            raise RuntimeError('can\'t get nclients from invalid request object')

        return len(self.client_ids)


class OnlineScoreRequest(RequestObject):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    REQUIRED_PAIRS = [
        (phone, email),
        (first_name, last_name),
        (gender, birthday),
    ]

    @property
    def initialized_fields(self):
        if self.get_validation_errors():
            raise RuntimeError('can\'t get nclients from invalid request object')

        return [field.name for field in self._fields if getattr(self, field.name) is not None]

    def _validate(self):
        for field_a, field_b in self.REQUIRED_PAIRS:
            if getattr(self, field_a.name) and getattr(self, field_b.name):
                return

        required_pairs_repr = [
            (field_a.name, field_b.name) for field_a, field_b in self.REQUIRED_PAIRS
        ]
        raise ValidationError('one of these pairs must be set: {}'.format(required_pairs_repr))


class MethodRequest(RequestObject):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)


if __name__ == '__main__':
    mr = MethodRequest({
        'login': 'x',
        'arguments': {},
        'method': 123,
        'token': 'abc'
    })
