from models.constants import *
from utils.serializer import Jsonizable
from utils.responses import Response
from abc import abstractmethod


class SuccessfulClientResponse(Jsonizable, Response):

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

    def __init__(self, user, headers=None):
        self._headers = headers
        client = ActiveUserOutput(user)
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

    def headers(self):
        return self._headers


class ActiveUserOutput(Jsonizable):

    def __init__(self, user):
        self.id = user.id
        self.username = user.username
        self.email = user.email
        self.first_name = user.first_name
        self.last_name = user.last_name
        self.profile_pic = user.profile_pic
        self.role = user.role
        self.online = user.online

    def json(self):
        return vars(self)


class SuccessfulFullUserResponse(SuccessfulClientResponse):

    def __init__(self, user, headers=None):
        self._headers = headers
        client = ActiveFullUserOutput(user)
        super(SuccessfulFullUserResponse, self).__init__(client, UserResponseStatus.ACTIVE.value)

    def json(self):
        return {
            "status": self.status,
            "user": self.client.json()
        }


class ActiveFullUserOutput(Jsonizable):

    def __init__(self, user):
        self.id = user["id"]
        self.username = user["username"]
        self.email = user["email"]
        self.first_name = user["first_name"]
        self.last_name = user["last_name"]
        self.profile_pic = user["profile_pic"]
        self.role = user["role"]
        self.teams = user["teams"]

    def json(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "profile_pic": self.profile_pic,
            "teams": self.teams
        }


class SuccessfulUsersListResponse(Jsonizable, Response):

    def __init__(self, users_list):
        self.users_list = users_list

    def json(self):
        return {
            "status": UserResponseStatus.LIST.value,
            "users": self.users_list
        }

    def status_code(self):
        return StatusCode.OK.value


class UnsuccessfulClientResponse(Jsonizable, Response):

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": UserResponseStatus.ERROR.value,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.SERVER_ERROR.value


class BadRequestUserMessageResponse(Jsonizable, Response):

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


class NotFoundUserMessageResponse(Jsonizable, Response):

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


class SuccessfulUserMessageResponse(Jsonizable, Response):

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
