from models.constants import StatusCode


class UserError(Exception):

    def __init__(self):
        Exception.__init__(self)

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = self.status
        return rv


class UserCreationFailureError(UserError):
    status_code = StatusCode.BAD_REQUEST.value

    def __init__(self, message, status, payload=None):
        UserError()
        self.message = message
        self.status = status
        self.payload = payload


class CredentialsError(UserError):
    status_code = StatusCode.BAD_REQUEST.value

    def __init__(self, message, status, payload=None):
        UserError()
        self.message = message
        self.status = status
        self.payload = payload


class WrongTokenError(UserError):
    status_code = StatusCode.UNAUTHORIZED.value

    def __init__(self, message, status, payload=None):
        UserError()
        self.message = message
        self.status = status
        self.payload = payload
