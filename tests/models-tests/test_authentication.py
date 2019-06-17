import unittest
from unittest.mock import MagicMock, Mock
from time import sleep
from exceptions.exceptions import WrongTokenError, UserNotFoundError, NoPermissionsError


'''Mocking environment properties'''
import sys
sys.modules["config"] = MagicMock()
sys.modules["app"] = MagicMock()
sys.modules["app"].db = MagicMock()
sys.modules["tables.users"] = MagicMock()
sys.modules["tables.channels"] = MagicMock()
sys.modules["tables.teams"] = MagicMock()
sys.modules["os"].getenv = MagicMock(side_effect=lambda key: environment_properties.get(key))

environment_properties = {
    'SECRET': "TEST",
    'INVITE_TOKEN_LENGTH': "10",
    'RECOVER_TOKEN_LENGTH': "8"
}

from models.authentication import Authenticator


class AuthenticationTestCase(unittest.TestCase):

    def test_different_tokens_generated_for_different_users(self):
        user1_id = 1
        user2_id = 2
        self.assertNotEqual(Authenticator.generate(user1_id), Authenticator.generate(user2_id))

    def test_different_tokens_generated_for_same_user_in_different_times(self):
        user_id = 1
        token1 = Authenticator.generate(user_id)
        sleep(0.05)
        token2 = Authenticator.generate(user_id)
        self.assertNotEqual(token1, token2)

    def test_recovery_tokens_generated_are_different(self):
        self.assertNotEqual(Authenticator.generate_recovery_token(), Authenticator.generate_recovery_token())

    def test_team_invitations_generated_are_different(self):
        self.assertNotEqual(Authenticator.generate_team_invitation(), Authenticator.generate_team_invitation())

    def test_user_with_undecodable_token_throws_exception(self):
        authentication = MagicMock()
        authentication.token = "FAKE-TOKEN"
        self.assertRaises(WrongTokenError, Authenticator.authenticate, authentication)

    def test_user_not_found_after_token_decoding_throws_exception(self):
        user1_id = 1
        token = Authenticator.generate(user1_id)
        authentication = MagicMock()
        authentication.token = token
        sys.modules["app"].db.session.query().filter().one_or_none = MagicMock(return_value=None)
        self.assertRaises(UserNotFoundError, Authenticator.authenticate, authentication)

    def test_user_with_different_token_in_database_throws_exception(self):
        user1_id = 1
        token = Authenticator.generate(user1_id)
        authentication = MagicMock()
        authentication.token = token
        sys.modules["app"].db.session.query().filter().one_or_none = MagicMock()
        sys.modules["app"].db.session.query().filter().one_or_none().auth_token = "DIFFERENT-TOKEN"
        self.assertRaises(WrongTokenError, Authenticator.authenticate, authentication)

    def test_user_with_same_token_in_database_authenticates(self):
        user1_id = 1
        token = Authenticator.generate(user1_id)
        authentication = MagicMock()
        authentication.token = token
        sys.modules["app"].db.session.query().filter().one_or_none = MagicMock()
        sys.modules["app"].db.session.query().filter().one_or_none().auth_token = token
        sys.modules["app"].db.session.query().filter().one_or_none().id = user1_id
        authenticated_user = Authenticator.authenticate(authentication)
        self.assertTrue(authenticated_user.id == user1_id)

    def test_app_user_doesnt_belonging_to_team_throws_exception(self):
        user1_id = 1
        token = Authenticator.generate(user1_id)
        authentication = MagicMock()
        authentication.token = token
        sys.modules["app"].db.session.query().filter().one_or_none = MagicMock()
        sys.modules["app"].db.session.query().filter().one_or_none().auth_token = token
        sys.modules["app"].db.session.query().filter().one_or_none().id = user1_id
        sys.modules["app"].db.session.query().join().one_or_none = MagicMock(return_value=None)
        self.assertRaises(NoPermissionsError, Authenticator.authenticate_team, authentication)

    def test_app_user_doesnt_authenticating_to_unknown_team_throws_exception(self):
        user1_id = 1
        token = Authenticator.generate(user1_id)
        authentication = MagicMock()
        authentication.token = token
        sys.modules["app"].db.session.query().filter().one_or_none = MagicMock()
        sys.modules["app"].db.session.query().filter().one_or_none().auth_token = token
        sys.modules["app"].db.session.query().filter().one_or_none().id = user1_id
        sys.modules["app"].db.session.query().join().one_or_none = MagicMock(return_value=None)
        self.assertRaises(NoPermissionsError, Authenticator.authenticate_team, authentication)
