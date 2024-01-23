from __future__ import annotations
from typing import Dict, List, Any, Iterable, Optional
import threading


class WaitObjManager:

    _default_timeout_ms: int = 5000

    def __init__(self, timeout_ms: int = _default_timeout_ms) -> None:
        WaitObjManager._check_nonnegative_timeout(timeout_ms)
        self._timeout_ms = timeout_ms
        self._wait_dict: Dict[str, WaitObj] = dict()

    @property
    def timeout_ms(self) -> int: return self._timeout_ms

    def new_wait_obj(self, key: Any, timeout_ms: Optional[int] = None) -> WaitObj:
        """Create a new wait object and adds it to the wait queue for given key."""
        if timeout_ms is None:
            timeout_ms = self._timeout_ms
        wait_obj = WaitObj(key, timeout_ms)
        self._wait_dict[key] = wait_obj
        return wait_obj

    def notify(self, key: Any, response_content: Iterable[Any]) -> None:
        """Make the next wait object in the queue to respond with specified 'reponse_content' and remove it from the queue."""
        response_content  = list(response_content)
        if key in self._wait_dict:
            wait_obj:WaitObj|None = self._wait_dict.pop(key)
            if wait_obj is not None:
                wait_obj.add_reponse_content_and_stop_waiting(response_content)

    def remove_wait_obj(self, wait_obj:WaitObj) -> None:
        """Remove the wait object from the wait queue."""
        key = wait_obj.key
        if key in self._wait_dict:
            self._wait_dict.pop(key)

    def set_timeout(self, timeout_ms: int) -> None:
        """Set the timeout for wait objects in milliseconds."""
        self._check_nonnegative_timeout(timeout_ms)
        self._timeout_ms = timeout_ms

    def wait_and_get_response(self, key: Any, timeout_ms: Optional[int] = None) -> List[Any]:
        """Wait for the next wait object in queue to respond and returns the response content.
        The queue is identified by given key."""
        wait_obj = self.new_wait_obj(key, timeout_ms)
        reponse = wait_obj.wait_and_get_response()
        self.remove_wait_obj(wait_obj)
        return reponse

    @staticmethod
    def _check_nonnegative_timeout(timeout_ms: int) -> None:
        if timeout_ms < 0:
            raise ValueError(f"Timeout must be non-negative, got {timeout_ms}.")


class WaitObj:
    def __init__(self, key: Any, timeout_ms: int) -> None:
        self._key = key
        self._response_content: List[Any] = list()
        self._timeout_ms = timeout_ms
        self._condition = threading.Condition()

    @property
    def key(self) -> str: return self._key

    def add_reponse_content_and_stop_waiting(self, content: List[Any]) -> None:
        self._response_content = content.copy()
        with self._condition:
            self._condition.notify()

    def wait_and_get_response(self) -> List[Any]:
        """Wait for the response object to be set and then return it."""
        with self._condition:
            self._condition.wait(timeout=self._timeout_ms/1000)
        return self._response_content
