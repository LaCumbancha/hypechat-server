import unittest
from unittest.mock import MagicMock

from dtos.models.users import RegularClient, User, PublicUser, PasswordRecovery
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
sys.modules["logging"].getLogger = MagicMock()

from services.users import UserService
mock = MagicMock()


class MockedUserDatabase:

    batch_recoveries = 0
    stored_recoveries = 1
    recovery_token_sent = None

    batch_user = User(user_id=0)
    stored_user = User(user_id=0, username="TEST")

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
        MockedUserDatabase.batch_recoveries = 0
        MockedUserDatabase.stored_recoveries = 1
        MockedUserDatabase.recovery_token_sent = None
        MockedUserDatabase.batch_user = User(user_id=0)
        MockedUserDatabase.stored_user = User(user_id=0, username="TEST")
        MockedUserDatabase.batch_online = True
        MockedUserDatabase.stored_online = True
        MockedUserDatabase.batch_token = ""
        MockedUserDatabase.stored_token = ""
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
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_username = MagicMock()
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["daos.database"].DatabaseClient.rollback = MagicMock(side_effect=rollback)

        response = UserService.create_user(data)
        self.assertEqual(0, len(MockedUserDatabase.stored_clients))
        self.assertEqual(0, len(MockedUserDatabase.stored_users))
        self.assertEqual(0, len(MockedUserDatabase.batch_clients))
        self.assertEqual(0, len(MockedUserDatabase.batch_users))
        self.assertIsInstance(response, BadRequestUserMessageResponse)

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
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_username.return_value = None
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_email.return_value = MagicMock()

        response = UserService.create_user(data)
        self.assertEqual(0, len(MockedUserDatabase.stored_clients))
        self.assertEqual(0, len(MockedUserDatabase.stored_users))
        self.assertEqual(0, len(MockedUserDatabase.batch_clients))
        self.assertEqual(0, len(MockedUserDatabase.batch_users))
        self.assertIsInstance(response, BadRequestUserMessageResponse)

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
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_username.return_value = None
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

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_username.return_value = None
        sys.modules["daos.users"].UserDatabaseClient.add_client = MagicMock(side_effect=add_client)
        sys.modules["daos.users"].UserDatabaseClient.add_user = MagicMock(side_effect=add_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        response = UserService.create_user(data)
        self.assertEqual(1, len(MockedUserDatabase.stored_clients))
        self.assertEqual(1, len(MockedUserDatabase.stored_users))
        self.assertEqual(0, len(MockedUserDatabase.batch_clients))
        self.assertEqual(0, len(MockedUserDatabase.batch_users))
        self.assertIsInstance(response, SuccessfulUserResponse)

    def test_app_user_login_with_wrong_password_returns_wrong_credentials(self):
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

    def test_user_teams_for_user_without_any_team_returns_empty_list(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        teams = []

        sys.modules["models.authentication"].Authenticator.authenticate.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_user_teams_by_user_id.return_value = teams

        response = UserService.teams_for_user(data)
        self.assertIsInstance(response, SuccessfulTeamsListResponse)
        self.assertEqual(0, len(response.teams))

    def test_user_teams_for_user_with_two_team_returns_full_list(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        teams = [Team(name="TEST1"), Team(name="TEST2")]

        sys.modules["models.authentication"].Authenticator.authenticate.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_user_teams_by_user_id.return_value = teams

        response = UserService.teams_for_user(data)
        self.assertIsInstance(response, SuccessfulTeamsListResponse)
        self.assertEqual(2, len(response.teams))

    def test_user_teams_channels_for_user_without_any_channel_returns_empty_list(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        channels = []

        sys.modules["models.authentication"].Authenticator.authenticate.return_value = user
        sys.modules["daos.channels"].ChannelDatabaseClient.get_user_channels_by_user_id.return_value = channels

        response = UserService.channels_for_user(data)
        self.assertIsInstance(response, SuccessfulChannelsListResponse)
        self.assertEqual(0, len(response.channels))

    def test_user_teams_channels_for_user_with_two_channels_returns_full_list(self):
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

    def test_update_user_with_used_username_returns_bad_request(self):
        data = MagicMock()
        data.updated_user = {"username": "TEST"}

        def commit():
            raise IntegrityError(mock, mock, mock)

        '''Mocked outputs'''
        user = User(user_id=0)

        sys.modules["models.authentication"].Authenticator.authenticate.return_value = user
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_username.return_value = MagicMock()

        response = UserService.update_user(data)
        self.assertIsInstance(response, BadRequestUserMessageResponse)

    def test_update_user_with_used_email_returns_bad_request(self):
        data = MagicMock()
        data.updated_user = {"username": "TEST"}

        def commit():
            raise IntegrityError(mock, mock, mock)

        '''Mocked outputs'''
        user = User(user_id=0)

        sys.modules["models.authentication"].Authenticator.authenticate.return_value = user
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_username.return_value = None
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_email.return_value = MagicMock()

        response = UserService.update_user(data)
        self.assertIsInstance(response, BadRequestUserMessageResponse)

    def test_update_user_with_new_unused_username_works_properly(self):
        data = MagicMock()
        data.updated_user = {"username": "UPDATED-TEST"}

        def update_user(user):
            from tests.test_services import test_users
            MockedUserDatabase.batch_user.username = user.username

        def commit():
            from tests.test_services import test_users
            MockedUserDatabase.stored_user = MockedUserDatabase.batch_user
            MockedUserDatabase.batch_user = User(user_id=0)

        '''Mocked outputs'''
        user = User(user_id=0)

        sys.modules["models.authentication"].Authenticator.authenticate.return_value = user
        sys.modules["daos.users"].UserDatabaseClient.update_user = MagicMock(side_effect=update_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        response = UserService.update_user(data)
        self.assertEqual(0, MockedUserDatabase.batch_user.id)
        self.assertEqual(0, MockedUserDatabase.stored_user.id)
        self.assertEqual("UPDATED-TEST", MockedUserDatabase.stored_user.username)
        self.assertIsInstance(response, SuccessfulUserResponse)

    def test_user_profile_without_teams_returns_empty_team_list(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = MagicMock()
        user.id = 1
        user.team_id = None
        user.username = "TEST"

        sys.modules["models.authentication"].Authenticator.authenticate.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_user_teams_by_user_id.return_value = []
        sys.modules["daos.users"].UserDatabaseClient.get_user_profile.return_value = [user]

        response = UserService.user_profile(data)
        self.assertEqual(1, response.client.id)
        self.assertEqual("TEST", response.client.username)
        self.assertEqual(0, len(response.client.teams))
        self.assertIsInstance(response, SuccessfulFullUserResponse)

    def test_user_profile_with_two_teams_returns_full_list(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0, username="TEST")
        teams = [Team(team_id=1, name="TEST1"), Team(team_id=2, name="TEST2")]
        user_with_teams1 = MagicMock()
        user_with_teams1.id = 0
        user_with_teams1.username = "TEST"
        user_with_teams1.team_id = 1
        user_with_teams1.team_name = "TEST1"
        user_with_teams1.team_role = "CREATOR"
        user_with_teams2 = MagicMock()
        user_with_teams2.id = 0
        user_with_teams2.username = "TEST"
        user_with_teams2.team_id = 2
        user_with_teams2.team_name = "TEST2"
        user_with_teams2.team_role = "MEMBER"
        user_with_teams = [user_with_teams1, user_with_teams2]

        sys.modules["models.authentication"].Authenticator.authenticate.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_user_teams_by_user_id.return_value = teams
        sys.modules["daos.users"].UserDatabaseClient.get_user_profile.return_value = user_with_teams

        response = UserService.user_profile(data)
        self.assertEqual(0, response.client.id)
        self.assertEqual("TEST", response.client.username)
        self.assertEqual(2, len(response.client.teams))
        self.assertEqual(1, response.client.teams[0]["id"])
        self.assertEqual("TEST1", response.client.teams[0]["name"])
        self.assertEqual("CREATOR", response.client.teams[0]["role"])
        self.assertEqual(2, response.client.teams[1]["id"])
        self.assertEqual("TEST2", response.client.teams[1]["name"])
        self.assertEqual("MEMBER", response.client.teams[1]["role"])
        self.assertIsInstance(response, SuccessfulFullUserResponse)

    def test_user_profile_from_different_team_returns_none(self):
        searched_user_id = 1
        active_user_team_id = 0

        '''Mocked outputs'''
        user = User(user_id=1, username="TEST")
        teams = [Team(team_id=1, name="TEST1")]
        user_with_teams = MagicMock()
        user_with_teams.id = 0
        user_with_teams.username = "TEST"
        user_with_teams.team_id = 1
        user_with_teams.team_name = "TEST1"
        user_with_teams.team_role = "MEMBER"

        sys.modules["models.authentication"].Authenticator.authenticate.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_user_teams_by_user_id.return_value = teams
        sys.modules["daos.users"].UserDatabaseClient.get_user_profile.return_value = user_with_teams

        response = UserService.team_user_profile(searched_user_id, active_user_team_id)
        self.assertIsNone(response)

    def test_recover_password_with_not_found_user_throws_exception(self):
        data = MagicMock()

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_email.return_value = None
        self.assertRaises(UserNotFoundError, UserService.recover_password, data)

    def test_recover_password_with_old_recover_request_done_returns_same_token(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0, username="TEST")
        password_recovery = PasswordRecovery(user_id=0, token="TEST")

        def send_email(email_data):
            from tests.test_services import test_users
            MockedUserDatabase.recovery_token_sent = email_data.token

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_email.return_value = user
        sys.modules["daos.users"].UserDatabaseClient.get_password_recovery_by_id.return_value = password_recovery
        sys.modules["services.emails"].EmailService.send_email = MagicMock(side_effect=send_email)

        response = UserService.recover_password(data)
        self.assertEqual(MockedUserDatabase.recovery_token_sent, "TEST")
        self.assertIsInstance(response, SuccessfulUserMessageResponse)

    def test_recover_password_with_non_recover_request_done_returns_token(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0, username="TEST")

        def send_email(email_data):
            from tests.test_services import test_users
            MockedUserDatabase.recovery_token_sent = email_data.token

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_email.return_value = user
        sys.modules["daos.users"].UserDatabaseClient.get_password_recovery_by_id.return_value = None
        sys.modules["models.authentication"].Authenticator.generate_recovery_token.return_value = "TEST"
        sys.modules["services.emails"].EmailService.send_email = MagicMock(side_effect=send_email)

        response = UserService.recover_password(data)
        self.assertEqual(MockedUserDatabase.recovery_token_sent, "TEST")
        self.assertIsInstance(response, SuccessfulUserMessageResponse)

    def test_regenerate_token_with_not_found_user_throws_exception(self):
        data = MagicMock()

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_email.return_value = None
        self.assertRaises(UserNotFoundError, UserService.regenerate_token, data)

    def test_regenerate_token_with_not_found_password_recovery_data_returns_bad_request(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0, username="TEST")

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_email.return_value = user
        sys.modules["daos.users"].UserDatabaseClient.get_password_recovery_by_id.return_value = None

        response = UserService.regenerate_token(data)
        self.assertIsInstance(response, BadRequestUserMessageResponse)

    def test_regenerate_token_with_correct_password_recovery_data_works_properly(self):
        data = MagicMock()

        def delete_recovery(_):
            from tests.test_services import test_users
            MockedUserDatabase.batch_recoveries += 1

        def update_user(_):
            from tests.test_services import test_users
            MockedUserDatabase.batch_online = True

        def commit():
            from tests.test_services import test_users
            MockedUserDatabase.stored_recoveries -= MockedUserDatabase.batch_recoveries
            MockedUserDatabase.stored_online = MockedUserDatabase.batch_online
            MockedUserDatabase.batch_recoveries = 0
            MockedUserDatabase.batch_online = False

        '''Mocked outputs'''
        user = User(user_id=0, username="TEST")
        password_recovery = PasswordRecovery(user_id=0, token="TEST")

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_email.return_value = user
        sys.modules["daos.users"].UserDatabaseClient.get_password_recovery_by_id.return_value = password_recovery
        sys.modules["daos.users"].UserDatabaseClient.delete_password_recovery = MagicMock(side_effect=delete_recovery)
        sys.modules["daos.users"].UserDatabaseClient.update_user = MagicMock(side_effect=update_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        response = UserService.regenerate_token(data)
        self.assertFalse(MockedUserDatabase.batch_online)
        self.assertTrue(MockedUserDatabase.stored_online)
        self.assertEqual(0, MockedUserDatabase.batch_recoveries)
        self.assertEqual(0, MockedUserDatabase.batch_recoveries)
        self.assertIsInstance(response, SuccessfulUserResponse)

    def test_regenerate_token_with_failing_database_returns_unsuccessful_response(self):
        data = MagicMock()

        def delete_recovery(_):
            from tests.test_services import test_users
            MockedUserDatabase.batch_recoveries += 1

        def update_user(_):
            from tests.test_services import test_users
            MockedUserDatabase.batch_online = True

        def commit():
            raise IntegrityError(mock, mock, mock)

        def rollback():
            from tests.test_services import test_users
            MockedUserDatabase.batch_recoveries = 0
            MockedUserDatabase.batch_online = False

        '''Mocked outputs'''
        user = User(user_id=0, username="TEST")
        password_recovery = PasswordRecovery(user_id=0, token="TEST")

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_email.return_value = user
        sys.modules["daos.users"].UserDatabaseClient.get_password_recovery_by_id.return_value = password_recovery
        sys.modules["daos.users"].UserDatabaseClient.delete_password_recovery = MagicMock(side_effect=delete_recovery)
        sys.modules["daos.users"].UserDatabaseClient.update_user = MagicMock(side_effect=update_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["daos.database"].DatabaseClient.rollback = MagicMock(side_effect=rollback)

        response = UserService.regenerate_token(data)
        self.assertFalse(MockedUserDatabase.batch_online)
        self.assertEqual(0, MockedUserDatabase.batch_recoveries)
        self.assertIsInstance(response, UnsuccessfulClientResponse)
