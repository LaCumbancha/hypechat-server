import unittest
from unittest.mock import MagicMock

from dtos.models.users import RegularClient, User
from dtos.models.teams import Team
from dtos.models.channels import Channel, ChannelCreator
from dtos.responses.clients import *
from dtos.responses.teams import *
from dtos.responses.channels import *
from models.constants import UserResponseStatus
from sqlalchemy.exc import IntegrityError
from exceptions.exceptions import UserNotFoundError, FacebookWrongTokenError

'''Mocking environment properties'''
import sys
sys.modules["config"] = MagicMock()
sys.modules["daos.database"] = MagicMock()
sys.modules["daos.users"] = MagicMock()
sys.modules["daos.teams"] = MagicMock()
sys.modules["daos.channels"] = MagicMock()
sys.modules["models.authentication"] = MagicMock()
sys.modules["passlib.apps"] = MagicMock()

from services.users import UserService
mock = MagicMock()


class MockedUserDatabase:

    batch_online = True
    stored_online = True

    batch_token = ""
    stored_token = ""

    batch_login = False
    stored_login = False

    batch_users = []
    stored_users = []
    batch_clients = []
    stored_clients = []


class UserServiceTestCase(unittest.TestCase):

    def tearDown(self):
        MockedUserDatabase.batch_login = False
        MockedUserDatabase.stored_login = False
        MockedUserDatabase.batch_users = []
        MockedUserDatabase.stored_users = []
        MockedUserDatabase.batch_clients = []
        MockedUserDatabase.stored_clients = []

    def test_create_user_with_username_in_use_returns_bad_request(self):
        data = MagicMock()

        def add_client():
            from tests.test_services import test_users
            client = RegularClient(client_id=0)
            MockedUserDatabase.batch_clients += [client]
            return client

        def add_user(_):
            from tests.test_services import test_users
            MockedUserDatabase.batch_users += [User(user_id=0)]

        def commit():
            raise IntegrityError(mock, mock, mock)

        def rollback():
            from tests.test_services import test_users
            MockedUserDatabase.batch_clients = []
            MockedUserDatabase.batch_users = []

        sys.modules["daos.users"].UserDatabaseClient.add_client = MagicMock(side_effect=add_client)
        sys.modules["daos.users"].UserDatabaseClient.add_user = MagicMock(side_effect=add_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["daos.database"].DatabaseClient.rollback = MagicMock(side_effect=rollback)

        response = UserService.create_user(data)
        self.assertEqual(0, len(MockedUserDatabase.stored_clients))
        self.assertEqual(0, len(MockedUserDatabase.stored_users))
        self.assertEqual(0, len(MockedUserDatabase.batch_clients))
        self.assertEqual(0, len(MockedUserDatabase.batch_users))
        self.assertIsInstance(response, UnsuccessfulClientResponse)

    def test_create_user_with_email_in_use_returns_bad_request(self):
        data = MagicMock()

        def add_client():
            from tests.test_services import test_users
            client = RegularClient(client_id=0)
            MockedUserDatabase.batch_clients += [client]
            return client

        def add_user(_):
            from tests.test_services import test_users
            MockedUserDatabase.batch_users += [User(user_id=0)]

        def commit():
            raise IntegrityError(mock, mock, mock)

        def rollback():
            from tests.test_services import test_users
            MockedUserDatabase.batch_clients = []
            MockedUserDatabase.batch_users = []

        sys.modules["daos.users"].UserDatabaseClient.add_client = MagicMock(side_effect=add_client)
        sys.modules["daos.users"].UserDatabaseClient.add_user = MagicMock(side_effect=add_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["daos.database"].DatabaseClient.rollback = MagicMock(side_effect=rollback)
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_email.return_value = None
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_username.return_value = None

        response = UserService.create_user(data)
        self.assertEqual(0, len(MockedUserDatabase.stored_clients))
        self.assertEqual(0, len(MockedUserDatabase.stored_users))
        self.assertEqual(0, len(MockedUserDatabase.batch_clients))
        self.assertEqual(0, len(MockedUserDatabase.batch_users))
        self.assertIsInstance(response, UnsuccessfulClientResponse)

    def test_create_user_with_unknown_error_returns_unsuccessful(self):
        data = MagicMock()

        def add_client():
            from tests.test_services import test_users
            client = RegularClient(client_id=0)
            MockedUserDatabase.batch_clients += [client]
            return client

        def add_user(_):
            from tests.test_services import test_users
            MockedUserDatabase.batch_users += [User(user_id=0)]

        def commit():
            raise IntegrityError(mock, mock, mock)

        def rollback():
            from tests.test_services import test_users
            MockedUserDatabase.batch_clients = []
            MockedUserDatabase.batch_users = []

        sys.modules["daos.users"].UserDatabaseClient.add_client = MagicMock(side_effect=add_client)
        sys.modules["daos.users"].UserDatabaseClient.add_user = MagicMock(side_effect=add_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["daos.database"].DatabaseClient.rollback = MagicMock(side_effect=rollback)
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_email.return_value = None

        response = UserService.create_user(data)
        self.assertEqual(0, len(MockedUserDatabase.stored_clients))
        self.assertEqual(0, len(MockedUserDatabase.stored_users))
        self.assertEqual(0, len(MockedUserDatabase.batch_clients))
        self.assertEqual(0, len(MockedUserDatabase.batch_users))
        self.assertIsInstance(response, UnsuccessfulClientResponse)

    def test_create_user_with_correct_data_works_properly(self):
        data = MagicMock()

        def add_client():
            from tests.test_services import test_users
            client = RegularClient(client_id=0)
            MockedUserDatabase.batch_clients += [client]
            return client

        def add_user(_):
            from tests.test_services import test_users
            MockedUserDatabase.batch_users += [User(user_id=0)]

        def commit():
            from tests.test_services import test_users
            MockedUserDatabase.stored_clients = MockedUserDatabase.batch_clients
            MockedUserDatabase.batch_clients = []
            MockedUserDatabase.stored_users = MockedUserDatabase.batch_users
            MockedUserDatabase.batch_users = []

        sys.modules["daos.users"].UserDatabaseClient.add_client = MagicMock(side_effect=add_client)
        sys.modules["daos.users"].UserDatabaseClient.add_user = MagicMock(side_effect=add_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        response = UserService.create_user(data)
        self.assertEqual(1, len(MockedUserDatabase.stored_clients))
        self.assertEqual(1, len(MockedUserDatabase.stored_users))
        self.assertEqual(0, len(MockedUserDatabase.batch_clients))
        self.assertEqual(0, len(MockedUserDatabase.batch_users))
        self.assertIsInstance(response, SuccessfulUserResponse)

    def test_app_user_login_with_wrong_password_return_wrong_credentials(self):
        data = MagicMock()
        data.facebook_token = None

        def update_user(_):
            from tests.test_services import test_users
            MockedUserDatabase.batch_login = True

        def commit():
            from tests.test_services import test_users
            MockedUserDatabase.stored_login = MockedUserDatabase.batch_login
            MockedUserDatabase.batch_login = False

        '''Mocked outputs'''
        user = User(user_id=0)

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_email.return_value = user
        sys.modules["daos.users"].UserDatabaseClient.update_user = MagicMock(side_effect=update_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["passlib.apps"].custom_app_context.verify.return_value = False

        response = UserService.login_user(data)
        self.assertFalse(MockedUserDatabase.batch_login)
        self.assertFalse(MockedUserDatabase.stored_login)
        self.assertIsInstance(response, SuccessfulUserMessageResponse)
        self.assertEqual(response.status, UserResponseStatus.WRONG_CREDENTIALS.value)

    def test_app_user_login_with_correct_password_works_properly(self):
        data = MagicMock()
        data.facebook_token = None

        def update_user(_):
            from tests.test_services import test_users
            MockedUserDatabase.batch_login = True

        def commit():
            from tests.test_services import test_users
            MockedUserDatabase.stored_login = MockedUserDatabase.batch_login
            MockedUserDatabase.batch_login = False

        '''Mocked outputs'''
        user = User(user_id=0)

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_email.return_value = user
        sys.modules["daos.users"].UserDatabaseClient.update_user = MagicMock(side_effect=update_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["passlib.apps"].custom_app_context.verify.return_value = True

        response = UserService.login_user(data)
        self.assertFalse(MockedUserDatabase.batch_login)
        self.assertTrue(MockedUserDatabase.stored_login)
        self.assertIsInstance(response, SuccessfulUserResponse)

    def test_app_user_login_with_wrong_email_throws_exception(self):
        data = MagicMock()
        data.facebook_token = None
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_email.return_value = None
        self.assertRaises(UserNotFoundError, UserService.login_user, data)

    def test_facebook_user_login_with_wrong_token_returns_unsuccessful_client(self):
        data = MagicMock()
        data.facebook_token = 0

        def fail(_):
            raise FacebookWrongTokenError(mock)

        sys.modules["services.facebook"].FacebookService.get_user_from_facebook = MagicMock(side_effect=fail)

        response = UserService.login_user(data)
        self.assertFalse(MockedUserDatabase.batch_login)
        self.assertFalse(MockedUserDatabase.stored_login)
        self.assertIsInstance(response, UnsuccessfulClientResponse)

    def test_facebook_user_login_with_new_token_returns_works_properly(self):
        data = MagicMock()
        data.facebook_token = 0

        def add_client():
            from tests.test_services import test_users
            client = RegularClient(client_id=0)
            MockedUserDatabase.batch_clients += [client]
            return client

        def add_user(_):
            from tests.test_services import test_users
            MockedUserDatabase.batch_login = True
            MockedUserDatabase.batch_users += [User(user_id=0)]

        def commit():
            from tests.test_services import test_users
            MockedUserDatabase.stored_login = MockedUserDatabase.batch_login
            MockedUserDatabase.stored_users = MockedUserDatabase.batch_users
            MockedUserDatabase.stored_clients = MockedUserDatabase.batch_clients
            MockedUserDatabase.batch_login = False
            MockedUserDatabase.batch_users = []
            MockedUserDatabase.batch_clients = []

        sys.modules["services.facebook"].FacebookService.get_user_from_facebook = MagicMock()
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_facebook_id.return_value = None
        sys.modules["daos.users"].UserDatabaseClient.add_client = MagicMock(side_effect=add_client)
        sys.modules["daos.users"].UserDatabaseClient.add_user = MagicMock(side_effect=add_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        response = UserService.login_user(data)
        self.assertFalse(MockedUserDatabase.batch_login)
        self.assertTrue(MockedUserDatabase.stored_login)
        self.assertEqual(1, len(MockedUserDatabase.stored_clients))
        self.assertEqual(1, len(MockedUserDatabase.stored_users))
        self.assertEqual(0, len(MockedUserDatabase.batch_clients))
        self.assertEqual(0, len(MockedUserDatabase.batch_users))
        self.assertIsInstance(response, SuccessfulUserResponse)

    def test_facebook_user_login_with_already_in_use_token_returns_works_properly(self):
        data = MagicMock()
        data.facebook_token = 0

        def update_user(_):
            from tests.test_services import test_users
            MockedUserDatabase.batch_login = True

        def commit():
            from tests.test_services import test_users
            MockedUserDatabase.stored_login = MockedUserDatabase.batch_login
            MockedUserDatabase.batch_login = False

        '''Mocked outputs'''
        user = User(user_id=0)

        sys.modules["services.facebook"].FacebookService.get_user_from_facebook = MagicMock()
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_facebook_id.return_value = user
        sys.modules["daos.users"].UserDatabaseClient.update_user = MagicMock(side_effect=update_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        response = UserService.login_user(data)
        self.assertFalse(MockedUserDatabase.batch_login)
        self.assertTrue(MockedUserDatabase.stored_login)
        self.assertIsInstance(response, SuccessfulUserResponse)

    def test_logout_user_works_properly(self):
        data = MagicMock()

        def update_user(_):
            from tests.test_services import test_users
            MockedUserDatabase.batch_login = False
            MockedUserDatabase.batch_token = None

        def commit():
            from tests.test_services import test_users
            MockedUserDatabase.stored_login = MockedUserDatabase.batch_login
            MockedUserDatabase.stored_token = MockedUserDatabase.batch_token
            MockedUserDatabase.batch_login = True
            MockedUserDatabase.batch_token = "TEST"

        '''Mocked outputs'''
        user = User(user_id=0)

        sys.modules["models.authentication"].Authenticator.authenticate.return_value = user
        sys.modules["daos.users"].UserDatabaseClient.update_user = MagicMock(side_effect=update_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        response = UserService.logout_user(data)
        self.assertTrue(MockedUserDatabase.batch_login)
        self.assertFalse(MockedUserDatabase.stored_login)
        self.assertIsNotNone(MockedUserDatabase.batch_token)
        self.assertIsNone(MockedUserDatabase.stored_token)
        self.assertIsInstance(response, SuccessfulUserMessageResponse)

    def test_set_user_online_works_properly(self):
        data = MagicMock()

        def update_user(_):
            from tests.test_services import test_users
            MockedUserDatabase.batch_online = True

        def commit():
            from tests.test_services import test_users
            MockedUserDatabase.stored_online = MockedUserDatabase.batch_online
            MockedUserDatabase.batch_online = False

        '''Mocked outputs'''
        user = User(user_id=0)

        sys.modules["models.authentication"].Authenticator.authenticate.return_value = user
        sys.modules["daos.users"].UserDatabaseClient.update_user = MagicMock(side_effect=update_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        response = UserService.set_user_online(data)
        self.assertFalse(MockedUserDatabase.batch_online)
        self.assertTrue(MockedUserDatabase.stored_online)
        self.assertIsInstance(response, SuccessfulUserResponse)

    def test_set_user_offline_works_properly(self):
        data = MagicMock()

        def update_user(_):
            from tests.test_services import test_users
            MockedUserDatabase.batch_online = False

        def commit():
            from tests.test_services import test_users
            MockedUserDatabase.stored_online = MockedUserDatabase.batch_online
            MockedUserDatabase.batch_online = True

        '''Mocked outputs'''
        user = User(user_id=0)

        sys.modules["models.authentication"].Authenticator.authenticate.return_value = user
        sys.modules["daos.users"].UserDatabaseClient.update_user = MagicMock(side_effect=update_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        response = UserService.set_user_offline(data)
        self.assertTrue(MockedUserDatabase.batch_online)
        self.assertFalse(MockedUserDatabase.stored_online)
        self.assertIsInstance(response, SuccessfulUserResponse)

    def test_user_teams_for_user_without_any_team_return_empty_list(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        teams = []

        sys.modules["models.authentication"].Authenticator.authenticate.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_user_teams_by_user_id.return_value = teams

        response = UserService.teams_for_user(data)
        self.assertIsInstance(response, SuccessfulTeamsListResponse)
        self.assertEqual(0, len(response.teams))

    def test_user_teams_for_user_with_two_team_return_full_list(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        teams = [Team(name="TEST1"), Team(name="TEST2")]

        sys.modules["models.authentication"].Authenticator.authenticate.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_user_teams_by_user_id.return_value = teams

        response = UserService.teams_for_user(data)
        self.assertIsInstance(response, SuccessfulTeamsListResponse)
        self.assertEqual(2, len(response.teams))

    def test_user_teams_channels_for_user_without_any_channel_return_empty_list(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        channels = []

        sys.modules["models.authentication"].Authenticator.authenticate.return_value = user
        sys.modules["daos.channels"].ChannelDatabaseClient.get_user_channels_by_user_id.return_value = channels

        response = UserService.channels_for_user(data)
        self.assertIsInstance(response, SuccessfulChannelsListResponse)
        self.assertEqual(0, len(response.channels))

    def test_user_teams_channels_for_user_with_two_channels_return_full_list(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        channels = [
            Channel(channel_id=1, team_id=0, name="TEST1",
                    creator=ChannelCreator(user_id=0, username="TESTER", first_name="TESTER", last_name="TESTER")),
            Channel(channel_id=2, team_id=0, name="TEST2",
                    creator=ChannelCreator(user_id=0, username="TESTER", first_name="TESTER", last_name="TESTER")),
        ]

        sys.modules["models.authentication"].Authenticator.authenticate.return_value = user
        sys.modules["daos.channels"].ChannelDatabaseClient.get_user_channels_by_user_id.return_value = channels

        response = UserService.channels_for_user(data)
        self.assertIsInstance(response, SuccessfulChannelsListResponse)
        self.assertEqual(2, len(response.channels))
