"""Bootstrapper: load config → RuntimeEnvelope. Defaults FIXTURE / SHADOW_DECIDE.

Source: Runtime_Envelope_Selfcheck §3; Module_Skeleton §5.1
No credentials. LiveTransport never assembled here.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from garp_contracts.enums import (
    AdapterRuntime,
    EnvLabel,
    ExecutionMode,
    LearningPool,
    PacketKind,
    ReceiptSource,
    RuntimeMode,
)
from garp_contracts.envelope import RuntimeEnvelope


DEFAULT_CONFIG: dict[str, Any] = {
    # L1 default runtime — all values Proposed
    "env": "FIXTURE",
    "mode": "MODE_SHADOW_DECIDE",
    "adapter_runtime": "FIXTURE_ONLY",
    "dry_run": True,
    "receipt_source": "FIXTURE",
    "learning_pool": "SHADOW_POOL",
    "trust_credit_allowed": False,
    "execution_mode": "SHADOW_READ_ONLY",
    "packet_kind": "shadow_decision",
    "actor": "BOOT",
    # Proposed thresholds (not calibrated)
    "thresholds": {
        "forecast_write_confidence_min": 0.6,
        "n_revise_max": 2,
        "max_bid_delta_pct": 0.15,
        "max_budget_delta_pct": 0.10,
    },
}


def load_config(path: Optional[str] = None) -> dict[str, Any]:
    cfg = dict(DEFAULT_CONFIG)
    if path:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        # CLI/env override may only tighten safety, not escalate to LIVE (skeleton)
        if raw.get("mode") == "MODE_LIVE_WRITE" or raw.get("env") == "LIVE":
            raise PermissionError(
                "SC-A2: LIVE / MODE_LIVE_WRITE requires explicit GA-DEC; refused this round"
            )
        cfg.update(raw)
    return cfg


def bootstrap_envelope(config: Optional[dict[str, Any]] = None) -> RuntimeEnvelope:
    cfg = config or DEFAULT_CONFIG
    if cfg.get("mode") == "MODE_LIVE_WRITE" or cfg.get("env") == "LIVE":
        raise PermissionError("RE-I4 / SC-A2: LIVE not authorized this round")

    env = EnvLabel(cfg["env"])
    mode = RuntimeMode(cfg["mode"])
    adapter_runtime = AdapterRuntime(cfg["adapter_runtime"])
    execution_mode = ExecutionMode(cfg["execution_mode"])
    packet_kind = PacketKind(cfg["packet_kind"])
    dry_run = bool(cfg["dry_run"])
    learning_pool = LearningPool(cfg["learning_pool"])
    trust_credit_allowed = bool(cfg["trust_credit_allowed"])

    # SC-A3 / RE-I1..I3 forced defaults
    if env != EnvLabel.LIVE:
        trust_credit_allowed = False
        if learning_pool == LearningPool.LIVE_POOL:
            learning_pool = LearningPool.SHADOW_POOL
        dry_run = True

    if mode in (RuntimeMode.MODE_SHADOW_DECIDE, RuntimeMode.MODE_SHADOW_EXEC_SIM):
        execution_mode = ExecutionMode.SHADOW_READ_ONLY
        packet_kind = PacketKind.SHADOW_DECISION

    envelope = RuntimeEnvelope(
        env=env,
        mode=mode,
        adapter_runtime=adapter_runtime,
        dry_run=dry_run,
        receipt_source=ReceiptSource(cfg["receipt_source"]),
        learning_pool=learning_pool,
        trust_credit_allowed=trust_credit_allowed,
        execution_mode=execution_mode,
        packet_kind=packet_kind,
        envelope_id=f"ENV-{uuid.uuid4().hex[:12]}",
        session_id=f"SES-{uuid.uuid4().hex[:12]}",
        config_ref=str(config.get("config_ref", "configs/default.json") if config else "configs/default.json"),
        captured_at=datetime.now().astimezone(),
        actor=str(cfg.get("actor", "BOOT")),
    )
    envelope.assert_invariants()
    return envelope
