from models.constants import ChannelVisibilities


class Channel:

    def __init__(self, channel_id, team_id, name, creator_id, visibility, description, welcome_message):
        self.channel_id = channel_id
        self.team_id = team_id
        self.name = name
        self.creator_id = creator_id
        self.visibility = visibility or ChannelVisibilities.PUBLIC.value
        self.description = description
        self.welcome_message = welcome_message


class ChannelUser:

    def __init__(self, user_id, channel_id):
        self.user_id = user_id
        self.channel_id = channel_id
