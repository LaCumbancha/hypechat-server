from dtos.responses.clients import SuccessfulClientResponse
from models.constants import *
from utils.serializer import Jsonizable
from utils.responses import Response


class SuccessfulChannelResponse(SuccessfulClientResponse):

    def __init__(self, channel, status):
        client = ActiveChannelOutput(channel)
        super(SuccessfulChannelResponse, self).__init__(client, status)

    def json(self):
        return {
            "status": self.status,
            "channel": self.client.json()
        }


class SuccessfulChannelsListResponse(Jsonizable, Response):

    def __init__(self, channels_list):
        self.channels_list = channels_list

    def json(self):
        return {
            "status": UserResponseStatus.LIST.value,
            "channels": self.channels_list
        }

    def status_code(self):
        return StatusCode.OK.value


class ActiveChannelOutput(Jsonizable):

    def __init__(self, channel):
        self.channel_id = channel.channel_id
        self.team_id = channel.team_id
        self.name = channel.name
        self.creator = channel.creator_id
        self.visibility = channel.visibility
        self.description = channel.description
        self.welcome_message = channel.welcome_message

    def json(self):
        return vars(self)


class SuccessfulChannelMessageResponse(Jsonizable, Response):

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


class BadRequestChannelMessageResponse(Jsonizable, Response):

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


class ForbiddenChannelMessageResponse(Jsonizable, Response):

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


class UnsuccessfulChannelMessageResponse(Jsonizable, Response):

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": TeamResponseStatus.ERROR.value,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.SERVER_ERROR.value


class NotFoundChannelMessageResponse(Jsonizable, Response):

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
