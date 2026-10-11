import sys, os, datetime as dt, json, tempfile
os.environ["MIKE_BOT_TEST_MODE"] = "1"
sys.path.insert(0, "/tmp/ar2/probe"); sys.path.insert(0, "/tmp/ar2/WC/mike/bin")
from k1 import R, F, run, D, acf, nul, npr
import daily_nav_snapshot as dns
INC = {"inception_date": "2026-06-01", "starting_capital": 1e9}
# Thứ Ba 06-02, Tư 06-03, Năm 06-04. Phiên 06-03 (T) +10%. Nạp 220tr lúc 16:00 ngày T (sau đóng cửa).
T1, T, T2 = D(2026,6,2), D(2026,6,3), D(2026,6,4)
f = [F(T, "16:00", 220e6)]
print("== B1. Sự thật: phiên T +10%, T+1 đứng yên ⇒ giá đơn vị 10.000 → 11.000 → 11.000 (+10,0%)")
full = [R(T1, 1e9), R(T, 1.1e9 + 220e6), R(T2, 1.32e9)]
run("đủ dòng (có dòng phiên T)", full, f)
gap = [R(T1, 1e9), R(T2, 1.32e9)]
led, info = run("THIẾU dòng phiên T (như 2026-08-06 thật)", gap, f)
res = npr.compute_period_returns("X", T2, gap, INC, f)
print("   compute_period_returns asof T+1:", res["inception"]["return_pct"], "% | pending:", res["pending_flows"], "| dropped:", res["dropped_flows"], "| cash_flows:", [(c["timing"], c["session_date"]) for c in res["inception"]["cash_flows"]])
print("   cổng 5% (unexplained_nav_jumps):", acf.unexplained_nav_jumps(gap, f))
print("== B1b. Cùng ca, đi qua cổng 15% của daily_nav_snapshot đúng trình tự thật")
def hist(rows): return [{"date": r[0].isoformat(), "nav": f"{r[1]:.0f}", "balance_ts": r.balance_ts} for r in rows]
def verdict(date, prev_nav, nav, rows, flows, ts):
    p = tempfile.mktemp(suffix=".json", dir="/tmp/ar2"); json.dump({"X": [dict(x, date=x["date"].isoformat()) for x in flows]}, open(p, "w"))
    try: return dns.nav_jump_verdict("X", date.isoformat(), prev_nav, nav, 15.0, hist(rows), flows_path=p, balance_ts=ts)
    finally: os.remove(p)
ok, msg = verdict(T, 1e9, 1.32e9, [R(T1, 1e9)], [], f"{T}T19:10:00")
print(f"   tối T 19:10, CHƯA khai dòng tiền: ok={ok} (dòng phiên T {'ĐƯỢC ghi' if ok else 'KHÔNG được ghi — rc=3'})")
ok, msg = verdict(T2, 1e9, 1.32e9, [R(T1, 1e9)], f, f"{T2}T19:10:00")
print(f"   tối T+1 19:10, ĐÃ khai nạp 220tr 16:00 ngày T: ok={ok} :: {(msg or '')[:230]}")
print("   ⇒ nav_history = [T-1, T+1], dòng T thiếu vĩnh viễn nếu không ai backfill; sổ đơn vị:")
run("   sổ sau đó", gap, f)
print("== B1c. Biến thể: thiếu dòng T, tiền tới sáng T+1 08:00 (trước phiên)")
run("thiếu T, nạp 08:00 T+1", gap, [F(T2, "08:00", 220e6)])
print("== B1d. Thiếu NHIỀU phiên (T và T+1), tiền tới tối T+1")
T3 = D(2026,6,5)
run("thiếu T,T+1; nạp 20:00 T+1; dòng kế T+2", [R(T1, 1e9), R(T3, 1.1e9*1.05 + 220e6)], [F(T2, "20:00", 220e6)])
print("   (sự thật: 10.000 → 11.550)")
print("== B1e. Dữ liệu THẬT: SpaceX thiếu dòng 2026-08-06; nạp 100tr lúc 16:00 ngày 08-06")
rows = nul.load_nav_history("SpaceX"); inc = nul.load_inception("SpaceX")
fl = [F(D(2026,8,6), "16:00", 100e6)]
try:
    r = npr.compute_period_returns("SpaceX", D(2026,10,9), rows, inc, fl)
    print("   KHÔNG lỗi, KHÔNG cảnh báo; gán:", [(c["timing"], c["session_date"]) for c in r["inception"]["cash_flows"]], "| pending:", r["pending_flows"])
except Exception as e: print("   ", type(e).__name__, str(e)[:200])
