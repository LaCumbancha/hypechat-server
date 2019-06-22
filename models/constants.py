from enum import Enum


class StatusCode(Enum):
    OK = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    SERVER_ERROR = 500


class UserResponseStatus(Enum):
    OK = "OK"
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
    STATS = "STATS"
    CHAT_NOT_FOUND = "CHAT_NOT_FOUND"
    MESSAGE_TYPE_UNAVAILABLE = "MESSAGE_TYPE_UNAVAILABLE"


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
    NOT_FOUND = "NOT_FOUND"
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

    @classmethod
    def is_admin(cls, user_role):
        return user_role == UserRoles.ADMIN.value


class TeamRoles(Enum):
    CREATOR = "CREATOR"
    MODERATOR = "MODERATOR"
    MEMBER = "MEMBER"
    BOT = "BOT"

    @classmethod
    def is_team_moderator(cls, user_role):
        return user_role in [UserRoles.ADMIN.value, TeamRoles.CREATOR.value, TeamRoles.MODERATOR.value]

    @classmethod
    def is_team_creator(cls, user_role):
        return user_role == TeamRoles.CREATOR.value

    @classmethod
    def has_higher_role(cls, user1_role, user2_role):
        role_rank = {
            TeamRoles.MEMBER.value: 1,
            TeamRoles.MODERATOR.value: 2,
            TeamRoles.CREATOR.value: 3,
            UserRoles.ADMIN.value: 4
        }

        return role_rank.get(user1_role) > role_rank.get(user2_role)

    @classmethod
    def is_channel_creator(cls, is_channel_creator):
        return is_channel_creator


class ChannelVisibilities(Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


class SendMessageType(Enum):
    DIRECT = "DIRECT"
    CHANNEL = "CHANNEL"


class ClientType(Enum):
    BOT = "BOT"
    USER = "USER"
    CHANNEL = "CHANNEL"


class MessageType(Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    FILE = "FILE"
    SNIPPET = "SNIPPET"
