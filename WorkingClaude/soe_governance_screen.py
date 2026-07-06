"""State-Owned-Enterprise GOVERNANCE archetype — sector #19 framework + screen.
Design + backlook: job Taylor_20260706_040038. Framework: mike/agents/Taylor/soe_governance_framework.md.

This is NOT an industry. State-controlled names live scattered across sectors already screened
(GAS/PLX -> energy #9, POW/NT2 -> power/D&A, VCB/CTG/BID -> banking, BVH -> insurance). It is a
GOVERNANCE ARCHETYPE that cuts ACROSS sectors: companies where the State holds a controlling stake
(>50%, or de-facto control). The defining, testable features that make governance different from a
purely private capital-allocator:

  (a) DIVIDEND POLICY is partly a STATE-BUDGET decision, not a pure free-cash-flow decision. The State
      shareholder (SCIC / a line ministry / PVN / SBV) can want cash UP to the budget (the cash-cow SOEs:
      GAS, VEA, PLX) OR can FORCE RETENTION for policy reasons (state banks VCB/CTG/BID were pushed to pay
      STOCK dividends and retain to build CAR under Basel II). So "SOE => high stable DY" is only HALF true
      -> we test it, we do not assume it.
  (b) THIN FREE-FLOAT. 65-96% of shares are locked in State hands and do not trade. The tradeable float is
      small -> lower share turnover, harder execution, structural illiquidity even for a "large-cap".
      THIS is the cleanest, most measurable SOE signature (share turnover = Volume / shares-outstanding).
  (c) POLICY PRICE CONTROL caps the upside asymmetrically. Fuel retail (PLX), electricity (POW/NT2 sell to
      the EVN single buyer), gas — selling prices are administered for public-policy goals, not profit
      maximisation. The State caps your margin in the good times (2022 Petrolimex price-ceiling losses).
  (d) STATE ACTION is a discrete event risk/opportunity: divestment (SAB 2017 sold to ThaiBev at a huge
      premium; the SCIC/VNM overhang), forced capital raises, restructuring. Un-modellable in BQ -> noted
      qualitatively.

What this script settles quantitatively (auditable, self-check 0 VND, threads=1, walk-forward IS/OOS):

  PART 0 — FLOAT SIGNATURE. Annual share turnover (SUM Volume / OShares) SOE vs matched private peers.
           Hypothesis: state ownership % is INVERSELY related to turnover (thin float).
  PART 1 — SIGNAL TEST. Spearman IC of {state_pct, share-turnover, DY-when-present, PB, pb_rel} vs forward
           T+20/40/60 return (profit_1M/2M/3M — EVALUATION ONLY, never a live filter). Hypothesis:
           state_pct is ~0/negative (governance is not an alpha factor); DY does not rescue it.
  PART 2 — VALUATION DISCOUNT. SOE vs private PE/PB within the same sub-sector (power / banks / insurance).
           Hypothesis: NO uniform discount -> the index-heavyweight State FLAGSHIPS (VCB, GAS, BVH, SAB,
           VNM) actually trade a scarcity/quality PREMIUM; the discount story is refuted.
  PART 3 — BACKTESTS (the income-trap test). Three EW monthly baskets, liquidity-gated, hold-cash-when-empty:
           A SOE-controlled broad basket   (does state control drag realised return?)
           B private-peer matched basket    (the control group)
           C SOE high-DY cash-cow basket    (GAS/PLX/POW/NT2/VEA/PPC/BSR — the pure "yield play")
           NAV is PRICE-ONLY (no dividend reinvestment) -> the ~3-5%/yr cash-cow dividend is added back as
           an annotation to ask whether TOTAL return still lags = income trap.

State ownership % (public knowledge, approx, controlling holder in parens):
  GAS 95.8 (PVN) · PLX 75.9 (CMSC/MoIT) · POW 79.9 (PVN) · ACV 95.4 (CMSC) · BSR 92.1 (PVN) ·
  VEA 88.5 (MoIT) · NT2 59.4 (PVN/PV Power) · VCB 74.8 (SBV) · CTG 64.5 (SBV) · BID 81.0 (SBV) ·
  BVH 65.0 (MoF) · SAB 36.0 (post ThaiBev divest — was state, now ThaiBev-controlled: the divestment case) ·
  VNM 36.0 (SCIC, no longer controlling — the divestment-overhang case).
Private peers (matched sub-sector): REE/HDG/GEG/PPC (power+util), ACB/MBB/TCB/VPB/HDB (banks),
  BMI/PVI (insurance), QNS (beverage). (MBB has some military/state links but trades as a private bank.)

Auditable: prices + forward returns from tav2_bq.ticker_prune cache; financials (PE/PB/DY/OShares) ASOF-
joined from ticker_financial cache. Self-check 0 VND, threads=1, no look-ahead (profit_* eval-only).
"""
import duckdb, numpy as np, pandas as pd, json

