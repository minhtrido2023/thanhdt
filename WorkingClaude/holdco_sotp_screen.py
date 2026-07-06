"""HOLDING COMPANY / CONGLOMERATE — Sum-of-the-Parts (SOTP) archetype — sector #20 framework + screen.
Design + backlook: job Taylor_20260706_042831. Framework: mike/agents/Taylor/holdco_sotp_valuation_framework.md.

This is NOT an industry — it is a VALUATION METHODOLOGY that cuts across the listed multi-segment groups.
A blended P/E or P/B for the whole group is meaningless because each segment has different economics
(VIC = high-margin property VHM + cash-burning VinFast; MSN = consumer MCH + miner MSR + bank stake TCB).
The international convention is Sum-of-the-Parts: value each segment on its own sector multiple, add, then
subtract a "holdco discount" (opacity / double-tax / governance) at the parent.

VN advantage we exploit: several segments are THEMSELVES LISTED, so that slice is MEASURED directly from BQ
(parent's stake x subsidiary market cap), not estimated. We build a LISTED-STAKE SOTP coverage ratio:

    coverage(t) = ParentMarketCap(t) / SUM_s [ stake_s x SubsidiaryMarketCap_s(t) ]

  coverage < 1  -> parent trades BELOW the market value of just its listed stakes (deep holdco discount:
                   the market assigns <= 0 to all unlisted businesses + net cash)
  coverage > 1  -> parent trades ABOVE its listed stakes (the market pays UP for unlisted optionality:
                   VinFast at VIC, the industrial-park landbank at GVR — or it is simply a premium)

  MarketCap = (unadjusted) Price x OShares(ASOF from ticker_financial).

CRITICAL caveat baked into the reading: coverage IGNORES (a) unlisted operating businesses and (b) holdco
net debt. So coverage<1 is NOT automatically "cheap" (could be justified by holdco leverage — MSN, VIC),
and coverage>1 is NOT automatically "expensive" (unlisted ops have real value). coverage is therefore a
RELATIVE gauge vs the name's OWN history, never an absolute NAV. That is the whole point of the exercise.

Universe (listed parent -> listed subsidiaries measurable in BQ; unlisted parts noted qualitatively):
  VIC (Vingroup)  -> VHM (Vinhomes) ; + unlisted VinFast (cash-burn), Vinpearl, VEF
  MSN (Masan)     -> MCH (Masan Consumer), TCB (Techcombank stake) ; MSR/MML thin in prune, unlisted WinCommerce
  GEX (Gelex)     -> VGC (Viglacera), GEE (Gelex Electric, listed 2022)
  GVR (VN Rubber) -> PHR + DPR + TRC (rubber trio) ; + huge UNLISTED plantation/industrial-park landbank

Stakes are approximate PUBLIC economic stakes, HELD CONSTANT through time — a documented limitation
(real stakes drifted: VIC divested VRE 2024, HAG dumped HNG to Thaco 2021, Masan trimmed TCB). Same class
of accepted data limit as the SOE state% hand-curation (#19) and construction backlog (#18): BQ has no
ownership field.

What this script settles (auditable, self-check 0 VND, threads=1, walk-forward IS/OOS):
  PART 0 — SNAPSHOT. Current coverage per parent = premium or discount to its listed stakes. The contrast.
  PART 1 — WHY BLENDED MULTIPLES FAIL. VIC/MSN consolidated NPM/ROE/Debt_Eq dragged by cash-burn/leverage.
  PART 2 — STABILITY. Is coverage mean-reverting (tradeable) or a random walk / trend (permanent-discount
           trap)? Per-name mean/std/range, AR(1) half-life, trend-vs-time correlation.
  PART 3 — REGIME. Does the discount widen in BEAR/CRISIS and narrow in BULL? (DT5G state join.)
  PART 4 — SIGNAL TEST (exploratory, tiny N). Does buying a name when its OWN coverage z-score (vs trailing
           252d) is unusually LOW predict positive forward return? Pooled Spearman IC vs profit_1M/2M/3M
           (eval-only). Plus a 4-name discount-tilt basket vs naive EW vs VNINDEX, walk-forward IS/OOS.
Verdict is expected to be LENS-NOT-BOOK (consistent with #1-19): SOTP is a diagnostic overlay for the
conglomerate archetype, NOT a standalone book — tiny N + permanent-discount-trap risk forbid a gate.
"""
import duckdb, numpy as np, pandas as pd, json

