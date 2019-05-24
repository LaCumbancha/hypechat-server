from dtos.responses.clients import SuccessfulClientResponse
from models.constants import *
from utils.serializer import Jsonizable


class SuccessfulTeamResponse(SuccessfulClientResponse):

    def __init__(self, team):
        client = ActiveTeamResponse(team)
        super(SuccessfulTeamResponse, self).__init__(client, TeamResponseStatus.CREATED.value)

    def json(self):
        return {
            "status": self.status,
            "team": self.client.json()
        }


class ActiveTeamResponse(Jsonizable):

    def __init__(self, team):
        self.team_id = team.team_id
        self.team_name = team.team_name
        self.location = team.location
        self.description = team.description
        self.welcome_message = team.welcome_message

    def json(self):
        return vars(self)


class SuccessfulUserAddedResponse(Jsonizable):

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": TeamResponseStatus.USER_ADDED.value,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.OK.value


class TeamAlreadyCreatedResponse(Jsonizable):

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": TeamResponseStatus.ALREADY_REGISTERED.value,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.BAD_REQUEST.value


class RelationAlreadyCreatedResponse(Jsonizable):

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": TeamResponseStatus.ALREADY_REGISTERED.value,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.BAD_REQUEST.value


class UnsuccessfulTeamResponse(Jsonizable):

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": UserResponseStatus.ERROR.value,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.SERVER_ERROR.value
