from app import db
from exceptions.exceptions import *
from models.authentication import AuthToken
from tables.users import UserTableEntry
from passlib.apps import custom_app_context as hashing
from sqlalchemy import exc


class RegularUser:

    @classmethod
    def create_user(cls, username, email, password):
        new_user = UserTableEntry(username=username, email=email, password=hashing.hash(password))

        try:
            db.session.add(new_user)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            if db.session.query(UserTableEntry).filter(UserTableEntry.email == email).first():
                raise UserCreationFailureError("Email already in use for other user.")
            else:
                raise UserCreationFailureError("User already exists")
        else:
            return {"auth_token": new_user.auth_token}

    @classmethod
    def login_user(cls, email, password):
        user = db.session.query(UserTableEntry).filter(UserTableEntry.email == email).one_or_none()

        if user and hashing.verify(password, user.password):
            user.auth_token = AuthToken.generate()
            db.session.commit()
            return {"auth_token": user.auth_token}
        else:
            raise CredentialsError("Wrong email or password.")

    @classmethod
    def logout_user(cls, auth_token):
        user = db.session.query(UserTableEntry).filter(UserTableEntry.auth_token == auth_token).one_or_none()

        if user:
            user.auth_token = None
            db.session.commit()
            return {"message": "User logged out."}
        else:
            raise UserNotLoggedError("You must be logged to perform this action.")