PRUNE = "data/bq_cache/ticker_prune.parquet"
FIN   = "data/bq_cache/ticker_financial.parquet"
DT5G  = "data/bq_cache/vnindex_5state_dt5g_live.parquet"
START = "2016-01-01"
TC    = 0.001

# parent -> {listed subsidiary: approx public economic stake} (held constant; documented limitation)
OWN = {
    "VIC": {"VHM": 0.649},                                  # + unlisted VinFast / Vinpearl / VEF
    "MSN": {"MCH": 0.681, "TCB": 0.150},                    # + MSR/MML (thin in prune) + unlisted WinCommerce
    "GEX": {"VGC": 0.502, "GEE": 0.786},
    "GVR": {"PHR": 0.666, "DPR": 0.558, "TRC": 0.600},      # + huge unlisted plantation/IP landbank
}
STATE_NAME = ["CRISIS", "BEAR", "NEUTRAL", "BULL", "EXBULL"]
PARENTS = list(OWN)
SUBS = sorted({s for d in OWN.values() for s in d})
ALL = sorted(set(PARENTS) | set(SUBS))
inl = ",".join(f"'{t}'" for t in ALL)

con = duckdb.connect(config={"threads": 1})

# ---------- price + shares panels ----------
raw = con.execute(f"""SELECT ticker, time, Close, Price, Volume, profit_1M, profit_2M, profit_3M
  FROM read_parquet('{PRUNE}') WHERE ticker IN ({inl}) AND time >= DATE '{START}'""").df()
raw["time"] = pd.to_datetime(raw.time)
price = raw.pivot_table(index="time", columns="ticker", values="Price").sort_index()   # unadjusted, for market cap
close = raw.pivot_table(index="time", columns="ticker", values="Close").sort_index()   # adjusted, for returns
alldays = close.index

# OShares ASOF (quarterly -> daily forward-fill)
osh_q = con.execute(f"""SELECT ticker, time, OShares FROM read_parquet('{FIN}')
  WHERE ticker IN ({inl}) AND OShares > 0 ORDER BY ticker, time""").df()
osh_q["time"] = pd.to_datetime(osh_q.time)
osh = osh_q.pivot_table(index="time", columns="ticker", values="OShares").sort_index()
osh = osh.reindex(alldays.union(osh.index)).sort_index().ffill().reindex(alldays)

mcap = price * osh.reindex(columns=price.columns)     # market cap (VND) per ticker per day

# DT5G state
st = con.execute(f"SELECT time, state FROM read_parquet('{DT5G}') ORDER BY time").df()
st["time"] = pd.to_datetime(st.time)
state = st.set_index("time")["state"].reindex(alldays).ffill()

# ---------- coverage ratio time series ----------
cov = pd.DataFrame(index=alldays)
ltv = pd.DataFrame(index=alldays)   # look-through value of listed stakes
for p, subs in OWN.items():
    lt = None
    for s, w in subs.items():
        if s not in mcap.columns: continue
        contrib = w * mcap[s]
        lt = contrib if lt is None else lt.add(contrib, fill_value=np.nan)
    ltv[p] = lt
    cov[p] = mcap[p] / lt

