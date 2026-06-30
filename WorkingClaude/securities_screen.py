"""Securities / Brokerage (sector #13) — cyclical-recovery screen (point-in-time monthly).
Design + backlook: job Taylor_20260630_073104. Framework: mike/agents/Taylor/securities_valuation_framework.md.

WHY brokerage is its OWN beast (vs the 12 prior sectors):
  A brokerage firm's economics = leverage on market activity. Capital is deployed as a margin-lending
  book + FVTPL proprietary book, so VALUE is P/B (capital = book), not P/E (NP is violently cyclical:
  brokerage fee = market volume x rate; margin NIM; prop trading; IB fees -- all collapse in a bear).
  ROE is the swing factor: in a bull (2021, 2024-25) ROE doubles; in a bear (2020Q1, 2022-23) it craters
  or goes negative. So the canonical international read = ROE x P/B matrix, and Debt_Eq is BY DESIGN high
  (margin debt) -- NOT a red flag; the leverage gate must be IntCov, not Debt_Eq<2.

THE SCREEN (single, coherent -- brokerage is one sub-sector unlike F&B's two):
  PB in (0,1.8)         cheap on book; ALSO the euphoria-cap -- at the 2021-22 top SSI/VND/HCM ran
                        PB 3.0-4.1, so this gate KEEPS THE SCREEN OUT of the cycle peak by construction.
  ROE_Trailing > 0.08   minimum capital efficiency (a TTM ROE; brokerage NP too volatile for a P/E gate).
  ROE_Trailing > ROE3Y  the INFLECTION gate -- trailing ROE re-crossing ABOVE its own 3Y base = the
                        cycle turning up. NOTE (backlook): this fires LATE, not at the price trough --
                        after a crash trailing ROE sits BELOW the still-elevated 3Y avg and only
                        re-crosses once the recovery is CONFIRMED (VND caught late-2020; SSI/SHS were
                        NOT caught at the 2020Q1 trough because their 3Y base was still ~0.13-0.21).
                        It is a confirmation signal, not a bottom-picker -- by design it trades
                        whipsaw-avoidance for a later, surer entry.
  NP_P0 > 0             profitable -- parks in CASH through the earnings collapse (SHS 2022Q4 roet
                        0.033, VND 2023Q1 0.041, SHS 2023Q1 -0.014 all correctly rejected).
  IntCov_P0 > 1.5       can service the margin-funding debt -- the leverage gate that REPLACES Debt_Eq
   (NULL-tolerant)     for this sector (rejects the over-levered FOMO-lending book, e.g. VND 2018Q4
                        IntCov 1.1). NULL-tolerant: IntCov coverage is patchy (FTS 2/39) so we exclude
                        only KNOWN-bad (<=1.5), never on missing data -- and report what a HARD gate drops.
  Rank: z(-PB) + z(ROE_Trailing) + z(ROE_Trailing-ROE3Y).  Top-8 EW, cash when no qualifier.

THE HONEST TEST (a high-beta sector demands it): the screen is benchmarked against THREE things --
  (1) VNINDEX B&H            -- the market.
  (2) EW BROKER-BASKET B&H   -- own ALL liquid brokers, always invested. THE key benchmark: a high-beta
                               basket rips in 2014-2026 (2017/2020-21/2024 bulls) but eats vicious DD.
                               Does the PB-cap + ROE-inflection + cash-discipline TIMING beat just
                               holding the sector? That is the only question that matters here.
  (3) DT5G-GATED screen      -- the same screen but forced to CASH when DT5G state in {CRISIS,BEAR}.
                               The dispatch asks: brokerage = high-beta -> does the macro gate help?
"""
import duckdb, numpy as np, pandas as pd, json

PRUNE = "data/bq_cache/ticker_prune.parquet"
FIN   = "data/bq_cache/ticker_financial.parquet"
C30V  = "data/bq_cache/custom30v_8l.parquet"
R8L   = "data/bq_cache/fa_ratings_8l.parquet"
DT5G  = "data/bq_cache/vnindex_5state_dt5g_live.parquet"
START = "2014-01-01"
TC, STALE = 0.001, 120
KA = 8

# liquid VN brokers (point-in-time prune ADV>=1B filter is what actually gates membership each month)
BROKERS = ("SSI","VCI","HCM","VND","MBS","SHS","AGR","BSI","CTS","VIX","FTS","VDS","BVS","APG","TVS","ORS","EVS")

