from dtos.inputs.teams import TeamAuthenticationDTO
from models.constants import MessageResponseStatus, MessageType
from exceptions.exceptions import MessageTypeNotAvailableError


class InboxDTO:

    def __init__(self, token, team_id, chat_id, content, message_type):
        self.authentication = TeamAuthenticationDTO(token, team_id)
        self.chat_id = chat_id
        self.content = content
        try:
            self.message_type = MessageType[message_type].value
        except KeyError:
            raise MessageTypeNotAvailableError(f"Message type {message_type} is not defined.",
                                               MessageResponseStatus.MESSAGE_TYPE_UNAVAILABLE.value)


class ChatDTO:

    def __init__(self, token, team_id, chat_id, offset):
        self.authentication = TeamAuthenticationDTO(token, team_id)
        self.chat_id = chat_id
        self.offset = offset
