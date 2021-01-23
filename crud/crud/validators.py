from copy import deepcopy
from dataclasses import dataclass, fields
from enum import EnumMeta

from cerberus import schema_registry
from cerberus import Validator as CValidator


type_table = {
    bool: "boolean",
    int: "integer",
    str: "string"
}


class Validator(CValidator):
    base_schema = {}
    rounding_places = 2

    def _normalize_coerce_custom_round(self, value):
        return round(value, self.rounding_places)

    @staticmethod
    def _translate_type(t: type):
        try:
            return type_table[t]
        except KeyError:
            return t.__name__

    @staticmethod
    def _translate_field_rules(rules: dict):
        for k, rule_constraints in rules.items():
            if isinstance(rule_constraints, EnumMeta):
                rules[k] = [
                    v.value for v in rule_constraints.__members__.values()
                ]

    def _translate_schema(self, model: type):
        if len(model.__mro__) == 1:
            return

        # FIXME: See if this is necessary
        temp_schema = deepcopy(model._validation_schema)

        for field in fields(model):
            rules = temp_schema.get(field.name, {})
            if len(rules) > 0:
                self._translate_field_rules(rules)

            self.base_schema[field.name] = {
                "type": self._translate_type(field.type),
                **rules
            }

        self._translate_schema(model.__mro__[1])

    def __init__(self, model: dataclass):
        self._model = model
        if schema_registry.get(type(model)) is None:
            self._translate_schema(type(model))
        super().__init__(self.base_schema)
        self.validate()

    def validate(self):
        super().validate(self._model.__dict__)
