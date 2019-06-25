class Bot:

    def __init__(self, name, callback, token, bot_id=None):
        self.id = bot_id
        self.name = name
        self.callback = callback
        self.token = token
