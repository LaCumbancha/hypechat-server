from models.constants import UserStatus
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


class WrongCredentialsResponse(Jsonizable):

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": UserStatus.USER_NOT_FOUND.value,
            "message": self.message
        }


class UserLoggedOutResponse(Jsonizable):

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": UserStatus.LOGGED_OUT.value,
            "message": self.message
        }
