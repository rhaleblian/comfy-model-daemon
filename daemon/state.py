import json
from pathlib import Path
import logging


class DaemonState:
    """
    Tracks workflow file modification times so the daemon only processes
    files that have changed since the last poll.
    """

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.state_file = self.cache_dir / "state.json"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._state = self._load_state()
        logging.info(f"State file: {self.state_file}")

    def _load_state(self):
        if not self.state_file.exists():
            return {}

        try:
            with self.state_file.open("r") as f:
                return json.load(f)
        except Exception as e:
            logging.warning(f"Failed to load state file: {e}")
            return {}

    def _save_state(self):
        try:
            with self.state_file.open("w") as f:
                json.dump(self._state, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save state file: {e}")

    def should_process(self, path: Path, mtime: float):
        """
        Return True if the file has changed since last processed.
        """
        key = str(path)
        last_mtime = self._state.get(key)

        if last_mtime is None or mtime > last_mtime:
            return True

        return False

    def mark_processed(self, path: Path, mtime: float):
        """
        Record the file's latest modification time.
        """
        self._state[str(path)] = mtime
        self._save_state()

