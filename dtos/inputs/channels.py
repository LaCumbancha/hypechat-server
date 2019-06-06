from dtos.inputs.teams import TeamAuthenticationDTO
from models.constants import ChannelResponseStatus, ChannelVisibilities
from exceptions.exceptions import VisibilityNotAvailableError


class ChannelAuthenticationDTO:

    def __init__(self, token, team_id, channel_id):
        self.token = token
        self.team_id = team_id
        self.channel_id = channel_id


class NewChannelDTO:

    def __init__(self, token, team_id, name, visibility, description, welcome_message):
        self.authentication = TeamAuthenticationDTO(token, team_id)
        self.name = name
        self.description = description
        self.welcome_message = welcome_message
        try:
            self.visibility = ChannelVisibilities[visibility].value if visibility else None
        except KeyError:
            raise VisibilityNotAvailableError(f"Visibility {visibility} is not defined.",
                                              ChannelResponseStatus.VISIBILITY_UNAVAILABLE.value)


class ChannelInvitationDTO:

    def __init__(self, token, team_id, channel_id, user_invited_id):
        self.authentication = ChannelAuthenticationDTO(token, team_id, channel_id)
        self.user_invited_id = user_invited_id


class ChannelRegistrationDTO:

    def __init__(self, token, team_id, channel_id):
        self.authentication = TeamAuthenticationDTO(token, team_id)
        self.channel_id = channel_id


class DeleteUserChannelDTO:

    def __init__(self, token, team_id, channel_id, delete_id):
        self.authentication = ChannelAuthenticationDTO(token, team_id, channel_id)
        self.delete_id = delete_id


class ChannelUpdateDTO:

    def __init__(self, token, team_id, channel_id, updated_channel):
        self.authentication = ChannelAuthenticationDTO(token, team_id, channel_id)
        self.updated_channel = updated_channel
        if "visibility" in updated_channel and not updated_channel["visibility"] in ChannelVisibilities.__members__:
            raise VisibilityNotAvailableError(f"Visibility {updated_channel['visibility']} is not defined.",
                                              ChannelResponseStatus.VISIBILITY_UNAVAILABLE.value)
