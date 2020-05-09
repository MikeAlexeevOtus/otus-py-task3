from field import (
    ValidationError,
    Field,
    ArgumentsField,
    BirthDayField,
    CharField,
    ClientIDsField,
    DateField,
    EmailField,
    GenderField,
    PhoneField
)


class FieldInitializerMetaclass(type):
    """metaclass for fields names initialization"""

    def __init__(cls, name, bases, dct):
        cls._fields = []

        for field_name, field in cls.__dict__.items():
            if not isinstance(field, Field):
                continue

            field.name = field_name
            cls._fields.append(field)


class RequestObject(object):
    __metaclass__ = FieldInitializerMetaclass

    def __init__(self, data):
        self._errors = []
        if not isinstance(data, dict):
            self._errors.append('data must be a dict')
            return

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
        """any additional fields validation should be done here"""

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
            if (getattr(self, field_a.name) is not None and
                    getattr(self, field_b.name) is not None):
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
