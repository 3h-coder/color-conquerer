"""
Package containing all the configuration related modules to have specific
settings for each deployed instance of the app.
"""

import os
import pathlib

from server.config.variables import EnvironmentVariable

RUNTIME_DATA_FOLDER_NAME = "runtime_data"
TESTS_FOLDER_NAME = "tests"
LOGS_FOLDER_NAME = "logs"

root_path = pathlib.Path(__file__).parent.parent.resolve()

runtime_data_path = os.path.join(root_path, RUNTIME_DATA_FOLDER_NAME)
runtime_test_data_path = os.path.join(
    root_path, TESTS_FOLDER_NAME, RUNTIME_DATA_FOLDER_NAME
)

logs_root_path = os.environ.get(
    EnvironmentVariable.LOGS_PATH, os.path.join(runtime_data_path, LOGS_FOLDER_NAME)
)
test_logs_root_path = os.path.join(runtime_test_data_path, LOGS_FOLDER_NAME)
