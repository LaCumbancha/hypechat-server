class UserError(Exception):

    def __init__(self):
        Exception.__init__(self)

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class UserCreationFailureError(UserError):
    status_code = 400

    def __init__(self, message, payload=None):
        UserError()
        self.message = message
        self.payload = payload


class CredentialsError(UserError):
    status_code = 400

    def __init__(self, message, payload=None):
        UserError()
        self.message = message
        self.payload = payload


class UserNotLoggedError(UserError):
    status_code = 401

    def __init__(self, message, payload=None):
        UserError()
        self.message = message
        self.payload = payload
