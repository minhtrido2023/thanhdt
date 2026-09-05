"""CCS Phase 0 — per-trade ledger for BAL/LAG with PIT entry features.

Job Taylor_20260905_135003. EXTRACTION ONLY: no model change, no re-tune, no conclusion.

Sources (all one vintage = the frozen snapshot the R3 pin was measured on):
  - trade ledger  : data/v23_..._advprice_exp_repin0803_price_univpit.csv  (pinned R3 artifact,
                    self-check 0 VND, md5 7d053e6201c9d107685ff4d1dd9d2d2a)
  - PIT features  : data/bq_cache_asof20260729_postrestate/{ticker,universe_pit_q,
                    vnindex_5state_dt5g_live,fa_ratings_8l}
  - signal panels : ./dump/{sig_bal,sig_lag,lag_cand}.parquet  (probe rerun of the pinned command)

Data-registry check (coding_guidelines §9) done before wiring:
  universe_pit CANONICAL (price-volume/universe_pit.md) · vnindex_5state_dt5g_live CANONICAL
  (market-state/vnindex_5state_dt5g_live.md); tav2_bq.vnindex_5state is the TRAP base table - NOT used.
  breadth definition = convention 2026-08-22 (context_pack.md §"trục 2 mặc định"):
  COUNTIF(Close>MA200)/COUNT(*) over universe_pit, tercile = percentile within the 252 sessions BEFORE.

PIT discipline: every feature is measured at signal_date = last session STRICTLY BEFORE the first
fill (engine executes T+1 Open). Breadth additionally lagged one more session (t-1) per dispatch.
No profit_* column is read anywhere.
"""
import json
import os
import sys

import duckdb
import numpy as np
import pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.join(WC, "mike/agents/Taylor/research/ccs_phase0_Taylor_20260905_135003")
CACHE = os.path.join(WC, "data/bq_cache_asof20260729_postrestate")
PIN_CSV = os.path.join(WC, "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_"
                           "etfliqcustompitg_wtnamecap_advprice_exp_repin0803_price_univpit.csv")
DUMP = os.path.join(OUT, "dump")
BOOK_INIT_VND = 25e9          # each book is an independent 25B reference ledger (META combination_note)

con = duckdb.connect()
con.execute("SET threads=1")          # determinism, per results_registry note 6


def log(*a):
    print(*a, flush=True)


# ---------------------------------------------------------------- 1. read pinned audit file
raw = pd.read_csv(PIN_CSV, low_memory=False)
tx = raw[raw.record_type == "TX"].copy()
daily = raw[raw.record_type == "DAILY"].copy()
metric = raw[raw.record_type == "METRIC"].copy()
for c in ("shares", "adj_price", "buy_amount", "sell_amount", "fee", "cash_after"):
    tx[c] = pd.to_numeric(tx[c], errors="coerce")
tx["ymd"] = pd.to_datetime(tx["ymd"])
daily["ymd"] = pd.to_datetime(daily["ymd"])
for c in ("bal_cash_ref", "lag_cash_ref", "nav_bal_ref", "nav_lag_ref", "combined_nav"):
    daily[c] = pd.to_numeric(daily[c], errors="coerce")
tx["is_mtm"] = tx["reason"].astype(str).str.startswith("MTM")
log(f"[load] TX={len(tx)} DAILY={len(daily)} span {daily.ymd.min().date()}..{daily.ymd.max().date()}")

# --- repair: engine emits a handful of exit rows whose holding_id suffix is unresolved ("..._?").
# They are real exits of an existing buy group; left alone they orphan the sell and break the
# ledger<->NAV identity. Match on the "<TICKER>_<entrydate>_" prefix, and only when that prefix
# resolves to exactly ONE buy group whose bought shares equal the sold shares (else leave as-is).
_orph = tx.index[tx.holding_id.astype(str).str.endswith("_?")]
_repaired = []
for i in _orph:
    r = tx.loc[i]
    pref = str(r.holding_id)[:-1]
    cand = tx[(tx.book == r.book) & (tx.action == "buy")
              & tx.holding_id.astype(str).str.startswith(pref)]
    ids = cand.holding_id.unique()
    if len(ids) == 1 and abs(cand.shares.sum() - r.shares) < 1e-6:
        tx.loc[i, "holding_id"] = ids[0]
        _repaired.append((str(r.holding_id), ids[0], float(r.sell_amount)))
