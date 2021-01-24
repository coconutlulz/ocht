from .models import Sport, Event, Selection
from .utils import get_current_time


class SportView:
    def get_sport(self, sport_id: int):
        return Sport.new(id=sport_id)


class EventView:
    def get_event(self, event_id: int):
        return Event.new(id=event_id)


class SelectionView:
    def get_event(self, selection_id: int):
        return Selection.new(id=selection_id)
