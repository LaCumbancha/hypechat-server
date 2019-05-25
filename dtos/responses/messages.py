from models.constants import *
from utils.serializer import Jsonizable


class SuccessfulMessageResponse(Jsonizable):

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": MessageResponseStatus.SENT.value,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.OK.value


class UnsuccessfulMessageResponse(Jsonizable):

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": MessageResponseStatus.ERROR.value,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.SERVER_ERROR.value