log(f"[repair] orphan '_?' exit rows: {len(_orph)} found, {len(_repaired)} matched -> {_repaired}")
assert len(_orph) == len(_repaired), "unmatched orphan exit row — ledger identity would not close"

# ---------------------------------------------------------------- 2. SELF-CHECK 0 VND (book level)
# Books are independent 25B reference ledgers; the allocator scales their RETURN STREAMS into
# combined NAV (META combination_note). VND contributions are additive at BOOK level only.
sc = {}
for book, cashcol, navcol in (("BAL", "bal_cash_ref", "nav_bal_ref"),
                              ("LAG", "lag_cash_ref", "nav_lag_ref")):
    b = tx[tx.book == book]
    cash_flows = b.loc[~b.is_mtm, "sell_amount"].fillna(0).sum() \
        - b.loc[~b.is_mtm, "buy_amount"].fillna(0).sum() \
        - b.loc[~b.is_mtm, "fee"].fillna(0).sum()
    cash_rebuilt = BOOK_INIT_VND + cash_flows
    cash_ref = daily[cashcol].iloc[-1]
    mtm_val = b.loc[b.is_mtm, "sell_amount"].fillna(0).sum()
    nav_rebuilt = cash_rebuilt + mtm_val
    nav_ref = daily[navcol].iloc[-1]
    sc[book] = dict(cash_rebuilt=cash_rebuilt, cash_ref=cash_ref,
                    cash_err_vnd=cash_rebuilt - cash_ref,
                    nav_rebuilt=nav_rebuilt, nav_ref=nav_ref,
                    nav_err_vnd=nav_rebuilt - nav_ref)
    log(f"[selfcheck {book}] cash err = {sc[book]['cash_err_vnd']:+.6f} VND | "
        f"NAV err = {sc[book]['nav_err_vnd']:+.6f} VND | final NAV {nav_ref/1e9:.4f}B")
sc["combined_nav_final"] = float(daily["combined_nav"].iloc[-1])
sc["metric_pin"] = {str(r.key): float(r.value) for r in metric.itertuples()
                    if str(r.key) in ("final_nav_vnd", "cagr", "sharpe_252", "max_dd",
                                      "calmar", "final_nav_bal_ref_vnd",
                                      "final_nav_lag_ref_vnd",
                                      "combination_replay_err_vnd")}
log(f"[selfcheck COMB] final combined NAV = {sc['combined_nav_final']/1e9:.4f}B "
    f"(pin 1178.01B) | METRIC cagr={sc['metric_pin'].get('cagr'):.6f} "
    f"calmar={sc['metric_pin'].get('calmar'):.4f}")

# ---------------------------------------------------------------- 3. build per-trade ledger
tx = tx.sort_values(["book", "holding_id", "ymd", "action"], kind="mergesort")
rows = []
for (book, hid), g in tx.groupby(["book", "holding_id"], sort=False):
    buys = g[g.action == "buy"]
    sells = g[g.action == "sell"]
    if buys.empty:
        continue                                    # MTM-only residual (PENDING_<book>) - not a trade
    play = str(buys["play_type"].iloc[0])
    cost = float(buys.buy_amount.sum() + buys.fee.sum())
    proceeds = float(sells.sell_amount.sum() - sells.fee.sum())
    closed = bool(len(sells)) and not bool(sells.is_mtm.any())
    rows.append(dict(
        book=book, ticker=str(buys.ticker.iloc[0]), holding_id=hid, play_type=play,
        entry_fill_date=buys.ymd.min(), last_fill_date=buys.ymd.max(), n_fill_days=int(len(buys)),
        exit_date=(sells.ymd.max() if len(sells) else pd.NaT),
        exit_reason=(str(sells.reason.iloc[-1]) if len(sells) else "OPEN_NO_SELL"),
        closed=closed, shares_bought=float(buys.shares.sum()),
        cost_vnd=cost, proceeds_vnd=proceeds,
        contribution_vnd=proceeds - cost,
        ret=(proceeds / cost - 1.0) if cost > 0 else np.nan,
        fee_vnd=float(buys.fee.sum() + sells.fee.sum()),
        entry_px=float(buys.adj_price.iloc[0]),
    ))
