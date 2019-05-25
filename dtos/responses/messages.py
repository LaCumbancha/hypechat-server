from models.constants import *
from utils.serializer import Jsonizable


class SuccessfulMessageSentResponse(Jsonizable):

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": MessageResponseStatus.SENT.value,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.OK.value


class UnsuccessfulMessageSentResponse(Jsonizable):

    def __init__(self, message):
        self.message = message

    def json(self):
        return {
            "status": MessageResponseStatus.ERROR.value,
            "message": self.message
        }

    def status_code(self):
        return StatusCode.SERVER_ERROR.value


class MessageListResponse(Jsonizable):

    def __init__(self, messages_list):
        self.messages_list = messages_list

    def json(self):
        return {
            "status": MessageResponseStatus.LIST.value,
            "messages": self.messages_list
        }

    def status_code(self):
        return StatusCode.OK.value


class ChatsListResponse(Jsonizable):

    def __init__(self, chats_list):
        self.chats_list = chats_list

    def json(self):
        return {
            "status": MessageResponseStatus.LIST.value,
            "chats": self.chats_list
        }

    def status_code(self):
        return StatusCode.OK.value
