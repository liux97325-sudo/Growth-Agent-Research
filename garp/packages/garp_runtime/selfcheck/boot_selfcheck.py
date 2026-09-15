"""Boot selfcheck — SC-A / SC-B / SC-C subset (fixture-only probes, no network).

Source: Runtime_Envelope_Selfcheck_v0.1.md §3
"""

from __future__ import annotations

import uuid
from datetime import datetime

from garp_contracts.adapter import AbstractActionRequest
from garp_contracts.enums import (
    AdapterRuntime,
    EnvLabel,
    ExecutionMode,
    LifecycleStatus,
    PacketKind,
    ReceiptStatus,
    ReviewResult,
    RiskLevel,
    RuntimeMode,
    SelfcheckStatus,
)
from garp_contracts.envelope import CheckItem, RuntimeEnvelope, SelfcheckRecord
from garp_contracts.packet import (
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
)
from garp_edge.adapter.fixture_transport import FixtureTransport
from garp_edge.adapter.live_stub import LiveTransportNotAssembled, LiveTransportStub
from garp_runtime.bootstrap.credentials import (
    CredentialObservationError,
    observe_credential_state,
)


def _now() -> datetime:
    return datetime.now().astimezone()


def _probe_shadow_packet(envelope: RuntimeEnvelope) -> DecisionPacket:
    now = _now()
    return DecisionPacket(
        decision_id=f"DP-PROBE-{uuid.uuid4().hex[:8]}",
        schema_version="0.1.0",
        revision=1,
        status=LifecycleStatus.SELF_REVIEWED,
        packet_kind=PacketKind.SHADOW_DECISION,
        execution_mode=ExecutionMode.SHADOW_READ_ONLY,
        tenant_id="TEN-PROBE",
        shop_id="SHOP-PROBE",
        domain="JD_AD",
        episode_id="EP-PROBE",
        created_at=now,
        updated_at=now,
        objective_snapshot=ObjectiveSnapshot(template_id="T-PROBE", weights={"ctr": 1.0}),
        state_digest=StateDigest(
            state_id="STATE-PROBE",
            as_of=now,
            hash="sha256:probe",
            plan_mode="SEEDING",
            lifecycle_phase="growth",
        ),
        forecast_ref=ForecastRef(
            forecast_id="FC-PROBE",
            horizon="2h",
            confidence=0.9,
            based_on_validated_ids=("VM-PROBE",),
        ),
        hypothesis=Hypothesis(observation={}, cause_claim="probe", confidence=0.5),
        proposed_actions=(
            ProposedAction(
                action_id="ACT-PROBE-001",
                action_type="WA-BID-01",
                action_class="KEYWORD_BID",
                target={"plan_id": "PLAN-PROBE"},
                change={"field": "bid", "from_value": 1.0, "to_value": 1.1, "relative_pct": 0.1},
                rationale_ref="probe",
            ),
        ),
        expected_response_window=ResponseWindow(
            min_minutes=60, max_minutes=180, metric_hint=("impressions",)
        ),
        risk=RiskEval(risk_level=RiskLevel.R1),
        trust=TrustEval(trust_required=0, trust_actual=0),
        review=SRAReview(
            review_result=ReviewResult.APPROVE,
            approved_by="AGENT",
            review_event_id="REV-PROBE",
        ),
        tags=("shadow", "selfcheck-probe"),
    )


