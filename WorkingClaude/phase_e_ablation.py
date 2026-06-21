# -*- coding: utf-8 -*-
"""Phase E — Ablation 4 components from V5 production baseline (B=18.34%).

Variants:
  E1 — Remove max_pos=12, set max_pos=10 (eliminates 20% borrow over-leverage)
  E2 — Remove HYBRID entry (= revert to T+1 Open)
  E3 — Remove SV_TIGHT filter (= accept all signals regardless of Release_Date)
  E4 — Remove D1 RE_BACKLOG_BUY override

Each measures ONE change vs B. No estimates — pure measured CAGR/Sharpe/MaxDD/Calmar.

Then synthesizes ALL measured variants across Phase B/C/D/E to identify BEST version.
"""
import os, sys, io
import pandas as pd
import numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)

import pt_dates
pt_dates.START_DATE = "2014-01-02"

INNER = os.path.join(WORKDIR, "pt_v121_ens_q2.py")
with open(INNER, "r", encoding="utf-8") as f:
    base_code = f.read()


def patch_and_run(out_prefix, replacements, label):
    code = base_code
    code = code.replace('sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")',
                        '# stdout wrap stripped')
    code = code.replace("pt_v121_ens_q2_logs.csv",          f"{out_prefix}_logs.csv")
    code = code.replace("pt_v121_ens_q2_transactions.csv",  f"{out_prefix}_transactions.csv")
    code = code.replace("pt_v121_ens_q2_open_positions.csv",f"{out_prefix}_open_positions.csv")
    code = code.replace("pt_v121_ens_q2_report.md",         f"{out_prefix}_report.md")
    code = code.replace('name="pt_v121_ens_q2_BAL"',  f'name="{out_prefix}_BAL"')
    code = code.replace('name="pt_v121_ens_q2_VN30"', f'name="{out_prefix}_VN30"')
    for old, new in replacements:
        n = code.count(old)
        assert n >= 1, f"Pattern not found: {old[:80]}..."
        code = code.replace(old, new)
    print("\n" + "#"*100)
    print(f"#  RUN: {out_prefix}   ({label})")
    print("#"*100)
    ns = {"__name__":"__main__","__file__":INNER}
    exec(compile(code, INNER, "exec"), ns)


# E1: max_pos 12 → 10 (tier_weights stay 10%/slot → 100% NAV instead of 120%)
patch_and_run("phase_e_E1_max10",
    [("MAX_POS_V11 = 12", "MAX_POS_V11 = 10")],
    "max_pos 12→10")

# E2: Remove HYBRID — revert to T+1 Open by NOT passing entry_alt_prices / entry_fill_mode
# The cleanest is to comment out the alt_hybrid args and replace with no-op
patch_and_run("phase_e_E2_noHYBRID",
    [("entry_alt_prices=alt_hybrid, entry_fill_mode=\"v4_hybrid\",",
      "# entry_alt_prices=alt_hybrid, entry_fill_mode=\"v4_hybrid\",  # E2 ablation: removed HYBRID")],
    "no HYBRID entry (T+1 Open only)")

# E3: Remove SV_TIGHT — keep all signals regardless of Release_Date freshness
patch_and_run("phase_e_E3_noSVTIGHT",
    [("mk = (~mb) | sig.apply(sv_tight_keep, axis=1)",
      "mk = pd.Series(True, index=sig.index)  # E3 ablation: no SV_TIGHT filter")],
    "no SV_TIGHT filter")

# E4: Remove D1 RE_BACKLOG_BUY override
# Skip the d1 reclassification (the omask line)
patch_and_run("phase_e_E4_noD1",
    [("omask = sig[\"_d1_ok\"].fillna(False) & (sig[\"ta\"]>=120)\nsig.loc[omask,\"play_type\"] = \"RE_BACKLOG_BUY\"",
      "omask = pd.Series(False, index=sig.index)  # E4 ablation: no D1 RE_BACKLOG override")],
    "no D1 RE_BACKLOG")

