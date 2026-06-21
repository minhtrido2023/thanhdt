# -*- coding: utf-8 -*-
"""pt_book_c.py — Book C (VALUE) paper-trade, 15B, forward track
================================================================
The 3rd book of V2.2-EXTENDED (Option A: BAL 17.5 + LAG 17.5 + VALUE 15 = 50B).
Runs as a SEPARATE parallel track alongside pt_v22_dt5g.py (the momentum-only
V2.2 live baseline). The combined V2.2+C NAV is assembled at the end from the
two momentum legs (read from pt_v22_dt5g_logs.csv) + this Book C, weighted
35/35/30 with cross-book Band +-10pp (book_rebal_policy.py finding).

BOOK C design (all validated this session — see SESSION_SYNTHESIS_2026_06_12.md):
  Signal      : vscore = PB.rank(pct) + PE.rank(pct), top quintile (<=20%)
  Quality gate: ROIC5Y>=8% AND FSCORE>=5, PE in (0,100), PB>0, liq>=10B  (V4)
  Weighting   : liquidity-weighted, name cap 25%
  Rotation    : MONTHLY, anchor day-10 (first trading day on/after the 10th)
                + initial deployment at START_DATE  (book_c_rebal_timing.py)
  DT5G gating : exposure = STATE_W[state] of book NAV. ASYMMETRIC —
                de-risk IMMEDIATELY when state drops (hands cash to capit in
                CRISIS); re-risk only at the next monthly rebalance (slow,
                price-confirmed). CRISIS 0 / BEAR 20 / NEUTRAL 70 / BULL 100 /
                EX-BULL 130%.
  Costs       : TC 0.30% on turnover.

5-state source: tav2_bq.vnindex_5state_dt5g_live
Outputs (analyze_portfolio-compatible):
  data/pt_book_c_logs.csv / _transactions.csv / _open_positions.csv / _report.md
  data/pt_v22c_combined_logs.csv  (+ section in report)  [if momentum legs present]
"""
import os, sys, io, subprocess
import numpy as np
import pandas as pd
from io import StringIO

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
from pt_dates import detect_end_date

# ---- config ----------------------------------------------------------------
START_DATE  = os.environ.get("PT_BOOK_C_START", "2026-06-11")  # pure forward; env override for smoke-test
END_DATE    = detect_end_date()
STATE_TABLE = "tav2_bq.vnindex_5state_dt5g_live"
VALUE_NAV   = 15e9
REBAL_DAY   = 10                    # anchor: first trading day on/after the 10th
QTILE       = 0.20
NAME_CAP    = 0.25
TC          = 0.003
LIQ_FLOOR   = 10e9
DERISK_BAND = 0.10                  # trim to target if deployed exceeds target by >10pp
STATE_W     = {1: 0.0, 2: 0.20, 3: 0.70, 4: 1.0, 5: 1.30}
STATE_NAME  = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}
PROJECT     = "lithe-record-440915-m9"
BQ_PATH     = r"bq"

LOGS_P  = os.path.join(WORKDIR, "data", "pt_book_c_logs.csv")
TX_P    = os.path.join(WORKDIR, "data", "pt_book_c_transactions.csv")
OPEN_P  = os.path.join(WORKDIR, "data", "pt_book_c_open_positions.csv")
REPORT_P= os.path.join(WORKDIR, "data", "pt_book_c_report.md")
COMB_P  = os.path.join(WORKDIR, "data", "pt_v22c_combined_logs.csv")
V22_LOGS= os.path.join(WORKDIR, "data", "pt_v22_dt5g_logs.csv")


def bq(sql):
    cmd = (f'"{BQ_PATH}" query --use_legacy_sql=false --project_id={PROJECT}'
           f' --format=csv --quiet --max_rows=500000')
    r = subprocess.run(cmd, input=sql, capture_output=True, text=True,
                       encoding="utf-8", shell=True)
    if r.returncode != 0:
        raise RuntimeError(f"BQ rc={r.returncode}\n{r.stderr[:400]}")
    return pd.read_csv(StringIO(r.stdout)) if r.stdout.strip() else pd.DataFrame()


print("=" * 96)
print(f"  BOOK C (VALUE) — paper-trade  |  {VALUE_NAV/1e9:.0f}B  |  {START_DATE} -> {END_DATE}")
print(f"  signal=PB+PE rank, gate ROIC5Y>=8/FSCORE>=5, day-10 monthly, DT5G gated")
print("=" * 96)


