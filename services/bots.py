from daos.bots import BotDatabaseClient
from daos.database import DatabaseClient
from daos.users import UserDatabaseClient
from daos.teams import TeamDatabaseClient

from dtos.models.bots import Bot
from dtos.models.teams import TeamUser
from dtos.responses.bots import *
from dtos.responses.clients import *

from models.constants import UserRoles, TeamRoles
from models.authentication import Authenticator

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

import os
import logging
import requests


class BotService:
    TITO_ID = os.getenv("TITO_ID")
    EMPTY_TEXT = ""
    BOT_MENTION_FORMAT = "@{} "
    TITO_WELCOME_PARAMS = "welcome-user"

    @classmethod
    def logger(cls):
        return logging.getLogger(cls.__name__)

    @classmethod
    def register_tito(cls, team_id):
        try:
            team_tito = TeamUser(
                user_id=cls.TITO_ID,
                team_id=team_id,
                role=TeamRoles.BOT.value
            )
            TeamDatabaseClient.add_team_user(team_tito)
            DatabaseClient.commit()
            cls.logger().info(f"Tito added to team #{team_id}.")
        except SQLAlchemyError as exc:
            DatabaseClient.rollback()
            cls.logger().error(f"Failing to register Tito into team #{team_id}.", exc)
            raise

    @classmethod
    def tito_welcome(cls, user_id, team_id):
        bot = BotDatabaseClient.get_bot_by_id(cls.TITO_ID)
        team = TeamDatabaseClient.get_team_by_id(team_id)

        if bot is not None and team.welcome_message is not None:
            body = {
                "params": cls.TITO_WELCOME_PARAMS,
                "message": team.welcome_message,
                "user_id": user_id,
                "team_id": team_id
            }
            headers = {"X-Auth-Token": bot.token}
            requests.post(url=bot.callback, json=body, headers=headers)
            cls.logger().info(f"Tito notified to welcome user #{user_id} to team #{team_id}")
        elif team.welcome_message is not None:
            cls.logger().info(f"There's no message for Tito to welcome user #{user_id}.")

    @classmethod
    def create_bot(cls, bot_data):
        admin = Authenticator.authenticate_team(bot_data.authentication, UserRoles.is_admin)

        try:
            new_client = UserDatabaseClient.add_client()
            new_bot = Bot(
                bot_id=new_client.id,
                name=bot_data.name,
                callback=bot_data.callback,
                token=Authenticator.generate(new_client.id)
            )
            BotDatabaseClient.add_bot(new_bot)
            team_bot = TeamUser(
                user_id=new_client.id,
                team_id=admin.team_id,
                role=TeamRoles.BOT.value
            )
            TeamDatabaseClient.add_team_user(team_bot)
            DatabaseClient.commit()
            cls.logger().info(f"Bot #{new_bot.id} created in team {admin.team_id} with callback url {new_bot.callback} "
                              f"by admin {admin.id}.")
            return SuccessfulUserMessageResponse("Bot created.", UserResponseStatus.OK.value)

        except IntegrityError as exc:
            DatabaseClient.rollback()
            if BotDatabaseClient.get_bot_by_name(bot_data.name) is not None:
                cls.logger().info(f"Failing to create bot {bot_data.name}. Name already in use.", exc)
                return BadRequestUserMessageResponse("Name already in use for other bot.",
                                                     UserResponseStatus.ALREADY_REGISTERED.value)
            else:
                cls.logger().info(f"Failing to create bot {bot_data.name}.")
                return UnsuccessfulClientResponse("Couldn't create bot.")

    @classmethod
    def team_bots(cls, user_data):
        user = Authenticator.authenticate_team(user_data)
        bots = BotDatabaseClient.get_team_bots(user.team_id)
        return SuccessfulBotListResponse(bots)

    @classmethod
    def process_mention(cls, client_id, message):
        bot = BotDatabaseClient.get_bot_by_id(client_id)

        if bot is not None:
            body = {
                "params": cls._parse_message(message.content, bot.name),
                "user_id": message.sender_id,
                "chat_id": message.receiver_id,
                "team_id": message.team_id
            }
            headers = {"X-Auth-Token": bot.token}
            requests.post(url=bot.callback, json=body, headers=headers)

    @classmethod
    def _parse_message(cls, text, bot_name):
        return text.replace(cls.BOT_MENTION_FORMAT.format(bot_name), cls.EMPTY_TEXT)
