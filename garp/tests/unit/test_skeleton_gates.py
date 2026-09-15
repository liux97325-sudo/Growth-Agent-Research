"""Minimal unit tests — stdlib unittest only.

Run from garp/ root:
    python -m unittest discover -s tests/unit -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_PKG = _ROOT / "packages"
for _p in (_ROOT, _PKG):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from garp_contracts.enums import (  # noqa: E402
    ExecutionMode,
    GateOutcome,
    LifecycleStatus,
    PacketKind,
    ReceiptStatus,
    ReviewResult,
    SourceEnv,
)
from garp_contracts.adapter import AbstractActionRequest  # noqa: E402
from garp_contracts.packet import is_no_action, is_writable  # noqa: E402
from garp_edge.adapter.fixture_transport import FixtureTransport  # noqa: E402
from garp_edge.adapter.live_stub import LiveTransportStub, LiveTransportNotAssembled  # noqa: E402
from garp_gate.self_review.agent import SelfReviewAgent  # noqa: E402
from garp_gate.trust.filter import TrustSignal, ingest_signal, is_live_eligible  # noqa: E402
from garp_contracts.enums import normalize_source_env  # noqa: E402
from garp_runtime.bootstrap.bootstrapper import bootstrap_envelope  # noqa: E402
from garp_runtime.selfcheck.boot_selfcheck import run_boot_selfcheck  # noqa: E402

from tests.conftest import apply_review, default_envelope, make_draft_packet  # noqa: E402


class TestNoActionPacket(unittest.TestCase):
    """DPK-I2: NO_ACTION still forms a packet and passes SRA with NO_ACTION_APPROVE."""

    def test_no_action_packaging(self):
        draft = make_draft_packet(no_action=True)
        self.assertEqual(draft.status, LifecycleStatus.DRAFT)
        self.assertTrue(is_no_action(draft))

        sra = SelfReviewAgent()
        review = sra.review(draft, draft.risk, draft.trust)
        self.assertEqual(review.review_result, ReviewResult.NO_ACTION_APPROVE)

        packet = draft.with_review(review)
        self.assertEqual(packet.status, LifecycleStatus.SELF_REVIEWED)
        self.assertIsNotNone(packet.review)
        self.assertEqual(packet.review.review_result, ReviewResult.NO_ACTION_APPROVE)
        # Dual-field: lifecycle advanced, review written; still not platform-writable under SHADOW
        self.assertFalse(is_writable(packet))

        envelope = default_envelope()
        fixture = FixtureTransport(envelope)
        action = packet.proposed_actions[0]
        req = AbstractActionRequest(
            action_id=action.action_id,
            action_type=action.action_type,
            action_class=action.action_class,
            decision_package_id=packet.decision_id,
            plan_mode="HARVEST",
            target=dict(action.target),
            constraints={"idempotency_key": f"{packet.decision_id}:{action.action_id}"},
            rationale_ref=action.rationale_ref,
            dry_run=True,
            envelope=envelope,
        )
        receipt, decision = fixture.write(packet, req)
        self.assertEqual(receipt.status, ReceiptStatus.NOT_APPLICABLE_NO_ACTION)
        self.assertEqual(decision.outcome, GateOutcome.SYNTHETIC_NO_ACTION)
        self.assertTrue(decision.allowed)  # deprecated alias
        self.assertTrue(decision.is_synthetic_no_action)
        self.assertEqual(receipt.audit.source_env, SourceEnv.FIXTURE)


class TestShadowWriteReject(unittest.TestCase):
    """DPK-I5 / RA-02 / G-01: SHADOW_READ_ONLY write path hard-rejects."""

    def test_shadow_write_rejected(self):
        draft = make_draft_packet(
            no_action=False,
            execution_mode=ExecutionMode.SHADOW_READ_ONLY,
            packet_kind=PacketKind.SHADOW_DECISION,
        )
        packet = apply_review(draft, ReviewResult.APPROVE)
        self.assertEqual(packet.status, LifecycleStatus.SELF_REVIEWED)
        self.assertFalse(is_writable(packet))  # SHADOW never writable

        envelope = default_envelope()
        fixture = FixtureTransport(envelope)
        action = packet.proposed_actions[0]
        req = AbstractActionRequest(
            action_id=action.action_id,
            action_type=action.action_type,
            action_class=action.action_class,
            decision_package_id=packet.decision_id,
            plan_mode="SEEDING",
            target=dict(action.target),
            constraints={"idempotency_key": f"{packet.decision_id}:{action.action_id}"},
            rationale_ref=action.rationale_ref,
            dry_run=True,
            envelope=envelope,
            change=dict(action.change) if action.change else None,
        )
        receipt, decision = fixture.write(packet, req)
        self.assertEqual(decision.outcome, GateOutcome.REJECT)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, "SHADOW_WRITE_FORBIDDEN")
        self.assertEqual(receipt.status, ReceiptStatus.REJECTED_BY_GATE)
        self.assertNotEqual(receipt.status, ReceiptStatus.ACCEPTED)

    def test_live_transport_fail_closed(self):
        envelope = default_envelope()
        stub = LiveTransportStub(envelope)
        self.assertEqual(stub.state(), "FAIL_CLOSED_STUB")
        with self.assertRaises(LiveTransportNotAssembled):
            stub.read()
        with self.assertRaises(LiveTransportNotAssembled):
            draft = make_draft_packet()
            action = draft.proposed_actions[0]
            req = AbstractActionRequest(
                action_id=action.action_id,
                action_type=action.action_type,
                action_class=action.action_class,
                decision_package_id=draft.decision_id,
                plan_mode="SEEDING",
                target=dict(action.target),
                constraints={},
                rationale_ref=action.rationale_ref,
                dry_run=False,
                envelope=envelope,
            )
            stub.write(draft, req)


class TestSourceEnvFilter(unittest.TestCase):
    """P-02 / RA-06: only canonical LIVE source_env credits live Trust; HUMAN is valid but non-live."""

    def test_non_live_source_env_rejected_for_trust(self):
        envelope = default_envelope()
        for env_val in (SourceEnv.SHADOW, SourceEnv.SIMULATION, SourceEnv.FIXTURE, SourceEnv.HUMAN):
            signal = TrustSignal(signal_id=f"TS-{env_val.value}", source_env=env_val, score_delta=1.0)
            result = ingest_signal(signal, envelope)
            self.assertFalse(result.accepted_for_live)
            self.assertEqual(result.reason_code, "TRUST_CREDIT_FORBIDDEN")
            self.assertFalse(is_live_eligible(env_val))

    def test_canonical_set_includes_human_and_normalizes_real(self):
        for name in ("LIVE", "SHADOW", "SIMULATION", "FIXTURE", "HUMAN"):
            normalize_source_env(name)
        self.assertEqual(normalize_source_env("REAL"), SourceEnv.LIVE)
        self.assertEqual(normalize_source_env("real"), SourceEnv.LIVE)
        with self.assertRaises(ValueError):
            normalize_source_env("LEGACY")

    def test_boot_selfcheck_pass_on_default_fixture(self):
        envelope = default_envelope()
        record = run_boot_selfcheck(envelope)
        self.assertEqual(record.status.value, "PASS")
        self.assertEqual(record.live_transport_state, "FAIL_CLOSED_STUB")
        self.assertEqual(record.credential_state, "EmptyCredentialProvider")
        self.assertTrue(envelope.dry_run)
        self.assertFalse(envelope.trust_credit_allowed)
        # Evidence-based checks must actually run (not be absent).
        check_ids = {c.check_id for c in record.checks}
        self.assertIn("SC-A5", check_ids)
        self.assertIn("SC-B3", check_ids)
        sc_a5 = next(c for c in record.checks if c.check_id == "SC-A5")
        self.assertEqual(sc_a5.result, "PASS")
        self.assertIn("observed provider=EmptyCredentialProvider", sc_a5.detail)


if __name__ == "__main__":
    unittest.main()