def live_picks_md():
    """Live 'what Book C should hold today' from ticker_1m (fresh ~16:40, no lag) +
    current DT5G state. Writes data/book_c_live_picks.csv, returns a markdown block.
    Always runs (even while the forward NAV track is still seeding)."""
    try:
        ls = bq(f"SELECT s.state FROM {STATE_TABLE} AS s ORDER BY s.time DESC LIMIT 1")
        cur_state = int(ls["state"].iloc[0]) if not ls.empty else 3
    except Exception:
        cur_state = 3
    exp = STATE_W.get(cur_state, 0.70)
    try:
        scr = bq(f"""
        WITH q AS (
          SELECT t.time, t.ticker, t.Close, t.PB, t.PE, t.ROIC5Y, t.FSCORE,
                 t.Trading_Value_1M_P50/1e9 AS liq_B,
                 PERCENT_RANK() OVER (ORDER BY t.PB ASC) pbr,
                 PERCENT_RANK() OVER (ORDER BY t.PE ASC) per
          FROM tav2_bq.ticker_1m t
          WHERE t.time = (SELECT MAX(time) FROM tav2_bq.ticker_1m)
            AND t.PB>0 AND t.PE>0 AND t.PE<100
            AND t.ROIC5Y>=0.08 AND t.FSCORE>=5
            AND t.Trading_Value_1M_P50>={LIQ_FLOOR}
        ), s AS (
          SELECT *, pbr+per AS vscore,
            PERCENT_RANK() OVER (ORDER BY pbr+per ASC) AS vrank FROM q
        )
        SELECT time, ticker, Close, PB, PE, ROUND(ROIC5Y*100,1) AS roic, FSCORE,
               ROUND(liq_B,1) AS liq_B, ROUND(vscore,3) AS vscore
        FROM s WHERE vrank<={QTILE} ORDER BY vscore""")
    except Exception as ex:
        return f"\n## Live target picks\n\n_screen failed: {ex}_\n"
    if scr.empty:
        return "\n## Live target picks (ticker_1m)\n\n_no names pass the V4 gate today_\n"
    liq = scr["liq_B"].clip(upper=scr["liq_B"].quantile(0.90))
    w = (liq / liq.sum()).clip(upper=NAME_CAP); w = w / w.sum()
    scr = scr.assign(weight_pct=(w * exp * 100).round(1),
                     target_B=(w * exp * VALUE_NAV / 1e9).round(2))
    asof = pd.to_datetime(scr["time"].iloc[0]).date()
    scr.drop(columns=["time"]).to_csv(
        os.path.join(WORKDIR, "data", "book_c_live_picks.csv"), index=False)
    md = (f"\n## Live target picks — ticker_1m {asof} "
          f"(state {STATE_NAME.get(cur_state)}, exposure {exp*100:.0f}% of 15B)\n\n"
          "| Ticker | Close | PB | PE | ROIC% | FSCORE | liq(B) | weight% | target(B) |\n"
          "|---|---|---|---|---|---|---|---|---|\n")
    for _, r in scr.iterrows():
        md += (f"| {r['ticker']} | {r['Close']:.0f} | {r['PB']:.2f} | {r['PE']:.1f} | "
               f"{r['roic']:.1f} | {int(r['FSCORE'])} | {r['liq_B']:.1f} | "
               f"{r['weight_pct']:.1f} | {r['target_B']:.2f} |\n")
    return md


