from app import db
from sqlalchemy import exc, ForeignKey
from sqlalchemy.sql import func
from tables.users import ClientTableEntry


class MessageTableEntry(db.Model):
    __tablename__ = 'messages'

    message_id = db.Column(name='id', type_=db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(ForeignKey(ClientTableEntry.client_id), name='sender_id', type_=db.Integer, nullable=False)
    receiver_id = db.Column(ForeignKey(ClientTableEntry.client_id), name='receiver_id', type_=db.Integer, nullable=False)
    text_content = db.Column(name='content', type_=db.String(), nullable=False)
    timestamp = db.Column(name='timestamp', type_=db.DateTime(timezone=True), nullable=False, server_default=func.now())

    def __init__(self, sender_id, receiver_id, text_content):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.text_content = text_content


class ChatTableEntry(db.Model):
    __tablename__ = 'chats_messages'

    user_id = db.Column(ForeignKey(ClientTableEntry.client_id), name='user_id', type_=db.Integer,
                        nullable=False, primary_key=True)
    chat_id = db.Column(ForeignKey(ClientTableEntry.client_id), name='chat_id', type_=db.Integer,
                        nullable=False, primary_key=True)
    unseen_offset = db.Column(name='unseen', type_=db.Integer, nullable=False, default=0)

    def __init__(self, user_id, chat_id, unseen_offset):
        self.user_id = user_id
        self.chat_id = chat_id
        self.unseen_offset = unseen_offset