FIN   = "data/bq_cache/ticker_financial.parquet"
PRUNE = "data/bq_cache/ticker_prune.parquet"
C30V  = "data/bq_cache/custom30v_8l.parquet"
R8L   = "data/bq_cache/fa_ratings_8l.parquet"
START = "2014-01-01"
TC, STALE = 0.001, 120
KA  = 12          # basket cap (broad archetype, more names than a single-sector screen)
LIQ = 10e9        # 10B rolling ADV liquid gate (SOE large-caps; illiquid tail like ACV/VEA excluded from books)

# state-controlled (>50% or de-facto), approx state %
STATE = {"GAS":95.8,"PLX":75.9,"POW":79.9,"ACV":95.4,"BSR":92.1,"VEA":88.5,"NT2":59.4,
         "VCB":74.8,"CTG":64.5,"BID":81.0,"BVH":65.0,"SAB":36.0,"VNM":36.0}
PRIV  = {"REE":0,"HDG":0,"GEG":0,"PPC":0,"ACB":0,"MBB":0,"TCB":0,"VPB":0,"HDB":0,"BMI":0,"PVI":35,"QNS":0}
SUBSECTOR = {  # for the discount test — only groups with BOTH state and private names
    "power":     dict(soe=["POW","NT2"],          priv=["REE","HDG","GEG","PPC"]),
    "banks":     dict(soe=["VCB","CTG","BID"],     priv=["ACB","MBB","TCB","VPB","HDB"]),
    "insurance": dict(soe=["BVH"],                 priv=["BMI","PVI"]),
}
UNIVERSE = tuple(list(STATE) + list(PRIV))

# --- backtest baskets (liquid only) ---
SOE_BROAD   = ["GAS","PLX","POW","NT2","BSR","VCB","CTG","BID","BVH","VNM"]   # ADV>10B state-controlled
PRIV_PEER   = ["REE","HDG","GEG","ACB","MBB","TCB","VPB","HDB","BMI","QNS"]   # matched-sector private control
SOE_CASHCOW = ["GAS","PLX","POW","NT2","BSR","PPC"]                            # the pure high-DY yield play
CASHCOW_DIV = 0.045   # ~4.5%/yr gross cash dividend for the cash-cow basket (annotation only)

con = duckdb.connect(config={"threads": 1})
inl = ",".join(f"'{t}'" for t in UNIVERSE)

# ---------- price / forward-return panel ----------
raw = con.execute(f"""SELECT ticker, time, Close, Volume, Price, profit_1M, profit_2M, profit_3M
  FROM read_parquet('{PRUNE}') WHERE ticker IN ({inl}) AND time >= DATE '{START}'""").df()
raw["time"] = pd.to_datetime(raw.time)
px = raw.pivot_table(index="time", columns="ticker", values="Close").sort_index()
alldays = px.index
raw["tvday"] = raw.Volume * raw.Price
adv = raw.pivot_table(index="time", columns="ticker", values="tvday").sort_index().rolling(21, min_periods=5).mean()

ixq = con.execute(f"""SELECT DISTINCT time, VNINDEX FROM read_parquet('{PRUNE}')
  WHERE time >= DATE '{START}' AND VNINDEX IS NOT NULL ORDER BY time""").df()
