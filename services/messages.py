from app import db
from dtos.responses.messages import *
from exceptions.exceptions import *
from models.authentication import Authenticator
from tables.messages import *
from sqlalchemy import exc, and_

import logging


class MessageService:

    @classmethod
    def logger(cls):
        return logging.getLogger(cls.__name__)

    @classmethod
    def get_preview_messages(cls, user_data):
        user = Authenticator.authenticate(user_data)

    @classmethod
    def get_messages_from_direct_chat(cls, chat_data):
        user = Authenticator.authenticate(chat_data)

        chat = db.session.query(ChatTableEntry).filter(and_(ChatTableEntry.user_id == user.user_id,
                                                            ChatTableEntry.chat_id == chat_data.chat_id)).one_or_none()

        if not chat:
            cls.logger().error(
                f"User #{user.user_id} trying to retrieve messages from an nonexistent chat.")
            raise ChatNotFoundError("Chat not found.", MessageResponseStatus.CHAT_NOT_FOUND.value)
        else:
            messages_sent = db.session.query(MessageTableEntry).filter(and_(
                MessageTableEntry.sender_id == user.user_id, MessageTableEntry.receiver_id == chat_data.chat_id)).all()
            messages_received = db.session.query(MessageTableEntry).filter(and_(
                MessageTableEntry.sender_id == chat_data.chat_id, MessageTableEntry.receiver_id == user.user_id)).all()
            return MessageListResponse(cls._generate_message_list(messages_sent, messages_received, chat.unseen_offset))

    @classmethod
    def _generate_message_list(cls, messages_sent, messages_received, unseen_offset):
        messages = []

        messages_received.sort(key=lambda msg: msg.timestamp, reverse=True)
        for message in messages_received:

            if unseen_offset > 0:
                messages += [{
                    "user_id": message.sender_id,
                    "text_content": message.text_content,
                    "timestamp": message.timestamp,
                    "seen": False
                }]
                unseen_offset -= 1
            else:
                messages += [{
                    "user_id": message.sender_id,
                    "text_content": message.text_content,
                    "timestamp": message.timestamp,
                    "seen": True
                }]

        for message in messages_sent:
            messages += [{
                "user_id": message.sender_id,
                "text_content": message.text_content,
                "timestamp": message.timestamp,
                "seen": True
            }]

        messages.sort(key=lambda msg: msg["timestamp"], reverse=True)
        return messages

    @classmethod
    def send_direct_message(cls, inbox_data):
        user = Authenticator.authenticate(inbox_data)

        new_message = MessageTableEntry(
            sender_id=user.user_id,
            receiver_id=inbox_data.chat_id,
            text_content=inbox_data.text_content
        )

        chat_sender, chat_receiver = cls._increase_direct_chat_offset(user.user_id, inbox_data.chat_id)

        try:
            db.session.add(new_message)
            db.session.flush()
            db.session.add(chat_sender)
            db.session.flush()
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
                    f"Failing to send message from user #{new_message.sender_id} to client #{new_message.chat_id}.")
                return UnsuccessfulMessageSentResponse("Couldn't sent message.")
        else:
            return SuccessfulMessageSentResponse("Message sent")

    @classmethod
    def _increase_direct_chat_offset(cls, sender_id, receiver_id):
        chat_sender = db.session.query(ChatTableEntry).filter(
            and_(ChatTableEntry.user_id == sender_id, ChatTableEntry.chat_id == receiver_id)).one_or_none()
        chat_receiver = db.session.query(ChatTableEntry).filter(
            and_(ChatTableEntry.user_id == receiver_id, ChatTableEntry.chat_id == sender_id)).one_or_none()

        if chat_sender and chat_receiver:
            chat_sender.unseen_offset = 0
            chat_receiver.unseen_offset += 1
        else:
            chat_sender = ChatTableEntry(
                user_id=sender_id,
                chat_id=receiver_id,
                unseen_offset=0
            )
            chat_receiver = ChatTableEntry(
                user_id=receiver_id,
                chat_id=sender_id,
                unseen_offset=1
            )

        return chat_sender, chat_receiver
