"""
Used to run the backend server for the application.
"""

import subprocess

from config import root_path
from config.logging import root_logger
from scripts.shared import (
    ServerType,
    kill_process_on_port,
    venv_python,
    wait_for_server,
)


def launch_backend(port: int):
    """Launches the backend Flask-SocketIO server using gunicorn and eventlet."""
    server_dir = root_path
    kill_process_on_port(port)

    try:
        # Run the server with gunicorn and eventlet worker, showing logs in the current window
        subprocess.Popen(
            [
                venv_python,
                "-m",
                "gunicorn",
                "--worker-class",
                "eventlet",
                "--bind",
                f"0.0.0.0:{port}",
                "main:socketio",
            ],
            cwd=server_dir,
        )
    except subprocess.CalledProcessError as e:
        root_logger.error(f"Error running command: {e.cmd}")
        root_logger.error(f"Exit code: {e.returncode}")
        raise


def wait_for_backend(port: int, tries=5, delay=1):
    """Pings the given port to check if the backend server is up, retrying up to `tries` times."""
    wait_for_server(port, ServerType.Backend, tries, delay)
