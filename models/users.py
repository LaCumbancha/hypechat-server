from app import db
from exceptions.exceptions import UserAlreadyExistsError
from models.authentication import AuthToken
from sqlalchemy import exc


class RegularUser(db.Model):
    __tablename__ = 'users'

    _id = db.Column(name='id', type_=db.Integer, primary_key=True, autoincrement=True)
    _username = db.Column(name='username', type_=db.String(), unique=True)
    _email = db.Column(name='email', type_=db.String(), unique=True)
    _password = db.Column(name='password', type_=db.String(), nullable=False)
    _logged = db.Column(name='logged', type_=db.Boolean(), nullable=False, default=False)
    _auth_token = db.Column(name='auth_token', type_=db.String(), default=AuthToken.generate())

    @classmethod
    def create_user(cls, username, email, password):
        new_user = RegularUser(username=username, email=email, password=password)

        try:
            db.session.add(new_user)
            db.session.commit()
            return {"auth_token": new_user.token()}
        except exc.IntegrityError:
            db.session.rollback()
            raise UserAlreadyExistsError("User already exists")

    @classmethod
    def login_user(cls, email, password):
        user = db.session.query(RegularUser)\
            .filter(RegularUser._email == email)\
            .filter(RegularUser._password == password).first()

        if user:
            if not user.is_logged():
                user.login()
                db.session.commit()
                return {"id": user.id()}

        return None

    @classmethod
    def logout_user(cls, id):
        user = db.session.query(RegularUser).filter(RegularUser._id == id).first()

        if user:
            if user.is_logged():
                user.logout()
                db.session.commit()
                return {"id": user.id()}

        return None

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
        self._logged = True

    def logout(self):
        self._logged = False

    def token(self):
        return self._auth_token
