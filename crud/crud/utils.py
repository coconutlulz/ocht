# -*- coding: utf-8 -*-
from datetime import datetime
from logging import getLogger, DEBUG
from uuid import uuid1

from slugify import slugify


# The time used throughout any operation should be the time at which the operation began.
current_time = None

log = getLogger("CRUD")
log.setLevel(DEBUG)


def get_current_time():
    global current_time
    if current_time is None:
        set_current_time()
    return current_time


def set_current_time():
    global current_time
    current_time = datetime.utcnow()


class IDs:
    @staticmethod
    def generate_id():
        uuid = uuid1()
        if not uuid.is_safe:
            print("unsafe uuid generated")
        return uuid1().int >> 64


class Names:
    @staticmethod
    def generate_slug(name: str) -> str:
        return slugify(name)

