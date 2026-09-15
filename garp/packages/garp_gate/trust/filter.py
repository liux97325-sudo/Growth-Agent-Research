"""Trust signal filter — only LIVE source_env may credit live Trust (RE-I2 / RA-06 / P-02)."""

from __future__ import annotations

from dataclasses import dataclass

from garp_contracts.enums import LearningPool, SourceEnv
from garp_contracts.envelope import RuntimeEnvelope


@dataclass(frozen=True)
class TrustSignal:
    signal_id: str
    source_env: SourceEnv
    score_delta: float
    sample_ref: str = ""


@dataclass(frozen=True)
class IngestResult:
    accepted_for_live: bool
    pool: LearningPool
    reason_code: str
    detail: str = ""


def ingest_signal(signal: TrustSignal, envelope: RuntimeEnvelope) -> IngestResult:
    """Reject live credit when envelope.trust_credit_allowed is false or source_env != LIVE."""
    if not envelope.trust_credit_allowed or envelope.env.value != "LIVE":
        return IngestResult(
            accepted_for_live=False,
            pool=LearningPool.SHADOW_POOL,
            reason_code="TRUST_CREDIT_FORBIDDEN",
            detail="non-LIVE envelope; signal isolated to SHADOW_POOL",
        )
    if signal.source_env != SourceEnv.LIVE:
        return IngestResult(
            accepted_for_live=False,
            pool=LearningPool.SHADOW_POOL,
            reason_code="SOURCE_ENV_NOT_LIVE",
            detail=f"source_env={signal.source_env.value}; only LIVE credits live Trust",
        )
    return IngestResult(
        accepted_for_live=True,
        pool=LearningPool.LIVE_POOL,
        reason_code="OK",
    )


def is_live_eligible(source_env: SourceEnv | str) -> bool:
    """Canonical filter used by Memory/Trust entrypoints. REAL must already be normalized."""
    value = source_env.value if isinstance(source_env, SourceEnv) else str(source_env)
    return value.upper() == SourceEnv.LIVE.value
