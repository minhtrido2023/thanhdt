#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monitor PHANH LỖ CẤP NAV — CHỈ CẢNH BÁO (user duyệt 2026-10-12, job Taylor_20261012_111422;
sửa theo arch-review vòng 1, job Taylor_20261012_120049).

Đo ba phanh trên GIÁ ĐƠN VỊ QUỸ chốt-so-chốt của từng account, mỗi tối sau khi NAV đã chốt:
  · lỗ một ngày   <= `risk_circuit_breakers.daily_loss_limit_pct` (data/trading_rules.json)
  · lỗ từ đỉnh    >= DD_THRESHOLD (hằng số dưới đây — KHÔNG có khoá trong trading_rules.json)
  · lỗ từ điểm vào một episode đòn bẩy <= ngưỡng trong
    `macro_kill_switches.C_episode_drawdown_breaker` (data/trading_rules.json)

MONITOR NÀY KHÔNG BAO GIỜ tạo `data/BOT_STOP`, không huỷ lệnh, không gọi broker, không gọi BQ.
Chạm ngưỡng ⇒ gửi cảnh báo (in sẵn lệnh để NGƯỜI tự tạo BOT_STOP) và chờ người quyết.

TỈ SUẤT: một công thức duy nhất — `nav_unit_ledger.build_ledger` (chính sách
`kb/projects/fund-unit-performance-policy-20261010.md`). File này chỉ lấy TỈ SỐ hai giá đơn vị.

GIÁ CHỐT: một dòng nav_history chỉ là giá chốt của ngày `D` khi `balance_ts` của nó nằm trong
[giờ đóng cửa phiên gần nhất <= D, giờ mở cửa phiên kế sau D). Dòng chụp ngoài khoảng đó (vd
04:49 sáng, hay 09:15 hôm sau) KHÔNG phải giá chốt ⇒ số đo dùng nó chỉ là TẠM TÍNH.

CƠ SỞ ĐO ("basis"):
  · account KHÔNG khai `excluded_tickers` ⇒ "total": chuỗi NAV tổng (nav_history).
  · account CÓ khai `excluded_tickers` (secrets/trading_bot_accounts.json) ⇒ "managed": phần BOT
    QUẢN LÝ = nav − giá trị các mã loại trừ. NAV tổng chỉ hiển thị kèm, không kích phanh.
    nav_history không giữ giá/KL từng mã, nên giá trị mã loại trừ được GHI DẦN mỗi ngày vào
    `data/loss_brake/excluded_value_history_{account}.csv` (chỉ-ghi-thêm): KL lấy từ bản ghi
    positions cuối ngày (chụp SAU giờ đóng cửa) trong `dnse_raw_{date}.jsonl` (lọc account, §12);
    giá lấy từ `active_nav_{account}.json` của CHÍNH ngày đó (cron 20:15). Không mã loại trừ nào
    đang giữ ⇒ giá trị 0, không cần giá. Đính chính một dòng đã ghi (hoặc vá một ngày thiếu):
    `--correct-excluded`, kèm người + lý do — KHÔNG mổ CSV bằng tay.
    Chuỗi phải bắt đầu ĐÚNG mốc khởi điểm của account; bắt đầu muộn hơn ⇒ đỉnh cũ nằm ngoài
    chuỗi ⇒ lỗ từ đỉnh + episode chỉ là TẠM TÍNH (vá bằng nav_loss_brake_backfill_excluded.py).
    Tiền chạy GIỮA hai phần (cổ tức tiền của mã loại trừ, bán/mua mã loại trừ) là DÒNG TIỀN của
    phần quản lý: khai trong `data/loss_brake/managed_sleeve_flows.json` (cùng schema
    account_cash_flows.json). Bốn bẫy báo thiếu khai, xét trên MỌI phiên giữa hai dòng liền nhau
    của chuỗi: KL mã loại trừ đổi · giá mã loại trừ nhảy quá biên độ sàn của mã · lịch corp-action
    có sự kiện · KHÔNG ĐỌC ĐƯỢC lịch corp-action của một phiên trong lúc đang giữ mã loại trừ.
    Dính bẫy mà chưa khai ⇒ KHÔNG ĐO ĐƯỢC từ ngày đó TỚI KHI khai (kể cả `kind: market_only`).
    ⚠️ Giới hạn đã biết: `active_nav_{account}.json` chỉ ghi `computed_at` theo NGÀY, không có
    giờ ⇒ không chứng minh được nó định giá sau giờ đóng cửa; dung sai NAV_MATCH_TOL chỉ bắt
    được lệch đủ lớn giữa hai file, và mới đo trên một cặp cùng ngày.

FAIL-LOUD: thiếu dòng NAV phiên phải có, dòng không phải giá chốt, dòng `nav_is_estimate`, thiếu
phiên liền trước, sổ dòng tiền lỗi, thiếu khoá ngưỡng, không đọc được vị thế broker ⇒ "KHÔNG ĐO
ĐƯỢC" kèm lý do ĐỌC TỪ DỮ LIỆU (§29) và CÓ gửi cảnh báo. Số TẠM TÍNH mà đã vượt ngưỡng là trạng
thái RIÊNG (BREACH_PROVISIONAL): tin đỏ, có dòng lệnh BOT_STOP, khoá chống-trùng riêng. Monitor tự
hỏng (file trạng thái cụt, cấu hình không đọc được…) ⇒ vẫn ghi status KHÔNG ĐO ĐƯỢC và cố gửi một
tin "monitor lỗi". Không có nhánh nào coi "không đọc được" là "an toàn".

EPISODE: tự mở khi có ĐỦ hai bằng chứng — bản duyệt `data/margin_approvals/
margin_approval_{account}_{date}.json` (chưa thu hồi) VÀ vị thế mở dưới gói vay
`capit_margin_lever.loan_package_id` trong bản ghi positions SAU giờ đóng cửa của ngày duyệt hoặc
phiên kế. Bản duyệt mà không có vị thế = mới là ý định (§27), không mở. Mở tay: `--open-episode`.
Đóng bằng tay: `--close-episode`. Episode đang mở mà broker không còn vị thế gói vay, hoặc có
bản duyệt MỚI trong lúc episode còn mở (chưa `--ack-approval`) ⇒ phanh episode KHÔNG ĐO ĐƯỢC.

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
    python3 mike/bin/nav_loss_brake_monitor.py --correct-excluded ZaloPay --date 2026-08-24 \\
        --detail '{"DGC": {"qty": 10000, "price": 47100}}' --corrected-by "..." --reason "..."
