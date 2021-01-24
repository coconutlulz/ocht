import re

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


class SportView:
    @staticmethod
    def get_sport(sport_id: int):
        return Sport.new(id=sport_id)

    @staticmethod
    def get_sports_by_regex(pattern: str):
        for sport_id in get_by_glob("sport", pattern):
            yield SportView.get_sport(sport_id)


class EventView:
    @staticmethod
    def get_event(event_id: int):
        return Event.new(id=event_id)

    @staticmethod
    def get_events_by_regex(pattern: str):
        for event_id in get_by_glob("event", pattern):
            yield EventView.get_event(event_id)


class SelectionView:
    @staticmethod
    def get_selection(selection_id: int):
        return Selection.new(id=selection_id)

    @staticmethod
    def get_selections_by_regex(pattern: str):
        for selection_id in get_by_glob("selection", pattern):
            yield SelectionView.get_selection(selection_id)
