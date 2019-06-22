from tables.messages import MessageTableEntry, ChatTableEntry, MentionsByMessagesTableEntry

from dtos.models.messages import *
from models.constants import SendMessageType

import itertools


class MessageDatabaseMapper:

    @classmethod
    def to_message(cls, message):
        return MessageTableEntry(
            sender_id=message.sender_id,
            receiver_id=message.receiver_id,
            team_id=message.team_id,
            content=message.content,
            send_type=message.send_type,
            message_type=message.message_type
        )

    @classmethod
    def to_chat(cls, chat):
        return ChatTableEntry(
            user_id=chat.user_id,
            chat_id=chat.chat_id,
            team_id=chat.team_id,
            unseen_offset=chat.offset
        )

    @classmethod
    def to_mention(cls, mention):
        return MentionsByMessagesTableEntry(
            message_id=mention.message_id,
            client_id=mention.client_id
        )


class MessageModelMapper:

    @classmethod
    def to_message(cls, message_entry):
        return Message(
            message_id=message_entry.message_id,
            sender_id=message_entry.sender_id,
            receiver_id=message_entry.receiver_id,
            team_id=message_entry.team_id,
            content=message_entry.content,
            send_type=message_entry.send_type,
            message_type=message_entry.message_type
        ) if message_entry is not None else None

    @classmethod
    def to_chat(cls, chat_entry):
        return Chat(
            user_id=chat_entry.user_id,
            chat_id=chat_entry.chat_id,
            team_id=chat_entry.team_id,
            offset=chat_entry.unseen_offset
        ) if chat_entry is not None else None

    @classmethod
    def to_mentions(cls, mentions_entries):
        mentions = []
        for mention_entry in mentions_entries:
            if mention_entry.is_user is not None:
                mentions += [UserMention(
                    user_id=mention_entry.client_id,
                    username=mention_entry.username,
                    first_name=mention_entry.first_name,
                    last_name=mention_entry.last_name
                )]
            elif mention_entry.is_channel is not None:
                mentions += [ChannelMention(
                    channel_id=mention_entry.client_id,
                    channel_name=mention_entry.channel_name
                )]
            else:
                mentions += [BotMention(
                    bot_id=mention_entry.client_id,
                    bot_name=mention_entry.bot_name
                )]
        return mentions

    @classmethod
    def to_direct_messages_previews(cls, last_messages):
        preview_messages = []
        for last_message in last_messages:
            preview_messages += [
                PreviewDirectMessage(
                    message_id=last_message.message_id,
                    sender_id=last_message.sender_id,
                    receiver_id=last_message.receiver_id,
                    chat_username=last_message.username,
                    chat_first_name=last_message.first_name,
                    chat_last_name=last_message.last_name,
                    chat_picture=last_message.profile_pic,
                    chat_online=last_message.online,
                    content=last_message.content,
                    message_type=last_message.message_type,
                    timestamp=last_message.timestamp,
                    offset=last_message.unseen
                )
            ]
        return preview_messages

    @classmethod
    def to_channel_messages_previews(cls, last_messages):
        preview_messages = []
        for last_message in last_messages:
            preview_messages += [
                PreviewChannelMessage(
                    message_id=last_message.message_id,
                    chat_id=last_message.chat_id,
                    chat_name=last_message.chat_name,
                    chat_picture=None,
                    sender_id=last_message.sender_id,
                    sender_username=last_message.sender_username,
                    sender_first_name=last_message.sender_first_name,
                    sender_last_name=last_message.sender_last_name,
                    content=last_message.content,
                    message_type=last_message.message_type,
                    timestamp=last_message.message_timestamp,
                    offset=last_message.unseen_offset
                )
            ]
        return preview_messages

    @classmethod
    def to_messages_chat(cls, messages_entries):
        messages = []
        for message_entry in messages_entries:
            messages += [ChatMessage(
                message_id=message_entry.message_id,
                sender_id=message_entry.sender_id,
                receiver_id=message_entry.receiver_id,
                team_id=message_entry.team_id,
                content=message_entry.content,
                message_type=message_entry.message_type,
                timestamp=message_entry.timestamp,
                username=message_entry.username,
                profile_pic=message_entry.profile_pic,
                first_name=message_entry.first_name,
                last_name=message_entry.last_name,
                online=message_entry.online
            )]
        return messages

    @classmethod
    def to_message_receiver(cls, receiver):
        return MessageReceiver(
            user_id=receiver.user_id if receiver.is_user else None,
            team_id=receiver.team_id,
            is_user=receiver.is_user
        ) if receiver is not None else None

    @classmethod
    def to_stats(cls, stats_entries):
        stats = []
        grouped = itertools.groupby(stats_entries, key=lambda entry: entry.team_id)

        for team_id, messages in grouped:
            direct_messages = 0
            channel_messages = 0

            for message_type in list(messages):
                if message_type[1] == SendMessageType.DIRECT.value:
                    direct_messages = message_type[2]
                elif message_type[1] == SendMessageType.CHANNEL.value:
                    channel_messages = message_type[2]

            stats += [MessageStats(
                team_id=team_id,
                direct=direct_messages,
                channel=channel_messages
            )]

        return stats
