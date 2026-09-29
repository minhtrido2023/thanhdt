#!/usr/bin/env python3
"""Selfcheck cho `opening_window_l2_poll.py` — nhánh quan sát đầu phiên của
`order_book_execution_shadow` (dispatch Taylor_20260925_174424).

Mỗi ca dưới đây phải CHẾT nếu đúng cơ chế nó kiểm bị gỡ/hỏng — không kiểm "chạy không crash".
Chạy ĐỘC LẬP interpreter khỏi PLAN_DIR/ACCOUNTS_FILE thật (`ORDER_BOOK_OPENING_ACCOUNTS_FILE`
+ `load_plan_fn` injection) — không đụng broker thật/network ở bất kỳ ca nào.
"""
import importlib.util
import json
import os
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "opening_window_l2_poll.py")
PASS = []


def check(name, cond, detail=""):
    PASS.append((name, bool(cond)))
    if not cond:
        raise AssertionError(f"FAIL {name} :: {detail}")


spec = importlib.util.spec_from_file_location("_owp", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


# ------------------------------------------------------- A. load_live_accounts: lọc đúng luật
with tempfile.TemporaryDirectory() as root:
    accf = os.path.join(root, "accounts.json")
    with open(accf, "w", encoding="utf-8") as fh:
        json.dump({"accounts": [
            {"label": "main", "mode": "paper", "broker": "phs"},
            {"label": "ZaloPay", "mode": "live", "broker": "dnse", "enabled": True},
            {"label": "SpaceX", "mode": "live", "broker": "dnse"},          # thiếu "enabled" = bật
            {"label": "RocketX", "mode": "live", "broker": "dnse", "enabled": False},
            {"label": "ab_dip", "mode": "paper", "broker": "phs"},
            {"label": "otherbroker", "mode": "live", "broker": "phs_flash"},  # live nhưng KHÔNG dnse
        ]}, fh)
    labels = sorted(a["label"] for a in mod.load_live_accounts(accf))
    check("A1 chỉ account live+dnse+enabled≠False lọt qua",
          labels == ["SpaceX", "ZaloPay"], labels)

# A2. file thiếu/hỏng → [] (fail-safe, không raise)
check("A2 file không tồn tại → []", mod.load_live_accounts("/no/such/file.json") == [])
with tempfile.TemporaryDirectory() as root:
    bad = os.path.join(root, "bad.json")
    with open(bad, "w", encoding="utf-8") as fh:
        fh.write("{not json")
    check("A3 JSON hỏng → [] (không raise)", mod.load_live_accounts(bad) == [])


# ------------------------------------------------- B. collect_opening_tickers: gộp + bỏ qua lỗi
class _FakeOrder:
    def __init__(self, ticker):
        self.ticker = ticker


class _FakePlan:
    def __init__(self, orders):
        self.orders = orders


def _load_plan_ok(date, account):
    if account == "Broken":
        raise RuntimeError("schema lỗi")           # phải bị nuốt, không chặn account khác
    return {
        "SpaceX": _FakePlan([_FakeOrder("VNM"), _FakeOrder("FPT")]),
        "ZaloPay": _FakePlan([_FakeOrder("FPT")]),  # FPT trùng — phải gộp accounts
        "NoPlanToday": None,                        # HOLD hôm nay — bỏ qua, không raise
        "EmptyOrders": _FakePlan([]),
    }.get(account)


accounts = [{"label": l} for l in ("SpaceX", "ZaloPay", "Broken", "NoPlanToday", "EmptyOrders")]
out = mod.collect_opening_tickers(accounts, "2026-09-28", load_plan_fn=_load_plan_ok)
check("B1 gộp đúng ticker set", set(out) == {"VNM", "FPT"}, out)
check("B2 FPT gộp CẢ HAI account đã sort",
      out["FPT"] == ["SpaceX", "ZaloPay"], out)
check("B3 VNM chỉ có SpaceX", out["VNM"] == ["SpaceX"], out)
check("B4 account 'Broken' (exception) không chặn kết quả account khác",
      "VNM" in out and "FPT" in out, out)

check("B5 accounts=[] → {}", mod.collect_opening_tickers([], "2026-09-28",
      load_plan_fn=_load_plan_ok) == {})


# ------------------------------------------------------------- C. snapshot_record: valid/invalid
class _Q:
    def __init__(self, snap):
        self.l2_snapshot = snap


rec_valid = mod.snapshot_record("VNM", ["SpaceX"], "2026-09-28", 3,
                                _Q({"schema_version": "orderbook_l2_v1", "bids": [{"price": 1}]}))
check("C1 stratum='opening_cycle' đóng dấu MỌI bản ghi",
      rec_valid["stratum"] == "opening_cycle", rec_valid)
check("C2 schema riêng, KHÔNG mạo danh chương trình mẹ",
      rec_valid["schema_version"] == "orderbook_l2_opening_v1", rec_valid)
check("C3 snapshot_valid=True + giữ nguyên payload L2 khi CÓ snapshot",
      rec_valid["snapshot_valid"] is True and rec_valid["snapshot"]["bids"] == [{"price": 1}], rec_valid)
check("C4 poll_seq/accounts/ticker đúng field",
      rec_valid["poll_seq"] == 3 and rec_valid["accounts"] == ["SpaceX"] and rec_valid["ticker"] == "VNM",
      rec_valid)

rec_none = mod.snapshot_record("VNM", ["SpaceX"], "2026-09-28", 0, _Q(None))
check("C5 snapshot rỗng → snapshot_valid=False, KHÔNG bịa payload",
      rec_none["snapshot_valid"] is False and "snapshot" not in rec_none, rec_none)


class _QNoAttr:
    pass


rec_missing = mod.snapshot_record("VNM", ["SpaceX"], "2026-09-28", 0, _QNoAttr())
check("C6 Quote thiếu hẳn l2_snapshot (không raise AttributeError)",
      rec_missing["snapshot_valid"] is False, rec_missing)


# --------------------------------------------------------- D. poll_window: cửa sổ + resilience
import datetime as dt  # noqa: E402


class _FakeClock:
    """now_fn/sleep_fn giả — tua thời gian THEO SỐ LẦN GỌI, không sleep thật."""
    def __init__(self, start, step_sec=7.0):
        self.now = start
        self.step = step_sec
        self.sleep_calls = 0

    def now_fn(self):
        return self.now

    def sleep_fn(self, seconds):
        self.sleep_calls += 1
        # Round bên trong cửa sổ luôn tua đúng 1 "chu kỳ" — dùng step cố định thay vì cộng
        # `seconds` thật (elapsed) để test không phụ thuộc tốc độ máy chạy selfcheck.
        self.now = self.now + dt.timedelta(seconds=self.step)


class _FlakyBroker:
    """1 mã LUÔN lỗi (giả lập mất kết nối) — vòng lặp KHÔNG được crash vì nó."""
    def __init__(self):
        self.calls = []

    def get_quote(self, ticker):
        self.calls.append(ticker)
        if ticker == "BAD":
            raise RuntimeError("giả lập lỗi mạng")
        return _Q({"schema_version": "orderbook_l2_v1", "bids": [{"price": 100}],
                   "offers": [{"price": 101}]})


with tempfile.TemporaryDirectory() as root:
    out_path = os.path.join(root, "orderbook_opening_2026-09-28.jsonl")
    clock = _FakeClock(dt.datetime(2026, 9, 28, 9, 10, 0), step_sec=7.0)
    broker = _FlakyBroker()
    n = mod.poll_window(
        {"VNM": ["SpaceX"], "BAD": ["ZaloPay"]}, broker, out_path, poll_sec=7.0,
        window_start=dt.time(9, 14, 30), window_end=dt.time(9, 20, 0),
        now_fn=clock.now_fn, sleep_fn=clock.sleep_fn,
    )
    check("D1 KHÔNG poll gì trước window_start (09:10 → 09:14:30, phải chờ)",
          os.path.exists(out_path), "file phải tồn tại sau khi cửa sổ trôi qua")
    with open(out_path, encoding="utf-8") as fh:
        recs = [json.loads(line) for line in fh]
    ticks = sorted(set(r["ticker"] for r in recs))
    check("D2 mã lỗi ('BAD') KHÔNG sinh bản ghi nhưng mã lành ('VNM') vẫn được ghi mỗi vòng",
          ticks == ["VNM"], ticks)
    check("D3 broker vẫn được gọi cho CẢ HAI mã mỗi vòng (không bỏ sót vì 1 mã lỗi)",
          broker.calls.count("BAD") == broker.calls.count("VNM") and broker.calls.count("VNM") > 1,
          broker.calls)
    check("D4 mọi bản ghi nằm TRONG cửa sổ [09:14:30, 09:20:00)",
          all(dt.time(9, 14, 30) <= dt.datetime.fromisoformat(r["polled_at"]).time() < dt.time(9, 20, 0)
              for r in recs), [r["polled_at"] for r in recs])
    check("D5 poll_seq tăng dần, không reset", [r["poll_seq"] for r in recs if r["ticker"] == "VNM"]
          == sorted(set(r["poll_seq"] for r in recs if r["ticker"] == "VNM")),
          [r["poll_seq"] for r in recs])
    check("D6 count trả về khớp số dòng thật ghi ra file", n == len(recs), (n, len(recs)))
    check("D7 accounts giữ đúng theo mã ('BAD'→ZaloPay không lẫn 'VNM'→SpaceX)",
          all((r["ticker"] == "VNM") == (r["accounts"] == ["SpaceX"]) for r in recs), recs)

# D8: cửa sổ đã trôi qua HẲN trước khi bắt đầu (now >= window_end ngay từ đầu) → 0 bản ghi,
# KHÔNG vòng lặp vô hạn chờ "start" của NGÀY MAI (đây là mutation-bait: nếu code lỡ dùng vòng
# lặp while t < window_start mà không có nhánh thoát khi window đã qua, test này treo/timeout).
with tempfile.TemporaryDirectory() as root:
    out_path = os.path.join(root, "late.jsonl")
    clock2 = _FakeClock(dt.datetime(2026, 9, 28, 9, 25, 0), step_sec=7.0)
    n2 = mod.poll_window({"VNM": ["SpaceX"]}, _FlakyBroker(), out_path, poll_sec=7.0,
                         window_start=dt.time(9, 14, 30), window_end=dt.time(9, 20, 0),
                         now_fn=clock2.now_fn, sleep_fn=clock2.sleep_fn)
    check("D8 khởi động SAU khi cửa sổ đã qua → 0 bản ghi, thoát ngay (không treo)", n2 == 0, n2)


# --------------------------------------------- E. mutation: xoá guard stratum phải bị bắt bởi C1
# (tài liệu hoá ý định — nếu ai xoá dòng `"stratum": "opening_cycle"` khỏi snapshot_record(),
# C1 ở trên chết ngay; không cần chạy lại mutation thật, comment này neo lại lý do C1 tồn tại.)

print(f"opening_window_l2_poll_selfcheck: {len(PASS)}/{len(PASS)} PASS "
      f"({len([p for p in PASS if p[1]])} ok, 0 FAIL) — nhóm A-D (accounts/tickers/snapshot/window)")