led = pd.DataFrame(rows)
led["is_park"] = led.play_type.eq("ETF_PARK")
led["holding_days"] = (led.exit_date - led.entry_fill_date).dt.days

# reconciliation: ledger contributions must rebuild each book's final NAV exactly
for book in ("BAL", "LAG"):
    s = led.loc[led.book == book, "contribution_vnd"].sum()
    err = BOOK_INIT_VND + s - sc[book]["nav_ref"]
    sc[book]["ledger_contrib_vnd"] = float(s)
    sc[book]["ledger_vs_nav_err_vnd"] = float(err)
    log(f"[selfcheck {book}] 25B + Σ ledger contribution − final NAV = {err:+.6f} VND "
        f"(Σ={s/1e9:.4f}B, n_trades={int((led.book == book).sum())})")

stock = led[~led.is_park].copy()                    # entries of the two books (parking vehicle excluded)
log(f"[ledger] total={len(led)} | stock entries BAL={int((stock.book=='BAL').sum())} "
    f"LAG={int((stock.book=='LAG').sum())} | parking lots={int(led.is_park.sum())}")

# ---------------------------------------------------------------- 4. trading calendar + signal_date
vni = con.execute(f"""SELECT DISTINCT time FROM read_parquet('{CACHE}/ticker/*.parquet')
                      WHERE ticker='VNINDEX' ORDER BY time""").df()
cal = pd.DatetimeIndex(pd.to_datetime(vni["time"]))
pos = {d: i for i, d in enumerate(cal)}


def prev_session(d, k=1):
    i = pos.get(pd.Timestamp(d))
    if i is None:
        i = int(cal.searchsorted(pd.Timestamp(d)))          # not a VNI session -> next index
    j = i - k
    return cal[j] if 0 <= j < len(cal) else pd.NaT


stock["signal_date"] = [prev_session(d, 1) for d in stock.entry_fill_date]
stock["holding_sessions"] = [
    (pos.get(pd.Timestamp(e), np.nan) - pos.get(pd.Timestamp(s), np.nan))
    if (pd.notna(e) and pd.Timestamp(e) in pos and pd.Timestamp(s) in pos) else np.nan
    for s, e in zip(stock.entry_fill_date, stock.exit_date)]

# ---------------------------------------------------------------- 5. per-ticker PIT price features
names = sorted(stock.ticker.unique())
q = f"""
SELECT ticker, time, Close, COALESCE(Price, Close) AS PxAdv, PE, Volume_3M_P50,
       CAST(FLOOR(ICB_Code/1000) AS INT) AS sector
FROM read_parquet('{CACHE}/ticker/*.parquet')
WHERE ticker IN ({','.join(chr(39)+t+chr(39) for t in names)})
  AND time BETWEEN DATE '2012-06-01' AND DATE '2026-06-19'
ORDER BY ticker, time"""
px = con.execute(q).df()
px["time"] = pd.to_datetime(px["time"])
log(f"[px] {len(px):,} rows / {px.ticker.nunique()} tickers")

px = px.sort_values(["ticker", "time"], kind="mergesort")
g = px.groupby("ticker", sort=False)["Close"]
px["hi252"] = g.transform(lambda s: s.rolling(252, min_periods=60).max())
px["dd52"] = px["Close"] / px["hi252"] - 1.0
px["ret1"] = g.transform(lambda s: s.pct_change())
px["vol60"] = px.groupby("ticker", sort=False)["ret1"].transform(
    lambda s: s.rolling(60, min_periods=30).std())
px["adv_vnd"] = px["Volume_3M_P50"] * px["PxAdv"]         # LAG_ADV_BASIS=price (production default)
px["ey"] = np.where(px["PE"] > 0, 1.0 / px["PE"], np.nan)

