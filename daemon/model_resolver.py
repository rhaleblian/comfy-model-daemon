import logging


class ModelResolver:
    """
    Resolves a model identifier to a concrete download URL
    using the configured model sources.

    This implementation is intentionally simple:
    - model_id is assumed to be a string like "12345" or "model-name"
    - each source defines a base_url
    - the resolver tries each source in order until one matches
    """

    def __init__(self, sources):
        self.sources = sources
        logging.info(f"Loaded {len(self.sources)} model sources")

    def resolve(self, model_id: str):
        """
        Return a URL for the given model_id, or None if no source applies.
        """
        for source in self.sources:
            base = source.get("base_url")
            if not base:
                continue

            # Simple heuristic: numeric IDs → civitai-style endpoints
            if model_id.isdigit() and "civitai" in source["name"].lower():
                url = f"{base}{model_id}"
                logging.debug(f"Resolved {model_id} via {source['name']}: {url}")
                return url

            # Otherwise, assume HuggingFace-style pathing
            if "huggingface" in source["name"].lower():
                url = f"{base}{model_id}"
                logging.debug(f"Resolved {model_id} via {source['name']}: {url}")
                return url

        logging.warning(f"Could not resolve model ID: {model_id}")
        return None

