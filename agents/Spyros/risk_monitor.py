#!/usr/bin/env python3
"""
Spyros Risk Monitor — giám sát ngưỡng rủi ro cho fleet Mike.

Đọc data/eod_account_<date>.json + plan đã duyệt, kiểm tra:
  1. Drawdown từ đỉnh NAV >= 25%
  2. Tập trung 1 mã > 20% NAV
  3. Đòn bẩy / margin vượt hạn
  4. Lệch fill vs plan quá tolerance (5%)

Nếu vi phạm: ghi bus + hạ kill-switch BOT_STOP.

Usage:
  python risk_monitor.py [--date YYYY-MM-DD] [--dry-run]
"""

import json
import sys
import os
import glob
import argparse
import subprocess
from datetime import date, datetime
from pathlib import Path

WORKDIR = Path("/home/trido/thanhdt/WorkingClaude")
DATA_DIR = WORKDIR / "data"
BOT_STOP = DATA_DIR / "BOT_STOP"
APPEND_EVENT = WORKDIR / "mike/bin/append_event.sh"

# Ngưỡng rủi ro
DD_THRESHOLD = 0.25       # Drawdown từ đỉnh >= 25% → halt
CONC_THRESHOLD = 0.20     # 1 mã > 20% NAV → cảnh báo
MARGIN_LIMIT = 1.0        # Gross exposure > 100% → cảnh báo (không có margin thật)
FILL_TOLERANCE = 0.05     # Lệch fill vs plan > 5% weight → flag


def load_eod(target_date: str | None = None) -> dict | None:
    """Tải EOD snapshot gần nhất (hoặc theo ngày)."""
    if target_date:
        path = DATA_DIR / f"eod_account_{target_date}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())

    files = sorted(glob.glob(str(DATA_DIR / "eod_account_*.json")))
    if not files:
        return None
    return json.loads(Path(files[-1]).read_text())


def load_plan(target_date: str | None = None) -> dict | None:
    """Tải plan đã duyệt gần nhất."""
    if target_date:
        files = sorted(glob.glob(str(DATA_DIR / f"plan_*_{target_date}.json")))
    else:
        files = sorted(glob.glob(str(DATA_DIR / "plan_*.json")))
    if not files:
        return None
    return json.loads(Path(files[-1]).read_text())


def load_nav_history() -> list[float]:
    """Tải lịch sử NAV để tính đỉnh. Đọc tất cả EOD files."""
    nav_series = []
    for f in sorted(glob.glob(str(DATA_DIR / "eod_account_*.json"))):
        try:
            snap = json.loads(Path(f).read_text())
            nav = snap.get("nav_total") or snap.get("NAV") or snap.get("nav")
            if nav:
                nav_series.append(float(nav))
        except Exception:
            pass
    return nav_series


def check_drawdown(nav_history: list[float], current_nav: float) -> dict:
    """Tính drawdown từ đỉnh."""
    if not nav_history:
        peak = current_nav
    else:
        peak = max(max(nav_history), current_nav)

    dd = (current_nav - peak) / peak if peak > 0 else 0.0
    breach = dd <= -DD_THRESHOLD
    return {"peak": peak, "current": current_nav, "drawdown": dd, "breach": breach}


def check_concentration(positions: list[dict], nav: float) -> list[dict]:
    """Kiểm tra tập trung > 20% NAV."""
    violations = []
    for pos in positions:
        ticker = pos.get("ticker", "?")
        value = float(pos.get("market_value") or pos.get("value") or 0)
        weight = value / nav if nav > 0 else 0
        if weight > CONC_THRESHOLD:
            violations.append({"ticker": ticker, "weight": weight, "value": value})
    return violations


def check_margin(positions: list[dict], nav: float, cash: float) -> dict:
    """Kiểm tra đòn bẩy / gross exposure."""
    total_long = sum(
        float(pos.get("market_value") or pos.get("value") or 0)
        for pos in positions
        if float(pos.get("market_value") or pos.get("value") or 0) > 0
    )
    gross_exposure = total_long / nav if nav > 0 else 0
    breach = gross_exposure > MARGIN_LIMIT
    return {"gross_exposure": gross_exposure, "total_long": total_long, "breach": breach}


def check_fill_vs_plan(positions: list[dict], plan: dict, nav: float) -> list[dict]:
    """So sánh fill thực tế vs plan đã duyệt."""
    if not plan:
        return []

    planned = {p["ticker"]: p.get("target_weight", p.get("weight", 0))
               for p in plan.get("orders", plan.get("positions", []))}
    actual = {
        pos["ticker"]: float(pos.get("market_value") or pos.get("value") or 0) / nav
        for pos in positions
        if nav > 0
    }

    violations = []
    all_tickers = set(planned) | set(actual)
    for t in all_tickers:
        pw = planned.get(t, 0)
        aw = actual.get(t, 0)
        diff = abs(aw - pw)
        if diff > FILL_TOLERANCE:
            violations.append({"ticker": t, "planned": pw, "actual": aw, "diff": diff})
    return violations


def halt_bot(reason: str, dry_run: bool = False):
    """Hạ kill-switch."""
    if dry_run:
        print(f"[DRY-RUN] Would create BOT_STOP: {reason}")
        return
    BOT_STOP.write_text(f"{datetime.utcnow().isoformat()}Z — {reason}\n")
    print(f"[HALT] BOT_STOP created: {reason}")


