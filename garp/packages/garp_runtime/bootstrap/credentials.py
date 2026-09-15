"""Credential provider observation for boot selfcheck (audit §6.3).

This round has NO credentials by design. The provider is a real object whose
state is observed by type/callables — selfcheck must not hardcode PASS strings.
"""

from __future__ import annotations

from typing import Any, Optional


class CredentialObservationError(RuntimeError):
    """Raised when credential state cannot be observed (selfcheck must FAIL, not fake PASS)."""


class EmptyCredentialProvider:
    """Fail-closed empty provider. Instantiation allowed; get() always None."""

    name = "EmptyCredentialProvider"

    def get(self, key: str) -> Optional[Any]:
        return None

    def has_credentials(self) -> bool:
        return False

    def observe_state(self) -> dict[str, Any]:
        """Real observation for selfcheck evidence. May raise on broken providers."""
        # Call the public surface so a broken implementation fails observation.
        has = bool(self.has_credentials())
        sample = self.get("__selfcheck_probe__")
        return {
            "provider_type": type(self).__name__,
            "provider_name": getattr(self, "name", ""),
            "has_credentials": has,
            "probe_returned": sample is not None,
        }


def get_credential_provider() -> EmptyCredentialProvider:
    """Factory. Always Empty this round — no env secrets, no files."""
    return EmptyCredentialProvider()


def observe_credential_state() -> dict[str, Any]:
    """Observe credential provider state. Raises CredentialObservationError on failure."""
    try:
        provider = get_credential_provider()
        state = provider.observe_state()
    except Exception as exc:  # noqa: BLE001 — must surface as observation failure
        raise CredentialObservationError(
            f"credential observation failed: {type(exc).__name__}: {exc}"
        ) from exc
    if not isinstance(state, dict) or "provider_type" not in state:
        raise CredentialObservationError("credential observation returned invalid state")
    return state
