from dtos.inputs.users import *
from dtos.inputs.messages import *
from dtos.inputs.teams import *
from dtos.inputs.channels import *
from exceptions.exceptions import RoleNotAvailableError

import logging


class ClientRequest:

    def __init__(self, data):
        self.data = data
        self.logging_request(self.data)

    @classmethod
    def logging_request(cls, data):
        logging.getLogger(cls.__name__).info({
            "Headers": data.headers.to_list(),
            "Body": data.get_json() if data.is_json else None
        })

    def query_params(self):
        return self.data.args

    def headers(self):
        return self.data.headers

    def json_body(self):
        return self.data.get_json()

    def new_user_data(self):
        return NewUserDTO(
            username=self.json_body().get("username"),
            email=self.json_body().get("email"),
            password=self.json_body().get("password"),
            first_name=self.json_body().get("first_name"),
            last_name=self.json_body().get("last_name"),
            profile_pic=self.json_body().get("profile_pic"),
            role=self.json_body().get("role")
        )

    def login_data(self):
        return LoginDTO(
            email=self.json_body().get("email"),
            password=self.json_body().get("password")
        )

    def recover_data(self):
        return RecoverPasswordDTO(
            email=self.json_body().get("email")
        )

    def regenerate_data(self):
        return RegeneratePasswordDTO(
            email=self.json_body().get("email"),
            recover_token=self.json_body().get("recover_token")
        )

    def user_update(self):
        return UserUpdateDTO(
            token=self.headers().get("X-Auth-Token"),
            updated_user=self.json_body()
        )

    def search_users_data(self, team_id, searched_username):
        return SearchUsersDTO(
            token=self.headers().get("X-Auth-Token"),
            team_id=team_id,
            searched_username=searched_username,
        )

    def search_user_by_id(self, team_id, user_id):
        return SearchUserByIdDTO(
            token=self.headers().get("X-Auth-Token"),
            team_id=team_id,
            user_id=user_id
        )

    def authentication_data(self):
        return AuthenticationDTO(
            token=self.headers().get("X-Auth-Token")
        )

    def inbox_data(self):
        try:
            return InboxDTO(
                token=self.headers().get("X-Auth-Token"),
                team_id=self.json_body().get("team_id"),
                chat_id=self.json_body().get("chat_id"),
                content=self.json_body().get("content"),
                message_type=self.json_body().get("message_type")
            )
        except MessageTypeNotAvailableError:
            logging.getLogger(self.__class__.__name__).warning(f"Message type {self.json_body().get('message_type')} not defined.")
            raise

    def chat_data(self, team_id, chat_id):
        return ChatDTO(
            token=self.headers().get("X-Auth-Token"),
            team_id=team_id,
            chat_id=chat_id,
            offset=self.query_params().get("offset") or 0
        )

    def new_team_data(self):
        return NewTeamDTO(
            token=self.headers().get("X-Auth-Token"),
            team_name=self.json_body().get("team_name"),
            picture=self.json_body().get("picture"),
            location=self.json_body().get("location"),
            description=self.json_body().get("description"),
            welcome_message=self.json_body().get("welcome_message"),
        )

    def invite_data(self):
        return TeamInviteDTO(
            token=self.headers().get("X-Auth-Token"),
            team_id=self.json_body().get("team_id"),
            email=self.json_body().get("email")
        )

    def accept_invite(self):
        return TeamInviteAcceptDTO(
            token=self.headers().get("X-Auth-Token"),
            team_id=self.json_body().get("team_id"),
            invite_token=self.json_body().get("invite_token")
        )

    def change_role(self, team_id):
        try:
            return ChangeRoleDTO(
                token=self.headers().get("X-Auth-Token"),
                team_id=team_id,
                user_id=self.json_body().get("user_id"),
                new_role=self.json_body().get("new_role")
            )
        except RoleNotAvailableError:
            logging.getLogger(self.__class__.__name__).warning(f"Role {self.json_body().get('new_role')} not defined.")
            raise

    def team_authentication(self, team_id):
        return TeamAuthenticationDTO(
            token=self.headers().get("X-Auth-Token"),
            team_id=team_id
        )

    def delete_user_team_data(self, team_id, delete_id):
        return DeleteUserTeamDTO(
            token=self.headers().get("X-Auth-Token"),
            team_id=team_id,
            delete_id=delete_id
        )

    def team_update(self, team_id):
        return TeamUpdateDTO(
            token=self.headers().get("X-Auth-Token"),
            team_id=team_id,
            updated_team=self.json_body()
        )

    def new_channel_data(self):
        try:
            return NewChannelDTO(
                token=self.headers().get("X-Auth-Token"),
                team_id=self.json_body().get("team_id"),
                name=self.json_body().get("name"),
                visibility=self.json_body().get("visibility"),
                description=self.json_body().get("description"),
                welcome_message=self.json_body().get("welcome_message")
            )
        except VisibilityNotAvailableError:
            logging.getLogger(self.__class__.__name__).warning(f"Visibility {self.json_body().get('visibility')} not defined.")
            raise

    def channel_invitation_data(self):
        return ChannelInvitationDTO(
            token=self.headers().get("X-Auth-Token"),
            team_id=self.json_body().get("team_id"),
            channel_id=self.json_body().get("channel_id"),
            user_invited_id=self.json_body().get("user_invited_id")
        )

    def channel_registration_data(self):
        return ChannelRegistrationDTO(
            token=self.headers().get("X-Auth-Token"),
            team_id=self.json_body().get("team_id"),
            channel_id=self.json_body().get("channel_id")
        )

    def delete_user_channel(self, team_id, channel_id, user_id):
        return DeleteUserChannelDTO(
            token=self.headers().get("X-Auth-Token"),
            team_id=team_id,
            channel_id=channel_id,
            delete_id=user_id
        )

    def channel_authentication(self, team_id, channel_id):
        return ChannelAuthenticationDTO(
            token=self.headers().get("X-Auth-Token"),
            team_id=team_id,
            channel_id=channel_id
        )

    def channel_update(self, team_id, channel_id):
        return ChannelUpdateDTO(
            token=self.headers().get("X-Auth-Token"),
            team_id=team_id,
            channel_id=channel_id,
            updated_channel=self.json_body()
        )
