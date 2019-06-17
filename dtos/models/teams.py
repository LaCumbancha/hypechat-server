from models.constants import UserRoles


class Team:

    def __init__(self, team_id, name, picture=None, location=None, description=None, welcome_message=None, role=None):
        self.id = team_id
        self.name = name
        self.picture = picture
        self.location = location
        self.description = description
        self.welcome_message = welcome_message
        self.role = role
