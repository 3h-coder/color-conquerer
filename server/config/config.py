import json
import os
import uuid

from config import root_path, runtime_data_path
from config.logging import root_logger
from config.variable_types import VariableType
from config.variables import OptionalVariables, RequiredVariables

# os.join is safer than pathlib.Path("directory", "subdirectory") as
# it does not replace drive:// with drive:/
CONFIG_FILE_PATH = os.path.join(root_path, "config.json")

config_vars_types = {
    RequiredVariables.APP_SECRET_KEY.name: VariableType.STRING,
    RequiredVariables.APP_SESSION_LIFETIME.name: VariableType.INT,
    RequiredVariables.MAX_ROOM_CAPACITY.name: VariableType.INT,
    # Optional Variables
    OptionalVariables.APP_SESSION_FILE_DIR.name: VariableType.STRING,
    OptionalVariables.RESET_SESSION_FILE_ON_STARTUP.name: VariableType.BOOL,
}

default_config = {
    RequiredVariables.APP_SECRET_KEY.name: f"{uuid.uuid4()}",
    RequiredVariables.APP_SESSION_LIFETIME.name: 7200,  # Two hours
    RequiredVariables.MAX_ROOM_CAPACITY.name: 50,
    # Optional Variables
    OptionalVariables.APP_SESSION_FILE_DIR.name: os.path.join(
        runtime_data_path, "session_data"
    ),
    OptionalVariables.RESET_SESSION_FILE_ON_STARTUP.name: True,
}

# To be initialized at startup once
_global_config = {}


def get_global_config():
    """
    Returns the global configuration, that can be used accross all modules.
    """
    global _global_config
    if not _global_config:
        _global_config = _get_config()

    return _global_config


def get_from_config(key: str, default_value=None):
    """
    Returns the value of a key in the configuration.
    If the key is not found, None is returned.
    """
    if key in _global_config:
        return _global_config[key]
    else:
        root_logger.error(f"Key {key} not found in the configuration")
        return default_value


def _get_config():
    """
    Gets the configuration for the whole program.
    If the config.json file is not found or corrupted,
    """

    root_logger.info("Loading the configuration")
    if len(default_config) != len(config_vars_types):
        raise Exception(
            "The default configuration and the config variables types do not match in length."
        )

    config = default_config
    try:
        with open(CONFIG_FILE_PATH, "r") as config_file:
            config = json.load(config_file)
    except Exception as ex:
        root_logger.debug(f"An error occured during configuration file reading : {ex}")
        root_logger.warning("Loading failed, resorting to default configuration")
        _write_config(config)

    # Check for missing variables
    missing_vars = _missing_required_vars(config)
    if missing_vars:
        raise Exception(
            f"The required variables are missing from the configuration : {missing_vars}"
        )

    # Check for incorrect variable types
    incorrect_var_types = _incorrect_var_types(config)
    if incorrect_var_types:
        exception_message = _get_incorrect_var_types_err(incorrect_var_types)
        raise ValueError(exception_message)

    return config


def _write_config(config):
    """
    Writes the config.json file, overriting any existing one.
    """

    root_logger.debug(f"Writing down the config file at {CONFIG_FILE_PATH}")
    with open(CONFIG_FILE_PATH, "w") as file:
        file.write(json.dumps(config, indent=2))


def _missing_required_vars(config):
    """
    Checks whether or not a required variable is missing from configuration
    """
    return [var.name for var in RequiredVariables if var.name not in config]


def _incorrect_var_types(config):
    """
    Checks whether some variables have been set with a correct type or not.
    We do not check string types as any object can always be stringified.
    """
    incorrect_var_types = {}

    for variable_name in config:
        if config_vars_types[variable_name] == VariableType.INT and not _is_valid_int(
            config[variable_name]
        ):
            incorrect_var_types[variable_name] = VariableType.INT

        elif config_vars_types[
            variable_name
        ] == VariableType.BOOL and not _is_valid_bool(config[variable_name]):
            incorrect_var_types[variable_name] = VariableType.BOOL

        elif config_vars_types[
            variable_name
        ] == VariableType.FLOAT and not _is_valid_float(config[variable_name]):
            incorrect_var_types[variable_name] = VariableType.FLOAT

    return incorrect_var_types


def _get_incorrect_var_types_err(incorrect_var_types: dict[str, VariableType]):
    err_message = "One of more variable(s) have the wrong type : \n"
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
