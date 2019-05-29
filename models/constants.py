from enum import Enum


class StatusCode(Enum):
    OK = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    SERVER_ERROR = 500


class UserResponseStatus(Enum):
    LIST = "LIST"
    ERROR = "ERROR"
    ACTIVE = "ACTIVE"
    OFFLINE = "OFFLINE"
    LOGGED_OUT = "LOGGED_OUT"
    WRONG_TOKEN = "WRONG_TOKEN"
    WRONG_CREDENTIALS = "WRONG_CREDENTIALS"
    ALREADY_LOGGED_IN = "ALREADY_LOGGED_IN"
    ALREADY_REGISTERED = "ALREADY_REGISTERED"
    USER_NOT_FOUND = "USER_NOT_FOUND"


class MessageResponseStatus(Enum):
    LIST = "LIST"
    SENT = "SENT"
    ERROR = "ERROR"
    CHAT_NOT_FOUND = "CHAT_NOT_FOUND"


class TeamResponseStatus(Enum):
    LIST = "LIST"
    ERROR = "ERROR"
    CREATED = "CREATED"
    USER_ADDED = "USER_ADDED"
    USER_INVITED = "USER_INVITED"
    USER_REMOVED = "USER_REMOVED"
    NOT_ENOUGH_PERMISSIONS = "NOT_ENOUGH_PERMISSIONS"
    ALREADY_REGISTERED = "ALREADY_REGISTERED"
    ALREADY_INVITED = "ALREADY_INVITED"
    TEAM_NOT_FOUND = "TEAM_NOT_FOUND"
    ROLE_UNAVAILABLE = "ROLE_UNAVAILABLE"
    ROLE_MODIFIED = "ROLE_MODIFIED"
    USER_NOT_MEMBER = "USER_NOT_MEMBER"


class TeamRoles(Enum):
    CREATOR = "CREATOR"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"

    @classmethod
    def is_admin(cls, user):
        return user.role in [TeamRoles.CREATOR.value, TeamRoles.ADMIN.value]

    @classmethod
    def is_creator(cls, user):
        return user.role == TeamRoles.CREATOR.value

    @classmethod
    def is_higher_role(cls, user1, user2):
        if user1.role == TeamRoles.CREATOR.value:
            return True
        elif user1.role == TeamRoles.ADMIN.value and user2.role == TeamRoles.MEMBER.value:
            return True
        else:
            return False
