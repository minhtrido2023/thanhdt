#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A1 — Rate-regime x ro parking custom30V (job Taylor_20260822_131318).

Cau hoi: +7,4pp parking co con dung trong bucket lai suat hien tai (HIGH >6.5%) khong,
va CHI PHI cua sector-cap ngan hang la bao nhieu?

Nguon (da tra mike/kb/data_registry/ index.md truoc khi chon):
  - tav2_bq.custom30v_8l           CANONICAL (production parking, money-path). rebal PIT that.
  - tav2_bq.ticker (Close, ICB_Code) CANONICAL. Close = gia DIEU CHINH (adj) -> total return.
  - deposit_rate_vn.py DEPOSIT_EVENTS  CANONICAL-PROXY. ⚠️ caveat (b): 26 moc neo hoi to CUNG
    1 lan 2026-06-19 => KHONG point-in-time that cho qua khu; bucket lich su mang hindsight bias.
  - tav2_bq.vnindex_5state_dt5g_live  CANONICAL (state). KHONG doc bang khong hau to (= v3.4b BASE).
KHONG dung cot profit_* (forward-looking).
"""
import os, sys, json, subprocess
import numpy as np, pandas as pd

W = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, W)
OUT = os.path.join(W, "mike", "agents", "Taylor", "research", "strategy_regime_matrix_20260822")
os.makedirs(OUT, exist_ok=True)
SPY = 249.2785102175346          # sessions/year — dung dung hang so cua pin R3 de so sanh duoc
PRJ = "lithe-record-440915-m9"
BANK_ICB = 8355.0                # xac nhan 2026-08-22: 18 ma ABB..VPB, dung bo ngan hang VN

def bq(q, cache, max_rows=900000):
    p = os.path.join(OUT, cache)
    if os.path.exists(p) and os.path.getsize(p) > 200:
        return pd.read_csv(p)
    r = subprocess.run(["bq", "query", "--use_legacy_sql=false", "--format=csv",
                        f"--max_rows={max_rows}", f"--project_id={PRJ}", q],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("[BQ FAIL]", r.stderr[-1200:]); sys.exit(1)
    with open(p, "w") as f:
        f.write(r.stdout)
    return pd.read_csv(p)

# ------------------------------------------------------------------ 1. ro PIT
mem = bq("SELECT rebal_date, effective_from, effective_to, ticker, weight, liq_rank, rating_8l "
         "FROM `%s.tav2_bq.custom30v_8l` ORDER BY rebal_date, ticker" % PRJ, "a1_c30v_members.csv")
for c in ["rebal_date", "effective_from", "effective_to"]:
    mem[c] = pd.to_datetime(mem[c])
print(f"[data] custom30v_8l: {len(mem)} rows / {mem.rebal_date.nunique()} rebal "
      f"{mem.rebal_date.min().date()} -> {mem.rebal_date.max().date()}")

tks = sorted(mem.ticker.unique())
inlist = ",".join("'%s'" % t for t in tks)
px = bq("SELECT t.time, t.ticker, t.Close, t.ICB_Code FROM `%s.tav2_bq.ticker` AS t "
        "WHERE t.ticker IN (%s) AND t.time BETWEEN '2014-07-01' AND '2026-06-19'"
        % (PRJ, inlist), "a1_px.csv")
px["time"] = pd.to_datetime(px["time"])
icb = px.groupby("ticker").ICB_Code.last()
is_bank = {t: (icb.get(t) == BANK_ICB) for t in tks}
print(f"[data] px {len(px)} rows / {px.ticker.nunique()} tickers; banks in universe = "
      f"{sum(is_bank.values())} -> {sorted(t for t in tks if is_bank[t])}")

vni = bq("SELECT t.time, t.Close FROM `%s.tav2_bq.ticker` AS t WHERE t.ticker='VNINDEX' "
         "AND t.time BETWEEN '2014-07-01' AND '2026-06-19' ORDER BY t.time" % PRJ, "a1_vni.csv")
vni["time"] = pd.to_datetime(vni["time"]); vni = vni.set_index("time")["Close"].sort_index()

st = bq("SELECT s.time, s.state FROM `%s.tav2_bq.vnindex_5state_dt5g_live` AS s "
        "WHERE s.time>='2014-07-01' ORDER BY s.time" % PRJ, "a1_dt5g.csv")
st["time"] = pd.to_datetime(st["time"])
STMAP = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}

# wide close matrix
P = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="last").sort_index()
R = P.pct_change()

# ------------------------------------------------------------------ 2. weight PIT theo ngay
# effective_from -> effective_to (inclusive). Ngay khong thuoc bat ky khoang nao => khong co ro.
days = P.index[(P.index >= mem.effective_from.min()) & (P.index <= pd.Timestamp("2026-06-15"))]
Wt = pd.DataFrame(0.0, index=days, columns=P.columns)
period_of = pd.Series(pd.NaT, index=days)
for rd, g in mem.groupby("rebal_date"):
    f, t = g.effective_from.iloc[0], g.effective_to.iloc[0]
    m = (days >= f) & (days <= t)
    if not m.any():
        continue
    w = g.set_index("ticker").weight
    Wt.loc[days[m], w.index] = w.values
    period_of[days[m]] = rd
Wt = Wt.loc[period_of.notna()]
days = Wt.index
print(f"[data] weight PIT: {len(days)} phien {days.min().date()} -> {days.max().date()}, "
      f"sum(w) min/max = {Wt.sum(1).min():.6f}/{Wt.sum(1).max():.6f}")

# ------------------------------------------------------------------ 3. sector-cap branch
def apply_bank_cap(w, cap):
    """Cap TONG trong so ngan hang ve `cap`, giai phong phan du sang non-bank PRO-RATA theo
    trong so hien co (= giu nguyen thu tu yieldcombo an trong weight goc), waterfall name-cap 10%.
    KHONG tinh lai yieldcombo PIT (khong co cot score trong bang) — pro-rata la xap xi bao toan rank."""
    w = w.copy()
    bmask = np.array([is_bank[c] for c in w.index])
    bw = w[bmask].sum()
    if bw <= cap + 1e-12 or bw <= 0:
        return w
    w[bmask] *= cap / bw
    free = bw - cap
    nb = w[~bmask]
    live = nb[nb > 0]
    if len(live) == 0:
        return w / w.sum()
    NAMECAP = 0.10
    add = pd.Series(0.0, index=live.index)
    rem = free
    for _ in range(50):
        room = (NAMECAP - (live + add)).clip(lower=0)
        if room.sum() <= 1e-12 or rem <= 1e-12:
            break
        base = live + add
        share = base / base.sum() * rem
        take = np.minimum(share, room)
        add += take
        rem -= take.sum()
        if take.sum() <= 1e-15:
            break
    w.loc[live.index] += add
    if rem > 1e-9:                    # non-bank het room -> tra lai cho bank (cap khong binding het)
        w[bmask] += rem * (w[bmask] / w[bmask].sum())
    return w

BR = {}
for cap in (0.40, 0.50):
    Wc = Wt.copy()
    for rd, g in Wt.groupby(period_of.loc[Wt.index]):
        w0 = g.iloc[0]
        w1 = apply_bank_cap(w0[w0 > 0], cap)
        row = pd.Series(0.0, index=Wt.columns); row[w1.index] = w1.values
        Wc.loc[g.index] = row.values
    BR[cap] = Wc
    bwt = Wc.loc[:, [is_bank[c] for c in Wc.columns]].sum(1)
    print(f"[cap{int(cap*100)}] sum(w) {Wc.sum(1).min():.6f}/{Wc.sum(1).max():.6f}; "
          f"bank weight max = {bwt.max():.4f} (phai <= {cap:.2f}+eps); name max = {Wc.max().max():.4f}")

bw_raw = Wt.loc[:, [is_bank[c] for c in Wt.columns]].sum(1)
print(f"[uncapped] bank weight: mean={bw_raw.mean():.3f} last={bw_raw.iloc[-1]:.3f} max={bw_raw.max():.3f}")

# ------------------------------------------------------------------ 4. return series
def port_ret(Wmat, sub=None):
    """Fixed-weight, THUC THI TRE T+1: trong so DUNG cho return phien t la trong so NAM GIU khi
    BUOC VAO phien t = Wmat.shift(1). effective_from == rebal_date (kiem tra BQ 2026-08-22) nen
    ap trong so moi ngay chinh rebal_date se la nhin truoc — shift(1) loai bo dieu do va khop
    dung quy uoc backtest cua repo (CLAUDE.md §Backtest: thuc thi tre T+1).
    sub=True -> chi ngan hang, False -> chi non-bank (renormalize trong nhom)."""
    cols = Wmat.columns
    if sub is not None:
        keep = np.array([is_bank[c] == sub for c in cols])
        Wm = Wmat.loc[:, cols[keep]]
    else:
        Wm = Wmat
    Wm = Wm.shift(1)
    Wm = Wm.div(Wm.sum(1).replace(0, np.nan), axis=0)
    Rm = R.reindex(index=Wm.index, columns=Wm.columns)
    # ma thieu gia phien do -> bo, renormalize phan con lai (khong gia dinh return 0)
    valid = Rm.notna() & (Wm > 0)
    Wv = Wm.where(valid, 0.0)
    s = Wv.sum(1).replace(0, np.nan)
    return (Wv.mul(Rm.fillna(0.0)).sum(1) / s)

series = {
    "base":    port_ret(Wt),
    "bank":    port_ret(Wt, sub=True),
    "nonbank": port_ret(Wt, sub=False),
    "cap40":   port_ret(BR[0.40]),
    "cap50":   port_ret(BR[0.50]),
}
rvni = vni.pct_change().reindex(days)

# ------------------------------------------------------------------ 5. SELFCHECK NAV 0 VND
# Dung 2 duong doc lap: (a) cumprod daily portfolio return; (b) so cai gia tri tung ma (VND),
# rebalance ve target moi phien. Neu logic trong so/return sai, 2 duong lech.
def nav_ledger(Wmat, cap0=1e9):
    """Duong doc lap: so cai gia tri tung ma (VND). Cung quy uoc T+1 (w cua phien truoc)."""
    Wm = Wmat.div(Wmat.sum(1).replace(0, np.nan), axis=0)
    Rm = R.reindex(index=Wm.index, columns=Wm.columns)
    nav = cap0; out = []
    for i, dt in enumerate(Wm.index):
        if i == 0:
            out.append(nav); continue
        w = Wm.iloc[i - 1]; r = Rm.iloc[i]
        ok = (w > 0) & r.notna()
        if ok.sum() == 0:
            out.append(nav); continue
        wn = w[ok] / w[ok].sum()
        val = nav * wn                     # phan bo VND theo target cuoi phien truoc
        nav = float((val * (1 + r[ok])).sum())
        out.append(nav)
    return pd.Series(out, index=Wm.index)

SC = {}
for nm, Wm in [("base", Wt), ("cap40", BR[0.40]), ("cap50", BR[0.50])]:
    r = series[nm] if nm == "base" else port_ret(Wm)
    nav_a = 1e9 * (1 + r.fillna(0)).cumprod()
    nav_b = nav_ledger(Wm)
    d = float((nav_a - nav_b).abs().max())
    SC[nm] = d
    print(f"[selfcheck NAV {nm}] max|cumprod - so_cai| = {d:,.6f} VND  (phai = 0)")

rng = np.random.default_rng(20260822)
rnd = Wt.copy() * 0.0
for rd, g in Wt.groupby(period_of.loc[Wt.index]):
    pick = rng.choice(len(Wt.columns), 30, replace=False)
    row = pd.Series(0.0, index=Wt.columns); row.iloc[pick] = 1 / 30
    rnd.loc[g.index] = row.values
rr = port_ret(rnd)
na, nb = 1e9 * (1 + rr.fillna(0)).cumprod(), nav_ledger(rnd)
SC["random"] = float((na - nb).abs().max())
print(f"[selfcheck ro NGAU NHIEN] max|cumprod - so_cai| = {SC['random']:,.6f} VND  (phai = 0)")
if max(SC.values()) > 1.0:
    print("[SELFCHECK FAIL] lech > 1 VND — DUNG, khong dung ket qua."); sys.exit(2)
print("[SELFCHECK PASS] 4/4 duong NAV khop 0 VND")

# ------------------------------------------------------------------ 6. rate bucket PIT
from deposit_rate_vn import deposit_events_df
ev = deposit_events_df()
dep = pd.merge_asof(pd.DataFrame({"time": days}), ev, on="time", direction="backward")
dep = dep.set_index("time").deposit_rate
def bucket(x):
    return "LOW" if x < 5.0 else ("MID" if x <= 6.5 else "HIGH")
bk = dep.map(bucket)
print("\n[bucket] phan bo phien:", bk.value_counts().to_dict())
runs = (bk != bk.shift()).cumsum()
epi = bk.groupby(runs).agg(["first", "size"])
print("[bucket] episodes (chu ky lien tuc):")
for g, row in epi.iterrows():
    idx = bk.index[runs == g]
    print(f"    {row['first']:5s} {idx.min().date()} -> {idx.max().date()}  ({row['size']} phien)")
n_eff = epi.groupby("first").size().to_dict()
print("[bucket] N HIEU DUNG (so episode lien tuc, KHONG phai so phien):", n_eff)

stm = st.set_index("time").state.reindex(days).ffill()
neutral = (stm == 3)
print(f"[state] NEUTRAL phien = {int(neutral.sum())}/{len(days)} ({neutral.mean():.1%})")

pd.DataFrame({"time": days, "deposit_rate": dep.values, "bucket": bk.values,
              "state": stm.values, "bank_w": bw_raw.reindex(days).values,
              **{f"r_{k}": v.reindex(days).values for k, v in series.items()},
              "r_vni": rvni.values}).to_csv(os.path.join(OUT, "a1_daily.csv"), index=False)

# ------------------------------------------------------------------ 7. thong ke theo bucket
def cagr(r):
    r = r.dropna()
    if len(r) < 20: return np.nan
    return (1 + r).prod() ** (SPY / len(r)) - 1

def blockboot(x, y, L=20, B=2000, seed=7):
    """CI cho excess CAGR (geometric) bang block-bootstrap L=20 tren CAP (x,y) dong bo."""
    x, y = x.align(y, join="inner")
    m = x.notna() & y.notna()
    x, y = x[m].values, y[m].values
    n = len(x)
    if n < 3 * L: return (np.nan, np.nan, np.nan)
    rng = np.random.default_rng(seed); nb = int(np.ceil(n / L)); out = np.empty(B)
    for b in range(B):
        st_ = rng.integers(0, n - L + 1, nb)
        ix = np.concatenate([np.arange(s, s + L) for s in st_])[:n]
        gx = (1 + x[ix]).prod() ** (SPY / n) - 1
        gy = (1 + y[ix]).prod() ** (SPY / n) - 1
        out[b] = gx - gy
    return (float(np.percentile(out, 5)), float(np.percentile(out, 50)), float(np.percentile(out, 95)))

def block(sel, tag, nb_epi):
    row = {"scope": tag, "n_days": int(sel.sum()), "n_episodes": nb_epi,
           "VNI_cagr": cagr(rvni[sel])}
    for k, v in series.items():
        row[f"{k}_cagr"] = cagr(v[sel])
        row[f"{k}_ex"] = row[f"{k}_cagr"] - row["VNI_cagr"]
    lo, md, hi = blockboot(series["base"][sel], rvni[sel])
    row["base_ex_p5"], row["base_ex_p50"], row["base_ex_p95"] = lo, md, hi
    lo, md, hi = blockboot(series["cap40"][sel], series["base"][sel])
    row["cap40_vs_base_p5"], row["cap40_vs_base_p50"], row["cap40_vs_base_p95"] = lo, md, hi
    lo, md, hi = blockboot(series["cap50"][sel], series["base"][sel])
    row["cap50_vs_base_p5"], row["cap50_vs_base_p50"], row["cap50_vs_base_p95"] = lo, md, hi
    row["bank_w_mean"] = float(bw_raw.reindex(days)[sel].mean())
    return row

rows = []
for b in ["LOW", "MID", "HIGH"]:
    sel = (bk == b)
    rows.append(block(sel, f"ALL/{b}", n_eff.get(b, 0)))
rows.append(block(pd.Series(True, index=days), "ALL/*", len(epi)))
for b in ["LOW", "MID", "HIGH"]:
    sel = (bk == b) & neutral
    ne = ((bk == b) & neutral).astype(int)
    ne = int(((ne.diff() == 1)).sum() + (1 if ne.iloc[0] == 1 else 0))
    rows.append(block(sel, f"NEUTRAL/{b}", ne))
sel = neutral
ne = neutral.astype(int); ne = int((ne.diff() == 1).sum() + (1 if ne.iloc[0] else 0))
rows.append(block(sel, "NEUTRAL/*", ne))
T = pd.DataFrame(rows)
T.to_csv(os.path.join(OUT, "a1_bucket_table.csv"), index=False)

pd.set_option("display.width", 250, "display.max_columns", 60)
print("\n=== A1 BANG CHINH — excess CAGR vs VNINDEX theo rate bucket (pp/nam) ===")
show = T[["scope", "n_days", "n_episodes", "bank_w_mean", "VNI_cagr", "base_cagr", "base_ex",
          "bank_ex", "nonbank_ex", "cap40_ex", "cap50_ex",
          "base_ex_p5", "base_ex_p95", "cap40_vs_base_p50", "cap50_vs_base_p50"]].copy()
for c in show.columns:
    if c not in ("scope", "n_days", "n_episodes"):
        show[c] = (show[c] * 100).round(2)
print(show.to_string(index=False))

# ------------------------------------------------------------------ 8. LOO theo nam
print("\n=== A1 LOO theo nam (drop 1 nam, excess base vs VNI, pp/nam) ===")
yrs = sorted(set(days.year))
loo = []
for b in ["LOW", "MID", "HIGH", "*"]:
    selb = pd.Series(True, index=days) if b == "*" else (bk == b)
    full = cagr(series["base"][selb]) - cagr(rvni[selb])
    vals = {}
    yr_s = pd.Series(days.year, index=days)
    for y in yrs:
        if y < 2018: continue
        if int((selb & (yr_s == y)).sum()) < 40:
            continue          # nam nay khong co phien trong bucket -> drop no la KHONG-OP, bo qua
        s2 = selb & (yr_s != y)
        if s2.sum() < 60: continue
        vals[y] = cagr(series["base"][s2]) - cagr(rvni[s2])
    if not vals: continue
    pos = sum(1 for v in vals.values() if v > 0)
    loo.append({"bucket": b, "full_ex_pp": round(full * 100, 2), "n_loo": len(vals),
                "n_pos": pos, "min_pp": round(min(vals.values()) * 100, 2),
                "max_pp": round(max(vals.values()) * 100, 2),
                "detail": {k: round(v * 100, 2) for k, v in vals.items()}})
L = pd.DataFrame(loo)
print(L[["bucket", "full_ex_pp", "n_loo", "n_pos", "min_pp", "max_pp"]].to_string(index=False))
for r in loo:
    print(f"   {r['bucket']:5s} {r['detail']}")
L.to_csv(os.path.join(OUT, "a1_loo.csv"), index=False)

# per-year excess (bo sung, de doc dong luc)
print("\n=== excess base vs VNI theo NAM (pp) + bucket chu dao trong nam ===")
py = []
for y in yrs:
    s = pd.Series(days.year, index=days) == y
    if s.sum() < 40: continue
    py.append({"year": y, "n": int(s.sum()), "bucket_mode": bk[s].mode().iloc[0],
               "dep_mean": round(float(dep[s].mean()), 2),
               "base_ex_pp": round((cagr(series["base"][s]) - cagr(rvni[s])) * 100, 2),
               "bank_ex_pp": round((cagr(series["bank"][s]) - cagr(rvni[s])) * 100, 2),
               "nonbank_ex_pp": round((cagr(series["nonbank"][s]) - cagr(rvni[s])) * 100, 2),
               "cap40_minus_base_pp": round((cagr(series["cap40"][s]) - cagr(series["base"][s])) * 100, 2)})
PY = pd.DataFrame(py); print(PY.to_string(index=False))
PY.to_csv(os.path.join(OUT, "a1_peryear.csv"), index=False)
# ------------------------------------------------------------------ 9. episode-level (N THAT)
print("\n=== A1 EPISODE-LEVEL — moi chu ky lai suat lien tuc la 1 quan sat doc lap ===")
er = []
for g in epi.index:
    idx = bk.index[runs == g]
    sel = pd.Series(days.isin(idx), index=days)
    if sel.sum() < 40: continue
    er.append({"bucket": bk[idx[0]], "from": str(idx.min().date()), "to": str(idx.max().date()),
               "n": int(sel.sum()), "bank_w": round(float(bw_raw.reindex(days)[sel].mean()), 3),
               "VNI_pp": round(cagr(rvni[sel]) * 100, 2),
               "base_pp": round(cagr(series["base"][sel]) * 100, 2),
               "base_ex_pp": round((cagr(series["base"][sel]) - cagr(rvni[sel])) * 100, 2),
               "bank_ex_pp": round((cagr(series["bank"][sel]) - cagr(rvni[sel])) * 100, 2),
               "nonbank_ex_pp": round((cagr(series["nonbank"][sel]) - cagr(rvni[sel])) * 100, 2),
               "cap40_minus_base_pp": round((cagr(series["cap40"][sel]) - cagr(series["base"][sel])) * 100, 2),
               "cap50_minus_base_pp": round((cagr(series["cap50"][sel]) - cagr(series["base"][sel])) * 100, 2)})
E = pd.DataFrame(er); print(E.to_string(index=False))
E.to_csv(os.path.join(OUT, "a1_episodes.csv"), index=False)
print("\n[done] outputs:", OUT)
