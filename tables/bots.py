from app import db
from sqlalchemy import exc, ForeignKey

from tables.users import ClientTableEntry
from tables.teams import TeamTableEntry


class BotTableEntry(db.Model):
    __tablename__ = 'bots'

    bot_id = db.Column(ForeignKey(ClientTableEntry.client_id, ondelete='CASCADE'), name='id', type_=db.Integer,
                       nullable=False, primary_key=True, autoincrement=True)
    bot_name = db.Column(name='name', type_=db.String(), nullable=False, unique=True)
    token = db.Column(name='auth_token', type_=db.String(), nullable=False, unique=True)
    callback_url = db.Column(name='callback_url', type_=db.String(), nullable=False)
