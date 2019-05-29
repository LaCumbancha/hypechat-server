from dtos.responses.clients import SuccessfulClientResponse
from models.constants import *
from utils.serializer import Jsonizable
from utils.responses import Response


class SuccessfulTeamCreatedResponse(SuccessfulClientResponse):

    def __init__(self, team):
        client = ActiveTeamOutput(team)
        super(SuccessfulTeamCreatedResponse, self).__init__(client, TeamResponseStatus.CREATED.value)

    def json(self):
        return {
            "status": self.status,
            "team": self.client.json()
        }


class ActiveTeamOutput(Jsonizable):

    def __init__(self, team):
        self.team_id = team.team_id
        self.team_name = team.team_name
        self.location = team.location
        self.description = team.description
        self.welcome_message = team.welcome_message

    def json(self):
        return vars(self)


class SuccessfulTeamsListResponse(Jsonizable, Response):

    def __init__(self, teams_list):
        self.teams_list = teams_list

    def json(self):
        return {
            "status": TeamResponseStatus.LIST.value,
            "teams": self.teams_list
        }

    def status_code(self):
        return StatusCode.OK.value


class SuccessfulTeamResponse(Jsonizable, Response):

    def __init__(self, message, status):
        self.status = status
        self.message = message

    def json(self):
        return {
            "status": self.status,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.OK.value


class BadRequestTeamResponse(Jsonizable, Response):

    def __init__(self, message, status):
        self.status = status
        self.message = message

    def json(self):
        return {
            "status": self.status,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.BAD_REQUEST.value


class ForbiddenTeamResponse(Jsonizable, Response):

    def __init__(self, message, status):
        self.status = status
        self.message = message

    def json(self):
        return {
            "status": self.status,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.FORBIDDEN.value


class UnsuccessfulTeamResponse(Jsonizable, Response):

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": TeamResponseStatus.ERROR.value,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.SERVER_ERROR.value


class NotFoundTeamResponse(Jsonizable, Response):

    def __init__(self, message, status):
        self.status = status
        self.message = message

    def json(self):
        return {
            "status": self.status,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.NOT_FOUND.value
