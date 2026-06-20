"""LoyaltyVIP API client (standard library only).

The public casino directory needs no key. A player's own data requires a
personal API key (``lvip_live_...``) minted at
https://loyaltyvip.com/dashboard/developer.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

DEFAULT_BASE_URL = "https://nbhagdwegk.execute-api.us-east-1.amazonaws.com"

__all__ = ["LoyaltyVIP", "LoyaltyVIPError", "DEFAULT_BASE_URL"]


class LoyaltyVIPError(Exception):
    """Raised on any non-2xx API response. Carries the typed error envelope."""

    def __init__(self, status: int, code: str, message: str, docs: Optional[str] = None) -> None:
        super().__init__(f"{status} ({code}): {message}")
        self.status = status
        self.code = code
        self.message = message
        self.docs = docs


class LoyaltyVIP:
    """A thin, typed-ish client for the LoyaltyVIP REST API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # ── Public directory (no key) ────────────────────────────────────────

    def search_casinos(
        self,
        q: Optional[str] = None,
        state: Optional[str] = None,
        type: Optional[str] = None,  # noqa: A002 - mirrors the API param name
        has_rewards: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> dict[str, Any]:
        """Search the public U.S. casino directory."""
        return self._get(
            "/v1/casinos",
            {"q": q, "state": state, "type": type, "has_rewards": has_rewards, "limit": limit, "offset": offset},
        )

    def get_casino(self, slug: str) -> dict[str, Any]:
        """Casino detail including rewards program and full tier ladder."""
        return self._get(f"/v1/casinos/{urllib.parse.quote(slug)}")

    def list_rewards_programs(
        self, search: Optional[str] = None, brand: Optional[str] = None, limit: Optional[int] = None
    ) -> dict[str, Any]:
        """List casino rewards / players-club programs."""
        return self._get("/v1/rewards-programs", {"search": search, "brand": brand, "limit": limit})

    def get_rewards_program(self, program_id: str) -> dict[str, Any]:
        """A single rewards program with its tier ladder."""
        return self._get(f"/v1/rewards-programs/{urllib.parse.quote(program_id)}")

    # ── Account / actions (API key required) ─────────────────────────────

    def me(self) -> dict[str, Any]:
        return self._get("/v1/me", auth=True)

    def tiers(self) -> dict[str, Any]:
        return self._get("/v1/tiers", auth=True)

    def trips(self) -> dict[str, Any]:
        return self._get("/v1/trips", auth=True)

    def offers(self) -> dict[str, Any]:
        return self._get("/v1/offers", auth=True)

    def player(self, action: str, **params: Any) -> dict[str, Any]:
        """Invoke any /v1/player action (read/write/tax/host scopes apply)."""
        return self._post("/v1/player", {"action": action, **params}, auth=True)

    def comp(self, action: str, **params: Any) -> dict[str, Any]:
        return self._post("/v1/comp/calculate", {"action": action, **params}, auth=True)

    def predict(self, action: str, **params: Any) -> dict[str, Any]:
        return self._post("/v1/comp/predict", {"action": action, **params}, auth=True)

    def tier_match(self, action: str, **params: Any) -> dict[str, Any]:
        return self._post("/v1/tier-match", {"action": action, **params}, auth=True)

    def tax_report(self, action: str, **params: Any) -> dict[str, Any]:
        """IRS gambling tax documents (scope: tax)."""
        return self._post("/v1/tax-report", {"action": action, **params}, auth=True)

    # ── Internals ─────────────────────────────────────────────────────────

    def _headers(self, auth: bool) -> dict[str, str]:
        headers = {"accept": "application/json"}
        if auth and not self.api_key:
            raise LoyaltyVIPError(401, "invalid_token", "This call requires an API key. Pass api_key=...")
        if self.api_key:
            headers["authorization"] = f"Bearer {self.api_key}"
        return headers

    def _get(self, path: str, query: Optional[dict[str, Any]] = None, auth: bool = False) -> dict[str, Any]:
        url = self.base_url + path
        if query:
            clean = {k: v for k, v in query.items() if v is not None and v != ""}
            if clean:
                # Booleans must serialize as lowercase true/false.
                for k, v in list(clean.items()):
                    if isinstance(v, bool):
                        clean[k] = "true" if v else "false"
                url += "?" + urllib.parse.urlencode(clean)
        return self._request("GET", url, None, auth)

    def _post(self, path: str, body: dict[str, Any], auth: bool = False) -> dict[str, Any]:
        return self._request("POST", self.base_url + path, body, auth)

    def _request(self, method: str, url: str, body: Optional[dict[str, Any]], auth: bool) -> dict[str, Any]:
        headers = self._headers(auth)
        data = None
        if body is not None:
            headers["content-type"] = "application/json"
            data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8") or "{}")
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", "replace")
            try:
                err = json.loads(raw).get("error", {})
            except json.JSONDecodeError:
                err = {}
            raise LoyaltyVIPError(
                exc.code,
                err.get("code", "error"),
                err.get("message", f"Request failed with {exc.code}"),
                err.get("docs"),
            ) from None
