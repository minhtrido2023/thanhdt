# -*- coding: utf-8 -*-
"""Phase F — Stacked combo backtest.

F1a = D (diversify max20 + 5%/slot) + S (soft-15% trim50% + hard-25%) + E4 (no D1)
F1b = E1 (concentrate max10) + S (soft-15% trim50% + hard-25%) + E4 (no D1)

Both fix the over-leverage issue (12*10%=120% NAV) but in opposite directions:
  F1a → 20 pos × 5%/slot = 100% NAV, more diversified
  F1b → 10 pos × 10%/slot = 100% NAV, more concentrated

Compare with all prior phase results to pick FINAL winner.
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


# F1a: D (diversify) + S (soft stop) + E4 (no D1)
REPL_F1A = [
    ("MAX_POS_V11 = 12", "MAX_POS_V11 = 20"),
    ("TIER_WEIGHTS_V11 = {t: 0.10 for t in TIER_BAL}",
     "TIER_WEIGHTS_V11 = {t: 0.05 for t in TIER_BAL}"),
    ("hold_days=45, stop_loss=-0.20,",
     "hold_days=45, stop_loss=-0.25, soft_stop_partial=(-0.15, 0.5),"),
    ("omask = sig[\"_d1_ok\"].fillna(False) & (sig[\"ta\"]>=120)\nsig.loc[omask,\"play_type\"] = \"RE_BACKLOG_BUY\"",
     "omask = pd.Series(False, index=sig.index)  # F: no D1 RE_BACKLOG"),
]
patch_and_run("phase_f_F1a_DS_E4", REPL_F1A, "D + S + E4 (max20,5%,soft,noD1)")

# F1b: E1 (concentrate max=10) + S (soft stop) + E4 (no D1)
REPL_F1B = [
    ("MAX_POS_V11 = 12", "MAX_POS_V11 = 10"),
    ("hold_days=45, stop_loss=-0.20,",
     "hold_days=45, stop_loss=-0.25, soft_stop_partial=(-0.15, 0.5),"),
    ("omask = sig[\"_d1_ok\"].fillna(False) & (sig[\"ta\"]>=120)\nsig.loc[omask,\"play_type\"] = \"RE_BACKLOG_BUY\"",
     "omask = pd.Series(False, index=sig.index)  # F: no D1 RE_BACKLOG"),
]
patch_and_run("phase_f_F1b_E1S_E4", REPL_F1B, "E1 + S + E4 (max10,10%,soft,noD1)")

# ============================================================================
# Final synthesis: rank ALL measured variants by OOS Calmar
# ============================================================================
print("\n" + "="*100)
print("  PHASE F — FINAL synthesis (all phases, all measured)")
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
    ("phase_b_baseline",     "B   baseline V5 prod"),
    ("phase_c_D",            "C-D diversify (max20,5%)"),
    ("phase_c_S",            "C-S soft-stop -15%"),
    ("phase_c_DS",           "C-DS D+S"),
    ("phase_d_v5_no_q2",     "D   no Q2"),
    ("phase_e_E1_max10",     "E1  max_pos=10"),
    ("phase_e_E2_noHYBRID",  "E2  no HYBRID"),
    ("phase_e_E3_noSVTIGHT", "E3  no SV_TIGHT"),
    ("phase_e_E4_noD1",      "E4  no D1"),
    ("phase_f_F1a_DS_E4",    "F1a D+S+E4 (max20,5%,soft,noD1)"),
    ("phase_f_F1b_E1S_E4",   "F1b E1+S+E4 (max10,10%,soft,noD1)"),
]

rows = []
for prefix, label in variants:
    try:
        df = load_logs(prefix)
        for period_label, period_df in [
            ("FULL", df),
            ("IS 14-21", df[df["ymd"]<IS_END]),
            ("OOS 22-26", df[df["ymd"]>=IS_END]),
        ]:
            m = metrics(period_df, label)
            rows.append({"variant": label, "period":period_label,
                         "CAGR%":m["CAGR%"], "Sharpe":m["Sharpe"],
                         "MaxDD%":m["MaxDD%"], "Calmar":m["Calmar"],
                         "Final B":m["Final B"]})
    except Exception as e:
        print(f"  WARN: {prefix} load failed: {e}")

mdf = pd.DataFrame(rows)

# OOS leaderboard
print("\n=== OOS 2022-2026 leaderboard (ranked by Calmar) ===")
oos = mdf[mdf["period"]=="OOS 22-26"].copy().sort_values("Calmar", ascending=False)
print(oos.to_string(index=False, float_format=lambda x: f"{x:.3f}" if isinstance(x,float) else x))

# FULL leaderboard
print("\n=== FULL period leaderboard (ranked by CAGR) ===")
full = mdf[mdf["period"]=="FULL"].copy().sort_values("CAGR%", ascending=False)
print(full.to_string(index=False, float_format=lambda x: f"{x:.3f}" if isinstance(x,float) else x))

# IS-OOS coherence (smallest gap)
is_df = mdf[mdf["period"]=="IS 14-21"].copy()[["variant","CAGR%"]].rename(columns={"CAGR%":"IS_CAGR%"})
oos_df = mdf[mdf["period"]=="OOS 22-26"].copy()[["variant","CAGR%","Calmar","MaxDD%"]].rename(columns={"CAGR%":"OOS_CAGR%","Calmar":"OOS_Calmar","MaxDD%":"OOS_DD%"})
gap_df = is_df.merge(oos_df, on="variant")
gap_df["IS_OOS_gap"] = gap_df["IS_CAGR%"] - gap_df["OOS_CAGR%"]
gap_df = gap_df.sort_values("IS_OOS_gap")
print("\n=== IS-OOS coherence (smaller gap = more robust) ===")
print(gap_df.to_string(index=False, float_format=lambda x: f"{x:.3f}" if isinstance(x,float) else x))

# Pick FINAL winner
top_calmar = oos.iloc[0]
top_cagr   = oos.sort_values("CAGR%", ascending=False).iloc[0]
top_dd     = oos.sort_values("MaxDD%", ascending=False).iloc[0]
top_full   = full.iloc[0]
print(f"\n{'='*100}")
print(f"  ABSOLUTE WINNERS (hard measured, no estimates)")
print(f"{'='*100}")
print(f"  Best OOS Calmar:  {top_calmar['variant']:50s}  Calmar={top_calmar['Calmar']:.3f}  CAGR={top_calmar['CAGR%']:+.2f}%  DD={top_calmar['MaxDD%']:+.2f}%")
print(f"  Best OOS CAGR:    {top_cagr['variant']:50s}  CAGR={top_cagr['CAGR%']:+.2f}%  Calmar={top_cagr['Calmar']:.3f}  DD={top_cagr['MaxDD%']:+.2f}%")
print(f"  Best OOS MaxDD:   {top_dd['variant']:50s}  DD={top_dd['MaxDD%']:+.2f}%  CAGR={top_dd['CAGR%']:+.2f}%  Calmar={top_dd['Calmar']:.3f}")
print(f"  Best FULL CAGR:   {top_full['variant']:50s}  CAGR={top_full['CAGR%']:+.2f}%  Calmar={top_full['Calmar']:.3f}  Final={top_full['Final B']:.0f}B")

# Save
mdf.to_csv(os.path.join(WORKDIR,"data","phase_f_all_variants.csv"), index=False)
out = ["# Phase F — FINAL synthesis (all measured)\n"]
out.append("\n## All variants (FULL / IS / OOS)\n")
out.append("| Variant | Period | CAGR% | Sharpe | MaxDD% | Calmar | Final B |")
out.append("|---|---|---|---|---|---|---|")
for _,r in mdf.iterrows():
    out.append(f"| {r['variant']} | {r['period']} | {r['CAGR%']:+.2f} | {r['Sharpe']:.2f} | {r['MaxDD%']:+.2f} | {r['Calmar']:.2f} | {r['Final B']:.1f} |")

out.append("\n## OOS 2022-2026 leaderboard (ranked by Calmar)\n")
out.append("| Rank | Variant | CAGR% | Sharpe | MaxDD% | Calmar |")
out.append("|---|---|---|---|---|---|")
for i,(_,r) in enumerate(oos.iterrows(),1):
    out.append(f"| {i} | {r['variant']} | {r['CAGR%']:+.2f} | {r['Sharpe']:.2f} | {r['MaxDD%']:+.2f} | {r['Calmar']:.2f} |")

out.append("\n## FULL period leaderboard (ranked by CAGR)\n")
out.append("| Rank | Variant | CAGR% | Sharpe | MaxDD% | Calmar | Final B |")
out.append("|---|---|---|---|---|---|---|")
for i,(_,r) in enumerate(full.iterrows(),1):
    out.append(f"| {i} | {r['variant']} | {r['CAGR%']:+.2f} | {r['Sharpe']:.2f} | {r['MaxDD%']:+.2f} | {r['Calmar']:.2f} | {r['Final B']:.1f} |")

out.append("\n## IS-OOS coherence (smaller gap = more robust)\n")
out.append("| Variant | IS CAGR% | OOS CAGR% | Gap | OOS Calmar | OOS DD% |")
out.append("|---|---|---|---|---|---|")
for _,r in gap_df.iterrows():
    out.append(f"| {r['variant']} | {r['IS_CAGR%']:+.2f} | {r['OOS_CAGR%']:+.2f} | {r['IS_OOS_gap']:+.2f} | {r['OOS_Calmar']:.2f} | {r['OOS_DD%']:+.2f} |")

out.append(f"\n## ABSOLUTE WINNERS\n")
out.append(f"- **Best OOS Calmar**: {top_calmar['variant']} → Calmar {top_calmar['Calmar']:.3f}, CAGR {top_calmar['CAGR%']:+.2f}%, DD {top_calmar['MaxDD%']:+.2f}%")
out.append(f"- **Best OOS CAGR**: {top_cagr['variant']} → CAGR {top_cagr['CAGR%']:+.2f}%, Calmar {top_cagr['Calmar']:.3f}")
out.append(f"- **Best OOS MaxDD**: {top_dd['variant']} → DD {top_dd['MaxDD%']:+.2f}%, CAGR {top_dd['CAGR%']:+.2f}%")
out.append(f"- **Best FULL CAGR**: {top_full['variant']} → CAGR {top_full['CAGR%']:+.2f}%, Final {top_full['Final B']:.0f}B")

with open(os.path.join(WORKDIR,"data","phase_f_summary.md"),"w",encoding="utf-8") as f:
    f.write("\n".join(out))
print("\n  data/phase_f_summary.md")
print("  data/phase_f_all_variants.csv")
