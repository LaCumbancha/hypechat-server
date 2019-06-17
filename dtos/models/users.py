from models.constants import UserRoles


class RegularClient:

    def __init__(self, client_id=None):
        self.id = client_id

    def set_id(self, client_id):
        self.id = client_id


class User:

    def __init__(self, user_id, online=True, role=None, token=None, first_name=None, last_name=None, profile_pic=None,
                 password=None, email=None, username=None, facebook_id=None):
        self.id = user_id
        self.role = role or UserRoles.USER.value
        self.online = online
        self.token = token
        self.first_name = first_name
        self.last_name = last_name
        self.profile_pic = profile_pic
        self.password = password
        self.email = email
        self.username = username
        self.facebook_id = facebook_id


class PublicUser:

    def __init__(self, user_id, online=True, role=None, first_name=None, last_name=None, profile_pic=None, email=None,
                 username=None):
        self.id = user_id
        self.role = role or UserRoles.USER.value
        self.online = online
        self.first_name = first_name
        self.last_name = last_name
        self.profile_pic = profile_pic
        self.email = email
        self.username = username


class PasswordRecovery:

    def __init__(self, user_id, token):
        self.user_id = user_id
        self.token = token
