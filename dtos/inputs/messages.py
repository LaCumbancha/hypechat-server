from dtos.inputs.users import AuthenticationDTO

class InboxDTO:

    def __init__(self, username, token, chat_id, text_content):
        self.authentication = AuthenticationDTO(username, token)
        self.chat_id = chat_id
        self.text_content = text_content


class ChatDTO:

    def __init__(self, username, token, chat_id):
        self.authentication = AuthenticationDTO(username, token)
        self.chat_id = chat_id
