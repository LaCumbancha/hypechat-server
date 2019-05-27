from models.constants import TeamRoles, TeamResponseStatus
from exceptions.exceptions import RoleNotAvailableError
from dtos.inputs.users import AuthenticationDTO


class TeamAuthenticationDTO:

    def __init__(self, username, token, team_id):
        self.username = username
        self.token = token
        self.team_id = team_id


class NewTeamDTO:

    def __init__(self, username, token, team_name, location, description, welcome_message):
        self.authentication = AuthenticationDTO(username, token)
        self.team_name = team_name
        self.location = location
        self.description = description
        self.welcome_message = welcome_message


class TeamInviteDTO:

    def __init__(self, username, token, team_id, email):
        self.authentication = TeamAuthenticationDTO(username, token, team_id)
        self.email = email


class TeamInviteAcceptDTO:

    def __init__(self, username, token, team_id, invite_token):
        self.authentication = AuthenticationDTO(username, token)
        self.team_id = team_id
        self.invite_token = invite_token


class ChangeRoleDTO:

    def __init__(self, username, token, team_id, user_id, new_role):
        self.authentication = TeamAuthenticationDTO(username, token, team_id)
        self.user_id = user_id
        self.new_role = new_role
