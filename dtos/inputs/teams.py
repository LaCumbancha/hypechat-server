class NewTeamDTO:

    def __init__(self, username, token, team_name, location, description, welcome_message):
        self._username = username
        self._token = token
        self._team_name = team_name
        self._location = location
        self._description = description
        self._welcome_message = welcome_message

    def username(self):
        return self._username

    def token(self):
        return self._token

    def team_name(self):
        return self._team_name

    def location(self):
        return self._location

    def description(self):
        return self._description

    def welcome_message(self):
        return self._welcome_message
