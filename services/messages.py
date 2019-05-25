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
    def send_message(cls, chat_data):
        user = Authenticator.authenticate(chat_data)

        new_message = MessageTableEntry(
            sender_id=user.user_id,
            receiver_id=chat_data.receiver_id,
            text_content=chat_data.text_content
        )

        chat = cls._increase_chat_offset(user.user_id, chat_data.receiver_id)

        try:
            db.session.add(new_message)
            db.session.flush()
            db.session.add(chat)
            db.session.flush()
            db.session.commit()
            cls.logger().info(f"Message sent from user #{new_message.sender_id} to #{new_message.receiver_id}.")
        except exc.IntegrityError:
            db.session.rollback()
            if not db.session.query(ClientTableEntry).filter(
                    ClientTableEntry.client_id == chat_data.receiver_id).one_or_none():
                cls.logger().error(
                    f"User #{new_message.sender_id} tried to sent a message to an nonexistent user.")
                raise UserNotFoundError("User not found.", UserResponseStatus.USER_NOT_FOUND.value)
            else:
                cls.logger().error(
                    f"Failing to send message from user #{new_message.sender_id} to #{new_message.receiver_id}.")
                return UnsuccessfulMessageResponse("Couldn't sent message.")
        else:
            return SuccessfulMessageResponse("Message sent")

    @classmethod
    def _increase_chat_offset(cls, sender_id, receiver_id):
        chat = db.session.query(ChatTableEntry).filter(
            and_(ChatTableEntry.user_id == receiver_id, ChatTableEntry.chat_id == sender_id)).one_or_none()

        if chat:
            chat.unseen_offset += 1
            return chat
        else:
            return ChatTableEntry(
                user_id=receiver_id,
                chat_id=sender_id,
                unseen_offset=1
            )
