"""LiveTransport Fail-Closed stub. MUST NOT be assembled under non-LIVE envelope.

Source: Module_Skeleton D-07 / RE-I5 / SC-B1. No real SDK, no credentials.
"""

from __future__ import annotations

from typing import Any, NoReturn

from garp_contracts.adapter import AbstractActionRequest
from garp_contracts.envelope import RuntimeEnvelope
from garp_contracts.packet import DecisionPacket


class LiveTransportNotAssembled(RuntimeError):
    """Raised on any attempt to use LiveTransport this round."""


class LiveTransportStub:
    """Fail-closed placeholder. Instantiation is allowed only for DI shape; every op raises."""

    def __init__(self, envelope: RuntimeEnvelope):
        self._envelope = envelope
        if envelope.adapter_runtime.value in ("FIXTURE_ONLY", "SIMULATION"):
            # Instantiation under non-LIVE is a boot misassembly signal
            self._misassembled = True
        else:
            self._misassembled = True  # this round LIVE is never authorized

    def read(self, *args: Any, **kwargs: Any) -> NoReturn:
        raise LiveTransportNotAssembled(
            "TRANSPORT_NOT_AUTHORIZED: LiveTransport is Fail-Closed stub (SC-B1 / D-07)"
        )

    def write(self, packet: DecisionPacket, req: AbstractActionRequest) -> NoReturn:
        raise LiveTransportNotAssembled(
            "SHADOW_WRITE_FORBIDDEN: LiveTransport write not assembled (RE-I5)"
        )

    def state(self) -> str:
        return "FAIL_CLOSED_STUB"
