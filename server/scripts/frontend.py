"""
Used to run the frontend server for the application.
"""

import os
import subprocess

from config import root_path
from config.logging import root_logger


def build_frontend_static_files():
    """Launches the frontend server for the application."""
    client_dir = os.path.abspath(os.path.join(root_path, "..", "client"))

    root_logger.info(f"Building frontend in directory: {client_dir}")
    try:
        # Install dependencies
        subprocess.check_call(["npm", "install"], cwd=client_dir)

        # Build for production
        subprocess.check_call(["npm", "run", "build"], cwd=client_dir)
        root_logger.info("===== Frontend build completed successfully. =====")

        # Nginx will server the static files from the dist directory, so we do nothing more
    except subprocess.CalledProcessError as e:
        root_logger.error(f"Error running command: {e.cmd}")
        root_logger.error(f"Exit code: {e.returncode}")
        raise
