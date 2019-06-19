from daos.database import DatabaseClient
from daos.messages import MessageDatabaseClient

from dtos.models.messages import Mention

from sqlalchemy.exc import IntegrityError

import logging


class MentionService:

    @classmethod
    def logger(cls):
        return logging.getLogger(cls.__name__)

    @classmethod
    def save_mentions(cls, message, mentions):
        cls.logger().debug(f"Saving mentions from message #{message.message_id}.")

        try:
            for mention in mentions:
                new_mention = Mention(message_id=message.message_id, client_id=mention)
                MessageDatabaseClient.add_mention(new_mention)

            DatabaseClient.commit()
            cls.logger().debug(f"{len(mentions)} mentions saved for message #{message.message_id}.")
        except IntegrityError:
            DatabaseClient.rollback()
            cls.logger().error(f"Couldn't save mentions for message #{message.message_id}.")

    @classmethod
    def get_mentions(cls, message_id):
        db_mentions = MessageDatabaseClient.get_mentions_by_message(message_id)

        mentions = []
        for mention in db_mentions:
            mentions += [{
                "user_id": mention.id,
                "username": mention.username,
                "first_name": mention.first_name,
                "last_name": mention.last_name
            }]

        return mentions
