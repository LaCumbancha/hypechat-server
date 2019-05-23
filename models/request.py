from dtos.inputs.users import *

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
