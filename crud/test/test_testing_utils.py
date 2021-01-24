import unittest

from crud.crud.models import connection
from crud.test.utils import (
    flush_all_dbs,
    generate_test_db,
    create_events,
    create_sports,
    create_selections
)


class TestTestingUtils(unittest.TestCase):
    def setUp(self):
        generate_test_db()

    def tearDown(self):
        flush_all_dbs()

    def test_create_sports(self):
        n = 10
        result = list(create_sports(n))
        self.assertEqual(len(result), 10)

    def test_create_events(self):
        n = 20
        sports = list(create_sports())
        result = list(create_events(sports, n))
        self.assertEqual(len(result), n)

    def test_create_selections(self):
        n = 10
        sports = list(create_sports())
        events = list(create_events(sports))
        result = list(create_selections(events, n))
        self.assertEqual(len(result), n)
