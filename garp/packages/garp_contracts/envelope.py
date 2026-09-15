"""RuntimeEnvelope + SelfcheckRecord.

Source: Runtime_Envelope_Selfcheck_v0.1.md §1, §5
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Any, Optional

from garp_contracts.enums import (
    AdapterRuntime,
    EnvLabel,
    ExecutionMode,
    LearningPool,
    PacketKind,
    ReceiptSource,
    RuntimeMode,
    SelfcheckStatus,
)


@dataclass(frozen=True)
class RuntimeEnvelope:
    """Forced-transparent runtime context. Do not launder env fields mid-pipeline (RE-I6)."""

    env: EnvLabel
    mode: RuntimeMode
    adapter_runtime: AdapterRuntime
    dry_run: bool
    receipt_source: ReceiptSource
    learning_pool: LearningPool
    trust_credit_allowed: bool
    execution_mode: ExecutionMode
    packet_kind: PacketKind
    envelope_id: str
    session_id: str
    config_ref: str
    captured_at: datetime
    actor: str = "BOOT"
    version: str = "0.1.0"
    selfcheck_ref: Optional[str] = None

    def with_selfcheck_ref(self, ref: str) -> "RuntimeEnvelope":
        return replace(self, selfcheck_ref=ref)

    def assert_invariants(self) -> None:
        """RE-I1..I4 / RE-I8 static combinations. Fail-closed."""
        if self.env != EnvLabel.LIVE and self.learning_pool == LearningPool.LIVE_POOL:
            raise ValueError("RE-I1: non-LIVE env must not use LIVE_POOL")
        if self.env != EnvLabel.LIVE and self.trust_credit_allowed:
            raise ValueError("RE-I2: non-LIVE env forbids trust_credit_allowed")
        if self.mode in (RuntimeMode.MODE_SHADOW_DECIDE, RuntimeMode.MODE_SHADOW_EXEC_SIM):
            if not self.dry_run:
                raise ValueError("RE-I3: shadow modes require dry_run=true")
            if self.execution_mode != ExecutionMode.SHADOW_READ_ONLY:
                raise ValueError("RE-I3: shadow modes require SHADOW_READ_ONLY")
        if self.mode == RuntimeMode.MODE_LIVE_WRITE:
            raise ValueError("RE-I4: MODE_LIVE_WRITE not authorized this round")
        if self.packet_kind == PacketKind.SHADOW_DECISION:
            if self.execution_mode != ExecutionMode.SHADOW_READ_ONLY:
                raise ValueError("RE-I8: shadow_decision ⇔ SHADOW_READ_ONLY")


@dataclass
class CheckItem:
    check_id: str
    phase: str  # CONFIG | TRANSPORT | WRITE_PROBE | PASSTHROUGH | ISOLATION
    result: str  # PASS | FAIL | SKIPPED | WARN
    detail: str = ""
    reason_codes: tuple[str, ...] = ()


@dataclass
class SelfcheckRecord:
    selfcheck_id: str
    session_id: str
    envelope_id: str
    kind: str  # BOOT | PROBE | CIRCUIT_TRIP | REBIND | AUDIT_SAMPLE
    status: SelfcheckStatus
    started_at: datetime
    finished_at: datetime
    config_ref: str
    env: str
    mode: str
    adapter_runtime: str
    dry_run: bool
    execution_mode: str
    live_transport_state: str
    credential_state: str
    checks: list[CheckItem] = field(default_factory=list)
    failed_check_ids: list[str] = field(default_factory=list)
    reason_codes: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    schema_version: str = "0.1.0"
    actor: str = "BOOT"
    extra: dict[str, Any] = field(default_factory=dict)