Mã thoát lượt chạy: 0 = cả ba phanh OK · 1 = có phanh chạm / tạm tính vượt / không đo được ·
3 = monitor lỗi hoặc không gửi được cảnh báo · 4 = lượt khác đang giữ khoá.
Selfcheck: python3 mike/bin/nav_loss_brake_monitor_selfcheck.py
"""
import argparse
import contextlib
import csv
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

from account_cash_flows import SESSION_CLOSE_ICT, NavRow, load_flows  # noqa: E402
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
# Biên độ giá/ngày theo sàn. Giá đóng cửa nhảy quá biên của sàn (+BAND_PAD làm tròn bước giá)
# không thể do khớp lệnh thường ⇒ có sự kiện quyền. Sàn của từng mã loại trừ khai trong
# `data/loss_brake/excluded_ticker_exchange.json` ({"DGC": "HOSE"}); mã chưa khai / sàn lạ ⇒
# dùng DEFAULT_EXCHANGE — sàn có biên HẸP nhất, tức nghiêng về KÊU chứ không nghiêng về im.
EXCHANGE_BAND = {"HOSE": 0.07, "HNX": 0.10, "UPCOM": 0.15}
DEFAULT_EXCHANGE = "HOSE"
BAND_PAD = 0.005
# active_nav_{account}.json (cron 20:15) và dòng nav_history cùng ngày phải định giá CÙNG một
# danh mục: `total_nav` của file kia được lệch NAV tối đa chừng này. Lệch hơn = hai file dùng giá
# khác nhau cho ít nhất một mã (ca DGC 11/09: broker 38.750 vs giá đóng cửa 46.750 = 8% NAV) ⇒
# lấy giá mã loại trừ từ file kia rồi trừ khỏi NAV này sẽ ra lãi/lỗ GIẢ ở phần quản lý.
# 0,1% là GIẢ ĐỊNH CHƯA KIỂM: mới có 1 cặp cùng ngày để đo (ZaloPay 2026-10-09, lệch đúng 0đ).
NAV_MATCH_TOL = 0.001
# Sai số dấu phẩy động khi so đúng biên (−5,00% phải kêu). 1e-9 = 0,0000001pp.
EPS = 1e-9
# Khoảng hợp lý của ngưỡng episode đọc từ trading_rules.json; ngoài khoảng ⇒ từ chối, không đoán.
EPISODE_TH_RANGE = (-0.30, -0.05)
# Khoá SỐ của ngưỡng episode (chưa có trong trading_rules.json lúc viết; có thì ưu tiên hơn chuỗi
# `trigger`): macro_kill_switches.C_episode_drawdown_breaker.<khoá này>.
EPISODE_NUMERIC_KEY = "episode_drawdown_limit_pct"
# Chờ khoá state tối đa chừng này giây rồi bỏ lượt (lượt đang giữ khoá làm đúng việc đó).
LOCK_WAIT_S = 60

OK, BREACH, BREACH_PROV = "OK", "BREACH", "BREACH_PROVISIONAL"
UNMEASURABLE, NO_EPISODE = "UNMEASURABLE", "NO_EPISODE"
ALERTING = (BREACH, BREACH_PROV, UNMEASURABLE)
BRAKES = ("daily", "drawdown", "episode")
BRAKE_VI = {"daily": "Lỗ một ngày", "drawdown": "Lỗ từ đỉnh", "episode": "Lỗ từ điểm vào episode"}
EXCL_FIELDS = ["date", "excluded_value", "detail", "source", "positions_ts", "recorded_at"]
SINK_ENV = "MIKE_LOSS_BRAKE_ALERT_SINK"
NOTIFY_CHANNEL = "trading_daily"
STATUS_SCHEMA = 2
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
        self.corrections_path = os.path.join(self.state_dir, "excluded_value_corrections.json")
        self.exchange_path = os.path.join(self.state_dir, "excluded_ticker_exchange.json")
        self.run_log_path = os.path.join(self.state_dir, "run_log.jsonl")
        self.lock_path = os.path.join(self.state_dir, ".lock")
        self.now = now or datetime.datetime.now(ICT)
        # {date: {account_no: (positions, ts)}} — chỉ --replay bật (đọc lại cùng file nhiều lần)
        self.pos_cache = None

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


def next_session(d):
    d += datetime.timedelta(days=1)
    while not is_session(d):
        d += datetime.timedelta(days=1)
    return d


def sessions_between(prev, cur):
    """Các phiên giao dịch trong (prev, cur]."""
    return [s for s in (prev + datetime.timedelta(days=i) for i in range(1, (cur - prev).days + 1))
            if is_session(s)]


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
    """Khoá độc quyền cho mọi đường GHI vào state-dir (lượt chạy, mở/đóng episode, đính chính)."""
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
    """(ngưỡng | None, lỗi | None) của phanh episode. Khoá số (nếu có) thắng chuỗi `trigger`."""
    where = f"{rules_path}: macro_kill_switches.C_episode_drawdown_breaker"
    lo, hi = EPISODE_TH_RANGE
    if EPISODE_NUMERIC_KEY in node:
        v = node[EPISODE_NUMERIC_KEY]
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not lo <= v <= hi:
            return None, (f"{where}.{EPISODE_NUMERIC_KEY} phải là số trong [{lo}, {hi}], đọc "
                          f"được {v!r}")
        return float(v), None
    trig = node.get("trigger")
    # đúng dạng -0.xx (hai chữ số thập phân), không dính vào số khác (1-0.15, -0.015)
    found = (sorted(set(re.findall(r"(?<![\d.])-0\.\d\d(?!\d)", trig)))
             if isinstance(trig, str) else [])
    if len(found) != 1:
        return None, (f"{where}.trigger phải chứa ĐÚNG MỘT ngưỡng dạng -0.xx (hai chữ số thập "
                      f"phân), đọc được {trig!r}")
    v = float(found[0])
    if not lo <= v <= hi:
        return None, f"{where}.trigger: ngưỡng {v} nằm ngoài khoảng hợp lý [{lo}, {hi}] ({trig!r})"
    stated = re.findall(r"\(-(\d+(?:\.\d+)?)%\)", trig)
    if stated and any(abs(-float(s) / 100 - v) > EPS for s in stated):
        return None, (f"{where}.trigger tự mâu thuẫn: ngưỡng số {v} nhưng phần trăm ghi kèm là "
                      f"{stated} ({trig!r})")
    return v, None


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
    node = (rules.get("macro_kill_switches") or {}).get("C_episode_drawdown_breaker") or {}
    th["episode"], err = _episode_threshold(rules_path, node if isinstance(node, dict) else {})
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
    """{label: {"account_id", "excluded_tickers"}} từ secrets/trading_bot_accounts.json."""
    with open(secrets_path, encoding="utf-8") as f:
        cfg = json.load(f)
    return {rec["label"]: {"account_id": rec.get("account_id"),
                           "excluded_tickers": sorted(rec.get("excluded_tickers") or [])}
            for rec in cfg.get("accounts", []) if rec.get("label")}


# ------------------------------------------------------------------ broker raw (chỉ ĐỌC file)
def _last_positions_by_account(path):
    """{account_no: (payload positions, ts)} — bản ghi positions CUỐI CÙNG của từng account."""
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
            out[str(rec.get("account_no"))] = ((rec.get("payload") or {}).get("positions") or [],
                                               rec.get("ts"))
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
    latest, ts = by_acc[str(account_no)]
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


def _qty_by_symbol(positions, keep=None):
    out = {}
    for p in positions:
        if keep is None or keep(p):
            out[p.get("symbol")] = out.get(p.get("symbol"), 0.0) + float(p["openQuantity"])
    return out


# ------------------------------------------------------------------ chuỗi giá trị mã loại trừ
def load_corrections(ctx, account):
    """{date: {"value", "detail", "source"}} — đính chính có người + lý do, đè lên dòng CSV."""
    out = {}
    for rec in (_read_json(ctx.corrections_path, {}) or {}).get(account) or []:
        d = datetime.date.fromisoformat(rec["date"])
        detail = {t: {"qty": float(x["qty"]), "price": float(x["price"])}
                  for t, x in rec["detail"].items()}
        out[d] = {"value": sum(x["qty"] * x["price"] for x in detail.values()), "detail": detail,
                  "source": f"đính chính bởi {rec['corrected_by']}: {rec['reason']}"}
    return out


def read_excluded_history(path, corrections=None):
    """{date: {"value", "detail": {ticker: {"qty", "price"}}}}. File thiếu ⇒ {} (+ đính chính)."""
    out = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8", newline="") as f:
            for rec in csv.DictReader(f):
                d = datetime.date.fromisoformat(rec["date"])
                out[d] = {"value": float(rec["excluded_value"]),
                          "detail": json.loads(rec["detail"] or "{}"), "source": rec["source"]}
    out.update(corrections or {})
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
    KL: broker raw SAU giờ đóng cửa. Giá (chỉ cần khi có giữ): active_nav của CHÍNH ngày đó."""
    positions, ts, why = close_positions(ctx, account_no, date)
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
    have = read_excluded_history(ctx.excl_path(account), load_corrections(ctx, account))
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
def _corp_events(ctx, s, tickers):
    """Sự kiện quyền của `tickers` có ngày hiệu lực ĐÚNG phiên `s`, theo snapshot
    corp_action_daily của chính `s`. `(events | None, note)`: None = KHÔNG kiểm được phiên đó
    (snapshot thiếu / hỏng / không dùng được) — người gọi phải coi là một bẫy, không phải "sạch"."""
    path = os.path.join(ctx.corp_dir, f"corp_action_daily_{s}.json")
    if not os.path.exists(path):
        return None, f"không có {os.path.basename(path)}"
    try:
        snap = _read_json(path, {})
    except ValueError as exc:
        return None, f"{os.path.basename(path)} không đọc được: {exc}"
    if snap.get("asof") != s.isoformat() or snap.get("usable") is not True:
        return None, (f"{os.path.basename(path)} không dùng được (asof={snap.get('asof')!r} "
                      f"usable={snap.get('usable')!r})")
    return [e for e in snap.get("upcoming_events_held") or []
            if e.get("ticker") in tickers and e.get("date") == s.isoformat()], None


