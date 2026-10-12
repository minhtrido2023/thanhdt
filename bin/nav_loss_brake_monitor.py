#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monitor PHANH LỖ CẤP NAV — CHỈ CẢNH BÁO (user duyệt 2026-10-12, job Taylor_20261012_111422;
sửa theo arch-review vòng 1 và 2; vòng 3 = job Taylor_20261012_161627).

Đo ba phanh trên GIÁ ĐƠN VỊ QUỸ chốt-so-chốt của từng account, mỗi tối sau khi NAV đã chốt:
  · lỗ một ngày   <= `risk_circuit_breakers.daily_loss_limit_pct` (data/trading_rules.json)
  · lỗ từ đỉnh    >= DD_THRESHOLD (hằng số dưới đây — KHÔNG có khoá trong trading_rules.json)
  · lỗ từ điểm vào một episode đòn bẩy <= `macro_kill_switches.C_episode_drawdown_breaker.
    episode_drawdown_limit_pct` (data/trading_rules.json)

MONITOR NÀY KHÔNG BAO GIỜ tạo `data/BOT_STOP`, không huỷ lệnh, không gọi broker, không gọi BQ.
Chạm ngưỡng ⇒ gửi cảnh báo (in sẵn lệnh để NGƯỜI tự tạo BOT_STOP) và chờ người quyết.

CƠ SỞ ĐO: NAV TOÀN TÀI KHOẢN, cho MỌI account (user chốt 2026-10-12 21:31 ICT: không còn tách
"phần bot quản lý"; `excluded_tickers` của account KHÔNG ảnh hưởng gì tới monitor này). Tỉ suất:
một công thức duy nhất — `nav_unit_ledger.build_ledger` (chính sách
`kb/projects/fund-unit-performance-policy-20261010.md`); file này chỉ lấy TỈ SỐ hai giá đơn vị.

GIÁ CHỐT: một dòng nav_history chỉ là giá chốt của ngày `D` khi `balance_ts` của nó nằm trong
[giờ đóng cửa phiên gần nhất <= D, giờ mở cửa phiên kế sau D). Dòng chụp ngoài khoảng đó (vd
04:49 sáng, hay 09:15 hôm sau) KHÔNG phải giá chốt ⇒ số đo dùng nó chỉ là TẠM TÍNH.

FAIL-LOUD: thiếu dòng NAV phiên phải có, dòng không phải giá chốt, dòng `nav_is_estimate`, thiếu
phiên liền trước, sổ dòng tiền thiếu/lỗi/còn dòng TREO, thiếu khoá ngưỡng, không đọc được vị thế
broker ⇒ "KHÔNG ĐO ĐƯỢC" kèm lý do ĐỌC TỪ DỮ LIỆU (§29). Hễ sổ còn dựng được và có dòng NAV của
phiên thì LUÔN kèm số TẠM TÍNH; tạm tính đã vượt ngưỡng là trạng thái RIÊNG (BREACH_PROVISIONAL):
tin đỏ, có dòng lệnh BOT_STOP, khoá chống-trùng riêng. Monitor tự hỏng ⇒ vẫn ghi status KHÔNG ĐO
ĐƯỢC và cố gửi một tin "monitor lỗi". Không có nhánh nào coi "không đọc được" là "an toàn".

LUẬT GIẢM TIN (user duyệt 2026-10-12 21:31 ICT): một phanh KHÔNG ĐO ĐƯỢC mà lý do DUY NHẤT là cờ
`nav_is_estimate` (dòng phiên hoặc dòng mốc so) VÀ số tạm tính còn cách ngưỡng HƠN
QUIET_ESTIMATE_MARGIN_PP điểm % ⇒ KHÔNG đẩy tin tối; trạng thái vẫn là KHÔNG ĐO ĐƯỢC kèm số tạm
tính trong status.json và dòng kiểm sáng. Mọi ca khác đẩy như cũ.

EPISODE: tự mở khi có ĐỦ hai bằng chứng — bản duyệt `data/margin_approvals/
margin_approval_{account}_{date}.json` (chưa thu hồi) VÀ vị thế mở dưới gói vay
`capit_margin_lever.loan_package_id` trong bản ghi positions SAU giờ đóng cửa của ngày duyệt hoặc
phiên kế. Bản duyệt mà không có vị thế = mới là ý định (§27), không mở. Mở tay: `--open-episode`.
Đóng bằng tay: `--close-episode` (phiên của CHÍNH ngày đóng vẫn đo với episode). Episode đang mở
mà broker không còn vị thế gói vay, hoặc có bản duyệt MỚI trong lúc episode còn mở (chưa
`--ack-approval`) ⇒ phanh episode KHÔNG ĐO ĐƯỢC. Mỗi lệnh tay ghi state gửi MỘT dòng vào
trading_daily (ai, lý do, trước/sau), ghi `human_actions.jsonl`, và hiện trong notes lượt đo kế.

Dùng:
    python3 mike/bin/nav_loss_brake_monitor.py                      # chạy thật (cron tối)
    python3 mike/bin/nav_loss_brake_monitor.py --date 2026-10-09    # phiên cũ: CHẠY KHÔ, không ghi/gửi
    python3 mike/bin/nav_loss_brake_monitor.py --date 2026-10-09 --write-backdated
    python3 mike/bin/nav_loss_brake_monitor.py --replay             # chạy thử toàn lịch sử, không ghi/gửi
    python3 mike/bin/nav_loss_brake_monitor.py --health-line --account SpaceX   # ops_health_check
    python3 mike/bin/nav_loss_brake_monitor.py --close-episode SpaceX --closed-by "user ..." --reason "..."
    python3 mike/bin/nav_loss_brake_monitor.py --open-episode SpaceX --opened-date 2026-10-13 \\
        --opened-by "user ..." --reason "..."
    python3 mike/bin/nav_loss_brake_monitor.py --ack-approval SpaceX --approval-date 2026-10-14 \\
        --acked-by "user ..." --reason "cùng episode, giải ngân thêm"
