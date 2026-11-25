# -*- coding: utf-8 -*-
"""a_events.py — bảng SỰ KIỆN QUÝ PIT cho nghiên cứu dự báo earnings (job Taylor_20261125_011012).
Nguồn: data/bq_cache/ticker_financial.parquet (1 vintage, NP_P0..P7, Revenue_P0..P7 — số QUÝ),
       ../in_snapshot/vp2.parquet (panel V3 md5 daaa63ec…: E, N, MC_rel, roe_tc5, payout, route, in_universe, lv_D0, mc).
known K = max(time, Release_Date) (bảo thủ). Mọi trường của dòng q đã công bố tại K.
Out: ../out/events.parquet, ../out/inventory.json"""
import os, json
import numpy as np, pandas as pd, duckdb
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUT_DIR") or os.path.join(HERE, "..", "out"); SNAP = os.environ.get("SNAP_DIR") or os.path.join(HERE, "..", "in_snapshot")   # J3: SNAP_DIR=in_snapshot_v31 OUT_DIR=out_J3
os.makedirs(OUT, exist_ok=True)
WC = "/home/trido/thanhdt/WorkingClaude"
c = duckdb.connect()
cols = ",".join([f"NP_P{k}" for k in range(8)] + [f"Revenue_P{k}" for k in range(8)])
f = c.execute(f"""SELECT ticker, CAST(time AS DATE) AS time, CAST(Release_Date AS DATE) AS rel, quarter, {cols},
   totalAsset_P0 AS ta, StLiab_P0 AS stl, LtLiab_P0 AS ltl FROM read_parquet('{WC}/data/bq_cache/ticker_financial.parquet')""").df()
f["time"] = pd.to_datetime(f.time); f["rel"] = pd.to_datetime(f.rel)
f["K"] = f[["time", "rel"]].max(axis=1)
f["qp"] = pd.PeriodIndex(f.quarter, freq="Q"); f["qi"] = f.qp.dt.year * 4 + f.qp.dt.quarter
f = f.sort_values(["ticker", "qi", "K"]).drop_duplicates(["ticker", "qi"], keep="first").reset_index(drop=True)
LOG = {"fin_rows": int(len(f)), "fin_tickers": int(f.ticker.nunique()), "K_minus_qend_days_p50": float((f.K - f.qp.dt.end_time.dt.normalize()).dt.days.median())}

# --- revision check: NP_P1 của dòng q vs NP_P0 của dòng q-1 (cùng vintage) ---
prev = f[["ticker", "qi", "NP_P0"]].rename(columns={"NP_P0": "np0_prev"}); prev["qi"] += 1
r = f.merge(prev, on=["ticker", "qi"], how="inner"); ok = r.NP_P1.notna() & r.np0_prev.notna() & (r.np0_prev.abs() > 0)
rv = (r.NP_P1[ok] - r.np0_prev[ok]).abs() / r.np0_prev[ok].abs()
LOG["revision_NP_P1_vs_prevP0"] = {"n": int(ok.sum()), "share_exact_lt_0.1pct": float((rv < 0.001).mean()), "share_gt_5pct": float((rv > 0.05).mean())}

# --- valuation fields từ vp2 (1 dòng / (ticker, quarter): dòng tháng đầu tiên sau K) ---
vp = pd.read_parquet(os.path.join(SNAP, "vp2.parquet"), columns=["ticker", "time", "ym", "quarter", "known", "src", "in_universe", "E", "N", "MC_rel",
     "close_rel", "roe", "roe_tc5", "roe_sd5", "payout", "route", "rating", "np_ttm", "lv_D0", "mc", "Close", "Price"])
