from models.constants import TeamRoles, TeamResponseStatus
from exceptions.exceptions import RoleNotAvailableError


class NewTeamDTO:

    def __init__(self, username, token, team_name, location, description, welcome_message):
        self.username = username
        self.token = token
        self.team_name = team_name
        self.location = location
        self.description = description
        self.welcome_message = welcome_message


class TeamInviteDTO:

    def __init__(self, username, token, team_id, email):
        self.username = username
        self.token = token
        self.team_id = team_id
        self.email = email


class TeamInviteAcceptDTO:

    def __init__(self, username, token, team_id, invite_token):
        self.username = username
        self.token = token
        self.team_id = team_id
        self.invite_token = invite_token
