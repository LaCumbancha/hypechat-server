from enum import Enum


class StatusCode(Enum):
    OK = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    SERVER_ERROR = 500


class UserResponseStatus(Enum):
    ERROR = "ERROR"
    ACTIVE = "ACTIVE"
    OFFLINE = "OFFLINE"
    LOGGED_OUT = "LOGGED_OUT"
    WRONG_TOKEN = "WRONG_TOKEN"
    WRONG_CREDENTIALS = "WRONG_CREDENTIALS"
    ALREADY_LOGGED_IN = "ALREADY_LOGGED_IN"
    ALREADY_REGISTERED = "ALREADY_REGISTERED"
    USER_NOT_FOUND = "USER_NOT_FOUND"


class TeamResponseStatus(Enum):
    CREATED = "CREATED"
    USER_ADDED = "USER_ADDED"
    NOT_ENOUGH_PERMISSIONS = "NOT_ENOUGH_PERMISSIONS"
    ALREADY_REGISTERED = "ALREADY_REGISTERED"


class TeamRoles(Enum):
    CREATOR = "CREATOR"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
