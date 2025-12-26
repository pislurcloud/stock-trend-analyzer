import time
import logging
from typing import Callable


# Basic logging config (can be overridden later)
logging.basicConfig(level=logging.INFO)


def log_node_execution(node_name: str, fn: Callable):
    """
    Wraps a LangGraph node function with simple logging.

    Logs:
    - Node name
    - Execution duration
    - Keys written to state

    This is intentionally minimal for MVP.
    """

    def wrapper(state: dict) -> dict:
        start_time = time.time()
        output = fn(state)
        duration = round(time.time() - start_time, 3)

        logging.info(
            f"[LLM NODE] {node_name} | "
            f"time={duration}s | "
            f"outputs={list(output.keys())}"
        )

        return output

    return wrapper
