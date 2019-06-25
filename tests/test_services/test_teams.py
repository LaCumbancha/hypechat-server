import unittest
from unittest.mock import MagicMock

from dtos.models.users import User, PublicUser
from dtos.models.teams import Team, TeamUser, TeamInvite
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
    batch_invites = 0
    stored_invites = 1

    batch_teams = []
    stored_teams = []
    batch_team_users = []
    stored_team_users = []


class UserServiceTestCase(unittest.TestCase):

    def tearDown(self):
        MockedTeamDatabase.batch_invites = 0
        MockedTeamDatabase.stored_invites = 1
        MockedTeamDatabase.batch_teams = []
        MockedTeamDatabase.stored_teams = []
        MockedTeamDatabase.batch_team_users = []
        MockedTeamDatabase.stored_team_users = []

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
        user = User(user_id=1)

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