def load_bands(ctx):
    """({ticker: sàn đã khai}, ghi chú | None). File thiếu ⇒ mọi mã dùng DEFAULT_EXCHANGE."""
    try:
        raw = _read_json(ctx.exchange_path, {})
        if not isinstance(raw, dict):
            raise ValueError(f"nội dung là {type(raw).__name__}, không phải object")
    except (OSError, ValueError) as exc:
        return {}, (f"{ctx.exchange_path} không đọc được ({type(exc).__name__}: {exc}) ⇒ mọi mã "
                    f"loại trừ dùng biên {DEFAULT_EXCHANGE}")
    return {t: x for t, x in raw.items() if not t.startswith("_")}, None


def price_band(exchanges, ticker):
    """(biên một phiên, nhãn để in) của mã loại trừ `ticker`."""
    ex = exchanges.get(ticker)
    if ex in EXCHANGE_BAND:
        return EXCHANGE_BAND[ex] + BAND_PAD, ex
    return EXCHANGE_BAND[DEFAULT_EXCHANGE] + BAND_PAD, (
        f"{DEFAULT_EXCHANGE} — mặc định, sàn của {ticker} "
        + ("chưa khai" if ex is None else f"khai {ex!r} không nhận ra"))


def sleeve_tripwires(ctx, excl, dates, declared, exchanges):
    """{date: lý do} — ngày phần quản lý CÓ THỂ đã nhận/chuyển tiền với phần loại trừ mà chưa có
    bản ghi nào trong managed_sleeve_flows.json cho ngày đó. Xét MỌI phiên trong (dòng trước,
    dòng này] — chuỗi có thể bắc cầu qua ngày thiếu."""
    out = {}
    for prev, cur in zip(dates, dates[1:]):
        a, b = excl[prev]["detail"], excl[cur]["detail"]
        why = []
        sessions = sessions_between(prev, cur)
        n = max(1, len(sessions))
        for t in sorted(set(a) | set(b)):
            qa, qb = (a.get(t) or {}).get("qty", 0.0), (b.get(t) or {}).get("qty", 0.0)
            if abs(qa - qb) > 1e-6:
                why.append(f"KL mã loại trừ {t} đổi {vnd(qa)} → {vnd(qb)} (so với {prev})")
                continue
            if qa <= 0:
                continue
            ratio = b[t]["price"] / a[t]["price"]
            band, label = price_band(exchanges, t)
            if not (1 - band) ** n <= ratio <= (1 + band) ** n:
                why.append(f"giá {t} nhảy {pct(ratio - 1)} ({vnd(a[t]['price'])} → "
                           f"{vnd(b[t]['price'])}, so với {prev}) — quá biên độ sàn "
                           f"±{pct(band, 1)[1:]}/phiên ({label}) qua {n} phiên")
        qty = {t: max((a.get(t) or {}).get("qty", 0.0), (b.get(t) or {}).get("qty", 0.0))
               for t in set(a) | set(b)}
        held = {t for t, q in qty.items() if q > 0}
        for s in sessions if held else []:
            events, note = _corp_events(ctx, s, held)
            if events is None:
                why.append(f"KHÔNG kiểm được lịch corp-action phiên {s} trong lúc đang giữ "
                           f"{', '.join(sorted(held))}: {note}")
                continue
            for e in events:
                amt = ""
                try:
                    if e.get("event_code") == "DIV":
                        amt = (f" ≈ {vnd(float(e['value_per_share']) * qty[e['ticker']])}đ"
                               f" tiền về phần quản lý")
                except (KeyError, TypeError, ValueError):
                    pass
                why.append(f"lịch corp-action: {e.get('ticker')} {e.get('event_code')} hiệu lực "
                           f"{s} ({e.get('title')}){amt}")
        if why and cur not in declared:
            out[cur] = "; ".join(why)
    return out


