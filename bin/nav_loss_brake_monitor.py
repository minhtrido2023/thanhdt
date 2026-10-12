#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monitor PHANH LỖ CẤP NAV — CHỈ CẢNH BÁO (user duyệt 2026-10-12, job Taylor_20261012_111422).

Đo ba phanh trên GIÁ ĐƠN VỊ QUỸ chốt-so-chốt của từng account, mỗi tối sau khi NAV đã chốt:
  · lỗ một ngày   <= `risk_circuit_breakers.daily_loss_limit_pct` (data/trading_rules.json)
  · lỗ từ đỉnh    >= DD_THRESHOLD (hằng số dưới đây — KHÔNG có khoá trong trading_rules.json)
  · lỗ từ điểm vào một episode đòn bẩy <= ngưỡng trong
    `macro_kill_switches.C_episode_drawdown_breaker.trigger` (data/trading_rules.json)

MONITOR NÀY KHÔNG BAO GIỜ tạo `data/BOT_STOP`, không huỷ lệnh, không gọi broker, không gọi BQ.
Chạm ngưỡng ⇒ gửi cảnh báo (in sẵn lệnh để NGƯỜI tự tạo BOT_STOP) và chờ người quyết.

TỈ SUẤT: một công thức duy nhất — `nav_unit_ledger.build_ledger` (chính sách
`kb/projects/fund-unit-performance-policy-20261010.md`). File này chỉ lấy TỈ SỐ hai giá đơn vị.

CƠ SỞ ĐO ("basis"):
  · account KHÔNG khai `excluded_tickers` ⇒ "total": chuỗi NAV tổng (nav_history).
  · account CÓ khai `excluded_tickers` (secrets/trading_bot_accounts.json) ⇒ "managed": phần BOT
    QUẢN LÝ = nav − giá trị các mã loại trừ. NAV tổng chỉ hiển thị kèm, không kích phanh.
    nav_history không giữ giá/KL từng mã, nên giá trị mã loại trừ được GHI DẦN mỗi ngày vào
    `data/loss_brake/excluded_value_history_{account}.csv` (chỉ-ghi-thêm): KL lấy từ bản ghi
    positions cuối ngày trong `dnse_raw_{date}.jsonl` (lọc account, §12); giá lấy từ
    `active_nav_{account}.json` của CHÍNH ngày đó (cron 20:15). Không mã loại trừ nào đang giữ ⇒
    giá trị 0, không cần giá (ngày thiếu kiểu này tự vá ở lượt chạy sau).
    Tiền chạy GIỮA hai phần (cổ tức tiền của mã loại trừ, bán/mua mã loại trừ) là DÒNG TIỀN của
    phần quản lý: khai trong `data/loss_brake/managed_sleeve_flows.json` (cùng schema
    account_cash_flows.json). Ba bẫy báo thiếu khai: KL mã loại trừ đổi · giá mã loại trừ nhảy
    quá biên độ sàn · lịch corp-action có sự kiện đúng ngày. Dính bẫy mà chưa khai ⇒ KHÔNG ĐO ĐƯỢC.

FAIL-LOUD: thiếu dòng NAV phiên phải có, dòng `nav_is_estimate`, thiếu phiên liền trước, sổ dòng
tiền lỗi, thiếu khoá ngưỡng ⇒ trạng thái "KHÔNG ĐO ĐƯỢC" kèm lý do ĐỌC TỪ DỮ LIỆU (§29) và CÓ gửi
cảnh báo. Không có nhánh nào coi "không đọc được" là "an toàn".

EPISODE: mở khi có ĐỦ hai bằng chứng cùng ngày — bản duyệt `data/margin_approvals/
margin_approval_{account}_{date}.json` (chưa thu hồi) VÀ vị thế mở dưới gói vay
`capit_margin_lever.loan_package_id` trong bản ghi positions của broker ngày đó. Bản duyệt mà
không có vị thế = mới là ý định (§27), không mở. Đóng bằng tay: `--close-episode`.

Dùng:
    python3 mike/bin/nav_loss_brake_monitor.py                      # chạy thật (cron tối)
    python3 mike/bin/nav_loss_brake_monitor.py --date 2026-10-09
    python3 mike/bin/nav_loss_brake_monitor.py --replay             # chạy thử toàn lịch sử, không ghi/gửi
    python3 mike/bin/nav_loss_brake_monitor.py --health-line --account SpaceX   # ops_health_check
    python3 mike/bin/nav_loss_brake_monitor.py --close-episode SpaceX --closed-by "user ..." --reason "..."