vp = vp.sort_values(["ticker", "time"])
v1 = vp.drop_duplicates(["ticker", "quarter"], keep="first").copy()
v1["V_D0"] = np.exp(v1.lv_D0) * v1.mc                    # V của D0 không phụ thuộc mc (lv_D0 = log(vb·E) − log mc)
v1 = v1.rename(columns={"in_universe": "iu_m1", "time": "t_m1", "known": "known_vp"})
ev = f.merge(v1[["ticker", "quarter", "t_m1", "known_vp", "src", "iu_m1", "E", "N", "MC_rel", "roe", "roe_tc5", "roe_sd5", "payout", "route", "rating", "np_ttm", "V_D0"]],
             on=["ticker", "quarter"], how="left")
LOG["vp_quarters_total"] = int(v1.shape[0]); LOG["vp_quarters_src"] = v1.src.value_counts().to_dict()
LOG["events_with_vp"] = int(ev.E.notna().sum())
LOG["known_vp_vs_K_days"] = ev.loc[ev.known_vp.notna(), :].eval("(K - known_vp)").dt.days.describe().round(2).to_dict()
# universe tại K: universe_pit phiên ≤ K
uni = c.execute(f"SELECT ticker, CAST(time AS DATE) AS time FROM read_parquet('{WC}/data/bq_cache/universe_pit/*.parquet') WHERE in_universe").df()
uni["time"] = pd.to_datetime(uni.time); uni["iuK"] = True
ev = pd.merge_asof(ev.sort_values("K"), uni.sort_values("time").rename(columns={"time": "ut"}), left_on="K", right_on="ut", by="ticker",
                   direction="backward", tolerance=pd.Timedelta(days=7))
ev["iuK"] = ev.iuK.fillna(False).astype(bool)
ev["E_bs"] = ev.ta - ev.stl.fillna(0) - ev.ltl.fillna(0)
ev = ev.sort_values(["ticker", "qi"]).reset_index(drop=True)
# thực hiện (actual) quý q+h = NP_P0 dòng q+h (lần công bố đầu trong vintage này) + K của nó
for h in (1, 2, 3, 4):
    a = f[["ticker", "qi", "NP_P0", "K"]].rename(columns={"NP_P0": f"A{h}", "K": f"KA{h}"}); a["qi"] -= h
    ev = ev.merge(a, on=["ticker", "qi"], how="left")
ev["hist8"] = ev[[f"NP_P{k}" for k in range(8)]].notna().all(axis=1)
ev["rev8"] = ev[[f"Revenue_P{k}" for k in range(8)]].notna().all(axis=1)
ev["yr"] = ev.K.dt.year
ev["era"] = np.where(ev.yr.between(2014, 2019), "IS", np.where(ev.yr >= 2020, "OOS", "PRE"))
base = ev.iuK & ev.hist8 & (ev.E > 0)
inv = {}
for era in ("IS", "OOS"):
    m = base & (ev.era == era)
    inv[era] = {"events": int(m.sum()), "tickers": int(ev[m].ticker.nunique()), "report_quarters": int(ev[m].qp.nunique()),
                "years": sorted(ev[m].yr.unique().tolist()), "with_A1": int((m & ev.A1.notna()).sum()), "with_A4": int((m & ev.A4.notna()).sum()),
                "with_rev8": int((m & ev.rev8).sum()), "with_V_D0": int((m & ev.V_D0.notna()).sum()),
                "route": ev[m].route.value_counts().to_dict(),
                "events_per_quarter_p50": float(ev[m].groupby("qp").size().median())}
LOG["inventory"] = inv
LOG["note_survivorship"] = "sự kiện chỉ từ ticker_financial (mã có trong BQ); mã huỷ niêm yết chỉ có ở nguồn VND của panel V3 (src=VND) không có NP_P* ⇒ thiếu ở A"
ev.to_parquet(os.path.join(OUT, "events.parquet"))
json.dump(LOG, open(os.path.join(OUT, "inventory.json"), "w"), indent=1, ensure_ascii=False, default=str)
print(json.dumps(LOG, indent=1, ensure_ascii=False, default=str))
