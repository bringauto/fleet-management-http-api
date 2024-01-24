from __future__ import annotations
from typing import Dict, List, Any, Iterable, Optional, Callable
import threading


class WaitObjManager:

    _default_timeout_ms: int = 5000

    def __init__(self, timeout_ms: int = _default_timeout_ms) -> None:
        WaitObjManager._check_nonnegative_timeout(timeout_ms)
        self._timeout_ms = timeout_ms
        self._wait_dict: Dict[str, List[WaitObj]] = dict()

    @property
    def timeout_ms(self) -> int: return self._timeout_ms

    def new_wait_obj(
        self,
        key: Any,
        timeout_ms: Optional[int] = None,
        validation: Optional[Callable[[Any], bool]] = None
        ) -> WaitObj:
        """Create a new wait object and adds it to the wait queue for given key."""

        if timeout_ms is None or timeout_ms < 0:
            timeout_ms = self._timeout_ms
        if not key in self._wait_dict:
            self._wait_dict[key] = list()
        wait_obj = WaitObj(key, timeout_ms, validation)
        self._wait_dict[key].append(wait_obj)
        return wait_obj

    def notify(self, key: Any, response_content: Iterable[Any]) -> None:
        """Make the next wait object in the queue to respond with specified 'reponse_content' and remove it from the queue."""
        response_content  = list(response_content)
        if key in self._wait_dict:
            for wait_obj in self._wait_dict[key]:
                wait_obj.stop_waiting_if_content_ok(response_content)

            for wait_obj in self._wait_dict[key]:
                if not wait_obj.is_waiting:
                    self._wait_dict[key].remove(wait_obj)

            if not self._wait_dict[key]:
                self._wait_dict.pop(key)

    def set_timeout(self, timeout_ms: int) -> None:
        """Set the timeout for wait objects in milliseconds."""
        self._check_nonnegative_timeout(timeout_ms)
        self._timeout_ms = timeout_ms

    def wait_and_get_response(
        self,
        key: Any,
        timeout_ms: Optional[int] = None,
        validation: Optional[Callable[[Any], bool]] = None
        ) -> List[Any]:
        """Wait for the next wait object in queue to respond and returns the response content.
        The queue is identified by given key.
        """
        wait_obj = self.new_wait_obj(key, timeout_ms, validation)
        reponse = wait_obj.wait_and_get_response()
        self._remove_wait_obj(wait_obj)
        return reponse

    def _remove_wait_obj(self, wait_obj:WaitObj) -> None:
        """Remove the wait object from the wait queue."""
        key = wait_obj.key
        if key in self._wait_dict:
            if wait_obj in self._wait_dict[key]:
                wait_obj.stop_waiting_if_content_ok([])
                self._wait_dict[key].remove(wait_obj)
            if not self._wait_dict[key]:
                self._wait_dict.pop(key)

    @staticmethod
    def _check_nonnegative_timeout(timeout_ms: int) -> None:
        if timeout_ms < 0:
            raise ValueError(f"Timeout must be non-negative, got {timeout_ms}.")


class WaitObj:

    __default_timeout: int = 0

    def __init__(self, key: Any, timeout_ms: int, validation: Optional[Callable[[Any], bool]]) -> None:
        self._key = key
        self._response_content: List[Any] = list()
        self._condition = threading.Condition()
        self._is_valid = validation
        if timeout_ms < 0:
            timeout_ms = WaitObj.__default_timeout
        self._timeout_ms = timeout_ms
        self._is_waiting = False

    @property
    def key(self) -> str: return self._key
    @property
    def is_waiting(self) -> bool: return self._is_waiting

    def stop_waiting_if_content_ok(self, content: List[Any]):
        filtered_content = self._filter_content(content)
        if filtered_content:
            self._response_content = content.copy()
            with self._condition:
                self._is_waiting = False
                self._condition.notify()

    def wait_and_get_response(self) -> List[Any]:
        """Wait for the response object to be set and then return it."""
        with self._condition:
            self._is_waiting = True
            self._condition.wait(timeout=self._timeout_ms/1000)
        return self._response_content

    def _filter_content(self, content: List[Any]) -> List[Any]:
        if self._is_valid is None:
            return content
        else:
            return [item for item in content if self._is_valid(item)]