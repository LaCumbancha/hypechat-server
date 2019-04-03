from app import db


class RegularUser(db.Model):
    __tablename__ = 'users'

    _id = db.Column(name='id', type_=db.Integer, primary_key=True)
    _username = db.Column(name='username', type_=db.String(), primary_key=True)
    _email = db.Column(name='email', type_=db.String(), primary_key=True)
    _password = db.Column(name='password', type_=db.String(), nullable=False)

    @classmethod
    def new_with(cls, username, email, password):
        new_user = RegularUser(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return new_user

    def __init__(self, username, email, password):
        self._username = username
        self._email = email
        self._password = password

    def username(self):
        return self._username

    def email(self):
        return self._email

    def password(self):
        return self._password
