import unittest
from unittest.mock import MagicMock

from time import sleep
from exceptions.exceptions import WrongTokenError, UserNotFoundError, NoPermissionsError, TeamNotFoundError, \
    ChannelNotFoundError

from dtos.models.users import User, PublicUser
from dtos.models.teams import Team
from dtos.models.channels import Channel

from models.constants import TeamRoles, UserRoles

'''Mocking environment properties'''
import sys

sys.modules["config"] = MagicMock()
sys.modules["daos.database"] = MagicMock()
sys.modules["daos.users"] = MagicMock()
sys.modules["daos.teams"] = MagicMock()
sys.modules["daos.channels"] = MagicMock()
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
        user_id = 0
        token = Authenticator.generate(user_id)
        authentication = MagicMock()
        authentication.token = token
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = None
        self.assertRaises(UserNotFoundError, Authenticator.authenticate, authentication)

    def test_user_with_different_token_in_database_throws_exception(self):
        user_id = 0
        token = Authenticator.generate(user_id)
        authentication = MagicMock()
        authentication.token = token

        '''Mocked outputs'''
        user = User(user_id=user_id, token="DIFFERENT-TOKEN")

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = user
        self.assertRaises(WrongTokenError, Authenticator.authenticate, authentication)

    def test_user_with_same_token_in_database_authenticates(self):
        user_id = 0
        token = Authenticator.generate(user_id)
        authentication = MagicMock()
        authentication.token = token
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = User(user_id=user_id, token=token)
        authenticated_user = Authenticator.authenticate(authentication)
        self.assertTrue(authenticated_user.id == user_id)

    def test_app_user_doesnt_belonging_to_team_throws_exception(self):
        user_id = 0
        token = Authenticator.generate(user_id)
        authentication = MagicMock()
        authentication.token = token
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = User(user_id=user_id, token=token)
        sys.modules["daos.users"].UserDatabaseClient.get_team_user_by_ids.return_value = None
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_id.return_value = Team(name=None)
        self.assertRaises(NoPermissionsError, Authenticator.authenticate_team, authentication)

    def test_app_user_authenticating_to_unknown_team_throws_exception(self):
        user_id = 0
        token = Authenticator.generate(user_id)
        authentication = MagicMock()
        authentication.token = token
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = User(user_id=user_id, token=token)
        sys.modules["daos.users"].UserDatabaseClient.get_team_user_by_ids.return_value = None
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_id.return_value = None
        self.assertRaises(TeamNotFoundError, Authenticator.authenticate_team, authentication)

    def test_app_user_authenticating_to_team_with_no_role_verifying_throws_exception(self):
        user_id = 0
        team_id = 0
        token = Authenticator.generate(user_id)
        authentication = MagicMock()
        authentication.token = token
        authentication.team_id = team_id

        def verifying_function(_): return False

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = User(user_id=user_id, token=token)
        self.assertRaises(NoPermissionsError, Authenticator.authenticate_team, authentication, verifying_function)

    def test_app_user_authenticating_to_team_with_role_verifying_authenticates(self):
        user_id = 0
        team_id = 0
        token = Authenticator.generate(user_id)
        authentication = MagicMock()
        authentication.token = token
        authentication.team_id = team_id

        def verifying_function(_): return True

        '''Mocked outputs'''
        user = User(user_id=user_id, token=token)
        team_user = PublicUser(user_id=user_id)
        team_user.team_role = TeamRoles.CREATOR.value
        team_user.team_id = team_id

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = user
        sys.modules["daos.users"].UserDatabaseClient.get_team_user_by_ids.return_value = team_user

        authenticated_user = Authenticator.authenticate_team(authentication, verifying_function)
        self.assertEqual(user_id, authenticated_user.id)

    def test_admin_user_authenticates_to_every_team(self):
        user_id = 0
        team_id = 0
        token = Authenticator.generate(user_id)
        authentication = MagicMock()
        authentication.token = token
        authentication.team_id = team_id

        '''Mocked outputs'''
        user = User(user_id=user_id, token=token, role=UserRoles.ADMIN.value)

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = user
        authenticated_user = Authenticator.authenticate_team(authentication)

        self.assertEqual(user_id, authenticated_user.id)
        self.assertEqual(team_id, authenticated_user.team_id)
        self.assertEqual(UserRoles.ADMIN.value, authenticated_user.role)

    def test_team_moderator_authenticates_to_every_team_channel(self):
        user_id = 0
        team_id = 0
        channel_id = 0
        token = Authenticator.generate(user_id)
        authentication = MagicMock()
        authentication.token = token
        authentication.team_id = team_id
        authentication.channel_id = channel_id

        '''Mocked outputs'''
        user = User(user_id=user_id, token=token)
        team_user = PublicUser(user_id=user_id)
        team_user.team_role = TeamRoles.MODERATOR.value
        team_user.team_id = team_id

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = user
        sys.modules["daos.users"].UserDatabaseClient.get_team_user_by_ids.return_value = team_user
        authenticated_user = Authenticator.authenticate_channel(authentication)

        self.assertEqual(user_id, authenticated_user.id)
        self.assertEqual(team_id, authenticated_user.team_id)
        self.assertEqual(channel_id, authenticated_user.channel_id)
        self.assertFalse(authenticated_user.is_channel_creator)
        self.assertEqual(TeamRoles.MODERATOR.value, authenticated_user.team_role)

    def test_team_member_authenticates_just_to_channels_he_belongs(self):
        user_id = 0
        team_id = 0
        channel_id = 0
        token = Authenticator.generate(user_id)
        authentication = MagicMock()
        authentication.token = token
        authentication.team_id = team_id
        authentication.channel_id = channel_id

        '''Mocked outputs'''
        user = User(user_id=user_id, token=token)
        team_user = PublicUser(user_id=user_id)
        team_user.team_role = TeamRoles.MEMBER.value
        team_user.team_id = team_id
        channel_user = PublicUser(user_id=user_id)
        channel_user.team_id = team_id
        channel_user.channel_id = channel_id
        channel_user.is_channel_creator = False

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = user
        sys.modules["daos.users"].UserDatabaseClient.get_team_user_by_ids.return_value = team_user
        sys.modules["daos.users"].UserDatabaseClient.get_channel_user_by_ids.return_value = channel_user
        authenticated_user = Authenticator.authenticate_channel(authentication)

        self.assertEqual(user_id, authenticated_user.id)
        self.assertEqual(team_id, authenticated_user.team_id)
        self.assertEqual(channel_id, authenticated_user.channel_id)
        self.assertFalse(authenticated_user.is_channel_creator)

    def test_channel_regular_member_authenticating_to_channel_moderation_throws_exception(self):
        user_id = 0
        team_id = 0
        channel_id = 0
        token = Authenticator.generate(user_id)
        authentication = MagicMock()
        authentication.token = token
        authentication.team_id = team_id
        authentication.channel_id = channel_id

        '''Mocked outputs'''
        user = User(user_id=user_id, token=token)
        team_user = PublicUser(user_id=user_id)
        team_user.team_role = TeamRoles.MEMBER.value
        team_user.team_id = team_id
        channel_user = PublicUser(user_id=user_id)
        channel_user.team_id = team_id
        channel_user.channel_id = channel_id
        channel_user.is_channel_creator = False

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = user
        sys.modules["daos.users"].UserDatabaseClient.get_team_user_by_ids.return_value = team_user
        sys.modules["daos.users"].UserDatabaseClient.get_channel_user_by_ids.return_value = channel_user
        self.assertRaises(NoPermissionsError, Authenticator.authenticate_channel, authentication,
                          TeamRoles.is_channel_creator)

        channel_user.is_channel_creator = True
        sys.modules["daos.users"].UserDatabaseClient.get_channel_user_by_ids.return_value = channel_user
        authenticated_user = Authenticator.authenticate_channel(authentication, TeamRoles.is_channel_creator)

        self.assertEqual(user_id, authenticated_user.id)
        self.assertEqual(team_id, authenticated_user.team_id)
        self.assertEqual(channel_id, authenticated_user.channel_id)
        self.assertTrue(authenticated_user.is_channel_creator)

    def test_team_regular_member_authenticating_to_not_belonging_channel_throws_exception(self):
        user_id = 0
        team_id = 0
        channel_id = 0
        token = Authenticator.generate(user_id)
        authentication = MagicMock()
        authentication.token = token
        authentication.team_id = team_id
        authentication.channel_id = channel_id

        '''Mocked outputs'''
        user = User(user_id=user_id, token=token)
        team_user = PublicUser(user_id=user_id)
        team_user.team_role = TeamRoles.MEMBER.value
        team_user.team_id = team_id
        channel = Channel(channel_id=channel_id, team_id=team_id, name="test", creator=None)

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = user
        sys.modules["daos.users"].UserDatabaseClient.get_team_user_by_ids.return_value = team_user
        sys.modules["daos.users"].UserDatabaseClient.get_channel_user_by_ids.return_value = None
        sys.modules["daos.channels"].ChannelDatabaseClient.get_channel_by_id.return_value = channel
        self.assertRaises(NoPermissionsError, Authenticator.authenticate_channel, authentication)

    def test_admin_user_authenticates_to_every_channel(self):
        user_id = 0
        team_id = 0
        channel_id = 0
        token = Authenticator.generate(user_id)
        authentication = MagicMock()
        authentication.token = token
        authentication.team_id = team_id
        authentication.channel_id = channel_id

        '''Mocked outputs'''
        user = User(user_id=user_id, token=token, role=UserRoles.ADMIN.value)

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = user
        authenticated_user = Authenticator.authenticate_channel(authentication)

        self.assertEqual(user_id, authenticated_user.id)
        self.assertEqual(team_id, authenticated_user.team_id)
        self.assertEqual(channel_id, authenticated_user.channel_id)
        self.assertFalse(authenticated_user.is_channel_creator)
        self.assertEqual(UserRoles.ADMIN.value, authenticated_user.role)

    def test_authenticating_to_non_existing_channel_channel_throws_exception(self):
        user_id = 0
        team_id = 0
        channel_id = 0
        token = Authenticator.generate(user_id)
        authentication = MagicMock()
        authentication.token = token
        authentication.team_id = team_id
        authentication.channel_id = channel_id

        '''Mocked outputs'''
        user = User(user_id=user_id, token=token)
        team_user = PublicUser(user_id=user_id)
        team_user.team_role = TeamRoles.MEMBER.value
        team_user.team_id = team_id

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = user
        sys.modules["daos.users"].UserDatabaseClient.get_team_user_by_ids.return_value = team_user
        sys.modules["daos.users"].UserDatabaseClient.get_channel_user_by_ids.return_value = None
        sys.modules["daos.channels"].ChannelDatabaseClient.get_channel_by_id.return_value = None
        self.assertRaises(ChannelNotFoundError, Authenticator.authenticate_channel, authentication)
