import json
import os
import pathlib
import uuid

from config import root_path
from config.logger import logger
from config.variable_types import VariableType
from config.variables import OptionalVariables, RequiredVariables

# os.join is safer than pathlib.Path("directory", "subdirectory") as
# it does not replace drive:// with drive:/
CONFIG_FILE_PATH = os.path.join(root_path, "config.json")

config_vars_types = {
    RequiredVariables.APP_SECRET_KEY.name: VariableType.STRING,
    RequiredVariables.APP_SESSION_LIFETIME.name: VariableType.INT,
    # Optional Variables
    OptionalVariables.APP_SESSION_FILE_DIR.name: VariableType.STRING,
    OptionalVariables.RESET_SESSION_FILE_ON_STARTUP.name: VariableType.BOOL,
}

default_config = {
    RequiredVariables.APP_SECRET_KEY.name: f"{uuid.uuid4()}",
    RequiredVariables.APP_SESSION_LIFETIME.name: 7200,  # Two hours
    # Optional Variables
    OptionalVariables.APP_SESSION_FILE_DIR.name: os.path.join(
        root_path, "session_data"
    ),
    OptionalVariables.RESET_SESSION_FILE_ON_STARTUP.name: True,
}


def _get_config():
    """
    Gets the configuration for the whole program.
    If the config.json file is not found or corrupted,
    """

    logger.info("Loading the configuration")

    config = default_config
    try:
        with open(CONFIG_FILE_PATH, "r") as config_file:
            config = json.load(config_file)
    except Exception as ex:
        logger.debug(f"An error occured during configuration loading : {ex}")
        logger.warning("Loading failed, resorting to default configuration")
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
        raise Exception(exception_message)

    return config


def _write_config(config):
    """
    Writes the config.json file, overriting any existing one.
    """

    logger.debug(f"Writing down the config file at {CONFIG_FILE_PATH}")
    with open(CONFIG_FILE_PATH, "w") as file:
        file.write(json.dumps(config, indent=2))


def _missing_required_vars(config):
    """
    Checks whether or not a required variable is missing from configuration
    """
    return [var for var in RequiredVariables if var.name not in config]


def _incorrect_var_types(config):
    """
    Checks if some variables have been set with a correct type or not.
    """
    incorrect_var_types = {}

    for var in config:
        if config_vars_types[var] == VariableType.STRING and not isinstance(var, str):
            incorrect_var_types[var] = VariableType.STRING
        elif config_vars_types[var] == VariableType.INT and not isinstance(var, int):
            incorrect_var_types[var] = VariableType.INT
        elif config_vars_types[var] == VariableType.BOOL and not isinstance(var, bool):
            incorrect_var_types[var] = VariableType.BOOL
        elif config_vars_types[var] == VariableType.FLOAT and not isinstance(
            var, float
        ):
            incorrect_var_types[var] = VariableType.FLOAT

    return incorrect_var_types


def _get_incorrect_var_types_err(incorrect_var_types: dict[str, VariableType]):
    err_message = "One of more variable(s) have the wrong type : \n"
    for index, var in enumerate(incorrect_var_types):
        new_line = "\n" if index != len(incorrect_var_types - 1) else ""
        err_message += (
            f"{var} should be of type {incorrect_var_types[var].name.lower()}{new_line}"
        )
    return err_message


global_config = _get_config()
