"""Server process management."""

from multiprocessing import Process
from os import getpid, kill
from signal import SIGTERM
from urllib.request import urlopen

from logprise import logger

from .loader import config


class ServerManager:
    """Manages the server process."""

    def __init__(self):
        self.server_proc: Process | None = None
        self.main_pid = getpid()

    def ping(self) -> bytes | bool:
        """Ping the server."""
        try:
            with urlopen(config.app.pong_url) as u:
                return u.read()
        except Exception:
            return False

    def kill(self) -> bool:
        """Kill server and main processes."""
        ping_result = self.ping()
        if not ping_result:
            return False

        try:
            lines = ping_result.splitlines()[1:]
            main_pid = int(lines[0].split(b":")[1].strip())
            server_pid = int(lines[1].split(b":")[1].strip())

            kill(server_pid, SIGTERM)
            kill(main_pid, SIGTERM)
            logger.info(f"Killed processes: main={main_pid}, server={server_pid}")
            return True
        except Exception as e:
            logger.error(f"Failed to kill processes: {e}")
            return False

    def start(self, target_func):
        """Start the server process."""
        self.server_proc = Process(target=target_func)
        self.server_proc.start()
        return self.server_proc.pid


server_manager = ServerManager()