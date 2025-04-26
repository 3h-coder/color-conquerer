"""
Package containing all the configuration related modules to have specific
settings for each deployed instance of the app.
"""

import os
import pathlib

root_path = pathlib.Path(__file__).parent.parent.resolve()
logs_root_path = os.path.join(root_path, "logs")
test_logs_root_path = os.path.join(root_path, "tests", "logs")
