import os
import random
import string
import datetime

from tables.users import UserTableEntry, TeamTableEntry, UsersByTeamsTableEntry
from models.constants import UserResponseStatus, TeamResponseStatus
from exceptions.exceptions import *
from sqlalchemy import and_

from app import db
import logging

import jwt
from jwt.contrib.algorithms.pycrypto import RSAAlgorithm

jwt.unregister_algorithm('RS256')
jwt.register_algorithm('RS256', RSAAlgorithm(RSAAlgorithm.SHA256))


class Authenticator:
    _secret = os.getenv('SECRET')
    _invite_token_length = os.getenv('INVITE_TOKEN_LENGTH')

    @classmethod
    def generate(cls, username, password):
        payload = {
            "username": username,
            "password": password,
            "timestamp": datetime.datetime.now().__str__()
        }
        return jwt.encode(payload, cls._secret, algorithm='HS256').decode("utf-8")

    @classmethod
    def team_invitation(cls):
        chars = string.ascii_uppercase
        return "".join(random.choice(chars) for _ in range(int(cls._invite_token_length)))

    @classmethod
    def authenticate(cls, authentication):
        logger = logging.getLogger(cls.__name__)
        payload = jwt.decode(authentication.token.encode(), cls._secret, algorithms='HS256')

        user = db.session.query(UserTableEntry).filter(
            UserTableEntry.username == payload["username"]).one_or_none()

        if user:
            if user.auth_token == authentication.token:
                logger.info(f"User #{user.user_id} authenticated.")
                return user
            else:
                logger.info(f"Failing to authenticate user {user.username}.")
                raise WrongTokenError("You must be logged to perform this action.",
                                      UserResponseStatus.WRONG_TOKEN.value)
        else:
            logger.info(f"User not found.")
            raise UserNotFoundError("User not found.", UserResponseStatus.USER_NOT_FOUND.value)

    @classmethod
    def authenticate_team(cls, authentication, role_verifying=lambda _: True):
        logger = logging.getLogger(cls.__name__)

        user = cls.authenticate(authentication)
        team_user = db.session.query(
            UserTableEntry.user_id,
            UserTableEntry.username,
            UserTableEntry.email,
            UserTableEntry.first_name,
            UserTableEntry.last_name,
            UserTableEntry.profile_pic,
            UserTableEntry.online,
            UsersByTeamsTableEntry.team_id,
            UsersByTeamsTableEntry.role
        ).join(
            UsersByTeamsTableEntry,
            and_(
                UsersByTeamsTableEntry.user_id == UserTableEntry.user_id,
                UsersByTeamsTableEntry.user_id == user.user_id,
                UsersByTeamsTableEntry.team_id == authentication.team_id
            )
        ).one_or_none()

        if team_user:
            if role_verifying(team_user):
                logger.info(f"User {user.username} authenticated as team #{authentication.team_id} {team_user.role}.")
                return team_user
            else:
                logger.info(f"User {user.username} does not have permissions to perform this action.")
                raise NoPermissionsError("You don't have enough permissions to perform this action.",
                                         TeamResponseStatus.NOT_ENOUGH_PERMISSIONS.value)
        else:
            if not db.session.query(TeamTableEntry).filter(
                    TeamTableEntry.team_id == authentication.team_id
            ).one_or_none():
                logger.info(f"Team #{authentication_data.team_id} not found.")
                raise TeamNotFoundError("Team not found.", TeamResponseStatus.TEAM_NOT_FOUND.value)
            else:
                logger.info(
                    f"User {user.username} trying to access team #{authentication.team_id}, when it's not part of it.")
                raise NoPermissionsError("You're not part of this team!",
                                         TeamResponseStatus.NOT_ENOUGH_PERMISSIONS.value)
