# -*- coding: utf-8 -*-
"""custom30v_hybrid.py — does a WEEKLY/MONTHLY 8L-rating overlay improve custom30V?

PROPOSAL (user, 2026-07-02): keep custom30V exactly (yieldcombo=rank(1/PE)+rank(1/PCF),
top-30, namecap 0.10, gate rating<=3, quarterly q2m5 rebal) but BETWEEN quarterly rebals,
every week (or month), look for names that have RISEN into 8L golden/strong tier (rating<=2)
and are NOT in the basket; if such a candidate is MATERIALLY better rated than the weakest
basket names (by yieldcombo rank), swap in up to 2. Goal: faster basket refresh than quarterly.

METHOD (faithful, auditable, all from raw BQ):
  * BASELINE = custom_basket.build_pit(yieldcombo, q2m5, gate=3, namecap, 0.10) — AUTHORITATIVE.
    Its per-quarter membership seeds each quarter of the hybrid (base is byte-identical).
  * OVERLAY runs on a weekly / monthly trading-day grid WITHIN each quarter (resets to the
    baseline pick at every q2m5 rebal, so the base selector is untouched).
  * yieldcombo scores are quarterly (fundamentals only update quarterly) -> computed over the
    top-80 liquid names per source-quarter so a newly-upgraded name still has a value score.
  * Gating for candidate eligibility uses rating_asof(overlay_date) (FRESH ratings) — this is the
    only thing that changes intra-quarter and is what makes "rising into rating<=2" meaningful.
  * Swap rule: OUT = the (up to) 2 lowest-yieldcombo basket names; IN = eligible rating<=2
    candidates (not in basket) with best yieldcombo. Execute a swap iff
    rating(cand) <= rating(weak) - NOTCH (material rating improvement).
  * Re-chain the namecap cap-weighted index IDENTICALLY to build_pit over the union daily panel.
    Self-check: re-chained baseline must equal build_pit's own level series (audit_baseline_diff).
  * TC: baseline basket index is raw (like custom30v_select_audit). Hybrid reported BOTH gross
    (raw selection effect) and net of the EXTRA swap turnover (TC=0.1%/side, sum|dw|~2*nswap/30).

Comparison: BASKET INDEX metrics (isolates the selector) — CAGR/Sharpe/MaxDD/Calmar over
FULL 2014->now / IS 2014-2019 / OOS 2020->now walk-forward. This mirrors the accepted
custom30v_select_audit.py methodology for "does selector X beat yieldcombo".
"""
import os, sys, bisect, numpy as np, pandas as pd
WORKDIR = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude"); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import bq
import custom_basket as cb

START, END = "2014-01-01", "2026-06-19"
TOP_N, POOL, NAME_CAP, GATE = 30, 60, 0.10, 3
LIQ_TOP = 80                       # yieldcombo score computed over this many liquid names / quarter
TC_SIDE = 0.001                    # 0.1% per side, applied to sum|dw| of the extra swap turnover
MAX_SWAPS = 2

# ---------- metrics ----------
def metrics(lvl):
    s = pd.Series(lvl).sort_index(); s.index = pd.to_datetime(s.index)
    r = s.pct_change().dropna()
    if len(r) < 5: return dict(CAGR=float('nan'), Sharpe=float('nan'), MaxDD=float('nan'), Calmar=float('nan'))
    yrs = (s.index[-1]-s.index[0]).days/365.25
    cagr = (s.iloc[-1]/s.iloc[0])**(1/yrs)-1
    spd = len(r)/yrs
    sharpe = r.mean()/r.std()*np.sqrt(spd) if r.std()>0 else 0
    dd = (s/s.cummax()-1).min()
    return dict(CAGR=cagr*100, Sharpe=sharpe, MaxDD=dd*100, Calmar=(cagr*100)/abs(dd*100) if dd<0 else 0)

def window(series, a, b):
    s = pd.Series(series).sort_index(); s.index = pd.to_datetime(s.index)
    if a is not None: s = s[s.index >= pd.Timestamp(a)]
    if b is not None: s = s[s.index <= pd.Timestamp(b)]
    return s

# ---------- 1) baseline (authoritative) ----------
print("[1] build_pit baseline (custom30V yieldcombo, q2m5, gate3, namecap0.10)...")
os.environ["BASKET_SELECT"] = "yieldcombo"
lvl_base_bp, _, memdf, _ = cb.build_pit(bq, START, END, quality="none", rebal="q2m5",
                                        gate_rating=GATE, weight_scheme="namecap")
