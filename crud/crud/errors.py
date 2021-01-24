class DBException(Exception):
    pass


class MissingResultException(DBException):
    pass


class ForeignKeyException(DBException):
    pass