from app import db
from exceptions.exceptions import *
from models.authentication import Authenticator
from tables.users import UserTableEntry
from passlib.apps import custom_app_context as hashing
from sqlalchemy import exc

import logging


class UserService:

    @classmethod
    def create_user(cls, new_user_data):
        logger = logging.getLogger(cls.__name__)

        new_user = UserTableEntry(
            username=new_user_data.username(),
            email=new_user_data.email(),
            password=hashing.hash(new_user_data.password()),
            first_name=new_user_data.first_name(),
            last_name=new_user_data.last_name(),
            profile_pic=new_user_data.profile_pic(),
            token=Authenticator.generate()
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            logger.info(f"User with ID {new_user.id} created.")
        except exc.IntegrityError:
            logger.info(f"Failing to create user with ID {new_user.id}.")
            db.session.rollback()
            if db.session.query(UserTableEntry).filter(UserTableEntry.email == new_user_data.email()).first():
                raise UserCreationFailureError("Email already in use for other user.")
            else:
                raise UserCreationFailureError("User already exists")
        else:
            return {"auth_token": new_user.auth_token}

    @classmethod
    def login_user(cls, login_data):
        logger = logging.getLogger(cls.__name__)
        user = db.session.query(UserTableEntry).filter(UserTableEntry.email == login_data.email()).one_or_none()

        if user and hashing.verify(login_data.password(), user.password):
            user.auth_token = Authenticator.generate()
            db.session.commit()
            logger.info(f"Logging in user with ID {user.id}")
            return {"auth_token": user.auth_token}
        else:
            logger.info(f"Wrong credentials while attempting to log in user with ID {user.id}")
            raise CredentialsError("Wrong email or password.")

    @classmethod
    def logout_user(cls, user):
        user.auth_token = None
        db.session.commit()
        logger = logging.getLogger(cls.__name__)
        logger.info(f"User with ID {user.id} logged out.")
        return {"message": "User logged out."}
