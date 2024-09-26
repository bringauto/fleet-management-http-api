import json
import os


def clear_logs() -> None:
    """Find and clear the log file."""
    dir = os.path.dirname(__file__)
    config = json.loads(open(os.path.join(dir,"test_config.json")).read())
    log_file_path = config["logging"]["log-path"]
    for file in os.listdir(log_file_path):
        if os.path.isfile(file) and file.endswith(".log"):
            with open(file, "w") as f:
                f.write("")
