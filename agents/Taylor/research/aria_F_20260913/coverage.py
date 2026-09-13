"""aria-F1a: coverage email khop lenh vs fill trong dnse_raw (dnse_fill_events), theo ngay/account/ma/chieu."""
import sys, glob, os, json
import pandas as pd
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/bin")
from verify_account_snapshot import dnse_fill_events
HERE = os.path.dirname(os.path.abspath(__file__))
ACC = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}
em = pd.read_csv(os.path.join(HERE, "all_fills.csv"), dtype={"tieu_khoan": str})
em["date"] = pd.to_datetime(em.email_date, format="%d/%m/%Y").dt.strftime("%Y-%m-%d")
em["side"] = em.loai_lenh.map({"MUA": "buy", "BÁN": "sell"})
e = em.groupby(["date", "acct", "ma", "side"]).agg(e_qty=("khoi_luong", "sum"), e_val=("gia_tri_khop", "sum")).reset_index()
rows = []
dates = sorted({os.path.basename(p)[9:19] for p in glob.glob("/home/trido/thanhdt/WorkingClaude/data/execution_logs/dnse_raw_2026-0[789]-*.jsonl")})
dates = [d for d in dates if "2026-07-01" <= d <= "2026-09-12"]
for acct, no in ACC.items():
    for d in dates:
        ev, err = dnse_fill_events(no, d)
        for _ts, _k, tk, side, qty, px in (ev or []):
            rows.append((d, acct, tk, side, qty, qty * px))
r = pd.DataFrame(rows, columns=["date", "acct", "ma", "side", "qty", "val"]).groupby(["date", "acct", "ma", "side"]).agg(r_qty=("qty", "sum"), r_val=("val", "sum")).reset_index()
m = r.merge(e, how="outer", on=["date", "acct", "ma", "side"]).fillna(0)
m["dq"] = m.r_qty - m.e_qty; m["dv"] = m.r_val - m.e_val
m.to_csv(os.path.join(HERE, "coverage_raw_vs_email.csv"), index=False)
ses = m.groupby(["acct", "date"]).agg(raw=("r_qty", "sum"), email=("e_qty", "sum"), absdq=("dq", lambda s: s.abs().sum()), absdv=("dv", lambda s: s.abs().sum())).reset_index()
print(ses.to_string())
for acct, s in ses.groupby("acct"):
    raw_days = set(s[s.raw > 0].date); em_days = set(s[s.email > 0].date)
    print(acct, "raw fill days", len(raw_days), "email days", len(em_days), "both", len(raw_days & em_days), "raw-only", sorted(raw_days - em_days), "email-only", sorted(em_days - raw_days))
print(m[(m.dq.abs() > 0) | (m.dv.abs() > 1000)].to_string())
