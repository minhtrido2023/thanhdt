# -*- coding: utf-8 -*-
"""CCS Phase 2 — STEP 0 GATE: when 50% of a BOTTOM-tercile order's target weight is cut,
where does the freed capital actually go on the harness?

Measured on the two legs (ctrl = pinned R3 reproduced byte-identically; trim50 = treatment),
per BOOK and per YEAR, entirely from the engine's own DAILY per-book ledger:

  outstanding_cut_frac(d) = sum over trimmed holdings ALIVE on d of cut_vnd / book_nav_treat(d)
        = the share of book NAV the trim removed from the intended stock exposure on day d.
  d_cash_frac(d)   = cash_frac_treat(d)   - cash_frac_ctrl(d)
  d_stocks_frac(d) = stocks_frac_treat(d) - stocks_frac_ctrl(d)
  d_etf_frac(d)    = etf_frac_treat(d)    - etf_frac_ctrl(d)

  redeploy_ratio = 1 - mean(d_cash_frac) / mean(outstanding_cut_frac)
      1.0 = every VND cut was put back to work (more names / bigger parking / CAPIT)
      0.0 = every VND cut sat in cash at 0%/yr (per the shared cost convention)

Nothing here re-runs the engine; it reads the two legs' artifacts only.
"""
import os, sys, json
import numpy as np
import pandas as pd

D = os.path.dirname(os.path.abspath(__file__))
CTRL, TRIM = "ctrl", "trim50"
BOOKS = {"BAL": ("nav_bal_ref", "bal_cash_ref", "bal_stocks_ref", "bal_etf_ref"),
         "LAG": ("nav_lag_ref", "lag_cash_ref", "lag_stocks_ref", "lag_etf_ref")}

def daily(leg):
    d = pd.read_csv(os.path.join(D, f"daily_{leg}_exp.csv"), parse_dates=["ymd"])
    return d.set_index("ymd")

dc, dt = daily(CTRL), daily(TRIM)
assert dc.index.equals(dt.index), "calendars differ between legs"
cal = list(dc.index)

tx = pd.read_csv(os.path.join(D, f"tx_{TRIM}_exp.csv"), parse_dates=["ymd"])
tl = pd.read_csv(os.path.join(D, f"trimlog_{TRIM}_exp.csv"), parse_dates=["ymd"])

# The engine simulates each book TWICE: a "base" pass (whose cash path only SIZES the CAPIT arm)
# and the "main" pass that produces the reported ledger. Only the main pass is the traded book.
tl_main = tl[tl["pass"] == "main"].copy()
# target_value is recomputed every session until the first fill lands, so an entry can appear on
# several consecutive sessions. The LAST row is the session the size was actually committed on.
tl_main = tl_main.sort_values("ymd").drop_duplicates(["book", "ticker", "seq_id"], keep="last")

# ---- holding spans of the trimmed entries, from the treatment leg's own TX ------------------
buys = tx[tx["action"] == "buy"].groupby("holding_id")["ymd"].min()
sells = tx[tx["action"] == "sell"].groupby("holding_id")["ymd"].max()
tl_main["entry_ymd"] = tl_main["holding_id"].map(buys)
tl_main["exit_ymd"] = tl_main["holding_id"].map(sells)
matched = tl_main["entry_ymd"].notna()
print(f"[match] trimmed first-fill targets (main pass): {len(tl_main)}  "
      f"matched to a real fill in TX: {int(matched.sum())} "
      f"({matched.mean():.1%})  unmatched = sized but never bought (liquidity/slot/cash block)")
tlm = tl_main[matched].copy()
tlm["exit_ymd"] = tlm["exit_ymd"].fillna(pd.Timestamp(cal[-1]))

