import time


def timestamp_ms() -> int:
    return _get_time_in_ms()


def _get_time_in_ms() -> int:
    return int(1000 * time.time())