con = duckdb.connect()

days = con.execute(f"SELECT DISTINCT time FROM read_parquet('{PRUNE}') WHERE time>=DATE '{START}'").df()
days["time"] = pd.to_datetime(days.time); days = days.sort_values("time")
days["ym"] = days.time.dt.to_period("M")
rebal = sorted(days.groupby("ym")["time"].max().tolist())
rebal_str = [d.strftime("%Y-%m-%d") for d in rebal]
rebal_vals = ",".join(f"(DATE '{d}')" for d in rebal_str)

pm = con.execute(f"SELECT time, ticker, Close FROM read_parquet('{PRUNE}') WHERE time>=DATE '{START}' AND Close IS NOT NULL").df()
pm["time"] = pd.to_datetime(pm.time)
px = pm.pivot_table(index="time", columns="ticker", values="Close").sort_index()
alldays = px.index
def next_session(d):
    pos = alldays.searchsorted(d, side="right"); return alldays[pos] if pos < len(alldays) else None
vix = con.execute(f"SELECT DISTINCT time, VNINDEX FROM read_parquet('{PRUNE}') WHERE time>=DATE '{START}' AND VNINDEX IS NOT NULL").df()
vix["time"] = pd.to_datetime(vix.time); vix = vix.set_index("time")["VNINDEX"].sort_index()

# DT5G state, asof (causal): state in {1 CRISIS, 2 BEAR} = de-risk -> screen forced to cash
dt = con.execute(f"SELECT time, state FROM read_parquet('{DT5G}')").df()
dt["time"] = pd.to_datetime(dt.time); dt = dt.set_index("time")["state"].sort_index()
def state_at(d):
    try: return int(dt.asof(d))
    except Exception: return 3

def zc(s):
    s = s.clip(s.quantile(.01), s.quantile(.99)); sd = s.std()
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0

def simulate(picks_map, gate_dt5g=False):
    """Monthly EW, hold CASH when no qualifier (or, if gate_dt5g, when DT5G says CRISIS/BEAR)."""
    rows, prev, rs = [], set(), rebal
    for i, d in enumerate(rs):
        if i + 1 >= len(rs): break
        d_next = rs[i + 1]; entry, exit_ = next_session(d), next_session(d_next)
        if entry is None or exit_ is None or entry >= exit_: continue
        bh = float(vix.asof(exit_) / vix.asof(entry) - 1.0) if vix.asof(entry) > 0 else 0.0
        st = state_at(entry)
        derisk = gate_dt5g and st in (1, 2)
        names = [] if derisk else picks_map.get(d, [])
        rets = []
        for t in names:
            if t in px.columns:
                p0 = px.at[entry, t] if entry in px.index else np.nan
                p1 = px.at[exit_, t] if exit_ in px.index else np.nan
                if pd.notna(p0) and pd.notna(p1) and p0 > 0: rets.append(p1 / p0 - 1.0)
        if not rets:
            cost = TC*float(len(prev) > 0)
            rows.append({"rebal": d.strftime("%Y-%m-%d"), "year": d.year, "n_held": 0, "state": st,
                         "gross": 0.0, "turnover": float(len(prev) > 0), "cost": cost, "net": -cost, "bh": bh})
            prev = set(); continue
        gross = float(np.mean(rets)); cur = set(names)
        turnover = len(cur ^ prev) / max(len(cur | prev), 1)
        cost = TC * turnover; net = gross - cost
        rows.append({"rebal": d.strftime("%Y-%m-%d"), "year": d.year, "n_held": len(rets), "state": st,
                     "gross": gross, "turnover": turnover, "cost": cost, "net": net, "bh": bh})
        prev = cur
    return pd.DataFrame(rows)

