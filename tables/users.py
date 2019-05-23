from app import db
from exceptions.exceptions import *
from passlib.apps import custom_app_context as hash_builder
from sqlalchemy import exc


class ClientTableEntry(db.Model):
    __tablename__ = 'clients'

    client_id = db.Column(name='id', type_=db.Integer, nullable=False, primary_key=True, autoincrement=True)


class UserTableEntry(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(name='id', type_=db.Integer, nullable=False, primary_key=True)
    username = db.Column(name='username', type_=db.String(), nullable=False, unique=True)
    email = db.Column(name='email', type_=db.String(), nullable=False, unique=True)
    password = db.Column(name='password', type_=db.String(), nullable=False)
    first_name = db.Column(name='first_name', type_=db.String(), nullable=True)
    last_name = db.Column(name='last_name', type_=db.String(), nullable=True)
    profile_pic = db.Column(name='profile_pic', type_=db.String(), nullable=True)
    auth_token = db.Column(name='auth_token', type_=db.String(), nullable=False, default=None)
    online = db.Column(name='online', type_=db.Boolean, nullable=False, default=True)

    def __init__(self, user_id, username, email, password, first_name, last_name, profile_pic, token):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.profile_pic = profile_pic
        self.auth_token = token


class TeamTableEntry(db.Model):
    __tablename__ = 'teams'

    team_id = db.Column(name='id', type_=db.Integer, nullable=False, primary_key=True, autoincrement=True)
    team_name = db.Column(name='name', type_=db.String(), nullable=False, unique=True)
    location = db.Column(name='location', type_=db.String(), nullable=True)
    description = db.Column(name='description', type_=db.String(), nullable=True)
    welcome_message = db.Column(name='welcome_message', type_=db.String(), nullable=True)


class UsersByTeamsTableEntry(db.Model):
    __tablename__ = 'users_teams'

    user_id = db.Column(name='user_id', type_=db.Integer, nullable=False, primary_key=True)
    team_id = db.Column(name='team_id', type_=db.Integer, nullable=False, primary_key=True)
    role = db.Column(name='role', type_=db.String(), nullable=False)


class Channels(db.Model):
    __tablename__ = 'channels'

    channel_id = db.Column(name='id', type_=db.Integer, nullable=False, primary_key=True)
    visibility = db.Column(name='visibility', type_=db.String(), nullable=False)
    description = db.Column(name='description', type_=db.String(), nullable=True)
    welcome_message = db.Column(name='welcome_message', type_=db.String(), nullable=True)


class UsersByChannels(db.Model):
    __tablename__ = 'users_channels'

    user_id = db.Column(name='user_id', type_=db.Integer, nullable=False, primary_key=True)
    channel_id = db.Column(name='channel_id', type_=db.Integer, nullable=False, primary_key=True)
    role = db.Column(name='role', type_=db.String(), nullable=False)