feat = px[["ticker", "time", "dd52", "vol60", "adv_vnd", "ey", "PE", "sector", "Close"]]
stock = stock.merge(feat, left_on=["ticker", "signal_date"], right_on=["ticker", "time"],
                    how="left").drop(columns=["time"])
stock["pct_adv"] = stock["cost_vnd"] / stock["adv_vnd"]
stock["r_multiple_stop"] = np.where(stock.book == "BAL", stock["ret"] / 0.20, np.nan)
stock["r_multiple_vol"] = stock["ret"] / (stock["vol60"] * np.sqrt(stock["holding_sessions"]))

# ---------------------------------------------------------------- 6. 1/PE tercile, cross-section PIT
uni = con.execute(f"""SELECT time, ticker FROM read_parquet('{CACHE}/universe_pit_q/*.parquet', union_by_name=true)
                      WHERE in_universe AND time BETWEEN DATE '2013-12-01' AND DATE '2026-06-19'""").df()
uni["time"] = pd.to_datetime(uni["time"])
log(f"[universe_pit] {len(uni):,} ticker-days, {uni.time.min().date()}..{uni.time.max().date()}")

ey_all = con.execute(f"""SELECT ticker, time, PE FROM read_parquet('{CACHE}/ticker/*.parquet')
                         WHERE time BETWEEN DATE '2013-12-01' AND DATE '2026-06-19' AND PE > 0""").df()
ey_all["time"] = pd.to_datetime(ey_all["time"])
ey_all["ey"] = 1.0 / ey_all["PE"]
cs = uni.merge(ey_all[["ticker", "time", "ey"]], on=["ticker", "time"], how="inner")
# The REFERENCE cross-section is universe_pit that day. A traded name is scored against it even when
# the name itself is not a member — LAG candidates come from the earnings panel, not from
# universe_pit, so restricting to members would drop ~half the LAG book from H2/H4.
cut_lo = cs.groupby("time")["ey"].quantile(1/3).rename("ey_q33")
cut_hi = cs.groupby("time")["ey"].quantile(2/3).rename("ey_q67")
cs_size = cs.groupby("time")["ey"].size().rename("ey_xsec_n")
cuts = pd.concat([cut_lo, cut_hi, cs_size], axis=1).reset_index()
stock = stock.merge(cuts, left_on="signal_date", right_on="time", how="left").drop(columns=["time"])
stock["ey_tercile"] = np.where(
    stock.ey.isna() | stock.ey_q33.isna(), None,
    np.where(stock.ey <= stock.ey_q33, "EXPENSIVE",
             np.where(stock.ey <= stock.ey_q67, "MID", "CHEAP")))
# exact percentile of the name inside that day's reference cross-section
_ey_by_day = {t: np.sort(g.to_numpy()) for t, g in cs.groupby("time")["ey"]}
stock["ey_pct"] = [
    (float(np.searchsorted(_ey_by_day[d], v, side="left")) / len(_ey_by_day[d]))
    if (pd.notna(v) and d in _ey_by_day and len(_ey_by_day[d])) else np.nan
    for d, v in zip(stock.signal_date, stock.ey)]

# ---------------------------------------------------------------- 7. 8L rating PIT
r8 = con.execute(f"""SELECT time, ticker, rating_8l, CAST(rating_asof AS DATE) AS rating_asof
                     FROM read_parquet('{CACHE}/universe_pit_q/*.parquet', union_by_name=true)
                     WHERE rating_8l IS NOT NULL
                       AND time BETWEEN DATE '2013-12-01' AND DATE '2026-06-19'""").df()
r8["time"] = pd.to_datetime(r8["time"])
stock = stock.merge(r8[["ticker", "time", "rating_8l", "rating_asof"]],
                    left_on=["ticker", "signal_date"], right_on=["ticker", "time"],
                    how="left").drop(columns=["time"])
