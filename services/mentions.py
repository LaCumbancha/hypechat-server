from daos.database import *
from sqlalchemy import exc

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
                new_mention = TableEntryBuilder.new_mention(message_id=message.message_id, user_id=mention)
                DatabaseClient.add(new_mention)

            DatabaseClient.commit()
            cls.logger().debug(f"{len(mentions)} mentions saved for message #{message.message_id}.")
        except exc.IntegrityError:
            DatabaseClient.rollback()
            cls.logger().error(f"Couldn't save mentions for message #{message.message_id}.")

    @classmethod
    def get_mentions(cls, message_id):
        db_mentions = DatabaseClient.get_mentions_by_message(message_id)

        mentions = []
        for mention in db_mentions:
            mentions += [{
                "user_id": mention.user_id,
                "username": mention.username,
                "first_name": mention.first_name,
                "last_name": mention.last_name
            }]

        return mentions
