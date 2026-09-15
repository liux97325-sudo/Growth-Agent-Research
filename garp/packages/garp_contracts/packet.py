"""DecisionPacket + is_writable dual-field gate.

Source: Decision_Packet_Schema_v0.1.md, Module_Skeleton_Design_v0.1.md §4.1
Dual-field: status (lifecycle) + review.review_result (approval).
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Any, Optional

from garp_contracts.enums import (
    ExecutionMode,
    LifecycleStatus,
    PacketKind,
    ReviewResult,
    RiskLevel,
)


@dataclass(frozen=True)
class Hypothesis:
    observation: dict[str, Any]
    cause_claim: str
    confidence: float  # [0,1] Proposed range
    supporting_signals: tuple[str, ...] = ()
    rival_hypotheses: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProposedAction:
    action_id: str
    action_type: str  # e.g. WA-BID-01 | WA-CLS-01
    action_class: str  # KEYWORD_BID | ... | NO_ACTION
    target: dict[str, Any]
    change: Optional[dict[str, Any]] = None  # omitted for NO_ACTION
    priority: int = 1
    rationale_ref: str = ""


@dataclass(frozen=True)
class RiskConstraints:
    max_bid_delta_pct: Optional[float] = None
    max_budget_delta_pct: Optional[float] = None
    max_daily_adjust_count: Optional[int] = None
    min_response_window_minutes: Optional[int] = None
    allow_new_plan: bool = False
    exploration_budget_cap: Optional[float] = None
    require_higher_trust: Optional[int] = None
    review_mode: str = "STANDARD"  # LITE | STANDARD | STRICT | HUMAN


@dataclass(frozen=True)
class RiskEval:
    risk_level: RiskLevel
    hard_block: tuple[str, ...] = ()
    constraints: RiskConstraints = field(default_factory=RiskConstraints)
    reason_codes: tuple[str, ...] = ()
    baseline_version: str = "RB-PROPOSED-0.1"
    dimensions: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TrustEval:
    trust_required: int  # 0–5
    trust_actual: int  # 0–5
    trust_score_snapshot: Optional[float] = None  # 0–100
    version: Optional[str] = None


@dataclass(frozen=True)
class PredicateResult:
    id: str  # CHK_MODEL / CHK_RISK / ...
    result: str  # pass | fail | unknown
    detail: Optional[str] = None


@dataclass(frozen=True)
class SRAReview:
    review_result: ReviewResult
    approved_by: str  # AGENT | HUMAN
    predicate_trace: tuple[PredicateResult, ...] = ()
    reason_codes: tuple[str, ...] = ()
    revise_round: Optional[int] = None
    human_ticket_id: Optional[str] = None
    review_event_id: str = ""


@dataclass(frozen=True)
class StateDigest:
    state_id: str
    as_of: datetime
    hash: str
    plan_mode: str  # SEEDING | HARVEST | MIXED | UNKNOWN
    lifecycle_phase: str
    gap_flags: tuple[str, ...] = ()
    validation_confidence: str = "HIGH"  # HIGH | MEDIUM | LOW
    inventory_risk: Optional[str] = None


@dataclass(frozen=True)
class ForecastRef:
    forecast_id: str
    horizon: str
    confidence: float  # [0,1]; Proposed write-trigger floor ≥0.6
    summary: dict[str, Any] = field(default_factory=dict)
    based_on_validated_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ObjectiveSnapshot:
    template_id: str
    weights: dict[str, float]
    lifecycle_bias: Optional[str] = None
    explanation: Optional[str] = None


@dataclass(frozen=True)
class ResponseWindow:
    min_minutes: int
    max_minutes: int
    metric_hint: tuple[str, ...] = ()


@dataclass(frozen=True)
class DecisionPacket:
    """Growth minimal atomic unit. Logical immutability; transitions return new instances."""

    decision_id: str
    schema_version: str  # semver e.g. "0.1.0"
    revision: int
    status: LifecycleStatus  # lifecycle, NOT review result
    packet_kind: PacketKind
    execution_mode: ExecutionMode
    tenant_id: str
    shop_id: str
    domain: str  # JD_AD | DOUYIN_OPS
    episode_id: str
    created_at: datetime
    updated_at: datetime
    objective_snapshot: ObjectiveSnapshot
    state_digest: StateDigest
    forecast_ref: ForecastRef
    hypothesis: Hypothesis
    proposed_actions: tuple[ProposedAction, ...]  # minItems=1
    expected_response_window: ResponseWindow
    risk: RiskEval
    trust: TrustEval
    review: Optional[SRAReview] = None
    action_receipts: tuple[dict[str, Any], ...] = ()
    no_action_reason: Optional[str] = None
    parent_decision_id: Optional[str] = None
    tags: tuple[str, ...] = ()

    def with_review(self, review: SRAReview) -> "DecisionPacket":
        """Apply SRA review → status=SELF_REVIEWED. Only SRA path should call this."""
        return replace(
            self,
            review=review,
            status=LifecycleStatus.SELF_REVIEWED,
            updated_at=datetime.now().astimezone(),
        )


def is_writable(packet: DecisionPacket) -> bool:
    """Ordinary platform-write admission (GIP v0.2 §1.1 dual-field + DPK-I11/I12).

    Rules (audit GA2-R03 / §10.3):
    - NO_ACTION packets are NEVER platform-writable (use SYNTHETIC_NO_ACTION path).
    - Ordinary actions require review_result == APPROVE only;
      NO_ACTION_APPROVE must not approve ordinary side-effect actions.
    - status must be Self-reviewed (Executed retry path is not implemented this round).
    - empty proposed_actions is schema-invalid → not writable.

    Raises nothing; returns bool.
    """
    # Empty action set is schema-invalid; all([]) must not make a packet writable.
    if not packet.proposed_actions:
        return False
    # NO_ACTION packets never take the platform write path.
    if is_no_action(packet):
        return False
    if packet.status is not LifecycleStatus.SELF_REVIEWED:
        # Executed re-entry requires a controlled retry branch (not in this skeleton).
        return False
    if packet.review is None:
        return False
    # DPK-I11: only APPROVE admits ordinary writes. NO_ACTION_APPROVE is for NO_ACTION only.
    if packet.review.review_result is not ReviewResult.APPROVE:
        return False
    if packet.execution_mode is not ExecutionMode.LIVE:
        return False  # SHADOW_READ_ONLY never writable
    if packet.risk.hard_block:
        return False
    return True


def is_no_action(packet: DecisionPacket) -> bool:
    """DPK-I9: true iff proposed_actions is non-empty AND every action_class == NO_ACTION.

    Empty action set must NOT be treated as NO_ACTION (all([]) is True in Python).
    """
    actions = packet.proposed_actions
    return bool(actions) and all(a.action_class == "NO_ACTION" for a in actions)


def validate_packet_actions(packet: DecisionPacket) -> tuple[str, ...]:
    """Minimal action-schema checks used by WriteGate / SRA / negative tests.

    Returns a tuple of violation codes; empty tuple means no action-level violations.
    """
    codes: list[str] = []
    actions = packet.proposed_actions
    if not actions:
        codes.append("EMPTY_ACTIONS")
        return tuple(codes)

    seen: set[str] = set()
    for a in actions:
        if a.action_id in seen:
            codes.append("DUPLICATE_ACTION_ID")
        seen.add(a.action_id)
        if a.action_class == "NO_ACTION":
            if a.change is not None:
                codes.append("NO_ACTION_WITH_CHANGE")
        elif a.change is None:
            codes.append("ACTION_MISSING_CHANGE")

    if is_no_action(packet) and not (packet.no_action_reason or "").strip():
        codes.append("NO_ACTION_REASON_MISSING")
    return tuple(codes)


def assert_packet_envelope_consistency(
    packet: DecisionPacket, execution_mode: ExecutionMode, packet_kind: PacketKind
) -> None:
    """RA-10 / RE-I8: shadow_decision ⇔ SHADOW_READ_ONLY."""
    if packet.packet_kind == PacketKind.SHADOW_DECISION:
        if packet.execution_mode != ExecutionMode.SHADOW_READ_ONLY:
            raise ValueError("PACKET_KIND_MISMATCH: shadow_decision requires SHADOW_READ_ONLY")
        if execution_mode != ExecutionMode.SHADOW_READ_ONLY or packet_kind != PacketKind.SHADOW_DECISION:
            raise ValueError("PACKET_KIND_MISMATCH: envelope/packet inconsistent")
