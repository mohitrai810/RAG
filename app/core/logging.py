import json
import logging
import sys


logger = logging.getLogger("rag")

logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)

logger.addHandler(handler)


def log_event(event: str, **fields):
    payload = {
        "event": event,
        **fields,
    }

    logger.info(json.dumps(payload))