memdf["rebal_date"] = pd.to_datetime(memdf["rebal_date"])
rebal_dates = sorted(memdf["rebal_date"].unique())
base_members = {d: list(g.sort_values("liq_rank")["ticker"]) for d, g in memdf.groupby("rebal_date")}
print(f"    {len(rebal_dates)} quarterly rebals; baseline union={memdf.ticker.nunique()} names")

# ---------- 2) quarterly inputs for the overlay ----------
print("[2] quarterly liquidity / ratings / yield pivots...")
qliq = bq(f"""SELECT t.ticker, DATE_TRUNC(t.time, QUARTER) AS q, AVG(t.Volume_3M_P50*t.Close) AS liq, COUNT(*) nd
FROM tav2_bq.ticker t
WHERE t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)
  AND t.ICB_Code IS NOT NULL
  AND t.time >= DATE_SUB(DATE '{START}', INTERVAL 380 DAY) AND t.time <= DATE '{END}'
GROUP BY t.ticker, q HAVING nd >= 20""")
qliq["q"] = pd.to_datetime(qliq["q"])
liq_piv = qliq.pivot_table(index="q", columns="ticker", values="liq")

rat = bq(f"SELECT r.ticker, r.time, r.rating FROM tav2_bq.fa_ratings_8l r WHERE r.time <= DATE '{END}' ORDER BY r.ticker, r.time")
rat["time"] = pd.to_datetime(rat["time"])
rat_by_tk = {tk: (list(g["time"]), list(g["rating"])) for tk, g in rat.groupby("ticker")}
def rating_asof(tk, d):
    e = rat_by_tk.get(tk)
    if not e: return np.nan
    i = bisect.bisect_right(e[0], d) - 1
    return float(e[1][i]) if i >= 0 else np.nan

def yield_piv(col):
    y = bq(f"""SELECT t.ticker, DATE_TRUNC(t.time, QUARTER) AS q, AVG(SAFE_DIVIDE(1, t.{col})) AS y
FROM tav2_bq.ticker t WHERE t.{col} > 0 AND t.time BETWEEN DATE '{START}' AND DATE '{END}'
GROUP BY t.ticker, q""")
    y["q"] = pd.to_datetime(y["q"]); return y.pivot_table(index="q", columns="ticker", values="y")
pe_piv, pcf_piv = yield_piv("PE"), yield_piv("PCF")

# per rebal: source quarter + yieldcombo score over top-LIQ_TOP liquid names of that source quarter
def src_quarter(d):
    qd = pd.Timestamp(d).to_period("Q").start_time
    prior = [qq for qq in liq_piv.index if qq < qd]
    return max(prior) if prior else (qd if qd in liq_piv.index else None)

yc_score = {}   # rebal_date -> {ticker: rank(1/PE)+rank(1/PCF)}  over top-LIQ_TOP liquid names
liq_pool = {}   # rebal_date -> list of liquid names (for candidate universe)
for d in rebal_dates:
    sq = src_quarter(d)
    if sq is None: yc_score[d] = {}; liq_pool[d] = []; continue
    liq_row = liq_piv.loc[sq].dropna().sort_values(ascending=False)
    names = list(liq_row.index[:LIQ_TOP])
    pe_s  = pe_piv.loc[sq]  if sq in pe_piv.index  else pd.Series(dtype=float)
    pcf_s = pcf_piv.loc[sq] if sq in pcf_piv.index else pd.Series(dtype=float)
    pe_r  = pd.Series({t: pe_s.get(t, np.nan)  for t in names}).rank(pct=True).fillna(0.5)
    pcf_r = pd.Series({t: pcf_s.get(t, np.nan) for t in names}).rank(pct=True).fillna(0.5)
    yc_score[d] = {t: float(pe_r[t] + pcf_r[t]) for t in names}
    liq_pool[d] = names

