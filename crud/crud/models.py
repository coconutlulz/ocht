# -*- coding: utf-8 -*-
from dataclasses import dataclass, field, fields, MISSING
from datetime import datetime
from enum import Enum, unique

from .database import connection
from .utils import IDs, Names
from .validators import Validator


@dataclass
class Model:
    id: int
    name: str

    _excluded = ("id",)

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
        return f"{command} {extras}"

    @classmethod
    def _generate_key(cls, id: int, key_name: str) -> str:
        return f"{cls.__name__}:{id}:{key_name}"

    @classmethod
    def _exec(cls, command: str):
        try:
            return connection.execute_command(command)
        except Exception as e:
            print("exception: {}".format(e))
        raise Exception("NO RESULT FROM DB")

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
        command = f"{command} {value}"

        result = cls._exec(command)
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

    def _validate(self):
        self._validator.validate()

    def __post_init__(self, *args, **kwargs):
        self._validator = Validator(self)
        self._commands = []
        print("__post_init__ put_model")
        self.put_model()


@dataclass
class Sport(Model):
    _excluded = ("id", "slug",)
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
        "events": {"items": [{"type": "integer"}]}
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

    _validation_schema = {
        "type": {"allowed": Types},
        "status": {"allowed": Statuses},
        "scheduled_start": {"min": datetime.utcnow()},
        "selections": {"items": [{"type": "integer"}]}
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
                return datetime.fromtimestamp(float(value))

            @staticmethod
            def selections(value):
                return value

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
        "price": {"coerce": "custom_round"},
        "outcome": {"allowed": Outcomes}
    }