# fallback for names outside universe_pit that day: fa_ratings_8l as-of (latest time <= signal_date)
fa = con.execute(f"SELECT ticker, time, rating FROM read_parquet('{CACHE}/fa_ratings_8l.parquet')").df()
fa["time"] = pd.to_datetime(fa["time"])
fa = fa.sort_values(["ticker", "time"], kind="mergesort")
need = stock.rating_8l.isna() & stock.signal_date.notna()
if need.any():
    left = stock.loc[need, ["ticker", "signal_date"]].reset_index().sort_values(
        "signal_date", kind="mergesort")
    tmp = pd.merge_asof(
        left, fa.rename(columns={"time": "signal_date"}).sort_values("signal_date",
                                                                     kind="mergesort"),
        on="signal_date", by="ticker", direction="backward")
    # merge_asof returns rows in ITS sort order — realign on the preserved original index, never
    # positionally (assigning .to_numpy() back into the unsorted frame silently scrambles ratings).
    tmp = tmp.set_index("index")["rating"]
    stock.loc[tmp.index, "rating_8l"] = tmp
    stock.loc[tmp.index[tmp.notna()], "rating_src"] = "fa_ratings_8l_asof"
stock["rating_src"] = stock["rating_src"].fillna("universe_pit_q") if "rating_src" in stock \
    else "universe_pit_q"

# ---------------------------------------------------------------- 8. DT5G state + sessions since upgrade
dt = con.execute(f"SELECT time, state FROM read_parquet('{CACHE}/vnindex_5state_dt5g_live.parquet') "
                 "ORDER BY time").df()
dt["time"] = pd.to_datetime(dt["time"])
# 2-writer architecture (registry market-state/vnindex_5state_dt5g_live.md): the table can carry a
# duplicate row for one session. Verified here that every duplicated time agrees on `state`, so
# de-duplicating cannot change any value.
_dupt = dt[dt.duplicated("time", keep=False)]
assert _dupt.groupby("time")["state"].nunique().le(1).all(), "dt5g duplicate rows disagree on state"
log(f"[dt5g] {len(dt)} rows, {dt.time.nunique()} sessions, {dt.time.duplicated().sum()} dup rows dropped")
dt = dt.drop_duplicates("time", keep="first")
dts = dt.set_index("time")["state"].reindex(cal).ffill()          # committed state, forward-filled
prev = dts.shift(1)
upgrade = (dts > prev) & prev.notna()
last_up = pd.Series(np.where(upgrade, np.arange(len(dts)), np.nan), index=dts.index).ffill()
sess_since = pd.Series(np.arange(len(dts)), index=dts.index) - last_up
dt_feat = pd.DataFrame({"signal_date": dts.index, "dt5g_state": dts.to_numpy(),
                        "sessions_since_dt5g_upgrade": sess_since.to_numpy()})
stock = stock.merge(dt_feat, on="signal_date", how="left")

# ---------------------------------------------------------------- 9. breadth tercile PIT (t-1)
# convention 2026-08-22: breadth = %(Close>MA200) over universe_pit; tercile = percentile of that
# value inside the 252 sessions BEFORE it. Dispatch: use breadth_{t-1}, never same-session.
br = con.execute(f"""
SELECT u.time, COUNT(*) AS n_univ,
       SUM(CASE WHEN t.Close > t.MA200 THEN 1 ELSE 0 END) AS n_above
FROM read_parquet('{CACHE}/universe_pit_q/*.parquet', union_by_name=true) AS u
JOIN read_parquet('{CACHE}/ticker/*.parquet') AS t ON t.ticker=u.ticker AND t.time=u.time
WHERE u.in_universe AND t.Close IS NOT NULL AND t.MA200 IS NOT NULL
GROUP BY u.time ORDER BY u.time""").df()
br["time"] = pd.to_datetime(br["time"])
br["breadth"] = br["n_above"] / br["n_univ"]
b = br.breadth.to_numpy()
pct = np.full(len(b), np.nan)
for i in range(252, len(b)):
    win = b[i - 252:i]                                   # 252 sessions BEFORE i, i excluded
    pct[i] = float((win < b[i]).mean())
