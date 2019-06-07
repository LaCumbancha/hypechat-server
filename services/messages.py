from app import db
from dtos.responses.messages import *
from exceptions.exceptions import *
from models.authentication import Authenticator
from tables.users import *
from tables.messages import *
from tables.channels import *
from sqlalchemy import exc, func, and_, or_, literal
from sqlalchemy.orm import exc as orm

import logging

CHAT_MESSAGE_PAGE = 50


class MessageService:

    @classmethod
    def logger(cls):
        return logging.getLogger(cls.__name__)

    @classmethod
    def get_preview_messages(cls, user_data):
        user = Authenticator.authenticate_team(user_data)

        direct_messages = cls._get_direct_messages_previews(user.user_id, user.team_id)
        channel_messages = cls._get_channel_messages_previews(user.user_id, user.team_id)
        total_messages = direct_messages + channel_messages

        cls.logger().info(f"Retrieved {len(total_messages)} chats from user #{user.user_id} ({user.username}).")
        return ChatsListResponse(cls._generate_chats_list(total_messages))

    @classmethod
    def _get_direct_messages_previews(cls, user_id, team_id):
        cls.logger().debug("Retrieving messages preview from a direct chat.")
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
            MessageTableEntry.team_id == team_id
        )).group_by(
            func.least(MessageTableEntry.sender_id, MessageTableEntry.receiver_id),
            func.greatest(MessageTableEntry.sender_id, MessageTableEntry.receiver_id)
        ).subquery("sq2")

        return db.session.query(
            MessageTableEntry.sender_id,
            MessageTableEntry.receiver_id,
            UserTableEntry.username,
            UserTableEntry.profile_pic,
            MessageTableEntry.text_content,
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
                MessageTableEntry.timestamp == last_messages_mixed.c.maxtimestamp
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
                ),
                MessageTableEntry.team_id == chats.c.team_id
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
    def _get_channel_messages_previews(cls, user_id, team_id):
        return []

    @classmethod
    def _generate_chats_list(cls, last_messages):
        chats = []

        last_messages.sort(key=lambda msg: msg.timestamp, reverse=True)
        for message in last_messages:
            chats += [{
                "sender_id": message.sender_id,
                "receiver_id": message.receiver_id,
                "chat_name": message.username,
                "chat_picture": message.profile_pic,
                "content": message.text_content,
                "timestamp": message.timestamp,
                "unseen": True if (message.unseen > 0) else False,
                "offset": message.unseen
            }]

        return chats

    @classmethod
    def get_messages_from_chat(cls, chat_data):
        user = Authenticator.authenticate_team(chat_data.authentication)

        chat = db.session.query(ChatTableEntry).filter(and_(
            ChatTableEntry.user_id == user.user_id,
            ChatTableEntry.chat_id == chat_data.chat_id,
            ChatTableEntry.team_id == user.team_id
        )).one_or_none()

        if not chat:
            cls.logger().error(
                f"User #{user.user_id} trying to retrieve messages from chat {chat_data.chat_id}, that doesnt' exist.")
            raise ChatNotFoundError("Chat not found.", MessageResponseStatus.CHAT_NOT_FOUND.value)
        else:
            messages = cls._determinate_messages(user.user_id, chat_data.chat_id, user.team_id, chat_data.offset)
            unseen_messages = chat.unseen_offset
            try:
                chat.unseen_offset = 0
                db.session.commit()
                cls.logger().error(
                    f"{unseen_messages} messages set as seen for user {user.user_id} in chat {chat.chat_id}.")
            except exc.IntegrityError:
                db.session().rollback()
                cls.logger().error(f"Couldn't set seen messages for user {user.user_id} in chat {chat.chat_id}.")

            cls.logger().info(
                f"Retrieved {len(messages)} messages from chat {chat_data.chat_id} " +
                f"from user #{user.user_id} ({user.username}).")
            return MessageListResponse(
                cls._generate_messages_list(messages, unseen_messages, user.user_id))

    @classmethod
    def _determinate_messages(cls, user_id, chat_id, team_id, offset):
        if db.session.query(ChannelTableEntry).filter(ChannelTableEntry.channel_id == chat_id).one_or_none():
            cls.logger().debug("Retrieving messages from a channel.")
            return db.session.query(
                MessageTableEntry.message_id,
                MessageTableEntry.sender_id,
                MessageTableEntry.receiver_id,
                MessageTableEntry.team_id,
                MessageTableEntry.text_content,
                MessageTableEntry.timestamp,
                UserTableEntry.username,
                UserTableEntry.profile_pic,
                UserTableEntry.online
            ).join(
                UserTableEntry,
                MessageTableEntry.sender_id == UserTableEntry.user_id
            ).filter(and_(
                MessageTableEntry.team_id == team_id,
                MessageTableEntry.receiver_id == chat_id
            )).offset(offset).limit(CHAT_MESSAGE_PAGE).all()
        else:
            cls.logger().debug("Retrieving messages from a direct chat.")
            return db.session.query(
                MessageTableEntry.message_id,
                MessageTableEntry.sender_id,
                MessageTableEntry.receiver_id,
                MessageTableEntry.team_id,
                MessageTableEntry.text_content,
                MessageTableEntry.timestamp,
                UserTableEntry.username,
                UserTableEntry.profile_pic,
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
            )).offset(offset).limit(CHAT_MESSAGE_PAGE).all()

    @classmethod
    def _generate_messages_list(cls, messages, unseen_offset, user_id):
        output_messages = []

        messages.sort(key=lambda msg: msg.timestamp, reverse=True)
        for message in messages:

            output_messages += [{
                "sender": {
                    "id": message.sender_id,
                    "username": message.username,
                    "profile_pic": message.profile_pic,
                    "online": message.online
                },
                "text_content": message.text_content,
                "timestamp": message.timestamp,
                "seen": False if message.sender_id != user_id and unseen_offset > 0 else True
            }]

            if message.sender_id != user_id:
                unseen_offset -= 1

        return output_messages

    @classmethod
    def send_message(cls, inbox_data):
        user = Authenticator.authenticate_team(inbox_data.authentication)

        if user.user_id == inbox_data.chat_id:
            raise WrongActionError("You cannot send a message to yourself!", MessageResponseStatus.ERROR.value)

        receiver = cls._determinate_message_receiver(inbox_data.chat_id)
        if not receiver or receiver.team_id != user.team_id:
            cls.logger().info(
                f"Trying to send a message to client #{inbox_data.chat_id} who's not part of team {user.team_id}.")
            return BadRequestMessageSentResponse("The receiver it's not part of this team!",
                                                 TeamResponseStatus.USER_NOT_MEMBER.value)

        new_message = MessageTableEntry(
            sender_id=user.user_id,
            receiver_id=inbox_data.chat_id,
            team_id=user.team_id,
            text_content=inbox_data.text_content
        )

        chat_sender, chat_receivers = cls._increase_chats_offset(user.user_id, inbox_data.chat_id, user.team_id,
                                                                 receiver.is_user)

        try:
            db.session.add(new_message)
            db.session.flush()
            db.session.add(chat_sender)
            db.session.flush()
            for chat_receiver in chat_receivers:
                db.session.add(chat_receiver)
                db.session.flush()
            db.session.commit()
            cls.logger().info(f"Message sent from user #{new_message.sender_id} to client #{new_message.receiver_id}.")
        except exc.IntegrityError:
            db.session.rollback()
            if not db.session.query(ClientTableEntry).filter(
                    ClientTableEntry.client_id == inbox_data.chat_id).one_or_none():
                cls.logger().error(
                    f"User #{new_message.sender_id} trying to sent a message to an nonexistent user.")
                raise UserNotFoundError("User not found.", UserResponseStatus.USER_NOT_FOUND.value)
            else:
                cls.logger().error(
                    f"Failing to send message from user #{new_message.sender_id} to client #{inbox_data.chat_id}.")
                return UnsuccessfulMessageSentResponse("Couldn't sent message.")
        except orm.FlushError:
            cls.logger().error(
                f"Failing to send message from user #{new_message.sender_id} to client #{inbox_data.chat_id} "
                f"due to DB problems.")
            return UnsuccessfulMessageSentResponse("Couldn't sent message.")
        else:
            return SuccessfulMessageSentResponse("Message sent")

    @classmethod
    def _determinate_message_receiver(cls, receiver_id):
        receiver = db.session.query(
            UserTableEntry.user_id,
            UsersByTeamsTableEntry.team_id,
            literal(True).label("is_user")
        ).join(
            UsersByTeamsTableEntry,
            and_(
                UsersByTeamsTableEntry.user_id == UserTableEntry.user_id,
                UsersByTeamsTableEntry.user_id == receiver_id
            )
        ).one_or_none()

        if not receiver:
            cls.logger().debug("Channel message sent.")
            receiver = db.session.query(
                ChannelTableEntry.team_id,
                literal(False).label("is_user")
            ).filter(
                ChannelTableEntry.channel_id == receiver_id
            ).one_or_none()

        return receiver

    @classmethod
    def _increase_chats_offset(cls, sender_id, receiver_id, team_id, is_direct_message):
        sender_chat = db.session.query(ChatTableEntry).filter(and_(
            ChatTableEntry.user_id == sender_id,
            ChatTableEntry.chat_id == receiver_id,
            ChatTableEntry.team_id == team_id
        )).one_or_none()

        if sender_chat:
            cls.logger().debug("Sender chat already exist. Setting sender offset in 0.")
            sender_chat.unseen_offset = 0
        else:
            cls.logger().debug("New sender chat. Initializing sender offset in 0.")
            sender_chat = ChatTableEntry(
                user_id=sender_id,
                chat_id=receiver_id,
                team_id=team_id,
                unseen_offset=0
            )

        receivers_chat = []

        if is_direct_message:
            cls.logger().debug("Defining receiver chat offset for a Direct Message.")

            receiver_user = db.session.query(ChatTableEntry).filter(and_(
                ChatTableEntry.user_id == receiver_id,
                ChatTableEntry.chat_id == sender_id,
                ChatTableEntry.team_id == team_id
            )).one_or_none()

            if receiver_user:
                cls.logger().debug("Receiver chat already exist. Increasing receiver offset by 1.")
                receiver_user.unseen_offset += 1
                receivers_chat += [receiver_user]
            else:
                cls.logger().debug("New receiver chat. Initializing receiver offset in 1.")
                receivers_chat += [ChatTableEntry(
                    user_id=receiver_id,
                    chat_id=sender_id,
                    team_id=team_id,
                    unseen_offset=1
                )]

        else:

            cls.logger().debug("Defining receivers chat offset for a Channel Message.")
            channel_members = db.session.query(UsersByChannelsTableEntry).filter(and_(
                UsersByChannelsTableEntry.channel_id == receiver_id,
                UsersByChannelsTableEntry.user_id != sender_id
            )).all()

            cls.logger().debug(f"Channel has {len(channel_members)} members.")

            for member in channel_members:
                receiver_user = db.session.query(ChatTableEntry).filter(and_(
                    ChatTableEntry.user_id == member.user_id,
                    ChatTableEntry.chat_id == receiver_id,
                    ChatTableEntry.team_id == team_id
                )).one_or_none()

                if receiver_user:
                    cls.logger().debug(f"Receiving channel member chat already exists. Increasing offset by 1.")
                    receiver_user.unseen_offset += 1
                    receivers_chat += [receiver_user]
                else:
                    cls.logger().debug(f"New receiving channel member. Initializing offset in 1.")
                    receivers_chat += [ChatTableEntry(
                        user_id=member.user_id,
                        chat_id=receiver_id,
                        team_id=team_id,
                        unseen_offset=1
                    )]

        return sender_chat, receivers_chat
