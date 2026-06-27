#!/usr/bin/env python3
"""
Spyros Risk Monitor — giám sát ngưỡng rủi ro cho fleet Mike.

Đọc data/eod_account_<date>.json + plan đã duyệt, kiểm tra:
  1. Drawdown từ đỉnh NAV >= 25%
  2. Tập trung 1 mã > 20% NAV
  3. Đòn bẩy / margin vượt hạn
  4. Lệch fill vs plan quá tolerance (5%)
  5. [MỚI] Episode-drawdown breaker: NAV drop >= -15% từ lever-entry → BOT_STOP

Episode-drawdown breaker spec (Spyros 2026-06-27, mge20-tail-review, MGE=1.5 approved):
  - Episode = khi recovery/CAPIT arm deploy lần đầu (gross > 1.0x HOẶC plan có sleeve recovery)
  - Threshold: -15% từ episode-entry NAV (cập nhật từ -12% cho MGE=1.3 → -15% cho MGE=1.5)
  - State lưu tại: data/recovery_episode_state.json
  - S4 trong 6 tháng đầu go-live (2026-07-01 → 2026-12-31): tự động flag halt-review

Nếu vi phạm: ghi bus + hạ kill-switch BOT_STOP + Telegram alert.

Usage:
  python risk_monitor.py [--date YYYY-MM-DD] [--dry-run]
  python risk_monitor.py --open-episode NAV DATE   # thủ công mở episode (lever fire)
  python risk_monitor.py --close-episode           # đóng episode sau khi recovery kết thúc
  python risk_monitor.py --test-killswitch
  python risk_monitor.py --test-episode-breaker    # test S4 logic (paper)
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
NOTIFY_SH = WORKDIR / "mike/bin/notify.sh"
EPISODE_STATE_FILE = DATA_DIR / "recovery_episode_state.json"
TELEGRAM_CONFIG = WORKDIR / "telegram_config.json"

# Ngưỡng rủi ro
DD_THRESHOLD = 0.25       # Drawdown từ đỉnh >= 25% → halt
CONC_THRESHOLD = 0.20     # 1 mã > 20% NAV → cảnh báo
MARGIN_WARN = 1.0         # Gross exposure > 100% → soft warning
MARGIN_HARD = 1.50        # Gross exposure > 150% → HALT (ceiling MGE=1.5, Spyros 2026-06-27)
FILL_TOLERANCE = 0.05     # Lệch fill vs plan > 5% weight → flag

# Episode-drawdown breaker (S4) — trading_rules C_episode_drawdown_breaker
EPISODE_DD_THRESHOLD = -0.15   # -15% từ lever-entry (MGE=1.5, updated từ -12% cho 1.3x)
GOLIVE_DATE = date(2026, 7, 1)
FIRST_6M_END = date(2026, 12, 31)  # 6 tháng sau go-live → auto halt-review flag

# Nhận dạng recovery/lever sleeve trong plan
RECOVERY_SLEEVES = {"recovery_park", "capit", "capitulation", "deep_cheap", "recovery",
                    "lever", "capit_arm", "recovery_arm"}


# ---------------------------------------------------------------------------
# Episode state helpers
# ---------------------------------------------------------------------------

def load_episode_state() -> dict:
    """Tải trạng thái episode recovery hiện tại. Trả về dict rỗng nếu chưa có."""
    if not EPISODE_STATE_FILE.exists():
        return {"episode_active": False}
    try:
        return json.loads(EPISODE_STATE_FILE.read_text())
    except Exception:
        return {"episode_active": False}


def save_episode_state(state: dict, dry_run: bool = False):
    """Lưu trạng thái episode. Thêm timestamp cập nhật."""
    state["_updated"] = datetime.utcnow().isoformat() + "Z"
    if dry_run:
        print(f"[DRY-RUN] Episode state: {json.dumps(state, ensure_ascii=False)[:200]}")
        return
    EPISODE_STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def open_episode(nav: float, entry_date: str, source: str = "auto",
                 dry_run: bool = False):
    """Mở một episode mới (lever fire). Chỉ ghi nếu chưa có episode active."""
    state = load_episode_state()
    if state.get("episode_active"):
        print(f"INFO: Episode đã active từ {state.get('episode_entry_date')} — không ghi đè.")
        return state
    state = {
        "episode_active": True,
        "episode_entry_date": entry_date,
        "episode_entry_nav": nav,
        "lever_fire_date": entry_date,
        "lever_fire_nav": nav,
        "source": source,
        "s4_events": state.get("s4_events", []),
    }
    print(f"[EPISODE OPEN] entry_date={entry_date}, entry_nav={nav/1e9:.3f}B, source={source}")
    save_episode_state(state, dry_run)
    return state


def close_episode(reason: str = "manual", dry_run: bool = False):
    """Đóng episode (recovery kết thúc / manual close)."""
    state = load_episode_state()
    if not state.get("episode_active"):
        print("INFO: Không có episode active — close là no-op.")
        return
    state["episode_active"] = False
    state["episode_closed_at"] = datetime.utcnow().isoformat() + "Z"
    state["episode_close_reason"] = reason
    print(f"[EPISODE CLOSE] reason={reason}")
    save_episode_state(state, dry_run)


def detect_lever_fire(plan: dict | None, positions: list[dict], nav: float,
                      market_state: str = "") -> bool:
    """
    Phát hiện lever fire (episode cần mở) từ plan và EOD.

    True khi:
    - Plan có sleeve nằm trong RECOVERY_SLEEVES, HOẶC
    - Plan có kill_switches_armed.C_episode_drawdown_breaker != N/A (active episode), HOẶC
    - Gross exposure > 1.0x VÀ market_state là CRISIS hoặc BEAR
    """
    if plan:
        # Check sleeve names trong target_positions hoặc orders
        for pos in plan.get("target_positions", plan.get("orders", plan.get("positions", []))):
            sleeve = (pos.get("sleeve") or "").lower().replace(" ", "_")
            if any(s in sleeve for s in RECOVERY_SLEEVES):
                return True
        # Check kill_switches_armed
        ks = plan.get("market_context", {}).get("kill_switches_armed", {})
        c_switch = ks.get("C_episode_drawdown_breaker", "N/A")
        if c_switch not in ("N/A", "N/A_no_recovery_episode", False, None):
            return True

    # Gross exposure > 1.0x trong CRISIS/BEAR → lever arm đang chạy
    if nav > 0 and market_state.upper() in ("CRISIS", "BEAR"):
        total_long = sum(
            float(p.get("market_value") or p.get("value") or 0)
            for p in positions
            if float(p.get("market_value") or p.get("value") or 0) > 0
        )
        gross = total_long / nav
        if gross > 1.0:
            return True

    return False


def check_episode_drawdown(episode_state: dict, current_nav: float) -> dict:
    """
    Kiểm tra episode-drawdown (S4).
    Trả về dict với breach=True nếu NAV drop >= EPISODE_DD_THRESHOLD từ entry.
    """
    if not episode_state.get("episode_active"):
        return {"active": False, "breach": False}

    entry_nav = float(episode_state.get("episode_entry_nav", 0))
    if entry_nav <= 0:
        return {"active": True, "breach": False, "error": "entry_nav missing"}

    dd = (current_nav - entry_nav) / entry_nav
    breach = dd <= EPISODE_DD_THRESHOLD
    return {
        "active": True,
        "episode_entry_date": episode_state.get("episode_entry_date"),
        "episode_entry_nav": entry_nav,
        "current_nav": current_nav,
        "episode_dd": dd,
        "threshold": EPISODE_DD_THRESHOLD,
        "breach": breach,
    }


def is_first_6m_golive() -> bool:
    """True nếu hôm nay nằm trong 6 tháng đầu sau go-live."""
    today = date.today()
    return GOLIVE_DATE <= today <= FIRST_6M_END


# ---------------------------------------------------------------------------
# Alert helpers
# ---------------------------------------------------------------------------

def send_telegram_alert(message: str):
    """Gửi Telegram alert. Fail silent (không crash monitor)."""
    if not TELEGRAM_CONFIG.exists():
        return
    try:
        import requests
        cfg = json.loads(TELEGRAM_CONFIG.read_text())
        bot_token = cfg.get("bot_token", "")
        chat_id = cfg.get("chat_id", "")
        if not bot_token or not chat_id or "1234567890" in bot_token:
            return
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(url, data={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }, timeout=15)
    except Exception:
        pass


def send_alert(message: str, dry_run: bool = False):
    """Gửi alert qua Telegram (nếu có config) + Discord notify.sh fallback."""
    if dry_run:
        print(f"[DRY-RUN] ALERT: {message}")
        return
    send_telegram_alert(message)
    # Discord fallback qua notify.sh
    if NOTIFY_SH.exists():
        try:
            subprocess.run([str(NOTIFY_SH), message], timeout=15,
                           capture_output=True)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Core data loaders
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Risk checks
# ---------------------------------------------------------------------------

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
    """Kiểm tra đòn bẩy / gross exposure.
    MARGIN_WARN (1.0): soft warning — CAPIT arm 1.0→1.5x là OK.
    MARGIN_HARD (1.50): vi phạm ceiling MGE=1.5 → HALT.
    """
    total_long = sum(
        float(pos.get("market_value") or pos.get("value") or 0)
        for pos in positions
        if float(pos.get("market_value") or pos.get("value") or 0) > 0
    )
    gross_exposure = total_long / nav if nav > 0 else 0
    soft_warn = gross_exposure > MARGIN_WARN
    hard_breach = gross_exposure > MARGIN_HARD
    return {
        "gross_exposure": gross_exposure,
        "total_long": total_long,
        "soft_warn": soft_warn,
        "breach": hard_breach,
    }


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


# ---------------------------------------------------------------------------
# Kill-switch
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Main monitor
# ---------------------------------------------------------------------------

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
                "margin_soft_warn": f"gross>{MARGIN_WARN*100:.0f}%",
                "margin_hard_halt": f"gross>{MARGIN_HARD*100:.0f}%",
                "fill_tol": f">{FILL_TOLERANCE*100:.0f}%",
                "episode_dd_halt": f">={abs(EPISODE_DD_THRESHOLD)*100:.0f}% từ lever-entry",
            }
        }, dry_run)
        return 0

    nav = float(snap.get("nav_total") or snap.get("NAV") or snap.get("nav") or 0)
    cash = float(snap.get("cash") or 0)
    positions = snap.get("positions", [])
    today_str = target_date or date.today().isoformat()
    market_state = snap.get("market_state", "")

    if nav <= 0:
        print("WARN: NAV = 0 trong snapshot — dữ liệu có vấn đề")
        return 0

    nav_history = load_nav_history()
    plan = load_plan(target_date)
    breaches = []

    # ------------------------------------------------------------------
    # 1. Drawdown từ đỉnh
    # ------------------------------------------------------------------
    dd_result = check_drawdown(nav_history[:-1], nav)
    print(f"Drawdown: {dd_result['drawdown']*100:.1f}% (peak={dd_result['peak']/1e9:.2f}B, nav={nav/1e9:.2f}B)")
    if dd_result["breach"]:
        breaches.append(f"DRAWDOWN {dd_result['drawdown']*100:.1f}% >= {DD_THRESHOLD*100:.0f}%")
        halt_bot(f"Drawdown {dd_result['drawdown']*100:.1f}%", dry_run)
        append_bus("error", "risk-breach-drawdown", dd_result, dry_run)

    # ------------------------------------------------------------------
    # 2. Tập trung
    # ------------------------------------------------------------------
    conc_violations = check_concentration(positions, nav)
    if conc_violations:
        for v in conc_violations:
            print(f"WARN: Tập trung {v['ticker']} = {v['weight']*100:.1f}% NAV")
        append_bus("finding", "risk-concentration", {"violations": conc_violations}, dry_run)

    # ------------------------------------------------------------------
    # 3. Đòn bẩy
    # ------------------------------------------------------------------
    margin_result = check_margin(positions, nav, cash)
    print(f"Gross exposure: {margin_result['gross_exposure']*100:.1f}%")
    if margin_result["breach"]:
        breaches.append(f"MARGIN gross={margin_result['gross_exposure']*100:.1f}% > {MARGIN_HARD*100:.0f}%")
        halt_bot(f"Gross exposure {margin_result['gross_exposure']*100:.1f}% vượt hard ceiling MGE={MARGIN_HARD}x", dry_run)
        append_bus("error", "risk-breach-margin-hard", margin_result, dry_run)
    elif margin_result["soft_warn"]:
        print(f"INFO: Gross exposure {margin_result['gross_exposure']*100:.1f}% > {MARGIN_WARN*100:.0f}% (OK nếu CAPIT arm active, ceiling MGE={MARGIN_HARD}x)")
        append_bus("finding", "risk-margin-elevated", {
            **margin_result,
            "note": f"1.0-{MARGIN_HARD}x range: valid when CAPIT arm active (CRISIS/BEAR + pb_z<=-0.7 + money_cond)"
        }, dry_run)

    # ------------------------------------------------------------------
    # 4. Fill vs plan
    # ------------------------------------------------------------------
    if plan:
        fill_violations = check_fill_vs_plan(positions, plan, nav)
        if fill_violations:
            print(f"WARN: Fill lệch plan: {len(fill_violations)} mã")
            for v in fill_violations:
                print(f"  {v['ticker']}: plan={v['planned']*100:.1f}% actual={v['actual']*100:.1f}% diff={v['diff']*100:.1f}%")
            append_bus("finding", "risk-fill-deviation", {"violations": fill_violations}, dry_run)

    # ------------------------------------------------------------------
    # 5. Episode-drawdown breaker (S4) — NAV drop >= -15% từ lever-entry
    # ------------------------------------------------------------------
    episode_state = load_episode_state()

    # Auto-detect lever fire: nếu plan/EOD cho thấy recovery arm đang active
    if not episode_state.get("episode_active"):
        if detect_lever_fire(plan, positions, nav, market_state):
            print(f"[EPISODE] Lever fire detected — mở episode tại NAV={nav/1e9:.3f}B, date={today_str}")
            episode_state = open_episode(nav, today_str, source="auto_detect", dry_run=dry_run)
            append_bus("finding", "episode-lever-fire-detected", {
                "date": today_str,
                "nav": nav,
                "market_state": market_state,
                "source": "auto_detect",
            }, dry_run)

    # Kiểm tra S4 nếu episode đang active
    ep_result = check_episode_drawdown(episode_state, nav)
    if ep_result.get("active"):
        ep_dd_pct = ep_result.get("episode_dd", 0) * 100
        print(f"Episode DD: {ep_dd_pct:.1f}% (entry={ep_result['episode_entry_nav']/1e9:.3f}B "
              f"@{ep_result['episode_entry_date']}, threshold={EPISODE_DD_THRESHOLD*100:.0f}%)")

        if ep_result["breach"]:
            # S4 FIRED
            s4_event = {
                "date": today_str,
                "episode_dd": ep_result["episode_dd"],
                "nav": nav,
                "entry_nav": ep_result["episode_entry_nav"],
                "entry_date": ep_result["episode_entry_date"],
                "halt_review_required": is_first_6m_golive(),
            }

            # Cập nhật episode state với S4 event
            episode_state.setdefault("s4_events", []).append(s4_event)
            episode_state["episode_active"] = False
            episode_state["episode_closed_at"] = datetime.utcnow().isoformat() + "Z"
            episode_state["episode_close_reason"] = "S4_episode_drawdown_breaker"
            save_episode_state(episode_state, dry_run)

            msg = (
                f"🚨 S4 EPISODE-DRAWDOWN BREAKER FIRED\n"
                f"NAV drop {ep_dd_pct:.1f}% từ lever-entry "
                f"(entry={ep_result['episode_entry_nav']/1e9:.3f}B @{ep_result['episode_entry_date']})\n"
                f"NAV hiện tại: {nav/1e9:.3f}B\n"
                f"Threshold: {EPISODE_DD_THRESHOLD*100:.0f}% (MGE=1.5)\n"
                f"BOT_STOP đã set — chờ human review."
            )
            if is_first_6m_golive():
                msg += "\n⚠️ HALT-REVIEW FLAG: S4 trong 6 tháng đầu go-live — cần review trước khi mở lại."

            print(f"\n[S4 BREACH] {msg}")
            breaches.append(f"EPISODE_DD {ep_dd_pct:.1f}% <= {EPISODE_DD_THRESHOLD*100:.0f}% (S4)")
            halt_bot(f"S4 episode-drawdown breaker: {ep_dd_pct:.1f}% từ entry", dry_run)
            send_alert(msg, dry_run)
            append_bus("decision", "S4-episode-drawdown-halt", {
                **s4_event,
                "msg": msg[:400],
                "halt_reason": "cumulative_episode_DD_breached_-15pct_threshold",
                "mge": 1.5,
                "first_6m_golive": is_first_6m_golive(),
            }, dry_run)
    else:
        print("Episode: không active (không có recovery/lever arm)")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    if breaches:
        print(f"\n[BREACH] {len(breaches)} vi phạm cứng: {'; '.join(breaches)}")
        return 1
    else:
        print(f"\n[CLEAN] Tất cả ngưỡng OK (conc_warn={len(conc_violations)}, "
              f"episode={'active' if ep_result.get('active') else 'idle'})")
        append_bus("status", "risk-check-clean", {
            "nav": nav, "dd": dd_result["drawdown"],
            "gross_exp": margin_result["gross_exposure"],
            "conc_warns": len(conc_violations),
            "episode_active": ep_result.get("active", False),
            "episode_dd": ep_result.get("episode_dd"),
        }, dry_run)
        return 0


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

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


def test_episode_breaker():
    """Test S4 episode-drawdown breaker (paper — không ghi BOT_STOP thật)."""
    print("--- Test episode-drawdown breaker (S4) ---")
    # Simulate: entry NAV = 50B, current = 41.5B → DD = -17% → phải breach -15%
    fake_episode = {
        "episode_active": True,
        "episode_entry_date": "2026-07-15",
        "episode_entry_nav": 50_000_000_000,
        "lever_fire_date": "2026-07-15",
        "lever_fire_nav": 50_000_000_000,
    }
    current_nav = 41_500_000_000  # -17% → breach
    result = check_episode_drawdown(fake_episode, current_nav)
    assert result["breach"], f"Expected breach at -17% but got {result}"
    assert abs(result["episode_dd"] - (-0.17)) < 1e-4
    print(f"  S4 breach at -17%: OK")

    # Simulate: -10% → không breach
    current_nav_ok = 45_000_000_000  # -10%
    result_ok = check_episode_drawdown(fake_episode, current_nav_ok)
    assert not result_ok["breach"], f"Expected no breach at -10% but got {result_ok}"
    print(f"  No breach at -10%: OK")

    # Simulate: đúng ngưỡng -15% → breach
    current_nav_exact = 42_500_000_000  # exactly -15%
    result_exact = check_episode_drawdown(fake_episode, current_nav_exact)
    assert result_exact["breach"], f"Expected breach at exactly -15%"
    print(f"  Breach at exactly -15%: OK")

    # Test first-6m flag
    today = date.today()
    in_6m = GOLIVE_DATE <= today <= FIRST_6M_END
    print(f"  First-6m flag today ({today}): {in_6m} (go-live={GOLIVE_DATE}, end={FIRST_6M_END})")

    print("Episode-breaker test PASSED\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spyros Risk Monitor")
    parser.add_argument("--date", help="Target date YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true",
                        help="Không ghi bus, không halt thật")
    parser.add_argument("--test-killswitch", action="store_true",
                        help="Test kill-switch rồi exit")
    parser.add_argument("--test-episode-breaker", action="store_true",
                        help="Test S4 episode-drawdown logic rồi exit")
    parser.add_argument("--open-episode", metavar="NAV",
                        help="Thủ công mở episode với NAV (VND) này (kèm --date)")
    parser.add_argument("--close-episode", action="store_true",
                        help="Đóng episode recovery hiện tại")
    parser.add_argument("--show-episode", action="store_true",
                        help="Hiển thị trạng thái episode hiện tại")
    args = parser.parse_args()

    if args.test_killswitch:
        test_killswitch()
        sys.exit(0)

    if args.test_episode_breaker:
        test_episode_breaker()
        sys.exit(0)

    if args.show_episode:
        ep = load_episode_state()
        print(json.dumps(ep, indent=2, ensure_ascii=False))
        sys.exit(0)

    if args.open_episode:
        nav_val = float(args.open_episode)
        entry_date = args.date or date.today().isoformat()
        open_episode(nav_val, entry_date, source="manual", dry_run=args.dry_run)
        sys.exit(0)

    if args.close_episode:
        close_episode("manual", dry_run=args.dry_run)
        sys.exit(0)

    rc = run_monitor(target_date=args.date, dry_run=args.dry_run)
    sys.exit(rc)