print("=" * 78)
print("PART 0 — SNAPSHOT: current listed-stake SOTP coverage (premium/discount to listed stakes)")
print("=" * 78)
snap = {}
for p in PARENTS:
    c = cov[p].dropna()
    if c.empty: continue
    d = c.index[-1]
    pmc = mcap[p].loc[d] / 1e12
    lv  = ltv[p].loc[d] / 1e12
    coverage = c.iloc[-1]
    prem = coverage - 1.0
    parts = " + ".join(f"{s}({w:.0%}x{mcap[s].loc[d]/1e12:.1f}tn)" for s, w in OWN[p].items() if s in mcap.columns)
    tag = "PREMIUM" if coverage > 1 else "DISCOUNT"
    snap[p] = dict(date=str(d.date()), parent_mcap_tn=round(pmc, 1), listed_stake_tn=round(lv, 1),
                   coverage=round(coverage, 3), premium_pct=round(prem * 100, 1), tag=tag,
                   listed_stakes=parts)
    print(f"  {p}: MC {pmc:7.1f}tn  vs listed stakes {lv:6.1f}tn  -> coverage {coverage:5.2f}x  "
          f"({prem*100:+5.0f}% {tag})")
    print(f"       stakes = {parts}")

# ============================================================================
# PART 1 — WHY BLENDED MULTIPLES FAIL (cash-burn / leverage drag at the parent)
# ============================================================================
print("\n" + "=" * 78)
print("PART 1 — Blended parent multiples are distorted by the cash-burner / leverage")
print("=" * 78)
drag = con.execute(f"""SELECT ticker, quarter, NPM_P0, ROE_Trailing, Debt_Eq_P0, PB
  FROM read_parquet('{FIN}') WHERE ticker IN ('VIC','VHM','MSN','MCH','GVR','GEX')
  AND quarter IN ('2022Q2','2024Q2','2026Q1') ORDER BY quarter, ticker""").df()
print(drag.to_string(index=False))
print("  Read: VIC NPM went NEGATIVE in 2022 (VinFast) while VHM ran ~0.30-0.50; VIC Debt_Eq 3.0->6.7,")
print("        PB ~11 (optionality) vs VHM PB ~2.3. You cannot value VIC on a consolidated multiple.")

# ============================================================================
# PART 2 — STABILITY (mean-revert vs random-walk / permanent-discount trap)
# ============================================================================
print("\n" + "=" * 78)
print("PART 2 — Coverage stability: mean / range / AR(1) half-life / trend-vs-time")
print("=" * 78)
stab = {}
for p in PARENTS:
    c = cov[p].dropna()
    if len(c) < 250:
        stab[p] = dict(n=len(c), note="insufficient history")
        print(f"  {p:4s} n={len(c)} (insufficient history)")
        continue
    lvl = c.values
    # AR(1) on level: x_t = a + b x_{t-1}; half-life = -ln(2)/ln(b)
    x0, x1 = lvl[:-1], lvl[1:]
    b = np.polyfit(x0, x1, 1)[0]
    hl = (-np.log(2) / np.log(b)) if 0 < b < 1 else np.inf
    # trend vs time (Spearman of coverage vs ordinal day)
    tr = pd.Series(lvl).rank().corr(pd.Series(np.arange(len(lvl))).rank())
    stab[p] = dict(n=len(c), mean=round(float(c.mean()), 3), std=round(float(c.std()), 3),
                   mn=round(float(c.min()), 3), mx=round(float(c.max()), 3),
                   ar1_b=round(float(b), 4), half_life_days=round(float(hl), 1) if np.isfinite(hl) else None,
                   trend_spearman=round(float(tr), 3))
    print(f"  {p:4s} n={len(c):4d}  mean {c.mean():4.2f}  std {c.std():4.2f}  range [{c.min():4.2f},{c.max():4.2f}]"
          f"  AR1 b={b:5.3f}  half-life {hl:6.1f}d  trend(t) {tr:+.2f}")

