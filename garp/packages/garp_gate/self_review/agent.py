"""SRA pseudo-implementation: sole writer of review_result (GIP C5 / D-04).

Skeleton only — predicate chain is a placeholder, not calibrated policy.
Audit GA2-R03 / §10.4: NO_ACTION requires NO_ACTION_APPROVE; empty actions
are schema-invalid; force_result is test-only and refused under LIVE.
"""

from __future__ import annotations

import uuid
from typing import Optional

from garp_contracts.enums import ExecutionMode, ReviewResult
from garp_contracts.packet import (
    DecisionPacket,
    PredicateResult,
    RiskEval,
    SRAReview,
    TrustEval,
    is_no_action,
    validate_packet_actions,
)


class SelfReviewAgent:
    """Placeholder SRA. hard_block non-empty ⇒ cannot APPROVE."""

    def review(
        self,
        packet: DecisionPacket,
        risk: RiskEval,
        trust: TrustEval,
        force_result: Optional[ReviewResult] = None,
    ) -> SRAReview:
        predicates: list[PredicateResult] = []

        # force_result is a test backdoor only (audit §10.5) — refuse LIVE.
        if force_result is not None and packet.execution_mode is ExecutionMode.LIVE:
            return SRAReview(
                review_result=ReviewResult.REJECT,
                approved_by="AGENT",
                predicate_trace=(
                    PredicateResult(id="CHK_FORCE", result="fail", detail="LIVE force_result forbidden"),
                ),
                reason_codes=("FORCE_RESULT_FORBIDDEN",),
                review_event_id=f"REV-{uuid.uuid4().hex[:10]}",
            )

        # CHK_SCHEMA (G-00 subset)
        violations = validate_packet_actions(packet)
        if "EMPTY_ACTIONS" in violations or "DUPLICATE_ACTION_ID" in violations:
            predicates.append(
                PredicateResult(id="CHK_SCHEMA", result="fail", detail=",".join(violations))
            )
            return SRAReview(
                review_result=ReviewResult.REJECT,
                approved_by="AGENT",
                predicate_trace=tuple(predicates),
                reason_codes=("ACTIONS_SCHEMA_INVALID",),
                review_event_id=f"REV-{uuid.uuid4().hex[:10]}",
            )
        predicates.append(PredicateResult(id="CHK_SCHEMA", result="pass"))

        # CHK_RISK
        if risk.hard_block:
            predicates.append(PredicateResult(id="CHK_RISK", result="fail", detail="hard_block"))
            return SRAReview(
                review_result=ReviewResult.REJECT,
                approved_by="AGENT",
                predicate_trace=tuple(predicates),
                reason_codes=("HARD_BLOCK",),
                review_event_id=f"REV-{uuid.uuid4().hex[:10]}",
            )
        predicates.append(PredicateResult(id="CHK_RISK", result="pass"))

        # CHK_TRUST (skeleton: actual >= required)
        if trust.trust_actual < trust.trust_required:
            predicates.append(PredicateResult(id="CHK_TRUST", result="fail"))
            return SRAReview(
                review_result=ReviewResult.HOLD,
                approved_by="AGENT",
                predicate_trace=tuple(predicates),
                reason_codes=("TRUST_BELOW_REQUIRED",),
                review_event_id=f"REV-{uuid.uuid4().hex[:10]}",
            )
        predicates.append(PredicateResult(id="CHK_TRUST", result="pass"))

        if force_result is not None:
            # Test-only forced outcome (non-LIVE). Marked for audit.
            return SRAReview(
                review_result=force_result,
                approved_by="AGENT",
                predicate_trace=tuple(predicates),
                reason_codes=("FORCED_FOR_TEST",),
                review_event_id=f"REV-{uuid.uuid4().hex[:10]}",
            )

        # NO_ACTION path (DPK-I2 / I10)
        if is_no_action(packet):
            if not (packet.no_action_reason or "").strip():
                predicates.append(
                    PredicateResult(id="CHK_STAB", result="fail", detail="missing no_action_reason")
                )
                return SRAReview(
                    review_result=ReviewResult.REJECT,
                    approved_by="AGENT",
                    predicate_trace=tuple(predicates),
                    reason_codes=("NO_ACTION_REASON_MISSING",),
                    review_event_id=f"REV-{uuid.uuid4().hex[:10]}",
                )
            predicates.append(PredicateResult(id="CHK_STAB", result="pass", detail="NO_ACTION"))
            return SRAReview(
                review_result=ReviewResult.NO_ACTION_APPROVE,
                approved_by="AGENT",
                predicate_trace=tuple(predicates),
                reason_codes=(),
                revise_round=0,
                review_event_id=f"REV-{uuid.uuid4().hex[:10]}",
            )

        predicates.append(PredicateResult(id="CHK_MODEL", result="pass", detail="skeleton"))
        return SRAReview(
            review_result=ReviewResult.APPROVE,
            approved_by="AGENT",
            predicate_trace=tuple(predicates),
            reason_codes=(),
            revise_round=0,
            review_event_id=f"REV-{uuid.uuid4().hex[:10]}",
        )