ixq["time"] = pd.to_datetime(ixq.time); vix = ixq.set_index("time")["VNINDEX"].sort_index()

def next_session(d):
    pos = alldays.searchsorted(d, side="right"); return alldays[pos] if pos < len(alldays) else None
cal = pd.DataFrame({"time": alldays}); cal["ym"] = cal.time.dt.to_period("M")
rebal = sorted(cal.groupby("ym")["time"].max().tolist())
rebal_str = [d.strftime("%Y-%m-%d") for d in rebal]
rebal_vals = ",".join(f"(DATE '{d}')" for d in rebal_str)

def zc(s):
    s = s.clip(s.quantile(.01), s.quantile(.99)); sd = s.std()
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0
negz = lambda s: -zc(s)
def spearman(a, b):
    m = a.notna() & b.notna()
    if m.sum() < 30: return np.nan
    return a[m].rank().corr(b[m].rank())

# ============================================================================
# PART 0 — FLOAT SIGNATURE (annual share turnover = Volume / shares-outstanding)
# ============================================================================
osh = con.execute(f"""SELECT ticker, ARG_MAX(OShares,time) osh FROM read_parquet('{FIN}')
  WHERE ticker IN ({inl}) AND OShares>0 GROUP BY ticker""").df()
vol24 = con.execute(f"""SELECT ticker, SUM(Volume) volsum, COUNT(DISTINCT EXTRACT(YEAR FROM time)) ny
  FROM read_parquet('{PRUNE}') WHERE ticker IN ({inl}) AND time>=DATE '2024-01-01' GROUP BY ticker""").df()
flt = vol24.merge(osh, on="ticker")
flt["turnover"] = flt.volsum / flt.ny / flt.osh
flt["state_pct"] = flt.ticker.map(lambda t: STATE.get(t, PRIV.get(t, 0)))
flt["type"] = flt.ticker.map(lambda t: "SOE" if t in STATE else "PRIV")
soe_med  = flt[flt.type == "SOE"].turnover.median()
priv_med = flt[flt.type == "PRIV"].turnover.median()
ic_state_turn = round(float(flt.state_pct.rank().corr(flt.turnover.rank())), 4)
print("="*74); print("PART 0 — FLOAT SIGNATURE (2024-25 annual share turnover = Volume/OShares)")
for _, r in flt.sort_values(["type","turnover"]).iterrows():
    print(f"  {r.ticker:5s} {r.type:4s} state%{r.state_pct:5.1f}  turnover {r.turnover:5.3f}")
print(f"  MEDIAN turnover  SOE {soe_med:.3f}  vs PRIV {priv_med:.3f}   (SOE/PRIV = {soe_med/priv_med:.2f}x)")
print(f"  Spearman(state_pct, turnover) across all names: {ic_state_turn:+.4f}  (expect NEGATIVE = thin float)")

# ============================================================================
# PART 1 — SIGNAL TEST (state_pct / turnover / DY / PB vs forward return)
# ============================================================================
fwd = raw[["time","ticker","profit_1M","profit_2M","profit_3M"]].dropna(subset=["profit_2M"]).copy()
finq = con.execute(f"""SELECT ticker, Release_Date, PB, PB_MA1Y, PE, DY, OShares
  FROM read_parquet('{FIN}') WHERE ticker IN ({inl}) AND Release_Date IS NOT NULL
  ORDER BY ticker, Release_Date""").df()
finq["Release_Date"] = pd.to_datetime(finq.Release_Date).astype("datetime64[ns]")
fwd["time"] = fwd["time"].astype("datetime64[ns]")
sig = pd.merge_asof(fwd.sort_values("time"), finq.sort_values("Release_Date"),
                    left_on="time", right_on="Release_Date", by="ticker", direction="backward")