# ============================================================================
# Synthesize ALL measured variants → identify BEST
# ============================================================================
print("\n" + "="*100)
print("  PHASE E — All measured variants synthesis")
print("="*100)

def load_logs(prefix):
    p = os.path.join(WORKDIR,"data",f"{prefix}_logs.csv")
    df = pd.read_csv(p); df["ymd"] = pd.to_datetime(df["ymd"])
    return df.sort_values("ymd").reset_index(drop=True)

def metrics(df, label):
    df = df.copy()
    df["ret"] = df["nav"].pct_change().fillna(0)
    df["peak"] = df["nav"].cummax()
    df["dd"] = df["nav"]/df["peak"] - 1
    years = (df["ymd"].iloc[-1] - df["ymd"].iloc[0]).days / 365.25
    final = df["nav"].iloc[-1]; init = df["nav"].iloc[0]
    cagr = (final/init)**(1/max(years,1e-9)) - 1
    sharpe = df["ret"].mean()/df["ret"].std() * np.sqrt(252) if df["ret"].std()>0 else 0
    maxdd = df["dd"].min()
    calmar = cagr/abs(maxdd) if maxdd<0 else np.nan
    return {"label":label, "years":years, "CAGR%":cagr*100, "Sharpe":sharpe,
            "MaxDD%":maxdd*100, "Calmar":calmar, "Final B":final/1e9}

IS_END = pd.Timestamp("2022-01-01")

variants = [
    ("phase_b_baseline",     "B   baseline V5 prod (12pos, Q2, HYBRID, SV_TIGHT, D1)"),
    ("phase_c_D",            "C-D diversify (max_pos20, 5%/slot)"),
    ("phase_c_S",            "C-S soft-stop -15% trim50%"),
    ("phase_c_DS",           "C-DS D+S combined"),
    ("phase_d_v5_no_q2",     "D   V5 no Q2 ({3:0.7})"),
    ("phase_e_E1_max10",     "E1  max_pos 12→10 (no over-leverage)"),
    ("phase_e_E2_noHYBRID",  "E2  no HYBRID entry"),
    ("phase_e_E3_noSVTIGHT", "E3  no SV_TIGHT filter"),
    ("phase_e_E4_noD1",      "E4  no D1 RE_BACKLOG"),
]

rows = []
for prefix, label in variants:
    try:
        df = load_logs(prefix)
        m_full = metrics(df, label)
        m_is   = metrics(df[df["ymd"]<IS_END], label + " IS")
        m_oos  = metrics(df[df["ymd"]>=IS_END], label + " OOS")
        rows.append({"variant": label, "period":"FULL",
                     "CAGR%":m_full["CAGR%"], "Sharpe":m_full["Sharpe"],
                     "MaxDD%":m_full["MaxDD%"], "Calmar":m_full["Calmar"],
                     "Final B":m_full["Final B"]})
        rows.append({"variant": label, "period":"IS 14-21",
                     "CAGR%":m_is["CAGR%"], "Sharpe":m_is["Sharpe"],
                     "MaxDD%":m_is["MaxDD%"], "Calmar":m_is["Calmar"],
                     "Final B":m_is["Final B"]})
        rows.append({"variant": label, "period":"OOS 22-26",
                     "CAGR%":m_oos["CAGR%"], "Sharpe":m_oos["Sharpe"],
                     "MaxDD%":m_oos["MaxDD%"], "Calmar":m_oos["Calmar"],
                     "Final B":m_oos["Final B"]})
    except Exception as e:
        print(f"  WARN: {prefix} load failed: {e}")

mdf = pd.DataFrame(rows)
print("\n=== ALL measured variants ===")
print(mdf.to_string(index=False, float_format=lambda x: f"{x:.3f}" if isinstance(x,float) else x))

# Identify BEST by 3 criteria
print("\n=== BEST OOS (2022-26) BY 3 METRICS ===")
oos_only = mdf[mdf["period"]=="OOS 22-26"].copy()
oos_only = oos_only.sort_values("Calmar", ascending=False)
print("\nRanked by OOS Calmar (risk-adjusted):")
print(oos_only.to_string(index=False, float_format=lambda x: f"{x:.3f}" if isinstance(x,float) else x))