br["pct252"] = pct
br["btile"] = pd.cut(br.pct252, [-1e-9, 1/3, 2/3, 1.0 + 1e-9], labels=["LOW", "MID", "HIGH"])
br.to_csv(os.path.join(OUT, "breadth_pit_frozen_exp.csv"), index=False)
brl = br[["time", "breadth", "pct252", "btile"]].copy()
brl["signal_date"] = [prev_session(d, -1) for d in brl.time]      # value of t-1 attached to session t
stock = stock.merge(brl.rename(columns={"breadth": "breadth_tm1", "pct252": "breadth_pct252_tm1",
                                        "btile": "breadth_tercile_tm1"})
                    [["signal_date", "breadth_tm1", "breadth_pct252_tm1", "breadth_tercile_tm1"]],
                    on="signal_date", how="left")

# ---------------------------------------------------------------- 10. signal rank/score + LAG surprise
TIER_PRIORITY = {}
try:
    sys.path.insert(0, WC)
    import simulate_holistic_nav as _shn
    TIER_PRIORITY = dict(_shn.TIER_PRIORITY)
except Exception as e:                                   # pragma: no cover
    log(f"[warn] could not import TIER_PRIORITY: {e}")
TIER_PRIORITY.update({"LAG_TOP": 90, "LAG_HI": 88, "LAG_LO": 82})

missing_feats = []
sb_path, sl_path, lc_path = (os.path.join(DUMP, f) for f in
                             ("sig_bal.parquet", "sig_lag.parquet", "lag_cand.parquet"))
if all(os.path.exists(p) for p in (sb_path, sl_path, lc_path)):
    # allowed_tiers = the pool simulate() actually ranks (shn.py:464), and _pri is
    # map(TIER_PRIORITY).fillna(0) (shn.py:1316) — the "_W" weak-name tiers really do fall to
    # priority 0 in the engine, so do NOT strip the suffix here.
    with open(os.path.join(DUMP, "rs_tier_weights.json")) as fh:
        BAL_TIERS = list(json.load(fh))
    LAG_TIERS = ["LAG_HI", "LAG_LO"]

    def rank_panel(df, book, allowed):
        d = df.copy()
        d["time"] = pd.to_datetime(d["time"])
        d = d[d["play_type"].isin(allowed)]
        d["_pri"] = d["play_type"].map(TIER_PRIORITY).fillna(0)
        d = d.sort_values(["time", "_pri", "ta"], ascending=[True, False, False], kind="mergesort")
        d["sig_rank"] = d.groupby("time").cumcount() + 1
        d["sig_n_cands"] = d.groupby("time")["ta"].transform("size")
        d["sig_rank_pct"] = (d["sig_rank"] - 1) / d["sig_n_cands"].clip(lower=1)
        d["book"] = book
        return d[["book", "ticker", "time", "play_type", "ta", "sig_rank",
                  "sig_n_cands", "sig_rank_pct"]]

    sb = rank_panel(pd.read_parquet(sb_path), "BAL", BAL_TIERS)
    sl = rank_panel(pd.read_parquet(sl_path), "LAG", LAG_TIERS)
    sig_all = pd.concat([sb, sl], ignore_index=True).rename(columns={"play_type": "sig_play_type"})
    # An entry does not always fill on the session right after its signal: shn queues it in
    # `pending_entries` and a slot/liquidity block can push the first fill out by a few sessions
    # (max_fill_days=5). So match the ORIGINATING signal with a backward as-of on the same ticker,
    # tolerance 5 sessions, and record the gap. Exact-date joining silently drops those entries
    # (measured: 0/452 BAL but 6/1498 LAG).
    _cal_i = pd.Series(range(len(cal)), index=cal)
    sig_all["_si"] = sig_all["time"].map(_cal_i)
    stock["_si"] = stock["signal_date"].map(_cal_i)
    sig_all = sig_all.dropna(subset=["_si"]).sort_values("_si", kind="mergesort")
    _left = stock[["book", "ticker", "_si"]].reset_index().dropna(subset=["_si"]) \
        .sort_values("_si", kind="mergesort")
    _m = pd.merge_asof(_left, sig_all.rename(columns={"time": "sig_signal_date"}),
                       on="_si", by=["book", "ticker"], direction="backward", tolerance=5)
    _m = _m.set_index("index")                      # realign by original index, never positionally
    for c in ("sig_play_type", "ta", "sig_rank", "sig_n_cands", "sig_rank_pct", "sig_signal_date"):
        stock[c] = _m[c]
    stock["entry_queue_sessions"] = stock["_si"] - stock["sig_signal_date"].map(_cal_i)
    stock = stock.drop(columns=["_si"])
    stock["sig_rank_tercile"] = pd.cut(stock.sig_rank_pct, [-1e-9, 1/3, 2/3, 1.0 + 1e-9],
                                       labels=["TOP", "MID", "BOTTOM"])

    lc = pd.read_parquet(lc_path)
    lc["sd"] = pd.to_datetime(lc["sd"])
    lc = lc.rename(columns={"sd": "signal_date", "surprise": "lag_surprise", "d_npr": "lag_d_npr"})
    keep = ["ticker", "signal_date", "lag_surprise"] + (["lag_d_npr"] if "lag_d_npr" in lc else [])
    lc["surp_pct"] = lc["lag_surprise"].rank(pct=True)
    lc["lag_surprise_tercile"] = pd.cut(lc.surp_pct, [-1e-9, 1/3, 2/3, 1.0 + 1e-9],
                                        labels=["LOW", "MID", "HIGH"])
    # same queue effect on the LAG candidate panel -> join on the matched signal date
    _lc = lc[keep + ["lag_surprise_tercile"]].drop_duplicates(["ticker", "signal_date"]) \
        .rename(columns={"signal_date": "sig_signal_date"})
    stock = stock.merge(_lc, on=["ticker", "sig_signal_date"], how="left")
