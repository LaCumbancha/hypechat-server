class NewUserDTO:

    def __init__(self, username, email, password, first_name, last_name, profile_pic):
        self._username = username
        self._email = email
        self._password = password
        self._first_name = first_name
        self._last_name = last_name
        self._profile_pic = profile_pic

    def username(self):
        return self._username

    def email(self):
        return self._email

    def password(self):
        return self._password

    def first_name(self):
        return self._first_name

    def last_name(self):
        return self._last_name

    def profile_pic(self):
        return self._profile_pic


class LoginDTO:

    def __init__(self, email, password):
        self._email = email
        self._password = password

    def email(self):
        return self._email

    def password(self):
        return self._password


class AuthenticationDTO:

    def __init__(self, username, token):
        self._username = username
        self._token = token

    def token(self):
        return self._token

    def username(self):
        return self._username
