from app import db
from dtos.responses.clients import *
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
                username=new_user_data.username,
                email=new_user_data.email,
                password=hashing.hash(new_user_data.password),
                first_name=new_user_data.first_name,
                last_name=new_user_data.last_name,
                profile_pic=new_user_data.profile_pic,
                token=Authenticator.generate()
            )
            db.session.add(new_user)
            db.session.flush()
            db.session.commit()
            cls.logger().info(f"User #{new_client.client_id} created.")
        except exc.IntegrityError:
            db.session.rollback()
            if db.session.query(UserTableEntry).filter(UserTableEntry.email == new_user_data.email).first():
                cls.logger().info(
                    f"Failing to create user {new_client.client_id}. Email already in use for other user.")
                return ClientAlreadyCreatedResponse("Email already in use for other user.")
            elif db.session.query(UserTableEntry).filter(UserTableEntry.username == new_user_data.username).first():
                cls.logger().info(
                    f"Failing to create user #{new_client.client_id}. Username already in use for other user.")
                return ClientAlreadyCreatedResponse("Username already in use for other user.")
            else:
                cls.logger().info(f"Failing to create user #{new_client.client_id}.")
                return UnsuccessfulClientResponse("Couldn't create user.")
        else:
            return SuccessfulUserResponse(new_user)

    @classmethod
    def login_user(cls, login_data):
        user = db.session.query(UserTableEntry).filter(
            UserTableEntry.email == login_data.email).one_or_none()

        if user:
            if hashing.verify(login_data.password, user.password):
                user.auth_token = Authenticator.generate()
                user.online = True
                db.session.commit()
                cls.logger().info(f"Logging in user {user.user_id}")
                return SuccessfulUserResponse(user)
            else:
                cls.logger().info(f"Wrong credentials while attempting to log in user #{login_data.email}")
                return WrongCredentialsResponse("Wrong email or password.")
        else:
            cls.logger().info(f"User #{login_data.email} not found.")
            raise UserNotFoundError("User not found.", UserResponseStatus.USER_NOT_FOUND.value)

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
