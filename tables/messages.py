from app import db
from sqlalchemy import exc, ForeignKey
from sqlalchemy.sql import func
from tables.users import ClientTableEntry
from tables.teams import TeamTableEntry


class MessageTableEntry(db.Model):
    __tablename__ = 'messages'

    message_id = db.Column(name='id', type_=db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(ForeignKey(ClientTableEntry.client_id, ondelete='CASCADE'), name='sender_id', type_=db.Integer, nullable=False)
    receiver_id = db.Column(ForeignKey(ClientTableEntry.client_id, ondelete='CASCADE'), name='receiver_id', type_=db.Integer, nullable=False)
    team_id = db.Column(ForeignKey(TeamTableEntry.team_id, ondelete='CASCADE'), name='team_id', type_=db.Integer, nullable=False)
    content = db.Column(name='content', type_=db.String(), nullable=False)
    send_type = db.Column(name='send_type', type_=db.String(), nullable=False)
    message_type = db.Column(name='message_type', type_=db.String(), nullable=False)
    timestamp = db.Column(name='timestamp', type_=db.DateTime(timezone=True), nullable=False, server_default=func.now())


class ChatTableEntry(db.Model):
    __tablename__ = 'chats_messages'

    user_id = db.Column(ForeignKey(ClientTableEntry.client_id, ondelete='CASCADE'), name='user_id', type_=db.Integer,
                        nullable=False, primary_key=True)
    chat_id = db.Column(ForeignKey(ClientTableEntry.client_id, ondelete='CASCADE'), name='chat_id', type_=db.Integer,
                        nullable=False, primary_key=True)
    team_id = db.Column(ForeignKey(TeamTableEntry.team_id, ondelete='CASCADE'), name='team_id', type_=db.Integer,
                        nullable=False, primary_key=True)
    unseen_offset = db.Column(name='unseen', type_=db.Integer, nullable=False, default=0)
