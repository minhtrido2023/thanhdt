#!/usr/bin/env python3
"""Focused regression checks for report_delivery_gate.py."""
import importlib.util
import json
from pathlib import Path
import tempfile

SRC = Path(__file__).with_name("report_delivery_gate.py")
spec = importlib.util.spec_from_file_location("rdg", SRC)
rdg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rdg)


def main():
    with tempfile.TemporaryDirectory() as td_s:
        td = Path(td_s)
        report = td / "weekly_report_2026-08-10_to_2026-08-14.md"
        report.write_text("# fixture\nNo position return table.\n", encoding="utf-8")
        state = td / "state.json"
        calls = []

        def fake(cmd):
            calls.append(Path(cmd[0]).name if cmd[0] != rdg.sys.executable else Path(cmd[1]).name)

        old = rdg.run_checked
        old_legacy = rdg.LEGACY_EMAIL_STATE
        rdg.run_checked = fake
        rdg.LEGACY_EMAIL_STATE = td / "legacy.json"
        try:
            assert rdg.status(report, state) == 1                         # artifact alone
            assert rdg.deliver(report, state, "trading_report", td/"notify", td/"email", True) == 0
            assert calls == ["notify", "email"]                         # both required
            assert rdg.status(report, state) == 0
            assert rdg.deliver(report, state, "trading_report", td/"notify", td/"email", True) == 0
            assert calls == ["notify", "email"]                         # no duplicate

            data = json.loads(state.read_text())
            rec = data["reports"][report.name]
            rec.pop("email")
            state.write_text(json.dumps(data))
            assert rdg.deliver(report, state, "trading_report", td/"notify", td/"email", True) == 0
            assert calls[-1] == "email" and calls.count("notify") == 1   # retry missing only

            data = json.loads(state.read_text())
            rec = data["reports"][report.name]
            rec.pop("discord")
            state.write_text(json.dumps(data))
            assert rdg.deliver(report, state, "trading_report", td/"notify", td/"email", True) == 0
            assert calls[-1] == "notify" and calls.count("email") == 2   # retry missing only

            state.write_text("{broken")
            assert rdg.status(report, state) == 1                        # malformed fails closed
        finally:
            rdg.run_checked = old
            rdg.LEGACY_EMAIL_STATE = old_legacy
    print("report_delivery_gate_selfcheck: PASS (7/7)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