# ---------- 3) daily price panel for the UNION (baseline + any candidate ever eligible) ----------
# candidate universe over all quarters = liquid pool names (a candidate can only come from here)
cand_union = set().union(*[set(v) for v in liq_pool.values()]) if liq_pool else set()
union = sorted(set(memdf.ticker.unique()) | cand_union)
print(f"[3] daily mcap panel for union={len(union)} names...")
inlist = ",".join(f"'{x}'" for x in union)
bx = bq(f"""WITH fin AS (
  SELECT f.ticker, f.time AS ftime, f.OShares,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS nft
  FROM tav2_bq.ticker_financial AS f WHERE f.OShares IS NOT NULL)
SELECT t.ticker, t.time, t.Close, fin.OShares
FROM tav2_bq.ticker AS t
LEFT JOIN fin ON fin.ticker=t.ticker AND t.time>=fin.ftime AND (fin.nft IS NULL OR t.time<fin.nft)
WHERE t.ticker IN ({inlist})
  AND t.time >= DATE_SUB(DATE '{START}', INTERVAL 10 DAY) AND t.time <= DATE '{END}'""")
bx["time"] = pd.to_datetime(bx["time"]); bx = bx.sort_values(["ticker", "time"])
bx["OShares"] = bx.groupby("ticker")["OShares"].ffill().bfill()
bx["mcap"] = bx["Close"] * bx["OShares"]
mcap = bx.pivot_table(index="time", columns="ticker", values="mcap").sort_index()
idx_dates = list(mcap.index)

# ---------- 4) chaining (identical to build_pit namecap path) ----------
def _cap_names(w, cap):
    w = np.array(w, dtype=float); s = w.sum()
    if s <= 0: return w
    w = w / s
    for _ in range(100):
        over = w > cap + 1e-12
        if not over.any(): break
        excess = float((w[over]-cap).sum()); w[over] = cap
        under = ~over; us = float(w[under].sum())
        if us <= 1e-12: break
        w[under] = w[under] + excess*w[under]/us
    return w

def chain(members, swap_tc_by_date=None):
    """members: dict date->list[ticker] (namecap, equal qmult=1). Returns level dict."""
    reb = sorted(members.keys())
    def active(d):
        i = bisect.bisect_right(reb, d) - 1
        return reb[i] if i >= 0 else None
    ret = pd.Series(0.0, index=idx_dates); prev = None
    for d in idx_dates:
        aq = active(d)
        if aq is None or prev is None: prev = d; continue
        tks = [t for t in members.get(aq, []) if t in mcap.columns]
        if tks:
            today = mcap.loc[d, tks].values.astype(float)
            yest  = mcap.loc[prev, tks].values.astype(float)
            valid = ~np.isnan(today) & ~np.isnan(yest)
            if valid.sum() > 0:
                yv = yest[valid]
                W = _cap_names(yv, NAME_CAP)
                r = today[valid]/yv - 1.0
                ret.loc[d] = float(np.nansum(W*r))
        if swap_tc_by_date and d in swap_tc_by_date:
            ret.loc[d] -= swap_tc_by_date[d]
        prev = d
    lvl = cb.BASE_LEVEL * (1.0 + ret).cumprod()
    return {t: float(v) for t, v in zip(lvl.index, lvl.values)}

# self-check: re-chained baseline == build_pit baseline
base_members_daily = dict(base_members)
lvl_base = chain(base_members_daily)
_a = pd.Series(lvl_base); _b = pd.Series(lvl_base_bp)
_common = _a.index.intersection(_b.index)
audit_baseline_diff = float((_a[_common]/_b[_common] - 1).abs().max())
print(f"[4] baseline re-chain self-check: max rel diff vs build_pit = {audit_baseline_diff:.2e}")

# ---------- 5) overlay grids ----------
dates_arr = np.array(idx_dates, dtype="datetime64[ns]")
def snap(ts):
    i = int(np.searchsorted(dates_arr, np.datetime64(pd.Timestamp(ts)), side="left"))
    return pd.Timestamp(dates_arr[i]) if i < len(dates_arr) else None

def weekly_grid():
    df = pd.Series(idx_dates, index=idx_dates)
    return sorted(set(df.groupby(pd.Grouper(freq="W-MON")).min().dropna().tolist()))
def monthly_grid():
    df = pd.Series(idx_dates, index=idx_dates)
    return sorted(set(df.groupby(pd.Grouper(freq="MS")).min().dropna().tolist()))

