from app import db
from sqlalchemy import and_, or_, literal, func

from daos.database import DatabaseClient
from daos.mappers.messages import MessageDatabaseMapper, MessageModelMapper

from tables.users import UserTableEntry, UsersByTeamsTableEntry
from tables.channels import ChannelTableEntry
from tables.messages import MessageTableEntry, ChatTableEntry, MentionsByMessagesTableEntry

from models.constants import SendMessageType


class MessageDatabaseClient:

    @classmethod
    def add_message(cls, message):
        message_entry = MessageDatabaseMapper.to_message(message)
        DatabaseClient.add(message_entry)

    @classmethod
    def add_chat(cls, chat):
        chat_entry = MessageDatabaseMapper.to_chat(chat)
        DatabaseClient.add(chat_entry)

    @classmethod
    def add_or_update_chat(cls, chat):
        chat_entry = db.session.query(ChatTableEntry).filter(
            ChatTableEntry.user_id == chat.user_id,
            ChatTableEntry.chat_id == chat.chat_id,
            ChatTableEntry.team_id == chat.team_id
        ).one_or_none()

        if chat_entry is not None:
            chat_entry.unseen_offset = chat.offset
        else:
            chat_entry = MessageDatabaseMapper.to_chat(chat)

        DatabaseClient.add(chat_entry)

    @classmethod
    def add_mention(cls, mention):
        mention_entry = MessageDatabaseMapper.to_mention(mention)
        DatabaseClient.add(mention_entry)

    @classmethod
    def get_mentions_by_message(cls, message_id):
        mentions = db.session.query(
            MentionsByMessagesTableEntry.client_id,
            UserTableEntry.username,
            UserTableEntry.first_name,
            UserTableEntry.last_name,
            ChannelTableEntry.name.label("channel_name"),
            UserTableEntry.user_id.label("is_user")
        ).outerjoin(
            UserTableEntry,
            UserTableEntry.user_id == MentionsByMessagesTableEntry.client_id
        ).outerjoin(
            ChannelTableEntry,
            ChannelTableEntry.channel_id == MentionsByMessagesTableEntry.client_id
        ).filter(
            MentionsByMessagesTableEntry.message_id == message_id
        ).all()
        return MessageModelMapper.to_mentions(mentions)

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

        last_messages = db.session.query(
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

        return MessageModelMapper.to_direct_messages_previews(last_messages)

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

        messages_previews = db.session.query(
            MessageTableEntry.message_id,
            MessageTableEntry.receiver_id.label("chat_id"),
            ChannelTableEntry.name.label("chat_name"),
            MessageTableEntry.sender_id.label("sender_id"),
            UserTableEntry.username.label("sender_username"),
            UserTableEntry.first_name.label("sender_first_name"),
            UserTableEntry.last_name.label("sender_last_name"),
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

        return MessageModelMapper.to_channel_messages_previews(messages_previews)

    @classmethod
    def get_chat_by_ids(cls, user_id, chat_id, team_id):
        chat = db.session.query(ChatTableEntry).filter(and_(
            ChatTableEntry.user_id == user_id,
            ChatTableEntry.chat_id == chat_id,
            ChatTableEntry.team_id == team_id
        )).one_or_none()
        return MessageModelMapper.to_chat(chat)

    @classmethod
    def get_channel_chat(cls, chat_id, team_id, offset, limit):
        chat = db.session.query(
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
        return MessageModelMapper.to_messages_chat(chat)

    @classmethod
    def get_direct_chat(cls, user_id, chat_id, team_id, offset, limit):
        chat = db.session.query(
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
        return MessageModelMapper.to_messages_chat(chat)

    @classmethod
    def get_message_direct_receiver_by_ids(cls, user_id, team_id):
        receiver = db.session.query(
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
        return MessageModelMapper.to_message_receiver(receiver)

    @classmethod
    def get_message_channel_receiver_by_ids(cls, channel_id):
        receiver = db.session.query(
            ChannelTableEntry.team_id,
            literal(False).label("is_user")
        ).filter(
            ChannelTableEntry.channel_id == channel_id
        ).one_or_none()
        return MessageModelMapper.to_message_receiver(receiver)

    @classmethod
    def get_team_messages_stats(cls, team_id):
        stats = db.session.query(
            MessageTableEntry.send_type,
            func.count().label("messages")
        ).group_by(
            MessageTableEntry.send_type
        ).filter(
            MessageTableEntry.team_id == team_id
        ).all()
        return MessageModelMapper.to_stats(stats)
