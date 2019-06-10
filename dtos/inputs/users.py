class AuthenticationDTO:

    def __init__(self, token):
        self.token = token


class NewUserDTO:

    def __init__(self, username, email, password, first_name, last_name, profile_pic, role):
        self.username = username
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.profile_pic = profile_pic
        self.role = role


class LoginDTO:

    def __init__(self, email, password, facebook_token):
        self.email = email
        self.password = password
        self.facebook_token = facebook_token


class RecoverPasswordDTO:

    def __init__(self, email):
        self.email = email


class RegeneratePasswordDTO:

    def __init__(self, email, recover_token):
        self.email = email
        self.recover_token = recover_token


class UserUpdateDTO:

    def __init__(self, token, updated_user):
        self.token = token
        self.updated_user = updated_user
