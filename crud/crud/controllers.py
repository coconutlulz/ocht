from datetime import datetime

from .models import Event, Selection, Sport

from .views import EventView, SelectionView, SportView


class SportController:
    @staticmethod
    def create_sport(name: str, active: bool = False):
        new_sport = Sport.new(name=name, active=active)
        return new_sport

    @staticmethod
    def update_sport(sport_id: int, **kwargs):
        sport = Sport.new(id=sport_id)
        sport.update(**kwargs)
        sport.put_model()
        return sport

    @staticmethod
    def update_sport_events(sport_id: int, event_ids: list):
        sport = Sport.new(id=sport_id)
        sport.events = event_ids
        sport.put_model()
        return sport

    @staticmethod
    def deactivate_sport(sport_id: int):
        sport = SportView.get_sport(sport_id)
        sport.deactivate()
        return sport


class EventController:
    @staticmethod
    def create_event(name: str, type: int, sport: int, status: int, scheduled_start: float):
        new_event = Event.new(
            name=name, type=type, sport=sport, status=status,
            scheduled_start=datetime.fromtimestamp(scheduled_start)
        )
        return new_event

    @staticmethod
    def update_event(event_id: int, **kwargs):
        event = EventView.get_event(event_id)
        event.update(**kwargs)
        event.put_model()
        return event

    @staticmethod
    def update_event_selections(event_id: int, selection_ids: list):
        event = EventView.get_event(event_id)
        event.selections = selection_ids
        event.put_model()
        return event

    @staticmethod
    def deactivate_event(event_id: int):
        event = EventView.get_event(event_id)

        for selection_id in event.selections:
            selection = SelectionView.get_selection(selection_id)
            selection.deactivate()
        event.deactivate()

        # Deactivate sport if all of its events are inactive.
        sport_id = event.sport
        sport = SportView.get_sport(sport_id)

        for event_id in sport.events:
            sub_event = EventView.get_event(event_id)
            if sub_event.active:
                return event
        sport.deactivate()
        return event


class SelectionController:
    @staticmethod
    def create_selection(name: str, event: int, price: float, outcome: int):
        new_selection = Selection.new(
            name=name, event=event, price=price, outcome=outcome
        )
        return new_selection

    @staticmethod
    def update_selection(selection_id: int, **kwargs):
        selection = SelectionView.get_selection(selection_id)
        selection.update(**kwargs)
        selection.put_model()
        return selection

    @staticmethod
    def deactivate_selection(selection_id: int):
        selection = Selection.new(id=selection_id)
        selection.deactivate()

        # Deactivate event if all selections are inactive.
        event = EventView.get_event(selection.event)

        for selection_id in event.selections:
            sub_selection = SelectionView.get_selection(selection_id)
            if sub_selection.active:
                return event
        event.deactivate()
        return selection


controller_mapping = {
    "sport": SportController,
    "event": EventController,
    "selection": SelectionController
}
