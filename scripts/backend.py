"""
Used to run the backend server for the application.
"""

import os
import subprocess

from shared import venv_python

from scripts.shared import ServerType, wait_for_server
from server.config.logging import root_logger


def launch_backend(port: int):
    """Launches the backend Flask-SocketIO server using gunicorn and eventlet."""
    server_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "server")
    )

    root_logger.info(f"Launching backend server in {server_dir} on port {port}...")
    try:
        # Run the server with gunicorn and eventlet worker, showing logs in the current window
        process = subprocess.Popen(
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
        process.wait()  # Wait for the server process to exit (Ctrl+C to stop)
    except subprocess.CalledProcessError as e:
        root_logger.error(f"Error running command: {e.cmd}")
        root_logger.error(f"Exit code: {e.returncode}")
        raise


def wait_for_backend(port: int, tries=5, delay=1):
    """Pings the given port to check if the backend server is up, retrying up to `tries` times."""
    wait_for_server(port, ServerType.Backend, tries, delay)
