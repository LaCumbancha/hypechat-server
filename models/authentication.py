import os
import random
import string

from tables.users import UserTableEntry
from models.constants import UserStatus
from exceptions.exceptions import WrongTokenError

from app import db
import logging


class Authenticator:
    _token_length = os.getenv('SECURITY_TOKEN_LENGTH')

    @classmethod
    def generate(cls):
        chars = string.ascii_letters + string.digits
        return "".join(random.choice(chars) for _ in range(int(cls._token_length)))

    @classmethod
    def authenticate(cls, authentication_data):
        logger = logging.getLogger(cls.__name__)

        user = db.session.query(UserTableEntry).filter(
            UserTableEntry.auth_token == authentication_data.token()).one_or_none()

        if user:
            logger.info(f"User with ID {user.id} authenticated.")
            return user
        else:
            logger.info(f"Failing to authenticate user.")
            raise WrongTokenError("You must be logged to perform this action.", UserStatus.WRONG_TOKEN.value)
