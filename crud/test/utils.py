from datetime import datetime
import random

from crud.crud.models import Sport, Event, Selection, connection


def get_random_sport():
    result = connection.execute_command("KEYS", "sport:*")


def create_sports(n=11):
    for i in range(0, n):
        sport = Sport.new(name=f"Sport {i}")
        sport.put_model()
        yield sport


def create_events(sports, n=20):
    types = [t.value for t in list(Event.Types)]
    statuses = [s.value for s in list(Event.Statuses)]

    def _create_event(index, sport_index):
        type = random.choice(types)
        status = random.choice(statuses)
        event = Event.new(
            name=f"Event {index}",
            scheduled_start=datetime.utcnow(),
            sport=sports[sport_index].id,
            type=type,
            status=status
        )
        return event

    sport_i = 0
    for i in range(0, n, 2):
        yield _create_event(i, sport_i)
        yield _create_event(i + 1, sport_i)
        sport_i += 1


def create_selections(events, n=10):
    outcomes = [o.value for o in list(Selection.Outcomes)]

    def _create_selection(index, event_index):
        outcome = random.choice(outcomes)
        selection = Selection.new(
            name=f"Selection {index}",
            event=events[index].id,
            price=float(index),
            outcome=outcome
        )
        return selection

    event_i = 0
    for i in range(0, n, 2):
        yield _create_selection(i, event_i)
        yield _create_selection(i + 1, event_i)
        event_i += 1


def flush_all_dbs():
    connection.execute_command("FLUSHALL")


def generate_test_db():
    flush_all_dbs()
    sports = [s for s in create_sports()]
    events = [e for e in create_events(sports)]
    selections = [s for s in create_selections(events)]


def check_ascii(string):
    return all(ord(char) < 128 for char in string)


if __name__ == "__main__":
    generate_test_db()
