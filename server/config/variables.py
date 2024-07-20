from enum import Enum


class RequiredVariables(Enum):
    APP_SECRET_KEY = 1
    APP_SESSION_LIFETIME = 2


class OptionalVariables(Enum):
    APP_SESSION_FILE_DIR = 1
