from enum import Enum


class StatusCode(Enum):
    OK = 200
    NOT_FOUND = 400
    SERVER_ERROR = 500
