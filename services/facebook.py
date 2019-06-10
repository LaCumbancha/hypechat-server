from dtos.model import FacebookUserDTO
from exceptions.exceptions import FacebookWrongTokenError

import requests
import logging
import json
import os


class FacebookService:
    FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
    GET_USER_URL = "https://graph.facebook.com/debug_token?input_token={}&access_token={}"
    GET_USER_DATA_URL = "https://graph.facebook.com/{}?fields=email,picture,first_name,last_name&access_token={}"

    @classmethod
    def logger(cls):
        return logging.getLogger(cls.__name__)

    @classmethod
    def get_user_from_facebook(cls, user_data):
        cls.logger().debug("Getting Facebook's user ID.")
        main_response = requests.get(cls.GET_USER_URL.format(user_data.facebook_token, cls.FACEBOOK_APP_SECRET))
        main_response_content = json.loads(main_response.content.decode('utf8').replace("'", '"'))["data"]

        if main_response_content["is_valid"]:
            facebook_user_id = main_response_content["user_id"]

            user_response = requests.get(cls.GET_USER_DATA_URL.format(facebook_user_id, cls.FACEBOOK_APP_SECRET))
            user_response_content = json.loads(user_response.content.decode('utf8').replace("'", '"'))

            return FacebookUserDTO(
                facebook_id=user_response_content["id"],
                email=None,#user_response_content["email"],
                first_name=user_response_content["first_name"],
                last_name=user_response_content["last_name"],
                profile_pic=user_response_content["picture"]["data"]["url"]
            )

        else:
            facebook_error_code = main_response_content["data"]["error"]["code"]

            if facebook_error_code == 190:
                cls.logger().error("Couldn't get Facebook data due to an invalid OAuth access token.")

            raise FacebookWrongTokenError("Invalid OAuth access token")
