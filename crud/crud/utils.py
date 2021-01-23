# -*- coding: utf-8 -*-
from uuid import uuid1

from slugify import slugify


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

