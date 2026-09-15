"""Shared test helpers — build draft packets under fixture/shadow envelope."""

from __future__ import annotations

import sys
import uuid
from datetime import datetime
from pathlib import Path

# packages/ on sys.path when running from garp/ root
_ROOT = Path(__file__).resolve().parents[1]
_PKG = _ROOT / "packages"
if str(_PKG) not in sys.path:
    sys.path.insert(0, str(_PKG))

from garp_contracts.enums import (  # noqa: E402
    ExecutionMode,
    LifecycleStatus,
    PacketKind,
    ReviewResult,
    RiskLevel,
)
from garp_contracts.packet import (  # noqa: E402
    DecisionPacket,
    ForecastRef,
    Hypothesis,
    ObjectiveSnapshot,
    ProposedAction,
    ResponseWindow,
    RiskEval,
    SRAReview,
    StateDigest,
    TrustEval,
    is_no_action,
)
from garp_runtime.bootstrap.bootstrapper import bootstrap_envelope  # noqa: E402


def make_draft_packet(
    *,
    no_action: bool = False,
    empty_actions: bool = False,
    missing_no_action_reason: bool = False,
    execution_mode: ExecutionMode = ExecutionMode.SHADOW_READ_ONLY,
    packet_kind: PacketKind = PacketKind.SHADOW_DECISION,
    hard_block: tuple[str, ...] = (),
    decision_id: str | None = None,
) -> DecisionPacket:
    now = datetime.now().astimezone()
    if empty_actions:
        actions: tuple[ProposedAction, ...] = ()
    elif no_action:
        actions = (
            ProposedAction(
                action_id="ACT-001",
                action_type="WA-CLS-01",
                action_class="NO_ACTION",
                target={"plan_id": "PLAN-9012"},
                rationale_ref="stability_first",
            ),
        )
    else:
        actions = (
            ProposedAction(
                action_id="ACT-001",
                action_type="WA-BID-01",
                action_class="KEYWORD_BID",
                target={"plan_id": "PLAN-8821", "keyword_id": "KW-core-001"},
                change={"field": "bid", "from_value": 4.2, "to_value": 4.7, "relative_pct": 0.12},
                rationale_ref="hypothesis#cause_claim",
            ),
        )
    no_action_reason = "CHK_STAB" if no_action and not missing_no_action_reason else None
    return DecisionPacket(
        decision_id=decision_id or f"DP-JD-TEST-{uuid.uuid4().hex[:8]}",
        schema_version="0.1.0",
        revision=1,
        status=LifecycleStatus.DRAFT,
        packet_kind=packet_kind,
        execution_mode=execution_mode,
        tenant_id="TEN-DEMO",
        shop_id="SHOP-DEMO-01",
        domain="JD_AD",
        episode_id="EP-DEMO-0001",
        created_at=now,
        updated_at=now,
        objective_snapshot=ObjectiveSnapshot(
            template_id="T-MHB-HARVEST" if no_action else "T-MHB-SEED",
            weights={"ctr": 0.5, "clicks": 0.5},
        ),
        state_digest=StateDigest(
            state_id="STATE-TEST",
            as_of=now,
            hash="sha256:test",
            plan_mode="HARVEST" if no_action else "SEEDING",
            lifecycle_phase="mature" if no_action else "growth",
        ),
        forecast_ref=ForecastRef(
            forecast_id="FC-TEST",
            horizon="to_day_end" if no_action else "2h",
            confidence=0.8,
            based_on_validated_ids=("VM-TEST",),
        ),
        hypothesis=Hypothesis(
            observation={"metric": "trusted_roi" if no_action else "impressions"},
            cause_claim="stable band" if no_action else "kw competition",
            confidence=0.7,
        ),
        proposed_actions=actions,
        expected_response_window=ResponseWindow(
            min_minutes=0 if no_action else 120,
            max_minutes=1440 if no_action else 360,
            metric_hint=("trusted_roi",) if no_action else ("impressions", "clicks"),
        ),
        risk=RiskEval(risk_level=RiskLevel.R1 if no_action else RiskLevel.R2, hard_block=hard_block),
        trust=TrustEval(trust_required=0 if no_action else 2, trust_actual=3),
        no_action_reason=no_action_reason,
        tags=("shadow", "fixture-test"),
    )


def apply_review(packet: DecisionPacket, result: ReviewResult | None = None) -> DecisionPacket:
    if result is None:
        if is_no_action(packet):
            result = ReviewResult.NO_ACTION_APPROVE
        else:
            result = ReviewResult.APPROVE
    review = SRAReview(
        review_result=result,
        approved_by="AGENT",
        predicate_trace=(),
        review_event_id=f"REV-{uuid.uuid4().hex[:8]}",
    )
    return packet.with_review(review)


def make_action_request(packet: DecisionPacket, envelope, *, dry_run: bool = True):
    """Build an AbstractActionRequest matching packet's first action (or a stub for empty)."""
    from garp_contracts.adapter import AbstractActionRequest

    if packet.proposed_actions:
        action = packet.proposed_actions[0]
        return AbstractActionRequest(
            action_id=action.action_id,
            action_type=action.action_type,
            action_class=action.action_class,
            decision_package_id=packet.decision_id,
            plan_mode=packet.state_digest.plan_mode,
            target=dict(action.target),
            constraints={"idempotency_key": f"{packet.decision_id}:{action.action_id}"},
            rationale_ref=action.rationale_ref,
            dry_run=dry_run,
            envelope=envelope,
            change=dict(action.change) if action.change else None,
        )
    return AbstractActionRequest(
        action_id="ACT-EMPTY",
        action_type="WA-BID-01",
        action_class="KEYWORD_BID",
        decision_package_id=packet.decision_id,
        plan_mode="SEEDING",
        target={},
        constraints={},
        rationale_ref="",
        dry_run=dry_run,
        envelope=envelope,
    )


def default_envelope():
    return bootstrap_envelope()