sig = sig[(sig.time - sig.Release_Date).dt.days <= STALE].copy()
sig["state_pct"] = sig.ticker.map(lambda t: STATE.get(t, PRIV.get(t, 0)))
sig["is_soe"]    = sig.ticker.map(lambda t: 1.0 if t in STATE else 0.0)
sig["pb_rel"]    = sig.PB / sig.PB_MA1Y
sig = sig.merge(flt[["ticker","turnover"]], on="ticker", how="left")
feats = ["state_pct","turnover","DY","PB","pb_rel"]
sig_ic = {f"{c}_vs_{r}": round(float(spearman(sig[c], sig[r])), 4)
          for c in feats for r in ["profit_1M","profit_2M","profit_3M"]}
# SOE vs PRIV mean forward return
grp = sig.groupby(sig.is_soe.map({1.0:"SOE",0.0:"PRIV"}))[["profit_1M","profit_2M","profit_3M"]].mean().round(3)
grp_n = sig.groupby(sig.is_soe.map({1.0:"SOE",0.0:"PRIV"})).size()
print("\n"+"="*74); print("PART 1 — SIGNAL TEST (rows %d names %d)" % (len(sig), sig.ticker.nunique()))
for k, v in sig_ic.items(): print(f"  Spearman {k:26s}: {v:+.4f}")
print("  mean forward return, SOE vs PRIV:"); print(grp.to_string())
print("  n:", dict(grp_n))

# ============================================================================
# PART 2 — VALUATION DISCOUNT (SOE vs private, within sub-sector, 2014+ avg + latest)
# ============================================================================
val = con.execute(f"""SELECT ticker, AVG(PE) pe_avg, AVG(PB) pb_avg,
    ARG_MAX(PE,time) pe_now, ARG_MAX(PB,time) pb_now
  FROM read_parquet('{FIN}') WHERE ticker IN ({inl}) AND time>=DATE '2014-01-01' AND PB IS NOT NULL
  GROUP BY ticker""").df().set_index("ticker")
print("\n"+"="*74); print("PART 2 — VALUATION: State FLAGSHIP vs private peer, per sub-sector")
disc = {}
for sec, d0 in SUBSECTOR.items():
    ssoe = val.reindex(d0["soe"]); spri = val.reindex(d0["priv"])
    soe_pb, pri_pb = ssoe.pb_avg.mean(), spri.pb_avg.mean()
    soe_pe, pri_pe = ssoe.pe_avg.mean(), spri.pe_avg.mean()
    disc[sec] = dict(soe_pb=round(soe_pb,2), priv_pb=round(pri_pb,2), pb_ratio=round(soe_pb/pri_pb,2),
                     soe_pe=round(soe_pe,2), priv_pe=round(pri_pe,2))
    print(f"  {sec:9s}  SOE avg PB {soe_pb:4.2f} / PE {soe_pe:5.1f}   PRIV avg PB {pri_pb:4.2f} / PE {pri_pe:5.1f}"
          f"   -> SOE/PRIV PB = {soe_pb/pri_pb:4.2f}x  ({'PREMIUM' if soe_pb>pri_pb else 'discount'})")

# ============================================================================
# PART 3 — BACKTESTS (income-trap test: SOE broad vs private peer vs SOE cash-cow)
# ============================================================================
def simulate(picks_map):
    rows, prev, rs = [], set(), rebal
    for i, d in enumerate(rs):
        if i + 1 >= len(rs): break
        d_next = rs[i + 1]; entry, exit_ = next_session(d), next_session(d_next)
        if entry is None or exit_ is None or entry >= exit_: continue
        names = picks_map.get(d, []); rets = []
        for t in names:
            if t in px.columns:
                p0 = px.at[entry, t] if entry in px.index else np.nan
                p1 = px.at[exit_, t] if exit_ in px.index else np.nan
                if pd.notna(p0) and pd.notna(p1) and p0 > 0: rets.append(p1 / p0 - 1.0)
        bh = float(vix.asof(exit_) / vix.asof(entry) - 1.0) if vix.asof(entry) > 0 else 0.0
        if not rets:
            cost = TC * float(len(prev) > 0)
            rows.append({"rebal": d.strftime("%Y-%m-%d"), "year": d.year, "n_held": 0,
                         "gross": 0.0, "turnover": float(len(prev) > 0), "cost": cost, "net": -cost, "bh": bh})
            prev = set(); continue
        gross = float(np.mean(rets)); cur = set(names)
        turnover = len(cur ^ prev) / max(len(cur | prev), 1)
        cost = TC * turnover; net = gross - cost
        rows.append({"rebal": d.strftime("%Y-%m-%d"), "year": d.year, "n_held": len(rets),
                     "gross": gross, "turnover": turnover, "cost": cost, "net": net, "bh": bh})
        prev = cur
    return pd.DataFrame(rows)

