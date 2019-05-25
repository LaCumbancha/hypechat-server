from app import db
from dtos.responses.users import *
from exceptions.exceptions import *
from models.authentication import Authenticator
from tables.users import *
from passlib.apps import custom_app_context as hashing
from sqlalchemy import exc

import logging


class UserService:

    @classmethod
    def logger(cls):
        return logging.getLogger(cls.__name__)

    @classmethod
    def create_user(cls, new_user_data):
        new_client = ClientTableEntry()

        try:
            db.session.add(new_client)
            db.session.flush()
            new_user = UserTableEntry(
                user_id=new_client.client_id,
                username=new_user_data.username(),
                email=new_user_data.email(),
                password=hashing.hash(new_user_data.password()),
                first_name=new_user_data.first_name(),
                last_name=new_user_data.last_name(),
                profile_pic=new_user_data.profile_pic(),
                token=Authenticator.generate()
            )
            db.session.add(new_user)
            db.session.flush()
            db.session.commit()
            cls.logger().info(f"User #{new_client.client_id} created.")
        except exc.IntegrityError:
            db.session.rollback()
            if db.session.query(UserTableEntry).filter(UserTableEntry.email == new_user_data.email()).first():
                cls.logger().info(f"Failing to create user {new_client.client_id}. Email already in use for other user.")
                return UserAlreadyCreatedResponse("Email already in use for other user.")
            elif db.session.query(UserTableEntry).filter(UserTableEntry.username == new_user_data.username()).first():
                cls.logger().info(f"Failing to create user #{new_client.client_id}. Username already in use for other user.")
                return UserAlreadyCreatedResponse("Username already in use for other user.")
            else:
                cls.logger().info(f"Failing to create user #{new_client.client_id}.")
                return UnsuccessfulUserResponse("Couldn't create user.")
        else:
            return SuccessfulUserResponse(new_user)

    @classmethod
    def login_user(cls, authentication_data):
        user = db.session.query(UserTableEntry).filter(UserTableEntry.email == authentication_data.email()).one_or_none()

        if user and hashing.verify(authentication_data.password(), user.password):
            user.auth_token = Authenticator.generate()
            db.session.commit()
            cls.logger().info(f"Logging in user {user.user_id}")
            return SuccessfulUserResponse(user)
        else:
            cls.logger().info(f"Wrong credentials while attempting to log in user #{user.user_id}")
            return WrongCredentialsResponse("Wrong email or password.")

    @classmethod
    def logout_user(cls, authentication_data):
        user = Authenticator.authenticate(authentication_data)
        user.auth_token = None
        db.session.commit()
        cls.logger().info(f"User #{user.user_id} logged out.")
        return UserLoggedOutResponse("User logged out.")

    @classmethod
    def set_user_online(cls, authentication_data):
        user = Authenticator.authenticate(authentication_data)
        user.online = True
        db.session.commit()
        cls.logger().info(f"User #{user.user_id} set online.")
        return SuccessfulUserResponse(user)

    @classmethod
    def set_user_offline(cls, authentication_data):
        user = Authenticator.authenticate(authentication_data)
        user.online = False
        db.session.commit()
        cls.logger().info(f"User #{user.user_id} set offline.")
        return SuccessfulUserResponse(user)
