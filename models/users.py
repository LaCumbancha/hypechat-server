from app import db
from exceptions.exceptions import *
from models.authentication import AuthToken
from passlib.apps import custom_app_context as hash_builder
from sqlalchemy import exc


class RegularUser(db.Model):
    __tablename__ = 'users'

    _id = db.Column(name='id', type_=db.Integer, primary_key=True, autoincrement=True)
    _username = db.Column(name='username', type_=db.String(), unique=True)
    _email = db.Column(name='email', type_=db.String(), unique=True)
    _password = db.Column(name='password', type_=db.String(), nullable=False)
    _auth_token = db.Column(name='auth_token', type_=db.String(), default=AuthToken.generate())

    @classmethod
    def create_user(cls, username, email, password):
        new_user = RegularUser(username=username, email=email, password=hash_builder.hash(password))

        try:
            db.session.add(new_user)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            if db.session.query(RegularUser).filter(RegularUser._email == email).first():
                raise UserCreationFailureError("Email already in use for other user.")
            else:
                raise UserCreationFailureError("User already exists")
        else:
            return {"auth_token": new_user.token()}

    @classmethod
    def login_user(cls, email, password):
        user = db.session.query(RegularUser).filter(RegularUser._email == email).one_or_none()

        if user and hash_builder.verify(password, user.password()):
            user.login()
            db.session.commit()
            return {"auth_token": user.token()}
        else:
            raise CredentialsError("Wrong email or password.")

    @classmethod
    def logout_user(cls, token):
        user = db.session.query(RegularUser).filter(RegularUser._auth_token == token).one_or_none()

        if user:
            user.logout()
            db.session.commit()
            return {"message": "User logged out."}
        else:
            raise UserNotLoggedError("You must be logged to perform this action.")

    def __init__(self, username, email, password):
        self._username = username
        self._email = email
        self._password = password

    def id(self):
        return self._id

    def username(self):
        return self._username

    def email(self):
        return self._email

    def password(self):
        return self._password

    def is_logged(self):
        return self._logged

    def login(self):
        self._auth_token = AuthToken.generate()

    def logout(self):
        self._auth_token = None

    def token(self):
        return self._auth_token