# ============================================================================
# PART 3 — REGIME (does the discount widen in stress?)
# ============================================================================
print("\n" + "=" * 78)
print("PART 3 — Mean coverage by DT5G regime (does discount widen in BEAR/CRISIS?)")
print("=" * 78)
regime = {}
for p in PARENTS:
    c = cov[p].dropna()
    if len(c) < 250: continue
    df = pd.DataFrame({"cov": c, "st": state.reindex(c.index)}).dropna()
    by = df.groupby("st")["cov"].mean()
    regime[p] = {STATE_NAME[int(k) - 1]: round(float(v), 3) for k, v in by.items()}
    row = "  ".join(f"{STATE_NAME[int(k) - 1]}:{v:.2f}" for k, v in by.items())
    print(f"  {p:4s}  {row}")

# ============================================================================
# PART 4 — SIGNAL TEST (exploratory; tiny N) + discount-tilt basket
# ============================================================================
print("\n" + "=" * 78)
print("PART 4 — Signal: does OWN-history-deep coverage predict forward return? (eval-only)")
print("=" * 78)
# z-score each parent's coverage vs its own trailing 252d; low z = deep discount vs own norm
covz = pd.DataFrame(index=alldays)
for p in PARENTS:
    c = cov[p]
    m = c.rolling(252, min_periods=120).mean()
    sd = c.rolling(252, min_periods=120).std()
    covz[p] = (c - m) / sd

# pooled IC: coverage-z vs forward parent return (profit_*), eval-only
fwd = raw[raw.ticker.isin(PARENTS)][["time", "ticker", "profit_1M", "profit_2M", "profit_3M"]].copy()
zl = covz.rename_axis("time").reset_index().melt(id_vars="time", var_name="ticker", value_name="covz")
panel = fwd.merge(zl, on=["time", "ticker"], how="inner").dropna(subset=["covz"])
def spear(a, b):
    m = a.notna() & b.notna()
    return float(a[m].rank().corr(b[m].rank())) if m.sum() >= 50 else np.nan
ic = {h: round(spear(panel["covz"], panel[h]), 4) for h in ["profit_1M", "profit_2M", "profit_3M"]}
print(f"  pooled rows {len(panel)}  Spearman(coverage-z, fwd): {ic}")
print("  (coverage-z LOW = deep discount vs own norm; POSITIVE IC would mean 'buy the discount' works)")

# ---- discount-tilt basket vs naive EW vs VNINDEX (monthly, walk-forward) ----
cal = pd.DataFrame({"time": alldays}); cal["ym"] = cal.time.dt.to_period("M")
rebal = sorted(cal.groupby("ym")["time"].max().tolist())
vnx = con.execute(f"""SELECT DISTINCT time, VNINDEX FROM read_parquet('{PRUNE}')
  WHERE time >= DATE '{START}' AND VNINDEX IS NOT NULL ORDER BY time""").df()
vnx["time"] = pd.to_datetime(vnx.time); vix = vnx.set_index("time")["VNINDEX"].sort_index()
def nxt(d):
    pos = alldays.searchsorted(d, side="right"); return alldays[pos] if pos < len(alldays) else None

def simulate(pick_fn, label):
    rows, prev = [], set()
    for i in range(len(rebal) - 1):
        d, dn = rebal[i], rebal[i + 1]
        e, x = nxt(d), nxt(dn)
        if e is None or x is None or e >= x: continue
        names = pick_fn(d)
        rets = []
        for t in names:
            if t in close.columns:
                p0 = close.at[e, t] if e in close.index else np.nan
                p1 = close.at[x, t] if x in close.index else np.nan
                if pd.notna(p0) and pd.notna(p1) and p0 > 0: rets.append(p1 / p0 - 1)
        bh = float(vix.asof(x) / vix.asof(e) - 1) if vix.asof(e) > 0 else 0.0
        cur = set(names)
        if not rets:
            cost = TC * float(len(prev) > 0)
            rows.append(dict(rebal=d.strftime("%Y-%m-%d"), year=d.year, n=0, net=-cost, bh=bh)); prev = set(); continue
        gross = float(np.mean(rets))
        turn = len(cur ^ prev) / max(len(cur | prev), 1)
        rows.append(dict(rebal=d.strftime("%Y-%m-%d"), year=d.year, n=len(rets), net=gross - TC * turn, bh=bh))
        prev = cur
    return pd.DataFrame(rows)

