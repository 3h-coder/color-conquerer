import json
import os
import uuid

from config import root_path, runtime_data_path
from config.logging import root_logger
from config.variable_types import VariableType
from config.variables import OptionalVariable, RequiredVariable
from utils import logging_utils

# os.join is safer than pathlib.Path("directory", "subdirectory") as
# it does not replace drive:// with drive:/
CONFIG_FILE_PATH = os.path.join(root_path, "config.json")

_config_vars_types = {
    RequiredVariable.DEBUG.name: VariableType.BOOL,
    RequiredVariable.CORS_ALLOWED_ORIGINS.name: VariableType.LIST_OF_STRINGS,
    RequiredVariable.APP_SECRET_KEY.name: VariableType.STRING,
    RequiredVariable.APP_SESSION_LIFETIME.name: VariableType.INT,
    RequiredVariable.APP_REDIS_SESSION_STORAGE.name: VariableType.BOOL,
    RequiredVariable.MAX_ROOM_CAPACITY.name: VariableType.INT,
    # Optional Variables
    OptionalVariable.APP_SESSION_FILE_DIR.name: VariableType.STRING,
    OptionalVariable.APP_REDIS_SERVER_PORT.name: VariableType.INT,
    OptionalVariable.RESET_SESSION_FILE_ON_STARTUP.name: VariableType.BOOL,
}

_default_config = {
    RequiredVariable.DEBUG.name: True,
    # The front-end server
    RequiredVariable.CORS_ALLOWED_ORIGINS.name: [
        # TODO : Update that once the actual domain is obtained
        "https://color-conquerer.com",
        "http://localhost:5173",
    ],
    RequiredVariable.APP_SECRET_KEY.name: f"{uuid.uuid4()}",
    RequiredVariable.APP_REDIS_SESSION_STORAGE.name: False,
    RequiredVariable.APP_SESSION_LIFETIME.name: 7200,  # Two hours
    RequiredVariable.MAX_ROOM_CAPACITY.name: 50,
    # Optional Variables
    OptionalVariable.APP_SESSION_FILE_DIR.name: os.path.join(
        runtime_data_path, "session_data"
    ),
    OptionalVariable.APP_REDIS_SERVER_PORT.name: 6379,  # Default redis port
    OptionalVariable.RESET_SESSION_FILE_ON_STARTUP.name: False,
}

# To be initialized at startup once
_global_config = {}


def get(config_variable: RequiredVariable | OptionalVariable):
    """
    Returns the value of a key in the configuration.
    If the key is not found, returns the value from `_default_config`.

    Raises:
        TypeError: If `config_variable` is not of type `RequiredVariable` or `OptionalVariable`
    """
    global _global_config
    if not _global_config:
        _global_config = _get_config()

    if not isinstance(config_variable, (RequiredVariable, OptionalVariable)):
        raise TypeError(
            f"[CONFIG] | The config variable must be an instance of {RequiredVariable.__name__}"
            f" or {OptionalVariable.__name__}, got {type(config_variable).__name__} instead."
        )

    key = config_variable.name
    try:
        return _global_config[key]
    except KeyError:
        value = _default_config[key]
        root_logger.error(
            f"[CONFIG] | The key {key} not found in the configuration, using the value from the default config ({value})"
        )
        return value


# region Loading


def _get_config():
    """
    Gets the configuration for the whole program, performing security checks along the way.
    If the config.json file is not found or corrupted, writes it down based on default_config.
    """

    root_logger.info("Loading the configuration")

    _check_for_missing_required_vars_in_default_config()
    _check_for_inconsistencies_between_default_config_and_var_types()

    config = _try_load_config()

    _check_for_missing_required_vars_in_loaded_config(config)
    _check_for_incorrect_var_types(config)

    return config


def _try_load_config():
    config = _default_config
    try:
        with open(CONFIG_FILE_PATH, "r") as config_file:
            config = json.load(config_file)
    except Exception as ex:
        root_logger.debug(f"An error occured during configuration file reading : {ex}")
        root_logger.warning("Loading failed, resorting to default configuration")
        _write_config(config)

    return config


# endregion

# region Checks


