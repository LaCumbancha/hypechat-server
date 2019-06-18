from models.constants import ChannelVisibilities


class Channel:

    def __init__(self, channel_id, team_id, name, creator, visibility=ChannelVisibilities.PUBLIC.value,
                 description=None, welcome_message=None):
        self.channel_id = channel_id
        self.team_id = team_id
        self.name = name
        self.creator = creator
        self.visibility = visibility or ChannelVisibilities.PUBLIC.value
        self.description = description
        self.welcome_message = welcome_message


class ChannelCreator:

    def __init__(self, user_id, username, first_name, last_name):
        self.id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name


class ChannelUser:

    def __init__(self, user_id, channel_id):
        self.user_id = user_id
        self.channel_id = channel_id
