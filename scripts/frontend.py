"""
Used to run the frontend server for the application.
"""

import os
import subprocess

from scripts.shared import ServerType, kill_process_on_port, wait_for_server
from server.config.logging import root_logger


def launch_frontend(port: int):
    """Launches the frontend server for the application."""
    client_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "client")
    )
    kill_process_on_port(port)

    root_logger.info(f"Launching frontend server in {client_dir} on port {port}...")
    try:
        # Install dependencies
        subprocess.check_call(["npm", "install"], cwd=client_dir)

        # Build for production
        subprocess.check_call(["npm", "run", "build"], cwd=client_dir)

        # Serve the build directory in a shell, showing logs in the current window
        subprocess.Popen(
            ["npx", "serve", "-s", "build", "-l", str(port)],
            cwd=client_dir,
        )
    except subprocess.CalledProcessError as e:
        root_logger.error(f"Error running command: {e.cmd}")
        root_logger.error(f"Exit code: {e.returncode}")
        raise


def wait_for_frontend(port: int, tries=5, delay=1):
    """Pings the given port to check if the server is up, retrying up to `tries` times."""
    wait_for_server(port, ServerType.Frontend, tries, delay)