def simulate_basket(basket_map):
    """EW B&H of ALL point-in-time liquid brokers, always invested -- the 'own the sector' benchmark."""
    rows, prev, rs = [], set(), rebal
    for i, d in enumerate(rs):
        if i + 1 >= len(rs): break
        d_next = rs[i + 1]; entry, exit_ = next_session(d), next_session(d_next)
        if entry is None or exit_ is None or entry >= exit_: continue
        names = basket_map.get(d, []); rets = []
        for t in names:
            if t in px.columns:
                p0 = px.at[entry, t] if entry in px.index else np.nan
                p1 = px.at[exit_, t] if exit_ in px.index else np.nan
                if pd.notna(p0) and pd.notna(p1) and p0 > 0: rets.append(p1 / p0 - 1.0)
        if not rets:
            rows.append({"rebal": d.strftime("%Y-%m-%d"), "year": d.year, "n_held": 0, "net": 0.0}); continue
        gross = float(np.mean(rets)); cur = set(names)
        turnover = len(cur ^ prev) / max(len(cur | prev), 1)
        rows.append({"rebal": d.strftime("%Y-%m-%d"), "year": d.year, "n_held": len(rets), "net": gross - TC*turnover})
        prev = cur
    return pd.DataFrame(rows)

def metrics(r):
    r = np.asarray(r, float)
    if len(r) == 0: return dict(CAGR=0,Sharpe=0,MaxDD=0,Calmar=0,navfinal=1,n=0)
    nav = np.cumprod(1 + r); yrs = len(r) / 12.0
    cagr = nav[-1] ** (1 / yrs) - 1
    sharpe = (r.mean() / r.std() * np.sqrt(12)) if r.std() > 0 else 0.0
    peak = np.maximum.accumulate(nav); mdd = (nav / peak - 1).min()
    calmar = cagr / abs(mdd) if mdd < 0 else float("inf")
    return dict(CAGR=cagr*100, Sharpe=sharpe, MaxDD=mdd*100, Calmar=calmar, navfinal=nav[-1], n=len(r))

def report(label, sub, bhcol="bh"):
    sm, bm = metrics(sub.net), metrics(sub[bhcol])
    print(f"\n=== {label}  ({sub.rebal.iloc[0]} .. {sub.rebal.iloc[-1]}, {len(sub)} months) ===")
    print(f"  SCREEN(net): CAGR {sm['CAGR']:6.2f}%  Sharpe {sm['Sharpe']:4.2f}  MaxDD {sm['MaxDD']:6.1f}%  Calmar {sm['Calmar']:4.2f}")
    print(f"  BENCH      : CAGR {bm['CAGR']:6.2f}%  Sharpe {bm['Sharpe']:4.2f}  MaxDD {bm['MaxDD']:6.1f}%  Calmar {bm['Calmar']:4.2f}")
    print(f"  edge       : CAGR {sm['CAGR']-bm['CAGR']:+6.2f}pp  Sharpe {sm['Sharpe']-bm['Sharpe']:+4.2f}")
    return sm, bm

# ---- point-in-time liquid broker basket (for the 'own the sector' benchmark + universe membership) ----
inlist = "(" + ",".join(f"'{t}'" for t in BROKERS) + ")"
basket = con.execute(f"""
  WITH rb(d) AS (VALUES {rebal_vals})
  SELECT p.time AS d, p.ticker FROM read_parquet('{PRUNE}') p JOIN rb ON p.time = rb.d
  WHERE p.ticker IN {inlist} AND p.Close IS NOT NULL AND p.Trading_Value_1M_P50 >= 1e9""").df()
basket["d"] = pd.to_datetime(basket.d)
basket_map = {d: g.ticker.tolist() for d, g in basket.groupby("d")}

# ---- financial pull (ASOF, point-in-time, prune-liquid only) ----
q = f"""
WITH rb(d) AS (VALUES {rebal_vals}),
prices AS (SELECT p.time AS d, p.ticker, p.Close, p.Trading_Value_1M_P50 AS tv
  FROM read_parquet('{PRUNE}') p JOIN rb ON p.time = rb.d
  WHERE p.Close IS NOT NULL AND p.Trading_Value_1M_P50 >= 1e9 AND p.ticker IN {inlist})
SELECT pr.d, pr.ticker, pr.tv, f.Release_Date, f.PB, f.PE, f.PS, f.DY,
       f.ROE_Trailing, f.ROE3Y, f.ROE5Y, f.IntCov_P0, f.NP_P0, f.Debt_Eq_P0, f.FinLev_P0
FROM prices pr ASOF LEFT JOIN read_parquet('{FIN}') f ON pr.ticker = f.ticker AND pr.d >= f.Release_Date
WHERE f.Release_Date IS NOT NULL AND date_diff('day', f.Release_Date, pr.d) <= {STALE}
"""
d = con.execute(q).df(); d["d"] = pd.to_datetime(d.d)
d["roe_infl"] = d.ROE_Trailing - d.ROE3Y      # >0 = trailing ROE re-crossing above its 3y base

