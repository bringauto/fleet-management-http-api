from __future__ import annotations
import dataclasses
from typing import Any, Optional

import connexion  # type: ignore


@dataclasses.dataclass
class RequestJSON:
    data: Any
    tenant: Optional[str] = None

    @staticmethod
    def load() -> RequestJSON | None:
        if not connexion.request.is_json:
            return None
        tenant = connexion.request.cookies.get("tenant", None)
        return RequestJSON(data=connexion.request.get_json(), tenant=tenant)


@dataclasses.dataclass
class RequestEmpty:
    tenant: Optional[str] = None

    @staticmethod
    def load() -> RequestJSON:
        tenant = connexion.request.cookies.get("tenant", None)
        return RequestEmpty(tenant=tenant)
