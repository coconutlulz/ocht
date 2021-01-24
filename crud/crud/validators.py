# -*- coding: utf-8 -*-
from dataclasses import dataclass, fields
from enum import EnumMeta

from cerberus import schema_registry
from cerberus import Validator as CValidator

from .errors import CoercionException, ValidationException


type_table = {
    bool: "boolean",
    int: "integer",
    str: "string"
}
reverse_type_table = {v: k for k, v in type_table.items()}


class Validator(CValidator):
    rounding_places = 2

    def _normalize_coerce_custom_round(self, value):
        return round(float(value), self.rounding_places)

    @staticmethod
    def _translate_type(t: type):
        try:
            return type_table[t]
        except KeyError:
            return t.__name__

    @staticmethod
    def _translate_field_rules(rules: dict):
        coerce_to_int = False
        for k, rule_constraints in rules.items():
            if isinstance(rule_constraints, EnumMeta):
                coerce_to_int = True
                rules[k] = [
                    v.value for v in rule_constraints.__members__.values()
                ]
        if coerce_to_int:
            rules["coerce"] = int

    @staticmethod
    def _add_coercion(rules: dict, field):
        try:
            rules["coerce"] = field.type
        except KeyError:
            raise CoercionException(f"Couldn't find type {field.type}")

    def _translate_schema(self, model: type):
        if len(model.__mro__) == 1:
            return

        for field in fields(model):
            rules = model._validation_schema.get(field.name, {})
            field_schema = {
                "type": self._translate_type(field.type),
            }

            if len(rules) > 0 or field.type == list:
                self._translate_field_rules(rules)
            else:
                self._add_coercion(rules, field)

            field_schema.update(**rules)

            self._base_schema[field.name] = field_schema

        self._translate_schema(model.__mro__[1])

    def __init__(self, model: dataclass = None, *args, **kwargs):
        if model is not None:
            self._base_schema = {}
            self._model = model
            if schema_registry.get(type(model)) is None:
                self._translate_schema(type(model))
        super().__init__(*args, **kwargs)

    def validate(self):
        if not super().validate(
            self._model.__dict__,
            schema=self._base_schema
        ):
            raise ValidationException(
                f"Failed to validate fields in model creation. "
                f"{self.errors} "
                f"{self._errors}"
            )