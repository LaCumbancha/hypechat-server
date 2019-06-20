from app import db
from sqlalchemy import and_

from daos.database import DatabaseClient
from daos.teams import TeamDatabaseClient
from daos.mappers.users import UserDatabaseMapper, UserModelMapper

from tables.users import ClientTableEntry, UserTableEntry, PasswordRecoveryTableEntry, UsersByTeamsTableEntry, \
    UsersByChannelsTableEntry
from tables.teams import TeamTableEntry
from tables.channels import ChannelTableEntry

from dtos.models.users import *


class UserDatabaseClient:

    @classmethod
    def add_client(cls):
        client_entry = ClientTableEntry()
        DatabaseClient.add(client_entry)
        return RegularClient(client_id=client_entry.client_id)

    @classmethod
    def add_user(cls, user):
        user_entry = UserDatabaseMapper.to_user(user)
        DatabaseClient.add(user_entry)

    @classmethod
    def add_password_recovery(cls, password_recovery):
        recovery_entry = UserDatabaseMapper.to_password_recovery(password_recovery)
        DatabaseClient.add(recovery_entry)

    @classmethod
    def delete_password_recovery(cls, password_recovery):
        db.session.query(PasswordRecoveryTableEntry).filter(
            PasswordRecoveryTableEntry.user_id == password_recovery.user_id
        ).delete()

    @classmethod
    def get_client_by_id(cls, client_id):
        client = db.session.query(ClientTableEntry).filter(
            ClientTableEntry.client_id == client_id
        ).one_or_none()
        return UserModelMapper.to_client(client)

    @classmethod
    def get_user_by_id(cls, user_id):
        user_entry = db.session.query(UserTableEntry).filter(UserTableEntry.user_id == user_id).one_or_none()
        return UserModelMapper.to_user(user_entry)

    @classmethod
    def get_user_by_email(cls, user_email):
        user_entry = db.session.query(UserTableEntry).filter(UserTableEntry.email == user_email).one_or_none()
        return UserModelMapper.to_user(user_entry)

    @classmethod
    def get_user_by_username(cls, username):
        user_entry = db.session.query(UserTableEntry).filter(UserTableEntry.username == username).one_or_none()
        return UserModelMapper.to_user(user_entry)

    @classmethod
    def get_user_by_facebook_id(cls, facebook_id):
        user_entry = db.session.query(UserTableEntry).filter(UserTableEntry.facebook_id == facebook_id).one_or_none()
        return UserModelMapper.to_user(user_entry)

    @classmethod
    def get_all_users(cls):
        users_entries = db.session.query(UserTableEntry).all()
        return UserModelMapper.to_users(users_entries)

    @classmethod
    def update_user(cls, user):
        user_entry = db.session.query(UserTableEntry).filter(UserTableEntry.user_id == user.id).one_or_none()
        user_entry.username = user.username
        user_entry.email = user.email
        user_entry.password = user.password
        user_entry.first_name = user.first_name
        user_entry.last_name = user.last_name
        user_entry.profile_pic = user.profile_pic
        user_entry.role = user.role
        user_entry.auth_token = user.token
        user_entry.online = user.online
        db.session.add(user_entry)
        db.session.flush()

    @classmethod
    def get_user_profile(cls, user):
        if len(TeamDatabaseClient.get_user_teams_by_user_id(user.id)) > 0:
            user_with_teams = db.session.query(
                UserTableEntry.user_id,
                UserTableEntry.username,
                UserTableEntry.email,
                UserTableEntry.first_name,
                UserTableEntry.last_name,
                UserTableEntry.profile_pic,
                UserTableEntry.role.label("user_role"),
                TeamTableEntry.team_id,
                TeamTableEntry.team_name,
                TeamTableEntry.picture,
                TeamTableEntry.location,
                TeamTableEntry.description,
                TeamTableEntry.welcome_message,
                UsersByTeamsTableEntry.role.label("team_role")
            ).join(
                UsersByTeamsTableEntry,
                UsersByTeamsTableEntry.user_id == UserTableEntry.user_id
            ).join(
                TeamTableEntry,
                UsersByTeamsTableEntry.team_id == TeamTableEntry.team_id
            ).filter(
                UserTableEntry.user_id == user.id
            ).all()
            return UserModelMapper.to_user_with_teams(user_with_teams)
        else:
            return user

    @classmethod
    def get_team_user_by_ids(cls, user_id, team_id):
        team_user_entry = db.session.query(
            UserTableEntry.user_id,
            UserTableEntry.username,
            UserTableEntry.email,
            UserTableEntry.first_name,
            UserTableEntry.last_name,
            UserTableEntry.profile_pic,
            UserTableEntry.online,
            UserTableEntry.role.label("user_role"),
            UsersByTeamsTableEntry.team_id,
            UsersByTeamsTableEntry.role.label("team_role")
        ).join(
            UsersByTeamsTableEntry,
            and_(
                UsersByTeamsTableEntry.user_id == UserTableEntry.user_id,
                UsersByTeamsTableEntry.user_id == user_id,
                UsersByTeamsTableEntry.team_id == team_id
            )
        ).one_or_none()
        return UserModelMapper.to_team_user(team_user_entry)

    @classmethod
    def get_channel_user_by_ids(cls, user_id, channel_id):
        channel_user = db.session.query(
            UserTableEntry.user_id,
            UserTableEntry.username,
            UserTableEntry.email,
            UserTableEntry.first_name,
            UserTableEntry.last_name,
            UserTableEntry.profile_pic,
            UserTableEntry.online,
            UserTableEntry.role,
            ChannelTableEntry.channel_id,
            ChannelTableEntry.creator,
            ChannelTableEntry.team_id,
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
        return UserModelMapper.to_channel_user(channel_user)

    @classmethod
    def get_password_recovery_by_id(cls, user_id):
        password_entry = db.session.query(PasswordRecoveryTableEntry).filter(
            PasswordRecoveryTableEntry.user_id == user_id
        ).one_or_none()
        return UserModelMapper.to_password_recovery(password_entry)
