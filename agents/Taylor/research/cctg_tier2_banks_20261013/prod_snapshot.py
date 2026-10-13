"""In sha256 của mọi đầu ra consumer-facing trên CODE + DỮ LIỆU production (chạy từ main checkout)."""
import hashlib, sys
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import deposit_rate_vn as dep, cctg_rate_vn as cctg, deposit_cctg_trend_check as trend, dcf_valuation as dcf
out = []
for a in (None, "2025-06-30", "2026-09-30", "2026-10-13", "2026-12-15"):
    for fn in (dep.current_deposit_rate, dep.effective_deposit_rate, dep.macro_killswitch_a_status,
               dep.consumer_deposit_rate_detail, dep.consumer_deposit_rate, cctg.current_cctg_rate):
        out.append((fn.__name__, a, repr(fn(a))))
    if a:
        out.append(("discount_rate", a, repr(dcf.discount_rate(a))))
out.append(dep.effective_deposit_events_df().to_csv()); out.append(cctg.cctg_events_df().to_csv())
out.append(repr(trend._load_series()))
print(len(out), hashlib.sha256(repr(out).encode()).hexdigest())
print([o for o in out if o[0] in ("effective_deposit_rate", "macro_killswitch_a_status") and o[1] is None])
