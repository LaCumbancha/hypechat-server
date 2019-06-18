from app import db
from sqlalchemy import and_, or_, literal

from tables.users import *
from tables.teams import *
from tables.channels import *
from tables.messages import *
from models.constants import ChannelVisibilities, SendMessageType, TeamRoles


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
    def get_client_by_id(cls, client_id):
        return db.session.query(ClientTableEntry).filter(ClientTableEntry.client_id == client_id).one_or_none()

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
    def get_team_by_name(cls, team_name):
        return db.session.query(TeamTableEntry).filter(TeamTableEntry.team_name == team_name).one_or_none()

    @classmethod
    def get_team_invite(cls, team_id, email):
        return db.session.query(TeamsInvitesTableEntry).filter(
            TeamsInvitesTableEntry.team_id == team_id,
            TeamsInvitesTableEntry.email == email
        ).one_or_none()

    @classmethod
    def get_team_invite_by_token(cls, token, email):
        return db.session.query(TeamsInvitesTableEntry).filter(
            TeamsInvitesTableEntry.invite_token == token,
            TeamsInvitesTableEntry.email == email
        ).one_or_none()

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
    def get_all_team_users_by_team_id(cls, team_id):
        return db.session.query(
            UserTableEntry.user_id,
            UserTableEntry.username,
            UserTableEntry.email,
            UserTableEntry.first_name,
            UserTableEntry.last_name,
            UserTableEntry.profile_pic,
            UserTableEntry.online,
            UsersByTeamsTableEntry.role
        ).join(
            UsersByTeamsTableEntry,
            and_(
                UserTableEntry.user_id == UsersByTeamsTableEntry.user_id,
                UsersByTeamsTableEntry.team_id == team_id
            )
        ).all()

    @classmethod
    def get_all_team_users_by_likely_name(cls, team_id, username):
        return db.session.query(
            UserTableEntry
        ).join(
            UsersByTeamsTableEntry,
            and_(
                UsersByTeamsTableEntry.user_id == UserTableEntry.user_id,
                UsersByTeamsTableEntry.team_id == team_id,
                UserTableEntry.username.like(f"%{username}%")
            )
        ).all()

    @classmethod
    def get_all_team_channels_by_team_id(cls, team_id):
        return db.session.query(ChannelTableEntry).filter(ChannelTableEntry.team_id == team_id).all()

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
    def get_user_in_team_by_email(cls, email, team_id):
        return db.session.query(
            UserTableEntry.user_id
        ).join(
            UsersByTeamsTableEntry,
            and_(
                UsersByTeamsTableEntry.team_id == team_id,
                UserTableEntry.user_id == UsersByTeamsTableEntry.user_id,
                UserTableEntry.email == email
            )
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

    @classmethod
    def get_direct_messages_previews(cls, user_id, team_id):
        chats = db.session.query(ChatTableEntry).filter(ChatTableEntry.user_id == user_id).subquery("sq1")

        last_messages_mixed = db.session.query(
            func.least(MessageTableEntry.sender_id, MessageTableEntry.receiver_id).label("user1"),
            func.greatest(MessageTableEntry.sender_id, MessageTableEntry.receiver_id).label("user2"),
            func.max(MessageTableEntry.timestamp).label("maxtimestamp")
        ).filter(and_(
            or_(
                MessageTableEntry.receiver_id == user_id,
                MessageTableEntry.sender_id == user_id
            ),
            MessageTableEntry.team_id == team_id,
            MessageTableEntry.send_type == SendMessageType.DIRECT.value
        )).group_by(
            func.least(MessageTableEntry.sender_id, MessageTableEntry.receiver_id),
            func.greatest(MessageTableEntry.sender_id, MessageTableEntry.receiver_id)
        ).subquery("sq2")

        return db.session.query(
            MessageTableEntry.message_id,
            MessageTableEntry.sender_id,
            MessageTableEntry.receiver_id,
            UserTableEntry.username,
            UserTableEntry.first_name,
            UserTableEntry.last_name,
            UserTableEntry.profile_pic,
            UserTableEntry.online,
            MessageTableEntry.content,
            MessageTableEntry.message_type,
            MessageTableEntry.timestamp,
            chats.c.unseen
        ).join(
            last_messages_mixed,
            and_(
                or_(
                    MessageTableEntry.sender_id == last_messages_mixed.c.user1,
                    MessageTableEntry.sender_id == last_messages_mixed.c.user2,
                ),
                or_(
                    MessageTableEntry.receiver_id == last_messages_mixed.c.user1,
                    MessageTableEntry.receiver_id == last_messages_mixed.c.user2,
                ),
                MessageTableEntry.timestamp == last_messages_mixed.c.maxtimestamp,
                MessageTableEntry.send_type == SendMessageType.DIRECT.value
            )
        ).join(
            chats,
            and_(
                or_(
                    MessageTableEntry.sender_id == chats.c.chat_id,
                    MessageTableEntry.receiver_id == chats.c.chat_id,
                ),
                or_(
                    MessageTableEntry.sender_id == chats.c.user_id,
                    MessageTableEntry.receiver_id == chats.c.user_id,
                )
            )
        ).join(
            UserTableEntry,
            or_(
                and_(
                    UserTableEntry.user_id == last_messages_mixed.c.user1,
                    UserTableEntry.user_id != user_id
                ),
                and_(
                    UserTableEntry.user_id == last_messages_mixed.c.user2,
                    UserTableEntry.user_id != user_id
                )
            )
        ).all()

    @classmethod
    def get_channel_messages_previews(cls, user_id, team_id):
        chats = db.session.query(ChatTableEntry).filter(ChatTableEntry.user_id == user_id).subquery("sq1")

        last_messages = db.session.query(
            MessageTableEntry.receiver_id.label("channel_id"),
            func.max(MessageTableEntry.timestamp).label("maxtimestamp")
        ).filter(and_(
            MessageTableEntry.team_id == team_id,
            MessageTableEntry.send_type == SendMessageType.CHANNEL.value
        )).group_by(
            MessageTableEntry.receiver_id
        ).subquery("sq2")

        return db.session.query(
            MessageTableEntry.message_id,
            MessageTableEntry.receiver_id.label("chat_id"),
            ChannelTableEntry.name.label("chat_name"),
            UserTableEntry.profile_pic.label("chat_picture"),
            MessageTableEntry.sender_id.label("sender_id"),
            UserTableEntry.username.label("sender_username"),
            MessageTableEntry.content.label("content"),
            MessageTableEntry.message_type,
            MessageTableEntry.timestamp.label("message_timestamp"),
            chats.c.unseen.label("unseen_offset")
        ).join(
            last_messages,
            and_(
                MessageTableEntry.receiver_id == last_messages.c.channel_id,
                MessageTableEntry.timestamp == last_messages.c.maxtimestamp
            )
        ).join(
            chats,
            and_(
                MessageTableEntry.team_id == chats.c.team_id,
                MessageTableEntry.receiver_id == chats.c.chat_id
            )
        ).join(
            UserTableEntry,
            UserTableEntry.user_id == MessageTableEntry.sender_id
        ).join(
            ChannelTableEntry,
            ChannelTableEntry.channel_id == MessageTableEntry.receiver_id
        ).all()

    @classmethod
    def get_chat_by_ids(cls, user_id, chat_id, team_id):
        return db.session.query(ChatTableEntry).filter(and_(
            ChatTableEntry.user_id == user_id,
            ChatTableEntry.chat_id == chat_id,
            ChatTableEntry.team_id == team_id
        )).one_or_none()

    @classmethod
    def get_channel_chat(cls, chat_id, team_id, offset, limit):
        return db.session.query(
            MessageTableEntry.message_id,
            MessageTableEntry.sender_id,
            MessageTableEntry.receiver_id,
            MessageTableEntry.team_id,
            MessageTableEntry.content,
            MessageTableEntry.message_type,
            MessageTableEntry.timestamp,
            UserTableEntry.username,
            UserTableEntry.first_name,
            UserTableEntry.last_name,
            UserTableEntry.profile_pic,
            UserTableEntry.online
        ).join(
            UserTableEntry,
            MessageTableEntry.sender_id == UserTableEntry.user_id
        ).filter(and_(
            MessageTableEntry.team_id == team_id,
            MessageTableEntry.receiver_id == chat_id
        )).offset(offset).limit(limit).all()

    @classmethod
    def get_direct_chat(cls, user_id, chat_id, team_id, offset, limit):
        return db.session.query(
            MessageTableEntry.message_id,
            MessageTableEntry.sender_id,
            MessageTableEntry.receiver_id,
            MessageTableEntry.team_id,
            MessageTableEntry.content,
            MessageTableEntry.message_type,
            MessageTableEntry.timestamp,
            UserTableEntry.username,
            UserTableEntry.profile_pic,
            UserTableEntry.first_name,
            UserTableEntry.last_name,
            UserTableEntry.online
        ).join(
            UserTableEntry,
            MessageTableEntry.sender_id == UserTableEntry.user_id
        ).filter(and_(
            MessageTableEntry.team_id == team_id,
            or_(
                and_(
                    MessageTableEntry.sender_id == user_id,
                    MessageTableEntry.receiver_id == chat_id),
                and_(
                    MessageTableEntry.sender_id == chat_id,
                    MessageTableEntry.receiver_id == user_id)
            ),
        )).offset(offset).limit(limit).all()

    @classmethod
    def get_message_direct_receiver_by_ids(cls, user_id, team_id):
        return db.session.query(
            UserTableEntry.user_id,
            UsersByTeamsTableEntry.team_id,
            literal(True).label("is_user")
        ).join(
            UsersByTeamsTableEntry,
            and_(
                UsersByTeamsTableEntry.user_id == UserTableEntry.user_id,
                UsersByTeamsTableEntry.user_id == user_id,
                UsersByTeamsTableEntry.team_id == team_id
            )
        ).one_or_none()

    @classmethod
    def get_message_channel_receiver_by_ids(cls, channel_id):
        return db.session.query(
            ChannelTableEntry.team_id,
            literal(False).label("is_user")
        ).filter(
            ChannelTableEntry.channel_id == channel_id
        ).one_or_none()

    @classmethod
    def get_channel_members(cls, channel_id, ignored_user_id=None):
        return db.session.query(UsersByChannelsTableEntry).filter(and_(
            UsersByChannelsTableEntry.channel_id == channel_id,
            UsersByChannelsTableEntry.user_id != ignored_user_id
        )).all()

    @classmethod
    def get_forbidden_word_by_word(cls, team_id, word):
        return db.session.query(ForbiddenWordTableEntry).filter(
            ForbiddenWordTableEntry.team_id == team_id,
            ForbiddenWordTableEntry.word == word
        ).one_or_none()

    @classmethod
    def get_forbidden_word_by_id(cls, team_id, word_id):
        return db.session.query(ForbiddenWordTableEntry).filter(
            ForbiddenWordTableEntry.team_id == team_id,
            ForbiddenWordTableEntry.id == word_id
        ).one_or_none()

    @classmethod
    def get_forbidden_words_by_team_id(cls, team_id):
        return db.session.query(ForbiddenWordTableEntry).filter(
            ForbiddenWordTableEntry.team_id == team_id
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
    def new_team(cls, team_name, picture=None, location=None, description=None, welcome_message=None):
        return TeamTableEntry(
            team_name=team_name,
            picture=picture,
            location=location,
            description=description,
            welcome_message=welcome_message
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
    def new_user_by_team(cls, user_id, team_id, role=TeamRoles.MEMBER.value):
        return UsersByTeamsTableEntry(user_id=user_id, team_id=team_id, role=role)

    @classmethod
    def new_user_by_channel(cls, user_id, channel_id):
        return UsersByChannelsTableEntry(user_id=user_id, channel_id=channel_id)

    @classmethod
    def new_mention(cls, message_id, user_id):
        return MentionsByMessagesTableEntry(message_id=message_id, user_id=user_id)

    @classmethod
    def new_message(cls, sender_id, receiver_id, team_id, content, send_type, message_type):
        return MessageTableEntry(
            sender_id=sender_id,
            receiver_id=receiver_id,
            team_id=team_id,
            content=content,
            send_type=send_type,
            message_type=message_type
        )

    @classmethod
    def new_chat(cls, user_id, chat_id, team_id, offset):
        return ChatTableEntry(
            user_id=user_id,
            chat_id=chat_id,
            team_id=team_id,
            unseen_offset=offset
        )

    @classmethod
    def new_team_invite(cls, team_id, email, invite_token):
        return TeamsInvitesTableEntry(
            team_id=team_id,
            email=email,
            invite_token=invite_token
        )

    @classmethod
    def new_forbidden_word(cls, word, team_id):
        return ForbiddenWordTableEntry(word=word, team_id=team_id)