# ---- seed helper -----------------------------------------------------------
def seed(reason):
    os.makedirs(os.path.join(WORKDIR, "data"), exist_ok=True)
    ts = pd.Timestamp(START_DATE)
    pd.DataFrame([{
        "ymd": ts, "nav": VALUE_NAV, "cash": VALUE_NAV, "stocks_mv": 0.0,
        "num_holdings": 0, "num_transactions": 0, "state": np.nan,
        "target_exposure": np.nan, "deployed_pct": 0.0,
    }]).to_csv(LOGS_P, index=False)
    pd.DataFrame(columns=["ymd", "ticker", "action", "buy_amount", "sell_amount",
                          "fee", "adj_price", "shares", "holding_id", "play_type",
                          "cash_after", "reason", "book"]).to_csv(TX_P, index=False)
    pd.DataFrame(columns=["ticker", "holding_id", "shares", "book"]).to_csv(OPEN_P, index=False)
    live_md = ""
    try: live_md = live_picks_md()
    except Exception as ex: live_md = f"\n_(live screen unavailable: {ex})_\n"
    with open(REPORT_P, "w", encoding="utf-8") as f:
        f.write("# pt_book_c — Book C (VALUE) on DT5G\n\n")
        f.write(f"*Start*: {START_DATE} (fresh 15B)  |  *Status*: **seeded, awaiting data**\n\n{reason}\n\n")
        f.write("*Init NAV*: 15B  |  *Final NAV*: 15.0000B  |  *Total ret*: +0.00%  |  0 sessions\n")
        f.write(live_md)
    print(f"\n[SEED] {reason}")
    if live_md and "|" in live_md:
        print("[SEED] Live target picks written (data/book_c_live_picks.csv).")
    print(f"[SEED] Wrote 15B seed for {START_DATE}; compounds once data >= {START_DATE} lands.")


if pd.Timestamp(END_DATE) < pd.Timestamp(START_DATE):
    seed(f"No trading data yet (latest BQ = {END_DATE} < start {START_DATE}).")
    sys.exit(0)

# ============================================================================
# 1. Trading-day calendar + DT5G state (window)
# ============================================================================
print("\n[1] Calendar + DT5G state...")
cal = bq(f"""
SELECT DISTINCT t.time FROM tav2_bq.ticker_prune AS t
WHERE t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY t.time
""")
cal["time"] = pd.to_datetime(cal["time"])
days = list(cal["time"])
if not days:
    seed(f"No ticker_prune rows in window {START_DATE}..{END_DATE}.")
    sys.exit(0)

st = bq(f"""SELECT s.time, s.state FROM {STATE_TABLE} AS s
WHERE s.time <= DATE '{END_DATE}' ORDER BY s.time""")
st["time"] = pd.to_datetime(st["time"])
state_by = dict(zip(st["time"], st["state"]))
# forward-fill state across trading days
state_ff, last = {}, 3
for d in days:
    if d in state_by and pd.notna(state_by[d]):
        last = int(state_by[d])
    state_ff[d] = last

# ---- rebalance dates: first trading day on/after REBAL_DAY each month + START
rebal_dates = [days[0]]            # initial deployment at start
seen_months = {(days[0].year, days[0].month)}
for d in days:
    key = (d.year, d.month)
    if key not in seen_months and d.day >= REBAL_DAY:
        rebal_dates.append(d)
        seen_months.add(key)
    elif key not in seen_months and d == [x for x in days if (x.year, x.month) == key][-1]:
        # month ended before day-10 had a trading day -> use last available day
        rebal_dates.append(d)
        seen_months.add(key)
rebal_dates = sorted(set(rebal_dates))
print(f"  trading days: {len(days)}  |  rebalance dates: {[d.date().isoformat() for d in rebal_dates]}")

# ============================================================================
# 2. Screen picks at each rebalance date (point-in-time, V4 gate)
# ============================================================================
print("\n[2] Screening value picks per rebalance date...")
rd_literals = ", ".join(f"DATE '{d.date()}'" for d in rebal_dates)
screen = bq(f"""
WITH universe AS (
  SELECT t.time, t.ticker, t.PB, t.PE, t.ROIC5Y, t.FSCORE,
         t.Trading_Value_1M_P50 AS liq
  FROM tav2_bq.ticker_prune AS t
  WHERE t.time IN ({rd_literals})
    AND t.PB > 0 AND t.PE > 0 AND t.PE < 100
    AND t.ROIC5Y >= 0.08 AND t.FSCORE >= 5
    AND t.Trading_Value_1M_P50 >= {LIQ_FLOOR}
),
ranked AS (
  SELECT *,
    PERCENT_RANK() OVER (PARTITION BY time ORDER BY PB ASC) AS pbr,
    PERCENT_RANK() OVER (PARTITION BY time ORDER BY PE ASC) AS per
  FROM universe
),
scored AS (
  SELECT *, pbr + per AS vscore,
    PERCENT_RANK() OVER (PARTITION BY time ORDER BY pbr + per ASC) AS vrank
  FROM ranked
)
SELECT time, ticker, PB, PE, ROIC5Y, FSCORE, liq, vscore
FROM scored WHERE vrank <= {QTILE} ORDER BY time, vscore
""")
screen["time"] = pd.to_datetime(screen["time"])

