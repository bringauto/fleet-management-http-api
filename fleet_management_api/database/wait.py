from __future__ import annotations
from typing import Any, Iterable, Optional, Callable
import threading as _threading


class WaitObjManager:
    """Instance of this class keeps track of WaitObjects and notifies them.

    It also keeps a default timeout value for WaitObjects.
    """

    _class_default_timeout_ms: int = 5000

    def __init__(self, timeout_ms: int = _class_default_timeout_ms) -> None:
        """Initialize the WaitObjManager with a default timeout in milliseconds.

        If `timeout_ms` is set to 0, the wait will return immediatelly empty content.
        If `timeout_ms` is set to None, the default timeout defined by the class will be used.
        """
        WaitObjManager._check_nonnegative_timeout(timeout_ms)
        self._timeout_ms = timeout_ms
        self._wait_dict: dict[str, list[WaitObject]] = dict()

    @property
    def timeout_ms(self) -> int:
        return self._timeout_ms

    def notify_about_content(self, key: Any, content: Iterable[Any]) -> None:
        """Send content to all waiting threads referenced by WaitObjects, which are stored under given key."""
        if key in self._wait_dict:
            for wait_obj in self._wait_dict[key]:
                wait_obj.resume_with_available_content(list(content))
        else:
            # No WaitObjects exists (no threads are paused) under the given key, do nothing.
            pass

    def set_default_timeout(self, timeout_ms: int) -> None:
        """Set the default timeout for new WaitObjects in milliseconds."""
        self._check_nonnegative_timeout(timeout_ms)
        self._timeout_ms = timeout_ms

    def wait_for_content(
        self,
        key: Any,
        timeout_ms: Optional[int] = None,
        validation: Optional[Callable[[Any], bool]] = None,
    ) -> list[Any]:
        """Wait for notification about available content sent from another thread with the same `key`.

        If `timeout_ms` is set to 0, the wait will return immediatelly empty content.
        If `validation` is set, the wait will only accept the content that passes the validation.
        """
        wait_obj = self._new_wait_obj(key, timeout_ms, validation)
        reponse = wait_obj.wait_and_return_content()
        self._remove_wait_obj(key, wait_obj)
        return reponse

    def _new_wait_obj(
        self,
        key: Any,
        timeout_ms: Optional[int] = None,
        validation: Optional[Callable[[Any], bool]] = None,
    ) -> WaitObject:
        """Create new WaitObject and add it to list under the given key."""

        if timeout_ms is None or timeout_ms < 0:
            timeout_ms = self._timeout_ms
        if key not in self._wait_dict:
            self._wait_dict[key] = list()
        wait_obj = WaitObject(timeout_ms, validation)
        self._wait_dict[key].append(wait_obj)
        return wait_obj

    def _remove_wait_obj(self, key: Any, wait_obj: WaitObject) -> None:
        """Remove the WaitObject from the list of WaitObjects."""
        if key in self._wait_dict and wait_obj in self._wait_dict[key]:
            self._wait_dict[key].remove(wait_obj)
        else:
            raise WaitObjManager.UnknownWaitingObj(f"Wait object for key {key} does not exist.")
        if not self._wait_dict[key]:
            self._wait_dict.pop(key)

    @staticmethod
    def _check_nonnegative_timeout(timeout_ms: int) -> None:
        if timeout_ms < 0:
            raise ValueError(f"Timeout must be non-negative, got {timeout_ms}.")

    class UnknownWaitingObj(Exception):
        pass


class WaitObject:
    """This class keeps track of a paused thread waiting for a data to become available,

    and resumes the thread when the data is available.
    """

    def __init__(
        self,
        timeout_ms: int,
        validation: Optional[Callable[[Any], bool]] = None,
    ) -> None:
        """
        - If `validation` is set, the WaitObject will only accept the data that passes the validation.
        - If `timeout_ms` is set to 0, the WaitObject will respond immediatelly.
        """
        self._response_content: list[Any] = list()
        self._wait_condition = _threading.Condition()
        self._is_valid = validation
        self._timeout_ms = max(timeout_ms, 0)

    def resume_with_available_content(self, content: Iterable[Any]) -> None:
        """Resume the waiting thread given content."""
        self._response_content = self.filter_content(content).copy()
        if self._response_content:
            with self._wait_condition:
                self._wait_condition.notify()

    def wait_and_return_content(self) -> list[Any]:
        """Wait for a content from another thread.

        If the content passes the validation, resume the current thread and return the content.
        """
        with self._wait_condition:
            self._wait_condition.wait(timeout=self._timeout_ms / 1000)
        return self._response_content

    def filter_content(self, content: Iterable[Any]) -> list[Any]:
        """Return only the part of `content` passing the validation."""
        if self._is_valid is None:
            return list(content)
        else:
            return [item for item in content if self._is_valid(item)]
