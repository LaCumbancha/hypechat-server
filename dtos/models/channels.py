from models.constants import UserRoles


class Channel:

    def __init__(self, channel_id, team_id, name, creator_id, visibility, description, welcome_message):
        self.channel_id = channel_id
        self.team_id = team_id
        self.name = name
        self.creator_id = creator_id
        self.visibility = visibility
        self.description = description
        self.welcome_message = welcome_message