else:
    missing_feats.append("sig_rank/sig_score (H6) + lag_surprise (H4): probe dump not found at "
                         + DUMP)
    for c in ("sig_rank", "sig_n_cands", "sig_rank_pct", "sig_rank_tercile",
              "lag_surprise", "lag_surprise_tercile"):
        stock[c] = np.nan

# ---------------------------------------------------------------- 11. write + coverage
stock["is_capit_arm"] = stock.play_type.astype(str).str.startswith(("CAPITB_", "CAPITL_"))
cols = ["book", "ticker", "holding_id", "play_type", "is_capit_arm", "sig_play_type",
        "entry_fill_date", "signal_date", "sig_signal_date", "entry_queue_sessions",
        "last_fill_date", "n_fill_days",
        "exit_date", "exit_reason", "closed", "holding_days", "holding_sessions",
        "dd52", "ey", "PE", "ey_pct", "ey_tercile", "rating_8l", "rating_asof", "rating_src",
        "pct_adv", "adv_vnd", "sector", "vol60", "ey_xsec_n",
        "dt5g_state", "sessions_since_dt5g_upgrade",
        "breadth_tm1", "breadth_pct252_tm1", "breadth_tercile_tm1",
        "sig_rank", "sig_n_cands", "sig_rank_pct", "sig_rank_tercile",
        "lag_surprise", "lag_surprise_tercile",
        "cost_vnd", "proceeds_vnd", "contribution_vnd", "fee_vnd",
        "ret", "r_multiple_stop", "r_multiple_vol", "entry_px", "shares_bought"]
cols = [c for c in cols if c in stock.columns]
stock = stock[cols].sort_values(["book", "entry_fill_date", "ticker"], kind="mergesort")
led_path = os.path.join(OUT, "trade_ledger_bal_lag_exp.csv")
stock.to_csv(led_path, index=False)
led.to_csv(os.path.join(OUT, "trade_ledger_all_incl_parking_exp.csv"), index=False)
log(f"[write] {led_path}  rows={len(stock)}")

cov = {c: float(stock[c].notna().mean()) for c in cols
       if c not in ("book", "ticker", "holding_id", "closed")}
sc["feature_coverage"] = cov
sc["missing_features"] = missing_feats
sc["n_entries"] = {"BAL": int((stock.book == "BAL").sum()), "LAG": int((stock.book == "LAG").sum())}
with open(os.path.join(OUT, "selfcheck_exp.json"), "w") as fh:
    json.dump(sc, fh, indent=2, default=str)
log("[coverage] " + ", ".join(f"{k}={v:.1%}" for k, v in sorted(cov.items()) if v < 0.995))
log("done.")
