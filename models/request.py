from dtos.inputs.bots import *
from dtos.inputs.users import *
from dtos.inputs.messages import *
from dtos.inputs.teams import *
from dtos.inputs.channels import *
from exceptions.exceptions import *

import logging


class ClientRequest:

    def __init__(self, data):
        self.data = data
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logging_request(self.data)

    @classmethod
    def logging_request(cls, request):
        logger = logging.getLogger(cls.__name__)
        if cls.has_application_json_header(request.headers.to_list()) and cls.has_empty_body(request.data):
            logger.error("Content-Type specified as \"application/json\" but no body provided.")

        logger.info({
            "Headers": request.headers.to_list(),
            "Body": request.get_json() if request.is_json else None
        })

    @classmethod
    def has_application_json_header(cls, headers):
        return any(map(lambda header: header[0] == 'Content-Type', headers))

    @classmethod
    def has_empty_body(cls, body):
        return body == b''

    def query_params(self):
        return self.data.args

    def headers(self):
        return self.data.headers

    def json_body(self):
        return self.data.get_json()

    def new_user_data(self):
        username = self.json_body().get("username")
        email = self.json_body().get("email")
        password = self.json_body().get("password")

        if username is None:
            self.logger.error("Missing parameter in request body: username.")
            raise MissingRequestParameterError("username")

        if email is None:
            self.logger.error("Missing parameter in request body: email.")
            raise MissingRequestParameterError("email")

        if password is None:
            self.logger.error("Missing parameter in request body: password.")
            raise MissingRequestParameterError("password")

        return NewUserDTO(
            username=username,
            email=email,
            password=password,
            first_name=self.json_body().get("first_name"),
            last_name=self.json_body().get("last_name"),
            profile_pic=self.json_body().get("profile_pic"),
            role=self.json_body().get("role")
        )

    def login_data(self):
        email = self.json_body().get("email")
        password = self.json_body().get("password")
        facebook_token = self.json_body().get("facebook_token")

        if facebook_token is None:

            if email is None:
                self.logger.error("Missing parameter in request body: email.")
                raise MissingRequestParameterError("email")

            if password is None:
                self.logger.error("Missing parameter in request body: password.")
                raise MissingRequestParameterError("password")

        return LoginDTO(
            email=email,
            password=password,
            facebook_token=facebook_token
        )

    def recover_password_data(self):
        email = self.json_body().get("email")

        if email is None:
            self.logger.error("Missing parameter in request body: email.")
            raise MissingRequestParameterError("email")

        return RecoverPasswordDTO(
            email=email
        )

    def regenerate_password_data(self):
        email = self.json_body().get("email")
        recover_token = self.json_body().get("recover_token")

        if email is None:
            self.logger.error("Missing parameter in request body: email.")
            raise MissingRequestParameterError("email")

        if recover_token is None:
            self.logger.error("Missing parameter in request body: recover_token.")
            raise MissingRequestParameterError("recover_token")

        return RegeneratePasswordDTO(
            email=email,
            recover_token=recover_token
        )

    def user_update_data(self):
        auth_token = self.headers().get("X-Auth-Token")

        if auth_token is None:
            self.logger.error("Missing parameter in request headers: X-Auth-Token.")
            raise MissingRequestHeaderError("X-Auth-Token")

        return UserUpdateDTO(
            token=auth_token,
            updated_user=self.json_body()
        )

    def search_users_by_username_data(self, team_id, searched_username):
        auth_token = self.headers().get("X-Auth-Token")

        if auth_token is None:
            self.logger.error("Missing parameter in request headers: X-Auth-Token.")
            raise MissingRequestHeaderError("X-Auth-Token")

        return SearchUsersDTO(
            token=auth_token,
            team_id=team_id,
            searched_username=searched_username,
        )

    def team_user_profile_data(self, team_id, user_id):
        auth_token = self.headers().get("X-Auth-Token")

        if auth_token is None:
            self.logger.error("Missing parameter in request headers: X-Auth-Token.")
            raise MissingRequestHeaderError("X-Auth-Token")

        return SearchUserByIdDTO(
            token=auth_token,
            team_id=team_id,
            user_id=user_id
        )

    def authentication_data(self):
        auth_token = self.headers().get("X-Auth-Token")

        if auth_token is None:
            self.logger.error("Missing parameter in request headers: X-Auth-Token.")
            raise MissingRequestHeaderError("X-Auth-Token")

        return AuthenticationDTO(
            token=auth_token
        )

    def inbox_data(self):
        auth_token = self.headers().get("X-Auth-Token")
        team_id = self.json_body().get("team_id")
        chat_id = self.json_body().get("chat_id")
        content = self.json_body().get("content")
        message_type = self.json_body().get("message_type")

        if auth_token is None:
            self.logger.error("Missing parameter in request headers: X-Auth-Token.")
            raise MissingRequestHeaderError("X-Auth-Token")

        if team_id is None:
            self.logger.error("Missing parameter in request body: team_id.")
            raise MissingRequestParameterError("team_id")

        if chat_id is None:
            self.logger.error("Missing parameter in request body: chat_id.")
            raise MissingRequestParameterError("chat_id")

        if content is None:
            self.logger.error("Missing parameter in request body: content.")
            raise MissingRequestParameterError("content")

        if message_type is None:
            self.logger.error("Missing parameter in request body: message_type.")
            raise MissingRequestParameterError("message_type")

        try:
            return InboxDTO(
                token=auth_token,
                team_id=team_id,
                chat_id=chat_id,
                content=content,
                message_type=message_type,
                mentions=self.json_body().get("mentions")
            )
        except MessageTypeNotAvailableError:
            logging.getLogger(self.__class__.__name__).warning(f"Message type {self.json_body().get('message_type')} not defined.")
            raise

    def chat_data(self, team_id, chat_id):
        auth_token = self.headers().get("X-Auth-Token")

        if auth_token is None:
            self.logger.error("Missing parameter in request headers: X-Auth-Token.")
            raise MissingRequestHeaderError("X-Auth-Token")

        return ChatDTO(
            token=auth_token,
            team_id=team_id,
            chat_id=chat_id,
            offset=self.query_params().get("offset") or 0
        )

    def new_team_data(self):
        auth_token = self.headers().get("X-Auth-Token")
        team_name = self.json_body().get("team_name")

        if auth_token is None:
            self.logger.error("Missing parameter in request headers: X-Auth-Token.")
            raise MissingRequestHeaderError("X-Auth-Token")

        if team_name is None:
            self.logger.error("Missing parameter in request body: team_name.")
            raise MissingRequestParameterError("team_name")

        return NewTeamDTO(
            token=auth_token,
            team_name=team_name,
            picture=self.json_body().get("picture"),
            location=self.json_body().get("location"),
            description=self.json_body().get("description"),
            welcome_message=self.json_body().get("welcome_message"),
        )

    def add_user_team_data(self):
        auth_token = self.headers().get("X-Auth-Token")
        team_id = self.json_body().get("team_id")
        add_user_id = self.json_body().get("add_user_id")

        if auth_token is None:
            self.logger.error("Missing parameter in request headers: X-Auth-Token.")
            raise MissingRequestHeaderError("X-Auth-Token")

        if team_id is None:
            self.logger.error("Missing parameter in request body: team_id.")
            raise MissingRequestParameterError("team_id")

        if add_user_id is None:
            self.logger.error("Missing parameter in request body: add_user_id.")
            raise MissingRequestParameterError("add_user_id")

        return AddUserTeamDTO(
            token=auth_token,
            team_id=team_id,
            add_user_id=add_user_id
        )

    def team_invite_data(self):
        auth_token = self.headers().get("X-Auth-Token")
        team_id = self.json_body().get("team_id")
        email = self.json_body().get("email")

        if auth_token is None:
            self.logger.error("Missing parameter in request headers: X-Auth-Token.")
            raise MissingRequestHeaderError("X-Auth-Token")

        if team_id is None:
            self.logger.error("Missing parameter in request body: team_id.")
            raise MissingRequestParameterError("team_id")

        if email is None:
            self.logger.error("Missing parameter in request body: email.")
            raise MissingRequestParameterError("email")

        return TeamInviteDTO(
            token=auth_token,
            team_id=team_id,
            email=email
        )

    def accept_team_invite_data(self):
        auth_token = self.headers().get("X-Auth-Token")
        invite_token = self.json_body().get("invite_token")

        if auth_token is None:
            self.logger.error("Missing parameter in request headers: X-Auth-Token.")
            raise MissingRequestHeaderError("X-Auth-Token")

        if invite_token is None:
            self.logger.error("Missing parameter in request body: invite_token.")
            raise MissingRequestParameterError("invite_token")

        return TeamInviteAcceptDTO(
            token=auth_token,
            invite_token=invite_token
        )

    def change_role_data(self, team_id):
        auth_token = self.headers().get("X-Auth-Token")
        user_id = self.json_body().get("user_id")
        new_role = self.json_body().get("new_role")

        if auth_token is None:
            self.logger.error("Missing parameter in request headers: X-Auth-Token.")
            raise MissingRequestHeaderError("X-Auth-Token")

        if user_id is None:
            self.logger.error("Missing parameter in request body: user_id.")
            raise MissingRequestParameterError("user_id")

        if new_role is None:
            self.logger.error("Missing parameter in request body: new_role.")
            raise MissingRequestParameterError("new_role")

        try:
            return ChangeRoleDTO(
                token=auth_token,
                team_id=team_id,
                user_id=user_id,
                new_role=new_role
            )
        except RoleNotAvailableError:
            logging.getLogger(self.__class__.__name__).warning(f"Role {self.json_body().get('new_role')} not defined.")
            raise

    def team_authentication_data(self, team_id):
        auth_token = self.headers().get("X-Auth-Token")

        if auth_token is None:
            self.logger.error("Missing parameter in request headers: X-Auth-Token.")
            raise MissingRequestHeaderError("X-Auth-Token")

        return TeamAuthenticationDTO(
            token=auth_token,
            team_id=team_id
        )

    def delete_user_team_data(self, team_id, delete_id):
        auth_token = self.headers().get("X-Auth-Token")

        if auth_token is None:
            self.logger.error("Missing parameter in request headers: X-Auth-Token.")
            raise MissingRequestHeaderError("X-Auth-Token")

        return DeleteUserTeamDTO(
            token=auth_token,
            team_id=team_id,
            delete_id=delete_id
        )

    def team_update_data(self, team_id):
        auth_token = self.headers().get("X-Auth-Token")

        if auth_token is None:
            self.logger.error("Missing parameter in request headers: X-Auth-Token.")
            raise MissingRequestHeaderError("X-Auth-Token")

        return TeamUpdateDTO(
            token=auth_token,
            team_id=team_id,
            updated_team=self.json_body()
        )

    def new_channel_data(self):
        auth_token = self.headers().get("X-Auth-Token")
        team_id = self.json_body().get("team_id")
        name = self.json_body().get("name")

        if auth_token is None:
            self.logger.error("Missing parameter in request headers: X-Auth-Token.")
            raise MissingRequestHeaderError("X-Auth-Token")

        if team_id is None:
            self.logger.error("Missing parameter in request body: team_id.")
            raise MissingRequestParameterError("team_id")

        if name is None:
            self.logger.error("Missing parameter in request body: name.")
            raise MissingRequestParameterError("name")

        try:
            return NewChannelDTO(
                token=auth_token,
                team_id=team_id,
                name=name,
                visibility=self.json_body().get("visibility"),
                description=self.json_body().get("description"),
                welcome_message=self.json_body().get("welcome_message")
            )
        except VisibilityNotAvailableError:
            logging.getLogger(self.__class__.__name__).warning(f"Visibility {self.json_body().get('visibility')} not defined.")
            raise

    def channel_invitation_data(self):
        auth_token = self.headers().get("X-Auth-Token")
        team_id = self.json_body().get("team_id")
        channel_id = self.json_body().get("channel_id")
        user_invited_id = self.json_body().get("user_invited_id")

        if auth_token is None:
            self.logger.error("Missing parameter in request headers: X-Auth-Token.")
            raise MissingRequestHeaderError("X-Auth-Token")

        if team_id is None:
            self.logger.error("Missing parameter in request body: team_id.")
            raise MissingRequestParameterError("team_id")

        if channel_id is None:
            self.logger.error("Missing parameter in request body: channel_id.")
            raise MissingRequestParameterError("channel_id")

        if user_invited_id is None:
            self.logger.error("Missing parameter in request body: user_invited_id.")
            raise MissingRequestParameterError("user_invited_id")

        return ChannelInvitationDTO(
            token=auth_token,
            team_id=team_id,
            channel_id=channel_id,
            user_invited_id=user_invited_id
        )

    def channel_registration_data(self):
        auth_token = self.headers().get("X-Auth-Token")
        team_id = self.json_body().get("team_id")
        channel_id = self.json_body().get("channel_id")

        if auth_token is None:
            self.logger.error("Missing parameter in request headers: X-Auth-Token.")
            raise MissingRequestHeaderError("X-Auth-Token")

        if team_id is None:
            self.logger.error("Missing parameter in request body: team_id.")
            raise MissingRequestParameterError("team_id")

        if channel_id is None:
            self.logger.error("Missing parameter in request body: channel_id.")
            raise MissingRequestParameterError("channel_id")

        return ChannelRegistrationDTO(
            token=auth_token,
            team_id=team_id,
            channel_id=channel_id
        )

    def delete_user_channel_data(self, team_id, channel_id, user_id):
        auth_token = self.headers().get("X-Auth-Token")

        if auth_token is None:
            self.logger.error("Missing parameter in request headers: X-Auth-Token.")
            raise MissingRequestHeaderError("X-Auth-Token")

        return DeleteUserChannelDTO(
            token=auth_token,
            team_id=team_id,
            channel_id=channel_id,
            delete_id=user_id
        )

    def channel_authentication_data(self, team_id, channel_id):
        auth_token = self.headers().get("X-Auth-Token")

        if auth_token is None:
            self.logger.error("Missing parameter in request headers: X-Auth-Token.")
            raise MissingRequestHeaderError("X-Auth-Token")

        return ChannelAuthenticationDTO(
            token=auth_token,
            team_id=team_id,
            channel_id=channel_id
        )

    def channel_update_data(self, team_id, channel_id):
        auth_token = self.headers().get("X-Auth-Token")

        if auth_token is None:
            self.logger.error("Missing parameter in request headers: X-Auth-Token.")
            raise MissingRequestHeaderError("X-Auth-Token")

        return ChannelUpdateDTO(
            token=auth_token,
            team_id=team_id,
            channel_id=channel_id,
            updated_channel=self.json_body()
        )

    def add_forbidden_word_data(self):
        auth_token = self.headers().get("X-Auth-Token")
        team_id = self.json_body().get("team_id")
        word = self.json_body().get("word")

        if auth_token is None:
            self.logger.error("Missing parameter in request headers: X-Auth-Token.")
            raise MissingRequestHeaderError("X-Auth-Token")

        if word is None:
            self.logger.error("Missing parameter in request body: word.")
            raise MissingRequestParameterError("word")

        if team_id is None:
            self.logger.error("Missing parameter in request body: team_id.")
            raise MissingRequestParameterError("team_id")

        return AddForbiddenWordDTO(
            token=auth_token,
            team_id=team_id,
            word=word
        )

    def delete_forbidden_word_data(self, team_id, word_id):
        auth_token = self.headers().get("X-Auth-Token")

        if auth_token is None:
            self.logger.error("Missing parameter in request headers: X-Auth-Token.")
            raise MissingRequestHeaderError("X-Auth-Token")

        return DeleteForbiddenWordDTO(
            token=auth_token,
            team_id=team_id,
            word_id=word_id
        )

    def new_bot_data(self):
        auth_token = self.headers().get("X-Auth-Token")
        team_id = self.json_body().get("team_id")
        bot_name = self.json_body().get("name")
        callback = self.json_body().get("url")

        if auth_token is None:
            self.logger.error("Missing parameter in request headers: X-Auth-Token.")
            raise MissingRequestHeaderError("X-Auth-Token")

        if team_id is None:
            self.logger.error("Missing parameter in request body: team_id.")
            raise MissingRequestParameterError("team_id")

        if bot_name is None:
            self.logger.error("Missing parameter in request body: name.")
            raise MissingRequestParameterError("name")

        if callback is None:
            self.logger.error("Missing parameter in request body: url.")
            raise MissingRequestParameterError("url")

        return NewBotDTO(
            token=auth_token,
            team_id=team_id,
            bot_name=bot_name,
            callback=callback
        )
