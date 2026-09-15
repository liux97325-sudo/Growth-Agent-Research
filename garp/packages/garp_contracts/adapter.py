"""Adapter contracts: AbstractActionRequest / ActionReceipt.

Source: JD_Adapter_Interface_v0.2, Module_Skeleton_Design_v0.1.md §4.6
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from garp_contracts.enums import ReceiptStatus, SourceEnv
from garp_contracts.envelope import RuntimeEnvelope


@dataclass(frozen=True)
class ReceiptAudit:
    decision_id: str
    source_env: SourceEnv  # GA-DEC-006 canonical; REAL must be normalized to LIVE
    response_window_due_at: Optional[datetime] = None
    causal_memory_pending: bool = True


@dataclass(frozen=True)
class ActionReceipt:
    receipt_id: str
    action_id: str
    status: ReceiptStatus
    idempotency_key: str
    submitted_at: datetime
    audit: ReceiptAudit
    platform_ack_ref: Optional[str] = None


@dataclass(frozen=True)
class AbstractActionRequest:
    action_id: str
    action_type: str
    action_class: str
    decision_package_id: str
    plan_mode: str
    target: dict[str, Any]
    constraints: dict[str, Any]  # idempotency_key required at runtime
    rationale_ref: str
    dry_run: bool
    envelope: RuntimeEnvelope
    change: Optional[dict[str, Any]] = None


@dataclass(frozen=True)
class ResourceQuery:
    query_id: str
    resource: str
    scope: dict[str, Any] = field(default_factory=dict)
    fields: Optional[tuple[str, ...]] = None
    dry_run: bool = True  # RO always true
    envelope: Optional[RuntimeEnvelope] = None
