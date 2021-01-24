from datetime import datetime, timedelta
import unittest

from crud.crud.controllers import EventController, SportController
from crud.crud.errors import ForeignKeyException, InstantiationException
from crud.crud.models import Sport, Event, Selection
from crud.crud.utils import get_current_time
from crud.test.utils import check_ascii, flush_all_dbs, generate_test_db


class TestEventModel(unittest.TestCase):
    def setUp(self):
        generate_test_db()

    def tearDown(self):
        flush_all_dbs()

    def test_cannot_specify_id(self):
        with self.assertRaises(InstantiationException):
            Event.new(
                id=123123, name="someevent12313"
            )


class TestEventController(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        flush_all_dbs()

    def test_event_creation(self):
        def _create_event(sport_id: int):
            return EventController.create_event(
                name="test_event",
                type=Event.Types.PREPLAY.value,
                sport=sport_id,
                status=Event.Statuses.PENDING.value,
                scheduled_start=datetime.timestamp(
                    get_current_time() + timedelta(hours=5)
                )
            )

        # Referenced Sport does not yet exist.
        with self.assertRaises(ForeignKeyException):
            _create_event(123123)

        new_sport = SportController.create_sport("some sport", active=True)
        new_event = _create_event(new_sport.id)

        event_from_db = Event.new(id=new_event.id)

        self.assertEqual(new_event.sport, new_sport.id)
        self.assertEqual(event_from_db.sport, new_sport.id)

    def test_event_update(self):
        new_sport = SportController.create_sport("some sport", active=True)

        new_event = EventController.create_event(
            name="a test event",
            type=Event.Types.PREPLAY.value,
            sport=new_sport.id,
            status=Event.Statuses.PENDING.value,
            scheduled_start=datetime.timestamp(
                get_current_time() + timedelta(hours=5)
            )
        )

        self.assertEqual(new_event.status, Event.Statuses.PENDING.value)

        updated_event = EventController.update_event(
            event_id=new_event.id, status=Event.Statuses.STARTED.value
        )

        event_from_db = Event.new(id=new_event.id)

        self.assertEqual(updated_event.status, event_from_db.status)
        self.assertEqual(event_from_db.status, Event.Statuses.STARTED.value)