Selfcheck: python3 mike/bin/nav_loss_brake_monitor_selfcheck.py
"""
import argparse
import csv
import datetime
import glob
import json
import os
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BIN)

from account_cash_flows import NavRow, load_flows  # noqa: E402
from nav_unit_ledger import (_inception_baseline, build_ledger, load_inception,  # noqa: E402
                             load_nav_history)
from wc_paths import find_wc_root  # noqa: E402

WC_ROOT = find_wc_root(__file__)
sys.path.insert(0, WC_ROOT)

from trading_bot.vn_market import is_holiday  # noqa: E402

ICT = ZoneInfo("Asia/Ho_Chi_Minh")

# Ngưỡng lỗ từ đỉnh. Nguồn: `agents/Spyros/risk_monitor.py:46` (DD_THRESHOLD = 0.25) — con số
# này KHÔNG có khoá trong data/trading_rules.json nên giữ ở đây dưới dạng hằng số có tên.
DD_THRESHOLD = 0.25
# Sau giờ này của một ngày giao dịch thì NAV chốt của CHÍNH ngày đó phải đã có: lượt
# `nav_sync_retry.sh` cuối cùng chạy 21:45 ICT (kb/cron_registry.md).
NAV_EXPECTED_AFTER_ICT = datetime.time(21, 50)
# Biên độ giá/ngày rộng nhất của sàn có mã loại trừ (HOSE ±7%) + 0,5pp làm tròn bước giá. Giá
# đóng cửa nhảy quá mức này không thể do khớp lệnh thường ⇒ có sự kiện quyền.
EXCL_PRICE_BAND = 0.075
# active_nav_{account}.json (cron 20:15) và dòng nav_history cùng ngày phải định giá CÙNG một
# danh mục: `total_nav` của file kia được lệch NAV tối đa chừng này. Lệch hơn = hai file dùng giá
# khác nhau cho ít nhất một mã (ca DGC 11/09: broker 38.750 vs giá đóng cửa 46.750 = 8% NAV) ⇒
# lấy giá mã loại trừ từ file kia rồi trừ khỏi NAV này sẽ ra lãi/lỗ GIẢ ở phần quản lý.
# 0,1% là GIẢ ĐỊNH: mới có 1 cặp cùng ngày để đo (ZaloPay 2026-10-09, lệch đúng 0đ).
NAV_MATCH_TOL = 0.001
# Sai số dấu phẩy động khi so đúng biên (−5,00% phải kêu). 1e-9 = 0,0000001pp.
EPS = 1e-9

OK, BREACH, UNMEASURABLE, NO_EPISODE = "OK", "BREACH", "UNMEASURABLE", "NO_EPISODE"
BRAKES = ("daily", "drawdown", "episode")
BRAKE_VI = {"daily": "Lỗ một ngày", "drawdown": "Lỗ từ đỉnh", "episode": "Lỗ từ điểm vào episode"}
EXCL_FIELDS = ["date", "excluded_value", "detail", "source", "positions_ts", "recorded_at"]
SINK_ENV = "MIKE_LOSS_BRAKE_ALERT_SINK"
NOTIFY_CHANNEL = "trading_daily"
STATUS_SCHEMA = 1


class ConfigError(ValueError):
    pass


class Ctx:
    """Mọi đường dẫn ở một chỗ. `data_root`/`state_dir`/`secrets_path` đổi được để selfcheck và
    chạy thử không chạm dữ liệu thật; `is_live` = cả ba đang trỏ đúng mặc định."""

    def __init__(self, data_root=None, state_dir=None, secrets_path=None, now=None):
        d_data = os.path.join(WC_ROOT, "data")
        d_secrets = os.path.join(WC_ROOT, "secrets", "trading_bot_accounts.json")
        self.data_root = data_root or d_data
        self.state_dir = state_dir or os.path.join(self.data_root, "loss_brake")
        self.secrets_path = secrets_path or d_secrets
        self.is_live = (os.path.realpath(self.data_root) == os.path.realpath(d_data)
                        and os.path.realpath(self.state_dir)
                        == os.path.realpath(os.path.join(d_data, "loss_brake"))
                        and os.path.realpath(self.secrets_path) == os.path.realpath(d_secrets))
        self.exec_dir = os.path.join(self.data_root, "execution_logs")
        self.rules_path = os.path.join(self.data_root, "trading_rules.json")
        self.inception_path = os.path.join(self.data_root, "account_inception.json")
        self.flows_path = os.path.join(self.data_root, "account_cash_flows.json")
        self.approvals_dir = os.path.join(self.data_root, "margin_approvals")
        self.corp_dir = os.path.join(self.data_root, "corp_action_daily")
        self.sleeve_flows_path = os.path.join(self.state_dir, "managed_sleeve_flows.json")
        self.episodes_path = os.path.join(self.state_dir, "episodes.json")
        self.status_path = os.path.join(self.state_dir, "status.json")
        self.sent_path = os.path.join(self.state_dir, "alerts_sent.json")
        self.now = now or datetime.datetime.now(ICT)

    def excl_path(self, account):
        return os.path.join(self.state_dir, f"excluded_value_history_{account}.csv")


# ------------------------------------------------------------------ lịch phiên (§16: neo ICT)
def is_session(d):
    return d.weekday() < 5 and not is_holiday(d)


def prev_session(d):
    d -= datetime.timedelta(days=1)
    while not is_session(d):
        d -= datetime.timedelta(days=1)
    return d


def expected_session(now):
    """Phiên gần nhất mà NAV chốt PHẢI đã có tại thời điểm `now` (datetime ICT)."""
    d = now.astimezone(ICT).date() if now.tzinfo else now.date()
    t = now.astimezone(ICT).time() if now.tzinfo else now.time()
    if is_session(d) and t >= NAV_EXPECTED_AFTER_ICT:
        return d
    return prev_session(d)


# ------------------------------------------------------------------ tiện ích file
def _write_atomic(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _write_json_atomic(path, obj):
    _write_atomic(path, json.dumps(obj, ensure_ascii=False, indent=2, default=str) + "\n")


def _read_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def vnd(x):
    return f"{x:,.0f}".replace(",", ".")


def pct(x, digits=2):
    return "n/a" if x is None else f"{x * 100:+.{digits}f}%".replace(".", ",")


# ------------------------------------------------------------------ ngưỡng (nguồn sự thật)
def load_thresholds(rules_path):
    """Trả `(th, errors)`. `errors[brake]` = lý do KHÔNG đọc được ngưỡng của phanh đó — phanh ấy
    thành KHÔNG ĐO ĐƯỢC, không có mặc định ngầm."""
    th = {"drawdown": -DD_THRESHOLD, "daily": None, "episode": None, "lever_package_id": None}
    errors = {}
    try:
        with open(rules_path, encoding="utf-8") as f:
            rules = json.load(f)
    except (OSError, ValueError) as exc:
        why = f"không đọc được {rules_path}: {exc}"
        return th, {"daily": why, "episode": why}
    v = (rules.get("risk_circuit_breakers") or {}).get("daily_loss_limit_pct")
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not -1 < v < 0:
        errors["daily"] = (f"{rules_path}: risk_circuit_breakers.daily_loss_limit_pct phải là số "
                           f"trong (−1, 0), đọc được {v!r}")
    else:
        th["daily"] = float(v)
    trig = ((rules.get("macro_kill_switches") or {}).get("C_episode_drawdown_breaker")
            or {}).get("trigger")
    found = sorted(set(re.findall(r"-0\.\d+", trig))) if isinstance(trig, str) else []
    if len(found) != 1:
        errors["episode"] = (f"{rules_path}: macro_kill_switches.C_episode_drawdown_breaker.trigger "
                             f"phải chứa ĐÚNG MỘT ngưỡng dạng -0.xx, đọc được {trig!r}")
    else:
        th["episode"] = float(found[0])
    pkg = (rules.get("capit_margin_lever") or {}).get("loan_package_id")
    if isinstance(pkg, bool) or not isinstance(pkg, int):
        errors.setdefault("episode", f"{rules_path}: capit_margin_lever.loan_package_id phải là "
                                     f"số nguyên, đọc được {pkg!r}")
    else:
        th["lever_package_id"] = pkg
    return th, errors


def load_profiles(secrets_path):
    """{label: {"account_id", "excluded_tickers"}} từ secrets/trading_bot_accounts.json."""
    with open(secrets_path, encoding="utf-8") as f:
        cfg = json.load(f)
    return {rec["label"]: {"account_id": rec.get("account_id"),
                           "excluded_tickers": sorted(rec.get("excluded_tickers") or [])}
            for rec in cfg.get("accounts", []) if rec.get("label")}


# ------------------------------------------------------------------ broker raw (chỉ ĐỌC file)
def raw_positions(exec_dir, account_no, date):
    """(list vị thế mở | None, ts, lý do) từ bản ghi positions CUỐI CÙNG của `account_no` trong
    dnse_raw_{date}.jsonl. §12: lọc account là việc ĐẦU TIÊN với mỗi bản ghi."""
    path = os.path.join(exec_dir, f"dnse_raw_{date}.jsonl")
    if not os.path.exists(path):
        return None, None, f"không có file {os.path.basename(path)}"
    latest, ts = None, None
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if str(rec.get("account_no")) != str(account_no):
                continue
            if rec.get("kind") != "positions":
                continue
            latest, ts = (rec.get("payload") or {}).get("positions") or [], rec.get("ts")
    if latest is None:
        return None, None, (f"{os.path.basename(path)} không có bản ghi positions nào của account "
                            f"{account_no}")
    return [p for p in latest if float(p.get("openQuantity") or 0) > 0], ts, None


def _qty_by_symbol(positions, keep=None):
    out = {}
    for p in positions:
        if keep is None or keep(p):
            out[p.get("symbol")] = out.get(p.get("symbol"), 0.0) + float(p["openQuantity"])
    return out


# ------------------------------------------------------------------ chuỗi giá trị mã loại trừ
def read_excluded_history(path):
    """{date: {"value", "detail": {ticker: {"qty", "price"}}}}. File thiếu ⇒ {}."""
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8", newline="") as f:
        for rec in csv.DictReader(f):
            d = datetime.date.fromisoformat(rec["date"])
            out[d] = {"value": float(rec["excluded_value"]),
                      "detail": json.loads(rec["detail"] or "{}"), "source": rec["source"]}
    return out


def _append_excluded(path, rows):
    """Chỉ-ghi-thêm: dòng đã có KHÔNG bị ghi đè. Ghi nguyên tử cả file."""
    old = []
    if os.path.exists(path):
        with open(path, encoding="utf-8", newline="") as f:
            old = list(csv.DictReader(f))
    have = {r["date"] for r in old}
    merged = sorted(old + [r for r in rows if r["date"] not in have], key=lambda r: r["date"])
    lines = [",".join(EXCL_FIELDS)]
    for r in merged:
        lines.append(",".join('"' + str(r[k]).replace('"', '""') + '"' if k == "detail"
                              else str(r[k]) for k in EXCL_FIELDS))
    _write_atomic(path, "\n".join(lines) + "\n")


def excluded_value_for(ctx, account, account_no, excluded, date, nav):
    """Dòng giá trị mã loại trừ của `date`, hoặc `(None, lý do)` khi dữ liệu không cho phép.
    KL: broker raw. Giá (chỉ cần khi có giữ): active_nav của CHÍNH ngày đó."""
    positions, ts, why = raw_positions(ctx.exec_dir, account_no, date)
    if positions is None:
        return None, why
    held = _qty_by_symbol(positions, keep=lambda p: p.get("symbol") in excluded)
    row = {"date": date.isoformat(), "excluded_value": "0", "detail": "{}", "positions_ts": ts,
           "source": "dnse_raw positions: không giữ mã loại trừ nào",
           "recorded_at": ctx.now.isoformat(timespec="seconds")}
    if not held:
        return row, None
    path = os.path.join(ctx.exec_dir, f"active_nav_{account}.json")
    try:
        an = _read_json(path, None)
    except ValueError as exc:
        return None, f"{path} không đọc được: {exc}"
    if an is None:
        return None, f"đang giữ {sorted(held)} nhưng không có {path} để lấy giá đóng cửa"
    if an.get("account") != account or an.get("computed_at") != date.isoformat():
        return None, (f"đang giữ {sorted(held)} nhưng {os.path.basename(path)} là của account="
                      f"{an.get('account')!r} computed_at={an.get('computed_at')!r}, không phải "
                      f"{account} ngày {date} ⇒ không có giá đóng cửa đúng ngày")
    try:
        gap = float(an.get("total_nav")) / nav - 1
    except (TypeError, ValueError):
        return None, f"{os.path.basename(path)} không có total_nav để đối chiếu với nav_history"
    if abs(gap) > NAV_MATCH_TOL:
        return None, (f"{os.path.basename(path)} total_nav {vnd(float(an['total_nav']))} lệch "
                      f"{pct(gap)} so với nav_history {date} ({vnd(nav)}) — quá "
                      f"{pct(NAV_MATCH_TOL, 1)} ⇒ hai file định giá khác nhau, không dùng giá mã "
                      f"loại trừ của file này để trừ khỏi NAV kia")
    detail, total = {}, 0.0
    by_t = {p.get("ticker"): p for p in an.get("positions") or []}
    for t, qty in sorted(held.items()):
        p = by_t.get(t)
        if not p or not float(p.get("price") or 0) > 0:
            return None, f"{os.path.basename(path)} không có giá của mã loại trừ {t}"
        if abs(float(p.get("qty") or 0) - qty) > 1e-6:
            return None, (f"KL {t} lệch giữa hai nguồn cùng ngày {date}: dnse_raw {vnd(qty)} vs "
                          f"{os.path.basename(path)} {vnd(float(p.get('qty') or 0))}")
        detail[t] = {"qty": qty, "price": float(p["price"])}
        total += qty * float(p["price"])
    row.update(excluded_value=f"{total:.0f}", detail=json.dumps(detail, sort_keys=True),
               source=f"dnse_raw positions × {os.path.basename(path)} ({p.get('price_source')})")
    return row, None


def record_excluded(ctx, account, account_no, excluded, navs):
    """Ghi các ngày nav_history còn thiếu trong chuỗi giá trị mã loại trừ (`navs`: [(date, nav)]).
    Trả {date: lý do} cho ngày KHÔNG ghi được."""
    have = read_excluded_history(ctx.excl_path(account))
    new, failed = [], {}
    for d, nav in navs:
        if d in have:
            continue
        row, why = excluded_value_for(ctx, account, account_no, excluded, d, nav)
        if row is None:
            failed[d] = why
        else:
            new.append(row)
    if new:
        _append_excluded(ctx.excl_path(account), new)
    return failed


# ------------------------------------------------------------------ dựng chuỗi giá đơn vị
def _corp_events_today(ctx, d, tickers):
    """Sự kiện quyền của `tickers` có ngày hiệu lực ĐÚNG `d`, theo snapshot corp_action_daily của
    chính `d`. `(events, note)`; snapshot thiếu/không dùng được ⇒ ([], note nói rõ)."""
    path = os.path.join(ctx.corp_dir, f"corp_action_daily_{d}.json")
    if not os.path.exists(path):
        return [], f"không có {os.path.basename(path)}"
    try:
        snap = _read_json(path, {})
    except ValueError as exc:
        return [], f"{os.path.basename(path)} không đọc được: {exc}"
    if snap.get("asof") != d.isoformat() or snap.get("usable") is not True:
        return [], (f"{os.path.basename(path)} không dùng được (asof={snap.get('asof')!r} "
                    f"usable={snap.get('usable')!r})")
    return [e for e in snap.get("upcoming_events_held") or []
            if e.get("ticker") in tickers and e.get("date") == d.isoformat()], None


def sleeve_tripwires(ctx, excl, dates, declared):
    """{date: lý do} — ngày phần quản lý CÓ THỂ đã nhận/chuyển tiền với phần loại trừ mà chưa có
    bản ghi nào trong managed_sleeve_flows.json cho ngày đó."""
    out = {}
    for prev, cur in zip(dates, dates[1:]):
        a, b = excl[prev]["detail"], excl[cur]["detail"]
        why = []
        # số phiên giao dịch trong (prev, cur] — hai dòng có thể cách nhau nhiều phiên (ngày thiếu)
        n = max(1, sum(is_session(prev + datetime.timedelta(days=i))
                       for i in range(1, (cur - prev).days + 1)))
        for t in sorted(set(a) | set(b)):
            qa, qb = (a.get(t) or {}).get("qty", 0.0), (b.get(t) or {}).get("qty", 0.0)
            if abs(qa - qb) > 1e-6:
                why.append(f"KL mã loại trừ {t} đổi {vnd(qa)} → {vnd(qb)} (so với {prev})")
                continue
            if qa <= 0:
                continue
            ratio = b[t]["price"] / a[t]["price"]
            if not (1 - EXCL_PRICE_BAND) ** n <= ratio <= (1 + EXCL_PRICE_BAND) ** n:
                why.append(f"giá {t} nhảy {pct(ratio - 1)} ({vnd(a[t]['price'])} → "
                           f"{vnd(b[t]['price'])}, so với {prev}) — quá biên độ sàn ±"
                           f"{EXCL_PRICE_BAND * 100:.1f}%/phiên qua {n} phiên".replace("7.5", "7,5"))
        if b:
            events, _note = _corp_events_today(ctx, cur, set(b))
            for e in events:
                amt = ""
                try:
                    if e.get("event_code") == "DIV":
                        amt = (f" ≈ {vnd(float(e['value_per_share']) * b[e['ticker']]['qty'])}đ"
                               f" tiền về phần quản lý")
                except (KeyError, TypeError, ValueError):
                    pass
                why.append(f"lịch corp-action: {e.get('ticker')} {e.get('event_code')} hiệu lực "
                           f"{cur} ({e.get('title')}){amt}")
        if why and cur not in declared:
            out[cur] = "; ".join(why)
    return out


def build_chain(ctx, account, profile, today):
    """Chuỗi giá đơn vị làm cơ sở đo + chuỗi NAV tổng (chỉ hiển thị).
    Trả dict: basis, ledger | None, error, warnings[], unexplained{date: lý do}, total_ledger,
    rows (nav_history), excl."""
    out = {"basis": "managed" if profile["excluded_tickers"] else "total", "ledger": None,
           "error": None, "warnings": [], "unexplained": {}, "total_ledger": None, "rows": [],
           "excl": {}}
    try:
        rows = load_nav_history(account, ctx.exec_dir)
        inception = load_inception(account, ctx.inception_path)
        flows = load_flows(account, flows_path=ctx.flows_path, require_file=True, today=today)
        base_date, base_nav = _inception_baseline(rows, inception)
        out["rows"] = rows
        total, info = build_ledger(rows, flows, base_date, base_nav)
        if info["pending"]:
            raise ValueError(f"{len(info['pending'])} dòng tiền TREO trong {ctx.flows_path} (chưa "
                             f"dòng NAV nào chụp sau thời điểm tiền vào/ra)")
        out["total_ledger"] = total
        if out["basis"] == "total":
            out["ledger"] = total
            return out
        excl = read_excluded_history(ctx.excl_path(account))
        out["excl"] = excl
        if not excl:
            raise ValueError(f"account khai excluded_tickers={profile['excluded_tickers']} nhưng "
                             f"chưa có chuỗi {ctx.excl_path(account)} ⇒ chưa tách được phần bot "
                             f"quản lý")
        sleeve = load_flows(account, flows_path=ctx.sleeve_flows_path, require_file=True,
                            today=today)
        m_rows = [NavRow(r[0], r[1] - excl[r[0]]["value"], is_estimate=r.is_estimate,
                         balance_ts=r.balance_ts) for r in rows if r[0] in excl]
        gaps = [r[0] for r in rows if r[0] not in excl and r[0] > base_date]
        if base_date in excl:
            m_base = (base_date, base_nav - excl[base_date]["value"])
        else:
            first = next((r for r in m_rows if r[0] > base_date), None)
            if first is None:
                raise ValueError(f"chuỗi {ctx.excl_path(account)} không có ngày nào trùng "
                                 f"nav_history sau mốc khởi điểm {base_date}")
            m_base = (first[0], first[1])
            out["warnings"].append(f"chuỗi phần quản lý chỉ bắt đầu từ {first[0]} (không có giá "
                                   f"trị mã loại trừ tại mốc khởi điểm {base_date})")
        if gaps:
            out["warnings"].append(f"{len(gaps)} ngày nav_history chưa có giá trị mã loại trừ "
                                   f"(chuỗi phần quản lý bắc cầu qua): "
                                   + ", ".join(str(d) for d in gaps[:6])
                                   + (" …" if len(gaps) > 6 else ""))
        ledger, info = build_ledger(m_rows, flows + sleeve, *m_base)
        if info["pending"]:
            raise ValueError(f"{len(info['pending'])} dòng tiền TREO (account_cash_flows / "
                             f"managed_sleeve_flows) chưa gán được vào dòng NAV nào")
        out["ledger"] = ledger
        dates = [r["date"] for r in ledger if r["date"] in excl]
        out["unexplained"] = sleeve_tripwires(ctx, excl, dates, {f["date"] for f in sleeve})
    except Exception as exc:  # §29: lý do = đúng thông điệp lỗi đọc được, không đoán
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


# ------------------------------------------------------------------ episode đòn bẩy
def load_episodes(ctx):
    data = _read_json(ctx.episodes_path, {"_doc": "Episode đòn bẩy cho phanh −15% "
                                          "(nav_loss_brake_monitor.py). Mở: monitor, khi đủ bằng "
                                          "chứng. Đóng: người, qua --close-episode.",
                                          "episodes": []})
    if not isinstance(data.get("episodes"), list):
        raise ValueError(f"{ctx.episodes_path}: thiếu list 'episodes'")
    return data


def active_episode(episodes, account, d):
    for e in episodes:
        if e["account"] != account or datetime.date.fromisoformat(e["opened_date"]) > d:
            continue
        if e.get("closed_date") is None or d < datetime.date.fromisoformat(e["closed_date"]):
            return e
    return None


def lever_positions(ctx, account_no, d, pkg):
    """({symbol: qty} dưới gói vay `pkg`, ts, lý do-không-đọc-được)."""
    positions, ts, why = raw_positions(ctx.exec_dir, account_no, d)
    if positions is None:
        return None, None, why
    return _qty_by_symbol(positions, keep=lambda p: p.get("loanPackageId") == pkg), ts, None


def detect_episode_opens(ctx, account, account_no, pkg, episodes, ledger, upto):
    """Mở episode cho những ngày có ĐỦ bản duyệt + vị thế gói vay thật. Trả (episode mới[], ghi
    chú[]). Không ghi file — người gọi quyết."""
    new, notes = [], []
    dates = [r["date"] for r in ledger]
    prefix = os.path.join(ctx.approvals_dir, f"margin_approval_{account}_")
    for path in sorted(glob.glob(prefix + "*.json")):
        try:
            d = datetime.date.fromisoformat(os.path.basename(path)[len(os.path.basename(prefix)):-5])
            rec = _read_json(path, {})
        except ValueError as exc:
            notes.append(f"{os.path.basename(path)} không đọc được: {exc}")
            continue
        if d > upto or rec.get("account") != account:
            continue
        mine = [e for e in episodes + new if e["account"] == account]
        if any(datetime.date.fromisoformat(e["opened_date"]) <= d
               and (e.get("closed_date") is None
                    or d < datetime.date.fromisoformat(e["closed_date"])) for e in mine):
            continue                      # ngày này đã nằm trong một episode
        if any(e.get("closed_date") and d < datetime.date.fromisoformat(e["closed_date"])
               for e in mine):
            continue                      # bản duyệt cũ hơn một episode đã đóng
        if rec.get("revoked"):
            notes.append(f"bản duyệt margin {d} đã bị thu hồi — không mở episode")
            continue
        held, ts, why = lever_positions(ctx, account_no, d, pkg)
        if held is None:
            notes.append(f"có bản duyệt margin {d} nhưng không kiểm được vị thế gói vay {pkg}: {why}")
            continue
        if not held:
            notes.append(f"có bản duyệt margin {d} nhưng broker KHÔNG có vị thế nào dưới gói vay "
                         f"{pkg} ngày đó ⇒ mới là ý định, chưa khớp — không mở episode")
            continue
        ref = [x for x in dates if x < d]
        if not ref:
            notes.append(f"bản duyệt margin {d} + vị thế gói vay {pkg} có thật, nhưng chuỗi giá "
                         f"đơn vị không có dòng nào trước {d} để làm điểm vào")
            continue
        new.append({"id": f"{account}-{d}", "account": account, "opened_date": d.isoformat(),
                    "entry_ref_date": ref[-1].isoformat(), "opened_by": "nav_loss_brake_monitor.py",
                    "evidence": {"approval_file": path, "approved_by": rec.get("approved_by"),
                                 "loan_package_id": pkg, "lever_positions": held,
                                 "positions_ts": ts},
                    "closed_date": None, "closed_by": None, "close_reason": None})
    return new, notes


# ------------------------------------------------------------------ đánh giá ba phanh
def _res(status, value=None, threshold=None, reason=None, **extra):
    r = {"status": status, "value": value, "threshold": threshold, "reason": reason}
    if value is not None and threshold is not None:
        # khoảng cách tới ngưỡng, điểm phần trăm; <= 0 = đã chạm
        r["distance_pp"] = (value - threshold) * 100
    r.update(extra)
    return r


def _missing_row_reason(ctx, account, d, chain):
    block = os.path.join(ctx.exec_dir, f"nav_gate_block_{account}_{d}.json")
    if os.path.exists(block):
        try:
            b = _read_json(block, {})
            return (f"nav_history không có dòng {d}: NAV bị cổng chặn — "
                    f"{os.path.basename(block)} gate_verdict={b.get('gate_verdict')!r} "
                    f"rc={b.get('rc')!r}")
        except ValueError as exc:
            return f"nav_history không có dòng {d}; {os.path.basename(block)} không đọc được: {exc}"
    if any(r[0] == d for r in chain["rows"]):
        return (f"nav_history CÓ dòng {d} nhưng chuỗi giá trị mã loại trừ thì không ⇒ chưa tách "
                f"được phần bot quản lý ngày đó")
    last = chain["rows"][-1][0] if chain["rows"] else None
    return (f"nav_history không có dòng {d} (dòng mới nhất: {last}); không thấy file "
            f"nav_gate_block_{account}_{d}.json")


def evaluate(ctx, account, d, chain, th, th_err, episodes, extra_block=None):
    """Ba phanh của `account` tại phiên `d`, chỉ dùng dữ liệu có ngày <= d."""
    res = {}
    block = chain["error"] or extra_block
    cut = [r for r in (chain["ledger"] or []) if r["date"] <= d]
    row = cut[-1] if cut and cut[-1]["date"] == d and len(cut) > 1 else None
    if not block and row is None:
        block = _missing_row_reason(ctx, account, d, chain)
    bad = {k: v for k, v in chain["unexplained"].items() if k <= d}
    if not block and bad:
        k = max(bad)
        block = (f"phần bot quản lý có {len(bad)} ngày nghi nhận/chuyển tiền với phần loại trừ mà "
                 f"CHƯA khai trong managed_sleeve_flows.json — gần nhất {k}: {bad[k]}")
    if block:
        for b in BRAKES:
            res[b] = _res(UNMEASURABLE, threshold=th.get(b), reason=th_err.get(b) or block)
        return res

    est = "dòng NAV {} mang cờ nav_is_estimate (backfill ước tính) — số dưới đây chỉ là TẠM TÍNH"
    # --- lỗ một ngày
    # Mốc so = giá chốt của phiên liền trước. nav_history có cả dòng của ngày NGHỈ (cron vẫn chạy,
    # vd 2026-08-31): dòng đó mang đúng giá chốt phiên trước + lãi tiền gửi, nên khi không có dòng
    # đúng ngày phiên trước thì một dòng ngày nghỉ nằm SAU nó vẫn là mốc hợp lệ.
    want = prev_session(d)
    prev = next((r for r in cut[:-1] if r["date"] == want), cut[-2])
    v = row["unit_price"] / prev["unit_price"] - 1
    if "daily" in th_err:
        res["daily"] = _res(UNMEASURABLE, reason=th_err["daily"])
    elif prev["date"] < want:
        res["daily"] = _res(UNMEASURABLE, v, th["daily"], provisional=True,
                            reason=f"thiếu dòng của phiên liền trước {want}: dòng trước {d} trong "
                                   f"chuỗi là {prev['date']} ⇒ con số là gộp nhiều phiên")
    elif row["nav_is_estimate"] or prev["nav_is_estimate"]:
        which = d if row["nav_is_estimate"] else prev["date"]
        res["daily"] = _res(UNMEASURABLE, v, th["daily"], provisional=True, reason=est.format(which))
    else:
        res["daily"] = _res(BREACH if v <= th["daily"] + EPS else OK, v, th["daily"])
    # --- lỗ từ đỉnh
    peak = max(cut, key=lambda r: r["unit_price"])
    v = row["unit_price"] / peak["unit_price"] - 1
    extra = {"peak_date": peak["date"].isoformat(), "peak_unit_price": peak["unit_price"]}
    if row["nav_is_estimate"]:
        res["drawdown"] = _res(UNMEASURABLE, v, -DD_THRESHOLD, provisional=True,
                               reason=est.format(d), **extra)
    else:
        res["drawdown"] = _res(BREACH if v <= -DD_THRESHOLD + EPS else OK, v, -DD_THRESHOLD,
                               **extra)
        if peak["nav_is_estimate"]:
            res["drawdown"]["note"] = f"đỉnh {peak['date']} nằm trên dòng nav_is_estimate"
    # --- lỗ từ điểm vào episode
    if "episode" in th_err:
        res["episode"] = _res(UNMEASURABLE, reason=th_err["episode"])
        return res
    ep = active_episode(episodes, account, d)
    if ep is None:
        res["episode"] = _res(NO_EPISODE, threshold=th["episode"],
                              reason="không có episode đòn bẩy nào đang mở")
        return res
    ref = datetime.date.fromisoformat(ep["entry_ref_date"])
    entry = next((r for r in cut if r["date"] == ref), None)
    extra = {"episode_id": ep["id"], "entry_ref_date": ep["entry_ref_date"]}
    if entry is None:
        res["episode"] = _res(UNMEASURABLE, threshold=th["episode"], **extra,
                              reason=f"episode {ep['id']}: chuỗi giá đơn vị không có dòng của điểm "
                                     f"vào {ref}")
        return res
    v = row["unit_price"] / entry["unit_price"] - 1
    if row["nav_is_estimate"]:
        res["episode"] = _res(UNMEASURABLE, v, th["episode"], provisional=True,
                              reason=est.format(d), **extra)
    else:
        res["episode"] = _res(BREACH if v <= th["episode"] + EPS else OK, v, th["episode"], **extra)
    return res


def total_info(chain, d):
    """Số của NAV tổng tại `d` — CHỈ hiển thị kèm, không kích phanh."""
    cut = [r for r in (chain["total_ledger"] or []) if r["date"] <= d]
    if len(cut) < 2 or cut[-1]["date"] != d:
        return None
    peak = max(cut, key=lambda r: r["unit_price"])
    return {"nav": cut[-1]["nav"], "daily": cut[-1]["unit_price"] / cut[-2]["unit_price"] - 1,
            "daily_prev_date": cut[-2]["date"].isoformat(),
            "drawdown": cut[-1]["unit_price"] / peak["unit_price"] - 1,
            "peak_date": peak["date"].isoformat()}


# ------------------------------------------------------------------ chạy cho một account
def run_account(ctx, account, profile, d, th, th_err, episodes_data, record=True):
    """Trả dict trạng thái của account tại phiên `d`. `record=True` mới ghi chuỗi mã loại trừ và
    mở episode (chạy thật); False = chỉ đọc (replay)."""
    account_no = profile["account_id"]
    notes, extra_block = [], None
    today = ctx.now.astimezone(ICT).date()
    if record and profile["excluded_tickers"]:
        try:
            navs = [(r[0], r[1]) for r in load_nav_history(account, ctx.exec_dir)]
            failed = record_excluded(ctx, account, account_no, set(profile["excluded_tickers"]),
                                     navs)
            if d in failed:
                extra_block = (f"chưa ghi được giá trị mã loại trừ ngày {d} ⇒ không tách được phần "
                               f"bot quản lý: {failed[d]}")
        except Exception as exc:
            extra_block = f"không ghi được chuỗi giá trị mã loại trừ: {type(exc).__name__}: {exc}"
    chain = build_chain(ctx, account, profile, today)
    episodes = episodes_data["episodes"]
    if chain["ledger"] and th.get("lever_package_id") is not None:
        new, ep_notes = detect_episode_opens(ctx, account, account_no, th["lever_package_id"],
                                             episodes, chain["ledger"], d)
        notes += ep_notes
        if new:
            episodes = episodes + new
            if record:
                episodes_data["episodes"] = episodes
                _write_json_atomic(ctx.episodes_path, episodes_data)
            notes += [f"MỞ episode {e['id']} (điểm vào {e['entry_ref_date']})" for e in new]
    res = evaluate(ctx, account, d, chain, th, th_err, episodes, extra_block=extra_block)
    # vị thế gói vay có thật mà không có episode nào ⇒ phanh −15% đang không canh gì: nói to
    if (res["episode"]["status"] == NO_EPISODE and th.get("lever_package_id") is not None):
        held, _ts, _why = lever_positions(ctx, account_no, d, th["lever_package_id"])
        if held:
            res["episode"] = _res(
                UNMEASURABLE, threshold=th["episode"],
                reason=(f"broker có vị thế dưới gói vay {th['lever_package_id']} ngày {d} "
                        f"({', '.join(f'{k} {vnd(v)}' for k, v in sorted(held.items()))}) nhưng "
                        f"KHÔNG có episode nào đang mở và không có bản duyệt margin hợp lệ để mở"))
    cut = [r for r in (chain["ledger"] or []) if r["date"] <= d]
    row = cut[-1] if cut and cut[-1]["date"] == d else None
    excl = chain["excl"].get(d)
    return {"basis": chain["basis"], "session": d.isoformat(),
            "basis_nav": row["nav"] if row else None,
            "unit_price": row["unit_price"] if row else None,
            "excluded_value": excl["value"] if excl else (0.0 if chain["basis"] == "total" else None),
            "excluded_detail": excl["detail"] if excl else {},
            "brakes": res, "total_nav_info": total_info(chain, d),
            "warnings": chain["warnings"], "notes": notes,
            "overall": worst([res[b]["status"] for b in BRAKES])}


def worst(statuses):
    for s in (BREACH, UNMEASURABLE):
        if s in statuses:
            return s
    return OK


# ------------------------------------------------------------------ cảnh báo (idempotent §5)
def brake_line(b, r):
    name = BRAKE_VI[b]
    if r["status"] == NO_EPISODE:
        return f"{name}: không có episode đang mở (ngưỡng {pct(r['threshold'], 0)})"
    if r["status"] == UNMEASURABLE:
        tmp = f" · tạm tính {pct(r['value'])} (ngưỡng {pct(r['threshold'], 0)})" \
            if r.get("value") is not None else ""
        return f"{name}: KHÔNG ĐO ĐƯỢC — {r['reason']}{tmp}"
    dist = f"{abs(r['distance_pp']):.2f}pp".replace(".", ",")
    tail = f"cách {dist}" if r["status"] == OK else f"ĐÃ CHẠM, vượt {dist}"
    more = f", đỉnh {r['peak_date']}" if b == "drawdown" else (
        f", điểm vào {r['entry_ref_date']}" if b == "episode" else "")
    return f"{name}: {pct(r['value'])} (ngưỡng {pct(r['threshold'], 0)}, {tail}{more})"


def brake_lines(res, mark=False):
    """Ba dòng (hoặc MỘT dòng khi cả ba phanh bị chặn bởi cùng một lý do)."""
    icon = {BREACH: "🔴 ", UNMEASURABLE: "🟡 "}
    if (all(res[b]["status"] == UNMEASURABLE for b in BRAKES)
            and len({res[b]["reason"] for b in BRAKES}) == 1):
        return [f"{icon[UNMEASURABLE] if mark else ''}Cả 3 phanh: KHÔNG ĐO ĐƯỢC — "
                f"{res['daily']['reason']}"]
    return [(icon.get(res[b]["status"], "🟢 ") if mark else "") + brake_line(b, res[b])
            for b in BRAKES]


def basis_vi(st):
    return "phần bot quản lý" if st["basis"] == "managed" else "NAV toàn tài khoản"


def alert_text(account, st):
    lines = []
    breach = [b for b in BRAKES if st["brakes"][b]["status"] == BREACH]
    head = "🚨 PHANH LỖ NAV ĐÃ CHẠM" if breach else "⚠️ PHANH LỖ NAV — KHÔNG ĐO ĐƯỢC"
    lines.append(f"{head} — {account} · phiên {st['session']} · đo trên {basis_vi(st)}")
    lines += brake_lines(st["brakes"], mark=True)
    t = st.get("total_nav_info")
    if st["basis"] == "managed" and t:
        lines.append(f"ℹ️ NAV tổng (chỉ để tham chiếu, KHÔNG kích phanh): {vnd(t['nav'])}đ · ngày "
                     f"{pct(t['daily'])} · từ đỉnh {pct(t['drawdown'])}")
    for w in st["warnings"] + st["notes"]:
        lines.append(f"• {w}")
    if breach:
        lines.append("Monitor CHỈ CẢNH BÁO: không dừng bot, không huỷ lệnh. Nếu anh/chị quyết định "
                     "dừng giao dịch, tự chạy:")
        lines.append(f"`touch {os.path.join(WC_ROOT, 'data', 'BOT_STOP')}`")
    else:
        lines.append("Không đo được KHÔNG có nghĩa là an toàn — cần người xem lý do ở trên.")
    return "\n".join(lines)


def send_alert(ctx, text):
    """(ok, chi tiết). Selfcheck/chạy thử đặt MIKE_LOSS_BRAKE_ALERT_SINK=<file> ⇒ không chạm mạng."""
    sink = os.environ.get(SINK_ENV)
    if sink:
        with open(sink, "a", encoding="utf-8") as f:
            f.write(json.dumps({"channel": NOTIFY_CHANNEL, "text": text}, ensure_ascii=False) + "\n")
        return True, f"sink {sink}"
    if not ctx.is_live:
        return False, (f"TỪ CHỐI gửi Discord thật: đang chạy với thư mục dữ liệu/state không phải "
                       f"mặc định và chưa đặt {SINK_ENV}")
    try:
        r = subprocess.run([os.path.join(BIN, "notify_thread.sh"), text, NOTIFY_CHANNEL],
                           capture_output=True, text=True, timeout=180)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"{type(exc).__name__}: {exc}"
    return r.returncode == 0, (f"notify_thread.sh rc={r.returncode} "
                               f"{(r.stderr or r.stdout or '').strip()[-300:]}")


def dispatch_alerts(ctx, account, st):
    """Gửi MỘT tin cho account nếu có phát hiện CHƯA từng gửi của phiên này. Ghi dấu NGAY sau khi
    gửi được (trước khi làm bất cứ gì khác). Trả dict kết quả cho file trạng thái."""
    keys = [f"{account}|{st['session']}|{b}|{st['brakes'][b]['status']}" for b in BRAKES
            if st["brakes"][b]["status"] in (BREACH, UNMEASURABLE)]
    sent = _read_json(ctx.sent_path, {})
    new = [k for k in keys if k not in sent]
    out = {"keys": keys, "new": new, "sent_now": False, "send_error": None}
    if not new:
        return out
    ok, detail = send_alert(ctx, alert_text(account, st))
    if not ok:
        out["send_error"] = detail
        return out
    stamp = datetime.datetime.now(ICT).isoformat(timespec="seconds")
    sent.update({k: stamp for k in new})
    _write_json_atomic(ctx.sent_path, sent)
    out["sent_now"] = True
    return out


# ------------------------------------------------------------------ dòng cho ops_health_check
def health_line(ctx, account):
    """(rc, dòng). rc=0: file trạng thái ĐÚNG phiên phải có và account OK. rc=1: phanh chạm /
    không đo được / gửi cảnh báo lỗi (việc của NGƯỜI). rc=2: monitor không chạy — file thiếu, cũ,
    hỏng (việc của vận hành). §14: độ tươi kiểm bằng PHIÊN ghi trong file so với lịch, không mtime."""
    want = expected_session(ctx.now)
    try:
        st = _read_json(ctx.status_path, None)
    except ValueError as exc:
        return 2, f"Phanh lỗ NAV [{account}]: {ctx.status_path} không đọc được ({exc})"
    if st is None:
        return 2, (f"Phanh lỗ NAV [{account}]: CHƯA có {ctx.status_path} — monitor chưa từng chạy "
                   f"(phanh lỗ đang không ai canh)")
    if st.get("session") != want.isoformat():
        return 2, (f"Phanh lỗ NAV [{account}]: file trạng thái CŨ — đang ghi phiên "
                   f"{st.get('session')} (chạy lúc {st.get('generated_at')}), phiên phải có là "
                   f"{want} ⇒ monitor không chạy tối qua")
    a = (st.get("accounts") or {}).get(account)
    if a is None:
        return 2, (f"Phanh lỗ NAV [{account}]: file trạng thái phiên {want} không có account này "
                   f"(có: {sorted(st.get('accounts') or {})})")
    body = " · ".join(brake_lines(a["brakes"]))
    alert = a.get("alert") or {}
    if alert.get("send_error"):
        body += f" · ❌ GỬI CẢNH BÁO LỖI: {alert['send_error']}"
    rc = 0 if a["overall"] == OK and not alert.get("send_error") else 1
    return rc, f"Phanh lỗ NAV [{account}] phiên {want:%d/%m} ({basis_vi(a)}): {body}"


# ------------------------------------------------------------------ replay toàn lịch sử
def replay(ctx, accounts, profiles, th, th_err):
    """Chạy thử: với MỖI phiên từ mốc khởi điểm tới dòng NAV mới nhất, monitor sẽ nói gì nếu chạy
    tối hôm đó trên dữ liệu ĐANG CÓ. Không ghi, không gửi."""
    eps = load_episodes(ctx)
    rc = 0
    for account in accounts:
        today = ctx.now.astimezone(ICT).date()
        chain = build_chain(ctx, account, profiles[account], today)
        print(f"\n=== {account} · cơ sở đo: {chain['basis']} ===")
        if chain["error"]:
            print(f"  KHÔNG dựng được chuỗi: {chain['error']}")
            rc = 1
            continue
        for w in chain["warnings"]:
            print(f"  ⚠ {w}")
        led = chain["ledger"]
        new, notes = detect_episode_opens(ctx, account, profiles[account]["account_id"],
                                          th.get("lever_package_id"), eps["episodes"], led,
                                          led[-1]["date"]) if th.get("lever_package_id") else ([], [])
        episodes = eps["episodes"] + new
        for n in notes + [f"episode sẽ mở: {e['id']} (điểm vào {e['entry_ref_date']})" for e in new]:
            print(f"  • {n}")
        d, last = led[0]["date"], chain["rows"][-1][0]
        n_ok = n_days = 0
        run = []                         # [thông điệp, phiên đầu, phiên cuối, số phiên]

        def flush():
            if run:
                span = f"{run[1]}" if run[3] == 1 else f"{run[1]} → {run[2]} ({run[3]} phiên)"
                print(f"  {span}\n      " + run[0].replace("\n", "\n      "))
            run.clear()
        worst_day, worst_dd = (0.0, None), (0.0, None)
        while d < last:
            d += datetime.timedelta(days=1)
            if not is_session(d):
                continue
            n_days += 1
            res = evaluate(ctx, account, d, chain, th, th_err, episodes)
            for b, tracker in (("daily", "day"), ("drawdown", "dd")):
                v = res[b].get("value")
                if v is not None and res[b]["status"] in (OK, BREACH):
                    if tracker == "day" and v < worst_day[0]:
                        worst_day = (v, d)
                    if tracker == "dd" and v < worst_dd[0]:
                        worst_dd = (v, d)
            if worst([res[b]["status"] for b in BRAKES]) == OK:
                n_ok += 1
                flush()
                continue
            if len({res[b]["reason"] for b in BRAKES}) == 1:      # cùng một lý do chặn cả ba
                msg = f"{UNMEASURABLE} cả 3 phanh — {res['daily']['reason']}"
            else:
                msg = "\n".join(f"{res[b]['status']} {brake_line(b, res[b])}" for b in BRAKES
                                if res[b]["status"] in (BREACH, UNMEASURABLE))
            if run and run[0] == msg:
                run[2], run[3] = d, run[3] + 1
            else:
                flush()
                run.extend([msg, d, d, 1])
        flush()
        print(f"  — {n_days} phiên, {n_ok} phiên im lặng, {n_days - n_ok} phiên sẽ kêu.")
        print(f"  — ngày giảm mạnh nhất (đo được): {pct(worst_day[0])} ngày {worst_day[1]} · "
              f"sâu nhất từ đỉnh: {pct(worst_dd[0])} ngày {worst_dd[1]}")
        st = run_account(ctx, account, profiles[account], last, th, th_err,
                         {"episodes": episodes}, record=False)
        print(f"  — dòng mới nhất {last}: " + " · ".join(brake_line(b, st["brakes"][b])
                                                         for b in BRAKES))
        t = st["total_nav_info"]
        if t:
            print(f"  — NAV tổng {last}: ngày {pct(t['daily'])} · từ đỉnh {pct(t['drawdown'])} "
                  f"(đỉnh {t['peak_date']})")
        tl = chain["total_ledger"]
        day = min(((b["unit_price"] / a["unit_price"] - 1, b["date"]) for a, b in zip(tl, tl[1:])))
        peak, dd = tl[0]["unit_price"], (0.0, None)
        for r in tl:
            peak = max(peak, r["unit_price"])
            dd = min(dd, (r["unit_price"] / peak - 1, r["date"]), key=lambda x: x[0])
        print(f"  — NAV tổng, cả lịch sử (dòng-so-dòng, kể cả dòng ước tính): ngày giảm mạnh nhất "
              f"{pct(day[0])} ngày {day[1]} · sâu nhất từ đỉnh {pct(dd[0])} ngày {dd[1]}")
    return rc


# ------------------------------------------------------------------ main
def close_episode(ctx, account, closed_by, reason):
    if not (closed_by or "").strip() or not (reason or "").strip():
        print("❌ --close-episode cần --closed-by và --reason (ai đóng, vì sao).", file=sys.stderr)
        return 2
    data = load_episodes(ctx)
    today = ctx.now.astimezone(ICT).date()
    ep = next((e for e in data["episodes"] if e["account"] == account
               and e.get("closed_date") is None), None)
    if ep is None:
        print(f"❌ {account}: không có episode nào đang mở trong {ctx.episodes_path}.",
              file=sys.stderr)
        return 1
    ep.update(closed_date=today.isoformat(), closed_by=closed_by.strip(),
              close_reason=reason.strip())
    _write_json_atomic(ctx.episodes_path, data)
    print(f"Đã đóng episode {ep['id']} từ {today} (bởi {closed_by}).")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--account", action="append",
                    help="mặc định: mọi account có trong account_inception.json")
    ap.add_argument("--date", help="phiên cần đo YYYY-MM-DD (mặc định: phiên phải có NAV chốt)")
    ap.add_argument("--data-root")
    ap.add_argument("--state-dir")
    ap.add_argument("--secrets")
    ap.add_argument("--now", help="giả lập đồng hồ ICT (ISO) — chỉ cho selfcheck")
    ap.add_argument("--replay", action="store_true")
    ap.add_argument("--health-line", action="store_true")
    ap.add_argument("--close-episode", metavar="ACCOUNT")
    ap.add_argument("--closed-by")
    ap.add_argument("--reason")
    args = ap.parse_args(argv)

    now = None
    if args.now:
        now = datetime.datetime.fromisoformat(args.now)
        now = now.replace(tzinfo=ICT) if now.tzinfo is None else now.astimezone(ICT)
    ctx = Ctx(args.data_root, args.state_dir, args.secrets, now)

    if args.close_episode:
        return close_episode(ctx, args.close_episode, args.closed_by, args.reason)
    if args.health_line:
        if not args.account or len(args.account) != 1:
            print("❌ --health-line cần đúng một --account.", file=sys.stderr)
            return 2
        rc, line = health_line(ctx, args.account[0])
        print(line)
        return rc

    profiles = load_profiles(ctx.secrets_path)
    accounts = args.account or [k for k in _read_json(ctx.inception_path, {})
                                if not k.startswith("_")]
    missing = [a for a in accounts if a not in profiles or not profiles[a]["account_id"]]
    if missing or not accounts:
        print(f"❌ account {missing or '(rỗng)'} không có trong {ctx.secrets_path} — không biết "
              f"account_no để lọc dữ liệu broker (§12).", file=sys.stderr)
        return 2
    th, th_err = load_thresholds(ctx.rules_path)
    for b, why in th_err.items():
        print(f"❌ THIẾU NGƯỠNG phanh '{b}': {why}", file=sys.stderr)
    if args.replay:
        return replay(ctx, accounts, profiles, th, th_err)

    d = datetime.date.fromisoformat(args.date) if args.date else expected_session(ctx.now)
    episodes_data = load_episodes(ctx)
    status = {"schema": STATUS_SCHEMA, "generated_at": ctx.now.isoformat(timespec="seconds"),
              "session": d.isoformat(),
              "thresholds": {"daily": th["daily"], "drawdown": th["drawdown"],
                             "episode": th["episode"], "errors": th_err,
                             "sources": {"daily": "trading_rules.json risk_circuit_breakers."
                                                  "daily_loss_limit_pct",
                                         "drawdown": "hằng số DD_THRESHOLD (risk_monitor.py:46)",
                                         "episode": "trading_rules.json macro_kill_switches."
                                                    "C_episode_drawdown_breaker.trigger"}},
              "accounts": {}}
    rc = 0
    for account in accounts:
        try:
            st = run_account(ctx, account, profiles[account], d, th, th_err, episodes_data)
        except Exception as exc:  # một account hỏng không được làm account kia mất tiếng
            why = f"monitor lỗi khi đo {account}: {type(exc).__name__}: {exc}"
            st = {"basis": "managed" if profiles[account]["excluded_tickers"] else "total",
                  "session": d.isoformat(), "basis_nav": None, "unit_price": None,
                  "excluded_value": None, "excluded_detail": {}, "total_nav_info": None,
                  "brakes": {b: _res(UNMEASURABLE, threshold=th.get(b), reason=why)
                             for b in BRAKES},
                  "warnings": [], "notes": [], "overall": UNMEASURABLE}
        st["alert"] = dispatch_alerts(ctx, account, st)
        status["accounts"][account] = st
        mark = {OK: "✅", BREACH: "🚨", UNMEASURABLE: "⚠️"}[st["overall"]]
        print(f"{mark} {account} phiên {d} ({basis_vi(st)}): " + " · ".join(brake_lines(st["brakes"])))
        if st["alert"]["send_error"]:
            print(f"❌ {account}: KHÔNG gửi được cảnh báo — {st['alert']['send_error']}",
                  file=sys.stderr)
            rc = 3
        elif st["overall"] != OK and rc == 0:
            rc = 1
    status["overall"] = worst([a["overall"] for a in status["accounts"].values()])
    _write_json_atomic(ctx.status_path, status)
    return rc


if __name__ == "__main__":
    sys.exit(main())