def run_boot_selfcheck(envelope: RuntimeEnvelope) -> SelfcheckRecord:
    started = _now()
    checks: list[CheckItem] = []

    # --- SC-A config ---
    try:
        envelope.assert_invariants()
        checks.append(CheckItem("SC-A3", "CONFIG", "PASS", "envelope invariants hold"))
    except ValueError as exc:
        checks.append(CheckItem("SC-A3", "CONFIG", "FAIL", str(exc), ("ENVELOPE_INVALID",)))

    if envelope.execution_mode != ExecutionMode.SHADOW_READ_ONLY:
        checks.append(
            CheckItem(
                "SC-A4",
                "CONFIG",
                "FAIL",
                "only SHADOW_READ_ONLY allowed",
                ("EXEC_MODE_FORBIDDEN",),
            )
        )
    else:
        checks.append(CheckItem("SC-A4", "CONFIG", "PASS", "execution_mode=SHADOW_READ_ONLY"))

    if envelope.env == EnvLabel.LIVE or envelope.mode == RuntimeMode.MODE_LIVE_WRITE:
        checks.append(CheckItem("SC-A2", "CONFIG", "FAIL", "LIVE not authorized", ("LIVE_FORBIDDEN",)))
    else:
        checks.append(CheckItem("SC-A2", "CONFIG", "PASS", "non-LIVE envelope"))

    # SC-A5: observe credential provider for real (audit §6.3 — no hardcoded PASS).
    credential_state = "OBSERVATION_FAILED"
    try:
        cred_obs = observe_credential_state()
        credential_state = str(cred_obs.get("provider_type", "UNKNOWN"))
        if cred_obs.get("has_credentials") or cred_obs.get("probe_returned"):
            checks.append(
                CheckItem(
                    "SC-A5",
                    "CONFIG",
                    "FAIL",
                    f"unexpected credentials present: {cred_obs}",
                    ("CREDENTIALS_PRESENT",),
                )
            )
        else:
            checks.append(
                CheckItem(
                    "SC-A5",
                    "CONFIG",
                    "PASS",
                    f"observed provider={credential_state} "
                    f"has_credentials={cred_obs.get('has_credentials')}",
                    ("NO_CREDENTIALS",),
                )
            )
    except CredentialObservationError as exc:
        checks.append(
            CheckItem(
                "SC-A5",
                "CONFIG",
                "FAIL",
                str(exc),
                ("CREDENTIAL_OBSERVATION_FAILED",),
            )
        )

    # --- SC-B transport ---
    live_stub = LiveTransportStub(envelope)
    probe_packet = _probe_shadow_packet(envelope)
    if live_stub.state() == "FAIL_CLOSED_STUB" and envelope.adapter_runtime in (
        AdapterRuntime.FIXTURE_ONLY,
        AdapterRuntime.SIMULATION,
    ):
        checks.append(CheckItem("SC-B1", "TRANSPORT", "PASS", "LiveTransport=FAIL_CLOSED_STUB"))
    else:
        checks.append(
            CheckItem(
                "SC-B1",
                "TRANSPORT",
                "FAIL",
                "LiveTransport state unexpected",
                ("LIVE_TRANSPORT_MISASSEMBLED",),
            )
        )

    if envelope.adapter_runtime in (AdapterRuntime.SANDBOX_LIVE, AdapterRuntime.LIVE):
        checks.append(
            CheckItem("SC-B2", "TRANSPORT", "FAIL", "SANDBOX_LIVE/LIVE not allowed", ("LIVE_FORBIDDEN",))
        )
    else:
        checks.append(CheckItem("SC-B2", "TRANSPORT", "PASS", "adapter_runtime non-LIVE"))

    # SC-B3: egress guard via real LiveTransport.write probe (must raise fail-closed).
    # No hardcoded PASS — observation failure is a FAIL.
    try:
        probe_req = AbstractActionRequest(
            action_id="ACT-PROBE-001",
            action_type="WA-BID-01",
            action_class="KEYWORD_BID",
            decision_package_id="DP-PROBE-EGRESS",
            plan_mode="SEEDING",
            target={"plan_id": "PLAN-PROBE"},
            constraints={},
            rationale_ref="egress-probe",
            dry_run=False,
            envelope=envelope,
        )
        live_stub.write(probe_packet, probe_req)
        checks.append(
            CheckItem(
                "SC-B3",
                "TRANSPORT",
                "FAIL",
                "LiveTransport.write did not raise — egress guard broken",
                ("LIVE_TRANSPORT_MISASSEMBLED",),
            )
        )
    except LiveTransportNotAssembled as exc:
        checks.append(
            CheckItem(
                "SC-B3",
                "TRANSPORT",
                "PASS",
                f"egress guard observed: {type(exc).__name__}",
            )
        )
    except Exception as exc:  # noqa: BLE001 — unexpected exception type is not a PASS
        checks.append(
            CheckItem(
                "SC-B3",
                "TRANSPORT",
                "FAIL",
                f"unexpected egress exception: {type(exc).__name__}: {exc}",
                ("LIVE_TRANSPORT_MISASSEMBLED",),
            )
        )

    # --- SC-C write probe (fixture only) ---
    fixture = FixtureTransport(envelope)
    for action in probe_packet.proposed_actions:
        req = AbstractActionRequest(
            action_id=action.action_id,
            action_type=action.action_type,
            action_class=action.action_class,
            decision_package_id=probe_packet.decision_id,
            plan_mode="SEEDING",
            target=dict(action.target),
            constraints={"idempotency_key": f"probe:{action.action_id}"},
            rationale_ref=action.rationale_ref,
            dry_run=True,
            envelope=envelope,
            change=dict(action.change) if action.change else None,
        )
        receipt, decision = fixture.write(probe_packet, req)
        if (
            receipt.status == ReceiptStatus.REJECTED_BY_GATE
            and decision.reason_code == "SHADOW_WRITE_FORBIDDEN"
        ):
            checks.append(
                CheckItem(
                    "SC-C2",
                    "WRITE_PROBE",
                    "PASS",
                    "shadow write hard-rejected",
                    ("SHADOW_WRITE_FORBIDDEN",),
                )
            )
        elif receipt.status == ReceiptStatus.ACCEPTED:
            checks.append(
                CheckItem(
                    "SC-C1",
                    "WRITE_PROBE",
                    "FAIL",
                    "probe returned ACCEPTED — must not happen",
                    ("FALSE_ACK",),
                )
            )
        else:
            checks.append(
                CheckItem("SC-C1", "WRITE_PROBE", "PASS", f"probe status={receipt.status.value}")
            )

    # LiveTransport probe: must raise (fail-closed)
    try:
        live_stub.read()
        checks.append(
            CheckItem(
                "SC-B1b",
                "TRANSPORT",
                "FAIL",
                "LiveTransport.read did not raise",
                ("LIVE_TRANSPORT_MISASSEMBLED",),
            )
        )
    except Exception as exc:  # noqa: BLE001 — expected fail-closed
        checks.append(
            CheckItem(
                "SC-B1b",
                "TRANSPORT",
                "PASS",
                f"LiveTransport fail-closed: {type(exc).__name__}",
            )
        )

    # --- aggregate ---
    failed = [c.check_id for c in checks if c.result == "FAIL"]
    reason_codes: list[str] = []
    for c in checks:
        if c.result == "FAIL":
            reason_codes.extend(c.reason_codes)

    if failed:
        status = SelfcheckStatus.FAIL
        if "LIVE_TRANSPORT_MISASSEMBLED" in reason_codes or "LIVE_FORBIDDEN" in reason_codes:
            status = SelfcheckStatus.ABORT
    else:
        status = SelfcheckStatus.PASS

    record = SelfcheckRecord(
        selfcheck_id=f"SC-{uuid.uuid4().hex[:10]}",
        session_id=envelope.session_id,
        envelope_id=envelope.envelope_id,
        kind="BOOT",
        status=status,
        started_at=started,
        finished_at=_now(),
        config_ref=envelope.config_ref,
        env=envelope.env.value,
        mode=envelope.mode.value,
        adapter_runtime=envelope.adapter_runtime.value,
        dry_run=envelope.dry_run,
        execution_mode=envelope.execution_mode.value,
        live_transport_state=live_stub.state(),
        credential_state=credential_state,
        checks=checks,
        failed_check_ids=failed,
        reason_codes=reason_codes,
        evidence_refs=[],
        actor="BOOT",
    )
    return record
