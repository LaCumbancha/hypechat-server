from models.constants import StatusCode


class HypechatError(Exception):

    def __init__(self):
        Exception.__init__(self)

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = self.status
        return rv


class UserNotFoundError(HypechatError):
    status_code = StatusCode.NOT_FOUND.value

    def __init__(self, message, status, payload=None):
        HypechatError()
        self.message = message
        self.status = status
        self.payload = payload


class TeamNotFoundError(HypechatError):
    status_code = StatusCode.NOT_FOUND.value

    def __init__(self, message, status, payload=None):
        HypechatError()
        self.message = message
        self.status = status
        self.payload = payload


class ChannelNotFoundError(HypechatError):
    status_code = StatusCode.NOT_FOUND.value

    def __init__(self, message, status, payload=None):
        HypechatError()
        self.message = message
        self.status = status
        self.payload = payload


class ChatNotFoundError(HypechatError):
    status_code = StatusCode.NOT_FOUND.value

    def __init__(self, message, status, payload=None):
        HypechatError()
        self.message = message
        self.status = status
        self.payload = payload


class WrongTokenError(HypechatError):
    status_code = StatusCode.FORBIDDEN.value

    def __init__(self, message, status, payload=None):
        HypechatError()
        self.message = message
        self.status = status
        self.payload = payload


class WrongActionError(HypechatError):
    status_code = StatusCode.BAD_REQUEST.value

    def __init__(self, message, status, payload=None):
        HypechatError()
        self.message = message
        self.status = status
        self.payload = payload


class NoPermissionsError(HypechatError):
    status_code = StatusCode.FORBIDDEN.value

    def __init__(self, message, status, payload=None):
        HypechatError()
        self.message = message
        self.status = status
        self.payload = payload


class RoleNotAvailableError(HypechatError):
    status_code = StatusCode.BAD_REQUEST.value

    def __init__(self, message, status, payload=None):
        HypechatError()
        self.message = message
        self.status = status
        self.payload = payload


class VisibilityNotAvailableError(HypechatError):
    status_code = StatusCode.BAD_REQUEST.value

    def __init__(self, message, status, payload=None):
        HypechatError()
        self.message = message
        self.status = status
        self.payload = payload


class MessageTypeNotAvailableError(HypechatError):
    status_code = StatusCode.BAD_REQUEST.value

    def __init__(self, message, status, payload=None):
        HypechatError()
        self.message = message
        self.status = status
        self.payload = payload


class MissingRequestParameterError(HypechatError):
    status_code = StatusCode.BAD_REQUEST.value
    MISSING_PARAMETER = "MISSING_PARAMETER"

    def __init__(self, parameter):
        HypechatError()
        self.message = f"Parameter \"{parameter}\" is required and is missing."
        self.status = self.MISSING_PARAMETER
        self.payload = None


class MissingRequestHeaderError(HypechatError):
    status_code = StatusCode.BAD_REQUEST.value
    MISSING_PARAMETER = "MISSING_PARAMETER"

    def __init__(self, parameter):
        HypechatError()
        self.message = f"Header \"{parameter}\" is required and is missing."
        self.status = self.MISSING_PARAMETER
        self.payload = None


class FacebookWrongTokenError(HypechatError):
    status_code = StatusCode.BAD_REQUEST.value
    WRONG_FACEBOOK_TOKEN = "WRONG_FACEBOOK_TOKEN"

    def __init__(self, message, payload=None):
        HypechatError()
        self.message = message
        self.status = self.WRONG_FACEBOOK_TOKEN
        self.payload = payload


class WrongEmailError(HypechatError):
    status_code = StatusCode.BAD_REQUEST.value
    NOT_VALID_EMAIL = "NOT_VALID_EMAIL"

    def __init__(self, message, payload=None):
        HypechatError()
        self.message = message
        self.status = self.NOT_VALID_EMAIL
        self.payload = payload
