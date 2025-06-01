import os
import socket
import subprocess
import time
from enum import StrEnum, auto

from config.logging import root_logger

venv_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "venv"))
venv_python = os.path.join(venv_dir, "bin", "python")


class ServerType(StrEnum):
    Frontend = auto()
    Backend = auto()


def kill_process_on_port(port: int):
    """
    Kills the process running on the given port using npx kill-port.
    Requires Node.js and npx to be installed.
    """
    try:
        root_logger.info(f"Killing any process on port {port} using npx kill-port...")
        subprocess.check_call(["npx", "kill-port", str(port)])
        root_logger.info(f"Successfully killed process on port {port}.")
    except subprocess.CalledProcessError as e:
        root_logger.error(f"Failed to kill process on port {port}: {e}")
    except Exception as e:
        root_logger.error(f"Unexpected error while killing process on port {port}: {e}")


def wait_for_server(port: int, server: ServerType, tries=5, delay=1):
    """Pings the given port to check if the server is up, retrying up to `tries` times."""

    root_logger.info(f"Check if the {server} server is up on port {port}...")
    for attempt in range(1, tries + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(delay)
            result = sock.connect_ex(("localhost", port))
            if result == 0:
                root_logger.info(
                    f"{server} server is up on port {port} (attempt {attempt})"
                )
                return True
            else:
                root_logger.info(
                    f"Attempt {attempt}: Server not up yet on port {port}. Retrying in {delay}s..."
                )
                time.sleep(delay)
    root_logger.error(
        f"The {server} server did not start on port {port} after {tries} attempts."
    )
    return False
