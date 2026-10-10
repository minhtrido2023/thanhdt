"""arch-review: P1 trên bản THẬT của account_ledger/_broker_touched — tài khoản thứ ba có bản ghi
positions RỖNG (đúng hình dạng một tài khoản live vừa bật: bot poll mỗi tối, positions=[])."""
import json, os, sys, tempfile, types
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/wt-dailyreturn-1010/bin")
os.environ.pop("DAR_BQ_MEMO_DIR", None)
import dividend_adjusted_return as dar

def pos(acct, ts, items):
    return {"kind": "positions", "account_no": acct, "ts": ts, "payload": {"positions": [
        {"accountNo": acct, "symbol": s, "openQuantity": q, "costPrice": c} for s, q, c in items]}}
def bal(acct, ts, cash):
    return {"kind": "balances", "account_no": acct, "ts": ts,
            "payload": {"stock": {"totalCash": cash, "availableCash": cash, "depositInterest": 0,
                                  "cashDividendReceiving": 0}}}
def build(days):
    d = tempfile.mkdtemp(prefix="archrev_p1_")
    for day, recs in days.items():
        with open(os.path.join(d, f"dnse_raw_{day}.jsonl"), "w") as fh:
            for r in recs: fh.write(json.dumps(r) + "\n")
    return d

DAYS = ["2026-09-01", "2026-09-04", "2026-09-17", "2026-09-18", "2026-09-21", "2026-09-22", "2026-10-09"]
def scenario(third):
    """TK '2' (ZaloPay) giữ DRI phẳng suốt; TK '3' theo `third(day)` -> list items | None (không có bản ghi)."""
    days = {}
    for day in DAYS:
        ts = f"{day}T19:07:00"
        recs = [pos("2", ts, [("DRI", 1900, 13263.16)]), bal("2", ts, 1_000_000)]
        t = third(day)
        if t is not None:
            recs += [pos("3", f"{day}T19:08:00", t), bal("3", f"{day}T19:08:00", 5_000_000)]
        days[day] = recs
    d = build(days)
    keep = dar.EXEC_LOG_DIR
    dar.EXEC_LOG_DIR = d
    try:
        led = {"ZaloPay": dar.account_ledger("2"), "New3": dar.account_ledger("3")}
    finally:
        dar.EXEC_LOG_DIR = keep
        import shutil; shutil.rmtree(d, ignore_errors=True)
    cand = types.SimpleNamespace(ticker="DRI", last_cum_date="2026-09-18", ex_date="2026-09-21")
    return dar._broker_touched(cand, led, ()), led["New3"]["first"], led["New3"]["ts"][:2]

cases = [
 ("A. TK thứ 3 KHÔNG có bản ghi nào", lambda day: None),
 ("B. TK thứ 3 bật 05/10→ chỉ có bản ghi 09/10 (rỗng)", lambda day: [] if day >= "2026-10-09" else None),
 ("C. TK thứ 3 có bản ghi RỖNG mọi tối từ 01/09 (sổ phủ hai đầu cửa sổ, chưa từng giữ gì)", lambda day: []),
 ("D. như C, nhưng 09/10 mua PVT (mã khác)", lambda day: [("PVT", 100, 20000.0)] if day == "2026-10-09" else []),
 ("E. như C, nhưng giữ PVT suốt từ 01/09 (đối chứng: sổ có dòng ⇒ nhìn thấy)", lambda day: [("PVT", 100, 20000.0)]),
 ("F. TK thứ 3: bản ghi ĐẦU (22/09, sau cửa sổ) là bản đọc RỖNG do lỗi API, 09/10 lộ ra đang giữ DRI",
  lambda day: None if day < "2026-09-22" else ([] if day == "2026-09-22" else [("DRI", 500, 13000.0)])),
]
for name, fn in cases:
    veto, first, ts = scenario(fn)
    print(f"{name}\n   first={first!r} ts[:2]={ts}\n   _broker_touched -> {veto!r}\n")
