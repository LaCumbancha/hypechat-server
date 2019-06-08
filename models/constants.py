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
    ADDED = "ADDED"
    INVITED = "INVITED"
    REMOVED = "REMOVED"
    UPDATED = "UPDATED"
    NOT_ENOUGH_PERMISSIONS = "NOT_ENOUGH_PERMISSIONS"
    ALREADY_REGISTERED = "ALREADY_REGISTERED"
    ALREADY_INVITED = "ALREADY_INVITED"
    TEAM_NOT_FOUND = "TEAM_NOT_FOUND"
    ROLE_UNAVAILABLE = "ROLE_UNAVAILABLE"
    ROLE_MODIFIED = "ROLE_MODIFIED"
    USER_NOT_MEMBER = "USER_NOT_MEMBER"


class ChannelResponseStatus(Enum):
    ADDED = "ADDED"
    JOINED = "JOINED"
    UPDATED = "UPDATED"
    REMOVED = "REMOVED"
    OTHER_TEAM = "OTHER_TEAM"
    USER_NOT_MEMBER = "USER_NOT_MEMBER"
    CHANNEL_NOT_FOUND = "CHANNEL_NOT_FOUND"
    PRIVATE_VISIBILITY = "PRIVATE_VISIBILITY"
    VISIBILITY_UNAVAILABLE = "VISIBILITY_UNAVAILABLE"


class UserRoles(Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class TeamRoles(Enum):
    CREATOR = "CREATOR"
    MODERATOR = "MODERATOR"
    MEMBER = "MEMBER"

    @classmethod
    def is_team_admin(cls, user):
        return user.role in [TeamRoles.CREATOR.value, TeamRoles.MODERATOR.value]

    @classmethod
    def is_team_creator(cls, user):
        return user.role == TeamRoles.CREATOR.value

    @classmethod
    def is_higher_role(cls, user1, user2):
        if user1.role == TeamRoles.CREATOR.value:
            return True
        elif user1.role == TeamRoles.MODERATOR.value and user2.role == TeamRoles.MEMBER.value:
            return True
        else:
            return False

    @classmethod
    def is_channel_creator(cls, user_id, creator_id):
        return user_id == creator_id


class ChannelVisibilities(Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


class MessageTypes(Enum):
    DIRECT = "DIRECT"
    CHANNEL = "CHANNEL"