def append_bus(level: str, topic: str, payload: dict, dry_run: bool = False):
    """Ghi sự kiện lên bus."""
    payload_str = json.dumps(payload, ensure_ascii=False)
    cmd = [str(APPEND_EVENT), "Spyros", level, topic, payload_str]
    if dry_run:
        print(f"[DRY-RUN] Bus: {level} | {topic} | {payload_str[:120]}")
        return
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except Exception as e:
        print(f"[WARN] append_event failed: {e}")


def run_monitor(target_date: str | None = None, dry_run: bool = False) -> int:
    """Chạy vòng kiểm tra rủi ro. Trả về exit code: 0=clean, 1=breach."""
    print(f"=== Spyros Risk Monitor {'[DRY-RUN] ' if dry_run else ''}=== {datetime.utcnow().isoformat()}Z")

    snap = load_eod(target_date)
    if snap is None:
        print("INFO: Không có EOD snapshot — chưa có dữ liệu live. Monitor sẵn sàng nhưng idle.")
        append_bus("status", "risk-monitor-idle", {
            "reason": "no eod snapshot found",
            "thresholds": {
                "dd_halt": f">={DD_THRESHOLD*100:.0f}%",
                "conc_warn": f">{CONC_THRESHOLD*100:.0f}% NAV",
                "margin": f"gross>{MARGIN_LIMIT*100:.0f}%",
                "fill_tol": f">{FILL_TOLERANCE*100:.0f}%"
            }
        }, dry_run)
        return 0

    nav = float(snap.get("nav_total") or snap.get("NAV") or snap.get("nav") or 0)
    cash = float(snap.get("cash") or 0)
    positions = snap.get("positions", [])

    if nav <= 0:
        print("WARN: NAV = 0 trong snapshot — dữ liệu có vấn đề")
        return 0

    nav_history = load_nav_history()
    plan = load_plan(target_date)
    breaches = []

    # 1. Drawdown
    dd_result = check_drawdown(nav_history[:-1], nav)  # exclude current from history peak
    print(f"Drawdown: {dd_result['drawdown']*100:.1f}% (peak={dd_result['peak']/1e9:.2f}B, nav={nav/1e9:.2f}B)")
    if dd_result["breach"]:
        breaches.append(f"DRAWDOWN {dd_result['drawdown']*100:.1f}% >= {DD_THRESHOLD*100:.0f}%")
        halt_bot(f"Drawdown {dd_result['drawdown']*100:.1f}%", dry_run)
        append_bus("error", "risk-breach-drawdown", dd_result, dry_run)

    # 2. Tập trung
    conc_violations = check_concentration(positions, nav)
    if conc_violations:
        for v in conc_violations:
            print(f"WARN: Tập trung {v['ticker']} = {v['weight']*100:.1f}% NAV")
        append_bus("finding", "risk-concentration", {"violations": conc_violations}, dry_run)

    # 3. Đòn bẩy
    margin_result = check_margin(positions, nav, cash)
    print(f"Gross exposure: {margin_result['gross_exposure']*100:.1f}%")
    if margin_result["breach"]:
        breaches.append(f"MARGIN gross={margin_result['gross_exposure']*100:.1f}%")
        append_bus("error", "risk-breach-margin", margin_result, dry_run)

    # 4. Fill vs plan
    if plan:
        fill_violations = check_fill_vs_plan(positions, plan, nav)
        if fill_violations:
            print(f"WARN: Fill lệch plan: {len(fill_violations)} mã")
            for v in fill_violations:
                print(f"  {v['ticker']}: plan={v['planned']*100:.1f}% actual={v['actual']*100:.1f}% diff={v['diff']*100:.1f}%")
            append_bus("finding", "risk-fill-deviation", {"violations": fill_violations}, dry_run)

    # Summary
    if breaches:
        print(f"\n[BREACH] {len(breaches)} vi phạm cứng: {'; '.join(breaches)}")
        return 1
    else:
        print(f"\n[CLEAN] Tất cả ngưỡng OK (conc_warn={len(conc_violations)})")
        append_bus("status", "risk-check-clean", {
            "nav": nav, "dd": dd_result["drawdown"],
            "gross_exp": margin_result["gross_exposure"],
            "conc_warns": len(conc_violations)
        }, dry_run)
        return 0


def test_killswitch():
    """Test kill-switch: tạo rồi xoá BOT_STOP."""
    print("--- Test kill-switch ---")
    BOT_STOP.write_text("TEST — auto-removed\n")
    assert BOT_STOP.exists(), "BOT_STOP không được tạo!"
    print(f"  Created: {BOT_STOP}")
    BOT_STOP.unlink()
    assert not BOT_STOP.exists(), "BOT_STOP vẫn còn sau khi xoá!"
    print(f"  Removed: OK")
    print("Kill-switch test PASSED\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spyros Risk Monitor")
    parser.add_argument("--date", help="Target date YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true", help="Không ghi bus, không halt thật")
    parser.add_argument("--test-killswitch", action="store_true", help="Test kill-switch rồi exit")
    args = parser.parse_args()

    if args.test_killswitch:
        test_killswitch()
        sys.exit(0)

    rc = run_monitor(target_date=args.date, dry_run=args.dry_run)
    sys.exit(rc)
