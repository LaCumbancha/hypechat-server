from app import db
from services.notifications import NotificationService
from tables.users import UserTableEntry
from tables.messages import MentionsByMessagesTableEntry
from sqlalchemy import exc, and_

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
                new_mention = MentionsByMessagesTableEntry(
                    message_id=message.message_id,
                    user_id=mention
                )
                db.session.add(new_mention)
                db.session.flush()
                NotificationService.notify_mention(message, mention)

            db.session.commit()
            cls.logger().debug(f"{len(mentions)} mentions saved for message #{message.message_id}.")
        except exc.IntegrityError:
            db.session.rollback()
            cls.logger().error(f"Couldn't save mentions for message #{message.message_id}.")

    @classmethod
    def get_mentions(cls, message_id):
        db_mentions = db.session.query(
            UserTableEntry.user_id,
            UserTableEntry.username,
            UserTableEntry.first_name,
            UserTableEntry.last_name
        ).join(
            MentionsByMessagesTableEntry,
            and_(
                MentionsByMessagesTableEntry.user_id == UserTableEntry.user_id,
                MentionsByMessagesTableEntry.message_id == message_id
            )
        ).all()

        mentions = []
        for mention in db_mentions:
            mentions += [{
                "user_id": mention.user_id,
                "username": mention.username,
                "first_name": mention.first_name,
                "last_name": mention.last_name
            }]

        return mentions
