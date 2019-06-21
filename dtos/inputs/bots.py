from dtos.inputs.teams import TeamAuthenticationDTO


class NewBotDTO:

    def __init__(self, token, team_id, bot_name, callback):
        self.authentication = TeamAuthenticationDTO(token=token, team_id=team_id)
        self.name = bot_name,
        self.callback = callback
