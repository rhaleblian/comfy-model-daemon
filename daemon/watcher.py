import json
import logging
import sys
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
        # Print visited nodes and models found to stderr for visibility
        nodes = workflow.get("nodes", [])
        visited = []
        models_found = []

        for idx, node in enumerate(nodes):
            desc = node.get("id") or node.get("name") or node.get("type") or f"node_{idx}"
            visited.append(str(desc))
            model = self._get_input_value(node, "model")
            if model:
                models_found.append(str(model))

        if visited:
            print(f"Visited nodes: {', '.join(visited)}", file=sys.stderr)
        if models_found:
            print(f"Models found: {', '.join(models_found)}", file=sys.stderr)

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
            model = self._get_input_value(node, "model")
            if model:
                model_ids.add(model)

        return list(model_ids)

    def _get_input_value(self, node: dict, key: str):
        """
        Safely extract a value for `key` from `node['inputs']`.
        `inputs` may be a dict (map of names -> values) or a list (array of input
        descriptors). Handle both cases and return the first matching value or
        None when not found.
        """
        inputs = node.get("inputs")
        if inputs is None:
            return None

        # If inputs is a mapping, use get
        if isinstance(inputs, dict):
            return inputs.get(key)

        # If inputs is a list, try to find an element that contains the key
        if isinstance(inputs, list):
            for item in inputs:
                if isinstance(item, dict):
                    # direct key
                    if key in item:
                        return item[key]
                    # common formats may wrap value under 'value' or 'default'
                    if item.get("name") == key and "value" in item:
                        return item["value"]
                    if item.get("id") == key and "value" in item:
                        return item["value"]
            return None

        # Unknown inputs structure
        return None

