"""Contract enums aligned with Decision_Packet_Schema / GIP v0.2 / GA-DEC-006.

All thresholds / defaults referenced here are Proposed (see configs/).
"""

from __future__ import annotations

from enum import Enum


class LifecycleStatus(str, Enum):
    """Decision Packet lifecycle (NOT review result). Dual-field semantics: status + review.review_result."""

    DRAFT = "Draft"
    SELF_REVIEWED = "Self-reviewed"
    EXECUTED = "Executed"
    OBSERVED = "Observed"
    REFLECTED = "Reflected"
    ARCHIVED = "Archived"
    SUPERSEDED = "Superseded"


class ReviewResult(str, Enum):
    """SRA review outcome. Only SRA writes this field."""

    APPROVE = "APPROVE"
    NO_ACTION_APPROVE = "NO_ACTION_APPROVE"
    REVISE = "REVISE"
    HOLD = "HOLD"
    REJECT = "REJECT"
    ESCALATE_HUMAN = "ESCALATE_HUMAN"


class ExecutionMode(str, Enum):
    LIVE = "LIVE"
    SHADOW_READ_ONLY = "SHADOW_READ_ONLY"  # only mode allowed this round


class PacketKind(str, Enum):
    STANDARD = "standard"  # canonical; do not use live_decision
    SHADOW_DECISION = "shadow_decision"


class RiskLevel(str, Enum):
    R0 = "R0"
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"
    R4 = "R4"


class ReceiptStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED_BY_PLATFORM = "REJECTED_BY_PLATFORM"
    REJECTED_BY_GATE = "REJECTED_BY_GATE"
    TIMEOUT = "TIMEOUT"
    UNKNOWN = "UNKNOWN"
    SIMULATED = "SIMULATED"
    NOT_APPLICABLE_NO_ACTION = "NOT_APPLICABLE_NO_ACTION"


class EnvLabel(str, Enum):
    """Runtime environment label. GA-DEC-006: canonical includes HUMAN."""

    LIVE = "LIVE"
    SHADOW = "SHADOW"
    SIMULATION = "SIMULATION"
    FIXTURE = "FIXTURE"
    HUMAN = "HUMAN"


class SourceEnv(str, Enum):
    """Canonical receipt audit.source_env (GA-DEC-006).

    Historical alias: source=REAL must be normalized to LIVE.
    """

    LIVE = "LIVE"
    SHADOW = "SHADOW"
    SIMULATION = "SIMULATION"
    FIXTURE = "FIXTURE"
    HUMAN = "HUMAN"


def normalize_source_env(raw: str) -> SourceEnv:
    """Normalize historical aliases (REAL → LIVE). Fail-closed on unknown."""
    value = (raw or "").strip().upper()
    if value == "REAL":
        return SourceEnv.LIVE
    try:
        return SourceEnv(value)
    except ValueError as exc:
        raise ValueError(f"SOURCE_ENV_INVALID: {raw!r}") from exc


class RuntimeMode(str, Enum):
    MODE_READ = "MODE_READ"
    MODE_SHADOW_DECIDE = "MODE_SHADOW_DECIDE"
    MODE_SHADOW_EXEC_SIM = "MODE_SHADOW_EXEC_SIM"
    MODE_LIVE_WRITE = "MODE_LIVE_WRITE"  # prohibited this round


class AdapterRuntime(str, Enum):
    FIXTURE_ONLY = "FIXTURE_ONLY"
    SIMULATION = "SIMULATION"
    SANDBOX_LIVE = "SANDBOX_LIVE"
    LIVE = "LIVE"


class LearningPool(str, Enum):
    LIVE_POOL = "LIVE_POOL"
    SHADOW_POOL = "SHADOW_POOL"
    DROPPED = "DROPPED"


class ReceiptSource(str, Enum):
    PLATFORM = "PLATFORM"
    GATE_ONLY = "GATE_ONLY"
    LOCAL_SIM = "LOCAL_SIM"
    FIXTURE = "FIXTURE"


class SelfcheckStatus(str, Enum):
    PASS = "PASS"
    PASS_READ_ONLY = "PASS_READ_ONLY"
    FAIL = "FAIL"
    ABORT = "ABORT"


class GateOutcome(str, Enum):
    """WriteGate decision outcome (GA2-R03 / audit §10.1).

    Replaces the overloaded boolean `allowed` as the authoritative signal:
    - PLATFORM_WRITE: ordinary action may enter the platform write path
      (still subject to transport authorization; this round LIVE write is prohibited).
    - SYNTHETIC_NO_ACTION: NO_ACTION approved → synthetic receipt only, never a platform write.
    - REJECT: hard refusal (schema, semantic mismatch, shadow write, etc.).
    - HOLD: suspended, may re-review later.
    - ESCALATE: handed to human review.
    """

    PLATFORM_WRITE = "PLATFORM_WRITE"
    SYNTHETIC_NO_ACTION = "SYNTHETIC_NO_ACTION"
    REJECT = "REJECT"
    HOLD = "HOLD"
    ESCALATE = "ESCALATE"
