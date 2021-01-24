class DBException(Exception):
    pass


class MissingResultException(DBException):
    pass


class ForeignKeyException(DBException):
    pass


class ValidationError(Exception):
    pass


class CoercionError(ValidationError):
    pass