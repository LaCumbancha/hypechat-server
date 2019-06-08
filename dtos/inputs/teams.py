from models.constants import TeamRoles, TeamResponseStatus
from exceptions.exceptions import RoleNotAvailableError
from dtos.inputs.users import AuthenticationDTO


class TeamAuthenticationDTO:

    def __init__(self, token, team_id):
        self.token = token
        self.team_id = team_id


class NewTeamDTO:

    def __init__(self, token, team_name, picture, location, description, welcome_message):
        self.token = token
        self.team_name = team_name
        self.picture = picture
        self.location = location
        self.description = description
        self.welcome_message = welcome_message


class TeamInviteDTO:

    def __init__(self, token, team_id, email):
        self.authentication = TeamAuthenticationDTO(token, team_id)
        self.email = email


class TeamInviteAcceptDTO:

    def __init__(self, token, team_id, invite_token):
        self.token = token
        self.team_id = team_id
        self.invite_token = invite_token


class ChangeRoleDTO:

    def __init__(self, token, team_id, user_id, new_role):
        self.authentication = TeamAuthenticationDTO(token, team_id)
        self.user_id = user_id
        try:
            self.new_role = TeamRoles[new_role].value
        except KeyError:
            raise RoleNotAvailableError(f"Role {new_role} is not defined.", TeamResponseStatus.ROLE_UNAVAILABLE.value)


class DeleteUserTeamDTO:

    def __init__(self, token, team_id, delete_id):
        self.authentication = TeamAuthenticationDTO(token, team_id)
        self.delete_id = delete_id


class TeamUpdateDTO:

    def __init__(self, token, team_id, updated_team):
        self.authentication = TeamAuthenticationDTO(token, team_id)
        self.updated_team = updated_team


class SearchUsersDTO:

    def __init__(self, token, team_id, searched_username):
        self.authentication = TeamAuthenticationDTO(token, team_id)
        self.searched_username = searched_username


class SearchUserByIdDTO:

    def __init__(self, token, team_id, user_id):
        self.authentication = TeamAuthenticationDTO(token, team_id)
        self.user_id = user_id
