import os
import random
import string

from tables.users import UserTableEntry
from exceptions.exceptions import UserNotLoggedError

from app import db


class Authenticator:
    _token_length = os.getenv('SECURITY_TOKEN_LENGTH')

    @classmethod
    def generate(cls):
        chars = string.ascii_letters + string.digits
        return "".join(random.choice(chars) for _ in range(int(cls._token_length)))

    @classmethod
    def authenticate(cls, authentication_data):
        user = db.session.query(UserTableEntry).filter(
            UserTableEntry.auth_token == authentication_data.auth_token()).one_or_none()

        if user:
            return user
        else:
            raise UserNotLoggedError("You must be logged to perform this action.")
