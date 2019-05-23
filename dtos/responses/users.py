from models.constants import *
from utils.serializer import Jsonizable


class SuccessfulUserResponse(Jsonizable):

    def __init__(self, user):
        self.user = ActiveUserResponse(user)
        self.status = self._status()

    def json(self):
        return {
            "status": self.status,
            "user": self.user.json()
        }

    def _status(self):
        if self.user.online:
            return UserResponseStatus.ACTIVE.value
        else:
            return UserResponseStatus.OFFLINE.value

    def status_code(self):
        return StatusCode.OK.value


class UnsuccessfulUserResponse(Jsonizable):

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


class UserAlreadyCreatedResponse(Jsonizable):

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
