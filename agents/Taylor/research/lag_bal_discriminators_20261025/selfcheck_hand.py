"""Tính tay độc lập payout1Y + cfo_np cho 2 vị thế (Python thuần trên record thô) và so với features.csv."""
import csv, datetime as dt
import pandas as pd
ROOT = "/home/trido/thanhdt/WorkingClaude"
HIDS = ["HPG_20200511_", "VNM_"]  # tiền tố; chọn vị thế main đầu tiên khớp
feat = list(csv.DictReader(open("features.csv")))
fin = pd.read_parquet(f"{ROOT}/data/bq_cache_asof20260729_postrestate/ticker_financial.parquet").to_dict("records")
out = []
picks = []
for book in ["LAG", "BAL"]:
    for r in feat:
        if r["book"] == book and r["abandoned"] == "False" and r["mtm"] == "False" and r["G"] == "NONFIN" and r["cfo_np"] and r["payout1Y"]:
            picks.append(r); break
for r in picks:
    sig = dt.datetime.strptime(r["signal_date"][:10], "%Y-%m-%d")
    best = None
    for f in fin:
        if f["ticker"] != r["ticker"]:
            continue
        t = pd.Timestamp(f["time"]).to_pydatetime()
        rd = f["Release_Date"]
        eff = max(t, pd.Timestamp(rd).to_pydatetime()) if rd is not None and rd == rd else t + dt.timedelta(days=11)
        if eff <= sig and (best is None or (eff, f["ID_Release"] or 0) > best[0]):
            best = ((eff, f["ID_Release"] or 0), f)
    f = best[1]
    np_ttm = f["NP_P0"] + f["NP_P1"] + f["NP_P2"] + f["NP_P3"]
    cfo = f["CF_OA_P0"] + f["CF_OA_P1"] + f["CF_OA_P2"] + f["CF_OA_P3"]
    p1 = f["Dividend_1Y"] * f["OShares"] / np_ttm
    c = cfo / np_ttm
    out.append(f"{r['holding_id']} {r['book']} quarter={f['quarter']} eff={best[0][0].date()} sig={sig.date()} | payout1Y tay={p1:.8f} engine={float(r['payout1Y']):.8f} | cfo_np tay={c:.8f} engine={float(r['cfo_np']):.8f} | khớp={abs(p1-float(r['payout1Y']))<1e-6 and abs(c-float(r['cfo_np']))<1e-6}")
print("\n".join(out))
open("selfcheck_hand.txt", "w").write("\n".join(out) + "\n")
