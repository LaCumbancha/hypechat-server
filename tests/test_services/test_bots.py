import unittest
from unittest.mock import MagicMock

from sqlalchemy.exc import SQLAlchemyError

'''Mocking environment properties'''
import sys
sys.modules["daos.database"] = MagicMock()
sys.modules["daos.users"] = MagicMock()
sys.modules["daos.teams"] = MagicMock()
sys.modules["daos.bots"] = MagicMock()
sys.modules["models.authentication"] = MagicMock()
sys.modules["logging"].getLogger = MagicMock()
sys.modules["requests"] = MagicMock()
sys.modules["os"].getenv = MagicMock(side_effect=lambda key: environment_properties.get(key))

environment_properties = {
    'TITO_ID': "0"
}

from services.bots import BotService

mock = MagicMock()


class MockedBotDatabase:

    batch_team_bots = None
    stored_team_bots = []


class BotTestCase(unittest.TestCase):

    def tearDown(self):
        MockedBotDatabase.batch_team_bots = None
        MockedBotDatabase.stored_team_bots = []

    def test_register_tito_with_unknown_sqlalchemy_error_throws_exception(self):
        team_id = 0

        def add_team_bot(team_bot):
            from tests.test_services import test_bots
            MockedBotDatabase.batch_team_bots = team_bot

        def commit():
            raise SQLAlchemyError(mock, mock)

        def rollback():
            from tests.test_services import test_bots
            MockedBotDatabase.batch_team_bots = None

        sys.modules["daos.teams"].TeamDatabaseClient.add_team_user = MagicMock(side_effect=add_team_bot)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["daos.database"].DatabaseClient.rollback = MagicMock(side_effect=rollback)

        self.assertRaises(SQLAlchemyError, BotService.register_tito, team_id)

    def test_register_tito_without_unknown_sqlalchemy_error_does_add_bot_to_team(self):
        team_id = 0

        def add_team_bot(team_bot):
            from tests.test_services import test_bots
            MockedBotDatabase.batch_team_bots = team_bot

        def commit():
            from tests.test_services import test_bots
            MockedBotDatabase.stored_team_bots += [MockedBotDatabase.batch_team_bots]
            MockedBotDatabase.batch_team_bots = None

        sys.modules["daos.teams"].TeamDatabaseClient.add_team_user = MagicMock(side_effect=add_team_bot)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        BotService.register_tito(team_id)
        self.assertIsNone(MockedBotDatabase.batch_team_bots)
        self.assertEqual(1, len(MockedBotDatabase.stored_team_bots))
