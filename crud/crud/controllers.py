from .models import Sport


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
        sport.event_ids = event_ids
        sport.put_model()
        return sport

