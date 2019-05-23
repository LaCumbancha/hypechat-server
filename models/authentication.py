import os
import random
import string

from tables.users import UserTableEntry
from models.constants import UserResponseStatus
from exceptions.exceptions import WrongTokenError
from sqlalchemy import and_

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

        user = db.session.query(UserTableEntry).filter(and_(
            UserTableEntry.auth_token == authentication_data.token(),
            UserTableEntry.username == authentication_data.username())).one_or_none()

        if user:
            logger.info(f"User #{user.user_id} authenticated.")
            return user
        else:
            logger.info(f"Failing to authenticate user {authentication_data.username}.")
            raise WrongTokenError("You must be logged to perform this action.", UserResponseStatus.WRONG_TOKEN.value)
