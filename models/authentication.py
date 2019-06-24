import os
import random
import string
import datetime

from daos.bots import BotDatabaseClient
from daos.database import DatabaseClient
from daos.users import UserDatabaseClient
from daos.teams import TeamDatabaseClient
from daos.channels import ChannelDatabaseClient

from models.constants import UserResponseStatus, TeamResponseStatus, ChannelResponseStatus, TeamRoles, UserRoles
from exceptions.exceptions import *

import logging

from jwt.exceptions import DecodeError
import jwt


class Authenticator:
    _secret = os.getenv('SECRET')
    _invite_token_length = os.getenv('INVITE_TOKEN_LENGTH')
    _recovery_token_length = os.getenv('RECOVER_TOKEN_LENGTH')

    @classmethod
    def generate(cls, user_id, password=None):
        payload = {
            "user_id": user_id,
            "password": password,
            "timestamp": datetime.datetime.now().__str__()
        }
        return jwt.encode(payload, cls._secret, algorithm='HS256').decode("utf-8")

    @classmethod
    def generate_recovery_token(cls):
        chars = string.ascii_uppercase
        return "".join(random.choice(chars) for _ in range(int(cls._recovery_token_length)))

    @classmethod
    def generate_team_invitation(cls):
        chars = string.ascii_uppercase
        return "".join(random.choice(chars) for _ in range(int(cls._invite_token_length)))

    @classmethod
    def authenticate(cls, authentication, role_verifying=lambda _: True):
        logger = logging.getLogger(cls.__name__)

        try:
            payload = jwt.decode(authentication.token.encode(), cls._secret, algorithms='HS256')

            user = UserDatabaseClient.get_user_by_id(payload.get("user_id"))

            if user is not None:
                if role_verifying(user.role):
                    if user.token == authentication.token:
                        logger.info(f"User #{user.id} authenticated.")
                        return user
                    else:
                        logger.info(f"Failing to authenticate user #{payload['user_id']}.")
                        raise WrongTokenError("You must be logged to perform this action.",
                                              UserResponseStatus.WRONG_TOKEN.value)
                else:
                    bot = BotDatabaseClient.get_bot_by_id(payload.get("user_id"))

                    if bot is not None:
                        logger.info(f"Bot #{bot.id} authenticated.")
                        return bot
                    else:
                        logger.info(f"User #{user.id} does not have permissions to perform this action.")
                        raise NoPermissionsError("You don't have enough permissions to perform this action.",
                                                 TeamResponseStatus.NOT_ENOUGH_PERMISSIONS.value)
            else:
                logger.info(f"User not found.")
                raise UserNotFoundError("User not found.", UserResponseStatus.USER_NOT_FOUND.value)

        except DecodeError:
            logger.info(f"Failing to authenticate user.")
            raise WrongTokenError("You must be logged to perform this action.", UserResponseStatus.WRONG_TOKEN.value)

    @classmethod
    def authenticate_team(cls, authentication, role_verifying=lambda _: True):
        logger = logging.getLogger(cls.__name__)

        user = cls.authenticate(authentication)

        if user.role == UserRoles.ADMIN.value:
            user.user_role = user.role
            user.team_id = authentication.team_id
            user.team_role = user.role
            return user

        team_user = UserDatabaseClient.get_team_user_by_ids(user.id, authentication.team_id)

        if team_user is not None:
            if role_verifying(team_user.team_role):
                logger.info(f"Client #{team_user.id} authenticated as team #{team_user.team_id} {team_user.team_role}.")
                return team_user
            else:
                logger.info(f"User #{user.id} does not have permissions to perform this action.")
                raise NoPermissionsError("You don't have enough permissions to perform this action.",
                                         TeamResponseStatus.NOT_ENOUGH_PERMISSIONS.value)
        else:
            team = TeamDatabaseClient.get_team_by_id(authentication.team_id)

            if team is None:
                logger.info(f"Team #{authentication.team_id} not found.")
                raise TeamNotFoundError("Team not found.", TeamResponseStatus.NOT_FOUND.value)
            else:
                logger.info(f"User {user.username} trying to access team #{team.id}, when it's not part of it.")
                raise NoPermissionsError("You're not part of this team!",
                                         TeamResponseStatus.NOT_ENOUGH_PERMISSIONS.value)

    @classmethod
    def authenticate_channel(cls, authentication, channel_role_verifying=lambda _: True):
        logger = logging.getLogger(cls.__name__)

        try:
            user = cls.authenticate_team(authentication, lambda user: TeamRoles.is_team_moderator(user))
            user.channel_id = authentication.channel_id
            user.is_channel_creator = False
            return user
        except NoPermissionsError:

            user = cls.authenticate_team(authentication)
            channel_user = UserDatabaseClient.get_channel_user_by_ids(user.id, authentication.channel_id)

            if channel_user is not None:
                if channel_role_verifying(channel_user.is_channel_creator):
                    logger.info(f"User {user.username} authenticated as channel #{authentication.channel_id} creator.")
                    return channel_user
                else:
                    raise NoPermissionsError("You don't have enough permissions to perform this action.",
                                             TeamResponseStatus.NOT_ENOUGH_PERMISSIONS.value)
            else:
                channel = ChannelDatabaseClient.get_channel_by_id(authentication.channel_id)

                if channel is None:
                    logger.info(f"Chanel #{authentication.channel_id} not found.")
                    raise ChannelNotFoundError("Channel not found.", ChannelResponseStatus.CHANNEL_NOT_FOUND.value)
                else:
                    logger.info(f"User {user.username} trying to access channel #{channel.channel_id}, "
                                f"when it's not part of it.")
                    raise NoPermissionsError("You're not part of this channel!",
                                             TeamResponseStatus.NOT_ENOUGH_PERMISSIONS.value)
