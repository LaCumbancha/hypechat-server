from models.constants import *
from utils.serializer import Jsonizable
from utils.responses import Response


class SuccessfulMessageSentResponse(Jsonizable, Response):

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": MessageResponseStatus.SENT.value,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.OK.value


class SuccessfulMessageStatsResponse(Jsonizable, Response):

    def __init__(self, stats):
        self.stats = stats

    def json(self):
        return {
            "status": MessageResponseStatus.STATS.value,
            "messages": vars(self.stats)
        }

    def status_code(self):
        return StatusCode.OK.value


class UnsuccessfulMessageSentResponse(Jsonizable, Response):

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": MessageResponseStatus.ERROR.value,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.SERVER_ERROR.value


class BadRequestMessageSentResponse(Jsonizable, Response):

    def __init__(self, message, status):
        self.message = message
        self.status = status

    def json(self):
        return {
            "status": self.status,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.BAD_REQUEST.value


class MessageListResponse(Jsonizable, Response):

    def __init__(self, messages_list):
        self.messages_list = messages_list

    def json(self):
        return {
            "status": MessageResponseStatus.LIST.value,
            "messages": self.messages_list
        }

    def status_code(self):
        return StatusCode.OK.value


class ChatsListResponse(Jsonizable, Response):

    def __init__(self, chats_list):
        self.chats_list = chats_list

    def json(self):
        return {
            "status": MessageResponseStatus.LIST.value,
            "chats": self.chats_list
        }

    def status_code(self):
        return StatusCode.OK.value
