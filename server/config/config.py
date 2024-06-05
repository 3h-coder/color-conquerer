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
}


def _get_config():
    """
    Gets the configuration for the whole program.
    If the config.json file is not found or corrupted,
    """

    logger.info("Loading the configuration")

    default_config = {
        RequiredVariables.APP_SECRET_KEY.name: f"{uuid.uuid4()}",
    }

    config = default_config
    try:
        config = json.load(CONFIG_FILE_PATH)
    except Exception:
        logger.warning("Loading failed, resorting to default configuration")
        _write_config(config)

    return config


def _write_config(config):
    """
    Writes the config.json file, overriting any existing one.
    """

    logger.debug(f"Writing down the config file at {CONFIG_FILE_PATH}")
    with open(CONFIG_FILE_PATH, "w") as file:
        file.write(json.dumps(config))


global_config = _get_config()
