from dtos.responses.clients import SuccessfulClientResponse
from models.constants import *
from utils.serializer import Jsonizable
from utils.responses import Response


class SuccessfulTeamResponse(SuccessfulClientResponse):

    def __init__(self, team, status):
        client = ActiveTeamOutput(team)
        super(SuccessfulTeamResponse, self).__init__(client, status)

    def json(self):
        return {
            "status": self.status,
            "team": self.client.json()
        }


class ActiveTeamOutput(Jsonizable):

    def __init__(self, team):
        self.id = team.id
        self.team_name = team.name
        self.picture = team.picture
        self.location = team.location
        self.description = team.description
        self.welcome_message = team.welcome_message

    def json(self):
        return vars(self)


class SuccessfulTeamsListResponse(Jsonizable, Response):

    def __init__(self, teams_list):
        self.teams = teams_list

    def json(self):
        return {
            "status": TeamResponseStatus.LIST.value,
            "teams": self.teams
        }

    def status_code(self):
        return StatusCode.OK.value


class SuccessfulForbiddenWordsList(Jsonizable, Response):

    def __init__(self, words_list):
        self.words_list = words_list

    def json(self):
        return {
            "status": TeamResponseStatus.LIST.value,
            "forbidden_words": self.words_list
        }

    def status_code(self):
        return StatusCode.OK.value


class SuccessfulTeamMessageResponse(Jsonizable, Response):

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


class BadRequestTeamMessageResponse(Jsonizable, Response):

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


class ForbiddenTeamMessageResponse(Jsonizable, Response):

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


class UnsuccessfulTeamMessageResponse(Jsonizable, Response):

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": TeamResponseStatus.ERROR.value,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.SERVER_ERROR.value


class NotFoundTeamMessageResponse(Jsonizable, Response):

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
