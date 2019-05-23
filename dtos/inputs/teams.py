class NewTeamDTO:

    def __init__(self, username, token, team_name, location, description, welcome_message):
        self.username = username
        self.token = token
        self.team_name = team_name
        self.location = location
        self.description = description
        self.welcome_message = welcome_message
