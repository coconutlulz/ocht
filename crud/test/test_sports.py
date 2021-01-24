import unittest

from crud.crud.controllers import SportController
from crud.crud.errors import InstantiationException
from crud.crud.models import Sport, Event, Selection
from crud.test.utils import check_ascii, flush_all_dbs, generate_test_db


class TestSportModel(unittest.TestCase):
    def setUp(self):
        generate_test_db()

    def tearDown(self):
        flush_all_dbs()

    def test_cannot_specify_id(self):
        with self.assertRaises(InstantiationException):
            Sport.new(
                id=123123, name="somesport123123", active=True
            )


class TestSportsController(unittest.TestCase):
    def setUp(self):
        pass
        #generate_test_db()

    def tearDown(self):
        pass
        #flush_all_dbs()

    def test_sport_creation(self):
        new_sport = SportController.create_sport("test_sport", active=True)
        self.assertIsInstance(new_sport.slug, str)
        self.assertTrue(check_ascii(new_sport.slug))

    def test_sport_update(self):
        name = "IDon'tReallyLikeSports"
        new_sport = SportController.create_sport(name, active=False)
        sport_id = new_sport.id

        new_name = "ChangedMyMind"
        updated_sport = SportController.update_sport(sport_id=sport_id, active=True, name=new_name)

        self.assertEqual(updated_sport.name, new_name)
        self.assertEqual(updated_sport.active, True)

        sport_from_db = Sport.new(id=sport_id)

        self.assertEqual(sport_from_db.name, new_name)
        self.assertEqual(sport_from_db.active, True)
