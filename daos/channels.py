from app import db

from daos.builder import TableEntryBuilder, ModelBuilder
from tables.channels import *
from dtos.models.channels import *


class ChannelDatabaseClient:

    @classmethod
    def get_channel_by_id(cls, channel_id):
        channel_entry = db.session.query(ChannelTableEntry).filter(
            ChannelTableEntry.channel_id == channel_id
        ).one_or_none()
        return ModelBuilder.to_channel(channel_entry)