# ---- per-day outstanding cut, per book ------------------------------------------------------
idx = pd.DatetimeIndex(cal)
rows = []
for bk, (navc, cashc, stkc, etfc) in BOOKS.items():
    out_vnd = pd.Series(0.0, index=idx)
    sub = tlm[tlm["book"] == bk]
    for _, r in sub.iterrows():
        m = (idx >= r["entry_ymd"]) & (idx <= r["exit_ymd"])
        out_vnd[m] += float(r["cut_vnd"])
    f = pd.DataFrame({
        "out_cut_frac": out_vnd / dt[navc],
        "d_cash":   dt[cashc] / dt[navc] - dc[cashc] / dc[navc],
        "d_stocks": dt[stkc] / dt[navc] - dc[stkc] / dc[navc],
        "d_etf":    dt[etfc] / dt[navc] - dc[etfc] / dc[navc],
    })
    f["book"] = bk
    f["year"] = f.index.year
    rows.append(f)
F = pd.concat(rows)

def block(g):
    oc = g["out_cut_frac"].mean()
    dcash = g["d_cash"].mean()
    return pd.Series({
        "sessions": len(g),
        "mean_out_cut_frac_pct": 100 * oc,
        "mean_d_cash_pct": 100 * dcash,
        "mean_d_stocks_pct": 100 * g["d_stocks"].mean(),
        "mean_d_etf_pct": 100 * g["d_etf"].mean(),
        "redeploy_ratio": (np.nan if oc <= 0 else 1.0 - dcash / oc),
    })

by_book = F.groupby("book").apply(block, include_groups=False)
by_year = F.groupby(["book", "year"]).apply(block, include_groups=False)
overall = block(F)

pd.set_option("display.width", 200, "display.float_format", lambda v: f"{v:,.4f}")
print("\n=== STEP 0 — per BOOK (whole 2014-01-02 -> 2026-06-19 window) ===")
print(by_book.to_string())
print("\n=== STEP 0 — per BOOK x YEAR ===")
print(by_year.to_string())
print("\n=== STEP 0 — pooled over both books ===")
print(overall.to_string())

# ---- corroborating counts: did the trim leg actually hold MORE names? -----------------------
def counts(leg):
    t = pd.read_csv(os.path.join(D, f"tx_{leg}_exp.csv"), parse_dates=["ymd"])
    t = t[t["reason"] != "MTM_FINAL"] if "reason" in t else t
    b = t[t["action"] == "buy"]
    return {"n_buy_fills": len(b),
            "n_holdings": b["holding_id"].nunique(),
            "gross_bought_bn": b["buy_amount"].sum() / 1e9}
cnt = {"ctrl": counts(CTRL), "trim50": counts(TRIM)}
print("\n=== corroboration: entry counts / gross deployed ===")
print(pd.DataFrame(cnt).to_string())

# ---- headline metrics of both legs ----------------------------------------------------------
def metrics(leg):
    m = pd.read_csv(os.path.join(D, f"metric_{leg}_exp.csv"))
    return m.set_index("key")["value"]
mc, mt = metrics(CTRL), metrics(TRIM)
keys = [k for k in mc.index if k in set(mt.index)]
cmp_ = pd.DataFrame({"ctrl": mc[keys], "trim50": mt[keys]})
print("\n=== headline / self-check (both legs) ===")
print(cmp_.loc[[k for k in cmp_.index if any(s in k for s in
      ("cagr", "CAGR", "sharpe", "maxdd", "calmar", "final_nav", "cash_flow_identity",
       "selfcheck", "self_check", "identity"))]].to_string())

out = {"by_book": by_book.reset_index().to_dict("records"),
       "by_book_year": by_year.reset_index().to_dict("records"),
       "pooled": overall.to_dict(),
       "n_trimmed_targets_main": int(len(tl_main)),
       "n_trimmed_filled": int(matched.sum()),
       "total_cut_vnd_filled": float(tlm["cut_vnd"].sum()),
       "counts": cnt}
with open(os.path.join(D, "step0_result_exp.json"), "w") as fh:
    json.dump(out, fh, indent=2, default=str)
F.reset_index().rename(columns={"index": "ymd"}).to_csv(os.path.join(D, "step0_daily_exp.csv"), index=False)
print("\nwrote step0_result_exp.json + step0_daily_exp.csv")