# target weights per rebalance date (liq-weighted, name-capped, renormalized)
picks_by_date = {}
for d, g in screen.groupby("time"):
    g = g.copy()
    liq = g["liq"].clip(upper=g["liq"].quantile(0.90))   # damp megacap dominance
    w = liq / liq.sum()
    w = w.clip(upper=NAME_CAP)
    w = w / w.sum()
    picks_by_date[d] = dict(zip(g["ticker"], w))
    print(f"  {d.date()}: {len(g)} picks -> {', '.join(g['ticker'].tolist()[:8])}")

# ============================================================================
# 3. Daily Close panel for all tickers ever held/candidate
# ============================================================================
print("\n[3] Price panel...")
all_tk = sorted({t for d in picks_by_date for t in picks_by_date[d]})
prices = {}
if all_tk:
    tk_lit = ", ".join(f"'{t}'" for t in all_tk)
    pr = bq(f"""SELECT t.time, t.ticker, t.Close FROM tav2_bq.ticker_prune AS t
    WHERE t.ticker IN ({tk_lit})
      AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'""")
    pr["time"] = pd.to_datetime(pr["time"])
    for tk, g in pr.groupby("ticker"):
        prices[tk] = dict(zip(g["time"], g["Close"]))

def px(tk, d):
    """Last known close on/before d."""
    m = prices.get(tk, {})
    if d in m: return m[d]
    cands = [x for x in m if x <= d]
    return m[max(cands)] if cands else None

# ============================================================================
# 4. Daily simulation
# ============================================================================
print("\n[4] Simulating Book C day-by-day...")
cash = VALUE_NAV
holds = {}                 # ticker -> shares
tx, log_rows = [], []
hid = 0
rebal_set = set(rebal_dates)

def book_nav(d):
    mv = sum(sh * (px(tk, d) or 0) for tk, sh in holds.items())
    return cash + mv, mv

for d in days:
    state = state_ff[d]
    target_exp = STATE_W.get(state, 0.70)

    # ---- a) REBALANCE (monthly anchor) -> full reset to target picks * exposure
    if d in rebal_set and d in picks_by_date:
        nav_now, _ = book_nav(d)
        tgt_w = picks_by_date[d]
        budget = nav_now * target_exp
        # desired VND per name
        desired = {tk: budget * w for tk, w in tgt_w.items()}
        # sell names not in target (or trim) ; buy/top-up names in target
        # 1) sells
        for tk in list(holds.keys()):
            p = px(tk, d)
            if p is None: continue
            cur_val = holds[tk] * p
            want = desired.get(tk, 0.0)
            if want < cur_val:                  # trim or full exit
                sell_val = cur_val - want
                sh_sell = sell_val / p
                fee = sell_val * TC
                cash += sell_val - fee
                holds[tk] -= sh_sell
                if holds[tk] * p < 1e6: holds.pop(tk, None)
                tx.append(dict(ymd=d, ticker=tk, action="sell", buy_amount=0.0,
                               sell_amount=sell_val, fee=fee, adj_price=p,
                               shares=sh_sell, holding_id=f"C{hid}", play_type="VALUE",
                               cash_after=cash, reason="REBAL_trim", book="VALUE"))
                hid += 1
        # 2) buys / top-ups
        for tk, want in sorted(desired.items(), key=lambda x: -x[1]):
            p = px(tk, d)
            if p is None or want <= 0: continue
            cur_val = holds.get(tk, 0.0) * p
            if want > cur_val:
                buy_val = min(want - cur_val, cash / (1 + TC))
                if buy_val < 1e6: continue
                fee = buy_val * TC
                cash -= buy_val + fee
                holds[tk] = holds.get(tk, 0.0) + buy_val / p
                tx.append(dict(ymd=d, ticker=tk, action="buy", buy_amount=buy_val,
                               sell_amount=0.0, fee=fee, adj_price=p,
                               shares=buy_val / p, holding_id=f"C{hid}", play_type="VALUE",
                               cash_after=cash, reason="REBAL_buy", book="VALUE"))
                hid += 1

    # ---- b) INTRA-MONTH DE-RISK (asymmetric): if state dropped, trim to target now
    else:
        nav_now, mv = book_nav(d)
        deployed = mv / nav_now if nav_now > 0 else 0.0
        if deployed - target_exp > DERISK_BAND and mv > 0:
            # sell pro-rata down to target exposure
            target_mv = nav_now * target_exp
            sell_total = mv - target_mv
            for tk in list(holds.keys()):
                p = px(tk, d)
                if p is None: continue
                cur_val = holds[tk] * p
                sell_val = sell_total * (cur_val / mv)
                sh_sell = sell_val / p
                fee = sell_val * TC
                cash += sell_val - fee
                holds[tk] -= sh_sell
                if holds[tk] * p < 1e6: holds.pop(tk, None)
                tx.append(dict(ymd=d, ticker=tk, action="sell", buy_amount=0.0,
                               sell_amount=sell_val, fee=fee, adj_price=p,
                               shares=sh_sell, holding_id=f"C{hid}", play_type="VALUE",
                               cash_after=cash, reason=f"DERISK_state{state}", book="VALUE"))
                hid += 1

    # ---- c) end-of-day MTM log
    nav_now, mv = book_nav(d)
    log_rows.append(dict(ymd=d, nav=nav_now, cash=cash, stocks_mv=mv,
                         num_holdings=len(holds),
                         num_transactions=len(tx),
                         state=state, target_exposure=target_exp,
                         deployed_pct=(mv / nav_now * 100) if nav_now > 0 else 0.0))

