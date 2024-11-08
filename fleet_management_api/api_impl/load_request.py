from __future__ import annotations
import dataclasses
from typing import Any

import connexion  # type: ignore


@dataclasses.dataclass
class Request:
    data: Any

    @staticmethod
    def load() -> Request | None:
        if not connexion.request.is_json:
            return None
        return Request(data=connexion.request.get_json())
