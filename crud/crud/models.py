# -*- coding: utf-8 -*-
from dataclasses import dataclass, field, MISSING
from datetime import datetime
from enum import Enum, unique

from .utils import IDs, Names
from .validators import Validator


@dataclass
class Model:
    _validation_schema = {}

    id: int = field(init=False, default_factory=IDs.generate_id)
    name: str

    def _validate(self):
        self._validator.validate()

    def __post_init__(self, *args, **kwargs):
        self._validator = Validator(self)


@dataclass
class Sport(Model):
    name: str
    active: bool = False
    slug: str = field(init=False)

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

    slug: str = field(init=False)
    actual_start: datetime = field(init=False)
    active: bool = False

    _validation_schema = {
        "type": {"allowed": Types},
        "status": {"allowed": Statuses},
        "scheduled_start": {"min": datetime.utcnow()}
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
