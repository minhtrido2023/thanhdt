import sys, os, json, tempfile, datetime as dt
os.environ["MIKE_BOT_TEST_MODE"] = "1"
sys.path.insert(0, "/tmp/ar2/probe"); sys.path.insert(0, "/tmp/ar2/WC/mike/bin")
from k1 import R, F, run, D, acf, nul, npr
import daily_nav_snapshot as dns
FRI, SAT, SUN, MON, TUE = D(2026,7,3), D(2026,7,4), D(2026,7,5), D(2026,7,6), D(2026,7,7)
def hist(rows): return [{"date": r[0].isoformat(), "nav": f"{r[1]:.0f}", "balance_ts": r.balance_ts} for r in rows]
def verdict(label, date, prev_nav, nav, rows, recs, ts, acct="X"):
    p = tempfile.mktemp(suffix=".json", dir="/tmp/ar2"); json.dump({acct: recs}, open(p, "w"))
    try:
        ok, msg = dns.nav_jump_verdict(acct, date.isoformat(), prev_nav, nav, 15.0, hist(rows), flows_path=p, balance_ts=ts)
        print(f"[{label}] ok={ok} :: {(msg or '').replace(chr(10), ' ⏎ ')[:330]}")
    except Exception as e: print(f"[{label}] *** EXC {type(e).__name__}: {e}")
    finally: os.remove(p)
base = [R(D(2026,7,2), 1e9), R(FRI, 1e9)]
dep = lambda d, t, a=200e6, **k: dict({"date": d, "time_ict": t, "amount_vnd": a, "kind": "deposit", "evidence": "sao kê"}, **k)
verdict("N3 nạp thứ Bảy 10:00, chụp thứ Hai +20%", MON, 1e9, 1.2e9, base, [dep("2026-07-04", "10:00")], f"{MON}T19:10:00")
verdict("N3 nạp thứ Sáu 20:00 (sau chụp)", MON, 1e9, 1.2e9, base, [dep("2026-07-03", "20:00")], f"{MON}T19:10:00")
verdict("N3 nạp thứ Hai 16:00 (trước chụp)", MON, 1e9, 1.2e9, base, [dep("2026-07-06", "16:00")], f"{MON}T19:10:00")
verdict("nạp thứ Hai 20:00 (SAU lần chụp thứ Hai) mà NAV đã +20%", MON, 1e9, 1.2e9, base, [dep("2026-07-06", "20:00")], f"{MON}T19:10:00")
verdict("N4 bản ghi thiếu giờ", MON, 1e9, 1.2e9, base, [{"date": "2026-07-04", "amount_vnd": 200e6, "kind": "deposit", "evidence": "x"}], f"{MON}T19:10:00")
verdict("N4 lịch sử thiếu balance_ts", MON, 1e9, 1.2e9, [acf.NavRow(D(2026,7,2), 1e9), acf.NavRow(FRI, 1e9)], [dep("2026-07-04", "10:00")], f"{MON}T19:10:00")
verdict("dòng hôm nay balance_ts=None", MON, 1e9, 1.2e9, base, [dep("2026-07-04", "10:00")], None)
verdict("không bản ghi", MON, 1e9, 1.2e9, base, [], f"{MON}T19:10:00")
verdict("market_only thứ Hai", MON, 1e9, 1.2e9, base, [{"date": "2026-07-06", "amount_vnd": 0, "kind": "market_only", "evidence": "x"}], f"{MON}T19:10:00")
verdict("khai timing=eod sai", MON, 1e9, 1.2e9, base, [dep("2026-07-04", "10:00", timing="eod")], f"{MON}T19:10:00")
verdict("bước nhảy 10% (<15%) + bản ghi HỎNG ⇒ không đụng sổ", MON, 1e9, 1.1e9, base, [{"date": None}], f"{MON}T19:10:00")
verdict("bước nhảy 20% + bản ghi date=null", MON, 1e9, 1.2e9, base, [{"date": None, "time_ict": "10:00", "amount_vnd": 1, "kind": "deposit", "evidence": "x"}], f"{MON}T19:10:00")
print("== cổng 5% báo cáo cho nạp thứ Bảy"); rows = base + [R(MON, 1.2e9)]
print(acf.unexplained_nav_jumps(rows, [F(SAT, "10:00", 200e6)]), "| không bản ghi:", [(str(j["date"]), round(j["change_pct"], 1)) for j in acf.unexplained_nav_jumps(rows, [])])
