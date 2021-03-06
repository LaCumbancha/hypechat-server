from app import db
from sqlalchemy import exc, func, ForeignKey
from models.constants import TeamRoles, UserRoles
from tables.teams import TeamTableEntry


class ClientTableEntry(db.Model):
    __tablename__ = 'clients'

    client_id = db.Column(name='id', type_=db.Integer, nullable=False, primary_key=True, autoincrement=True)


class UserTableEntry(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(ForeignKey(ClientTableEntry.client_id, ondelete='CASCADE'), name='id', type_=db.Integer,
                        nullable=False, primary_key=True)
    facebook_id = db.Column(name='facebook_id', type_=db.Integer, nullable=True, unique=True, default=None)
    username = db.Column(name='username', type_=db.String(), nullable=True, unique=True, default=None)
    email = db.Column(name='email', type_=db.String(), nullable=True, unique=True)
    password = db.Column(name='password', type_=db.String(), nullable=True, default=None)
    first_name = db.Column(name='first_name', type_=db.String(), nullable=True)
    last_name = db.Column(name='last_name', type_=db.String(), nullable=True)
    profile_pic = db.Column(name='profile_pic', type_=db.String(), nullable=True)
    role = db.Column(name='role', type_=db.String(), nullable=False, default=UserRoles.USER.value)
    created = db.Column(name='created', type_=db.DateTime(timezone=True), nullable=False, server_default=func.now())
    auth_token = db.Column(name='auth_token', type_=db.String(), nullable=False, default=None)
    online = db.Column(name='online', type_=db.Boolean, nullable=False, default=True)


class PasswordRecoveryTableEntry(db.Model):
    __tablename__ = 'password_recoveries'

    user_id = db.Column(ForeignKey(ClientTableEntry.client_id, ondelete='CASCADE'), name='user_id', type_=db.Integer,
                        nullable=False, primary_key=True)
    token = db.Column(name='recovery_token', type_=db.String(), nullable=False, default=None)


class UsersByTeamsTableEntry(db.Model):
    __tablename__ = 'users_teams'

    user_id = db.Column(ForeignKey(ClientTableEntry.client_id, ondelete='CASCADE'), name='user_id', type_=db.Integer,
                        nullable=False, primary_key=True)
    team_id = db.Column(ForeignKey(TeamTableEntry.team_id, ondelete='CASCADE'), name='team_id', type_=db.Integer,
                        nullable=False, primary_key=True)
    role = db.Column(name='role', type_=db.String(), nullable=False, default=TeamRoles.MEMBER.value)


class UsersByChannelsTableEntry(db.Model):
    __tablename__ = 'users_channels'

    user_id = db.Column(ForeignKey(ClientTableEntry.client_id, ondelete='CASCADE'), name='user_id', type_=db.Integer,
                        nullable=False, primary_key=True)
    channel_id = db.Column(ForeignKey(ClientTableEntry.client_id, ondelete='CASCADE'), name='channel_id', type_=db.Integer,
                           nullable=False, primary_key=True)
