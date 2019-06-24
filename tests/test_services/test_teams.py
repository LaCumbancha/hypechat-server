import unittest
from unittest.mock import MagicMock

from dtos.models.users import User
from dtos.models.teams import Team, TeamUser
from dtos.responses.teams import *
from exceptions.exceptions import UserNotFoundError
from sqlalchemy.exc import IntegrityError

'''Mocking environment properties'''
import sys
sys.modules["daos.database"] = MagicMock()
sys.modules["daos.users"] = MagicMock()
sys.modules["daos.teams"] = MagicMock()
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
        admin = User(user_id=0)

        sys.modules["models.authentication"].Authenticator.authenticate.return_value = admin
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = None

        self.assertRaises(UserNotFoundError, TeamService.add_user, data)

    def test_add_user_already_part_of_team_returns_bad_request(self):
        data = MagicMock()
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