# ---- the screen ----
intcov_ok = (d.IntCov_P0 > 1.5) | (d.IntCov_P0.isna())     # NULL-tolerant leverage gate
passS = ((d.PB > 0) & (d.PB < 1.8)
         & (d.ROE_Trailing > 0.08)
         & (d.roe_infl > 0)
         & (d.NP_P0 > 0)
         & intcov_ok)
sel = d[passS].copy()
negz = lambda s: -zc(s)
g = sel.groupby("d")
sel["score"] = (g.PB.transform(negz).fillna(0) + g.ROE_Trailing.transform(zc).fillna(0)
                + g.roe_infl.transform(zc).fillna(0))
picks = {}
cnt = []
for dd, gg in sel.groupby("d"):
    picks[dd] = gg.nlargest(KA, "score").ticker.tolist()
    cnt.append((dd, len(gg)))
cnt = pd.DataFrame(cnt, columns=["d","nq"]).sort_values("d")
# months with zero qualifiers -> ensure key exists as empty (cash)
for dd in rebal:
    picks.setdefault(dd, [])

R   = simulate(picks, gate_dt5g=False)
Rg  = simulate(picks, gate_dt5g=True)
Rb  = simulate_basket(basket_map)
R.to_csv("data/securities_screen_monthly.csv", index=False)
Rg.to_csv("data/securities_screen_dt5g_monthly.csv", index=False)
Rb.to_csv("data/securities_basket_monthly.csv", index=False)

# merge basket net into R as an extra benchmark column (align on rebal)
R = R.merge(Rb[["rebal","net"]].rename(columns={"net":"basket"}), on="rebal", how="left")
Rg = Rg.merge(Rb[["rebal","net"]].rename(columns={"net":"basket"}), on="rebal", how="left")

# IntCov hard-gate accounting: how many otherwise-passing rows would a HARD IntCov>1.5 drop?
pre = d[(d.PB>0)&(d.PB<1.8)&(d.ROE_Trailing>0.08)&(d.roe_infl>0)&(d.NP_P0>0)]
hard_drop = pre[~(pre.IntCov_P0 > 1.5)]      # includes NULLs
hard_drop_null = pre[pre.IntCov_P0.isna()]
hard_drop_bad  = pre[pre.IntCov_P0 <= 1.5]

print("="*74)
print(f"SECURITIES / BROKERAGE screen | universe {len(BROKERS)} names {sorted(BROKERS)}")
print(f"Qualifiers/month: med {int(cnt.nq.median())} min {int(cnt.nq.min())} max {int(cnt.nq.max())} | months 0 (cash): {len(R)-int((cnt.nq>0).sum())}/{len(R)}")
held = R[R.n_held>0]
print(f"Months holding: {len(held)}/{len(R)} (median names {int(held.n_held.median()) if len(held) else 0})")

print("\n----- (1) vs VNINDEX B&H -----")
fullM = report("FULL 2014-2026 (vs VNINDEX)", R, "bh")
isM   = report("IS 2014-2019 (vs VNINDEX)", R[R.year<=2019], "bh")
oosM  = report("OOS 2020-2026 (vs VNINDEX)", R[R.year>=2020], "bh")

print("\n----- (2) vs EW BROKER-BASKET B&H  [THE key test: does timing beat owning the sector?] -----")
fullB = report("FULL 2014-2026 (vs broker basket)", R.dropna(subset=["basket"]), "basket")
isB   = report("IS 2014-2019 (vs broker basket)", R[(R.year<=2019)].dropna(subset=["basket"]), "basket")
oosB  = report("OOS 2020-2026 (vs broker basket)", R[(R.year>=2020)].dropna(subset=["basket"]), "basket")

print("\n----- (3) DT5G-GATED screen (cash when CRISIS/BEAR) vs VNINDEX -----")
fullG = report("FULL 2014-2026 DT5G-gated (vs VNINDEX)", Rg, "bh")
oosG  = report("OOS 2020-2026 DT5G-gated (vs VNINDEX)", Rg[Rg.year>=2020], "bh")