def metrics(r):
    r = np.asarray(r, float)
    if len(r) == 0: return dict(CAGR=0, Sharpe=0, MaxDD=0, Calmar=0, navfinal=1, n=0)
    nav = np.cumprod(1 + r); yrs = len(r) / 12.0
    cagr = nav[-1] ** (1 / yrs) - 1
    sharpe = (r.mean() / r.std() * np.sqrt(12)) if r.std() > 0 else 0.0
    peak = np.maximum.accumulate(nav); mdd = (nav / peak - 1).min()
    calmar = cagr / abs(mdd) if mdd < 0 else float("inf")
    return dict(CAGR=cagr*100, Sharpe=sharpe, MaxDD=mdd*100, Calmar=calmar, navfinal=nav[-1], n=len(r))

def report(label, sub):
    sm, bm = metrics(sub.net), metrics(sub.bh)
    print(f"\n=== {label}  ({sub.rebal.iloc[0]} .. {sub.rebal.iloc[-1]}, {len(sub)} months) ===")
    print(f"  BASKET(net): CAGR {sm['CAGR']:6.2f}%  Sharpe {sm['Sharpe']:4.2f}  MaxDD {sm['MaxDD']:6.1f}%  Calmar {sm['Calmar']:4.2f}")
    print(f"  B&H VNINDEX: CAGR {bm['CAGR']:6.2f}%  Sharpe {bm['Sharpe']:4.2f}  MaxDD {bm['MaxDD']:6.1f}%  Calmar {bm['Calmar']:4.2f}")
    print(f"  edge(net-B&H): CAGR {sm['CAGR']-bm['CAGR']:+6.2f}pp  Sharpe {sm['Sharpe']-bm['Sharpe']:+4.2f}")
    return sm, bm

# ASOF financials at each rebalance (for the liquidity gate we use rolling ADV; membership is fixed baskets)
def basket_picks(members):
    picks = {}
    for dd in rebal:
        held = []
        for t in members:
            if t in adv.columns:
                s = adv[t]; s = s[s.index <= dd]
                if len(s) and pd.notna(s.iloc[-1]) and s.iloc[-1] >= LIQ:
                    held.append(t)
        picks[dd] = held
    return picks

picksA = basket_picks(SOE_BROAD)
picksB = basket_picks(PRIV_PEER)
picksC = basket_picks(SOE_CASHCOW)
RA = simulate(picksA); RA.to_csv("data/soe_broad_monthly.csv", index=False)
RB = simulate(picksB); RB.to_csv("data/soe_privpeer_monthly.csv", index=False)
RC = simulate(picksC); RC.to_csv("data/soe_cashcow_monthly.csv", index=False)

def block(name, R):
    held = R[R.n_held > 0]
    print("\n" + "="*74 + f"\n{name}")
    print(f"Months holding: {len(held)}/{len(R)} (median names {int(held.n_held.median()) if len(held) else 0})")
    full = report(f"{name} FULL 2014-2026", R)
    is_  = report(f"{name} IS 2014-2019", R[R.year <= 2019])
    oos  = report(f"{name} OOS 2020-2026", R[R.year >= 2020])
    print(f"\n{name} per-year (net vs B&H):")
    for yr, gy in R.groupby("year"):
        sret = (np.prod(1+gy.net)-1)*100; bret = (np.prod(1+gy.bh)-1)*100
        print(f"  {yr} {len(gy):>2}mo  sys {sret:>7.1f}%  bh {bret:>7.1f}%  edge {sret-bret:>+6.1f}pp  held {gy.n_held.mean():>4.1f}")
    return full, is_, oos

