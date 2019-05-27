import os
import random
import string

from tables.users import UserTableEntry, TeamTableEntry, UsersByTeamsTableEntry
from models.constants import UserResponseStatus, TeamResponseStatus
from exceptions.exceptions import *
from sqlalchemy import and_

from app import db
import logging


class Authenticator:
    _token_length = os.getenv('SECURITY_TOKEN_LENGTH')
    _invite_token_length = os.getenv('INVITE_TOKEN_LENGTH')

    @classmethod
    def generate(cls):
        chars = string.ascii_letters + string.digits
        return "".join(random.choice(chars) for _ in range(int(cls._token_length)))

    @classmethod
    def team_invitation(cls):
        chars = string.ascii_uppercase
        return "".join(random.choice(chars) for _ in range(int(cls._invite_token_length)))

    @classmethod
    def authenticate(cls, authentication_data):
        logger = logging.getLogger(cls.__name__)

        user = db.session.query(UserTableEntry).filter(
            UserTableEntry.username == authentication_data.username).one_or_none()

        if user:
            if user.auth_token == authentication_data.token:
                logger.info(f"User #{user.user_id} authenticated.")
                return user
            else:
                logger.info(f"Failing to authenticate user {authentication_data.username}.")
                raise WrongTokenError("You must be logged to perform this action.",
                                      UserResponseStatus.WRONG_TOKEN.value)
        else:
            logger.info(f"User {authentication_data.username} not found.")
            raise UserNotFoundError("User not found.", UserResponseStatus.USER_NOT_FOUND.value)

    @classmethod
    def authenticate_team(cls, authentication_data, role_verifying):
        logger = logging.getLogger(cls.__name__)

        user = db.session.query(UserTableEntry).filter(
            UserTableEntry.username == authentication_data.username).one_or_none()

        if user:
            if user.auth_token == authentication_data.token:
                team_user = db.session.query(UsersByTeamsTableEntry).filter(and_(
                    UsersByTeamsTableEntry.user_id == user.user_id,
                    UsersByTeamsTableEntry.team_id == authentication_data.team_id)).one_or_none()
                if team_user and role_verifying(team_user):
                    logger.info(
                        f"User {user.username} authenticated as team #{authentication_data.team_id} {team_user.role}.")
                    return user
                else:
                    if not db.session.query(TeamTableEntry).filter(TeamTableEntry.team_id == authentication_data.team_id).one_or_none():
                        logger.info(f"Team #{authentication_data.team_id} not found.")
                        raise TeamNotFoundError("Team not found.", TeamResponseStatus.TEAM_NOT_FOUND.value)
                    else:
                        logger.info(f"User {user.username} does not have permissions to perform this action.")
                        raise NoPermissionsError("You don't have enough permissions to perform this action.",
                                                 TeamResponseStatus.NOT_ENOUGH_PERMISSIONS.value)
            else:
                logger.info(f"Failing to authenticate user {authentication_data.username}.")
                raise WrongTokenError("You must be logged to perform this action.",
                                      UserResponseStatus.WRONG_TOKEN.value)
        else:
            logger.info(f"User #{authentication_data.username} not found.")
            raise UserNotFoundError("User not found.", UserResponseStatus.USER_NOT_FOUND.value)