def _check_for_inconsistencies_between_default_config_and_var_types():
    """
    Validates that the keys in the default configuration and the configuration variable types match.
    This function compares the keys in `_default_config` and `_config_vars_types` to ensure that they are identical.

    Raises:
        ValueError: If there are mismatched keys between `_default_config` and `_config_vars_types`.
    """

    default_keys = set(_default_config.keys())
    type_keys = set(_config_vars_types.keys())

    if default_keys != type_keys:
        missing_in_default = type_keys - default_keys
        missing_in_types = default_keys - type_keys

        raise ValueError(
            f"The default configuration and the config variables types do not have matching keys.\n"
            f"Keys missing in default configuration: {None if not missing_in_default else missing_in_default}\n"
            f"Keys missing in config variable types: {None if not missing_in_types else missing_in_types}"
        )


def _check_for_missing_required_vars_in_default_config():
    """
    Validates that all variables (optional or not) are defined in the default configuration.

    Raises:
        ValueError: If one or more required variables are not defined in the default configuration.
    """

    missing_vars_in_default_config = _missing_vars_in_default_config()
    if missing_vars_in_default_config:
        raise ValueError(
            f"The following variables are not defined in the default configuration : {missing_vars_in_default_config}"
        )


def _check_for_missing_required_vars_in_loaded_config(config):
    """
    Validates that all required variables are defined in the loaded configuration.

    Raises:
        ValueError: If one or more required variables are not defined in the default configuration.
    """
    missing_vars = _missing_required_vars_in_loaded_config(config)
    if missing_vars:
        raise ValueError(
            f"The following required variables are missing from the configuration : {missing_vars}"
        )


def _check_for_incorrect_var_types(config):
    """
    Validates the types for each variable in the given configuration.

    Raises:
        ValueError: If any variables in the configuration have incorrect types.
    """

    incorrect_var_types = _incorrect_var_types(config)
    if incorrect_var_types:
        exception_message = _get_incorrect_var_types_err(incorrect_var_types)
        raise TypeError(exception_message)


# endregion

# region Utils methods


def _write_config(config):
    """
    Writes the config.json file, overriting any existing one.
    """

    root_logger.info(f"Writing down the config file at {CONFIG_FILE_PATH}")
    with open(CONFIG_FILE_PATH, "w") as file:
        file.write(json.dumps(config, indent=2))


def _missing_vars_in_default_config():
    """
    Checks whether or not a variable (required or optional) is missing from default_config
    """
    return [
        var.name
        for var in (*RequiredVariable, *OptionalVariable)
        if var.name not in _default_config
    ]


def _missing_required_vars_in_loaded_config(config):
    """
    Checks whether or not a required variable is missing from the loaded
    """
    return [var.name for var in RequiredVariable if var.name not in config]


def _incorrect_var_types(config):
    """
    Checks whether some variables have been set with a correct type or not.
    We do not check string types as any object can always be stringified.
    """
    incorrect_var_types = {}

    for variable_name in config:
        if _config_vars_types[variable_name] == VariableType.INT and not _is_valid_int(
            config[variable_name]
        ):
            incorrect_var_types[variable_name] = VariableType.INT

        elif _config_vars_types[
            variable_name
        ] == VariableType.BOOL and not _is_valid_bool(config[variable_name]):
            incorrect_var_types[variable_name] = VariableType.BOOL

        elif _config_vars_types[
            variable_name
        ] == VariableType.FLOAT and not _is_valid_float(config[variable_name]):
            incorrect_var_types[variable_name] = VariableType.FLOAT

        elif _config_vars_types[
            variable_name
        ] == VariableType.LIST_OF_STRINGS and not _is_valid_list_of_strings(
            config[variable_name]
        ):
            incorrect_var_types[variable_name] = VariableType.LIST_OF_STRINGS

    return incorrect_var_types


def _get_incorrect_var_types_err(incorrect_var_types: dict[str, VariableType]):
    err_message = "One or more variable(s) have the wrong type : \n"
    for index, var in enumerate(incorrect_var_types):
        new_line = "\n" if index != len(incorrect_var_types) - 1 else ""
        err_message += (
            f"{var} should be of type {incorrect_var_types[var].name.lower()}{new_line}"
        )
    return err_message


def _is_valid_int(var):
    try:
        var = int(var)
        return True
    except ValueError:
        return False


def _is_valid_bool(var):
    try:
        var = bool(var)
        return True
    except ValueError:
        return False


def _is_valid_float(var):
    try:
        var = float(var)
        return True
    except ValueError:
        return False


def _is_valid_list_of_strings(var):
    return isinstance(var, list) and all(isinstance(value, str) for value in var)


# endregion
