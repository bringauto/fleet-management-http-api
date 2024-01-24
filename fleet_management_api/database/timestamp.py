import time


def get_time_in_ms() -> int:
    return int(time.time())


def timestamp_in_ms() -> int:
    return 1000*get_time_in_ms()

