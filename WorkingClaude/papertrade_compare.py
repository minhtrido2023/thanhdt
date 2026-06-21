# -*- coding: utf-8 -*-
"""Paper-trade comparison report — 4 systems side-by-side.

Updated 2026-05-27:
  - Removed V3 (pt_v12_live) — alt state test no longer needed
  - Renamed to architecture-based names (V11 / V12 / V121_ENS / V121_Kelly)

Reads:
  data/pt_v11_tq34b_logs.csv     (V11        = Song Sinh: BAL+VN30 + TQ34b)
  data/pt_v12_tq34b_logs.csv     (V12        = Âm Dương: BAL+LAGGED + TQ34b)
  data/pt_v121_ens_logs.csv      (V121_ENS   = V12.1 + Ensemble M1+M3r AND-HOLD + BASE)
  data/pt_v121_ens_q2_logs.csv   (V121_Kelly = V121_ENS + Kelly NEUTRAL{3:1.0})

Plus VNINDEX from BQ for the same window as a passive benchmark.

Writes:
  data/papertrade_compare5.md    — markdown comparison report
  data/papertrade_compare5.csv   — daily NAV/return for all 4 + VNI
"""
import os, sys, io, datetime as dt
import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
from simulate_holistic_nav import bq

# Production base = DT4G + MACRO overlay (adopted 2026-05-29). V11/V12 on it;
# ensemble (V121) still on TQ34b pending integrated validation.
SYSTEMS = [
    ("V11",         "V11 Song Sinh + KELLY + DT5G ⭐",             "data/pt_v11_tq34b_logs.csv"),
    ("V12",         "V12 Âm Dương (BAL+LAGGED) + DT5G ⭐",         "data/pt_v12_macro_logs.csv"),
    # V121_ENS / V121_Kelly (ensemble M1+M3 switch) REMOVED from daily comparison 2026-06-16:
    # faithful audit (T+1 Open, BQ) = 16.85% < V11 19.80% < V2.3 21-22%; the ~24% ensemble edge
    # was a reduced-harness artifact (see audited_versions_tally_2026 / dt4_ensemble_smart_integration).
    # Scripts pt_v121_ensemble.py / pt_v121_ens_q2.py kept for reference; no longer run daily.
    ("V4_DT5G",     "V4 12.1 (V121_ENS + BASE) + DT5G — fresh 2026-06-01", "data/pt_v4_dt5g_logs.csv"),
    ("V23",         "V2.3 = V2.2 (BAL|LAG static + park) + capit — fresh 2026-06-11 ⭐", "data/pt_v22_dt5g_logs.csv"),
]


def vni_series(start: str, end: str) -> pd.Series:
    df = bq(f"SELECT t.time, t.Close FROM tav2_bq.ticker AS t "
            f"WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{start}' AND DATE '{end}' "
            f"ORDER BY t.time")
    df["time"] = pd.to_datetime(df["time"])
    return df.set_index("time")["Close"]


def stats(nav: pd.Series) -> dict:
    nav = nav.dropna()
    if len(nav) < 2: return {}
    ret_total = nav.iloc[-1]/nav.iloc[0] - 1
    days = (nav.index[-1] - nav.index[0]).days
    years = days / 365.25
    cagr = (1+ret_total)**(1/years) - 1 if years > 0 else 0
    daily_ret = nav.pct_change().dropna()
    vol_ann = daily_ret.std() * np.sqrt(252)
    sharpe = (daily_ret.mean()*252)/vol_ann if vol_ann > 0 else 0
    peak = nav.cummax()
    dd = (nav-peak)/peak
    max_dd = dd.min()
    calmar = cagr/abs(max_dd) if max_dd < 0 else float("nan")
    # ---- GRIND LENS: current drawdown depth + how long underwater + recent momentum ----
    peak_date = nav.idxmax()
    cur_dd = nav.iloc[-1]/peak.iloc[-1] - 1            # drawdown from running peak (0 = at high)
    underwater_days = (nav.index[-1] - peak_date).days  # 0 if currently at a high
    def _trail(n):                                      # trailing return over last n sessions
        return (nav.iloc[-1]/nav.iloc[-1-n] - 1) if len(nav) > n else float("nan")
    ret_1m, ret_3m = _trail(21), _trail(63)
    return {"start": nav.index[0].date(), "end": nav.index[-1].date(),
            "days": days, "init": nav.iloc[0], "final": nav.iloc[-1],
            "ret_total": ret_total, "cagr": cagr, "vol_ann": vol_ann,
            "sharpe": sharpe, "max_dd": max_dd, "calmar": calmar,
            "cur_dd": cur_dd, "underwater_days": underwater_days,
            "peak_date": peak_date.date(), "ret_1m": ret_1m, "ret_3m": ret_3m}