def build_chain(ctx, account, profile, today):
    """Chuỗi giá đơn vị làm cơ sở đo + chuỗi NAV tổng (chỉ hiển thị).
    Trả dict: basis, ledger | None, error, warnings[], unexplained{date: lý do}, total_ledger,
    rows (nav_history), excl, ts{date: balance_ts}, base_date (mốc khởi điểm của account),
    late_start (lý do | None: chuỗi phần quản lý bắt đầu muộn hơn mốc khởi điểm)."""
    out = {"basis": "managed" if profile["excluded_tickers"] else "total", "ledger": None,
           "error": None, "warnings": [], "unexplained": {}, "total_ledger": None, "rows": [],
           "excl": {}, "ts": {}, "base_date": None, "late_start": None}
    try:
        rows = load_nav_history(account, ctx.exec_dir)
        inception = load_inception(account, ctx.inception_path)
        flows = load_flows(account, flows_path=ctx.flows_path, require_file=True, today=today)
        base_date, base_nav = _inception_baseline(rows, inception)
        out.update(rows=rows, base_date=base_date, ts={r[0]: r.balance_ts for r in rows})
        total, info = build_ledger(rows, flows, base_date, base_nav)
        if info["pending"]:
            raise ValueError(f"{len(info['pending'])} dòng tiền TREO trong {ctx.flows_path} (chưa "
                             f"dòng NAV nào chụp sau thời điểm tiền vào/ra)")
        out["total_ledger"] = total
        if out["basis"] == "total":
            out["ledger"] = total
            return out
        excl = read_excluded_history(ctx.excl_path(account), load_corrections(ctx, account))
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
            out["late_start"] = (f"chuỗi phần quản lý chỉ bắt đầu từ {first[0]} (không có giá "
                                 f"trị mã loại trừ tại mốc khởi điểm {base_date}) ⇒ đỉnh trước "
                                 f"{first[0]} nằm NGOÀI chuỗi")
            out["warnings"].append(out["late_start"])
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
        exchanges, note = load_bands(ctx)
        if note:
            out["warnings"].append(note)
        dates = [r["date"] for r in ledger if r["date"] in excl]
        out["unexplained"] = sleeve_tripwires(ctx, excl, dates, {f["date"] for f in sleeve},
                                              exchanges)
    except Exception as exc:  # §29: lý do = đúng thông điệp lỗi đọc được, không đoán
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


def active_episode(episodes, account, d):
    for e in episodes:
        if e["account"] != account or datetime.date.fromisoformat(e["opened_date"]) > d:
            continue
        if e.get("closed_date") is None or d < datetime.date.fromisoformat(e["closed_date"]):
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


def lever_positions(ctx, account_no, d, pkg):
    """({symbol: qty} dưới gói vay `pkg` CUỐI PHIÊN d | None, ts, lý do-không-đọc-được)."""
    positions, ts, why = close_positions(ctx, account_no, d)
    if positions is None:
        return None, ts, why
    return _qty_by_symbol(positions, keep=lambda p: p.get("loanPackageId") == pkg), ts, None


