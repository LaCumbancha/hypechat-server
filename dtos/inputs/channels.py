from dtos.inputs.teams import TeamAuthenticationDTO
from models.constants import ChannelResponseStatus, ChannelVisibilities
from exceptions.exceptions import VisibilityNotAvailableError


class NewChannelDTO:

    def __init__(self, token, team_id, name, visibility, description, welcome_message):
        self.authentication = TeamAuthenticationDTO(token, team_id)
        self.name = name
        self.description = description
        self.welcome_message = welcome_message
        try:
            self.visibility = ChannelVisibilities[visibility].value
        except KeyError:
            raise VisibilityNotAvailableError(f"Visibility {visibility} is not defined.",
                                              ChannelResponseStatus.VISIBILITY_UNAVAILABLE.value)