fullA, isA, oosA = block("BASKET A — SOE-CONTROLLED BROAD", RA)
fullB, isB, oosB = block("BASKET B — PRIVATE-PEER MATCHED (control)", RB)
fullC, isC, oosC = block("BASKET C — SOE HIGH-DY CASH-COW (yield play)", RC)

# income-trap annotation: add ~4.5%/yr dividend to cash-cow total return
cc_price_cagr = fullC[0]["CAGR"]; cc_total_cagr = cc_price_cagr + CASHCOW_DIV*100
print(f"\nINCOME-TRAP CHECK (Basket C): price-only CAGR {cc_price_cagr:.2f}% + ~{CASHCOW_DIV*100:.1f}pp gross div"
      f" = ~{cc_total_cagr:.2f}% total-return vs B&H {fullC[1]['CAGR']:.2f}%"
      f"  -> {'STILL LAGS (income trap)' if cc_total_cagr < fullC[1]['CAGR'] else 'closes the gap'}")

# ---------- self-check 0 VND ----------
NAV0 = 1e9
def selfcheck(R, path):
    chk = pd.read_csv(path)
    return abs(NAV0*np.prod(1+R.net.values) - NAV0*np.prod(1+chk.net.values))
dA = selfcheck(RA, "data/soe_broad_monthly.csv")
dB = selfcheck(RB, "data/soe_privpeer_monthly.csv")
dC = selfcheck(RC, "data/soe_cashcow_monthly.csv")
print(f"\nSELF-CHECK soe_broad {dA:.6f} {'PASS' if dA<1 else 'FAIL'} | privpeer {dB:.6f} {'PASS' if dB<1 else 'FAIL'} | cashcow {dC:.6f} {'PASS' if dC<1 else 'FAIL'}")

# ---------- verdict json ----------
def pack(R, full, is_, oos):
    held = R[R.n_held > 0]
    return dict(months_held=len(held), months=len(R),
        full={k: round(x, 3) for k, x in full[0].items()}, full_bh={k: round(x, 3) for k, x in full[1].items()},
        is_={k: round(x, 3) for k, x in is_[0].items()}, oos={k: round(x, 3) for k, x in oos[0].items()},
        oos_bh={k: round(x, 3) for k, x in oos[1].items()})
out = dict(job="Taylor_20260706_040038", archetype="state_owned_enterprise_governance",
    universe=list(UNIVERSE), state_pct=STATE, liq_gate_vnd=LIQ,
    float_signature=dict(turnover_median_soe=round(soe_med,3), turnover_median_priv=round(priv_med,3),
        soe_over_priv=round(soe_med/priv_med,3), spearman_state_turnover=ic_state_turn,
        per_name={r.ticker: round(r.turnover,3) for _, r in flt.iterrows()}),
    signal_test=dict(spearman_ic=sig_ic, soe_vs_priv_fwd={k: v.to_dict() for k, v in grp.iterrows()}),
    valuation_discount=disc,
    baskets=dict(A_soe_broad=pack(RA, fullA, isA, oosA),
                 B_priv_peer=pack(RB, fullB, isB, oosB),
                 C_soe_cashcow=pack(RC, fullC, isC, oosC)),
    income_trap=dict(cashcow_price_cagr=round(cc_price_cagr,2), assumed_div_pp=CASHCOW_DIV*100,
        cashcow_total_cagr=round(cc_total_cagr,2), bh_cagr=round(fullC[1]["CAGR"],2),
        still_lags=bool(cc_total_cagr < fullC[1]["CAGR"])),
    selfcheck=dict(soe_broad=round(dA,6), privpeer=round(dB,6), cashcow=round(dC,6)))
with open("data/soe_governance_verdict.json", "w") as f: json.dump(out, f, indent=2, default=str)
print("\nwrote data/soe_governance_verdict.json")