logs = pd.DataFrame(log_rows)

# ============================================================================
# 5. Save Book C standalone outputs
# ============================================================================
print("\n[5] Saving Book C outputs...")
os.makedirs(os.path.join(WORKDIR, "data"), exist_ok=True)
last_day = days[-1]

# MTM phantom sells for open positions (analyze_portfolio convention)
open_rows, mtm = [], []
for tk, sh in holds.items():
    p = px(tk, last_day)
    if p is None: continue
    open_rows.append(dict(ticker=tk, holding_id="C_open", shares=sh, book="VALUE",
                          last_price=p, mark_value=sh * p))
    mtm.append(dict(ymd=last_day, ticker=tk, action="sell", buy_amount=0.0,
                    sell_amount=sh * p, fee=0.0, adj_price=p, shares=sh,
                    holding_id="C_open", play_type="VALUE", cash_after=None,
                    reason="MTM_UNREALIZED", book="VALUE"))
tx_all = pd.DataFrame(tx)
if mtm:
    tx_all = pd.concat([tx_all, pd.DataFrame(mtm)], ignore_index=True)
if not tx_all.empty:
    tx_all = tx_all.sort_values(["ymd", "action", "ticker"]).reset_index(drop=True)

logs.to_csv(LOGS_P, index=False)
tx_all.to_csv(TX_P, index=False)
pd.DataFrame(open_rows if open_rows else
             [], columns=["ticker", "holding_id", "shares", "book", "last_price", "mark_value"]
             ).to_csv(OPEN_P, index=False)

final_nav = logs["nav"].iloc[-1]
years = max((last_day - days[0]).days / 365.25, 1e-9)
tot = (final_nav / VALUE_NAV - 1) * 100
cagr = (final_nav / VALUE_NAV) ** (1 / years) - 1 if years > 0.05 else 0.0
peak = logs.set_index("ymd")["nav"].cummax()
dd = ((logs.set_index("ymd")["nav"] - peak) / peak).min() * 100

print("\n" + "=" * 96)
print(f" BOOK C SUMMARY  |  {days[0].date()} -> {last_day.date()} ({years:.3f}y, {len(days)} sessions)")
print(f" Init 15B  Final {final_nav/1e9:.4f}B  ret={tot:+.2f}%  MaxDD={dd:+.2f}%  "
      f"state={STATE_NAME.get(state_ff[last_day])}  holdings={len(holds)}")
print("=" * 96)

