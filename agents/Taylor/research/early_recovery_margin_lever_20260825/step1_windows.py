"""Step 1 — dung cua so early-recovery (causal) + liet ke episode."""
import pandas as pd, numpy as np, sys
W = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, W)

# --- DT5G (CANONICAL: tav2_bq.vnindex_5state_dt5g_live; ban local da doi soat) ---
dt = pd.read_csv(W + "/data/vnindex_5state_dt5g_live.csv", parse_dates=["time"])
dt = dt.sort_values("time").reset_index(drop=True)
STATE = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}
dt["prev"] = dt["state"].shift(1)

# --- VNINDEX close (tu chinh CSV pin cua engine: cot vni_close, dung vintage) ---
CSV = W + "/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_repin0803_price_univpit.csv"
df = pd.read_csv(CSV, low_memory=False)
d = df[df["record_type"] == "DAILY"].copy()
d["ymd"] = pd.to_datetime(d["ymd"])
d = d.sort_values("ymd").drop_duplicates("ymd", keep="last").set_index("ymd")
vni = pd.to_numeric(d["vni_close"], errors="coerce")

# --- Value Radar (CANONICAL, DISPLAY-ONLY -> dung o day CHI de dinh nghia cua so nghien cuu) ---
import value_radar
vr = value_radar.load_series(update=False)
vr = vr.set_index("time")
radar = vr["score"].astype(float)
pe = vr["pe_cap10"].astype(float)
# PE percentile rolling 10Y (2500 phien, min 500) - PIT thuan tuy, khong dung deposit rate
pe_pct = pe.rolling(2500, min_periods=500).rank(pct=True) * 100

# --- Bobby classification (kb/data_registry/market-state/vn_macro_regime_history.md) ---
# Episode DT5G-era da phan loai doc lap, BLIND to forward return:
#   EP-2018-01 CONFIDENCE_LIQUIDITY / CONTAINABLE (ambiguous, N_eff 0.5)
#   EP-2020-02 CONFIDENCE_LIQUIDITY / CONTAINABLE (clean,     N_eff 1.0)
#   EP-2022-05 CONFIDENCE_LIQUIDITY / CONTAINABLE (clean,     N_eff 1.0)
BOBBY_LOAI2_SPANS = [("2018-01-01", "2018-12-31"), ("2020-02-01", "2021-12-31"), ("2022-05-01", "2023-06-30")]

# --- liet ke MOI exit CRISIS/BEAR -> NEUTRAL/BULL ---
ex = dt[(dt["prev"].isin([1, 2])) & (dt["state"].isin([3, 4]))].copy()
rows = []
for _, r in ex.iterrows():
    T = r["time"]
    # do sau spell CRISIS/BEAR truoc do (causal: chi dung du lieu <= T)
    hist = dt[dt["time"] < T]
    # tim ngay bat dau spell lien tuc trong {1,2}
    i = len(hist) - 1
    while i >= 0 and hist.iloc[i]["state"] in (1, 2):
        i -= 1
    spell_start = hist.iloc[i + 1]["time"] if i + 1 < len(hist) else hist.iloc[0]["time"]
    spell_days = len(hist[hist["time"] >= spell_start])
    v = vni[(vni.index >= spell_start) & (vni.index <= T)]
    vpre = vni[vni.index <= T].tail(252)
    dd52 = (vpre.iloc[-1] / vpre.max() - 1) * 100 if len(vpre) else np.nan
    dd_spell = (v.min() / vni[vni.index <= spell_start].tail(252).max() - 1) * 100 if len(v) and len(vni[vni.index <= spell_start]) else np.nan
    rd = radar[radar.index <= T]
    pp = pe_pct[pe_pct.index <= T]
    bobby = any(pd.Timestamp(a) <= T <= pd.Timestamp(b) for a, b in BOBBY_LOAI2_SPANS)
    rows.append(dict(exit=T.date(), frm=STATE[int(r["prev"])], to=STATE[int(r["state"])],
                     spell_start=spell_start.date(), spell_days=spell_days,
                     dd52_at_exit=round(dd52, 1), dd_spell_trough=round(dd_spell, 1),
                     radar=round(rd.iloc[-1], 1) if len(rd) else np.nan,
                     pe_pct=round(pp.iloc[-1], 1) if len(pp) else np.nan,
                     bobby_loai2=bobby))
out = pd.DataFrame(rows)
pd.set_option("display.width", 200)
print(out.to_string(index=False))
out.to_csv(W + "/mike/agents/Taylor/research/early_recovery_margin_lever_20260825/exits.csv", index=False)
