from dtos.inputs.users import AuthenticationDTO


class InboxDTO:

    def __init__(self, token, chat_id, text_content):
        self.token = token
        self.chat_id = chat_id
        self.text_content = text_content


class ChatDTO:

    def __init__(self, token, chat_id, offset):
        self.token = token
        self.chat_id = chat_id
        self.offset = offset
