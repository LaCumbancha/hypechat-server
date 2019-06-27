import unittest
from unittest.mock import MagicMock

from dtos.models.users import User, PublicUser
from dtos.models.teams import Team, TeamUser, TeamInvite, ForbiddenWord
from dtos.models.channels import Channel, ChannelCreator

from dtos.responses.teams import *
from dtos.responses.clients import *
from dtos.responses.channels import *

from exceptions.exceptions import UserNotFoundError
from sqlalchemy.exc import IntegrityError

'''Mocking environment properties'''
import sys

sys.modules["daos.database"] = MagicMock()
sys.modules["daos.users"] = MagicMock()
sys.modules["daos.teams"] = MagicMock()
sys.modules["services.bots"] = MagicMock()
sys.modules["services.users"] = MagicMock()
sys.modules["services.emails"] = MagicMock()
sys.modules["services.notifications"] = MagicMock()
sys.modules["models.authentication"] = MagicMock()
sys.modules["logging"].getLogger = MagicMock()

from services.teams import TeamService
mock = MagicMock()


class MockedTeamDatabase:
    batch_team = None
    stored_team = Team(team_id=0, name="TEST-0")

    batch_team_user = None
    stored_team_user = TeamUser(user_id=0, team_id=0, role=TeamRoles.MEMBER.value)

    batch_invites = 0
    stored_invites = 1

    batch_teams = []
    stored_teams = []
    batch_team_users = []
    stored_team_users = []
    batch_forbidden_words = []
    stored_forbidden_words = []


