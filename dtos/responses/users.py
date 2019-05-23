from models.constants import *
from utils.serializer import Jsonizable


class SuccessfulUserResponse(Jsonizable):

    def __init__(self, user):
        self.status = UserStatus.ACTIVE.value
        self.user = ActiveUserResponse(user)

    def json(self):
        return {
            "status": self.status,
            "user": self.user.json()
        }

    def status_code(self):
        return StatusCode.OK.value


class ActiveUserResponse(Jsonizable):

    def __init__(self, user):
        self.username = user.username
        self.email = user.email
        self.first_name = user.first_name
        self.last_name = user.last_name
        self.profile_pic = user.profile_pic
        self.token = user.auth_token

    def json(self):
        return vars(self)


class UserAlreadyCreatedResponse(Jsonizable):

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": UserStatus.ALREADY_REGISTERED.value,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.BAD_REQUEST.value


class WrongCredentialsResponse(Jsonizable):

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": UserStatus.WRONG_CREDENTIALS.value,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.FORBIDDEN.value


class UserLoggedOutResponse(Jsonizable):

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": UserStatus.LOGGED_OUT.value,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.OK.value
