import json
import os
import uuid

from config import root_path
from config.logger import logger
from config.variable_types import VariableType
from config.variables import OptionalVariables, RequiredVariables

# os.join is safer than pathlib.Path("directory", "subdirectory") as
# it does not replace drive:// with drive:/
CONFIG_FILE_PATH = os.path.join(root_path, "config.json")

config_vars_types = {
    RequiredVariables.APP_SECRET_KEY: VariableType.STRING,
    RequiredVariables.APP_SESSION_LIFETIME: VariableType.INT,
    # Optional Variables
    OptionalVariables.APP_SESSION_FILE_DIR: VariableType.PATH,
}

default_config = {
    RequiredVariables.APP_SECRET_KEY.name: f"{uuid.uuid4()}",
    RequiredVariables.APP_SESSION_LIFETIME.name: 7200,  # Two hours
    # Optional Variables
    OptionalVariables.APP_SESSION_FILE_DIR.name: os.path.join(
        root_path, "session_data"
    ),
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


global_config = _get_config()
