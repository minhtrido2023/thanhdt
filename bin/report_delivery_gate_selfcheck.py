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

        n = _check_period_returns_selfcheck(rdg, td)

    print(f"report_delivery_gate_selfcheck: PASS (7/7 delivery + {n}/{n} period-return)")
    return 0


def _check_period_returns_selfcheck(rdg, td: Path) -> int:
    """D3 (job Taylor_20260919_033902): _check_period_returns coverage against a real
    SpaceX inception canonical (nav_period_returns.py reads live data/nav_history — no BQ)."""
    n = 0

    zp = td / "ZaloPay_weekly_report_2026-09-14_to_2026-09-18.md"
    zp.write_text("| Từ khi bắt đầu hoạt động (01/07 → 18/09) | −99,99% | −2,76% | +1,10pp |\n",
                   encoding="utf-8")
    rdg._check_period_returns(zp)                                        # ZaloPay: no-op, no raise
    n += 1

    no_table = td / "SpaceX_weekly_report_2026-09-14_to_2026-09-18.md"
    no_table.write_text("# fixture\nKhông có bảng hiệu suất.\n", encoding="utf-8")
    rdg._check_period_returns(no_table)                                  # thiếu bảng: WARN, no raise
    n += 1

    bad_name = td / "SpaceX_special_report.md"
    bad_name.write_text("| Từ khi bắt đầu hoạt động (x) | −1,66% | −2,76% | +1,10pp |\n",
                         encoding="utf-8")
    rdg._check_period_returns(bad_name)                                  # không suy được date: WARN
    n += 1

    real_canonical = json.loads(
        rdg.subprocess.run(
            [rdg.sys.executable, str(rdg.ROOT / "bin" / "nav_period_returns.py"),
             "--account", "SpaceX", "--report-date", "2026-09-18"],
            check=True, capture_output=True, text=True).stdout
    )["inception"]["return_pct"]

    matching = td / "SpaceX_weekly_report_2026-09-11_to_2026-09-18.md"
    matching.write_text(
        f"| Từ khi bắt đầu hoạt động (01/07 → 18/09) | {real_canonical:+.2f}% | −2,76% | +1,10pp |\n",
        encoding="utf-8")
    rdg._check_period_returns(matching)                                  # trong tolerance: PASS, no raise
    n += 1

    wrong = td / "SpaceX_weekly_report_2026-09-14_to_2026-09-18b.md"
    wrong.write_text("| Từ khi bắt đầu hoạt động (01/07 → 18/09) | −1,66% | −2,76% | +1,10pp |\n",
                      encoding="utf-8")
    try:
        rdg._check_period_returns(wrong)
        raise AssertionError("period-return check phải BLOCK khi lệch canonical thật")
    except RuntimeError as exc:
        assert "period-return BLOCK" in str(exc)
    n += 1

    return n


if __name__ == "__main__":
    raise SystemExit(main())