def detect_episode_opens(ctx, account, account_no, pkg, episodes, ledger, upto, approvals):
    """Mở episode khi có ĐỦ bản duyệt + vị thế gói vay thật ở ngày duyệt hoặc phiên kế. Trả
    (episode mới[], ghi chú[]). Không ghi file — người gọi quyết."""
    new, notes = [], []
    dates = [r["date"] for r in ledger]
    for d, rec, path in approvals:
        if d > upto:
            continue
        mine = [e for e in episodes + new if e["account"] == account]
        if any(datetime.date.fromisoformat(e["opened_date"]) <= d
               and (e.get("closed_date") is None
                    or d < datetime.date.fromisoformat(e["closed_date"])) for e in mine):
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
        opened = None
        for c in cands:
            held, ts, why = lever_positions(ctx, account_no, c, pkg)
            if held is None:
                notes.append(f"có bản duyệt margin {d} nhưng không kiểm được vị thế gói vay {pkg} "
                             f"phiên {c}: {why} — nếu vị thế đã có thật, mở tay bằng "
                             f"--open-episode")
                break
            if held:
                opened = (c, held, ts)
                break
        else:
            notes.append(f"có bản duyệt margin {d} nhưng broker KHÔNG có vị thế nào dưới gói vay "
                         f"{pkg} cuối phiên {', '.join(str(c) for c in cands) or '(chưa tới)'}"
                         + (" ⇒ mới là ý định, chưa khớp — không mở episode" if len(cands) == 2
                            else " — sẽ kiểm lại ở phiên kế"))
        if opened is None:
            continue
        c, held, ts = opened
        if active_episode(mine, account, c) is not None:
            continue
        ref = [x for x in dates if x < c]
        if not ref:
            notes.append(f"bản duyệt margin {d} + vị thế gói vay {pkg} có thật, nhưng chuỗi giá "
                         f"đơn vị không có dòng nào trước {c} để làm điểm vào")
            continue
        new.append({"id": f"{account}-{c}", "account": account, "opened_date": c.isoformat(),
                    "approval_date": d.isoformat(), "entry_ref_date": ref[-1].isoformat(),
                    "opened_by": "nav_loss_brake_monitor.py",
                    "evidence": {"approval_file": path, "approved_by": rec.get("approved_by"),
                                 "loan_package_id": pkg, "lever_positions": held,
                                 "positions_ts": ts},
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


def lever_guard(ctx, account, account_no, d, pkg, episodes, approvals):
    """Bằng chứng broker cho phanh episode tại phiên `d`: {"held": {sym: qty} | None, "why",
    "pkg", "new_approvals": [ngày]}."""
    held, _ts, why = lever_positions(ctx, account_no, d, pkg)
    ep = active_episode(episodes, account, d)
    return {"held": held, "why": why, "pkg": pkg,
            "new_approvals": new_approvals(ep, approvals, d) if ep else []}


# ------------------------------------------------------------------ đánh giá ba phanh
def _res(status, value=None, threshold=None, reason=None, **extra):
    r = {"status": status, "value": value, "threshold": threshold, "reason": reason}
    if value is not None and threshold is not None:
        # khoảng cách tới ngưỡng, điểm phần trăm; <= 0 = đã chạm
        r["distance_pp"] = (value - threshold) * 100
    r.update(extra)
    return r


def _measured(v, th, problems, **extra):
    """Kết quả một phanh ĐÃ CÓ SỐ. Không vướng gì ⇒ BREACH/OK. Có vướng (`problems`) ⇒ số chỉ là
    TẠM TÍNH: đã vượt ngưỡng ⇒ BREACH_PROVISIONAL, chưa vượt ⇒ KHÔNG ĐO ĐƯỢC."""
    hit = v <= th + EPS
    if not problems:
        return _res(BREACH if hit else OK, v, th, **extra)
    return _res(BREACH_PROV if hit else UNMEASURABLE, v, th, provisional=True,
                reason="; ".join(problems), **extra)


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


def evaluate(ctx, account, d, chain, th, th_err, episodes, guard, extra_block=None):
    """Ba phanh của `account` tại phiên `d`, chỉ dùng dữ liệu có ngày <= d. `guard`: kết quả
    `lever_guard` (bằng chứng broker cho phanh episode)."""
    res = {}
    block = chain["error"] or extra_block
    cut = [r for r in (chain["ledger"] or []) if r["date"] <= d]
    row = cut[-1] if len(cut) > 1 and cut[-1]["date"] == d else None
    if not block and row is None:
        if cut and cut[-1]["date"] == d:
            block = (f"phiên {d} là dòng ĐẦU TIÊN của chuỗi giá đơn vị — chưa có dòng nào trước "
                     f"nó để so")
        else:
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

    def flaws(r):
        """Vì sao dòng sổ `r` chưa phải giá chốt đã kiểm (rỗng = dùng được). Mốc khởi điểm của
        account là số KHAI trong account_inception.json, không có giờ chụp để kiểm."""
        out = []
        if r["date"] != chain["base_date"]:
            p = close_capture_problem(r["date"], chain["ts"].get(r["date"]))
            if p:
                out.append(p)
        if r["nav_is_estimate"]:
            out.append(f"dòng NAV {r['date']} mang cờ nav_is_estimate (backfill ước tính)")
        return out

    row_flaws = flaws(row)
    # --- lỗ một ngày
    # Mốc so = giá chốt của phiên liền trước. nav_history có cả dòng của ngày NGHỈ (cron vẫn chạy,
    # vd 2026-08-31): dòng đó mang đúng giá chốt phiên trước + lãi tiền gửi, nên khi không có dòng
    # đúng ngày phiên trước thì một dòng ngày nghỉ nằm SAU nó vẫn là mốc hợp lệ.
    want = prev_session(d)
    prev = next((r for r in cut[:-1] if r["date"] == want), cut[-2])
    v = row["unit_price"] / prev["unit_price"] - 1
    if "daily" in th_err:
        res["daily"] = _res(UNMEASURABLE, reason=th_err["daily"])
    else:
        probs = []
        if prev["date"] < want:
            probs.append(f"thiếu dòng của phiên liền trước {want}: dòng trước {d} trong chuỗi là "
                         f"{prev['date']} ⇒ con số là gộp nhiều phiên")
        res["daily"] = _measured(v, th["daily"], probs + row_flaws + flaws(prev))
    # --- lỗ từ đỉnh
    late = [chain["late_start"]] if chain.get("late_start") else []
    peak = max(cut, key=lambda r: r["unit_price"])
    v = row["unit_price"] / peak["unit_price"] - 1
    res["drawdown"] = _measured(v, -DD_THRESHOLD, late + row_flaws, peak_date=peak["date"].isoformat(),
                                peak_unit_price=peak["unit_price"])
    if peak is not row and flaws(peak):
        res["drawdown"]["note"] = "đỉnh chưa phải giá chốt đã kiểm: " + "; ".join(flaws(peak))
    # --- lỗ từ điểm vào episode
    if "episode" in th_err:
        res["episode"] = _res(UNMEASURABLE, reason=th_err["episode"])
        return res
    held, pkg = guard["held"], guard["pkg"]
    ep = active_episode(episodes, account, d)
    if ep is None:
        if held is None:
            res["episode"] = _res(
                UNMEASURABLE, threshold=th["episode"],
                reason=(f"không có episode nào đang mở, nhưng KHÔNG kiểm được broker có vị thế "
                        f"dưới gói vay {pkg} cuối phiên {d} hay không: {guard['why']}"))
        elif held:
            # vị thế gói vay có thật mà không có episode ⇒ phanh −15% đang không canh gì: nói to
            res["episode"] = _res(
                UNMEASURABLE, threshold=th["episode"],
                reason=(f"broker có vị thế dưới gói vay {pkg} ngày {d} "
                        f"({', '.join(f'{k} {vnd(q)}' for k, q in sorted(held.items()))}) nhưng "
                        f"KHÔNG có episode nào đang mở và không có bản duyệt margin hợp lệ để mở "
                        f"— xác minh rồi mở tay bằng --open-episode"))
        else:
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
    probs = late + row_flaws
    if held is None:
        probs.append(f"không kiểm được vị thế gói vay {pkg} cuối phiên {d}: {guard['why']}")
    elif not held:
        probs.append(f"episode {ep['id']} đang mở nhưng broker KHÔNG còn vị thế nào dưới gói vay "
                     f"{pkg} cuối phiên {d} ⇒ đã tất toán? Đóng bằng --close-episode (một lần "
                     f"vay mới sau đó sẽ có điểm vào KHÁC)")
    for a in guard["new_approvals"]:
        alt = [r for r in cut if r["date"] < a]
        v_alt = row["unit_price"] / alt[-1]["unit_price"] - 1 if alt else None
        probs.append(f"có bản duyệt margin MỚI ngày {a} trong lúc episode {ep['id']} còn mở ⇒ "
                     f"điểm vào có thể đã đổi (tính từ điểm vào gốc {ref}: {pct(v)}"
                     + (f"; tính từ chốt {alt[-1]['date']} trước bản duyệt mới: {pct(v_alt)}"
                        if alt else "")
                     + ") — cùng episode thì --ack-approval, vay mới thì --close-episode rồi "
                       "--open-episode")
        if v_alt is not None:
            v = min(v, v_alt)             # số đem so ngưỡng = trường hợp XẤU nhất
    res["episode"] = _measured(v, th["episode"], probs, **extra)
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
    mở episode (chạy thật); False = chỉ đọc (chạy khô / replay). `episodes_data` None = sổ
    episode không đọc được (lý do đã nằm trong `th_err["episode"]`) ⇒ không dò mở, không ghi."""
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
    episodes = episodes_data["episodes"] if episodes_data else []
    pkg = th.get("lever_package_id")
    guard = {"held": None, "why": "chưa có mã gói vay để kiểm", "pkg": pkg, "new_approvals": []}
    if pkg is not None:
        approvals, ap_notes = load_approvals(ctx, account)
        notes += ap_notes
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
        guard = lever_guard(ctx, account, account_no, d, pkg, episodes, approvals)
    res = evaluate(ctx, account, d, chain, th, th_err, episodes, guard, extra_block=extra_block)
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
    for s in ALERTING:
        if s in statuses:
            return s
    return OK


def failed_account_state(basis, d, th, why):
    """Trạng thái của một account mà monitor KHÔNG đo nổi vì chính nó lỗi (§29: `why` = lỗi thật)."""
    return {"basis": basis, "session": d.isoformat(), "basis_nav": None, "unit_price": None,
            "excluded_value": None, "excluded_detail": {}, "total_nav_info": None,
            "brakes": {b: _res(UNMEASURABLE, threshold=th.get(b), reason=why) for b in BRAKES},
            "warnings": [], "notes": [], "overall": UNMEASURABLE, "monitor_error": True}


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
    more = f", đỉnh {r['peak_date']}" if b == "drawdown" else (
        f", điểm vào {r['entry_ref_date']}" if b == "episode" else "")
    if r["status"] == BREACH_PROV:
        return (f"{name}: TẠM TÍNH {pct(r['value'])} ĐÃ VƯỢT ngưỡng {pct(r['threshold'], 0)} "
                f"(vượt {dist}{more}) — chưa phải số chốt: {r['reason']}")
    tail = f"cách {dist}" if r["status"] == OK else f"ĐÃ CHẠM, vượt {dist}"
    return f"{name}: {pct(r['value'])} (ngưỡng {pct(r['threshold'], 0)}, {tail}{more})"


def brake_lines(res, mark=False):
    """Ba dòng (hoặc MỘT dòng khi cả ba phanh bị chặn bởi cùng một lý do)."""
    icon = {BREACH: "🔴 ", BREACH_PROV: "🔴 ", UNMEASURABLE: "🟡 "}
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
    statuses = [st["brakes"][b]["status"] for b in BRAKES]
    if BREACH in statuses:
        head = "🚨 PHANH LỖ NAV ĐÃ CHẠM"
    elif BREACH_PROV in statuses:
        head = "🚨 PHANH LỖ NAV — SỐ TẠM TÍNH ĐÃ VƯỢT NGƯỠNG (chưa phải số chốt)"
    else:
        head = "⚠️ PHANH LỖ NAV — KHÔNG ĐO ĐƯỢC"
    lines.append(f"{head} — {account} · phiên {st['session']} · đo trên {basis_vi(st)}")
    lines += brake_lines(st["brakes"], mark=True)
    t = st.get("total_nav_info")
    if st["basis"] == "managed" and t:
        lines.append(f"ℹ️ NAV tổng (chỉ để tham chiếu, KHÔNG kích phanh): {vnd(t['nav'])}đ · ngày "
                     f"{pct(t['daily'])} · từ đỉnh {pct(t['drawdown'])}")
    for w in st["warnings"] + st["notes"]:
        lines.append(f"• {w}")
    if BREACH in statuses or BREACH_PROV in statuses:
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


def send_once(ctx, keys, make_text):
    """Gửi MỘT tin nếu trong `keys` có khoá CHƯA từng gửi. Ghi dấu NGAY sau khi gửi được (trước
    khi làm bất cứ gì khác). Sổ đã-gửi hỏng ⇒ coi như chưa gửi gì và VẪN gửi (thà trùng còn hơn
    im), cất file hỏng sang `.corrupt.*`. Gửi lỗi ⇒ không ghi dấu ⇒ lượt sau cùng phiên thử lại."""
    out = {"keys": keys, "new": [], "sent_now": False, "send_error": None, "ledger_error": None}
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
    ok, detail = send_alert(ctx, text)
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
    mang cả TRẠNG THÁI ⇒ KHÔNG ĐO ĐƯỢC rồi mới thành TẠM TÍNH VƯỢT NGƯỠNG là một tin mới."""
    keys = [f"{account}|{st['session']}|{b}|{st['brakes'][b]['status']}" for b in BRAKES
            if st["brakes"][b]["status"] in ALERTING]
    return send_once(ctx, keys, lambda: alert_text(account, st))


# ------------------------------------------------------------------ dòng cho ops_health_check
def health_line(ctx, account):
    """(rc, dòng). rc=0: file trạng thái ĐÚNG phiên phải có và account OK. rc=1: phanh chạm /
    tạm tính vượt / không đo được (việc của NGƯỜI — monitor chỉ cảnh báo). rc=2: monitor không
    chạy — file thiếu, cũ, hỏng. rc=3: monitor có chạy nhưng LỖI — tự nó hỏng, hoặc không gửi
    được cảnh báo (rc=2 và rc=3 là việc của vận hành). §14: độ tươi kiểm bằng PHIÊN ghi trong
    file so với lịch, không mtime."""
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
    rc = 3 if broken else (0 if a["overall"] == OK else 1)
    return rc, (f"Phanh lỗ NAV [{account}] phiên {want:%d/%m} ({basis_vi(a)}): "
                + ("❌ MONITOR LỖI — " if a.get("monitor_error") or st.get("error") else "") + body)


# ------------------------------------------------------------------ replay toàn lịch sử
def replay(ctx, accounts, profiles, th, th_err):
    """Chạy thử: với MỖI phiên từ mốc khởi điểm tới dòng NAV mới nhất, monitor sẽ nói gì nếu chạy
    tối hôm đó trên dữ liệu ĐANG CÓ. Không ghi, không gửi."""
    eps = load_episodes(ctx)
    ctx.pos_cache = {}
    rc = 0
    pkg = th.get("lever_package_id")
    for account in accounts:
        today = ctx.now.astimezone(ICT).date()
        account_no = profiles[account]["account_id"]
        chain = build_chain(ctx, account, profiles[account], today)
        print(f"\n=== {account} · cơ sở đo: {chain['basis']} ===")
        if chain["error"]:
            print(f"  KHÔNG dựng được chuỗi: {chain['error']}")
            rc = 1
            continue
        for w in chain["warnings"]:
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
            guard = (lever_guard(ctx, account, account_no, d, pkg, episodes, approvals)
                     if pkg is not None else
                     {"held": None, "why": "chưa có mã gói vay để kiểm", "pkg": pkg,
                      "new_approvals": []})
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
            if (all(res[b]["status"] == UNMEASURABLE for b in BRAKES)
                    and len({res[b]["reason"] for b in BRAKES}) == 1):   # một lý do chặn cả ba
                msg = f"{UNMEASURABLE} cả 3 phanh — {res['daily']['reason']}"
            else:
                msg = "\n".join(f"{res[b]['status']} {brake_line(b, res[b])}" for b in BRAKES
                                if res[b]["status"] in ALERTING)
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


# ------------------------------------------------------------------ việc của NGƯỜI (có khoá)
def _need(flag, **fields):
    """True nếu mọi trường bắt buộc đều có chữ; thiếu ⇒ in ❌ nêu tên cờ còn thiếu."""
    missing = [k for k, v in fields.items() if not (v or "").strip()]
    if missing:
        print(f"❌ {flag} cần " + " và ".join("--" + k.replace("_", "-") for k in missing)
              + " (ai làm, vì sao).", file=sys.stderr)
    return not missing


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
    ep.update(closed_date=today.isoformat(), closed_by=closed_by.strip(),
              close_reason=reason.strip())
    _write_json_atomic(ctx.episodes_path, data)
    print(f"Đã đóng episode {ep['id']} từ {today} (bởi {closed_by}).")
    return 0


def open_episode(ctx, account, opened_date, entry_ref_date, opened_by, reason):
    """Mở tay một episode — cho ca monitor không tự mở được (không đọc được positions ngày duyệt,
    vị thế xuất hiện muộn hơn phiên kế…). Điểm vào mặc định = dòng cuối của chuỗi TRƯỚC ngày mở."""
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
    chain = build_chain(ctx, account, profiles[account], today)
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
    data["episodes"].append({
        "id": eid, "account": account, "opened_date": opened.isoformat(), "approval_date": None,
        "entry_ref_date": ref.isoformat(), "opened_by": opened_by.strip(),
        "evidence": {"manual": True, "reason": reason.strip(),
                     "recorded_at": ctx.now.isoformat(timespec="seconds")},
        "acked_approvals": [], "closed_date": None, "closed_by": None, "close_reason": None})
    _write_json_atomic(ctx.episodes_path, data)
    print(f"Đã mở episode {eid} từ {opened}, điểm vào = giá chốt {ref} (bởi {opened_by}).")
    return 0


def ack_approval(ctx, account, approval_date, acked_by, reason):
    """Xác nhận một bản duyệt MỚI thuộc CÙNG episode đang mở (giải ngân thêm, không phải lần vay
    mới) ⇒ phanh episode đo tiếp từ điểm vào cũ."""
    if not _need("--ack-approval", approval_date=approval_date, acked_by=acked_by, reason=reason):
        return 2
    try:
        d = datetime.date.fromisoformat(approval_date)
    except ValueError as exc:
        print(f"❌ --ack-approval: --approval-date không đọc được ({exc}).", file=sys.stderr)
        return 2
    data = load_episodes(ctx)
    ep = next((e for e in data["episodes"] if e["account"] == account
               and e.get("closed_date") is None), None)
    if ep is None:
        print(f"❌ {account}: không có episode nào đang mở trong {ctx.episodes_path}.",
              file=sys.stderr)
        return 1
    ep.setdefault("acked_approvals", []).append(
        {"date": d.isoformat(), "acked_by": acked_by.strip(), "reason": reason.strip(),
         "recorded_at": ctx.now.isoformat(timespec="seconds")})
    _write_json_atomic(ctx.episodes_path, data)
    print(f"Đã xác nhận bản duyệt {d} thuộc episode {ep['id']} (bởi {acked_by}).")
    return 0


def correct_excluded(ctx, account, date, detail, corrected_by, reason):
    """Đính chính (hoặc vá ngày thiếu) giá trị mã loại trừ của một ngày. CSV gốc KHÔNG bị sửa:
    bản đính chính nằm ở excluded_value_corrections.json (chỉ-ghi-thêm) và đè khi đọc."""
    if not _need("--correct-excluded", date=date, detail=detail, corrected_by=corrected_by,
                 reason=reason):
        return 2
    profiles = load_profiles(ctx.secrets_path)
    excluded = set((profiles.get(account) or {}).get("excluded_tickers") or [])
    try:
        d = datetime.date.fromisoformat(date)
        det = json.loads(detail)
        if not isinstance(det, dict):
            raise ValueError("--detail phải là object {mã: {qty, price}}")
        clean = {}
        for t, x in det.items():
            if t not in excluded:
                raise ValueError(f"{t} không thuộc excluded_tickers của {account} "
                                 f"({sorted(excluded)})")
            qty, price = float(x["qty"]), float(x["price"])
            if not (qty > 0 and price > 0):
                raise ValueError(f"{t}: qty và price phải > 0 (không giữ thì bỏ mã khỏi --detail)")
            clean[t] = {"qty": qty, "price": price}
    except (ValueError, KeyError, TypeError) as exc:
        print(f"❌ --correct-excluded: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    data = _read_json(ctx.corrections_path, {}) or {}
    data.setdefault("_doc", "Đính chính giá trị mã loại trừ (nav_loss_brake_monitor.py "
                            "--correct-excluded). Chỉ-ghi-thêm; bản ghi SAU đè bản ghi trước "
                            "cùng ngày; đè lên excluded_value_history_{account}.csv khi đọc.")
    data.setdefault(account, []).append(
        {"date": d.isoformat(), "detail": clean, "corrected_by": corrected_by.strip(),
         "reason": reason.strip(), "recorded_at": ctx.now.isoformat(timespec="seconds")})
    _write_json_atomic(ctx.corrections_path, data)
    total = sum(x["qty"] * x["price"] for x in clean.values())
    print(f"Đã đính chính giá trị mã loại trừ {account} ngày {d}: {vnd(total)}đ (bởi "
          f"{corrected_by}).")
    return 0


# ------------------------------------------------------------------ main
def _status_skeleton(ctx, d, th, th_err):
    return {"schema": STATUS_SCHEMA, "generated_at": ctx.now.isoformat(timespec="seconds"),
            "session": d.isoformat(), "error": None,
            "thresholds": {"daily": th["daily"], "drawdown": th["drawdown"],
                           "episode": th["episode"], "errors": th_err,
                           "sources": {"daily": "trading_rules.json risk_circuit_breakers."
                                                "daily_loss_limit_pct",
                                       "drawdown": "hằng số DD_THRESHOLD (risk_monitor.py:46)",
                                       "episode": "trading_rules.json macro_kill_switches."
                                                  "C_episode_drawdown_breaker"}},
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
                               if (s.get("alert") or {}).get("sent_now"))},
                ensure_ascii=False) + "\n")
    except OSError as exc:
        print(f"❌ không ghi được {ctx.run_log_path}: {type(exc).__name__}: {exc}", file=sys.stderr)


