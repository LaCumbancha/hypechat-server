from app import db
from sqlalchemy import and_, or_, literal

from daos.database import DatabaseClient
from daos.builder import TableEntryBuilder, ModelBuilder
from daos.teams import TeamDatabaseClient

from tables.users import *
from tables.messages import *

from dtos.models.users import *


class MessageDatabaseClient:

    @classmethod
    def add_mention(cls, mention):
        mention_entry = TableEntryBuilder.to_mention(mention)
        DatabaseClient.add(mention_entry)

    @classmethod
    def get_mentions_by_message(cls, message_id):
        mentions = db.session.query(
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
        return ModelBuilder.to_mentions(mentions)
