# -*- coding: utf-8 -*-
from dataclasses import dataclass, field, fields, MISSING
from datetime import datetime
from enum import Enum, unique

from typing import Union

from .database import db
from .utils import IDs, Names
from .validators import Validator


@dataclass
class Model:
    id: int
    name: str

    _validation_schema = {}

    key_format = "{model}:{id}:{attribute}"

    class DBCommands:
        class Read:
            get = "GET {key}"

        class Write:
            put = "SET {key}"

    @staticmethod
    def _add_extras(command: str, extras: list = None) -> str:
        if extras is None:
            return command
        if isinstance(extras, list):
            return f"{command} {' '.join(str(e) for e in extras)}"
        return f"{command} {extras}"

    @classmethod
    def _generate_key(cls, _id: int, key_name: str) -> str:
        return f"{cls.__name__}:{_id}:{key_name}"

    @classmethod
    @db
    def multi_get(cls, _id: int, key_names: list[str] = None):
        command = "MGET {keys}"
        keys = []

        if key_names is None:
            key_names = [f.name for f in fields(cls)]

        for key_name in key_names:
            try:
                getattr(cls.DBCommands.Read, key_name)
                raise Exception("Can only use multi-get for GETs")
            except:
                keys.append(cls._generate_key(_id, key_name))

        command = command.format(keys=' '.join(str(k) for k in keys))
        return command

    @classmethod
    @db
    def get(cls, id: int, key_name: str, extras: Union[list, tuple] = None) -> str:
        key = cls._generate_key(id, key_name)
        try:
            command = getattr(cls.DBCommands.Read, key_name)
        except AttributeError:
            command = cls.DBCommands.Read.get

        command = command.format(key=key)
        return cls._add_extras(command, extras)

    @classmethod
    @db
    def put(cls, id: int, key_name: str, extras: Union[list, tuple] = None) -> str:
        key = cls._generate_key(id, key_name)
        try:
            command = getattr(cls.DBCommands.Write, key_name)
        except AttributeError:
            command = cls.DBCommands.Write.put

        command = command.format(key=key)
        return cls._add_extras(command, extras)

    @db
    def put_model(self):
        for f in fields(self):
            if f.name != "id":
                extras = getattr(self, f.name)
                if not extras:
                    continue
                self._commands.append(self.put(self.id, f.name, extras=extras))

    @classmethod
    def new(cls, *args, id: int = None, **kwargs):
        if id is not None:
            mget_result = cls.multi_get(id)
            print("lol")
        else:
            cls(*args, id=IDs.generate_id(), **kwargs)

    def _validate(self):
        self._validator.validate()

    def __post_init__(self, *args, **kwargs):
        self._validator = Validator(self)
        self._commands = []
        self.put_model()


@dataclass
class Sport(Model):
    events: list = field(default_factory=list)

    active: bool = False
    slug: str = field(init=False)

    class DBCommands(Model.DBCommands):
        class Read(Model.DBCommands.Read):
            pass

        class Write(Model.DBCommands.Write):
            events = "LPUSH {key}"

    _validation_schema = {
        "events": {"items": [{"type": "integer"}]}
    }

    @property
    def is_active(self) -> str:
        return self.get(self.id, "active")

    def activate(self) -> str:
        return self.put(self.id, "active", (1,))

    def deactivate(self) -> str:
        return self.put(self.id, "active", (0,))

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

    selections: list = field(default_factory=list)

    slug: str = field(init=False)
    actual_start: datetime = field(init=False)
    active: bool = False

    _validation_schema = {
        "type": {"allowed": Types},
        "status": {"allowed": Statuses},
        "scheduled_start": {"min": datetime.utcnow()},
        "selections": {"items": [{"type": "integer"}]}
    }

    def __post_init__(self, *args, **kwargs):
        self.actual_start = MISSING
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
