from datetime import datetime

from .models import Event, Sport


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
        event = Event.new(id=event_id)
        event.update(**kwargs)
        event.put_model()
        return event

    @staticmethod
    def update_event_selections(event_id: int, selection_ids: list):
        event = Event.new(id=event_id)
        event.selections = selection_ids
        event.put_model()
        return event
