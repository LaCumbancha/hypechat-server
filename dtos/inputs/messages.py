from dtos.inputs.teams import TeamAuthenticationDTO


class InboxDTO:

    def __init__(self, token, team_id, chat_id, text_content):
        self.authentication = TeamAuthenticationDTO(token, team_id)
        self.chat_id = chat_id
        self.text_content = text_content


class ChatDTO:

    def __init__(self, token, team_id, chat_id, offset):
        self.authentication = TeamAuthenticationDTO(token, team_id)
        self.chat_id = chat_id
        self.offset = offset
