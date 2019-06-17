from app import db
from sqlalchemy import and_

from tables.users import UserTableEntry, UsersByTeamsTableEntry, UsersByChannelsTableEntry
from tables.teams import TeamTableEntry
from tables.channels import ChannelTableEntry


class DatabaseClient:

    @classmethod
    def get_user_by_id(cls, user_id):
        return db.session.query(UserTableEntry).filter(UserTableEntry.user_id == user_id).one_or_none()

    @classmethod
    def get_team_by_id(cls, team_id):
        return db.session.query(TeamTableEntry).filter(TeamTableEntry.team_id == team_id).one_or_none()

    @classmethod
    def get_channel_by_id(cls, channel_id):
        return db.session.query(ChannelTableEntry).filter(ChannelTableEntry.channel_id == channel_id).one_or_none()

    @classmethod
    def get_team_user_by_ids(cls, user_id, team_id):
        return db.session.query(
            UserTableEntry.user_id,
            UserTableEntry.username,
            UserTableEntry.email,
            UserTableEntry.first_name,
            UserTableEntry.last_name,
            UserTableEntry.profile_pic,
            UserTableEntry.online,
            UsersByTeamsTableEntry.team_id,
            UsersByTeamsTableEntry.role
        ).join(
            UsersByTeamsTableEntry,
            and_(
                UsersByTeamsTableEntry.user_id == UserTableEntry.user_id,
                UsersByTeamsTableEntry.user_id == user_id,
                UsersByTeamsTableEntry.team_id == team_id
            )
        ).one_or_none()

    @classmethod
    def get_channel_user_by_ids(cls, user_id, channel_id):
        return db.session.query(
            UserTableEntry.user_id,
            UserTableEntry.username,
            UserTableEntry.email,
            UserTableEntry.first_name,
            UserTableEntry.last_name,
            UserTableEntry.profile_pic,
            UserTableEntry.online,
            UsersByChannelsTableEntry.channel_id,
            ChannelTableEntry.creator
        ).join(
            UsersByChannelsTableEntry,
            and_(
                UsersByChannelsTableEntry.user_id == UserTableEntry.user_id,
                UsersByChannelsTableEntry.user_id == user_id,
                UsersByChannelsTableEntry.channel_id == channel_id
            )
        ).join(
            ChannelTableEntry,
            UsersByChannelsTableEntry.channel_id == ChannelTableEntry.channel_id
        ).one_or_none()
