import logging


class WorkflowParser:
    """
    Extracts model identifiers from a ComfyUI workflow JSON structure.
    This module is intentionally simple and isolated so it can evolve
    independently as ComfyUI workflows become more complex.
    """

    def extract_model_ids(self, workflow: dict):
        """
        Return a list of model identifiers referenced in the workflow.
        The default implementation looks for:
            node["inputs"]["model"]
        """
        model_ids = set()

        nodes = workflow.get("nodes", [])
        if not isinstance(nodes, list):
            logging.warning("Workflow 'nodes' field is not a list")
            return []

        for node in nodes:
            inputs = node.get("inputs", {})
            if not isinstance(inputs, dict):
                continue

            model_id = inputs.get("model")
            if model_id:
                model_ids.add(model_id)

        return list(model_ids)

