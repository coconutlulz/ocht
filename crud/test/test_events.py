import unittest

from crud.crud.controllers import SportController
from crud.crud.errors import InstantiationException
from crud.crud.models import Sport, Event, Selection
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
