# -*- coding: utf-8 -*-
from dataclasses import dataclass, field, MISSING
from datetime import datetime
from enum import Enum, unique

from typing import Any, Union

from .utils import IDs, Names
from .validators import Validator


@dataclass
class Model:
    key_format = "{model}:{id}:{attribute}"

    class DBCommands:
        class Read:
            get = "GET {key}"

        class Write:
            put = "SET {key}"


    _validation_schema = {}

    id: int = field(init=False, default_factory=IDs.generate_id)
    name: str

    @staticmethod
    def _add_extras(command: str, extras: list) -> str:
        if extras is None:
            return command
        return f"{command} {' '.join(str(e) for e in extras)}"

    @classmethod
    def _generate_key(cls, id: int, key_name: str):
        return f"{cls.__name__}:{id}:{key_name}"

    @classmethod
    def get(cls, id: int, key_name: str, extras: Union[list, tuple] = None) -> str:
        key = cls._generate_key(id, key_name)
        try:
            command = getattr(cls.DBCommands.Read, key_name)
        except AttributeError:
            command = cls.DBCommands.Read.get

        command = command.format(key=key)

        return cls._add_extras(command, extras)

    @classmethod
    def put(cls, id: int, key_name: str, extras: Union[list, tuple] = None) -> str:
        key = cls._generate_key(id, key_name)
        try:
            command = getattr(cls.DBCommands.Write, key_name)
        except AttributeError:
            command = cls.DBCommands.Write.put

        command = command.format(key=key)
        return cls._add_extras(command, extras)

    @classmethod
    def new(cls, *args, **kwargs):
        try:
            return cls(*args, **kwargs)
        except TypeError as e:
            pass

    def _validate(self):
        self._validator.validate()

    def __post_init__(self, *args, **kwargs):
        self._validator = Validator(self)


@dataclass
class Sport(Model):
    class DBCommands(Model.DBCommands):
        class Read(Model.DBCommands.Read):
            active = "GETBIT {key}"

        class Write(Model.DBCommands.Write):
            active = "SETBIT {key}"

    events: list = field(default_factory=[])

    active: bool = False
    slug: str = field(init=False)

    _validation_schema = {
        "events": {"items": [{"type": "integer"}]}
    }

    @property
    def is_active(self):
        return self.get(self.id, "active")

    def activate(self):
        self.put(self.id, "active", (1,))

    def deactivate(self):
        self.put(self.id, "active", (0,))

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

    selections: list = field(default_factory=[])

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
