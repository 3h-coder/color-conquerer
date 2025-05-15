from enum import Enum


class RequiredVariable(Enum):
    DEBUG = 1
    CORS_ALLOWED_ORIGINS = 2
    APP_SECRET_KEY = 3
    APP_SESSION_LIFETIME = 4
    MAX_ROOM_CAPACITY = 5


class OptionalVariable(Enum):
    APP_SESSION_FILE_DIR = 1
    RESET_SESSION_FILE_ON_STARTUP = 2
