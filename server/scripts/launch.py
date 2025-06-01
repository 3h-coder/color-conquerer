"""
Entry point for the web app to server both the frontend and backend servers.
"""

import argparse
import os
import subprocess
import sys

from config import config
from config.logging import root_logger
from config.variables import RequiredVariable
from scripts.backend import launch_backend, wait_for_backend
from scripts.frontend import launch_frontend, wait_for_frontend
from scripts.shared import venv_dir, venv_python


def restart_nginx():
    """Restarts nginx if running (requires admin privileges)."""
    try:
        subprocess.check_call(["sudo", "systemctl", "restart", "nginx"])
        root_logger.info("nginx restarted successfully.")
    except Exception as e:
        root_logger.error("Failed to restart nginx.")
        raise


def check_venv():
    # Paths
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")

    # Check if venv exists
    if not os.path.exists(venv_python):
        root_logger.info("Virtual environment not found. Creating venv...")
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
    else:
        root_logger.info("Virtual environment found.")

    # Install requirements if needed
    try:
        root_logger.info("Checking and installing required packages...")
        subprocess.check_call([venv_python, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call(
            [venv_python, "-m", "pip", "install", "-r", requirements_path]
        )
    except subprocess.CalledProcessError as e:
        root_logger.error(f"Error running command: {e.cmd}")
        root_logger.error(f"Exit code: {e.returncode}")
        raise


def main(force_nginx_restart=False):
    back_end_port = config.get(RequiredVariable.BACKEND_SERVER_PORT)
    front_end_port = config.get(RequiredVariable.FRONTEND_SERVER_PORT)

    if force_nginx_restart:
        restart_nginx()

    check_venv()

    launch_backend(back_end_port)
    wait_for_backend(back_end_port)

    launch_frontend(front_end_port)
    wait_for_frontend(front_end_port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Launch Color Conquerer servers.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force restart nginx before launching servers.",
    )
    args = parser.parse_args()

    try:
        main(force_restart_nginx=args.force)
    except Exception as e:
        root_logger.error(
            "An error occurred while launching the servers.", exc_info=True
        )
        sys.exit(1)
