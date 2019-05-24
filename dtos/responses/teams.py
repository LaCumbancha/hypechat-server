from models.constants import *
from utils.serializer import Jsonizable


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