# ============================================================================
# 6. COMBINED V2.2 + C  (read momentum legs from pt_v22_dt5g_logs, Band +-10pp)
# ============================================================================
print("\n[6] Combined V2.2+C track (35/35/30, Band +-10pp)...")
combined_done = False
try:
    v22 = pd.read_csv(V22_LOGS, parse_dates=["ymd"])
    # reconstruct leg NAVs from the momentum track
    v22["bal_nav"]  = v22["BAL_cash"] + v22["BAL_stocks"] + v22["BAL_etf"]
    v22["lag_nav"]  = v22["SECOND_cash"] + v22["SECOND_stocks"] + v22["SECOND_etf"]
    v22 = v22.set_index("ymd").sort_index()
    bc = logs.set_index("ymd")["nav"]

    common = v22.index.intersection(bc.index)
    if len(common) >= 2:
        rb = v22["bal_nav"].loc[common].pct_change().fillna(0.0)
        rl = v22["lag_nav"].loc[common].pct_change().fillna(0.0)
        rv = bc.loc[common].pct_change().fillna(0.0)
        target = np.array([0.35, 0.35, 0.30]); band = 0.10
        w = target.copy(); navs = []; cur = 1.0
        for i, d in enumerate(common):
            r = np.array([rb.loc[d], rl.loc[d], rv.loc[d]])
            pr = float(np.dot(w, r))
            wd = w * (1 + r); wd = wd / wd.sum()
            if i > 0 and np.any(np.abs(wd - target) > band):
                pr -= np.abs(target - wd).sum() / 2 * TC
                w = target.copy()
            else:
                w = wd
            cur *= (1 + pr); navs.append(cur)
        comb = pd.Series(navs, index=common) * 50e9
        comb_df = pd.DataFrame({
            "ymd": common,
            "nav": comb.values,
            "bal_nav": v22["bal_nav"].loc[common].values * 0.7,   # 25B->17.5B notional
            "lag_nav": v22["lag_nav"].loc[common].values * 0.7,
            "value_nav": bc.loc[common].values,
            "state": v22["state"].loc[common].values if "state" in v22 else np.nan,
        })
        comb_df.to_csv(COMB_P, index=False)
        cf = comb.iloc[-1]; ct = (cf / 50e9 - 1) * 100
        cp = comb.cummax(); cdd = ((comb - cp) / cp).min() * 100
        print(f"  Combined: 50B -> {cf/1e9:.4f}B  ret={ct:+.2f}%  MaxDD={cdd:+.2f}%  ({len(common)} sessions)")
        combined_done = True
    else:
        print("  (momentum legs present but <2 overlapping sessions — combined deferred)")
except FileNotFoundError:
    print(f"  (pt_v22_dt5g_logs.csv not found — run pt_v22_dt5g.py first for combined view)")

# ============================================================================
# 7. Report
# ============================================================================
with open(REPORT_P, "w", encoding="utf-8") as f:
    f.write("# pt_book_c — Book C (VALUE) on DT5G\n\n")
    f.write(f"*Period*: {days[0].date()} -> {last_day.date()} ({years:.3f}y, {len(days)} sessions)\n\n")
    f.write(f"*Init*: 15B  |  *Final*: {final_nav/1e9:.4f}B  |  *Ret*: {tot:+.2f}%  |  "
            f"*MaxDD*: {dd:+.2f}%  |  *State*: {STATE_NAME.get(state_ff[last_day])} "
            f"(exposure {STATE_W.get(state_ff[last_day],0.7)*100:.0f}%)\n\n")
    f.write(f"*Holdings*: {len(holds)}  |  *Rebalances*: {len(rebal_dates)} "
            f"(day-{REBAL_DAY} monthly anchor)\n\n")
    if open_rows:
        f.write("## Open positions\n\n| Ticker | Shares | Value (B) |\n|---|---|---|\n")
        for r in sorted(open_rows, key=lambda x: -x["mark_value"]):
            f.write(f"| {r['ticker']} | {r['shares']:,.0f} | {r['mark_value']/1e9:.3f} |\n")
        f.write("\n")
    if combined_done:
        f.write("## Combined V2.2 + C (35/35/30, Band +-10pp)\n\n")
        f.write(f"See `data/pt_v22c_combined_logs.csv`. Final {cf/1e9:.4f}B / "
                f"ret {ct:+.2f}% / MaxDD {cdd:+.2f}%.\n")
    try:
        f.write(live_picks_md())
    except Exception as ex:
        f.write(f"\n_(live screen unavailable: {ex})_\n")
print(f"  reports -> {REPORT_P}")
print("\nDone. Run analyze_portfolio.py on pt_book_c_* for the full breakdown.")
