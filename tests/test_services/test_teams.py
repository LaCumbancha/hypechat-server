import unittest
from unittest.mock import MagicMock

from dtos.models.teams import Team, TeamUser
from dtos.responses.teams import BadRequestTeamMessageResponse
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
    batch_teams = []
    stored_teams = []
    batch_team_users = []
    stored_team_users = []


class UserServiceTestCase(unittest.TestCase):

    def tearDown(self):
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

