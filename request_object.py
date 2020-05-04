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
        if val is None and not self.nullable:
            raise ValueError('field "{}" can\'t be null'.format(self.name))
        self.val = val


class DictField(Field):
    pass


class CharField(Field):
    def __set__(self, obj, val):
        super(CharField, self).__set__(obj, val)
        if val is not None and not isinstance(val, basestring):
            raise ValueError('field "{}" must be a string'.format(self.name))

        self.val = val


class ArgumentsField(DictField):
    pass


class EmailField(CharField):
    pass


class PhoneField(object):
    pass


class DateField(object):
    pass


class BirthDayField(object):
    pass


class GenderField(object):
    pass


class ClientIDsField(object):
    pass


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
