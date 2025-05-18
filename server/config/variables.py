from enum import Enum


class RequiredVariable(Enum):
    DEBUG = 1
    CORS_ALLOWED_ORIGINS = 2
    APP_SECRET_KEY = 3
    APP_SESSION_LIFETIME = 4
    APP_REDIS_SESSION_STORAGE = 5
    MAX_ROOM_CAPACITY = 6


class OptionalVariable(Enum):
    APP_SESSION_FILE_DIR = 1
    APP_REDIS_SERVER_PORT = 2
    RESET_SESSION_FILE_ON_STARTUP = 3
