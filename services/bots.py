from daos.database import DatabaseClient
from daos.users import UserDatabaseClient
from daos.bots import BotDatabaseClient

from dtos.models.bots import Bot
from dtos.responses.bots import *
from dtos.responses.clients import *

from models.constants import UserRoles
from models.authentication import Authenticator

from sqlalchemy.exc import IntegrityError

import logging


class BotService:

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
                callback=bot_data.callback
            )
            BotDatabaseClient.add_bot(new_bot)
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
