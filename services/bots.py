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

from sqlalchemy.exc import IntegrityError

import json
import logging
import requests


class BotService:

    EMPTY_TEXT = ""
    BOT_MENTION_FORMAT = "@{} "

    @classmethod
    def logger(cls):
        return logging.getLogger(cls.__name__)

    @classmethod
    def create_bot(cls, bot_data):
        admin = Authenticator.authenticate_team(bot_data.authentication, UserRoles.is_admin)

        try:
            new_client = UserDatabaseClient.add_client()
            new_bot = Bot(
                bot_id=new_client.id,
                team_id=admin.team_id,
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
                "team_id": message.team_id,
                "chat_id": message.receiver_id
            }
            headers = {"X-Auth-Token": bot.token}
            requests.post(url=bot.callback, data=json.dumps(body), headers=headers)

    @classmethod
    def _parse_message(cls, text, bot_name):
        return text.replace(cls.BOT_MENTION_FORMAT.format(bot_name), cls.EMPTY_TEXT)