Mã thoát lượt chạy: 0 = cả ba phanh OK · 1 = có phanh chạm / tạm tính vượt / không đo được ·
3 = monitor lỗi hoặc không gửi được cảnh báo · 4 = lượt khác đang giữ khoá.
Mã thoát `--health-line`: 0 OK · 1 không đo được · 5 phanh chạm / tạm tính vượt · 2 monitor không
chạy (file thiếu/cũ/hỏng) · 3 monitor lỗi / không gửi được cảnh báo.
Selfcheck: python3 mike/bin/nav_loss_brake_monitor_selfcheck.py
"""
import argparse
import contextlib
import datetime
import fcntl
import glob
import json
import os
import re
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BIN)

from account_cash_flows import SESSION_CLOSE_ICT, load_flows  # noqa: E402
from nav_unit_ledger import (_inception_baseline, build_ledger, load_inception,  # noqa: E402
                             load_nav_history)
from wc_paths import find_wc_root  # noqa: E402

WC_ROOT = find_wc_root(__file__)
sys.path.insert(0, WC_ROOT)

from trading_bot.vn_market import SESSIONS, is_holiday  # noqa: E402

ICT = ZoneInfo("Asia/Ho_Chi_Minh")

# Ngưỡng lỗ từ đỉnh. Nguồn: `agents/Spyros/risk_monitor.py:46` (DD_THRESHOLD = 0.25) — con số
# này KHÔNG có khoá trong data/trading_rules.json nên giữ ở đây dưới dạng hằng số có tên.
DD_THRESHOLD = 0.25
# Sau giờ này của một ngày giao dịch thì NAV chốt của CHÍNH ngày đó phải đã có: lượt
# `nav_sync_retry.sh` cuối cùng chạy 21:45 ICT (kb/cron_registry.md).
NAV_EXPECTED_AFTER_ICT = datetime.time(21, 50)
# Giờ mở cửa phiên (ATO) — đọc từ bảng phiên của bot, không khai lại con số.
SESSION_OPEN_ICT = next(s[1] for s in SESSIONS if s[0] == "ATO")
# LUẬT GIẢM TIN — user duyệt 2026-10-12 21:31 ICT (giá trị do Mike đề xuất): phanh KHÔNG ĐO ĐƯỢC
# chỉ vì cờ nav_is_estimate mà số tạm tính còn cách ngưỡng HƠN chừng này điểm % thì không đẩy tin
# tối. Cách ngưỡng <= con số này (kể cả đúng 2,00) ⇒ vẫn đẩy.
QUIET_ESTIMATE_MARGIN_PP = 2.0
# Sai số dấu phẩy động khi so đúng biên (−5,00% phải kêu). 1e-9 = 0,0000001pp.
EPS = 1e-9
# Khoảng hợp lý của ngưỡng episode đọc từ trading_rules.json; ngoài khoảng ⇒ từ chối, không đoán.
EPISODE_TH_RANGE = (-0.30, -0.05)
# Khoá SỐ của ngưỡng episode: macro_kill_switches.C_episode_drawdown_breaker.<khoá này> (có trên
# WC main từ merge c6e43899). Chuỗi `trigger` cạnh nó chỉ còn để ĐỐI CHIẾU: lệch khoá số ⇒ lỗi.
EPISODE_NUMERIC_KEY = "episode_drawdown_limit_pct"
# Chờ khoá state tối đa chừng này giây rồi bỏ lượt (lượt đang giữ khoá làm đúng việc đó).
LOCK_WAIT_S = 60

OK, BREACH, BREACH_PROV = "OK", "BREACH", "BREACH_PROVISIONAL"
UNMEASURABLE, NO_EPISODE = "UNMEASURABLE", "NO_EPISODE"
ALERTING = (BREACH, BREACH_PROV, UNMEASURABLE)
BRAKES = ("daily", "drawdown", "episode")
BRAKE_VI = {"daily": "Lỗ một ngày", "drawdown": "Lỗ từ đỉnh", "episode": "Lỗ từ điểm vào episode"}
SINK_ENV = "MIKE_LOSS_BRAKE_ALERT_SINK"
NOTIFY_CHANNEL = "trading_daily"
STATUS_SCHEMA = 3
BASIS_VI = "NAV toàn tài khoản"
# Mã thoát của --health-line khi có phanh CHẠM / tạm tính vượt (tách khỏi 1 = không đo được).
HEALTH_RC_BREACH = 5
# Giá trị của cờ `revoked` được coi là CHƯA thu hồi — chép đúng trading_bot/plan.py (bản ghi
# duyệt margin): bất kỳ giá trị lạ nào khác đều nghiêng về ĐÃ THU HỒI.
NOT_REVOKED = (False, None, "", 0, "false", "False", "no", "0")


class ConfigError(ValueError):
    pass


class LockBusy(RuntimeError):
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
        self.state_is_live = (os.path.realpath(self.state_dir)
                              == os.path.realpath(os.path.join(d_data, "loss_brake")))
        self.is_live = (os.path.realpath(self.data_root) == os.path.realpath(d_data)
                        and self.state_is_live
                        and os.path.realpath(self.secrets_path) == os.path.realpath(d_secrets))
        self.exec_dir = os.path.join(self.data_root, "execution_logs")
        self.rules_path = os.path.join(self.data_root, "trading_rules.json")
        self.inception_path = os.path.join(self.data_root, "account_inception.json")
        self.flows_path = os.path.join(self.data_root, "account_cash_flows.json")
        self.approvals_dir = os.path.join(self.data_root, "margin_approvals")
        self.episodes_path = os.path.join(self.state_dir, "episodes.json")
        self.status_path = os.path.join(self.state_dir, "status.json")
        self.sent_path = os.path.join(self.state_dir, "alerts_sent.json")
        self.actions_path = os.path.join(self.state_dir, "human_actions.jsonl")
        self.run_log_path = os.path.join(self.state_dir, "run_log.jsonl")
        self.lock_path = os.path.join(self.state_dir, ".lock")
        self.now = now or datetime.datetime.now(ICT)
        # {date: {account_no: (positions, ts)}} — chỉ --replay bật (đọc lại cùng file nhiều lần)
        self.pos_cache = None


# ------------------------------------------------------------------ lịch phiên (§16: neo ICT)
def is_session(d):
    return d.weekday() < 5 and not is_holiday(d)


def prev_session(d):
    d -= datetime.timedelta(days=1)
    while not is_session(d):
        d -= datetime.timedelta(days=1)
    return d


def next_session(d):
    d += datetime.timedelta(days=1)
    while not is_session(d):
        d += datetime.timedelta(days=1)
    return d


def expected_session(now):
    """Phiên gần nhất mà NAV chốt PHẢI đã có tại thời điểm `now` (datetime ICT)."""
    d = now.astimezone(ICT).date() if now.tzinfo else now.date()
    t = now.astimezone(ICT).time() if now.tzinfo else now.time()
    if is_session(d) and t >= NAV_EXPECTED_AFTER_ICT:
        return d
    return prev_session(d)


def _parse_ts(ts):
    """Chuỗi giờ chụp (balance_ts / ts của dnse_raw) → datetime ICT naive; None = không đọc được."""
    try:
        t = datetime.datetime.fromisoformat(str(ts))
    except (TypeError, ValueError):
        return None
    return t.astimezone(ICT).replace(tzinfo=None) if t.tzinfo else t


def close_capture_problem(d, ts):
    """None nếu dòng NAV ngày `d` chụp lúc `ts` LÀ giá chốt: `ts` trong [giờ đóng cửa của phiên
    gần nhất <= d, giờ mở cửa của phiên kế sau d). Ngược lại trả lý do, trích giờ đọc được."""
    s = d if is_session(d) else prev_session(d)
    lo = datetime.datetime.combine(s, SESSION_CLOSE_ICT)
    hi = datetime.datetime.combine(next_session(d), SESSION_OPEN_ICT)
    t = _parse_ts(ts)
    if t is None:
        return (f"dòng NAV {d} không có balance_ts đọc được (đọc được: {ts!r}) ⇒ không biết chụp "
                f"trước hay sau giờ đóng cửa")
    if t < lo:
        return (f"dòng NAV {d} chụp số dư lúc {ts} — TRƯỚC giờ đóng cửa {lo:%H:%M} ngày {s} ⇒ "
                f"không phải giá chốt phiên {s}")
    if t >= hi:
        return (f"dòng NAV {d} chụp số dư lúc {ts} — SAU giờ mở cửa phiên kế "
                f"({hi:%H:%M} ngày {hi:%Y-%m-%d}) ⇒ đã lẫn giá của phiên sau")
    return None


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


@contextlib.contextmanager
def state_lock(ctx):
    """Khoá độc quyền cho mọi đường GHI vào state-dir (lượt chạy, mở/đóng episode, ack)."""
    os.makedirs(ctx.state_dir, exist_ok=True)
    f = open(ctx.lock_path, "a", encoding="utf-8")
    deadline = time.monotonic() + LOCK_WAIT_S
    try:
        while True:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError as exc:
                if time.monotonic() >= deadline:
                    raise LockBusy(f"không lấy được khoá {ctx.lock_path} sau {LOCK_WAIT_S}s "
                                   f"({type(exc).__name__}: {exc}) — một lượt khác đang ghi "
                                   f"state") from exc
                time.sleep(0.5)
        yield
    finally:
        f.close()


def vnd(x):
    return f"{x:,.0f}".replace(",", ".")


def pct(x, digits=2):
    return "n/a" if x is None else f"{x * 100:+.{digits}f}%".replace(".", ",")


# ------------------------------------------------------------------ ngưỡng (nguồn sự thật)
def _episode_threshold(rules_path, node):
    """(ngưỡng | None, lỗi | None, nguồn) của phanh episode. Khoá số là nguồn; chuỗi `trigger`
    chỉ để đối chiếu — hai bên LỆCH nhau ⇒ lỗi (không chọn hộ). Chưa có khoá số ⇒ đọc chuỗi."""
    where = f"{rules_path}: macro_kill_switches.C_episode_drawdown_breaker"
    lo, hi = EPISODE_TH_RANGE
    trig = node.get("trigger")
    # đúng dạng -0.xx (hai chữ số thập phân), không dính vào số khác (1-0.15, -0.015)
    found = (sorted(set(re.findall(r"(?<![\d.])-0\.\d\d(?!\d)", trig)))
             if isinstance(trig, str) else [])
    stated = re.findall(r"\(-(\d+(?:\.\d+)?)%\)", trig) if isinstance(trig, str) else []
    in_text = [float(x) for x in found] + [-float(x) / 100 for x in stated]
    if EPISODE_NUMERIC_KEY in node:
        v = node[EPISODE_NUMERIC_KEY]
        src = f"khoá số {EPISODE_NUMERIC_KEY}"
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not lo <= v <= hi:
            return None, (f"{where}.{EPISODE_NUMERIC_KEY} phải là số trong [{lo}, {hi}], đọc "
                          f"được {v!r}"), src
        if any(abs(x - v) > EPS for x in in_text):
            return None, (f"{where}: khoá số {EPISODE_NUMERIC_KEY}={v!r} LỆCH với câu chữ "
                          f"trigger={trig!r} ⇒ không biết ngưỡng nào đúng, không chọn hộ"), src
        return float(v), None, src
    src = "chuỗi trigger (chưa có khoá số)"
    if len(found) != 1:
        return None, (f"{where}.trigger phải chứa ĐÚNG MỘT ngưỡng dạng -0.xx (hai chữ số thập "
                      f"phân), đọc được {trig!r}"), src
    v = float(found[0])
    if not lo <= v <= hi:
        return None, (f"{where}.trigger: ngưỡng {v} nằm ngoài khoảng hợp lý [{lo}, {hi}] "
                      f"({trig!r})"), src
    if any(abs(x - v) > EPS for x in in_text):
        return None, (f"{where}.trigger tự mâu thuẫn: ngưỡng số {v} nhưng phần trăm ghi kèm là "
                      f"{stated} ({trig!r})"), src
    return v, None, src


def load_thresholds(rules_path):
    """Trả `(th, errors)`. `errors[brake]` = lý do KHÔNG đọc được ngưỡng của phanh đó — phanh ấy
    thành KHÔNG ĐO ĐƯỢC, không có mặc định ngầm."""
    th = {"drawdown": -DD_THRESHOLD, "daily": None, "episode": None, "lever_package_id": None,
          "episode_source": None}
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
    node = (rules.get("macro_kill_switches") or {}).get("C_episode_drawdown_breaker") or {}
    th["episode"], err, th["episode_source"] = _episode_threshold(
        rules_path, node if isinstance(node, dict) else {})
    if err:
        errors["episode"] = err
    pkg = (rules.get("capit_margin_lever") or {}).get("loan_package_id")
    if isinstance(pkg, bool) or not isinstance(pkg, int):
        errors.setdefault("episode", f"{rules_path}: capit_margin_lever.loan_package_id phải là "
                                     f"số nguyên, đọc được {pkg!r}")
    else:
        th["lever_package_id"] = pkg
    return th, errors


def load_profiles(secrets_path):
    """{label: account_id} từ secrets/trading_bot_accounts.json."""
    with open(secrets_path, encoding="utf-8") as f:
        cfg = json.load(f)
    return {rec["label"]: rec.get("account_id") for rec in cfg.get("accounts", [])
            if rec.get("label")}


# ------------------------------------------------------------------ broker raw (chỉ ĐỌC file)
def _last_positions_by_account(path):
    """{account_no: (list positions | None, ts, mô tả payload)} — bản ghi positions CUỐI CÙNG của
    từng account. list = None khi bản ghi KHÔNG có danh sách `payload.positions` (không đọc được
    ≠ không giữ gì)."""
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if '"positions"' not in line:        # lọc thô cho nhanh; quyết định vẫn ở dưới
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if rec.get("kind") != "positions":
                continue
            payload = rec.get("payload")
            pos = payload.get("positions") if isinstance(payload, dict) else None
            seen = (f"khoá {sorted(payload)}" if isinstance(payload, dict)
                    else f"payload kiểu {type(payload).__name__}")
            out[str(rec.get("account_no"))] = (pos if isinstance(pos, list) else None,
                                               rec.get("ts"), seen)
    return out


def raw_positions(ctx, account_no, date):
    """(list vị thế mở | None, ts, lý do) từ bản ghi positions CUỐI CÙNG của `account_no` trong
    dnse_raw_{date}.jsonl. §12: chỉ lấy bản ghi mang đúng account_no."""
    path = os.path.join(ctx.exec_dir, f"dnse_raw_{date}.jsonl")
    if not os.path.exists(path):
        return None, None, f"không có file {os.path.basename(path)}"
    if ctx.pos_cache is not None and date in ctx.pos_cache:
        by_acc = ctx.pos_cache[date]
    else:
        by_acc = _last_positions_by_account(path)
        if ctx.pos_cache is not None:
            ctx.pos_cache[date] = by_acc
    if str(account_no) not in by_acc:
        return None, None, (f"{os.path.basename(path)} không có bản ghi positions nào của account "
                            f"{account_no}")
    latest, ts, seen = by_acc[str(account_no)]
    if latest is None:
        return None, ts, (f"bản ghi positions cuối cùng của account {account_no} trong "
                          f"{os.path.basename(path)} (chụp {ts!r}) KHÔNG có danh sách "
                          f"payload.positions (đọc được: {seen}) ⇒ không biết đang giữ gì")
    return [p for p in latest if float(p.get("openQuantity") or 0) > 0], ts, None


def close_positions(ctx, account_no, date):
    """Như `raw_positions` nhưng CHỈ nhận danh mục CUỐI PHIÊN: với ngày có phiên, bản ghi cuối
    cùng phải chụp từ giờ đóng cửa trở đi. Chụp sớm hơn ⇒ (None, ts, lý do) — vị thế mua/bán
    trong phiên chưa nằm trong đó, không được coi là "không có"."""
    positions, ts, why = raw_positions(ctx, account_no, date)
    if positions is None:
        return None, ts, why
    t = _parse_ts(ts)
    if is_session(date) and (t is None or t < datetime.datetime.combine(date, SESSION_CLOSE_ICT)):
        return None, ts, (f"bản ghi positions cuối cùng của account {account_no} trong "
                          f"dnse_raw_{date}.jsonl chụp lúc {ts!r} — trước giờ đóng cửa "
                          f"{SESSION_CLOSE_ICT:%H:%M} ⇒ chưa phải danh mục cuối phiên")
    return positions, ts, None


def _pkg_id(x):
    """Mã gói vay đã chuẩn hoá về số nguyên (§28: broker có thể trả 1840, "1840", 1840.0);
    None = không phải số nguyên."""
    try:
        f = float(str(x).strip())
    except ValueError:
        return None
    return int(f) if f == int(f) else None


def lever_positions(ctx, account_no, d, pkg):
    """({symbol: qty} dưới gói vay `pkg` CUỐI PHIÊN d | None, ts, lý do-không-đọc-được)."""
    positions, ts, why = close_positions(ctx, account_no, d)
    if positions is None:
        return None, ts, why
    out = {}
    for p in positions:
        if _pkg_id(p.get("loanPackageId")) == pkg:
            out[p.get("symbol")] = out.get(p.get("symbol"), 0.0) + float(p["openQuantity"])
    return out, ts, None


# ------------------------------------------------------------------ dựng chuỗi giá đơn vị
def build_chain(ctx, account, today):
    """Chuỗi giá đơn vị của NAV toàn tài khoản. Trả dict: ledger | None, error (không dựng nổi
    sổ ⇒ không có số nào), problems[] (sổ dựng được nhưng mọi số chỉ là TẠM TÍNH — sổ dòng tiền
    thiếu/lỗi/còn dòng treo), rows (nav_history), ts{date: balance_ts}, base_date."""
    out = {"ledger": None, "error": None, "problems": [], "rows": [], "ts": {}, "base_date": None}
    try:
        rows = load_nav_history(account, ctx.exec_dir)
        inception = load_inception(account, ctx.inception_path)
        base_date, base_nav = _inception_baseline(rows, inception)
        out.update(rows=rows, base_date=base_date, ts={r[0]: r.balance_ts for r in rows})
        flows, why = [], None
        if not os.path.exists(ctx.flows_path):
            # KHÔNG gợi ý tạo file rỗng: thiếu sổ = không phân biệt được "chưa nạp/rút" với "mất sổ"
            why = (f"KHÔNG có sổ dòng tiền {ctx.flows_path} ⇒ không biết account có nạp/rút hay "
                   f"không (khôi phục file từ bản sao lưu)")
        else:
            try:
                flows = load_flows(account, flows_path=ctx.flows_path, require_file=True,
                                   today=today)
            except Exception as exc:  # §29: lý do = đúng thông điệp lỗi đọc được
                why = f"sổ dòng tiền {ctx.flows_path} không đọc được ({type(exc).__name__}: {exc})"
        ledger, info = build_ledger(rows, flows, base_date, base_nav)
        if why:
            out["problems"].append(("flows", why + " ⇒ số tạm tính KHÔNG trừ nạp/rút nào"))
        if info["pending"]:
            out["problems"].append(("flows", f"{len(info['pending'])} dòng tiền TREO trong "
                                             f"{ctx.flows_path} (chưa dòng NAV nào chụp sau thời "
                                             f"điểm tiền vào/ra) ⇒ số tạm tính chưa tính dòng tiền "
                                             f"đó"))
        out["ledger"] = ledger
    except Exception as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


# ------------------------------------------------------------------ episode đòn bẩy
def load_episodes(ctx):
    data = _read_json(ctx.episodes_path, {"_doc": "Episode đòn bẩy cho phanh −15% "
                                          "(nav_loss_brake_monitor.py). Mở: monitor khi đủ bằng "
                                          "chứng, hoặc người qua --open-episode. Đóng: người, "
                                          "qua --close-episode.",
                                          "episodes": []})
    if not isinstance(data, dict) or not isinstance(data.get("episodes"), list):
        raise ValueError(f"{ctx.episodes_path}: thiếu list 'episodes'")
    return data


def covers(e, d):
    """Episode `e` có hiệu lực ở phiên `d`: từ ngày mở tới HẾT ngày đóng (phiên của chính ngày
    đóng vẫn đo với episode — đóng trước lượt tối không được làm phiên đó thành 'không episode')."""
    return (datetime.date.fromisoformat(e["opened_date"]) <= d
            and (e.get("closed_date") is None
                 or d <= datetime.date.fromisoformat(e["closed_date"])))


def active_episode(episodes, account, d):
    for e in episodes:
        if e["account"] == account and covers(e, d):
            return e
    return None


def load_approvals(ctx, account):
    """([(ngày, bản ghi, path)] tăng dần, ghi chú[]) — mọi bản duyệt margin CỦA `account` (kể cả
    đã thu hồi; người gọi tự lọc). File không đọc được / ghi account khác ⇒ ghi chú, không lấy."""
    out, notes = [], []
    prefix = os.path.join(ctx.approvals_dir, f"margin_approval_{account}_")
    for path in sorted(glob.glob(prefix + "*.json")):
        name = os.path.basename(path)
        try:
            d = datetime.date.fromisoformat(name[len(os.path.basename(prefix)):-5])
            rec = _read_json(path, {})
            if not isinstance(rec, dict):
                raise ValueError(f"nội dung là {type(rec).__name__}, không phải object")
        except ValueError as exc:
            notes.append(f"{name} không đọc được: {exc}")
            continue
        if rec.get("account") != account:
            notes.append(f"{name} ghi account={rec.get('account')!r}, không phải {account!r} — "
                         f"bỏ qua")
            continue
        out.append((d, rec, path))
    return out, notes


def is_revoked(rec):
    return "revoked" in rec and rec.get("revoked") not in NOT_REVOKED


def detect_episode_opens(ctx, account, account_no, pkg, episodes, ledger, upto, approvals):
    """Mở episode khi có ĐỦ bản duyệt + vị thế gói vay thật ở ngày duyệt hoặc phiên kế. Trả
    (episode mới[], ghi chú[]). Không ghi file — người gọi quyết."""
    new, notes = [], []
    dates = [r["date"] for r in ledger]
    for d, rec, path in approvals:
        if d > upto:
            continue
        mine = [e for e in episodes + new if e["account"] == account]
        if any(covers(e, d) for e in mine):
            continue                      # nằm trong một episode — `new_approvals` lo phần nêu ra
        if any(e.get("closed_date") and d < datetime.date.fromisoformat(e["closed_date"])
               for e in mine):
            continue                      # bản duyệt cũ hơn một episode đã đóng
        if is_revoked(rec):
            notes.append(f"bản duyệt margin {d} đã bị thu hồi (revoked={rec.get('revoked')!r}) — "
                         f"không mở episode")
            continue
        cands = [c for c in (d if is_session(d) else next_session(d),) if c <= upto]
        if cands and next_session(cands[0]) <= upto:
            cands.append(next_session(cands[0]))
        opened, unreadable, empty = None, [], []
        for c in cands:
            held, ts, why = lever_positions(ctx, account_no, c, pkg)
            if held is None:              # không đọc được phiên này ⇒ VẪN thử phiên kế
                unreadable.append((c, why))
            elif held:
                opened = (c, held, ts)
                break
            else:
                empty.append(c)
        if opened is None:
            if unreadable:
                notes.append(f"có bản duyệt margin {d} nhưng CHƯA mở được episode: không kiểm được "
                             f"vị thế gói vay {pkg} phiên "
                             + "; ".join(f"{c} ({why})" for c, why in unreadable)
                             + (f"; phiên {', '.join(map(str, empty))} broker không có vị thế gói "
                                f"vay" if empty else "")
                             + " — nếu vị thế đã có thật, mở tay bằng --open-episode")
            else:
                notes.append(f"có bản duyệt margin {d} nhưng broker KHÔNG có vị thế nào dưới gói "
                             f"vay {pkg} cuối phiên "
                             f"{', '.join(str(c) for c in cands) or '(chưa tới)'}"
                             + (" ⇒ mới là ý định, chưa khớp — không mở episode" if len(cands) == 2
                                else " — sẽ kiểm lại ở phiên kế"))
            continue
        c, held, ts = opened
        if active_episode(mine, account, c) is not None:
            continue
        # Phiên trước `c` không đọc được ⇒ vị thế có thể đã có từ phiên đó: điểm vào lấy mốc SỚM
        # nhất có thể, mốc kia giữ làm điểm vào phụ — phanh đo theo mốc XẤU hơn (không chọn hộ).
        first = unreadable[0][0] if unreadable else c
        ref = [x for x in dates if x < first]
        if not ref:
            notes.append(f"bản duyệt margin {d} + vị thế gói vay {pkg} có thật, nhưng chuỗi giá "
                         f"đơn vị không có dòng nào trước {first} để làm điểm vào")
            continue
        alt = sorted({x.isoformat() for x in (max(y for y in dates if y < c),)} - {ref[-1].isoformat()})
        if alt:
            notes.append(f"bản duyệt margin {d}: phiên {first} không đọc được positions "
                         f"({unreadable[0][1]}) ⇒ không biết vị thế gói vay có từ {first} hay {c}; "
                         f"phanh episode đo theo điểm vào XẤU hơn trong hai mốc {ref[-1]} / {alt[0]}")
        new.append({"id": f"{account}-{c}", "account": account, "opened_date": c.isoformat(),
                    "approval_date": d.isoformat(), "entry_ref_date": ref[-1].isoformat(),
                    "entry_ref_alt_dates": alt,
                    "opened_by": "nav_loss_brake_monitor.py",
                    "evidence": {"approval_file": path, "approved_by": rec.get("approved_by"),
                                 "loan_package_id": pkg, "lever_positions": held,
                                 "positions_ts": ts,
                                 "unreadable_sessions": {str(x): w for x, w in unreadable}},
                    "acked_approvals": [],
                    "closed_date": None, "closed_by": None, "close_reason": None})
    return new, notes


def new_approvals(ep, approvals, d):
    """Ngày của các bản duyệt (chưa thu hồi) xuất hiện SAU khi episode `ep` mở, tới hết `d`, mà
    chưa ai xác nhận bằng --ack-approval: mỗi cái có thể là một điểm vào MỚI."""
    lo = max(ep["opened_date"], ep.get("approval_date") or "")
    acked = {a.get("date") for a in ep.get("acked_approvals") or []}
    return [a for a, rec, _ in approvals
            if lo < a.isoformat() <= d.isoformat() and a.isoformat() not in acked
            and not is_revoked(rec)]


def no_guard(pkg):
    return {"held": None, "why": "chưa có mã gói vay để kiểm", "pkg": pkg, "new_approvals": [],
            "approvals": [], "open_notes": []}


def lever_guard(ctx, account, account_no, d, pkg, episodes, approvals, open_notes=()):
    """Bằng chứng cho phanh episode tại phiên `d`: {"held": {sym: qty} | None, "why", "pkg",
    "new_approvals": [ngày], "approvals": [(ngày, đã thu hồi?)] tới hết d, "open_notes": vì sao
    các bản duyệt đó chưa mở được episode (đọc từ `detect_episode_opens`)}."""
    held, _ts, why = lever_positions(ctx, account_no, d, pkg)
    ep = active_episode(episodes, account, d)
    return {"held": held, "why": why, "pkg": pkg,
            "new_approvals": new_approvals(ep, approvals, d) if ep else [],
            "approvals": [(a.isoformat(), is_revoked(rec)) for a, rec, _ in approvals if a <= d],
            "open_notes": list(open_notes)}


# ------------------------------------------------------------------ đánh giá ba phanh
def _res(status, value=None, threshold=None, reason=None, **extra):
    r = {"status": status, "value": value, "threshold": threshold, "reason": reason}
    if value is not None and threshold is not None:
        # khoảng cách tới ngưỡng, điểm phần trăm; <= 0 = đã chạm
        r["distance_pp"] = (value - threshold) * 100
    r.update(extra)
    return r


def _measured(v, th, problems, **extra):
    """Kết quả một phanh ĐÃ CÓ SỐ. `problems`: [(loại, câu)]. Không vướng gì ⇒ BREACH/OK. Có
    vướng ⇒ số chỉ là TẠM TÍNH: đã vượt ngưỡng ⇒ BREACH_PROVISIONAL, chưa vượt ⇒ KHÔNG ĐO ĐƯỢC.
    `quiet` = luật giảm tin: chỉ vướng cờ ước tính VÀ còn cách ngưỡng hơn QUIET_ESTIMATE_MARGIN_PP."""
    hit = v <= th + EPS
    if not problems:
        return _res(BREACH if hit else OK, v, th, **extra)
    seen, texts = set(), []
    for _, t in problems:                 # cùng một dòng NAV có thể vừa là mốc so vừa là điểm vào
        if t not in seen:
            seen.add(t)
            texts.append(t)
    r = _res(BREACH_PROV if hit else UNMEASURABLE, v, th, provisional=True,
             reason="; ".join(texts), **extra)
    if (not hit and {k for k, _ in problems} == {"estimate"}
            and r["distance_pp"] > QUIET_ESTIMATE_MARGIN_PP + EPS * 100):
        r["quiet"] = True
    return r


def _no_threshold(v, why, **extra):
    """Phanh thiếu ngưỡng: KHÔNG ĐO ĐƯỢC, nhưng vẫn kèm số tạm tính nếu có."""
    return _res(UNMEASURABLE, v, reason=why, **({"provisional": True} if v is not None else {}),
                **extra)


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
    last = chain["rows"][-1][0] if chain["rows"] else None
    return (f"nav_history không có dòng {d} (dòng mới nhất: {last}); không thấy file "
            f"nav_gate_block_{account}_{d}.json")


def evaluate(ctx, account, d, chain, th, th_err, episodes, guard):
    """Ba phanh của `account` tại phiên `d`, chỉ dùng dữ liệu có ngày <= d. `guard`: kết quả
    `lever_guard` (bằng chứng broker + bản duyệt cho phanh episode)."""
    res = {}
    block = chain["error"]
    cut = [r for r in (chain["ledger"] or []) if r["date"] <= d]
    row = cut[-1] if len(cut) > 1 and cut[-1]["date"] == d else None
    if not block and row is None:
        if cut and cut[-1]["date"] == d:
            block = (f"phiên {d} là dòng ĐẦU TIÊN của chuỗi giá đơn vị — chưa có dòng nào trước "
                     f"nó để so")
        else:
            block = _missing_row_reason(ctx, account, d, chain)
    if block:                             # sổ không có dòng NAV của phiên ⇒ không có số nào
        for b in BRAKES:
            res[b] = _res(UNMEASURABLE, threshold=th.get(b), reason=th_err.get(b) or block)
        return res

    def flaws(r):
        """Vì sao dòng sổ `r` chưa phải giá chốt đã kiểm (rỗng = dùng được). Mốc khởi điểm của
        account là số KHAI trong account_inception.json, không có giờ chụp để kiểm."""
        out = []
        if r["date"] != chain["base_date"]:
            p = close_capture_problem(r["date"], chain["ts"].get(r["date"]))
            if p:
                out.append(("capture", p))
        if r["nav_is_estimate"]:
            out.append(("estimate", f"dòng NAV {r['date']} mang cờ nav_is_estimate (backfill "
                                    f"ước tính)"))
        return out

    base = chain["problems"] + flaws(row)
    # --- lỗ một ngày
    # Mốc so = giá chốt của phiên liền trước. nav_history có cả dòng của ngày NGHỈ (cron vẫn chạy,
    # vd 2026-08-31): dòng đó mang đúng giá chốt phiên trước + lãi tiền gửi, nên khi không có dòng
    # đúng ngày phiên trước thì một dòng ngày nghỉ nằm SAU nó vẫn là mốc hợp lệ.
    want = prev_session(d)
    prev = next((r for r in cut[:-1] if r["date"] == want), cut[-2])
    v = row["unit_price"] / prev["unit_price"] - 1
    if "daily" in th_err:
        res["daily"] = _no_threshold(v, th_err["daily"])
    else:
        probs = []
        if prev["date"] < want:
            probs.append(("gap", f"thiếu dòng của phiên liền trước {want}: dòng trước {d} trong "
                                 f"chuỗi là {prev['date']} ⇒ con số là gộp nhiều phiên"))
        res["daily"] = _measured(v, th["daily"], probs + base + flaws(prev))
    # --- lỗ từ đỉnh
    peak = max(cut, key=lambda r: r["unit_price"])
    v = row["unit_price"] / peak["unit_price"] - 1
    res["drawdown"] = _measured(v, -DD_THRESHOLD, base, peak_date=peak["date"].isoformat(),
                                peak_unit_price=peak["unit_price"])
    if peak is not row and flaws(peak):
        res["drawdown"]["note"] = ("đỉnh chưa phải giá chốt đã kiểm: "
                                   + "; ".join(t for _, t in flaws(peak)))
    # --- lỗ từ điểm vào episode
    held, pkg = guard["held"], guard["pkg"]
    ep = active_episode(episodes, account, d)
    v, extra, entries, missing = None, {}, [], []
    if ep is not None:
        extra = {"episode_id": ep["id"], "entry_ref_date": ep["entry_ref_date"]}
        for x in [ep["entry_ref_date"]] + list(ep.get("entry_ref_alt_dates") or []):
            e = next((r for r in cut if r["date"].isoformat() == x), None)
            (entries if e else missing).append(e or x)
        if entries and not missing[:1] == [ep["entry_ref_date"]]:
            v = min(row["unit_price"] / e["unit_price"] - 1 for e in entries)
    if "episode" in th_err:
        res["episode"] = _no_threshold(v, th_err["episode"], **extra)
        return res
    if ep is None:
        if held is None:
            res["episode"] = _res(
                UNMEASURABLE, threshold=th["episode"],
                reason=(f"không có episode nào đang mở, nhưng KHÔNG kiểm được broker có vị thế "
                        f"dưới gói vay {pkg} cuối phiên {d} hay không: {guard['why']}"))
        elif held:
            # vị thế gói vay có thật mà không có episode ⇒ phanh −15% đang không canh gì: nói to.
            # §29: câu về bản duyệt đọc từ đúng danh sách bản duyệt + ghi chú dò mở, không đoán.
            seen = guard["approvals"]
            about = (("bản duyệt margin đọc được tới phiên này: "
                      + ", ".join(a + (" (đã thu hồi)" if rv else "") for a, rv in seen)
                      + " — chưa bản nào mở được episode"
                      + (": " + "; ".join(guard["open_notes"]) if guard["open_notes"] else ""))
                     if seen else
                     f"không thấy bản duyệt margin nào của {account} có ngày <= {d} trong "
                     f"{ctx.approvals_dir}")
            res["episode"] = _res(
                UNMEASURABLE, threshold=th["episode"],
                reason=(f"broker có vị thế dưới gói vay {pkg} ngày {d} "
                        f"({', '.join(f'{k} {vnd(q)}' for k, q in sorted(held.items()))}) nhưng "
                        f"KHÔNG có episode nào đang mở; {about} — xác minh rồi mở tay bằng "
                        f"--open-episode"))
        else:
            res["episode"] = _res(NO_EPISODE, threshold=th["episode"],
                                  reason="không có episode đòn bẩy nào đang mở")
        return res
    if v is None:
        res["episode"] = _res(UNMEASURABLE, threshold=th["episode"], **extra,
                              reason=f"episode {ep['id']}: chuỗi giá đơn vị không có dòng của điểm "
                                     f"vào {ep['entry_ref_date']}")
        return res
    probs = list(base)
    for e in entries:                     # điểm vào cũng phải là giá chốt đã kiểm
        probs += flaws(e)
    for x in missing:
        probs.append(("entry", f"episode {ep['id']}: chuỗi giá đơn vị không có dòng của điểm vào "
                               f"phụ {x}"))
    if held is None:
        probs.append(("broker", f"không kiểm được vị thế gói vay {pkg} cuối phiên {d}: "
                                f"{guard['why']}"))
    elif not held and ep.get("closed_date") != d.isoformat():
        probs.append(("broker", f"episode {ep['id']} đang mở nhưng broker KHÔNG còn vị thế nào "
                                f"dưới gói vay {pkg} cuối phiên {d} ⇒ đã tất toán? Đóng bằng "
                                f"--close-episode (một lần vay mới sau đó sẽ có điểm vào KHÁC)"))
    ref = ep["entry_ref_date"]
    for a in guard["new_approvals"]:
        alt = [r for r in cut if r["date"] < a]
        v_alt = row["unit_price"] / alt[-1]["unit_price"] - 1 if alt else None
        probs.append(("approval",
                      f"có bản duyệt margin MỚI ngày {a} trong lúc episode {ep['id']} còn mở ⇒ "
                      f"điểm vào có thể đã đổi (tính từ điểm vào gốc {ref}: {pct(v)}"
                      + (f"; tính từ chốt {alt[-1]['date']} trước bản duyệt mới: {pct(v_alt)}"
                         if alt else "")
                      + ") — cùng episode thì --ack-approval, vay mới thì --close-episode rồi "
                        "--open-episode"))
        if v_alt is not None:
            v = min(v, v_alt)             # số đem so ngưỡng = trường hợp XẤU nhất
    res["episode"] = _measured(v, th["episode"], probs, **extra)
    if len(entries) > 1:
        res["episode"]["note"] = ("số đo = điểm vào XẤU hơn trong các mốc "
                                  + " / ".join(e["date"].isoformat() for e in entries)
                                  + " (lúc mở không đọc được positions của phiên giữa)")
    if ep.get("closed_date") == d.isoformat():
        res["episode"]["note"] = ((res["episode"].get("note", "") + "; ").lstrip("; ")
                                  + f"episode đã được đóng tay trong ngày {d} (bởi "
                                    f"{ep.get('closed_by')}) — phiên này vẫn đo")
    return res


# ------------------------------------------------------------------ lệnh tay của người (K2)
def recent_actions(ctx, account, d):
    """Ghi chú về các lệnh tay ghi state của `account` kể từ lượt đo phiên trước (sau
    NAV_EXPECTED_AFTER_ICT của phiên liền trước `d`) — để lượt đo kế LUÔN nêu ra: một lệnh tay có
    thể làm monitor xanh. Sổ không đọc được ⇒ nói đúng lỗi (§29), không coi là 'không có lệnh'."""
    if not os.path.exists(ctx.actions_path):
        return []
    since = datetime.datetime.combine(prev_session(d), NAV_EXPECTED_AFTER_ICT)
    out = []
    try:
        with open(ctx.actions_path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                at = _parse_ts(rec.get("at"))
                if rec.get("account") == account and at is not None and at > since:
                    out.append(f"LỆNH TAY {rec.get('cmd')} lúc {rec.get('at')} bởi {rec.get('by')} "
                               f"— lý do: {rec.get('reason')} · trước: {rec.get('before')} · sau: "
                               f"{rec.get('after')}")
    except (OSError, ValueError) as exc:
        out.append(f"sổ lệnh tay {ctx.actions_path} không đọc được ({type(exc).__name__}: {exc}) "
                   f"⇒ không biết có lệnh tay nào vừa đổi state hay không")
    return out


def announce_action(ctx, cmd, account, by, reason, before, after):
    """Sau khi một lệnh tay ĐÃ ghi state: ghi một dòng vào sổ lệnh tay rồi gửi MỘT dòng vào
    trading_daily. Trả mã thoát: 0, hoặc 3 khi không ghi được sổ / không gửi được tin (state đã
    đổi rồi — lượt đo kế vẫn nêu lệnh này nếu sổ ghi được)."""
    rec = {"at": ctx.now.isoformat(timespec="seconds"), "cmd": cmd, "account": account,
           "by": by.strip(), "reason": reason.strip(), "before": before, "after": after}
    rc = 0
    try:
        os.makedirs(ctx.state_dir, exist_ok=True)
        with open(ctx.actions_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError as exc:
        print(f"❌ không ghi được {ctx.actions_path}: {type(exc).__name__}: {exc}", file=sys.stderr)
        rc = 3
    text = (f"📝 PHANH LỖ NAV — LỆNH TAY {cmd} · {account} · bởi {rec['by']} · lý do: "
            f"{rec['reason']}\n• trước: {before}\n• sau: {after}")
    ok, detail, _sink = send_alert(ctx, text)
    if not ok:
        print(f"❌ state ĐÃ ghi nhưng KHÔNG gửi được dòng báo lệnh tay vào {NOTIFY_CHANNEL} — "
              f"{detail}", file=sys.stderr)
        rc = 3
    return rc


# ------------------------------------------------------------------ chạy cho một account
def run_account(ctx, account, account_no, d, th, th_err, episodes_data, record=True):
    """Trả dict trạng thái của account tại phiên `d`. `record=True` mới ghi episode tự mở (chạy
    thật); False = chỉ đọc (chạy khô / replay). `episodes_data` None = sổ episode không đọc được
    (lý do đã nằm trong `th_err["episode"]`) ⇒ không dò mở, không ghi."""
    notes = recent_actions(ctx, account, d)
    chain = build_chain(ctx, account, ctx.now.astimezone(ICT).date())
    episodes = episodes_data["episodes"] if episodes_data else []
    pkg = th.get("lever_package_id")
    guard = no_guard(pkg)
    if pkg is not None:
        approvals, ap_notes = load_approvals(ctx, account)
        notes += ap_notes
        ep_notes = []
        if chain["ledger"] and episodes_data:
            new, ep_notes = detect_episode_opens(ctx, account, account_no, pkg, episodes,
                                                 chain["ledger"], d, approvals)
            notes += ep_notes
            if new:
                episodes = episodes + new
                if record:
                    episodes_data["episodes"] = episodes
                    _write_json_atomic(ctx.episodes_path, episodes_data)
                notes += [f"MỞ episode {e['id']} (điểm vào {e['entry_ref_date']})" for e in new]
        guard = lever_guard(ctx, account, account_no, d, pkg, episodes, approvals, ep_notes)
    res = evaluate(ctx, account, d, chain, th, th_err, episodes, guard)
    cut = [r for r in (chain["ledger"] or []) if r["date"] <= d]
    row = cut[-1] if cut and cut[-1]["date"] == d else None
    return {"session": d.isoformat(), "nav": row["nav"] if row else None,
            "unit_price": row["unit_price"] if row else None,
            "brakes": res, "notes": notes,
            "overall": worst([res[b]["status"] for b in BRAKES])}


def worst(statuses):
    for s in ALERTING:
        if s in statuses:
            return s
    return OK


def pushes(res):
    """Các phanh PHẢI đẩy tin tối: đang kêu và không thuộc luật giảm tin."""
    return [b for b in BRAKES if res[b]["status"] in ALERTING and not res[b].get("quiet")]


def failed_account_state(d, th, why):
    """Trạng thái của một account mà monitor KHÔNG đo nổi vì chính nó lỗi (§29: `why` = lỗi thật)."""
    return {"session": d.isoformat(), "nav": None, "unit_price": None,
            "brakes": {b: _res(UNMEASURABLE, threshold=th.get(b), reason=why) for b in BRAKES},
            "notes": [], "overall": UNMEASURABLE, "monitor_error": True}


# ------------------------------------------------------------------ cảnh báo (idempotent §5)
def brake_line(b, r):
    name = BRAKE_VI[b]
    note = f" · ⚠ {r['note']}" if r.get("note") else ""
    if r["status"] == NO_EPISODE:
        return f"{name}: không có episode đang mở (ngưỡng {pct(r['threshold'], 0)})"
    if r["status"] == UNMEASURABLE:
        tmp = ""
        if r.get("value") is not None:
            tmp = f" · tạm tính {pct(r['value'])}" + (
                f" (ngưỡng {pct(r['threshold'], 0)})" if r.get("threshold") is not None else "")
        quiet = ""
        if r.get("quiet"):
            quiet = (f" · KHÔNG đẩy tin tối (chỉ vướng cờ ước tính, còn cách ngưỡng "
                     f"{r['distance_pp']:.2f}pp > {QUIET_ESTIMATE_MARGIN_PP:.1f}pp)").replace(".", ",")
        return f"{name}: KHÔNG ĐO ĐƯỢC — {r['reason']}{tmp}{quiet}{note}"
    dist = f"{abs(r['distance_pp']):.2f}pp".replace(".", ",")
    more = f", đỉnh {r['peak_date']}" if b == "drawdown" else (
        f", điểm vào {r['entry_ref_date']}" if b == "episode" else "")
    if r["status"] == BREACH_PROV:
        return (f"{name}: TẠM TÍNH {pct(r['value'])} ĐÃ VƯỢT ngưỡng {pct(r['threshold'], 0)} "
                f"(vượt {dist}{more}) — chưa phải số chốt: {r['reason']}{note}")
    tail = f"cách {dist}" if r["status"] == OK else f"ĐÃ CHẠM, vượt {dist}"
    return f"{name}: {pct(r['value'])} (ngưỡng {pct(r['threshold'], 0)}, {tail}{more}){note}"


def brake_lines(res, mark=False):
    """Ba dòng (hoặc MỘT dòng khi cả ba phanh bị chặn bởi cùng một lý do, không có số nào)."""
    icon = {BREACH: "🔴 ", BREACH_PROV: "🔴 ", UNMEASURABLE: "🟡 "}
    if (all(res[b]["status"] == UNMEASURABLE and res[b].get("value") is None for b in BRAKES)
            and len({res[b]["reason"] for b in BRAKES}) == 1):
        return [f"{icon[UNMEASURABLE] if mark else ''}Cả 3 phanh: KHÔNG ĐO ĐƯỢC — "
                f"{res['daily']['reason']}"]
    return [(icon.get(res[b]["status"], "🟢 ") if mark else "") + brake_line(b, res[b])
            for b in BRAKES]


def alert_text(account, st):
    lines = []
    statuses = [st["brakes"][b]["status"] for b in BRAKES]
    if BREACH in statuses:
        head = "🚨 PHANH LỖ NAV ĐÃ CHẠM"
    elif BREACH_PROV in statuses:
        head = "🚨 PHANH LỖ NAV — SỐ TẠM TÍNH ĐÃ VƯỢT NGƯỠNG (chưa phải số chốt)"
    else:
        head = "⚠️ PHANH LỖ NAV — KHÔNG ĐO ĐƯỢC"
    lines.append(f"{head} — {account} · phiên {st['session']} · đo trên {BASIS_VI}")
    lines += brake_lines(st["brakes"], mark=True)
    for w in st["notes"]:
        lines.append(f"• {w}")
    if BREACH in statuses or BREACH_PROV in statuses:
        lines.append("Monitor CHỈ CẢNH BÁO: không dừng bot, không huỷ lệnh. Nếu anh/chị quyết định "
                     "dừng giao dịch, tự chạy:")
        lines.append(f"`touch {os.path.join(WC_ROOT, 'data', 'BOT_STOP')}`")
    else:
        lines.append("Không đo được KHÔNG có nghĩa là an toàn — cần người xem lý do ở trên.")
    return "\n".join(lines)


def send_alert(ctx, text):
    """(ok, chi tiết, sink | None). Selfcheck/chạy thử đặt MIKE_LOSS_BRAKE_ALERT_SINK=<file> ⇒
    không chạm mạng. Trên state SỐNG, tin đi vào sink KHÔNG được tính là đã gửi (ok=False): biến
    môi trường lọt vào cron không được làm cảnh báo im mà vẫn ghi khoá chống-trùng."""
    sink = os.environ.get(SINK_ENV)
    if sink:
        with open(sink, "a", encoding="utf-8") as f:
            f.write(json.dumps({"channel": NOTIFY_CHANNEL, "text": text}, ensure_ascii=False) + "\n")
        if ctx.is_live:
            return False, (f"tin CHỈ đi vào file sink {sink} (biến {SINK_ENV} đang đặt trên state "
                           f"sống) — CHƯA tới Discord, không ghi dấu đã gửi"), sink
        return True, f"sink {sink}", sink
    if not ctx.is_live:
        return False, (f"TỪ CHỐI gửi Discord thật: đang chạy với thư mục dữ liệu/state không phải "
                       f"mặc định và chưa đặt {SINK_ENV}"), None
    try:
        r = subprocess.run([os.path.join(BIN, "notify_thread.sh"), text, NOTIFY_CHANNEL],
                           capture_output=True, text=True, timeout=180)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"{type(exc).__name__}: {exc}", None
    return r.returncode == 0, (f"notify_thread.sh rc={r.returncode} "
                               f"{(r.stderr or r.stdout or '').strip()[-300:]}"), None


def send_once(ctx, keys, make_text):
    """Gửi MỘT tin nếu trong `keys` có khoá CHƯA từng gửi. Ghi dấu NGAY sau khi gửi được (trước
    khi làm bất cứ gì khác). Sổ đã-gửi hỏng ⇒ coi như chưa gửi gì và VẪN gửi (thà trùng còn hơn
    im), cất file hỏng sang `.corrupt.*`. Gửi lỗi ⇒ không ghi dấu ⇒ lượt sau cùng phiên thử lại."""
    out = {"keys": keys, "new": [], "sent_now": False, "send_error": None, "ledger_error": None,
           "sink": None}
    if not keys:
        return out
    sent = {}
    try:
        sent = _read_json(ctx.sent_path, {})
        if not isinstance(sent, dict):
            raise ValueError(f"nội dung là {type(sent).__name__}, không phải object")
    except (OSError, ValueError) as exc:
        sent = {}
        out["ledger_error"] = (f"sổ đã-gửi {ctx.sent_path} không đọc được ({type(exc).__name__}: "
                               f"{exc}) ⇒ coi như CHƯA gửi gì — tin này có thể trùng")
    out["new"] = [k for k in keys if k not in sent]
    if not out["new"]:
        return out
    text = make_text()
    if out["ledger_error"]:
        text += f"\n• {out['ledger_error']}"
    ok, detail, out["sink"] = send_alert(ctx, text)
    if not ok:
        out["send_error"] = detail
        return out
    out["sent_now"] = True
    stamp = datetime.datetime.now(ICT)
    try:
        if out["ledger_error"] and os.path.exists(ctx.sent_path):
            os.replace(ctx.sent_path, f"{ctx.sent_path}.corrupt.{stamp:%Y%m%dT%H%M%S}")
        sent.update({k: stamp.isoformat(timespec="seconds") for k in out["new"]})
        _write_json_atomic(ctx.sent_path, sent)
    except OSError as exc:
        out["ledger_error"] = (f"ĐÃ gửi nhưng không ghi được dấu vào {ctx.sent_path} "
                               f"({type(exc).__name__}: {exc}) ⇒ lượt sau sẽ gửi lại")
    return out


def dispatch_alerts(ctx, account, st):
    """Gửi MỘT tin cho account nếu có phát hiện CHƯA từng gửi của phiên này. Khoá chống-trùng
    mang cả TRẠNG THÁI ⇒ KHÔNG ĐO ĐƯỢC rồi mới thành TẠM TÍNH VƯỢT NGƯỠNG là một tin mới. Phanh
    thuộc luật giảm tin (`quiet`) không tạo khoá ⇒ không tự nó đẩy tin."""
    res = st["brakes"]
    keys = [f"{account}|{st['session']}|{b}|{res[b]['status']}" for b in pushes(res)]
    out = send_once(ctx, keys, lambda: alert_text(account, st))
    out["suppressed"] = [b for b in BRAKES if res[b].get("quiet")]
    return out


# ------------------------------------------------------------------ dòng cho ops_health_check
def health_line(ctx, account):
    """(rc, dòng). rc=0: file trạng thái ĐÚNG phiên phải có và account OK. rc=1: có phanh không
    đo được. rc=HEALTH_RC_BREACH (5): có phanh CHẠM / tạm tính vượt ngưỡng (rc 1 và 5 là việc của
    NGƯỜI — monitor chỉ cảnh báo). rc=2: monitor không chạy — file thiếu, cũ, hỏng. rc=3: monitor
    có chạy nhưng LỖI — tự nó hỏng, hoặc không gửi được cảnh báo (rc=2 và rc=3 là việc của vận
    hành). §14: độ tươi kiểm bằng PHIÊN ghi trong file so với lịch, không mtime."""
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
        if st.get("error"):
            return 3, (f"Phanh lỗ NAV [{account}]: ❌ MONITOR LỖI phiên {want} — {st['error']} "
                       f"(phanh lỗ đêm đó không ai canh)")
        return 2, (f"Phanh lỗ NAV [{account}]: file trạng thái phiên {want} không có account này "
                   f"(có: {sorted(st.get('accounts') or {})})")
    body = " · ".join(brake_lines(a["brakes"]))
    alert = a.get("alert") or {}
    if alert.get("send_error"):
        body += f" · ❌ GỬI CẢNH BÁO LỖI: {alert['send_error']}"
    broken = a.get("monitor_error") or st.get("error") or alert.get("send_error")
    if broken:
        rc = 3
    elif a["overall"] in (BREACH, BREACH_PROV):
        rc = HEALTH_RC_BREACH
    else:
        rc = 0 if a["overall"] == OK else 1
    return rc, (f"Phanh lỗ NAV [{account}] phiên {want:%d/%m} ({BASIS_VI}): "
                + ("❌ MONITOR LỖI — " if a.get("monitor_error") or st.get("error") else "") + body)


# ------------------------------------------------------------------ replay toàn lịch sử
def replay(ctx, accounts, profiles, th, th_err):
    """Chạy thử: với MỖI phiên từ mốc khởi điểm tới dòng NAV mới nhất, monitor sẽ nói gì nếu chạy
    tối hôm đó trên dữ liệu ĐANG CÓ. Không ghi, không gửi. Mỗi nhóm phiên mang nhãn [ĐẨY TIN] hoặc
    [không đẩy — luật giảm tin]."""
    eps = load_episodes(ctx)
    ctx.pos_cache = {}
    rc = 0
    pkg = th.get("lever_package_id")
    for account in accounts:
        today = ctx.now.astimezone(ICT).date()
        account_no = profiles[account]
        chain = build_chain(ctx, account, today)
        print(f"\n=== {account} · đo trên {BASIS_VI} ===")
        if chain["error"]:
            print(f"  KHÔNG dựng được chuỗi: {chain['error']}")
            rc = 1
            continue
        for _, w in chain["problems"]:
            print(f"  ⚠ {w}")
        led = chain["ledger"]
        approvals, notes = load_approvals(ctx, account) if pkg is not None else ([], [])
        new, ep_notes = detect_episode_opens(ctx, account, account_no, pkg, eps["episodes"], led,
                                             led[-1]["date"], approvals) if pkg is not None else ([], [])
        episodes = eps["episodes"] + new
        for n in notes + ep_notes + [f"episode sẽ mở: {e['id']} (điểm vào {e['entry_ref_date']})"
                                     for e in new]:
            print(f"  • {n}")
        d, last = led[0]["date"], chain["rows"][-1][0]
        n_ok = n_days = n_push = 0
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
            guard = (lever_guard(ctx, account, account_no, d, pkg, episodes, approvals, ep_notes)
                     if pkg is not None else no_guard(pkg))
            res = evaluate(ctx, account, d, chain, th, th_err, episodes, guard)
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
            push = bool(pushes(res))
            n_push += push
            tag = "[ĐẨY TIN] " if push else "[không đẩy — luật giảm tin] "
            msg = tag + "\n".join(
                [x for x in brake_lines(res) if "KHÔNG ĐO ĐƯỢC" in x or "ĐÃ" in x])
            if run and run[0] == msg:
                run[2], run[3] = d, run[3] + 1
            else:
                flush()
                run.extend([msg, d, d, 1])
        flush()
        print(f"  — {n_days} phiên, {n_ok} phiên im lặng, {n_days - n_ok} phiên có phanh không OK: "
              f"TRƯỚC luật giảm tin đẩy {n_days - n_ok} tin · SAU luật giảm tin đẩy {n_push} tin "
              f"({n_days - n_ok - n_push} phiên chỉ hiện ở status + dòng kiểm sáng).")
        print(f"  — ngày giảm mạnh nhất (đo được): {pct(worst_day[0])} ngày {worst_day[1]} · "
              f"sâu nhất từ đỉnh: {pct(worst_dd[0])} ngày {worst_dd[1]}")
        st = run_account(ctx, account, account_no, last, th, th_err, {"episodes": episodes},
                         record=False)
        print(f"  — dòng mới nhất {last}: " + " · ".join(brake_lines(st["brakes"])))
        day = min(((b["unit_price"] / a["unit_price"] - 1, b["date"]) for a, b in zip(led, led[1:])))
        peak, dd = led[0]["unit_price"], (0.0, None)
        for r in led:
            peak = max(peak, r["unit_price"])
            dd = min(dd, (r["unit_price"] / peak - 1, r["date"]), key=lambda x: x[0])
        print(f"  — cả lịch sử, dòng-so-dòng (kể cả dòng ước tính / chụp lệch giờ): ngày giảm mạnh "
              f"nhất {pct(day[0])} ngày {day[1]} · sâu nhất từ đỉnh {pct(dd[0])} ngày {dd[1]}")
    return rc


# ------------------------------------------------------------------ việc của NGƯỜI (có khoá)
def _need(flag, **fields):
    """True nếu mọi trường bắt buộc đều có chữ; thiếu ⇒ in ❌ nêu tên cờ còn thiếu."""
    missing = [k for k, v in fields.items() if not (v or "").strip()]
    if missing:
        print(f"❌ {flag} cần " + " và ".join("--" + k.replace("_", "-") for k in missing)
              + " (ai làm, vì sao).", file=sys.stderr)
    return not missing


def _ep_brief(ep):
    return (f"episode {ep['id']} mở {ep['opened_date']}, điểm vào {ep['entry_ref_date']}, "
            + (f"đóng {ep['closed_date']}" if ep.get("closed_date") else "ĐANG MỞ")
            + f", bản duyệt đã ack: {[a.get('date') for a in ep.get('acked_approvals') or []]}")


def close_episode(ctx, account, closed_by, reason):
    if not _need("--close-episode", closed_by=closed_by, reason=reason):
        return 2
    data = load_episodes(ctx)
    today = ctx.now.astimezone(ICT).date()
    ep = next((e for e in data["episodes"] if e["account"] == account
               and e.get("closed_date") is None), None)
    if ep is None:
        print(f"❌ {account}: không có episode nào đang mở trong {ctx.episodes_path}.",
              file=sys.stderr)
        return 1
    before = _ep_brief(ep)
    ep.update(closed_date=today.isoformat(), closed_by=closed_by.strip(),
              close_reason=reason.strip())
    _write_json_atomic(ctx.episodes_path, data)
    print(f"Đã đóng episode {ep['id']} — hết hiệu lực SAU phiên {today} (phiên {today} vẫn đo với "
          f"episode; bởi {closed_by}).")
    return announce_action(ctx, "--close-episode", account, closed_by, reason, before,
                           _ep_brief(ep) + f" — phanh episode thôi đo từ phiên sau {today}")


def open_episode(ctx, account, opened_date, entry_ref_date, opened_by, reason):
    """Mở tay một episode — cho ca monitor không tự mở được (không có bản duyệt, vị thế xuất hiện
    muộn hơn phiên kế…). Điểm vào mặc định = dòng cuối của chuỗi TRƯỚC ngày mở."""
    if not _need("--open-episode", opened_date=opened_date, opened_by=opened_by, reason=reason):
        return 2
    today = ctx.now.astimezone(ICT).date()
    try:
        opened = datetime.date.fromisoformat(opened_date)
        ref = datetime.date.fromisoformat(entry_ref_date) if entry_ref_date else None
    except ValueError as exc:
        print(f"❌ --open-episode: ngày không đọc được ({exc}).", file=sys.stderr)
        return 2
    if opened > today or (ref is not None and ref >= opened):
        print(f"❌ --open-episode: ngày mở {opened} không được ở tương lai (hôm nay {today}) và "
              f"điểm vào ({ref}) phải TRƯỚC ngày mở.", file=sys.stderr)
        return 2
    profiles = load_profiles(ctx.secrets_path)
    if account not in profiles:
        print(f"❌ {account} không có trong {ctx.secrets_path}.", file=sys.stderr)
        return 2
    data = load_episodes(ctx)
    if any(e["account"] == account and e.get("closed_date") is None for e in data["episodes"]):
        print(f"❌ {account}: đang có một episode mở — đóng nó trước (--close-episode).",
              file=sys.stderr)
        return 1
    chain = build_chain(ctx, account, today)
    dates = [r["date"] for r in chain["ledger"] or []]
    if ref is None:
        before = [x for x in dates if x < opened]
        if not before:
            print(f"❌ {account}: không tìm được điểm vào trước {opened} trong chuỗi giá đơn vị "
                  f"({chain['error'] or 'chuỗi không có dòng nào trước ngày đó'}) — truyền "
                  f"--entry-ref-date.", file=sys.stderr)
            return 1
        ref = before[-1]
    elif dates and ref not in dates:
        print(f"❌ {account}: chuỗi giá đơn vị không có dòng {ref} để làm điểm vào.",
              file=sys.stderr)
        return 1
    eid = f"{account}-{opened}"
    if any(e["id"] == eid for e in data["episodes"]):
        eid += f"-m{sum(1 for e in data['episodes'] if e['id'].startswith(eid))}"
    ep = {"id": eid, "account": account, "opened_date": opened.isoformat(), "approval_date": None,
          "entry_ref_date": ref.isoformat(), "entry_ref_alt_dates": [],
          "opened_by": opened_by.strip(),
          "evidence": {"manual": True, "reason": reason.strip(),
                       "recorded_at": ctx.now.isoformat(timespec="seconds")},
          "acked_approvals": [], "closed_date": None, "closed_by": None, "close_reason": None}
    data["episodes"].append(ep)
    _write_json_atomic(ctx.episodes_path, data)
    print(f"Đã mở episode {eid} từ {opened}, điểm vào = giá chốt {ref} (bởi {opened_by}).")
    return announce_action(ctx, "--open-episode", account, opened_by, reason,
                           "không có episode nào đang mở", _ep_brief(ep))


def ack_approval(ctx, account, approval_date, acked_by, reason):
    """Xác nhận một bản duyệt MỚI thuộc CÙNG episode đang mở (giải ngân thêm, không phải lần vay
    mới) ⇒ phanh episode đo tiếp từ điểm vào cũ. Bản duyệt phải CÓ THẬT và không ở tương lai."""
    if not _need("--ack-approval", approval_date=approval_date, acked_by=acked_by, reason=reason):
        return 2
    today = ctx.now.astimezone(ICT).date()
    try:
        d = datetime.date.fromisoformat(approval_date)
    except ValueError as exc:
        print(f"❌ --ack-approval: --approval-date không đọc được ({exc}).", file=sys.stderr)
        return 2
    if d > today:
        print(f"❌ --ack-approval: ngày bản duyệt {d} ở TƯƠNG LAI (hôm nay {today}) — không xác "
              f"nhận trước một bản duyệt chưa tới.", file=sys.stderr)
        return 2
    approvals, notes = load_approvals(ctx, account)
    if d not in [a for a, _, _ in approvals]:
        print(f"❌ --ack-approval: không có bản duyệt margin đọc được của {account} ngày {d} trong "
              f"{ctx.approvals_dir} (đang có: {[str(a) for a, _, _ in approvals] or 'không bản nào'}"
              + (f"; {'; '.join(notes)}" if notes else "") + ").", file=sys.stderr)
        return 1
    data = load_episodes(ctx)
    ep = next((e for e in data["episodes"] if e["account"] == account
               and e.get("closed_date") is None), None)
    if ep is None:
        print(f"❌ {account}: không có episode nào đang mở trong {ctx.episodes_path}.",
              file=sys.stderr)
        return 1
    before = _ep_brief(ep)
    ep.setdefault("acked_approvals", []).append(
        {"date": d.isoformat(), "acked_by": acked_by.strip(), "reason": reason.strip(),
         "recorded_at": ctx.now.isoformat(timespec="seconds")})
    _write_json_atomic(ctx.episodes_path, data)
    print(f"Đã xác nhận bản duyệt {d} thuộc episode {ep['id']} (bởi {acked_by}).")
    return announce_action(ctx, "--ack-approval", account, acked_by, reason, before,
                           _ep_brief(ep) + f" — bản duyệt {d} KHÔNG còn làm phanh episode thành "
                                           f"tạm tính; đo tiếp từ điểm vào cũ")


# ------------------------------------------------------------------ main
def _status_skeleton(ctx, d, th, th_err):
    return {"schema": STATUS_SCHEMA, "generated_at": ctx.now.isoformat(timespec="seconds"),
            "session": d.isoformat(), "error": None, "basis": BASIS_VI,
            "thresholds": {"daily": th["daily"], "drawdown": th["drawdown"],
                           "episode": th["episode"], "errors": th_err,
                           "quiet_estimate_margin_pp": QUIET_ESTIMATE_MARGIN_PP,
                           "sources": {"daily": "trading_rules.json risk_circuit_breakers."
                                                "daily_loss_limit_pct",
                                       "drawdown": "hằng số DD_THRESHOLD (risk_monitor.py:46)",
                                       "episode": "trading_rules.json macro_kill_switches."
                                                  "C_episode_drawdown_breaker — "
                                                  f"{th.get('episode_source')}"}},
            "accounts": {}}


def _log_run(ctx, d, rc, status):
    """Một dòng mỗi lượt chạy thật — bằng chứng monitor CÓ chạy (ai cần đối chiếu với cron)."""
    try:
        os.makedirs(ctx.state_dir, exist_ok=True)
        with open(ctx.run_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "at": ctx.now.isoformat(timespec="seconds"), "session": d.isoformat(), "rc": rc,
                "overall": status.get("overall"), "error": status.get("error"),
                "accounts": {a: s["overall"] for a, s in status["accounts"].items()},
                "sent": sorted(a for a, s in status["accounts"].items()
                               if (s.get("alert") or {}).get("sent_now")),
                "suppressed": sorted(a for a, s in status["accounts"].items()
                                     if (s.get("alert") or {}).get("suppressed"))},
                ensure_ascii=False) + "\n")
    except OSError as exc:
        print(f"❌ không ghi được {ctx.run_log_path}: {type(exc).__name__}: {exc}", file=sys.stderr)


def run(ctx, args, d, dry):
    """Một lượt đo. `dry` = chỉ in: không mở episode, không ghi status, không gửi."""
    profiles = load_profiles(ctx.secrets_path)
    accounts = args.account or [k for k in _read_json(ctx.inception_path, {})
                                if not k.startswith("_")]
    missing = [a for a in accounts if not profiles.get(a)]
    if missing or not accounts:
        raise ConfigError(f"account {missing or '(rỗng)'} không có trong {ctx.secrets_path} — "
                          f"không biết account_no để lọc dữ liệu broker (§12)")
    th, th_err = load_thresholds(ctx.rules_path)
    try:
        episodes_data = load_episodes(ctx)
    except (OSError, ValueError) as exc:   # sổ episode hỏng: hai phanh kia vẫn phải đo
        episodes_data = None
        th_err = dict(th_err)
        th_err.setdefault("episode", f"sổ episode {ctx.episodes_path} không đọc được "
                                     f"({type(exc).__name__}: {exc}) ⇒ không biết có episode nào "
                                     f"đang mở")
    for b, why in th_err.items():
        print(f"❌ phanh '{b}' KHÔNG ĐO ĐƯỢC ngay từ cấu hình (THIẾU NGƯỠNG / sổ hỏng): {why}",
              file=sys.stderr)
    status = _status_skeleton(ctx, d, th, th_err)
    rc = 0
    for account in accounts:
        try:
            st = run_account(ctx, account, profiles[account], d, th, th_err, episodes_data,
                             record=not dry)
        except Exception as exc:  # một account hỏng không được làm account kia mất tiếng
            st = failed_account_state(d, th, f"monitor lỗi khi đo {account}: "
                                             f"{type(exc).__name__}: {exc}")
        if dry:
            st["alert"] = {"dry_run": True, "send_error": None}
        else:
            try:
                st["alert"] = dispatch_alerts(ctx, account, st)
            except Exception as exc:
                st["alert"] = {"keys": [], "new": [], "sent_now": False, "ledger_error": None,
                               "sink": None, "send_error": f"{type(exc).__name__}: {exc}"}
        status["accounts"][account] = st
        mark = {OK: "✅", BREACH: "🚨", BREACH_PROV: "🚨", UNMEASURABLE: "⚠️"}[st["overall"]]
        print(f"{mark} {account} phiên {d} ({BASIS_VI}): " + " · ".join(brake_lines(st["brakes"])))
        for n in st["notes"]:
            print(f"   • {n}")
        if st["alert"]["send_error"]:
            print(f"❌ {account}: KHÔNG gửi được cảnh báo — {st['alert']['send_error']}",
                  file=sys.stderr)
            rc = 3
        elif st.get("monitor_error"):
            rc = 3
        elif st["overall"] != OK and rc == 0:
            rc = 1
    status["overall"] = worst([a["overall"] for a in status["accounts"].values()])
    if dry:
        print(f"(CHẠY KHÔ: --date {d} khác phiên phải đo {expected_session(ctx.now)} ⇒ không ghi "
              f"status, không gửi. Muốn ghi/gửi cho phiên cũ: thêm --write-backdated.)")
        return rc
    _write_json_atomic(ctx.status_path, status)
    _log_run(ctx, d, rc, status)
    return rc


def crashed(ctx, args, d, exc):
    """Monitor TỰ HỎNG trước khi đo xong: vẫn để lại status KHÔNG ĐO ĐƯỢC và cố gửi một tin, kèm
    đúng lỗi đọc được (§29). Từng bước bọc riêng — bước này hỏng không được chặn bước kia."""
    why = f"{type(exc).__name__}: {exc}"
    print(f"❌ MONITOR PHANH LỖ NAV LỖI phiên {d}: {why}", file=sys.stderr)
    th = {"drawdown": -DD_THRESHOLD, "daily": None, "episode": None}
    accounts = list(args.account or [])
    if not accounts:
        try:
            accounts = [k for k in _read_json(ctx.inception_path, {}) if not k.startswith("_")]
        except (OSError, ValueError):
            accounts = []
    status = _status_skeleton(ctx, d, th, {})
    status.update(error=why, overall=UNMEASURABLE)
    for a in accounts:
        status["accounts"][a] = failed_account_state(d, th, f"monitor lỗi: {why}")
    text = (f"🛑 MONITOR PHANH LỖ NAV LỖI — phiên {d}\n{why}\n"
            f"Đêm nay KHÔNG phanh nào được đo cho {', '.join(accounts) or '(không rõ account)'}. "
            f"Không đo được KHÔNG có nghĩa là an toàn.")
    try:
        alert = send_once(ctx, [f"monitor|{d}|{type(exc).__name__}"], lambda: text)
    except Exception as exc2:
        alert = {"send_error": f"{type(exc2).__name__}: {exc2}", "sent_now": False}
    status["alert"] = alert
    if alert.get("send_error"):
        print(f"❌ KHÔNG gửi được tin 'monitor lỗi' — {alert['send_error']}", file=sys.stderr)
    try:
        _write_json_atomic(ctx.status_path, status)
    except OSError as exc3:
        print(f"❌ không ghi được {ctx.status_path}: {type(exc3).__name__}: {exc3}",
              file=sys.stderr)
    _log_run(ctx, d, 3, status)
    return 3


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--account", action="append",
                    help="mặc định: mọi account có trong account_inception.json")
    ap.add_argument("--date", help="phiên cần đo YYYY-MM-DD (mặc định: phiên phải có NAV chốt); "
                                   "khác phiên mặc định ⇒ CHẠY KHÔ trừ khi có --write-backdated")
    ap.add_argument("--write-backdated", action="store_true",
                    help="cho --date của phiên cũ được ghi status + gửi cảnh báo")
    ap.add_argument("--data-root")
    ap.add_argument("--state-dir")
    ap.add_argument("--secrets")
    ap.add_argument("--now", help="giả lập đồng hồ ICT (ISO) — chỉ cho selfcheck/chạy thử; bị TỪ "
                                  "CHỐI khi state-dir là state sống")
    ap.add_argument("--replay", action="store_true")
    ap.add_argument("--health-line", action="store_true")
    ap.add_argument("--close-episode", metavar="ACCOUNT")
    ap.add_argument("--closed-by")
    ap.add_argument("--open-episode", metavar="ACCOUNT")
    ap.add_argument("--opened-date")
    ap.add_argument("--entry-ref-date")
    ap.add_argument("--opened-by")
    ap.add_argument("--ack-approval", metavar="ACCOUNT")
    ap.add_argument("--approval-date")
    ap.add_argument("--acked-by")
    ap.add_argument("--reason")
    args = ap.parse_args(argv)

    now = None
    if args.now:
        now = datetime.datetime.fromisoformat(args.now)
        now = now.replace(tzinfo=ICT) if now.tzinfo is None else now.astimezone(ICT)
    ctx = Ctx(args.data_root, args.state_dir, args.secrets, now)
    if args.now and ctx.state_is_live:
        print(f"❌ TỪ CHỐI --now trên state sống ({ctx.state_dir}): đồng hồ giả sẽ ghi status / "
              f"khoá chống-trùng / ngày đóng episode sai ngày. Chạy thử thì thêm --state-dir "
              f"<thư mục tạm>.", file=sys.stderr)
        return 2

    if args.health_line:
        if not args.account or len(args.account) != 1:
            print("❌ --health-line cần đúng một --account.", file=sys.stderr)
            return 2
        rc, line = health_line(ctx, args.account[0])
        print(line)
        return rc
    human = args.close_episode or args.open_episode or args.ack_approval
    d = None
    try:
        if human:
            with state_lock(ctx):
                if args.close_episode:
                    return close_episode(ctx, args.close_episode, args.closed_by, args.reason)
                if args.open_episode:
                    return open_episode(ctx, args.open_episode, args.opened_date,
                                        args.entry_ref_date, args.opened_by, args.reason)
                return ack_approval(ctx, args.ack_approval, args.approval_date, args.acked_by,
                                    args.reason)
        if args.replay:
            profiles = load_profiles(ctx.secrets_path)
            accounts = args.account or [k for k in _read_json(ctx.inception_path, {})
                                        if not k.startswith("_")]
            th, th_err = load_thresholds(ctx.rules_path)
            return replay(ctx, accounts, profiles, th, th_err)
        d = datetime.date.fromisoformat(args.date) if args.date else expected_session(ctx.now)
        if d != expected_session(ctx.now) and not args.write_backdated:
            return run(ctx, args, d, dry=True)
        with state_lock(ctx):
            try:
                return run(ctx, args, d, dry=False)
            except Exception as exc:
                return crashed(ctx, args, d, exc)
    except LockBusy as exc:
        print(f"❌ {exc} — bỏ lượt này.", file=sys.stderr)
        return 4
    except OSError as exc:
        # không mở / không khoá được state-dir (K4): lượt đo ⇒ đi đường crashed() để vẫn cố để lại
        # status + một tin; lệnh tay / replay / chạy khô ⇒ nói đúng lỗi, rc=3 (không phải rc=1).
        if d is not None and not human and (d == expected_session(ctx.now) or args.write_backdated):
            return crashed(ctx, args, d, exc)
        print(f"❌ {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
