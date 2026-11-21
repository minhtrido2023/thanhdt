"""Muc 3: dem cap (ma,quy) BANK co ROE_Trailing/ROE5Y/ROE3Y deu trong (rate_bank_hist/proxy tra 3 bia).
Doc HIST_SQL/ICB_SQL that (read-only BQ). Ghi noroe_rows.csv + in tom tat."""
import os, sys
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/wt-bank-nodata-20261119/WorkingClaude")
import warnings; warnings.filterwarnings("ignore")
import pandas as pd, numpy as np
import rating_8l_history as H
OUT = os.path.dirname(os.path.abspath(__file__))
cache = os.path.join(OUT, "hist_pull.pkl")
if os.path.exists(cache):
    df = pd.read_pickle(cache)
else:
    df = H.bq(H.HIST_SQL); df["rd_untrusted"] = H.release_date_untrusted(df)
    df = H.attach_icb_pit(df, H.bq(H.ICB_SQL)); df.to_pickle(cache)
df["route"] = [H.route_of(t, c) for t, c in zip(df["ticker"], df["ICB_Code"])]
b = df[df.route == "BANK"].copy()
b["eff_date"] = H.eff_date_of(b["Release_Date"], b["q_time"], b["rd_untrusted"])
b = b.dropna(subset=["eff_date"])
nor = b[b[["ROE_Trailing", "ROE5Y", "ROE3Y"]].isna().all(axis=1)]
print("BANK rows", len(b), "tickers", b.ticker.nunique())
print("noROE rows", len(nor), "tickers", nor.ticker.nunique())
print(nor.groupby("ticker")["q_time"].agg(["min", "max", "count"]).to_string())
print("by year:", nor.assign(y=pd.to_datetime(nor.q_time).dt.year).groupby("y").size().to_dict())
latest = b.sort_values("eff_date").groupby("ticker").tail(1)
print("latest-row noROE today:", sorted(latest[latest[["ROE_Trailing","ROE5Y","ROE3Y"]].isna().all(axis=1)].ticker))
nor[["ticker", "q_time", "eff_date"]].to_csv(os.path.join(OUT, "noroe_rows.csv"), index=False)