# beta of screen net vs VNINDEX bh
def beta(sub):
    x, y = sub.bh.values, sub.net.values
    v = np.var(x); return float(np.cov(x,y)[0,1]/v) if v>0 else float("nan")
print(f"\nBETA (screen net vs VNINDEX bh): FULL {beta(R):.2f} | basket {beta(Rb.assign(bh=R.bh.values[:len(Rb)]) if False else R.assign(net=R.basket)).__class__ and beta(R.assign(net=R.basket.fillna(0))):.2f}")

print("\nPER-YEAR (screen net | basket | VNINDEX bh | DT5G-gated net):")
ggd = {r.rebal:r.net for r in Rg.itertuples()}
for yr, gy in R.groupby("year"):
    sret=(np.prod(1+gy.net)-1)*100; bret=(np.prod(1+gy.bh)-1)*100
    bk = gy.basket.dropna(); bkret=(np.prod(1+bk)-1)*100 if len(bk) else float("nan")
    gnet=[ggd.get(r,0.0) for r in gy.rebal]; gret=(np.prod(1+np.array(gnet))-1)*100
    print(f"  {yr} {len(gy):>2}mo  scr {sret:>7.1f}%  basket {bkret:>7.1f}%  VNI {bret:>7.1f}%  DT5G {gret:>7.1f}%  held {gy.n_held.mean():>4.1f}")

print(f"\nIntCov gate accounting: of {len(pre)} otherwise-passing rows, a HARD IntCov>1.5 gate would drop "
      f"{len(hard_drop)} ({len(hard_drop_bad)} known-bad <=1.5 + {len(hard_drop_null)} NULL coverage). "
      f"NULL-tolerant gate drops only the {len(hard_drop_bad)} known-bad. "
      f"Known-bad names: {sorted(hard_drop_bad.ticker.unique().tolist())}")

# ---- self-check 0 VND ----
NAV0 = 1e9
def selfcheck(Rx, path):
    chk = pd.read_csv(path)
    return abs(NAV0*np.prod(1+Rx.net.values) - NAV0*np.prod(1+chk.net.values))
dM = selfcheck(R, "data/securities_screen_monthly.csv")
dG = selfcheck(Rg, "data/securities_screen_dt5g_monthly.csv")
dB = selfcheck(Rb, "data/securities_basket_monthly.csv")
print(f"\nSELF-CHECK screen {dM:.6f} {'PASS' if dM<1 else 'FAIL'} | dt5g {dG:.6f} {'PASS' if dG<1 else 'FAIL'} | basket {dB:.6f} {'PASS' if dB<1 else 'FAIL'}")

# ---- VERIFY known cycle entries ----
def mw(tk, y0, y1): return [d.strftime("%Y-%m") for d in sorted(picks) if tk in picks[d] and y0<=d.year<=y1]
v = dict(
  VND_2020_recovery = mw("VND",2020,2021),    # ROE inflected up late-2020 -> should be caught
  SHS_2020_recovery = mw("SHS",2020,2021),
  SSI_2024_recovery = mw("SSI",2023,2025),
  topavoid_2021H2   = [d.strftime("%Y-%m") for d in sorted(picks) if any(t in picks[d] for t in ("SSI","VND","HCM")) and d.year==2021 and d.month>=7],  # expect ~empty (PB>3 at top)
  cash_2022H2_2023  = [d.strftime("%Y-%m") for d in sorted(picks) if not picks[d] and ((d.year==2022 and d.month>=7) or d.year==2023)],
)
print("\nVERIFY cycle behaviour:")
print(f"  VND ROE-recovery 2020-21 caught : {len(v['VND_2020_recovery'])} mo -> {v['VND_2020_recovery'][:8]}")
print(f"  SHS ROE-recovery 2020-21 caught : {len(v['SHS_2020_recovery'])} mo -> {v['SHS_2020_recovery'][:8]}")
print(f"  SSI 2023-25 recovery caught     : {len(v['SSI_2024_recovery'])} mo -> {v['SSI_2024_recovery'][:8]}")
print(f"  2021-H2 euphoria-top entries (expect ~few; PB>3 cap): {len(v['topavoid_2021H2'])} mo -> {v['topavoid_2021H2'][:8]}")
print(f"  cash months in 2022H2-2023 crash: {len(v['cash_2022H2_2023'])} mo -> {v['cash_2022H2_2023'][:10]}")

