class DBException(Exception):
    pass


class InstantiationException(Exception):
    pass


class MissingResultException(DBException):
    pass


class ForeignKeyException(DBException):
    pass


class ValidationException(Exception):
    pass


class CoercionException(ValidationException):
    pass