best_calmar = oos_only.iloc[0]
best_cagr = oos_only.sort_values("CAGR%", ascending=False).iloc[0]
best_sharpe = oos_only.sort_values("Sharpe", ascending=False).iloc[0]
best_dd = oos_only.sort_values("MaxDD%", ascending=False).iloc[0]

print(f"\n{'='*100}")
print(f"  WINNERS BY OOS METRIC (2022-2026, hard data)")
print(f"{'='*100}")
print(f"  Max OOS Calmar:  {best_calmar['variant']}  → Calmar {best_calmar['Calmar']:.3f}, CAGR {best_calmar['CAGR%']:+.2f}%, DD {best_calmar['MaxDD%']:+.2f}%")
print(f"  Max OOS CAGR:    {best_cagr['variant']}    → CAGR {best_cagr['CAGR%']:+.2f}%, Calmar {best_cagr['Calmar']:.3f}, DD {best_cagr['MaxDD%']:+.2f}%")
print(f"  Max OOS Sharpe:  {best_sharpe['variant']}  → Sharpe {best_sharpe['Sharpe']:.3f}, CAGR {best_sharpe['CAGR%']:+.2f}%, DD {best_sharpe['MaxDD%']:+.2f}%")
print(f"  Best OOS MaxDD:  {best_dd['variant']}     → DD {best_dd['MaxDD%']:+.2f}%, CAGR {best_dd['CAGR%']:+.2f}%, Calmar {best_dd['Calmar']:.3f}")

# Save full table
mdf.to_csv(os.path.join(WORKDIR,"data","phase_e_all_variants.csv"), index=False)

out = ["# Phase E — Ablation + ALL-Variants Synthesis\n"]
out.append("## All measured variants (FULL / IS / OOS)\n")
out.append("| Variant | Period | CAGR% | Sharpe | MaxDD% | Calmar | Final B |")
out.append("|---|---|---|---|---|---|---|")
for _,r in mdf.iterrows():
    out.append(f"| {r['variant']} | {r['period']} | {r['CAGR%']:+.2f} | {r['Sharpe']:.2f} | {r['MaxDD%']:+.2f} | {r['Calmar']:.2f} | {r['Final B']:.1f} |")

out.append("\n## OOS 2022-2026 leaderboard (ranked by Calmar)\n")
out.append("| Rank | Variant | CAGR% | Sharpe | MaxDD% | Calmar |")
out.append("|---|---|---|---|---|---|")
for i, (_,r) in enumerate(oos_only.iterrows(), 1):
    out.append(f"| {i} | {r['variant']} | {r['CAGR%']:+.2f} | {r['Sharpe']:.2f} | {r['MaxDD%']:+.2f} | {r['Calmar']:.2f} |")

out.append(f"\n## Hard winners (no estimates)\n")
out.append(f"- **Max OOS Calmar**: {best_calmar['variant']}")
out.append(f"  - Calmar {best_calmar['Calmar']:.3f} | CAGR {best_calmar['CAGR%']:+.2f}% | DD {best_calmar['MaxDD%']:+.2f}% | Sharpe {best_calmar['Sharpe']:.2f}")
out.append(f"- **Max OOS CAGR**: {best_cagr['variant']}")
out.append(f"  - CAGR {best_cagr['CAGR%']:+.2f}% | Calmar {best_cagr['Calmar']:.3f} | DD {best_cagr['MaxDD%']:+.2f}% | Sharpe {best_cagr['Sharpe']:.2f}")
out.append(f"- **Best OOS MaxDD**: {best_dd['variant']}")
out.append(f"  - DD {best_dd['MaxDD%']:+.2f}% | CAGR {best_dd['CAGR%']:+.2f}% | Calmar {best_dd['Calmar']:.3f}")

with open(os.path.join(WORKDIR,"data","phase_e_summary.md"),"w",encoding="utf-8") as f:
    f.write("\n".join(out))
print("\n  data/phase_e_summary.md")
print("  data/phase_e_all_variants.csv")
