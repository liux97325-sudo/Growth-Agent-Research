"""RW hard-gate chain (G-01 subset + shadow write reject).

Source: GIP v0.2 §1.1, JD v0.2 G-01, Runtime_Envelope RA-01/RA-02.
Audit GA2-R03/R04 / §10.1–10.4: outcome-typed gate; NO_ACTION never reuses
platform-write admission; REJECT/HOLD/REVISE never produce an approved synthetic receipt.

This is a skeleton pseudo-implementation — not a full G-01..G-09 chain.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from garp_contracts.adapter import AbstractActionRequest
from garp_contracts.enums import (
    ExecutionMode,
    GateOutcome,
    PacketKind,
    ReceiptStatus,
    ReviewResult,
    RuntimeMode,
)
from garp_contracts.envelope import RuntimeEnvelope
from garp_contracts.packet import (
    DecisionPacket,
    is_no_action,
    is_writable,
    validate_packet_actions,
)


@dataclass(frozen=True)
class WriteGateDecision:
    """Authoritative gate result.

    `outcome` is the primary signal. `allowed` is retained for call-site
    compatibility and is **deprecated**: True only when outcome is
    PLATFORM_WRITE or SYNTHETIC_NO_ACTION. Prefer `outcome` for new code.
    """

    outcome: GateOutcome
    reason_code: str
    detail: str = ""
    receipt_status: Optional[ReceiptStatus] = None
    passed_gate_ids: tuple[str, ...] = ()
    failed_gate_id: Optional[str] = None
    evidence_refs: tuple[str, ...] = ()

    @property
    def allowed(self) -> bool:
        """Deprecated: True iff outcome in (PLATFORM_WRITE, SYNTHETIC_NO_ACTION).

        Does NOT mean "platform write is permitted" when outcome is
        SYNTHETIC_NO_ACTION. Use `outcome` instead.
        """
        return self.outcome in (
            GateOutcome.PLATFORM_WRITE,
            GateOutcome.SYNTHETIC_NO_ACTION,
        )

    @property
    def is_platform_write(self) -> bool:
        return self.outcome is GateOutcome.PLATFORM_WRITE

    @property
    def is_synthetic_no_action(self) -> bool:
        return self.outcome is GateOutcome.SYNTHETIC_NO_ACTION


def _reject(
    reason_code: str,
    detail: str,
    *,
    outcome: GateOutcome = GateOutcome.REJECT,
    failed_gate_id: str = "G-01",
) -> WriteGateDecision:
    return WriteGateDecision(
        outcome=outcome,
        reason_code=reason_code,
        detail=detail,
        receipt_status=ReceiptStatus.REJECTED_BY_GATE,
        failed_gate_id=failed_gate_id,
    )


def _outcome_from_review(result: ReviewResult) -> GateOutcome:
    """Map non-approve review results to gate outcomes (audit §11.2)."""
    if result is ReviewResult.HOLD:
        return GateOutcome.HOLD
    if result is ReviewResult.ESCALATE_HUMAN:
        return GateOutcome.ESCALATE
    # REJECT / REVISE / unexpected APPROVE-misuse
    return GateOutcome.REJECT


class WriteGate:
    """Order (skeleton): schema → NO_ACTION branch | ordinary branch.

    NO_ACTION branch (DPK-I2/I9/I10, audit §10.4):
      non-empty all-NO_ACTION actions
      + review_result == NO_ACTION_APPROVE
      + no_action_reason non-empty
      → SYNTHETIC_NO_ACTION (never platform write).

    Ordinary branch (DPK-I11/I12, audit §10.3):
      non-NO_ACTION actions
      + review_result == APPROVE only
      + shadow / dry_run / transport checks
      → PLATFORM_WRITE (this round still dry_run / fixture only).
    """

    def evaluate(
        self,
        packet: DecisionPacket,
        req: AbstractActionRequest,
        envelope: RuntimeEnvelope,
    ) -> WriteGateDecision:
        # G-00 subset: empty / malformed action set is schema-invalid.
        violations = validate_packet_actions(packet)
        if "EMPTY_ACTIONS" in violations:
            return _reject(
                "EMPTY_ACTIONS",
                "proposed_actions must be non-empty (schema minItems=1); "
                "empty set is not NO_ACTION",
                failed_gate_id="G-00",
            )
        if "DUPLICATE_ACTION_ID" in violations:
            return _reject(
                "DUPLICATE_ACTION_ID",
                "action_id must be unique within the packet",
                failed_gate_id="G-00",
            )

        if is_no_action(packet):
            return self._evaluate_no_action(packet, envelope)

        return self._evaluate_ordinary_write(packet, req, envelope)

    # ------------------------------------------------------------------
    # NO_ACTION path
    # ------------------------------------------------------------------
    def _evaluate_no_action(
        self,
        packet: DecisionPacket,
        envelope: RuntimeEnvelope,
    ) -> WriteGateDecision:
        if packet.review is None:
            return _reject(
                "GATE_REVIEW_MISSING",
                "NO_ACTION still requires SRA (DPK-I2)",
            )

        result = packet.review.review_result

        # Audit GA2-R04 / §11.2: REJECT/HOLD/REVISE must not yield an approved synthetic receipt.
        if result is not ReviewResult.NO_ACTION_APPROVE:
            outcome = _outcome_from_review(result)
            # APPROVE on a NO_ACTION packet is a semantic mismatch (needs NO_ACTION_APPROVE).
            return _reject(
                "NO_ACTION_REVIEW_MISMATCH",
                f"NO_ACTION requires NO_ACTION_APPROVE; got {result.value}. "
                "No approved synthetic receipt is produced.",
                outcome=outcome,
            )

        # Schema: no_action_reason required when NO_ACTION_APPROVE.
        if not (packet.no_action_reason or "").strip():
            return _reject(
                "NO_ACTION_REASON_MISSING",
                "NO_ACTION_APPROVE requires non-empty no_action_reason",
            )

        # NO_ACTION never touches the platform transport (DPK-I2).
        return WriteGateDecision(
            outcome=GateOutcome.SYNTHETIC_NO_ACTION,
            reason_code="NO_ACTION_NO_PLATFORM_WRITE",
            detail="emit NOT_APPLICABLE_NO_ACTION synthetic receipt; never platform write",
            receipt_status=ReceiptStatus.NOT_APPLICABLE_NO_ACTION,
            passed_gate_ids=("G-01-NO_ACTION",),
        )

    # ------------------------------------------------------------------
    # Ordinary (side-effect) write path
    # ------------------------------------------------------------------
    def _evaluate_ordinary_write(
        self,
        packet: DecisionPacket,
        req: AbstractActionRequest,
        envelope: RuntimeEnvelope,
    ) -> WriteGateDecision:
        if packet.review is None:
            return _reject(
                "GATE_REVIEW_MISSING",
                "ordinary action requires SRA review_result",
            )

        result = packet.review.review_result

        # DPK-I12: NO_ACTION_APPROVE must not approve ordinary side-effect actions.
        if result is ReviewResult.NO_ACTION_APPROVE:
            return _reject(
                "NO_ACTION_APPROVE_CANNOT_WRITE",
                "NO_ACTION_APPROVE must not approve ordinary actions (DPK-I12)",
            )

        if result is ReviewResult.HOLD:
            return WriteGateDecision(
                outcome=GateOutcome.HOLD,
                reason_code="REVIEW_HOLD",
                detail="review_result=HOLD; suspended",
                receipt_status=ReceiptStatus.REJECTED_BY_GATE,
                failed_gate_id="G-01",
            )
        if result is ReviewResult.ESCALATE_HUMAN:
            return WriteGateDecision(
                outcome=GateOutcome.ESCALATE,
                reason_code="REVIEW_ESCALATE",
                detail="review_result=ESCALATE_HUMAN; human ticket required",
                receipt_status=ReceiptStatus.REJECTED_BY_GATE,
                failed_gate_id="G-01",
            )
        if result is not ReviewResult.APPROVE:
            return _reject(
                "REVIEW_NOT_APPROVED",
                f"ordinary action requires APPROVE; got {result.value}",
            )

        # RA-02 / DPK-I5 / G-01: SHADOW hard-reject write path
        if (
            packet.execution_mode is ExecutionMode.SHADOW_READ_ONLY
            or req.envelope.execution_mode is ExecutionMode.SHADOW_READ_ONLY
        ):
            return _reject(
                "SHADOW_WRITE_FORBIDDEN",
                "SHADOW_READ_ONLY packets must never produce platform side effects",
            )

        # RA-10 / RE-I8
        if (
            packet.packet_kind is PacketKind.SHADOW_DECISION
            and packet.execution_mode is not ExecutionMode.SHADOW_READ_ONLY
        ):
            return _reject(
                "PACKET_KIND_MISMATCH",
                "shadow_decision requires SHADOW_READ_ONLY",
            )

        # G-07 / RA-01: non-LIVE dry_run forced
        if envelope.mode is not RuntimeMode.MODE_LIVE_WRITE and not req.dry_run:
            return _reject(
                "DRY_RUN_REQUIRED",
                "non-LIVE write must set dry_run=true",
                failed_gate_id="G-07",
            )

        # RE-I5: Fixture/Sim transport cannot accept dry_run=false platform side effects
        if envelope.adapter_runtime.value in ("FIXTURE_ONLY", "SIMULATION") and not req.dry_run:
            return _reject(
                "TRANSPORT_NOT_AUTHORIZED",
                "LiveTransport not assembled under non-LIVE adapter_runtime",
                failed_gate_id="G-07",
            )

        # Dual-field admission (GIP §1.1 + DPK-I11) — ordinary path only.
        if not is_writable(packet):
            return _reject(
                "NOT_WRITABLE",
                "lifecycle_status/review_result/execution_mode/hard_block not satisfied",
            )

        return WriteGateDecision(
            outcome=GateOutcome.PLATFORM_WRITE,
            reason_code="GATE_PASS",
            detail="skeleton: still dry_run only this round; LIVE write prohibited",
            receipt_status=ReceiptStatus.SIMULATED if envelope.dry_run else ReceiptStatus.ACCEPTED,
            passed_gate_ids=("G-01", "G-07"),
        )
