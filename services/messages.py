from daos.database import *
from daos.users import UserDatabaseClient
from daos.teams import TeamDatabaseClient
from daos.channels import ChannelDatabaseClient
from daos.messages import MessageDatabaseClient

from dtos.models.messages import *
from dtos.responses.messages import *

from exceptions.exceptions import *
from models.authentication import Authenticator

from services.notifications import NotificationService
from services.mentions import MentionService

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError

import logging

CHAT_MESSAGE_PAGE = 50


class MessageService:

    @classmethod
    def logger(cls):
        return logging.getLogger(cls.__name__)

    @classmethod
    def get_preview_messages(cls, user_data):
        user = Authenticator.authenticate_team(user_data)

        db_direct_messages = MessageDatabaseClient.get_direct_messages_previews(user.id, user.team_id)
        db_channel_messages = MessageDatabaseClient.get_channel_messages_previews(user.id, user.team_id)
        direct_messages = cls._generate_direct_chats_list(db_direct_messages, user.id, user.team_id)
        channel_messages = cls._generate_channel_chats_list(db_channel_messages, user.team_id)
        total_messages = direct_messages + channel_messages

        cls.logger().info(f"Retrieved {len(total_messages)} chats from user #{user.id} ({user.username}).")
        return ChatsListResponse(total_messages)

    @classmethod
    def _generate_direct_chats_list(cls, last_messages, user_id, team_id):
        word_censor = WordCensor(team_id)
        chats = []

        last_messages.sort(key=lambda msg: msg.timestamp, reverse=True)
        for message in last_messages:
            chats += [{
                "chat_id": message.sender.id if message.sender.id != user_id else message.receiver_id,
                "chat_name": message.chat_name,
                "chat_picture": message.chat_picture,
                "sender": vars(message.sender),
                "mentions": MentionService.get_mentions(message.message_id),
                "content": word_censor.remove_forbidden_words(message),
                "type": message.message_type,
                "timestamp": message.timestamp,
                "unseen": True if (message.offset > 0) else False,
                "offset": message.offset,
            }]

        return chats

    @classmethod
    def _generate_channel_chats_list(cls, last_messages, team_id):
        word_censor = WordCensor(team_id)
        chats = []

        last_messages.sort(key=lambda msg: msg.timestamp, reverse=True)
        for message in last_messages:
            chats += [{
                "chat_id": message.chat_id,
                "chat_name": message.chat_name,
                "chat_picture": message.chat_picture,
                "sender": vars(message.sender),
                "mentions": MentionService.get_mentions(message.message_id),
                "content": word_censor.remove_forbidden_words(message),
                "type": message.message_type,
                "timestamp": message.timestamp,
                "unseen": True if (message.offset > 0) else False,
                "offset": message.offset,
            }]

        return chats

    @classmethod
    def get_messages_from_chat(cls, chat_data):
        user = Authenticator.authenticate_team(chat_data.authentication)
        chat = MessageDatabaseClient.get_chat_by_ids(user.id, chat_data.chat_id, user.team_id)

        if chat is None:
            cls.logger().error(f"User #{user.id} trying to retrieve messages from chat {chat_data.chat_id}, "
                               f"that doesn't exist.")
            raise ChatNotFoundError("Chat not found.", MessageResponseStatus.CHAT_NOT_FOUND.value)
        else:
            is_channel, messages = cls._determinate_messages(user.id, chat_data.chat_id, user.team_id, chat_data.offset)
            unseen_messages = chat.offset
            try:
                chat.offset = 0
                MessageDatabaseClient.add_or_update_chat(chat)
                DatabaseClient.commit()
                cls.logger().error(f"{unseen_messages} messages set as seen for user {user.id} in chat {chat.chat_id}.")
            except IntegrityError:
                DatabaseClient.rollback()
                cls.logger().error(f"Couldn't set seen messages for user {user.id} in chat {chat.chat_id}.")

            cls.logger().info(f"Retrieved {len(messages)} messages from chat {chat_data.chat_id} from user #{user.id}.")
            return MessageListResponse(cls._generate_messages_list(messages, unseen_messages, user.id, user.team_id), is_channel)

    @classmethod
    def _determinate_messages(cls, user_id, chat_id, team_id, offset):
        if ChannelDatabaseClient.get_channel_by_id(chat_id) is not None:
            cls.logger().debug("Retrieving messages from a channel.")
            return True, MessageDatabaseClient.get_channel_chat(chat_id, team_id, offset=offset, limit=CHAT_MESSAGE_PAGE)
        else:
            cls.logger().debug("Retrieving messages from a direct chat.")
            return False, MessageDatabaseClient.get_direct_chat(user_id, chat_id, team_id, offset=offset, limit=CHAT_MESSAGE_PAGE)

    @classmethod
    def _generate_messages_list(cls, messages, unseen_offset, user_id, team_id):
        word_censor = WordCensor(team_id)
        output_messages = []

        messages.sort(key=lambda msg: msg.timestamp, reverse=True)
        for message in messages:

            output_messages += [{
                "sender": vars(message.sender),
                "content": word_censor.remove_forbidden_words(message),
                "mentions": MentionService.get_mentions(message.message_id),
                "type": message.message_type,
                "timestamp": message.timestamp,
                "unseen": True if message.sender.id != user_id and unseen_offset > 0 else False
            }]

            if message.sender.id != user_id:
                unseen_offset -= 1

        return output_messages

    @classmethod
    def send_message(cls, inbox_data):
        user = Authenticator.authenticate_team(inbox_data.authentication)

        if user.id == inbox_data.chat_id:
            raise WrongActionError("You cannot send a message to yourself!", MessageResponseStatus.ERROR.value)

        receiver = cls._determinate_message_receiver(inbox_data.chat_id, user.team_id)
        if receiver is None or receiver.team_id != user.team_id:
            cls.logger().info(f"Trying to send a message to client #{inbox_data.chat_id} who's not part of team "
                              f"{user.team_id}.")
            return BadRequestMessageSentResponse("The receiver it's not part of this team!",
                                                 TeamResponseStatus.USER_NOT_MEMBER.value)

        new_message = Message(
            sender_id=user.id,
            receiver_id=inbox_data.chat_id,
            team_id=user.team_id,
            content=inbox_data.content,
            send_type=SendMessageType.DIRECT.value if receiver.is_user else SendMessageType.CHANNEL.value,
            message_type=inbox_data.message_type
        )

        chat_sender, chat_receivers = cls._increase_chats_offset(user.id, inbox_data.chat_id, user.team_id, receiver.is_user)

        try:
            new_message = MessageDatabaseClient.add_message(new_message)
            if inbox_data.mentions is not None:
                MentionService.save_mentions(new_message, inbox_data.mentions)
            MessageDatabaseClient.add_or_update_chat(chat_sender)
            for chat_receiver in chat_receivers:
                MessageDatabaseClient.add_or_update_chat(chat_receiver)
            DatabaseClient.commit()
            NotificationService.notify_message(new_message, receiver.is_user)
            cls.logger().info(f"Message sent from user #{new_message.sender_id} to client #{new_message.receiver_id}.")
        except IntegrityError:
            DatabaseClient.rollback()
            if UserDatabaseClient.get_client_by_id(inbox_data.chat_id) is None:
                cls.logger().error(f"User #{new_message.sender_id} trying to sent a message to an nonexistent user.")
                raise UserNotFoundError("User not found.", UserResponseStatus.USER_NOT_FOUND.value)
            else:
                cls.logger().error(f"Failing to send message from user #{new_message.sender_id} to client"
                                   f" #{inbox_data.chat_id}.")
                return UnsuccessfulMessageSentResponse("Couldn't sent message.")
        except FlushError:
            cls.logger().error(
                f"Failing to send message from user #{new_message.sender_id} to client #{inbox_data.chat_id} "
                f"due to DB problems.")
            return UnsuccessfulMessageSentResponse("Couldn't sent message.")
        else:
            return SuccessfulMessageSentResponse("Message sent")

    @classmethod
    def _determinate_message_receiver(cls, receiver_id, team_id):
        receiver = MessageDatabaseClient.get_message_direct_receiver_by_ids(receiver_id, team_id)

        if receiver is None:
            cls.logger().debug("Channel message sent.")
            receiver = MessageDatabaseClient.get_message_channel_receiver_by_ids(receiver_id)

        return receiver

    @classmethod
    def _increase_chats_offset(cls, sender_id, receiver_id, team_id, is_direct_message):
        sender_chat = MessageDatabaseClient.get_chat_by_ids(sender_id, receiver_id, team_id)

        if sender_chat is not None:
            cls.logger().debug("Sender chat already exist. Setting sender offset in 0.")
            sender_chat.offset = 0
        else:
            cls.logger().debug("New sender chat. Initializing sender offset in 0.")
            sender_chat = Chat(
                user_id=sender_id,
                chat_id=receiver_id,
                team_id=team_id
            )

        receivers_chat = []

        if is_direct_message:
            cls.logger().debug("Defining receiver chat offset for a Direct Message.")
            receiver_user = MessageDatabaseClient.get_chat_by_ids(receiver_id, sender_id, team_id)

            if receiver_user is not None:
                cls.logger().debug("Receiver chat already exist. Increasing receiver offset by 1.")
                receiver_user.offset += 1
                receivers_chat += [receiver_user]
            else:
                cls.logger().debug("New receiver chat. Initializing receiver offset in 1.")
                receivers_chat += [Chat(
                    user_id=receiver_id,
                    chat_id=sender_id,
                    team_id=team_id,
                    offset=1
                )]

        else:

            cls.logger().debug("Defining receivers chat offset for a Channel Message.")
            channel_members = ChannelDatabaseClient.get_all_channel_users_by_channel_id(receiver_id, sender_id)

            cls.logger().debug(f"Channel has {len(channel_members)} other members.")

            for member in channel_members:
                receiver_user = MessageDatabaseClient.get_chat_by_ids(member.id, receiver_id, team_id)

                if receiver_user:
                    cls.logger().debug(f"Receiving channel member chat already exists. Increasing offset by 1.")
                    receiver_user.offset += 1
                    receivers_chat += [receiver_user]
                else:
                    cls.logger().debug(f"New receiving channel member. Initializing offset in 1.")
                    receivers_chat += [Chat(
                        user_id=member.id,
                        chat_id=receiver_id,
                        team_id=team_id,
                        offset=1
                    )]

        return sender_chat, receivers_chat

    @classmethod
    def messages_stats(cls, user_data):
        admin = Authenticator.authenticate(user_data, UserRoles.is_admin)
        stats = MessageDatabaseClient.get_messages_stats()
        cls.logger().info(f"Admin #{admin.id} retrieved messages stats for {len(stats)} teams.")
        return SuccessfulMessageStatsResponse(stats)


class WordCensor:

    def __init__(self, team_id):
        self.forbidden_words = TeamDatabaseClient.get_forbidden_words_from_team(team_id)

    def remove_forbidden_words(self, message):
        message_content = message.content

        if message.message_type == MessageType.TEXT.value:
            replaceable_words = map(lambda word: f"{word.word}", self.forbidden_words)

            for replaceable_word in replaceable_words:
                message_content = self._replace(message_content, replaceable_word)

        return message_content

    def _replace(self, text, replaceable_text):
        replaceable_length = len(replaceable_text)
        replace_text = "".join(["*" for _ in range(replaceable_length)])
        return text.replace(replaceable_text, replace_text)
