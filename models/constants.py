from enum import Enum


class StatusCode(Enum):
    OK = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    SERVER_ERROR = 500
