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
    first_name = db.Column(name='first_name', type_=db.String(), nullable=True)
    last_name = db.Column(name='last_name', type_=db.String(), nullable=True)
    profile_pic = db.Column(name='profile_pic', type_=db.String(), nullable=True)
    auth_token = db.Column(name='auth_token', type_=db.String(), default=None)

    def __init__(self, username, email, password, first_name, last_name, profile_pic, token):
        self.username = username
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.profile_pic = profile_pic
        self.auth_token = token
