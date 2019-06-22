class Bot:

    def __init__(self, name, team_id, callback, token, bot_id=None):
        self.id = bot_id
        self.team_id = team_id
        self.name = name
        self.callback = callback
        self.token = token
