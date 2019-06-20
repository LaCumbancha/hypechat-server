from models.constants import UserRoles


class Message:

    def __init__(self, sender_id, receiver_id, team_id, content, send_type, message_type):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.team_id = team_id
        self.content = content
        self.send_type = send_type
        self.message_type = message_type


class Chat:

    def __init__(self, user_id, chat_id, team_id, offset=0):
        self.user_id = user_id
        self.chat_id = chat_id
        self.team_id = team_id
        self.offset = offset


class ChatMessage:

    def __init__(self, message_id, sender_id, receiver_id, team_id, content, message_type, timestamp, username,
                 profile_pic, first_name, last_name, online):
        self.message_id = message_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.team_id = team_id
        self.content = content
        self.message_type = message_type
        self.timestamp = timestamp
        self.username = username
        self.profile_pic = profile_pic
        self.first_name = first_name
        self.last_name = last_name
        self.online = online


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


class PreviewDirectMessage:

    def __init__(self, message_id, sender_id, receiver_id, chat_username, chat_first_name, chat_last_name, chat_picture,
                 chat_online, content, message_type, timestamp, offset):
        self.message_id = message_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.chat_username = chat_username
        self.chat_first_name = chat_first_name
        self.chat_last_name = chat_last_name
        self.chat_picture = chat_picture
        self.chat_online = chat_online
        self.content = content
        self.message_type = message_type
        self.timestamp = timestamp
        self.offset = offset


class PreviewChannelMessage:

    def __init__(self, message_id, chat_id, chat_name, chat_picture, sender_id, sender_username, sender_first_name,
                 sender_last_name, content, message_type, timestamp, offset):
        self.message_id = message_id
        self.chat_id = chat_id
        self.chat_name = chat_name
        self.chat_picture = chat_picture
        self.sender_id = sender_id
        self.sender_username = sender_username
        self.sender_first_name = sender_first_name
        self.sender_last_name = sender_last_name
        self.content = content
        self.message_type = message_type
        self.timestamp = timestamp
        self.offset = offset


class MessageReceiver:

    def __init__(self, user_id, team_id, is_user):
        self.user_id = user_id
        self.team_id = team_id
        self.is_user = is_user


class MessageStats:

    def __init__(self, direct, channel):
        self.direct = direct
        self.channel = channel
