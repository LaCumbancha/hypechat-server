from dtos.inputs.users import *
from dtos.inputs.messages import *
from dtos.inputs.teams import *
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
            "Body": data.get_json(),
            "Cookies": data.cookies
        })

    def json_body(self):
        return self.data.get_json()

    def new_user_data(self):
        return NewUserDTO(
            username=self.json_body().get("username"),
            email=self.json_body().get("email"),
            password=self.json_body().get("password"),
            first_name=self.json_body().get("first_name"),
            last_name=self.json_body().get("last_name"),
            profile_pic=self.json_body().get("profile_pic")
        )

    def login_data(self):
        return LoginDTO(
            email=self.json_body().get("email"),
            password=self.json_body().get("password")
        )

    def search_users_data(self, searched_username):
        return SearchUsersDTO(
            username=self.json_body().get("username"),
            token=self.json_body().get("auth_token"),
            searched_username=searched_username
        )

    def authentication_data(self):
        return AuthenticationDTO(
            username=self.json_body().get("username"),
            token=self.json_body().get("auth_token")
        )

    def inbox_data(self):
        return InboxDTO(
            username=self.json_body().get("username"),
            token=self.json_body().get("auth_token"),
            chat_id=self.json_body().get("chat_id"),
            text_content=self.json_body().get("text_content"),
        )

    def chat_data(self, chat_id):
        return ChatDTO(
            username=self.json_body().get("username"),
            token=self.json_body().get("auth_token"),
            chat_id=chat_id
        )

    def new_team_data(self):
        return NewTeamDTO(
            username=self.json_body().get("username"),
            token=self.json_body().get("auth_token"),
            team_name=self.json_body().get("team_name"),
            location=self.json_body().get("location"),
            description=self.json_body().get("description"),
            welcome_message=self.json_body().get("welcome_message"),
        )

    def invite_data(self, team_id):
        return TeamInviteDTO(
            username=self.json_body().get("username"),
            token=self.json_body().get("auth_token"),
            team_id=team_id,
            email=self.json_body().get("email")
        )

    def accept_invite(self, team_id):
        return TeamInviteAcceptDTO(
            username=self.json_body().get("username"),
            token=self.json_body().get("auth_token"),
            team_id=team_id,
            invite_token=self.json_body().get("invite_token")
        )
