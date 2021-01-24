# -*- coding: utf-8 -*-
from collections.abc import Iterable
from dataclasses import dataclass, field, fields, MISSING
from datetime import datetime
from enum import Enum, unique

from .database import connection
from .errors import ForeignKeyException, InstantiationException
from .utils import IDs, Names, log
from .validators import Validator


@dataclass
class Model:
    id: int
    name: str

    _excluded = ("id",)
    _foreign_keys = {}

    _validation_schema = {}

    key_format = "{model}:{id}:{attribute}"

    class Read:
        class Commands:
            @staticmethod
            def get(key):
                return f"GET {key}"

        class Converters:
            @staticmethod
            def _all(value):
                if value is None:
                    return
                return value.decode("utf-8")

    class Write:
        class Commands:
            @staticmethod
            def set(key):
                return f"SET {key}"

        class Converters:
            pass

    @staticmethod
    def _add_extras(command: str, extras: list = None) -> str:
        if extras is None:
            return command
        if isinstance(extras, list):
            return f"{command} {' '.join(str(e) for e in extras)}"
        return f"{command} '{extras}'"

    @classmethod
    def _generate_key(cls, id: int, key_name: str) -> str:
        return f"{cls.__name__.lower()}:{id}:{key_name}"

    @classmethod
    def _exec(cls, command: str, value=None):
        if value is None:
            return connection.execute_command(command)
        return connection.execute_command(command, value)

    @classmethod
    def _resolve_foreign_keys(cls, key_name: str, ids):
        key_name = cls._foreign_keys[key_name]

        def _resolve(k):
            command = f"{cls.Read.Commands.get(key_name)}:{k}:name"
            try:
                result = connection.execute_command(command)
                if result is None:
                    raise ForeignKeyException(
                        f"Could not resolve foreign key."
                        f"key_name={key_name} k={k} cls={cls}"
                    )
            except:
                log.exception(f"Something went wrong while attempting to resolve foreign keys.")
                raise

        if not isinstance(ids, Iterable) or isinstance(ids, str):
            ids = [ids]
        for i in ids:
            _resolve(i)

    @classmethod
    def get(cls, id: int, key_name: str):
        key = cls._generate_key(id, key_name)
        try:
            read_func = getattr(cls.Read.Commands, key_name)
        except AttributeError:
            read_func = cls.Read.Commands.get

        command = read_func(key)
        result = cls._exec(command)

        convert = getattr(cls.Read.Converters, key_name, cls.Read.Converters._all)
        result = convert(result)
        return result

    @classmethod
    def put(cls, id: int, key_name: str, value):
        key = cls._generate_key(id, key_name)

        converter = getattr(cls.Write.Converters, key_name, None)
        if converter is not None:
            value = converter(value)

        try:
            write_func = getattr(cls.Write.Commands, key_name)
        except AttributeError:
            write_func = cls.Write.Commands.set

        command = write_func(key)

        if key_name in cls._foreign_keys:
            cls._resolve_foreign_keys(key_name, value)

        result = cls._exec(command, value)
        return result

    @classmethod
    def get_model(cls, id: int, post: list):
        for f in fields(cls):
            if not f.init and f.name not in cls._excluded:
                post.append(
                    (f.name, cls.get(id, f.name),)
                )

            if f.name in cls._excluded or not f.init:
                continue
            yield f.name, cls.get(id, f.name)

    def put_model(self):
        for f in fields(self):
            if f.name in self._excluded:
                continue

            try:
                value = getattr(self, f.name)
                if value:
                    self.put(self.id, f.name, value)
            except AttributeError:
                continue

    @classmethod
    def new(cls, *args, id: int = None, **kwargs):
        if id is not None:
            if len(args) > 0 or len(kwargs) > 0:
                raise InstantiationException(
                    f"Cannot instantiate new model with id specified alongside other parameters."
                )
            return cls.load(id)
        else:
            return cls(*args, id=IDs.generate_id(), **kwargs)

    @classmethod
    def load(cls, id):
        post_init = []
        kwargs = {
            field_name: value for field_name, value in cls.get_model(id, post_init)
        }
        inst = cls(id=id, **kwargs)

        for attr_name, value in post_init:
            setattr(inst, attr_name, value)
        return inst

    def update(self, **kwargs):
        for attr_name in (f.name for f in fields(self) if f.name not in self._excluded):
            if hasattr(self, attr_name):
                try:
                    setattr(self, attr_name, kwargs[attr_name])
                except KeyError:
                    pass
        return self

    def __post_init__(self, *args, **kwargs):
        Validator(self).validate()
        self._commands = []
        self.put_model()  # FIXME Do not put if the model has just been read from DB.


