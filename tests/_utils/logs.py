import json
import os

import logging


def clear_logs() -> None:
    """Find and clear the log file."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(current_dir, "test_config.json"), "r") as f:
            config = json.load(f)
        _clear_log_files(os.path.abspath(config["logging"]["file"]["path"]))

    except KeyError as e:
        logging.error(f"Missing key in configuration file: {e}")
    except FileNotFoundError as e:
        logging.error(f"Configuration file not found: {e}")
    except Exception as e:
        logging.error(f"Unexpected error when clearing up log files: {e}")


def _clear_log_files(directory: str) -> None:
    """Clear all log files in the directory (absolute path)."""
    if not os.path.exists(directory):
        return
    for file in os.listdir(directory):
        if file.endswith(".log"):
            with open(file, "w") as f:
                f.close()
