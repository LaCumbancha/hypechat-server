from models.constants import *
from utils.serializer import Jsonizable
from abc import abstractmethod


class SuccessfulClientResponse(Jsonizable):

    def __init__(self, client, status):
        self.client = client
        self.status = status

    def json(self):
        return {
            "status": self.status,
            "client": self.client.json()
        }

    def status_code(self):
        return StatusCode.OK.value


class SuccessfulUserResponse(SuccessfulClientResponse):

    def __init__(self, user):
        client = ActiveUserResponse(user)
        super(SuccessfulUserResponse, self).__init__(client, self._status(client))

    def json(self):
        return {
            "status": self.status,
            "user": self.client.json()
        }

    @classmethod
    def _status(cls, client):
        if client.online:
            return UserResponseStatus.ACTIVE.value
        else:
            return UserResponseStatus.OFFLINE.value


class SuccessfulTeamResponse(SuccessfulClientResponse):

    def __init__(self, team):
        client = ActiveTeamResponse(team)
        super(SuccessfulTeamResponse, self).__init__(client, TeamResponseStatus.CREATED.value)

    def json(self):
        return {
            "status": self.status,
            "team": self.client.json()
        }


class UnsuccessfulClientResponse(Jsonizable):

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": UserResponseStatus.ERROR.value,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.SERVER_ERROR.value


class ActiveUserResponse(Jsonizable):

    def __init__(self, user):
        self.id = user.user_id
        self.username = user.username
        self.email = user.email
        self.first_name = user.first_name
        self.last_name = user.last_name
        self.profile_pic = user.profile_pic
        self.token = user.auth_token
        self.online = user.online

    def json(self):
        return vars(self)


class ActiveTeamResponse(Jsonizable):

    def __init__(self, team):
        self.team_id = team.team_id
        self.team_name = team.team_name
        self.location = team.location
        self.description = team.description
        self.welcome_message = team.welcome_message

    def json(self):
        return vars(self)


class ClientAlreadyCreatedResponse(Jsonizable):

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": UserResponseStatus.ALREADY_REGISTERED.value,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.BAD_REQUEST.value


class WrongCredentialsResponse(Jsonizable):

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": UserResponseStatus.WRONG_CREDENTIALS.value,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.FORBIDDEN.value


class UserLoggedOutResponse(Jsonizable):

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": UserResponseStatus.LOGGED_OUT.value,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.OK.value
