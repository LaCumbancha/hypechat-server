class Bot:

    def __init__(self, name, callback, bot_id=None):
        self.id = bot_id
        self.name = name
        self.callback = callback