@dataclass
class Sport(Model):
    _excluded = ("id", "slug",)
    _foreign_keys = {
        "events": "event"
    }

    events: list = field(default_factory=list)

    active: bool = False
    slug: str = field(init=False)

    class Read(Model.Read):
        class Commands(Model.Read.Commands):
            @staticmethod
            def events(key):
                return f"LRANGE {key} 0 -1"

        class Converters(Model.Read.Converters):
            @staticmethod
            def active(value):
                return bool(value)

            @staticmethod
            def events(value):
                return value

    class Write(Model.Write):
        class Commands(Model.Write.Commands):
            @staticmethod
            def events(key):
                return f"LPUSH {key}"

        class Converters(Model.Write.Converters):
            @staticmethod
            def active(value):
                return int(value)

            @staticmethod
            def events(value):
                if value is None:
                    return []
                return value

    _validation_schema = {
        "events": {"schema": {"type": "integer"}}
    }

    @property
    def is_active(self) -> str:
        return self.get(self.id, "active")

    def activate(self) -> str:
        return self.put(self.id, "active", True)

    def deactivate(self) -> str:
        return self.put(self.id, "active", False)

    def __post_init__(self, *args, **kwargs):
        self.slug = Names.generate_slug(self.name)
        super().__post_init__(*args, **kwargs)


@dataclass
class Event(Model):
    @unique
    class Types(Enum):
        PREPLAY = 0
        INPLAY = 1

    @unique
    class Statuses(Enum):
        PENDING = 0
        STARTED = 1
        ENDING = 2
        CANCELLED = 3

    type: int
    sport: int
    status: int
    scheduled_start: datetime
    actual_start: datetime = field(init=False)

    selections: list = field(default_factory=list)

    slug: str = field(init=False)
    active: bool = False

    _excluded = ("id", "slug",)
    _foreign_keys = {
        "selections": "selection",
        "sport": "sport"
    }

    _validation_schema = {
        "type": {"allowed": Types},
        "status": {"allowed": Statuses},
        "scheduled_start": {"min": datetime.utcnow()},
        "selections": {"schema": {"type": "integer"}}
    }

    class Read(Model.Read):
        class Commands(Model.Read.Commands):
            @staticmethod
            def selections(key):
                return f"LRANGE {key} 0 -1"

        class Converters(Model.Read.Converters):
            @classmethod
            def actual_start(cls, value):
                if value is None:
                    return None
                return cls.scheduled_start(value)

            @staticmethod
            def scheduled_start(value):
                return datetime.utcfromtimestamp(float(value))

            @staticmethod
            def selections(value):
                return [int(id) for id in value]

    class Write(Model.Write):
        class Commands(Model.Write.Commands):
            @staticmethod
            def selections(key):
                return f"LPUSH {key}"

        class Converters(Model.Write.Converters):
            @classmethod
            def actual_start(cls, value):
                if value is None or value == MISSING:
                    return "None"
                return cls.scheduled_start(value)

            @staticmethod
            def scheduled_start(value):
                return value.timestamp()

            @staticmethod
            def selections(value):
                if value is None:
                    return []
                return value

    def __post_init__(self, *args, **kwargs):
        self.slug = Names.generate_slug(self.name)
        super().__post_init__(*args, **kwargs)


@dataclass
class Selection(Model):
    _foreign_keys = {
        "event": "event"
    }

    @unique
    class Outcomes(Enum):
        UNSETTLED = 0
        VOID = 1
        LOSE = 2
        WIN = 3

    event: int
    price: float
    outcome: int

    active: bool = False

    _validation_schema = {
        "price": {"coerce": "custom_round", "min": 0.00},
        "outcome": {"allowed": Outcomes}
    }
