from enum import Enum


class LogLevelEnum(Enum):
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    TRACE = 5
    NOTSET = 0
