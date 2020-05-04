import datetime

ADMIN_LOGIN = "admin"
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


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
        return self.val

    def __set__(self, obj, val):
        self._validate(val)
        self.val = val

    def _validate(self, val):
        if val is None and not self.nullable:
            raise ValueError('field "{}" can\'t be null'.format(self.name))


class DictField(Field):
    def _validate(self, val):
        super(DictField, self)._validate(val)
        if val is not None and not isinstance(val, dict):
            raise ValueError('field "{}" must be a dict'.format(self.name))


class CharField(Field):
    def _validate(self, val):
        super(CharField, self)._validate(val)
        if val is not None and not isinstance(val, basestring):
            raise ValueError('field "{}" must be a string'.format(self.name))


class ArgumentsField(DictField):
    pass


class EmailField(CharField):
    pass


class PhoneField(object):
    pass


class DateField(CharField):
    def _validate(self, val):
        super(DateField, self)._validate(val)
        try:
            datetime.datetime.strptime(val, '%d.%m.%Y')
        except ValueError:
            raise ValueError('field "{}" must be a string in format "DD.MM.YYYY"'.format(self.name))


class BirthDayField(object):
    pass


class GenderField(Field):
    def _validate(self, val):
        super(GenderField, self)._validate(val)
        possible_values = sorted(GENDERS.keys())
        err = 'field "{}" must be an integer, one of {}'.format(
            self.name,
            ', '.join(str(i) for i in possible_values)
        )

        if val is not None and not isinstance(val, int):
            raise ValueError(err)
        elif val not in possible_values:
            raise ValueError(err)


class ClientIDsField(Field):
    def _validate(self, val):
        super(ClientIDsField, self)._validate(val)
        err = 'field "{}" must be a list of integers'.format(self.name)
        if val is not None and not isinstance(val, list):
            raise ValueError(err)

        for id_ in val:
            if not isinstance(id_, int):
                raise ValueError(err)


class ClientsInterestsRequest(object):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(object):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)


class MethodRequest(object):
    __metaclass__ = FieldInitializerMetaclass

    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    def __init__(self, data):
        for field in self._fields:
            if field.required and field.name not in data:
                raise ValueError('field "{}" is required'.format(field.name))

            setattr(self, field.name, data.get(field.name))

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


if __name__ == '__main__':
    mr = MethodRequest({
        'login': 'x',
        'arguments': {},
        'method': 123,
        'token': 'abc'
    })