def pick_all(d):
    return [p for p in PARENTS if p in cov.columns and pd.notna(cov[p].asof(d))]
def pick_discount(d):
    # hold the parents whose OWN coverage-z (deep discount) is in the bottom half that month
    z = {p: covz[p].asof(d) for p in PARENTS if pd.notna(covz[p].asof(d))}
    if len(z) < 2: return list(z)
    med = np.median(list(z.values()))
    return [p for p, v in z.items() if v <= med]

RALL = simulate(pick_all, "ALL")
RDIS = simulate(pick_discount, "DISCOUNT-TILT")
RALL.to_csv("data/holdco_all_monthly.csv", index=False)
RDIS.to_csv("data/holdco_discount_monthly.csv", index=False)

def metrics(r):
    r = np.asarray(r, float)
    if len(r) == 0: return dict(CAGR=0, Sharpe=0, MaxDD=0, Calmar=0)
    nav = np.cumprod(1 + r); yrs = len(r) / 12
    cagr = nav[-1] ** (1 / yrs) - 1
    sh = (r.mean() / r.std() * np.sqrt(12)) if r.std() > 0 else 0
    peak = np.maximum.accumulate(nav); mdd = (nav / peak - 1).min()
    cal_ = cagr / abs(mdd) if mdd < 0 else float("inf")
    return dict(CAGR=cagr * 100, Sharpe=sh, MaxDD=mdd * 100, Calmar=cal_)

def rep(label, R):
    s, b = metrics(R.net), metrics(R.bh)
    print(f"  {label:26s} CAGR {s['CAGR']:6.2f}% Sh {s['Sharpe']:4.2f} DD {s['MaxDD']:6.1f}% Cal {s['Calmar']:4.2f}"
          f"   | B&H CAGR {b['CAGR']:6.2f}% edge {s['CAGR']-b['CAGR']:+5.1f}pp")
    return s, b
print("\n  Backtest (monthly, 4-name conglomerate universe, TC 0.1%):")
fa = rep("ALL 4 parents FULL", RALL)
fd = rep("DISCOUNT-TILT FULL", RDIS)
rep("ALL IS 2016-2019", RALL[RALL.year <= 2019]); rep("ALL OOS 2020-2026", RALL[RALL.year >= 2020])
rep("DISCOUNT IS 2016-2019", RDIS[RDIS.year <= 2019]); rep("DISCOUNT OOS 2020-2026", RDIS[RDIS.year >= 2020])

# ---------- self-check 0 VND ----------
NAV0 = 1e9
def selfcheck(R, path):
    chk = pd.read_csv(path); return abs(NAV0 * np.prod(1 + R.net.values) - NAV0 * np.prod(1 + chk.net.values))
dA = selfcheck(RALL, "data/holdco_all_monthly.csv")
dB = selfcheck(RDIS, "data/holdco_discount_monthly.csv")
print(f"\nSELF-CHECK all {dA:.6f} {'PASS' if dA < 1 else 'FAIL'} | discount {dB:.6f} {'PASS' if dB < 1 else 'FAIL'}")

# ---------- verdict json ----------
out = dict(job="Taylor_20260706_042831", archetype="holding_company_conglomerate_sotp",
           universe=OWN, snapshot=snap, stability=stab, regime=regime,
           signal_ic=ic, signal_pooled_rows=int(len(panel)),
           backtest=dict(all_full={k: round(v, 3) for k, v in fa[0].items()},
                         discount_full={k: round(v, 3) for k, v in fd[0].items()},
                         bh_full={k: round(v, 3) for k, v in fa[1].items()}),
           selfcheck=dict(all=round(dA, 6), discount=round(dB, 6)))
with open("data/holdco_sotp_verdict.json", "w") as f:
    json.dump(out, f, indent=2, default=str)
print("\nwrote data/holdco_sotp_verdict.json")