def main():
    rows = {}
    nav_all = {}
    for key, name, path in SYSTEMS:
        full = os.path.join(WORKDIR, path)
        if not os.path.exists(full):
            print(f"  MISSING: {full}"); continue
        df = pd.read_csv(full, parse_dates=["ymd"]).sort_values("ymd")
        nav = df.set_index("ymd")["nav"]
        s = stats(nav)
        if not s:
            # Fresh/seed track with <2 sessions — not enough data for metrics yet.
            print(f"  SEEDED (awaiting data, {len(nav)} row): {name}")
            continue
        nav_all[key] = nav
        s["name"] = name; rows[key] = s

    if not rows:
        print("No logs found. Run pt_v11_tq34b.py / pt_v12_tq34b.py / pt_v12_live.py first.")
        return

    # VNI benchmark over same window
    first = min(s["start"] for s in rows.values())
    last  = max(s["end"]   for s in rows.values())
    try:
        vni = vni_series(first.strftime("%Y-%m-%d"), last.strftime("%Y-%m-%d"))
        # rebase to 50B at first day
        vni_nav = (vni / vni.iloc[0]) * 50e9
        nav_all["VNI_BH"] = vni_nav
        rows["VNI_BH"] = {**stats(vni_nav), "name": "VNINDEX Buy & Hold (rebased 50B)"}
    except Exception as e:
        print(f"  VNI load failed: {e}")

    # ------------------------------------------------------------------
    # Write markdown
    # ------------------------------------------------------------------
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    md = []
    md.append(f"# Paper-Trade Comparison — 5 Systems\n")
    md.append(f"*Generated: {now}*\n")
    md.append(f"*Window: {first} → {last} ({(last-first).days} calendar days)*\n")
    md.append(f"*Init NAV: 50B VND fresh, all-cash, no positions (each system)*\n\n")

    md.append("## Headline metrics\n")
    md.append("| System | Final NAV | Total Ret | CAGR | Vol (ann) | Sharpe | Max DD | Calmar |")
    md.append("|---|---|---|---|---|---|---|---|")
    keys_order = ["V11","V12","V4_DT5G","V23","VNI_BH"]
    for k in keys_order:
        if k not in rows: continue
        s = rows[k]
        md.append(f"| **{s['name']}** | {s['final']/1e9:.3f}B | "
                  f"{s['ret_total']*100:+.2f}% | {s['cagr']*100:+.2f}% | "
                  f"{s['vol_ann']*100:.2f}% | {s['sharpe']:+.2f} | "
                  f"{s['max_dd']*100:+.2f}% | {s['calmar']:+.2f} |")
    md.append("")

    # Delta vs V23 (production baseline; ensemble V121 books removed 2026-06-16)
    if "V23" in rows:
        ref_ret = rows["V23"]["ret_total"]
        ref_dd  = rows["V23"]["max_dd"]
        md.append("## Delta vs V23 (production baseline)\n")
        md.append("| System | ΔRet | ΔDD | Verdict |")
        md.append("|---|---|---|---|")
        for k in ["V11","V12","V4_DT5G","VNI_BH"]:
            if k not in rows: continue
            s = rows[k]
            dret = (s["ret_total"] - ref_ret) * 100
            ddd  = (s["max_dd"] - ref_dd) * 100
            verdict = ("Both better" if dret > 0 and ddd > 0
                       else "Return better, DD worse" if dret > 0
                       else "DD better, return worse" if ddd > 0
                       else "Both worse")
            md.append(f"| {s['name']} | {dret:+.2f}pp | {ddd:+.2f}pp | {verdict} |")
        md.append("")

    # NOTE (2026-05-29): DT4G+MACRO adopted as the production base for V11/V12.
    # The former DT4-vs-TQ and macro-vs-DT4 paper-trade A/B arms were retired
    # (decision made on integrated-backtest evidence; macro is event-driven so a
    # benign-window A/B can't validate it). Ensemble (V121) was REMOVED from the daily
    # comparison 2026-06-16 — faithful audit showed its edge was a reduced-harness artifact.

    # ------------------------------------------------------------------
    # GRIND LENS — current drawdown / underwater / recent momentum.
    # Surfaces "is a system grinding right now" separately from full-period
    # metrics (a system can have great CAGR yet be deep in a style-divergence
    # grind — the V2.2 momentum book Aug-2025 -> now is the canonical case).
    # ------------------------------------------------------------------
    md.append("## Grind lens — current drawdown & recent momentum\n")
    md.append("| System | Cur DD (from peak) | Underwater | Peak date | Trailing 1M | Trailing 3M |")
    md.append("|---|---|---|---|---|---|")
    for k in keys_order:
        if k not in rows: continue
        s = rows[k]
        r1 = f"{s['ret_1m']*100:+.1f}%" if pd.notna(s.get('ret_1m', float('nan'))) else "—"
        r3 = f"{s['ret_3m']*100:+.1f}%" if pd.notna(s.get('ret_3m', float('nan'))) else "—"
        uw = f"{s['underwater_days']}d" if s['underwater_days'] > 0 else "at high"
        md.append(f"| {s['name']} | {s['cur_dd']*100:+.1f}% | {uw} | {s['peak_date']} | {r1} | {r3} |")
    md.append("\n*Grind = sustained underwater stretch where the book bleeds while the index "
              "holds/rises (style-divergence). V2.3's known weak spot is the 2025-08→ style-divergence "
              "grind (momentum lags the VIC-led megacap index); watch V2.3 trailing-3M vs VNINDEX.*\n")

    # NAV curve snapshot every ~10 days
    md.append("## Weekly NAV snapshot (every ~5 trading days)\n")
    all_dates = sorted(set().union(*[set(nav.index) for nav in nav_all.values()]))
    snap_dates = all_dates[::5] + [all_dates[-1]]
    snap_dates = sorted(set(snap_dates))
    cols = ["Date"] + [rows[k]["name"] for k in keys_order if k in rows]
    md.append("| " + " | ".join(cols) + " |")
    md.append("|" + "|".join(["---"]*len(cols)) + "|")
    for d in snap_dates:
        row = [d.strftime("%Y-%m-%d")]
        for k in keys_order:
            if k not in nav_all: continue
            v = nav_all[k].asof(d)
            row.append(f"{v/1e9:.2f}B" if pd.notna(v) else "—")
        md.append("| " + " | ".join(row) + " |")
    md.append("")

    md.append("## Files\n")
    for key, name, path in SYSTEMS:
        md.append(f"- `{path}` — {name}")
    md.append(f"- `data/papertrade_compare5.csv` — daily NAV all systems\n")

    out_md = os.path.join(WORKDIR, "data", "papertrade_compare5.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"Wrote {out_md}")

    # ------------------------------------------------------------------
    # CSV with daily NAV all systems
    # ------------------------------------------------------------------
    all_d = pd.DataFrame(index=pd.DatetimeIndex(all_dates))
    for k, nav in nav_all.items():
        all_d[k] = nav.reindex(all_d.index).ffill()
    all_d.index.name = "ymd"
    out_csv = os.path.join(WORKDIR, "data", "papertrade_compare5.csv")
    all_d.to_csv(out_csv)
    print(f"Wrote {out_csv}")

    # Console summary
    print("\n" + "="*80)
    print(" PAPER-TRADE COMPARISON")
    print("="*80)
    for k in keys_order:
        if k not in rows: continue
        s = rows[k]
        print(f" {s['name']:<40} ret {s['ret_total']*100:+6.2f}%  CAGR {s['cagr']*100:+6.2f}%  "
              f"DD {s['max_dd']*100:+6.2f}%  Sharpe {s['sharpe']:+.2f}  Calmar {s['calmar']:+.2f}")
    print("="*80)


if __name__ == "__main__":
    main()
