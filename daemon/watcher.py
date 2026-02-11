import json
import logging
from pathlib import Path
from typing import List


class WorkflowWatcher:
    """
    Polls workflow directories for JSON workflow files.
    When a workflow changes, it extracts required models,
    resolves them to URLs, and triggers downloads.
    """

    def __init__(self, directories: List[str], resolver, downloader, state):
        self.directories = [Path(d) for d in directories]
        self.resolver = resolver
        self.downloader = downloader
        self.state = state

        for d in self.directories:
            d.mkdir(parents=True, exist_ok=True)

        logging.info(f"Watching {len(self.directories)} workflow directories")

    def poll(self):
        """
        Called once per main-loop tick.
        Scans workflow directories for JSON files and processes any that changed.
        """
        for directory in self.directories:
            for file in directory.glob("*.json"):
                self._process_workflow(file)

    def _process_workflow(self, path: Path):
        """
        If the workflow file changed since last seen, parse it and handle models.
        """
        mtime = path.stat().st_mtime

        if not self.state.should_process(path, mtime):
            return

        logging.info(f"Detected workflow change: {path}")

        try:
            with path.open("r") as f:
                workflow = json.load(f)
        except Exception as e:
            logging.error(f"Failed to parse workflow {path}: {e}")
            return

        model_ids = self._extract_model_ids(workflow)
        logging.info(f"Workflow requires {len(model_ids)} models")

        for model_id in model_ids:
            url = self.resolver.resolve(model_id)
            if not url:
                logging.warning(f"No source found for model: {model_id}")
                continue

            self.downloader.ensure_present(model_id, url)

        self.state.mark_processed(path, mtime)

    def _extract_model_ids(self, workflow: dict):
        """
        Extract model identifiers from a ComfyUI workflow JSON.
        This is intentionally simple — real workflows may require deeper parsing.
        """
        model_ids = set()

        for node in workflow.get("nodes", []):
            if "model" in node.get("inputs", {}):
                model_ids.add(node["inputs"]["model"])

        return list(model_ids)

