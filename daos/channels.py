from app import db

from daos.database import DatabaseClient
from daos.builder import TableEntryBuilder, ModelBuilder

from tables.messages import *
from tables.channels import *
from tables.users import *
from tables.teams import *

from sqlalchemy import and_


class ChannelDatabaseClient:

    @classmethod
    def add_channel(cls, channel):
        channel_entry = TableEntryBuilder.to_channel(channel)
        DatabaseClient.add(channel_entry)

    @classmethod
    def add_channel_user(cls, channel_user):
        channel_user_entry = TableEntryBuilder.to_channel_user(channel_user)
        DatabaseClient.add(channel_user_entry)

    @classmethod
    def delete_channel_user(cls, delete_user):
        db.session.query(UsersByChannelsTableEntry).filter(and_(
            UsersByChannelsTableEntry.user_id == delete_user.user_id,
            UsersByChannelsTableEntry.channel_id == delete_user.channel_id
        )).delete()

    @classmethod
    def delete_channel(cls, channel):
        db.session.query(ChannelTableEntry).filter(ChannelTableEntry.channel_id == channel.channel_id).delete()

    @classmethod
    def update_channel(cls, channel):
        channel_entry = db.session.query(ChannelTableEntry).filter(ChannelTableEntry.channel_id == channel.channel_id).one_or_none()
        channel_entry.name = channel.name
        channel_entry.visibility = channel.visibility
        channel_entry.description = channel.description
        channel_entry.welcome_message = channel.welcome_message
        db.session.add(channel_entry)
        db.session.flush()

    @classmethod
    def get_channel_by_id(cls, channel_id):
        channel_entry = db.session.query(ChannelTableEntry).filter(
            ChannelTableEntry.channel_id == channel_id
        ).one_or_none()
        return ModelBuilder.to_channel(channel_entry)

    @classmethod
    def get_channel_by_name(cls, channel_name):
        channel_entry = db.session.query(ChannelTableEntry).filter(
            ChannelTableEntry.name == channel_name
        ).one_or_none()
        return ModelBuilder.to_channel(channel_entry)

    @classmethod
    def get_user_in_channel_by_ids(cls, user_id, channel_id):
        channel_user_entry = db.session.query(UsersByChannelsTableEntry).filter(
            UsersByChannelsTableEntry.user_id == user_id,
            UsersByChannelsTableEntry.channel_id == channel_id
        ).one_or_none()
        return ModelBuilder.to_user_in_channel(channel_user_entry)

    @classmethod
    def get_all_channel_users_by_channel_id(cls, channel_id, ignored_user_id=None):
        users = db.session.query(
            UserTableEntry.user_id,
            UserTableEntry.username,
            UserTableEntry.email,
            UserTableEntry.first_name,
            UserTableEntry.last_name,
            UserTableEntry.profile_pic,
            UserTableEntry.role,
            UserTableEntry.online
        ).join(
            UsersByChannelsTableEntry,
            and_(
                UserTableEntry.user_id == UsersByChannelsTableEntry.user_id,
                UsersByChannelsTableEntry.channel_id == channel_id,
                UsersByChannelsTableEntry.user_id != ignored_user_id
            )
        ).all()
        return ModelBuilder.to_public_users(users)
