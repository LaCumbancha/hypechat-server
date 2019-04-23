from app import db
from exceptions.exceptions import *
from passlib.apps import custom_app_context as hash_builder
from sqlalchemy import exc


class UserTableEntry(db.Model):
    __tablename__ = 'users'

    id = db.Column(name='id', type_=db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(name='username', type_=db.String(), unique=True)
    email = db.Column(name='email', type_=db.String(), unique=True)
    password = db.Column(name='password', type_=db.String(), nullable=False)
    auth_token = db.Column(name='auth_token', type_=db.String(), default=None)

    def __init__(self, username, email, password, token):
        self.username = username
        self.email = email
        self.password = password
        self.auth_token = token
