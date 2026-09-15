"""Negative tests for P0 gate semantics (audit GA-2 §11.2 minimum set).

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

from garp_contracts.adapter import AbstractActionRequest  # noqa: E402
from garp_contracts.enums import (  # noqa: E402
    ExecutionMode,
    GateOutcome,
    PacketKind,
    ReceiptStatus,
    ReviewResult,
    SourceEnv,
    normalize_source_env,
)
from garp_contracts.packet import (  # noqa: E402
    is_no_action,
    is_writable,
    validate_packet_actions,
)
from garp_edge.adapter.fixture_transport import FixtureTransport  # noqa: E402
from garp_edge.adapter.write_gate import WriteGate  # noqa: E402
from garp_gate.self_review.agent import SelfReviewAgent  # noqa: E402
from garp_gate.trust.filter import TrustSignal, ingest_signal, is_live_eligible  # noqa: E402
from garp_runtime.bootstrap.credentials import observe_credential_state  # noqa: E402

from tests.conftest import (  # noqa: E402
    apply_review,
    default_envelope,
    make_action_request,
    make_draft_packet,
)


class TestIsNoActionEmptyActions(unittest.TestCase):
    """DPK-I9: empty proposed_actions is NOT NO_ACTION."""

    def test_empty_actions_not_no_action(self):
        packet = make_draft_packet(empty_actions=True)
        self.assertEqual(len(packet.proposed_actions), 0)
        self.assertFalse(is_no_action(packet))  # all([]) must not pass

    def test_all_no_action_is_no_action(self):
        packet = make_draft_packet(no_action=True)
        self.assertTrue(is_no_action(packet))

    def test_mixed_actions_not_no_action(self):
        packet = make_draft_packet(no_action=False)
        # ordinary KEYWORD_BID only
        self.assertFalse(is_no_action(packet))

    def test_validate_empty_actions(self):
        packet = make_draft_packet(empty_actions=True)
        self.assertIn("EMPTY_ACTIONS", validate_packet_actions(packet))


class TestReviewActionMismatch(unittest.TestCase):
    """Audit §11.2: ordinary + NO_ACTION_APPROVE; NO_ACTION + APPROVE."""

    def test_ordinary_plus_no_action_approve_rejected(self):
        envelope = default_envelope()
        draft = make_draft_packet(no_action=False)
        packet = apply_review(draft, ReviewResult.NO_ACTION_APPROVE)
        self.assertFalse(is_writable(packet))

        gate = WriteGate()
        req = make_action_request(packet, envelope)
        decision = gate.evaluate(packet, req, envelope)
        self.assertEqual(decision.outcome, GateOutcome.REJECT)
        self.assertEqual(decision.reason_code, "NO_ACTION_APPROVE_CANNOT_WRITE")
        self.assertFalse(decision.allowed)

    def test_no_action_plus_approve_rejected(self):
        envelope = default_envelope()
        draft = make_draft_packet(no_action=True)
        packet = apply_review(draft, ReviewResult.APPROVE)
        self.assertTrue(is_no_action(packet))

        gate = WriteGate()
        req = make_action_request(packet, envelope)
        decision = gate.evaluate(packet, req, envelope)
        self.assertEqual(decision.outcome, GateOutcome.REJECT)
        self.assertEqual(decision.reason_code, "NO_ACTION_REVIEW_MISMATCH")
        self.assertFalse(decision.is_synthetic_no_action)

        receipt, _ = FixtureTransport(envelope).write(packet, req)
        self.assertNotEqual(receipt.status, ReceiptStatus.NOT_APPLICABLE_NO_ACTION)
        self.assertNotEqual(receipt.status, ReceiptStatus.ACCEPTED)


class TestNoActionRejectedReviews(unittest.TestCase):
    """Audit GA2-R04 / §11.2: REJECT/HOLD/REVISE must not produce approved synthetic receipt."""

    def _evaluate_with_review(self, result: ReviewResult):
        envelope = default_envelope()
        draft = make_draft_packet(no_action=True)
        packet = apply_review(draft, result)
        gate = WriteGate()
        req = make_action_request(packet, envelope)
        decision = gate.evaluate(packet, req, envelope)
        receipt, _ = FixtureTransport(envelope).write(packet, req)
        return decision, receipt

    def test_no_action_plus_reject(self):
        decision, receipt = self._evaluate_with_review(ReviewResult.REJECT)
        self.assertEqual(decision.outcome, GateOutcome.REJECT)
        self.assertFalse(decision.is_synthetic_no_action)
        self.assertEqual(receipt.status, ReceiptStatus.REJECTED_BY_GATE)

    def test_no_action_plus_hold(self):
        decision, receipt = self._evaluate_with_review(ReviewResult.HOLD)
        self.assertEqual(decision.outcome, GateOutcome.HOLD)
        self.assertFalse(decision.is_synthetic_no_action)
        self.assertEqual(receipt.status, ReceiptStatus.REJECTED_BY_GATE)

    def test_no_action_plus_revise(self):
        decision, receipt = self._evaluate_with_review(ReviewResult.REVISE)
        self.assertEqual(decision.outcome, GateOutcome.REJECT)
        self.assertFalse(decision.is_synthetic_no_action)
        self.assertEqual(receipt.status, ReceiptStatus.REJECTED_BY_GATE)

    def test_no_action_plus_escalate(self):
        decision, _ = self._evaluate_with_review(ReviewResult.ESCALATE_HUMAN)
        self.assertEqual(decision.outcome, GateOutcome.ESCALATE)
        self.assertFalse(decision.is_synthetic_no_action)

    def test_no_action_approve_still_synthetic(self):
        decision, receipt = self._evaluate_with_review(ReviewResult.NO_ACTION_APPROVE)
        self.assertEqual(decision.outcome, GateOutcome.SYNTHETIC_NO_ACTION)
        self.assertTrue(decision.is_synthetic_no_action)
        self.assertTrue(decision.allowed)  # deprecated alias; outcome is authoritative
        self.assertEqual(receipt.status, ReceiptStatus.NOT_APPLICABLE_NO_ACTION)
        self.assertIsNone(receipt.platform_ack_ref)


class TestEmptyActionsGate(unittest.TestCase):
    """Empty actions → schema invalid; not treated as NO_ACTION."""

    def test_empty_actions_rejected_by_gate(self):
        envelope = default_envelope()
        draft = make_draft_packet(empty_actions=True)
        packet = apply_review(draft, ReviewResult.APPROVE)
        self.assertFalse(is_no_action(packet))

        gate = WriteGate()
        req = make_action_request(packet, envelope)
        decision = gate.evaluate(packet, req, envelope)
        self.assertEqual(decision.outcome, GateOutcome.REJECT)
        self.assertEqual(decision.reason_code, "EMPTY_ACTIONS")

    def test_empty_actions_rejected_by_sra(self):
        draft = make_draft_packet(empty_actions=True)
        sra = SelfReviewAgent()
        review = sra.review(draft, draft.risk, draft.trust)
        self.assertEqual(review.review_result, ReviewResult.REJECT)
        self.assertIn("ACTIONS_SCHEMA_INVALID", review.reason_codes)


class TestShadowWriteHardReject(unittest.TestCase):
    """FX-04: ordinary + APPROVE + Shadow → hard reject; outcome REJECT."""

    def test_shadow_write_outcome_reject(self):
        envelope = default_envelope()
        draft = make_draft_packet(
            no_action=False,
            execution_mode=ExecutionMode.SHADOW_READ_ONLY,
            packet_kind=PacketKind.SHADOW_DECISION,
        )
        packet = apply_review(draft, ReviewResult.APPROVE)
        gate = WriteGate()
        req = make_action_request(packet, envelope)
        decision = gate.evaluate(packet, req, envelope)
        self.assertEqual(decision.outcome, GateOutcome.REJECT)
        self.assertEqual(decision.reason_code, "SHADOW_WRITE_FORBIDDEN")
        self.assertFalse(decision.is_platform_write)

        receipt, _ = FixtureTransport(envelope).write(packet, req)
        self.assertEqual(receipt.status, ReceiptStatus.REJECTED_BY_GATE)


class TestSourceEnvNormalization(unittest.TestCase):
    """§11.2: source_env=REAL → normalize to LIVE; unknown → reject."""

    def test_real_normalizes_to_live(self):
        self.assertEqual(normalize_source_env("REAL"), SourceEnv.LIVE)
        self.assertEqual(normalize_source_env("real"), SourceEnv.LIVE)

    def test_unknown_source_env_rejected(self):
        with self.assertRaises(ValueError):
            normalize_source_env("LEGACY_PLATFORM")


class TestNonLiveTrustRejection(unittest.TestCase):
    """§11.2 / RE-I2: non-LIVE must not credit live Trust."""

    def test_non_live_envelope_rejects_trust_credit(self):
        envelope = default_envelope()
        self.assertFalse(envelope.trust_credit_allowed)
        signal = TrustSignal(signal_id="TS-1", source_env=SourceEnv.LIVE, score_delta=1.0)
        result = ingest_signal(signal, envelope)
        self.assertFalse(result.accepted_for_live)

    def test_non_live_source_env_not_eligible(self):
        for env_val in (SourceEnv.SHADOW, SourceEnv.SIMULATION, SourceEnv.FIXTURE, SourceEnv.HUMAN):
            self.assertFalse(is_live_eligible(env_val))


class TestIsWritableOrdinaryRules(unittest.TestCase):
    """DPK-I11/I12: ordinary write needs APPROVE; NO_ACTION never writable."""

    def test_no_action_approve_not_writable_for_ordinary(self):
        draft = make_draft_packet(no_action=False)
        packet = apply_review(draft, ReviewResult.NO_ACTION_APPROVE)
        self.assertFalse(is_writable(packet))

    def test_no_action_packet_never_writable(self):
        draft = make_draft_packet(no_action=True)
        packet = apply_review(draft, ReviewResult.NO_ACTION_APPROVE)
        self.assertTrue(is_no_action(packet))
        self.assertFalse(is_writable(packet))

    def test_draft_status_not_writable(self):
        draft = make_draft_packet(no_action=False)
        # still DRAFT, no review
        self.assertFalse(is_writable(draft))


class TestSelfcheckObservation(unittest.TestCase):
    """Selfcheck credential state is observed, not hardcoded."""

    def test_credential_provider_observed_empty(self):
        state = observe_credential_state()
        self.assertEqual(state["provider_type"], "EmptyCredentialProvider")
        self.assertFalse(state["has_credentials"])
        self.assertFalse(state["probe_returned"])


if __name__ == "__main__":
    unittest.main()
