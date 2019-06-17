from app import db
from sqlalchemy import and_, literal

from tables.users import *
from tables.teams import *
from tables.channels import *
from tables.messages import *
from models.constants import ChannelVisibilities


class DatabaseClient:

    @classmethod
    def commit(cls):
        db.session.commit()

    @classmethod
    def rollback(cls):
        db.session.rollback()

    @classmethod
    def add(cls, entry):
        db.session.add(entry)
        db.session.flush()

    @classmethod
    def delete(cls, entry):
        db.session.delete(entry)
        db.session.flush()

    @classmethod
    def get_user_by_id(cls, user_id):
        return db.session.query(UserTableEntry).filter(UserTableEntry.user_id == user_id).one_or_none()

    @classmethod
    def get_user_by_facebook_id(cls, facebook_id):
        return db.session.query(UserTableEntry).filter(UserTableEntry.facebook_id == facebook_id).one_or_none()

    @classmethod
    def get_user_by_email(cls, user_email):
        return db.session.query(UserTableEntry).filter(UserTableEntry.email == user_email).one_or_none()

    @classmethod
    def get_user_by_username(cls, username):
        return db.session.query(UserTableEntry).filter(UserTableEntry.username == username).one_or_none()

    @classmethod
    def get_user_teams_by_user_id(cls, user_id, is_admin=False):
        if is_admin:
            return db.session.query(
                TeamTableEntry.team_id,
                TeamTableEntry.team_name,
                TeamTableEntry.picture,
                TeamTableEntry.location,
                TeamTableEntry.description,
                TeamTableEntry.welcome_message,
                literal(None).label("role")
            ).all()
        else:
            return db.session.query(
                TeamTableEntry.team_id,
                TeamTableEntry.team_name,
                TeamTableEntry.picture,
                TeamTableEntry.location,
                TeamTableEntry.description,
                TeamTableEntry.welcome_message,
                UsersByTeamsTableEntry.role
            ).join(
                UsersByTeamsTableEntry,
                and_(
                    UsersByTeamsTableEntry.user_id == user_id,
                    UsersByTeamsTableEntry.team_id == TeamTableEntry.team_id
                )
            ).all()

    @classmethod
    def get_user_profile(cls, user):
        if len(cls.get_user_teams_by_user_id(user.user_id)) > 0:
            return db.session.query(
                UserTableEntry.user_id,
                UserTableEntry.username,
                UserTableEntry.email,
                UserTableEntry.first_name,
                UserTableEntry.last_name,
                UserTableEntry.profile_pic,
                UserTableEntry.role,
                TeamTableEntry.team_id,
                TeamTableEntry.team_name,
                TeamTableEntry.picture,
                TeamTableEntry.location,
                TeamTableEntry.description,
                TeamTableEntry.welcome_message,
                UsersByTeamsTableEntry.role
            ).join(
                UsersByTeamsTableEntry,
                UsersByTeamsTableEntry.user_id == UserTableEntry.user_id
            ).join(
                TeamTableEntry,
                UsersByTeamsTableEntry.team_id == TeamTableEntry.team_id
            ).filter(
                UserTableEntry.user_id == user.user_id
            ).all()
        else:
            return user

    @classmethod
    def get_team_by_id(cls, team_id):
        return db.session.query(TeamTableEntry).filter(TeamTableEntry.team_id == team_id).one_or_none()

    @classmethod
    def get_channel_by_id(cls, channel_id):
        return db.session.query(ChannelTableEntry).filter(ChannelTableEntry.channel_id == channel_id).one_or_none()

    @classmethod
    def get_channel_by_name(cls, channel_name):
        return db.session.query(ChannelTableEntry).filter(
            ChannelTableEntry.name == channel_name
        ).one_or_none()

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
            ChannelTableEntry.channel_id,
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

    @classmethod
    def get_all_channel_users_by_channel_id(cls, channel_id):
        return db.session.query(
            UserTableEntry.user_id,
            UserTableEntry.username,
            UserTableEntry.email,
            UserTableEntry.first_name,
            UserTableEntry.last_name,
            UserTableEntry.profile_pic,
            UserTableEntry.online
        ).join(
            UsersByChannelsTableEntry,
            and_(
                UserTableEntry.user_id == UsersByChannelsTableEntry.user_id,
                UsersByChannelsTableEntry.channel_id == channel_id
            )
        ).all()

    @classmethod
    def get_password_recovery_by_id(cls, user_id):
        return db.session.query(PasswordRecoveryTableEntry).filter(
            PasswordRecoveryTableEntry.user_id == user_id
        ).one_or_none()

    @classmethod
    def get_user_in_team_by_ids(cls, user_id, team_id):
        return db.session.query(UsersByTeamsTableEntry).filter(
            UsersByTeamsTableEntry.user_id == user_id,
            UsersByTeamsTableEntry.team_id == team_id
        ).one_or_none()

    @classmethod
    def get_user_in_channel_by_ids(cls, user_id, channel_id):
        db.session.query(UsersByChannelsTableEntry).filter(
            UsersByChannelsTableEntry.user_id == user_id,
            UsersByChannelsTableEntry.channel_id == channel_id
        ).one_or_none()

    @classmethod
    def get_mentions_by_message(cls, message_id):
        return db.session.query(
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


class TableEntryBuilder:

    @classmethod
    def new_client(cls):
        return ClientTableEntry()

    @classmethod
    def new_user(cls, user_id, email, role, auth_token, first_name=None, last_name=None, profile_pic=None,
                 username=None, password=None, facebook_id=None):
        return UserTableEntry(
            user_id=user_id,
            facebook_id=facebook_id,
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            profile_pic=profile_pic,
            role=role,
            auth_token=auth_token,
            online=True
        )

    @classmethod
    def new_channel(cls, channel_id, team_id, creator_id, name, description=None, welcome_message=None,
                    visibility=ChannelVisibilities.PUBLIC.value):
        return ChannelTableEntry(
            channel_id=channel_id,
            team_id=team_id,
            creator=creator_id,
            name=name,
            visibility=visibility or ChannelVisibilities.PUBLIC.value,
            description=description,
            welcome_message=welcome_message
        )

    @classmethod
    def new_password_recovery(cls, user_id, token):
        return PasswordRecoveryTableEntry(user_id=user_id, token=token)

    @classmethod
    def new_user_by_channel(cls, user_id, channel_id):
        return UsersByChannelsTableEntry(user_id=user_id, channel_id=channel_id)

    @classmethod
    def new_mention(cls, message_id, user_id):
        return MentionsByMessagesTableEntry(message_id=message_id, user_id=user_id)
