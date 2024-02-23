import time


def timestamp_ms() -> int:
    return 1000 * _get_time_in_ms()


def _get_time_in_ms() -> int:
    return int(time.time())
