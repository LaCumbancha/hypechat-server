import unittest
from unittest.mock import MagicMock

from dtos.models.users import RegularClient, User
from dtos.responses.clients import *
from models.constants import UserResponseStatus
from sqlalchemy.exc import IntegrityError

'''Mocking environment properties'''
import sys
sys.modules["daos.database"] = MagicMock()
sys.modules["daos.users"] = MagicMock()
sys.modules["daos.teams"] = MagicMock()
sys.modules["daos.channels"] = MagicMock()
sys.modules["models.authentication"] = MagicMock()

from services.users import UserService
mock = MagicMock()


class MockedUserDatabase:

    batch_users = []
    stored_users = []
    batch_clients = []
    stored_clients = []


class UserServiceTestCase(unittest.TestCase):

    def tearDown(self):
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
        self.assertIsInstance(response, BadRequestUserMessageResponse)
        self.assertEqual(response.status, UserResponseStatus.ALREADY_REGISTERED.value)

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
        self.assertIsInstance(response, BadRequestUserMessageResponse)
        self.assertEqual(response.status, UserResponseStatus.ALREADY_REGISTERED.value)

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
