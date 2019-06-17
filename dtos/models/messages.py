from models.constants import UserRoles


class Mention:

    def __init__(self, message_id, client_id):
        self.message_id = message_id
        self.client_id = client_id


class ClientMention:

    def __init__(self, user_id, username, first_name, last_name):
        self.id = user_id
        self.username = username,
        self.first_name = first_name
        self.last_name = last_name
