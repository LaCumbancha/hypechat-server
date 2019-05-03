from app import db
from exceptions.exceptions import *
from passlib.apps import custom_app_context as hash_builder
from sqlalchemy import exc


class MessageTableEntry(db.Model):
    __tablename__ = 'messages'

    id = db.Column(name='id', type_=db.Integer, primary_key=True, autoincrement=True)
    sender = db.Column(name='sender', type_=db.String(), nullable=False)
    receiver = db.Column(name='receiver', type_=db.String(), nullable=False)
    text_content = db.Column(name='text_content', type_=db.String(), nullable=False)

    def __init__(self, sender, receiver, text_content):
        self.sender = sender
        self.receiver = receiver
        self.text_content = text_content
