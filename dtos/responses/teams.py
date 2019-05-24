from models.constants import *


class SuccessfulUserAddedResponse:

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": TeamResponseStatus.USER_ADDED.value,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.OK.value
