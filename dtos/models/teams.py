from models.constants import TeamRoles


class Team:

    def __init__(self, name, team_id=None, picture=None, location=None, description=None, welcome_message=None, role=None):
        self.id = team_id
        self.name = name
        self.picture = picture
        self.location = location
        self.description = description
        self.welcome_message = welcome_message
        self.role = role


class TeamUser:

    def __init__(self, user_id, team_id, role=None):
        self.user_id = user_id
        self.team_id = team_id
        self.role = role or TeamRoles.MEMBER.value


class TeamInvite:

    def __init__(self, team_id, email, token):
        self.team_id = team_id
        self.email = email
        self.token = token


class ForbiddenWord:

    def __init__(self, word, team_id, word_id=None):
        self.id = word_id
        self.word = word
        self.team_id = team_id
