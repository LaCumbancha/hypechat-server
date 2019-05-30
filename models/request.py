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
            profile_pic=self.json_body().get("profile_pic")
        )

    def login_data(self):
        return LoginDTO(
            email=self.json_body().get("email"),
            password=self.json_body().get("password")
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

    def authentication_data(self):
        return AuthenticationDTO(
            token=self.headers().get("X-Auth-Token")
        )

    def inbox_data(self):
        return InboxDTO(
            token=self.headers().get("X-Auth-Token"),
            chat_id=self.json_body().get("chat_id"),
            text_content=self.json_body().get("text_content"),
        )

    def chat_data(self, chat_id):
        return ChatDTO(
            token=self.headers().get("X-Auth-Token"),
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

    def invite_data(self, team_id):
        return TeamInviteDTO(
            token=self.headers().get("X-Auth-Token"),
            team_id=team_id,
            email=self.json_body().get("email")
        )

    def accept_invite(self, team_id):
        return TeamInviteAcceptDTO(
            token=self.headers().get("X-Auth-Token"),
            team_id=team_id,
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

    def delete_user_data(self, team_id, delete_id):
        return DeleteUserDTO(
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
