#!/usr/bin/env python3
"""Static contract: every client-facing EOD branch uses the hash-bound delivery gate."""
from pathlib import Path


src = (Path(__file__).resolve().parent / "eod_trading_report.sh").read_text(encoding="utf-8")
checks = {
    "helper calls report_delivery_gate": 'report_delivery_gate.py" "${gate_args[@]}"' in src,
    "artifact name is cadence-discoverable": '_daily_report_${PLAN_DATE}.md' in src,
    "all three early branches call helper": src.count('_deliver_eod "$MSG" not_applicable') == 3,
    "early alerts skip only inapplicable return validation": 'gate_args+=(--skip-validation)' in src,
    "normal branch calls helper": '_deliver_eod "$FULL_REPORT"' in src,
    "normal branch returns delivery rc after risk audit": 'exit "$DELIVERY_RC"' in src,
    "legacy direct report delivery removed": 'DELIVERED_VIA="trading_report_thread"' not in src,
    "failure is durable and retryable": 'eod-trading-report-delivery-incomplete' in src
                                    and 'check_report_cadence' in src,
}
failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")
if failed:
    raise SystemExit(f"eod_delivery_wiring_selfcheck: FAIL {failed}")
print(f"eod_delivery_wiring_selfcheck: {len(checks)}/{len(checks)} PASS")
