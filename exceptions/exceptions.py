from models.constants import StatusCode


class UserError(Exception):

    def __init__(self):
        Exception.__init__(self)

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = self.status
        return rv


class UserNotFoundError(UserError):
    status_code = StatusCode.NOT_FOUND.value

    def __init__(self, message, status, payload=None):
        UserError()
        self.message = message
        self.status = status
        self.payload = payload


class TeamNotFoundError(UserError):
    status_code = StatusCode.NOT_FOUND.value

    def __init__(self, message, status, payload=None):
        UserError()
        self.message = message
        self.status = status
        self.payload = payload


class WrongTokenError(UserError):
    status_code = StatusCode.FORBIDDEN.value

    def __init__(self, message, status, payload=None):
        UserError()
        self.message = message
        self.status = status
        self.payload = payload


class NoPermissionsError(UserError):
    status_code = StatusCode.FORBIDDEN.value

    def __init__(self, message, status, payload=None):
        UserError()
        self.message = message
        self.status = status
        self.payload = payload
