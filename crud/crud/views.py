import operator
import re

from .errors import FilterException
from .models import Sport, Event, Selection, connection

scan_count = 50


def get_by_glob(model_type, pattern: str):
    all_keys = connection.execute_command(
        "KEYS", f"{model_type}:*:name"
    )
    decoded = " ".join([k.decode("utf-8") for k in all_keys])
    ids = [str(k).split(":")[1] for k in all_keys]
    names = [
        name.decode("utf-8") for name in
        connection.execute_command(f"MGET {decoded}")
    ]

    for id, name in zip(ids, names):
        r = re.compile(pattern)
        regex_result = r.match(name)
        if regex_result:
            yield int(id)


class Filter:
    comparisons = {
        "<<": operator.lt,
        "<=": operator.le,
        ">>": operator.gt,
        ">=": operator.ge,
        "==": operator.eq
    }

    def __init__(self, model_type, filter_string):
        self._model_type = model_type
        self._filter_string = filter_string
        self._filters = []
        self._results = self._regex(".*")

    def _regex(self, pattern):
        for model_id in get_by_glob(self._model_type, pattern):
            if self._model_type == "sport":
                yield SportView.get_sport(model_id)
            elif self._model_type == "event":
                yield EventView.get_event(model_id)
            elif self._model_type == "selection":
                yield SelectionView.get_selection(model_id)

    def regex(self, pattern):
        r = re.compile(pattern)
        self._results = [
            model for model in self._results
            if r.match(model.name) is not None
        ]

    def _model_attribute(self, param, attribute: str):
        op = param[:2]
        operand = float(param[2:])

        operator_func = self.comparisons[op]

        self._results = [
            model for model in self._results if
            operator_func(len(getattr(model, attribute)), operand)
        ]

    def events(self, param):
        self._model_attribute(param, "events")

    def selections(self, param):
        self._model_attribute(param, "selections")

    def filter(self):
        filter_strings = self._filter_string.split(" AND ")

        for filter_string in filter_strings:
            self._filters.append(filter_string.split(":"))

        self._results = list(self._regex(".*"))

        for filter_operation, filter_operand in self._filters:
            try:
                filter_func = getattr(self, filter_operation)
            except AttributeError:
                raise FilterException(
                    f"Specified filter not found: {filter_operation}"
                )
            filter_func(filter_operand)

        return self._results


class SportView:
    @staticmethod
    def get_sport(sport_id: int):
        return Sport.new(id=sport_id)

    @staticmethod
    def get_sport_filtered(filter_string: str):
        filter = Filter("sport", filter_string)
        results = filter.filter()
        return results


class EventView:
    @staticmethod
    def get_event(event_id: int):
        return Event.new(id=event_id)

    @staticmethod
    def get_events_filtered(filter_string: str):
        filter = Filter("event", filter_string)
        results = filter.filter()
        return results


class SelectionView:
    @staticmethod
    def get_selection(selection_id: int):
        return Selection.new(id=selection_id)

    @staticmethod
    def get_selections_filtered(filter_string: str):
        filter = Filter("selection", filter_string)
        results = filter.filter()
        return results


view_mapping = {
    "sport": SportView,
    "event": EventView,
    "selection": SelectionView
}