def build_hybrid(cadence, notch, require_cheaper=False):
    grid = weekly_grid() if cadence == "weekly" else monthly_grid()
    members = {}; swap_tc = {}
    n_swaps_total = 0
    for qi, rb in enumerate(rebal_dates):
        nxt = rebal_dates[qi+1] if qi+1 < len(rebal_dates) else pd.Timestamp("2100-01-01")
        cur = list(base_members[rb])
        members[rb] = list(cur)                                   # quarter opens on baseline pick
        sc = yc_score.get(rb, {}); pool = set(liq_pool.get(rb, []))
        for gd in grid:
            if gd <= rb or gd >= nxt: continue
            # weakest 2 basket names by yieldcombo (lowest score first)
            weak = sorted(cur, key=lambda t: sc.get(t, 0.0))
            # eligible candidates: liquid pool, rating<=2 as-of gd, not in basket, has a yield score
            cand = [t for t in pool if t not in cur and (rating_asof(t, gd) <= 2)]
            cand = sorted(cand, key=lambda t: sc.get(t, -1.0), reverse=True)
            swaps = 0; changed = False
            wi, ci = 0, 0
            while swaps < MAX_SWAPS and ci < len(cand) and wi < len(weak):
                c = cand[ci]; w = weak[wi]
                rc, rw = rating_asof(c, gd), rating_asof(w, gd)
                ok = pd.notna(rc) and pd.notna(rw) and (rc <= rw - notch)
                if require_cheaper: ok = ok and (sc.get(c, -1.0) >= sc.get(w, 0.0))
                if ok:
                    cur.remove(w); cur.append(c); swaps += 1; changed = True; wi += 1; ci += 1
                else:
                    wi += 1                                       # this weak name not swappable; try next
                    if wi >= len(weak): break
            if changed:
                members[gd] = list(cur)
                # extra swap turnover cost: sell w + buy c per swap ~ 2*swaps/TOP_N weight
                swap_tc[gd] = TC_SIDE * (2.0*swaps/TOP_N)
                n_swaps_total += swaps
    return members, swap_tc, n_swaps_total

# ---------- 6) run variants ----------
VARIANTS = [
    ("weekly",  1, False, "H_wk_n1"),
    ("weekly",  2, False, "H_wk_n2"),
    ("weekly",  1, True,  "H_wk_n1_cheaper"),
    ("monthly", 1, False, "H_mo_n1"),
]
WINS = [("FULL 2014->now", None, None),
        ("IS 2014-2019", None, "2019-12-31"),
        ("OOS 2020->now", "2020-01-01", None)]

print("\n[5] building & chaining hybrid variants...")
results = {"custom30V_base": (lvl_base, None, 0)}
for cadence, notch, req, name in VARIANTS:
    mem, stc, ns = build_hybrid(cadence, notch, req)
    lvl_gross = chain(mem)                       # raw selection effect
    lvl_net   = chain(mem, stc)                  # with extra swap TC
    results[name] = (lvl_gross, lvl_net, ns)
    print(f"    {name:<18} swaps={ns:4d}  (cadence={cadence}, notch>={notch}, cheaper_guard={req})")

# ---------- 7) report ----------
def row(lbl, lvl):
    parts = []
    for tag, a, b in WINS:
        m = metrics(window(lvl, a, b))
        parts.append(f"{m['CAGR']:7.2f} {m['Sharpe']:5.2f} {m['MaxDD']:7.1f} {m['Calmar']:5.2f}")
    return f"  {lbl:<20} " + " | ".join(parts)

print("\n" + "="*118)
print("RESULT — custom30V hybrid overlay vs baseline | BASKET INDEX (selector-isolated), walk-forward")
print(f"baseline re-chain self-check max rel diff = {audit_baseline_diff:.2e} (0 => faithful)")
print("="*118)
hdr = "  " + " "*20 + " " + " | ".join(f"{t:<26}" for t,_,_ in WINS)
print(hdr); print("  " + " "*20 + " " + " | ".join(" CAGR%  Shrp  MaxDD%  Cal " for _ in WINS))
print(row("custom30V_base", lvl_base))
for _,_,_,name in VARIANTS:
    print(row(name+" (gross)", results[name][0]))
    print(row(name+" (net-TC)", results[name][1]))

print("\n--- delta vs baseline (Full CAGR / OOS CAGR, net-of-swap-TC) ---")
b_full = metrics(window(lvl_base, None, None))["CAGR"]; b_oos = metrics(window(lvl_base,"2020-01-01",None))["CAGR"]
for _,_,_,name in VARIANTS:
    g = results[name][1]
    d_full = metrics(window(g,None,None))["CAGR"] - b_full
    d_oos  = metrics(window(g,"2020-01-01",None))["CAGR"] - b_oos
    print(f"  {name:<18} dFull {d_full:+.2f}pp   dOOS {d_oos:+.2f}pp   swaps={results[name][2]}")
print("\n[done]")
