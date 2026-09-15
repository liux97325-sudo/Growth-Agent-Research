#!/usr/bin/env python3
"""CLI: boot envelope + selfcheck. No network. No credentials.

Usage (from garp/ root):
    python apps/cli/selfcheck.py
    python apps/cli/selfcheck.py --config configs/default.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_PKG = _ROOT / "packages"
if str(_PKG) not in sys.path:
    sys.path.insert(0, str(_PKG))

from garp_runtime.bootstrap.bootstrapper import bootstrap_envelope, load_config  # noqa: E402
from garp_runtime.selfcheck.boot_selfcheck import run_boot_selfcheck  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="GARP fixture boot selfcheck")
    parser.add_argument(
        "--config",
        default=str(_ROOT / "configs" / "default.json"),
        help="path to runtime config JSON (Proposed defaults)",
    )
    args = parser.parse_args(argv)

    try:
        cfg = load_config(args.config)
        envelope = bootstrap_envelope(cfg)
    except PermissionError as exc:
        print(f"BOOT_REFUSED: {exc}", file=sys.stderr)
        return 2

    record = run_boot_selfcheck(envelope)
    payload = {
        "selfcheck_id": record.selfcheck_id,
        "session_id": record.session_id,
        "envelope_id": record.envelope_id,
        "status": record.status.value,
        "env": record.env,
        "mode": record.mode,
        "adapter_runtime": record.adapter_runtime,
        "execution_mode": record.execution_mode,
        "live_transport_state": record.live_transport_state,
        "credential_state": record.credential_state,
        "dry_run": record.dry_run,
        "failed_check_ids": record.failed_check_ids,
        "reason_codes": record.reason_codes,
        "checks": [
            {
                "check_id": c.check_id,
                "phase": c.phase,
                "result": c.result,
                "detail": c.detail,
                "reason_codes": list(c.reason_codes),
            }
            for c in record.checks
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if record.status.value in ("PASS", "PASS_READ_ONLY") else 1


if __name__ == "__main__":
    raise SystemExit(main())
