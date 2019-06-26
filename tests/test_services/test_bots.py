import unittest
from unittest.mock import MagicMock

from dtos.models.bots import Bot
from dtos.models.users import RegularClient, User
from dtos.models.teams import Team
from dtos.models.messages import Message
from dtos.responses.bots import SuccessfulBotListResponse
from dtos.responses.clients import BadRequestUserMessageResponse, UnsuccessfulClientResponse, SuccessfulUserMessageResponse
from models.constants import UserResponseStatus, TeamRoles, SendMessageType, MessageType
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

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
    batch_clients = None
    stored_clients = []
    batch_bots = None
    stored_bots = []

    posted_json = None


class BotTestCase(unittest.TestCase):

    def tearDown(self):
        MockedBotDatabase.batch_team_bots = None
        MockedBotDatabase.stored_team_bots = []
        MockedBotDatabase.batch_clients = None
        MockedBotDatabase.stored_clients = []
        MockedBotDatabase.batch_bots = None
        MockedBotDatabase.stored_bots = []
        MockedBotDatabase.posted_json = None

    def test_register_tito_it_team_with_unknown_sqlalchemy_error_throws_exception(self):
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

        self.assertRaises(SQLAlchemyError, BotService.register_tito_in_team, team_id)

    def test_register_tito_in_team_without_unknown_sqlalchemy_error_does_add_bot_to_team(self):
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

        BotService.register_tito_in_team(team_id)
        self.assertIsNone(MockedBotDatabase.batch_team_bots)
        self.assertEqual(1, len(MockedBotDatabase.stored_team_bots))

    def test_user_added_to_team_without_welcome_message_does_not_receives_titos_welcome(self):
        user_id = 1
        team_id = 0

        '''Mocked outputs'''
        tito = Bot(bot_id=0, name="tito", callback=None, token=None)
        team = Team(team_id=team_id, name="Test-Team")

        def post(url, json, headers):
            from tests.test_services import test_bots
            MockedBotDatabase.posted_json = json

        sys.modules["daos.bots"].BotDatabaseClient.get_bot_by_id.return_value = tito
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_id.return_value = team
        sys.modules["requests"].post = MagicMock(side_effect=post)

        BotService.tito_welcome(user_id, team_id)
        self.assertIsNone(MockedBotDatabase.posted_json)

    def test_user_added_to_team_with_welcome_message_does_not_receives_titos_welcome(self):
        user_id = 1
        team_id = 0

        '''Mocked outputs'''
        tito = Bot(bot_id=0, name="tito", callback=None, token=None)
        team = Team(team_id=team_id, name="Test-Team", welcome_message="Helloooooou!")

        def post(url, json, headers):
            from tests.test_services import test_bots
            MockedBotDatabase.posted_json = json

        sys.modules["daos.bots"].BotDatabaseClient.get_bot_by_id.return_value = tito
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_id.return_value = team
        sys.modules["requests"].post = MagicMock(side_effect=post)

        BotService.tito_welcome(user_id, team_id)
        self.assertIsNotNone(MockedBotDatabase.posted_json)
        self.assertEqual(0, MockedBotDatabase.posted_json.get("team_id"))
        self.assertEqual(1, MockedBotDatabase.posted_json.get("user_id"))
        self.assertEqual("welcome-user", MockedBotDatabase.posted_json.get("params"))
        self.assertEqual("Helloooooou!", MockedBotDatabase.posted_json.get("message"))

    def test_create_bot_with_name_in_use_returns_bad_request(self):
        data = MagicMock()

        '''Mocked outputs'''
        mod = User(user_id=0)
        mod.team_id = 0

        def add_client():
            from tests.test_services import test_bots
            client = RegularClient(client_id=0)
            MockedBotDatabase.batch_clients = client
            return client

        def add_bot(bot):
            from tests.test_services import test_bots
            MockedBotDatabase.batch_bots = bot

        def add_team_bot(team_bot):
            from tests.test_services import test_bots
            MockedBotDatabase.batch_team_bots = team_bot

        def commit():
            raise IntegrityError(mock, mock, mock)

        def rollback():
            from tests.test_services import test_bots
            MockedBotDatabase.batch_clients = None
            MockedBotDatabase.batch_bots = None
            MockedBotDatabase.batch_team_bots = None

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = mod
        sys.modules["daos.users"].UserDatabaseClient.add_client = MagicMock(side_effect=add_client)
        sys.modules["daos.bots"].BotDatabaseClient.add_bot = MagicMock(side_effect=add_bot)
        sys.modules["daos.teams"].TeamDatabaseClient.add_team_user = MagicMock(side_effect=add_team_bot)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["daos.database"].DatabaseClient.rollback = MagicMock(side_effect=rollback)
        sys.modules["daos.bots"].BotDatabaseClient.get_bot_by_name.return_value = MagicMock()

        response = BotService.create_bot(data)
        self.assertIsNone(MockedBotDatabase.batch_bots)
        self.assertIsNone(MockedBotDatabase.batch_clients)
        self.assertIsNone(MockedBotDatabase.batch_team_bots)
        self.assertEqual(0, len(MockedBotDatabase.stored_bots))
        self.assertEqual(0, len(MockedBotDatabase.stored_clients))
        self.assertEqual(0, len(MockedBotDatabase.stored_team_bots))
        self.assertEqual(UserResponseStatus.ALREADY_REGISTERED.value, response.status)
        self.assertIsInstance(response, BadRequestUserMessageResponse)

    def test_create_bot_with_unknown_integrity_error_returns_unsuccessful(self):
        data = MagicMock()

        '''Mocked outputs'''
        mod = User(user_id=0)
        mod.team_id = 0

        def add_client():
            from tests.test_services import test_bots
            client = RegularClient(client_id=0)
            MockedBotDatabase.batch_clients = client
            return client

        def add_bot(bot):
            from tests.test_services import test_bots
            MockedBotDatabase.batch_bots = bot

        def add_team_bot(team_bot):
            from tests.test_services import test_bots
            MockedBotDatabase.batch_team_bots = team_bot

        def commit():
            raise IntegrityError(mock, mock, mock)

        def rollback():
            from tests.test_services import test_bots
            MockedBotDatabase.batch_clients = None
            MockedBotDatabase.batch_bots = None
            MockedBotDatabase.batch_team_bots = None

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = mod
        sys.modules["daos.users"].UserDatabaseClient.add_client = MagicMock(side_effect=add_client)
        sys.modules["daos.bots"].BotDatabaseClient.add_bot = MagicMock(side_effect=add_bot)
        sys.modules["daos.teams"].TeamDatabaseClient.add_team_user = MagicMock(side_effect=add_team_bot)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["daos.database"].DatabaseClient.rollback = MagicMock(side_effect=rollback)
        sys.modules["daos.bots"].BotDatabaseClient.get_bot_by_name.return_value = None

        response = BotService.create_bot(data)
        self.assertIsNone(MockedBotDatabase.batch_bots)
        self.assertIsNone(MockedBotDatabase.batch_clients)
        self.assertIsNone(MockedBotDatabase.batch_team_bots)
        self.assertEqual(0, len(MockedBotDatabase.stored_bots))
        self.assertEqual(0, len(MockedBotDatabase.stored_clients))
        self.assertEqual(0, len(MockedBotDatabase.stored_team_bots))
        self.assertIsInstance(response, UnsuccessfulClientResponse)

    def test_create_bot_with_correct_data_works_properly(self):
        data = MagicMock()

        '''Mocked outputs'''
        mod = User(user_id=0)
        mod.team_id = 0

        def add_client():
            from tests.test_services import test_bots
            client = RegularClient(client_id=0)
            MockedBotDatabase.batch_clients = client
            return client

        def add_bot(bot):
            from tests.test_services import test_bots
            MockedBotDatabase.batch_bots = bot

        def add_team_bot(team_bot):
            from tests.test_services import test_bots
            MockedBotDatabase.batch_team_bots = team_bot

        def commit():
            from tests.test_services import test_bots
            MockedBotDatabase.stored_clients += [MockedBotDatabase.batch_clients]
            MockedBotDatabase.stored_bots += [MockedBotDatabase.batch_bots]
            MockedBotDatabase.stored_team_bots += [MockedBotDatabase.batch_team_bots]
            MockedBotDatabase.batch_clients = None
            MockedBotDatabase.batch_bots = None
            MockedBotDatabase.batch_team_bots = None

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = mod
        sys.modules["daos.users"].UserDatabaseClient.add_client = MagicMock(side_effect=add_client)
        sys.modules["daos.bots"].BotDatabaseClient.add_bot = MagicMock(side_effect=add_bot)
        sys.modules["daos.teams"].TeamDatabaseClient.add_team_user = MagicMock(side_effect=add_team_bot)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        response = BotService.create_bot(data)
        self.assertIsNone(MockedBotDatabase.batch_bots)
        self.assertIsNone(MockedBotDatabase.batch_clients)
        self.assertIsNone(MockedBotDatabase.batch_team_bots)
        self.assertEqual(1, len(MockedBotDatabase.stored_bots))
        self.assertEqual(0, MockedBotDatabase.stored_bots[0].id)
        self.assertEqual(1, len(MockedBotDatabase.stored_clients))
        self.assertEqual(0, MockedBotDatabase.stored_clients[0].id)
        self.assertEqual(1, len(MockedBotDatabase.stored_team_bots))
        self.assertEqual(0, MockedBotDatabase.stored_team_bots[0].user_id)
        self.assertEqual(0, MockedBotDatabase.stored_team_bots[0].team_id)
        self.assertEqual(TeamRoles.BOT.value, MockedBotDatabase.stored_team_bots[0].role)
        self.assertEqual(UserResponseStatus.OK.value, response.status)
        self.assertIsInstance(response, SuccessfulUserMessageResponse)

    def test_team_bots_return_team_bots_list_without_token(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        bot1 = Bot(bot_id=1, name="Bot-Test1", callback=None, token="Test-Token")
        bot2 = Bot(bot_id=2, name="Bot-Test2", callback=None, token="Test-Token")
        bots = [bot1, bot2]

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.bots"].BotDatabaseClient.get_team_bots.return_value = bots

        response = BotService.team_bots(data)
        self.assertEqual(UserResponseStatus.LIST.value, response.json().get("status"))
        self.assertEqual(1, response.json().get("bots")[0].get("id"))
        self.assertEqual(2, response.json().get("bots")[1].get("id"))
        self.assertEqual("Bot-Test1", response.json().get("bots")[0].get("name"))
        self.assertEqual("Bot-Test2", response.json().get("bots")[1].get("name"))
        self.assertIsNone(response.json().get("bots")[0].get("callback"))
        self.assertIsNone(response.json().get("bots")[1].get("callback"))
        self.assertFalse("token" in response.json().get("bots")[0])
        self.assertFalse("token" in response.json().get("bots")[1])
        self.assertIsInstance(response, SuccessfulBotListResponse)

    def test_bot_mention_not_sent_when_bot_not_found(self):
        client_id = 0
        message = Message(message_id=0, sender_id=1, receiver_id=2, team_id=0, content="@test hola",
                          send_type=SendMessageType.CHANNEL, message_type=MessageType.TEXT)

        '''Mocked outputs'''
        bot = None

        def post(url, json, headers):
            from tests.test_services import test_bots
            MockedBotDatabase.posted_json = json

        sys.modules["daos.bots"].BotDatabaseClient.get_bot_by_id.return_value = bot
        sys.modules["requests"].post = MagicMock(side_effect=post)

        BotService.process_mention(client_id, message)
        self.assertIsNone(MockedBotDatabase.posted_json)

    def test_bot_mention_properly_processed_when_bot_found(self):
        client_id = 0
        message = Message(message_id=0, sender_id=1, receiver_id=2, team_id=0, content="@test hola",
                          send_type=SendMessageType.CHANNEL, message_type=MessageType.TEXT)

        '''Mocked outputs'''
        bot = Bot(bot_id=0, name="test", callback=None, token=None)

        def post(url, json, headers):
            from tests.test_services import test_bots
            MockedBotDatabase.posted_json = json

        sys.modules["daos.bots"].BotDatabaseClient.get_bot_by_id.return_value = bot
        sys.modules["requests"].post = MagicMock(side_effect=post)

        BotService.process_mention(client_id, message)
        self.assertIsNotNone(MockedBotDatabase.posted_json)
        self.assertEqual(1, MockedBotDatabase.posted_json.get("user_id"))
        self.assertEqual(2, MockedBotDatabase.posted_json.get("chat_id"))
        self.assertEqual(0, MockedBotDatabase.posted_json.get("team_id"))
        self.assertEqual("hola", MockedBotDatabase.posted_json.get("params"))
