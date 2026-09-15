"""FixtureTransport — default local stub. Zero real network.

Source: Module_Skeleton_Design §5 BP-03; adapters/transport/fixture
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from garp_contracts.adapter import AbstractActionRequest, ActionReceipt, ReceiptAudit
from garp_contracts.enums import GateOutcome, ReceiptStatus, SourceEnv
from garp_contracts.envelope import RuntimeEnvelope
from garp_contracts.packet import DecisionPacket
from garp_edge.adapter.write_gate import WriteGate, WriteGateDecision


class FixtureTransport:
    """Local fixture read/write stub. Never contacts ad platforms."""

    def __init__(self, envelope: RuntimeEnvelope, fixtures: Optional[dict[str, Any]] = None):
        self._envelope = envelope
        self._fixtures = fixtures or {}
        self._gate = WriteGate()

    @property
    def source_env(self) -> SourceEnv:
        # Fixture transport always attributes receipts to FIXTURE
        return SourceEnv.FIXTURE

    def read(self, resource: str, scope: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """RO stub. Returns fixture payload or empty shell. No network."""
        payload = self._fixtures.get(resource, {"resource": resource, "rows": []})
        return {
            "payload_ref": f"FX-{resource}",
            "raw": payload,
            "validation_state": "UNVALIDATED",
            "fetched_at": datetime.now().astimezone().isoformat(),
            "envelope_id": self._envelope.envelope_id,
            "warnings": [],
        }

    def write(
        self,
        packet: DecisionPacket,
        req: AbstractActionRequest,
    ) -> tuple[ActionReceipt, WriteGateDecision]:
        """RW path under fixture. Shadow / non-writable → REJECTED_BY_GATE hard fail."""
        decision = self._gate.evaluate(packet, req, self._envelope)
        idempotency_key = req.constraints.get("idempotency_key") or f"{packet.decision_id}:{req.action_id}"
        now = datetime.now().astimezone()

        # Outcome is authoritative; REJECT/HOLD/ESCALATE never emit an approved receipt.
        if decision.outcome in (
            GateOutcome.REJECT,
            GateOutcome.HOLD,
            GateOutcome.ESCALATE,
        ):
            status = decision.receipt_status or ReceiptStatus.REJECTED_BY_GATE
            receipt = ActionReceipt(
                receipt_id=f"RCPT-FX-{uuid.uuid4().hex[:10]}",
                action_id=req.action_id,
                status=status,
                idempotency_key=idempotency_key,
                submitted_at=now,
                platform_ack_ref=None,
                audit=ReceiptAudit(
                    decision_id=packet.decision_id,
                    source_env=SourceEnv.FIXTURE,
                    response_window_due_at=None,
                ),
            )
            return receipt, decision

        # SYNTHETIC_NO_ACTION / PLATFORM_WRITE under fixture: never ACCEPTED from a real platform.
        if decision.outcome is GateOutcome.SYNTHETIC_NO_ACTION:
            status = ReceiptStatus.NOT_APPLICABLE_NO_ACTION
        else:
            status = ReceiptStatus.SIMULATED  # fixture must not claim platform ACCEPTED

        receipt = ActionReceipt(
            receipt_id=f"RCPT-FX-{uuid.uuid4().hex[:10]}",
            action_id=req.action_id,
            status=status,
            idempotency_key=idempotency_key,
            submitted_at=now,
            platform_ack_ref=None,
            audit=ReceiptAudit(
                decision_id=packet.decision_id,
                source_env=SourceEnv.FIXTURE,
            ),
        )
        return receipt, decision