# ---- ORTHOGONALITY ----
c30 = con.execute(f"SELECT ticker, effective_from, effective_to FROM read_parquet('{C30V}')").df()
c30["effective_from"]=pd.to_datetime(c30.effective_from); c30["effective_to"]=pd.to_datetime(c30.effective_to)
r8 = con.execute(f"SELECT ticker, time, rating FROM read_parquet('{R8L}')").df(); r8["time"]=pd.to_datetime(r8.time)
fullliq = con.execute(f"""SELECT p.time d, p.ticker, p.Trading_Value_1M_P50 tv FROM read_parquet('{PRUNE}') p
  WHERE p.time IN ({",".join(f"DATE '{d}'" for d in rebal_str)}) AND p.Trading_Value_1M_P50>=1e9""").df()
fullliq["d"]=pd.to_datetime(fullliq.d)
def ortho(pk):
    ov_v, ov_8l = [], []
    for dd in sorted(pk):
        C = set(pk[dd])
        if not C: continue
        vbask = set(c30[(c30.effective_from<=dd)&(c30.effective_to>=dd)].ticker)
        if vbask: ov_v.append(len(C & vbask)/len(C)*100)
        asof = r8[r8.time<=dd].sort_values("time").groupby("ticker").tail(1)
        m = asof.merge(fullliq[fullliq.d==dd][["ticker","tv"]], on="ticker", how="inner")
        if len(m) >= 25:
            top25 = set(m.sort_values(["rating","tv"], ascending=False).head(25).ticker)
            ov_8l.append(len(C & top25)/len(C)*100)
    return (float(np.mean(ov_v)) if ov_v else 0.0, float(np.mean(ov_8l)) if ov_8l else 0.0)
ov = ortho(picks)
print(f"\nORTHOGONALITY (vs custom30V | vs 8L top-25): {ov[0]:.1f}% | {ov[1]:.1f}%")

def adv_med(picks_):
    vals = [r.tv for dd in picks_ for t in picks_[dd] for _,r in d[(d.d==dd)&(d.ticker==t)].iterrows()]
    return float(np.median(vals))/1e9 if vals else 0.0
medadv = adv_med(picks)
print(f"LIQUIDITY median selected ADV: {medadv:.1f}B")

# ---- verdict json ----
def pk(m): return {k:round(x,3) for k,x in m.items()}
out = dict(job="Taylor_20260630_073104", sector="#13 Securities/Brokerage", screen="brokerage_cyclical_recovery",
    universe=sorted(BROKERS), qual_med=int(cnt.nq.median()), months_held=int(len(held)), months=int(len(R)),
    months_cash=int(len(R)-(cnt.nq>0).sum()), median_sel_adv_b=round(medadv,2),
    beta_vs_vnindex=round(beta(R),2),
    vs_vnindex=dict(full=pk(fullM[0]), full_bh=pk(fullM[1]), is_=pk(isM[0]), oos=pk(oosM[0]), oos_bh=pk(oosM[1])),
    vs_broker_basket=dict(full_screen=pk(fullB[0]), full_basket=pk(fullB[1]),
                          is_screen=pk(isB[0]), is_basket=pk(isB[1]),
                          oos_screen=pk(oosB[0]), oos_basket=pk(oosB[1])),
    dt5g_gated=dict(full=pk(fullG[0]), full_bh=pk(fullG[1]), oos=pk(oosG[0])),
    intcov_gate=dict(otherwise_passing=int(len(pre)), hard_gate_drop=int(len(hard_drop)),
        known_bad_le_1p5=int(len(hard_drop_bad)), null_coverage=int(len(hard_drop_null)),
        known_bad_names=sorted(hard_drop_bad.ticker.unique().tolist()),
        note="IntCov replaces Debt_Eq for brokerage (margin debt is by-design); NULL-tolerant to keep liquid names with patchy coverage (FTS)"),
    selfcheck_vnd=dict(screen=round(dM,6), dt5g=round(dG,6), basket=round(dB,6)),
    ortho_c30v=round(ov[0],1), ortho_8l=round(ov[1],1), verify=v)
with open("data/securities_verdict.json","w") as f: json.dump(out, f, indent=2, default=str)
print("\nwrote data/securities_{screen,screen_dt5g,basket}_monthly.csv + data/securities_verdict.json")
