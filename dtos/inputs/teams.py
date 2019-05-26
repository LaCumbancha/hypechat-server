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

    def __init__(self, username, token, team_id, new_user_id, role):
        self.username = username
        self.token = token
        self.team_id = team_id
        self.user_addable_id = new_user_id
        try:
            self.role = TeamRoles[role].value
        except KeyError:
            raise RoleNotAvailableError(f"Role {role} is not defined.", TeamResponseStatus.ROLE_UNAVAILABLE.value)


class TeamInviteAcceptDTO:

    def __init__(self, username, token, team_id, invite_token):
        self.username = username
        self.token = token
        self.team_id = team_id
        self.invite_token = invite_token
