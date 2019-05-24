from dtos.inputs.users import *
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

    def authentication_data(self):
        return AuthenticationDTO(
            username=self.json_body().get("username"),
            token=self.json_body().get("auth_token")
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

    def new_user_team_data(self):
        try:
            return NewUserTeamDTO(
                username=self.json_body().get("username"),
                token=self.json_body().get("auth_token"),
                team_id=self.json_body().get("team_id"),
                user_addable_id=self.json_body().get("user_addable_id"),
                role=self.json_body().get("role"),
            )
        except RoleNotAvailableError:
            logging.getLogger(self.__class__.__name__).warning(f"Role {self.json_body().get('role')} not defined.")
            raise