class UserServiceTestCase(unittest.TestCase):

    def tearDown(self):
        MockedTeamDatabase.batch_team = None
        MockedTeamDatabase.stored_team = Team(team_id=0, name="TEST-0")
        MockedTeamDatabase.batch_team_user = None
        MockedTeamDatabase.stored_team_user = TeamUser(user_id=0, team_id=0, role=TeamRoles.MEMBER.value)
        MockedTeamDatabase.batch_invites = 0
        MockedTeamDatabase.stored_invites = 1
        MockedTeamDatabase.batch_teams = []
        MockedTeamDatabase.stored_teams = []
        MockedTeamDatabase.batch_team_users = []
        MockedTeamDatabase.stored_team_users = []
        MockedTeamDatabase.batch_forbidden_words = []
        MockedTeamDatabase.stored_forbidden_words = []

    def test_create_team_with_name_in_use_returns_bad_request(self):
        data = MagicMock()

        def add_team(_):
            from tests.test_services import test_teams
            team = Team(team_id=0, name="TEST")
            MockedTeamDatabase.batch_teams += [team]
            return team

        def add_team_user(_):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_team_users += [TeamUser(user_id=0, team_id=0, role="CREATOR")]

        def commit():
            raise IntegrityError(mock, mock, mock)

        def rollback():
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_teams = []
            MockedTeamDatabase.batch_team_users = []

        sys.modules["daos.teams"].TeamDatabaseClient.add_team = MagicMock(side_effect=add_team)
        sys.modules["daos.teams"].TeamDatabaseClient.add_team_user = MagicMock(side_effect=add_team_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["daos.database"].DatabaseClient.rollback = MagicMock(side_effect=rollback)
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_name.return_value = MagicMock()

        response = TeamService.create_team(data)
        self.assertEqual(0, len(MockedTeamDatabase.batch_teams))
        self.assertEqual(0, len(MockedTeamDatabase.stored_teams))
        self.assertEqual(0, len(MockedTeamDatabase.batch_team_users))
        self.assertEqual(0, len(MockedTeamDatabase.stored_team_users))
        self.assertIsInstance(response, BadRequestTeamMessageResponse)

    def test_create_team_with_unknown_integrity_error_returns_unsuccessful(self):
        data = MagicMock()

        def add_team(_):
            from tests.test_services import test_teams
            team = Team(team_id=0, name="TEST")
            MockedTeamDatabase.batch_teams += [team]
            return team

        def add_team_user(_):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_team_users += [TeamUser(user_id=0, team_id=0, role="CREATOR")]

        def commit():
            raise IntegrityError(mock, mock, mock)

        def rollback():
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_teams = []
            MockedTeamDatabase.batch_team_users = []

        sys.modules["daos.teams"].TeamDatabaseClient.add_team = MagicMock(side_effect=add_team)
        sys.modules["daos.teams"].TeamDatabaseClient.add_team_user = MagicMock(side_effect=add_team_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["daos.database"].DatabaseClient.rollback = MagicMock(side_effect=rollback)
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_name.return_value = None

        response = TeamService.create_team(data)
        self.assertEqual(0, len(MockedTeamDatabase.batch_teams))
        self.assertEqual(0, len(MockedTeamDatabase.stored_teams))
        self.assertEqual(0, len(MockedTeamDatabase.batch_team_users))
        self.assertEqual(0, len(MockedTeamDatabase.stored_team_users))
        self.assertIsInstance(response, UnsuccessfulTeamMessageResponse)

    def test_create_team_with_correct_data_works_properly(self):
        data = MagicMock()

        def add_team(_):
            from tests.test_services import test_teams
            team = Team(team_id=0, name="TEST")
            MockedTeamDatabase.batch_teams += [team]
            return team

        def add_team_user(_):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_team_users += [TeamUser(user_id=0, team_id=0, role="CREATOR")]

        def commit():
            from tests.test_services import test_teams
            MockedTeamDatabase.stored_teams = MockedTeamDatabase.batch_teams
            MockedTeamDatabase.stored_team_users = MockedTeamDatabase.batch_team_users
            MockedTeamDatabase.batch_teams = []
            MockedTeamDatabase.batch_team_users = []

        sys.modules["daos.teams"].TeamDatabaseClient.add_team = MagicMock(side_effect=add_team)
        sys.modules["daos.teams"].TeamDatabaseClient.add_team_user = MagicMock(side_effect=add_team_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        response = TeamService.create_team(data)
        self.assertEqual(0, response.client.id)
        self.assertEqual(0, len(MockedTeamDatabase.batch_teams))
        self.assertEqual(1, len(MockedTeamDatabase.stored_teams))
        self.assertEqual(0, len(MockedTeamDatabase.batch_team_users))
        self.assertEqual(1, len(MockedTeamDatabase.stored_team_users))
        self.assertEqual(TeamResponseStatus.CREATED.value, response.status)
        self.assertIsInstance(response, SuccessfulTeamResponse)

    def test_add_nonexistent_user_throws_exception(self):
        data = MagicMock()

        '''Mocked outputs'''
        admin = User(user_id=0)

        sys.modules["models.authentication"].Authenticator.authenticate.return_value = admin
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = None

        self.assertRaises(UserNotFoundError, TeamService.add_user, data)

    def test_add_user_already_part_of_team_returns_bad_request(self):
        data = MagicMock()

        '''Mocked outputs'''
        admin = User(user_id=0)
        user = User(user_id=1)

        sys.modules["models.authentication"].Authenticator.authenticate.return_value = admin
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_user_in_team_by_ids = MagicMock()

        response = TeamService.add_user(data)
        self.assertEqual(TeamResponseStatus.ALREADY_REGISTERED.value, response.status)
        self.assertIsInstance(response, BadRequestTeamMessageResponse)

    def test_add_user_with_previous_invitation_delete_the_old_one_and_works_properly(self):
        data = MagicMock()

        '''Mocked outputs'''
        admin = User(user_id=0)
        user = User(user_id=1)

        def delete_invite(_):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_invites = 1

        def add_team_user(_):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_team_users += [TeamUser(user_id=0, team_id=0, role="CREATOR")]

        def commit():
            from tests.test_services import test_teams
            MockedTeamDatabase.stored_invites -= MockedTeamDatabase.batch_invites
            MockedTeamDatabase.stored_team_users = MockedTeamDatabase.batch_team_users
            MockedTeamDatabase.batch_invites = 0
            MockedTeamDatabase.batch_team_users = []

        sys.modules["models.authentication"].Authenticator.authenticate.return_value = admin
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_user_in_team_by_ids.return_value = None
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_invite = MagicMock()
        sys.modules["daos.teams"].TeamDatabaseClient.delete_invite = MagicMock(side_effect=delete_invite)
        sys.modules["daos.teams"].TeamDatabaseClient.add_team_user = MagicMock(side_effect=add_team_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        response = TeamService.add_user(data)
        self.assertEqual(0, len(MockedTeamDatabase.batch_team_users))
        self.assertEqual(1, len(MockedTeamDatabase.stored_team_users))
        self.assertEqual(0, MockedTeamDatabase.batch_invites)
        self.assertEqual(0, MockedTeamDatabase.stored_invites)
        self.assertEqual(TeamResponseStatus.ADDED.value, response.status)
        self.assertIsInstance(response, SuccessfulTeamMessageResponse)

    def test_add_user_with_unknown_integrity_error_returns_unsuccessful(self):
        data = MagicMock()

        '''Mocked outputs'''
        admin = User(user_id=0)
        user = User(user_id=1)

        def add_team_user(_):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_team_users += [TeamUser(user_id=0, team_id=0, role="CREATOR")]

        def commit():
            from tests.test_services import test_teams
            raise IntegrityError(mock, mock, mock)

        sys.modules["models.authentication"].Authenticator.authenticate.return_value = admin
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_user_in_team_by_ids.return_value = None
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_invite.return_value = None
        sys.modules["daos.teams"].TeamDatabaseClient.add_team_user = MagicMock(side_effect=add_team_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        response = TeamService.add_user(data)
        self.assertIsInstance(response, UnsuccessfulTeamMessageResponse)

    def test_invite_user_already_part_of_team_returns_bad_request(self):
        data = MagicMock()

        '''Mocked outputs'''
        mod = User(user_id=0)
        mod.team_id = 0
        user = TeamUser(user_id=1, team_id=0)

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = mod
        sys.modules["daos.teams"].TeamDatabaseClient.get_user_in_team_by_email.return_value = user

        response = TeamService.invite_user(data)
        self.assertEqual(TeamResponseStatus.ALREADY_REGISTERED.value, response.status)
        self.assertIsInstance(response, BadRequestTeamMessageResponse)

    def test_invite_user_already_invited_returns_bad_request(self):
        data = MagicMock()

        '''Mocked outputs'''
        mod = User(user_id=0)
        mod.team_id = 0

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = mod
        sys.modules["daos.teams"].TeamDatabaseClient.get_user_in_team_by_email.return_value = None
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_invite.return_value = MagicMock()

        response = TeamService.invite_user(data)
        self.assertEqual(TeamResponseStatus.ALREADY_INVITED.value, response.status)
        self.assertIsInstance(response, BadRequestTeamMessageResponse)

    def test_invite_user_with_unknown_integrity_error_returns_unsuccessful(self):
        data = MagicMock()

        '''Mocked outputs'''
        mod = User(user_id=0)
        mod.team_id = 0
        team = Team(team_id=0, name="TEST")

        def add_invite(_):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_invites = 1

        def commit():
            raise IntegrityError(mock, mock, mock)

        def rollback():
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_invites = 0

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = mod
        sys.modules["daos.teams"].TeamDatabaseClient.get_user_in_team_by_email.return_value = None
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_invite.return_value = None
        sys.modules["models.authentication"].Authenticator.generate_team_invitation.return_value = "TEST-INVITE"
        sys.modules["daos.teams"].TeamDatabaseClient.add_invite = MagicMock(side_effect=add_invite)
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_id.return_value = team
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["daos.database"].DatabaseClient.rollback = MagicMock(side_effect=rollback)

        response = TeamService.invite_user(data)
        self.assertEqual(0, MockedTeamDatabase.batch_invites)
        self.assertEqual(1, MockedTeamDatabase.stored_invites)
        self.assertIsInstance(response, UnsuccessfulTeamMessageResponse)

    def test_invite_user_with_correct_data_works_properly(self):
        data = MagicMock()

        '''Mocked outputs'''
        mod = User(user_id=0)
        mod.team_id = 0
        team = Team(team_id=0, name="TEST")

        def add_invite(_):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_invites = 1

        def commit():
            from tests.test_services import test_teams
            MockedTeamDatabase.stored_invites += MockedTeamDatabase.batch_invites
            MockedTeamDatabase.batch_invites = 0

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = mod
        sys.modules["daos.teams"].TeamDatabaseClient.get_user_in_team_by_email.return_value = None
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_invite.return_value = None
        sys.modules["models.authentication"].Authenticator.generate_team_invitation.return_value = "TEST-INVITE"
        sys.modules["daos.teams"].TeamDatabaseClient.add_invite = MagicMock(side_effect=add_invite)
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_id.return_value = team
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        response = TeamService.invite_user(data)
        self.assertEqual(0, MockedTeamDatabase.batch_invites)
        self.assertEqual(2, MockedTeamDatabase.stored_invites)
        self.assertEqual(TeamResponseStatus.INVITED.value, response.status)
        self.assertIsInstance(response, SuccessfulTeamMessageResponse)

    def test_accept_invite_not_found_returns_bad_request(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_invite_by_token.return_value = None

        response = TeamService.accept_invite(data)
        self.assertEqual(UserResponseStatus.WRONG_CREDENTIALS.value, response.status)
        self.assertIsInstance(response, BadRequestTeamMessageResponse)

    def test_accept_invite_found_works_properly(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        invite = TeamInvite(team_id=0, email="test@test", token="TEST-TOKEN")

        def delete_invite(_):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_invites = 1

        def add_team_user(_):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_team_users += [TeamUser(user_id=0, team_id=0, role="CREATOR")]

        def commit():
            from tests.test_services import test_teams
            MockedTeamDatabase.stored_invites += MockedTeamDatabase.batch_invites
            MockedTeamDatabase.stored_team_users = MockedTeamDatabase.batch_team_users
            MockedTeamDatabase.batch_invites = 0
            MockedTeamDatabase.batch_team_users = []

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_invite_by_token.return_value = invite
        sys.modules["daos.teams"].TeamDatabaseClient.delete_invite = MagicMock(side_effect=delete_invite)
        sys.modules["daos.teams"].TeamDatabaseClient.add_team_user = MagicMock(side_effect=add_team_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        response = TeamService.accept_invite(data)
        self.assertEqual(0, MockedTeamDatabase.batch_invites)
        self.assertEqual(2, MockedTeamDatabase.stored_invites)
        self.assertEqual(0, len(MockedTeamDatabase.batch_team_users))
        self.assertEqual(1, len(MockedTeamDatabase.stored_team_users))
        self.assertIsInstance(response, SuccessfulTeamMessageResponse)

    def test_accept_invite_with_unknown_integrity_error_returns_bad_request(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        invite = TeamInvite(team_id=0, email="test@test", token="TEST-TOKEN")

        def delete_invite(_):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_invites = 1

        def add_team_user(_):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_team_users += [TeamUser(user_id=0, team_id=0, role="CREATOR")]

        def commit():
            from tests.test_services import test_teams
            raise IntegrityError(mock, mock, mock)

        def rollback():
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_invites = 0
            MockedTeamDatabase.batch_team_users = []

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_invite_by_token.return_value = invite
        sys.modules["daos.teams"].TeamDatabaseClient.delete_invite = MagicMock(side_effect=delete_invite)
        sys.modules["daos.teams"].TeamDatabaseClient.add_team_user = MagicMock(side_effect=add_team_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["daos.database"].DatabaseClient.rollback = MagicMock(side_effect=rollback)

        response = TeamService.accept_invite(data)
        self.assertEqual(0, MockedTeamDatabase.batch_invites)
        self.assertEqual(1, MockedTeamDatabase.stored_invites)
        self.assertEqual(0, len(MockedTeamDatabase.batch_team_users))
        self.assertEqual(0, len(MockedTeamDatabase.stored_team_users))
        self.assertIsInstance(response, UnsuccessfulTeamMessageResponse)

    def test_get_team_users_with_empty_list_works_properly(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        members = []

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_all_team_users_by_team_id.return_value = members

        response = TeamService.team_users(data)
        self.assertEqual(UserResponseStatus.LIST.value, response.json().get("status"))
        self.assertEqual(0, len(response.users))
        self.assertIsInstance(response, SuccessfulUsersListResponse)

    def test_get_team_users_with_non_empty_list_works_properly(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0

        member1 = PublicUser(user_id=1)
        member1.team_id = 0
        member1.team_role = TeamRoles.MEMBER.value
        member2 = PublicUser(user_id=2)
        member2.team_id = 0
        member2.team_role = TeamRoles.MEMBER.value
        members = [member1, member2]

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_all_team_users_by_team_id.return_value = members

        response = TeamService.team_users(data)
        self.assertEqual(UserResponseStatus.LIST.value, response.json().get("status"))
        self.assertEqual(2, len(response.users))
        self.assertEqual(1, response.users[0].get("id"))
        self.assertEqual(TeamRoles.MEMBER.value, response.users[0].get("team_role"))
        self.assertEqual(2, response.users[1].get("id"))
        self.assertEqual(TeamRoles.MEMBER.value, response.users[1].get("team_role"))
        self.assertIsInstance(response, SuccessfulUsersListResponse)

    def test_get_team_channels_with_empty_list_works_properly(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        channels = []

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_all_team_channels_by_team_id.return_value = channels

        response = TeamService.team_channels(data)
        self.assertEqual(UserResponseStatus.LIST.value, response.json().get("status"))
        self.assertEqual(0, len(response.channels))
        self.assertIsInstance(response, SuccessfulChannelsListResponse)

    def test_get_team_channels_with_non_empty_list_works_properly(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0

        channel1 = Channel(channel_id=1, creator=ChannelCreator(user_id=0), name="TEST-1", team_id=0)
        channel2 = Channel(channel_id=2, creator=ChannelCreator(user_id=0), name="TEST-2", team_id=0)
        channels = [channel1, channel2]

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_all_team_channels_by_team_id.return_value = channels

        response = TeamService.team_channels(data)
        self.assertEqual(UserResponseStatus.LIST.value, response.json().get("status"))
        self.assertEqual(2, len(response.channels))
        self.assertEqual(1, response.channels[0].get("id"))
        self.assertEqual("TEST-1", response.channels[0].get("name"))
        self.assertEqual(2, response.channels[1].get("id"))
        self.assertEqual("TEST-2", response.channels[1].get("name"))
        self.assertIsInstance(response, SuccessfulChannelsListResponse)

    def test_team_user_profile_returns_bad_request_when_user_service_returns_none(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        user.team_role = TeamRoles.MEMBER.value

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["services.users"].UserService.team_user_profile.return_value = None

        response = TeamService.team_user_profile(data)
        self.assertEqual(TeamResponseStatus.USER_NOT_MEMBER.value, response.status)
        self.assertIsInstance(response, BadRequestTeamMessageResponse)

    def test_delete_user_not_found_returns_not_found_response(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_user_in_team_by_ids.return_value = None

        response = TeamService.delete_user(data)
        self.assertEqual(UserResponseStatus.USER_NOT_FOUND.value, response.status)
        self.assertIsInstance(response, NotFoundTeamMessageResponse)

    def test_delete_user_with_higher_role_returns_bad_request(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        user.team_role = TeamRoles.MEMBER.value
        delete_user = TeamUser(user_id=1, team_id=0, role=TeamRoles.MODERATOR.value)

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_user_in_team_by_ids.return_value = delete_user

        response = TeamService.delete_user(data)
        self.assertEqual(TeamResponseStatus.NOT_ENOUGH_PERMISSIONS.value, response.status)
        self.assertIsInstance(response, ForbiddenTeamMessageResponse)

    def test_delete_user_with_unknown_integrity_error_returns_unsuccessful(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        user.team_role = TeamRoles.MODERATOR.value
        delete_user = TeamUser(user_id=1, team_id=0, role=TeamRoles.MEMBER.value)

        def delete_team_user(_):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_team_users = 1

        def commit():
            raise IntegrityError(mock, mock, mock)

        def rollback():
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_team_users = 0

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_user_in_team_by_ids.return_value = delete_user
        sys.modules["daos.teams"].TeamDatabaseClient.delete_team_user = MagicMock(side_effect=delete_team_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["daos.database"].DatabaseClient.rollback = MagicMock(side_effect=rollback)

        response = TeamService.delete_user(data)
        self.assertIsInstance(response, UnsuccessfulTeamMessageResponse)

    def test_delete_user_without_database_errors_works_properly(self):
        data = MagicMock()
        MockedTeamDatabase.batch_team_users = 0
        MockedTeamDatabase.stored_team_users = 1

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        user.team_role = TeamRoles.MODERATOR.value
        delete_user = TeamUser(user_id=1, team_id=0, role=TeamRoles.MEMBER.value)

        def delete_team_user(_):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_team_users += 1

        def commit():
            from tests.test_services import test_teams
            MockedTeamDatabase.stored_team_users -= MockedTeamDatabase.batch_team_users
            MockedTeamDatabase.batch_team_users = 0

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_user_in_team_by_ids.return_value = delete_user
        sys.modules["daos.teams"].TeamDatabaseClient.delete_team_user = MagicMock(side_effect=delete_team_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        response = TeamService.delete_user(data)
        self.assertEqual(0, MockedTeamDatabase.batch_team_users)
        self.assertEqual(0, MockedTeamDatabase.stored_team_users)
        self.assertEqual(TeamResponseStatus.REMOVED.value, response.status)
        self.assertIsInstance(response, SuccessfulTeamMessageResponse)

    def test_change_role_to_creator_returns_bad_request(self):
        data = MagicMock()
        data.new_role = TeamRoles.CREATOR.value

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user

        response = TeamService.change_role(data)
        self.assertEqual(TeamResponseStatus.ROLE_UNAVAILABLE.value, response.status)
        self.assertIsInstance(response, BadRequestTeamMessageResponse)

    def test_change_role_to_not_member_user_returns_bad_request(self):
        data = MagicMock()
        data.new_role = TeamRoles.MODERATOR.value

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_user_in_team_by_ids.return_value = None

        response = TeamService.change_role(data)
        self.assertEqual(TeamResponseStatus.USER_NOT_MEMBER.value, response.status)
        self.assertIsInstance(response, BadRequestTeamMessageResponse)

    def test_change_role_with_database_error_returns_unsuccessful(self):
        data = MagicMock()
        data.new_role = TeamRoles.MODERATOR.value

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        user_to_change = TeamUser(user_id=1, team_id=0, role=TeamRoles.MEMBER.value)

        def update_team_user(team_user):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_team_user = team_user

        def commit():
            raise IntegrityError(mock, mock, mock)

        def rollback():
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_team_user = None

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_user_in_team_by_ids.return_value = user_to_change
        sys.modules["daos.teams"].TeamDatabaseClient.update_team_user = MagicMock(side_effect=update_team_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["daos.database"].DatabaseClient.rollback = MagicMock(side_effect=rollback)

        response = TeamService.change_role(data)
        self.assertIsNone(MockedTeamDatabase.batch_team_user)
        self.assertEqual(TeamRoles.MEMBER.value, MockedTeamDatabase.stored_team_user.role)
        self.assertIsInstance(response, UnsuccessfulTeamMessageResponse)

    def test_change_role_without_database_error_works_properly(self):
        data = MagicMock()
        data.new_role = TeamRoles.MODERATOR.value

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        user_to_change = TeamUser(user_id=1, team_id=0, role=TeamRoles.MEMBER.value)

        def update_team_user(team_user):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_team_user = team_user

        def commit():
            MockedTeamDatabase.stored_team_user = MockedTeamDatabase.batch_team_user
            MockedTeamDatabase.batch_team_user = None

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_user_in_team_by_ids.return_value = user_to_change
        sys.modules["daos.teams"].TeamDatabaseClient.update_team_user = MagicMock(side_effect=update_team_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        response = TeamService.change_role(data)
        self.assertIsNone(MockedTeamDatabase.batch_team_user)
        self.assertEqual(TeamRoles.MODERATOR.value, MockedTeamDatabase.stored_team_user.role)
        self.assertIsInstance(response, SuccessfulTeamMessageResponse)

    def test_leave_team_with_database_error_returns_unsuccessful(self):
        data = MagicMock()
        MockedTeamDatabase.batch_team_users = 0
        MockedTeamDatabase.stored_team_users = 1

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        delete_user = TeamUser(user_id=0, team_id=0)

        def delete_team_user(_):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_team_users = 1

        def commit():
            raise IntegrityError(mock, mock, mock)

        def rollback():
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_team_users = 0

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_user_in_team_by_ids.return_value = delete_user
        sys.modules["daos.teams"].TeamDatabaseClient.delete_team_user = MagicMock(side_effect=delete_team_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["daos.database"].DatabaseClient.rollback = MagicMock(side_effect=rollback)

        response = TeamService.leave_team(data)
        self.assertEqual(0, MockedTeamDatabase.batch_team_users)
        self.assertEqual(1, MockedTeamDatabase.stored_team_users)
        self.assertIsInstance(response, UnsuccessfulTeamMessageResponse)

    def test_leave_team_without_database_error_works_properly(self):
        data = MagicMock()
        MockedTeamDatabase.batch_team_users = 0
        MockedTeamDatabase.stored_team_users = 1

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        delete_user = TeamUser(user_id=0, team_id=0)

        def delete_team_user(_):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_team_users = 1

        def commit():
            from tests.test_services import test_teams
            MockedTeamDatabase.stored_team_users -= MockedTeamDatabase.batch_team_users
            MockedTeamDatabase.batch_team_users = 0

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_user_in_team_by_ids.return_value = delete_user
        sys.modules["daos.teams"].TeamDatabaseClient.delete_team_user = MagicMock(side_effect=delete_team_user)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        response = TeamService.leave_team(data)
        self.assertEqual(0, MockedTeamDatabase.batch_team_users)
        self.assertEqual(0, MockedTeamDatabase.stored_team_users)
        self.assertEqual(TeamResponseStatus.REMOVED.value, response.status)
        self.assertIsInstance(response, SuccessfulTeamMessageResponse)

    def test_update_team_with_used_name_returns_bad_request(self):
        data = MagicMock()
        data.updated_team = {"team_name": "TEST"}

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        team = Team(team_id=0, name="TEST-0")

        def update_team(team):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_team = team

        def commit():
            raise IntegrityError(mock, mock, mock)

        def rollback():
            MockedTeamDatabase.batch_team = None

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_id.return_value = team
        sys.modules["daos.teams"].TeamDatabaseClient.update_team = MagicMock(side_effect=update_team)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["daos.database"].DatabaseClient.rollback = MagicMock(side_effect=rollback)
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_name.return_value = MagicMock()

        response = TeamService.update_information(data)
        self.assertIsNone(MockedTeamDatabase.batch_team)
        self.assertEqual("TEST-0", MockedTeamDatabase.stored_team.name)
        self.assertEqual(TeamResponseStatus.ALREADY_REGISTERED.value, response.status)
        self.assertIsInstance(response, BadRequestTeamMessageResponse)

    def test_update_team_with_database_error_returns_unsuccessful(self):
        data = MagicMock()
        data.updated_team = {"team_name": "TEST"}

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        team = Team(team_id=0, name="TEST-0")

        def update_team(team):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_team = team

        def commit():
            raise IntegrityError(mock, mock, mock)

        def rollback():
            MockedTeamDatabase.batch_team = None

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_id.return_value = team
        sys.modules["daos.teams"].TeamDatabaseClient.update_team = MagicMock(side_effect=update_team)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["daos.database"].DatabaseClient.rollback = MagicMock(side_effect=rollback)
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_name.return_value = None

        response = TeamService.update_information(data)
        self.assertIsNone(MockedTeamDatabase.batch_team)
        self.assertEqual("TEST-0", MockedTeamDatabase.stored_team.name)
        self.assertIsInstance(response, UnsuccessfulTeamMessageResponse)

    def test_update_team_without_database_error_works_properly(self):
        data = MagicMock()
        data.updated_team = {"team_name": "TEST-1"}

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        user.team_role = TeamRoles.MODERATOR.value
        team = Team(team_id=0, name="TEST-0")

        def update_team(team):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_team = team
            return team

        def commit():
            from tests.test_services import test_teams
            MockedTeamDatabase.stored_team = MockedTeamDatabase.batch_team
            MockedTeamDatabase.batch_team = None

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_id.return_value = team
        sys.modules["daos.teams"].TeamDatabaseClient.update_team = MagicMock(side_effect=update_team)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        response = TeamService.update_information(data)
        self.assertIsNone(MockedTeamDatabase.batch_team)
        self.assertEqual("TEST-1", MockedTeamDatabase.stored_team.name)
        self.assertEqual(TeamResponseStatus.UPDATED.value, response.status)
        self.assertIsInstance(response, SuccessfulTeamResponse)

    def test_search_team_users_with_empty_list_works_properly(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        members = []

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_all_team_users_by_likely_name.return_value = members

        response = TeamService.search_users(data)
        self.assertEqual(UserResponseStatus.LIST.value, response.json().get("status"))
        self.assertEqual(0, len(response.users))
        self.assertIsInstance(response, SuccessfulUsersListResponse)

    def test_search_team_users_with_non_empty_list_works_properly(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0

        member1 = PublicUser(user_id=1)
        member1.team_id = 0
        member1.team_role = TeamRoles.MEMBER.value
        member2 = PublicUser(user_id=2)
        member2.team_id = 0
        member2.team_role = TeamRoles.MEMBER.value
        members = [member1, member2]

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_all_team_users_by_likely_name.return_value = members

        response = TeamService.search_users(data)
        self.assertEqual(UserResponseStatus.LIST.value, response.json().get("status"))
        self.assertEqual(2, len(response.users))
        self.assertEqual(1, response.users[0].get("id"))
        self.assertEqual(TeamRoles.MEMBER.value, response.users[0].get("team_role"))
        self.assertEqual(2, response.users[1].get("id"))
        self.assertEqual(TeamRoles.MEMBER.value, response.users[1].get("team_role"))
        self.assertIsInstance(response, SuccessfulUsersListResponse)

    def test_delete_team_with_unknown_integrity_error_returns_unsuccessful(self):
        data = MagicMock()
        MockedTeamDatabase.batch_teams = 0
        MockedTeamDatabase.stored_teams = 1

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        user.team_role = TeamRoles.MODERATOR.value
        team = Team(team_id=0, name="TEST-0")

        def delete_team(_):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_teams = 1

        def commit():
            raise IntegrityError(mock, mock, mock)

        def rollback():
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_teams = 0

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_id.return_value = team
        sys.modules["daos.teams"].TeamDatabaseClient.delete_team = MagicMock(side_effect=delete_team)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["daos.database"].DatabaseClient.rollback = MagicMock(side_effect=rollback)

        response = TeamService.delete_team(data)
        self.assertEqual(0, MockedTeamDatabase.batch_teams)
        self.assertEqual(1, MockedTeamDatabase.stored_teams)
        self.assertIsInstance(response, UnsuccessfulTeamMessageResponse)

    def test_delete_team_without_unknown_integrity_works_properly(self):
        data = MagicMock()
        MockedTeamDatabase.batch_teams = 0
        MockedTeamDatabase.stored_teams = 1

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        user.team_role = TeamRoles.MODERATOR.value
        team = Team(team_id=0, name="TEST-0")

        def delete_team(_):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_teams = 1

        def commit():
            from tests.test_services import test_teams
            MockedTeamDatabase.stored_teams -= MockedTeamDatabase.batch_teams
            MockedTeamDatabase.batch_teams = 0

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_id.return_value = team
        sys.modules["daos.teams"].TeamDatabaseClient.delete_team = MagicMock(side_effect=delete_team)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        response = TeamService.delete_team(data)
        self.assertEqual(0, MockedTeamDatabase.batch_teams)
        self.assertEqual(0, MockedTeamDatabase.stored_teams)
        self.assertEqual(TeamResponseStatus.REMOVED.value, response.status)
        self.assertIsInstance(response, SuccessfulTeamMessageResponse)

    def test_add_forbidden_word_already_registered_returns_bad_request(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        user.team_role = TeamRoles.MODERATOR.value

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_forbidden_word_by_word.return_value = MagicMock()

        response = TeamService.add_forbidden_word(data)
        self.assertEqual(TeamResponseStatus.ALREADY_REGISTERED.value, response.status)
        self.assertIsInstance(response, BadRequestTeamMessageResponse)

    def test_add_new_forbidden_with_unknown_integrity_error_returns_unsuccessful(self):
        data = MagicMock()
        data.word = "TEST"

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        user.team_role = TeamRoles.MODERATOR.value

        def add_forbidden_word(forbidden_word):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_forbidden_words += [forbidden_word]

        def commit():
            raise IntegrityError(mock, mock, mock)

        def rollback():
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_forbidden_words = []

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_forbidden_word_by_word.return_value = None
        sys.modules["daos.teams"].TeamDatabaseClient.add_forbidden_word = MagicMock(side_effect=add_forbidden_word)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["daos.database"].DatabaseClient.rollback = MagicMock(side_effect=rollback)

        response = TeamService.add_forbidden_word(data)
        self.assertEqual(0, len(MockedTeamDatabase.batch_forbidden_words))
        self.assertEqual(0, len(MockedTeamDatabase.stored_forbidden_words))
        self.assertIsInstance(response, UnsuccessfulTeamMessageResponse)

    def test_add_new_forbidden_without_unknown_integrity_error_returns_unsuccessful(self):
        data = MagicMock()
        data.word = "TEST"

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        user.team_role = TeamRoles.MODERATOR.value

        def add_forbidden_word(forbidden_word):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_forbidden_words += [forbidden_word]

        def commit():
            from tests.test_services import test_teams
            MockedTeamDatabase.stored_forbidden_words += MockedTeamDatabase.batch_forbidden_words
            MockedTeamDatabase.batch_forbidden_words = []

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_forbidden_word_by_word.return_value = None
        sys.modules["daos.teams"].TeamDatabaseClient.add_forbidden_word = MagicMock(side_effect=add_forbidden_word)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        response = TeamService.add_forbidden_word(data)
        self.assertEqual(0, len(MockedTeamDatabase.batch_forbidden_words))
        self.assertEqual(1, len(MockedTeamDatabase.stored_forbidden_words))
        self.assertEqual(TeamResponseStatus.ADDED.value, response.status)
        self.assertIsInstance(response, SuccessfulTeamMessageResponse)

    def test_get_forbidden_words_with_empty_list_works_properly(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        words = []

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_forbidden_words_from_team.return_value = words

        response = TeamService.forbidden_words(data)
        self.assertEqual(TeamResponseStatus.LIST.value, response.json().get("status"))
        self.assertEqual(0, len(response.words))
        self.assertIsInstance(response, SuccessfulForbiddenWordsList)

    def test_get_forbidden_words_with_non_empty_list_works_properly(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0

        word1 = ForbiddenWord(word="TEST-1", team_id=0)
        word2 = ForbiddenWord(word="TEST-2", team_id=0)
        words = [word1, word2]

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_forbidden_words_from_team.return_value = words

        response = TeamService.forbidden_words(data)
        self.assertEqual(TeamResponseStatus.LIST.value, response.json().get("status"))
        self.assertEqual(2, len(response.words))
        self.assertEqual("TEST-1", response.words[0].get("word"))
        self.assertEqual("TEST-2", response.words[1].get("word"))
        self.assertIsInstance(response, SuccessfulForbiddenWordsList)

    def test_delete_forbidden_word_not_found_returns_bad_request_response(self):
        data = MagicMock()

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        user.team_role = TeamRoles.MODERATOR.value

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_forbidden_word_by_id.return_value = None

        response = TeamService.delete_forbidden_word(data)
        self.assertEqual(TeamResponseStatus.NOT_FOUND.value, response.status)
        self.assertIsInstance(response, BadRequestTeamMessageResponse)

    def test_delete_forbidden_word_with_unknown_integrity_error_returns_unsuccessful(self):
        data = MagicMock()
        MockedTeamDatabase.batch_forbidden_words = 0
        MockedTeamDatabase.stored_forbidden_words = 1

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        user.team_role = TeamRoles.MODERATOR.value
        word = ForbiddenWord(word="TEST", team_id=0)

        def delete_word(_):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_forbidden_words = 1

        def commit():
            raise IntegrityError(mock, mock, mock)

        def rollback():
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_forbidden_words = 0

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_forbidden_word_by_id.return_value = word
        sys.modules["daos.teams"].TeamDatabaseClient.delete_forbidden_word = MagicMock(side_effect=delete_word)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["daos.database"].DatabaseClient.rollback = MagicMock(side_effect=rollback)

        response = TeamService.delete_forbidden_word(data)
        self.assertEqual(0, MockedTeamDatabase.batch_forbidden_words)
        self.assertEqual(1, MockedTeamDatabase.stored_forbidden_words)
        self.assertIsInstance(response, UnsuccessfulTeamMessageResponse)

    def test_delete_forbidden_word_without_unknown_integrity_error_returns_unsuccessful(self):
        data = MagicMock()
        MockedTeamDatabase.batch_forbidden_words = 0
        MockedTeamDatabase.stored_forbidden_words = 1

        '''Mocked outputs'''
        user = User(user_id=0)
        user.team_id = 0
        user.team_role = TeamRoles.MODERATOR.value
        word = ForbiddenWord(word="TEST", team_id=0)

        def delete_word(_):
            from tests.test_services import test_teams
            MockedTeamDatabase.batch_forbidden_words = 1

        def commit():
            from tests.test_services import test_teams
            MockedTeamDatabase.stored_forbidden_words -= MockedTeamDatabase.batch_forbidden_words
            MockedTeamDatabase.batch_forbidden_words = 0

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.teams"].TeamDatabaseClient.get_forbidden_word_by_id.return_value = word
        sys.modules["daos.teams"].TeamDatabaseClient.delete_forbidden_word = MagicMock(side_effect=delete_word)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        response = TeamService.delete_forbidden_word(data)
        self.assertEqual(0, MockedTeamDatabase.batch_forbidden_words)
        self.assertEqual(0, MockedTeamDatabase.stored_forbidden_words)
        self.assertEqual(TeamResponseStatus.REMOVED.value, response.status)
        self.assertIsInstance(response, SuccessfulTeamMessageResponse)