def run(ctx, args, d, dry):
    """Một lượt đo. `dry` = chỉ in: không ghi chuỗi mã loại trừ, không mở episode, không ghi
    status, không gửi."""
    profiles = load_profiles(ctx.secrets_path)
    accounts = args.account or [k for k in _read_json(ctx.inception_path, {})
                                if not k.startswith("_")]
    missing = [a for a in accounts if a not in profiles or not profiles[a]["account_id"]]
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
        basis = "managed" if profiles[account]["excluded_tickers"] else "total"
        try:
            st = run_account(ctx, account, profiles[account], d, th, th_err, episodes_data,
                             record=not dry)
        except Exception as exc:  # một account hỏng không được làm account kia mất tiếng
            st = failed_account_state(basis, d, th, f"monitor lỗi khi đo {account}: "
                                                    f"{type(exc).__name__}: {exc}")
        if dry:
            st["alert"] = {"dry_run": True, "send_error": None}
        else:
            try:
                st["alert"] = dispatch_alerts(ctx, account, st)
            except Exception as exc:
                st["alert"] = {"keys": [], "new": [], "sent_now": False, "ledger_error": None,
                               "send_error": f"{type(exc).__name__}: {exc}"}
        status["accounts"][account] = st
        mark = {OK: "✅", BREACH: "🚨", BREACH_PROV: "🚨", UNMEASURABLE: "⚠️"}[st["overall"]]
        print(f"{mark} {account} phiên {d} ({basis_vi(st)}): " + " · ".join(brake_lines(st["brakes"])))
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
        status["accounts"][a] = failed_account_state("total", d, th, f"monitor lỗi: {why}")
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
    ap.add_argument("--now", help="giả lập đồng hồ ICT (ISO) — chỉ cho selfcheck")
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
    ap.add_argument("--correct-excluded", metavar="ACCOUNT")
    ap.add_argument("--detail", help='JSON {mã: {"qty": …, "price": …}}; {} = không giữ mã nào')
    ap.add_argument("--corrected-by")
    ap.add_argument("--reason")
    args = ap.parse_args(argv)

    now = None
    if args.now:
        now = datetime.datetime.fromisoformat(args.now)
        now = now.replace(tzinfo=ICT) if now.tzinfo is None else now.astimezone(ICT)
    ctx = Ctx(args.data_root, args.state_dir, args.secrets, now)

    if args.health_line:
        if not args.account or len(args.account) != 1:
            print("❌ --health-line cần đúng một --account.", file=sys.stderr)
            return 2
        rc, line = health_line(ctx, args.account[0])
        print(line)
        return rc
    try:
        if args.close_episode or args.open_episode or args.ack_approval or args.correct_excluded:
            with state_lock(ctx):
                if args.close_episode:
                    return close_episode(ctx, args.close_episode, args.closed_by, args.reason)
                if args.open_episode:
                    return open_episode(ctx, args.open_episode, args.opened_date,
                                        args.entry_ref_date, args.opened_by, args.reason)
                if args.ack_approval:
                    return ack_approval(ctx, args.ack_approval, args.approval_date, args.acked_by,
                                        args.reason)
                return correct_excluded(ctx, args.correct_excluded, args.date, args.detail,
                                        args.corrected_by, args.reason)
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


if __name__ == "__main__":
    sys.exit(main())
