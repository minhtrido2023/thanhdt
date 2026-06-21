"""
paper_trade_review.py — scheduled 2026-06-30 cleanup of the paper-trade roster
==============================================================================
Decides keep/drop for the time-boxed sleeves (#6 vol-spike hedge, #7 F-sleeve,
#10 DT4-vs-TQ34b A/B) by QUANTITATIVE criteria on their accumulated forward logs,
checks whether V6-v2 "Tứ Trụ" is ready to ABSORB the standalone shadow sleeves,
and writes a recommendation (does NOT touch the live bat — proposes only).

Criteria:
  #6 vol-hedge : KEEP only if V5_hedged beats V5_only on BOTH Sharpe & MaxDD.
  #7 F-sleeve  : KEEP only if standalone Sharpe>0.3 AND corr(F, V5)<0.30 (orthogonal)
                 AND cumulative positive — else FOLD/DROP (memory: largely redundant).
  #10 DT4 A/B  : surface the A/B report verdict; production is already DT5G → RESOLVE.
  merge        : recommend folding capit-shadow (#9) into V6-v2's capit sleeve ONCE
                 V6-v2 forward is validated across >1 regime (not just a NEUTRAL rally).

Run: python paper_trade_review.py
"""
import sys, os
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
DEC_DATE = pd.Timestamp("2026-06-30")
TODAY = pd.read_csv(WORKDIR + r"\data\dt5g_vnindex.csv", parse_dates=["time"])["time"].max()


def daily_stats(nav):
    nav = nav.dropna()
    if len(nav) < 10: return None
    r = nav.pct_change().dropna()
    sh = r.mean()/r.std()*np.sqrt(252) if r.std() > 0 else 0
    dd = (nav/nav.cummax()-1).min()
    return dict(Sharpe=sh, MaxDD=dd*100, totRet=(nav.iloc[-1]/nav.iloc[0]-1)*100, n=len(nav))


def review_volhedge():
    p = WORKDIR + r"\data\vol_spike_hedge_pt_log.csv"
    if not os.path.exists(p): return "#6 vol-hedge: NO DATA → DROP (never accumulated)."
    d = pd.read_csv(p, parse_dates=["time"]).set_index("time")
    so, sh = daily_stats(d["V5_only"]), daily_stats(d["V5_hedged"])
    if not so or not sh: return "#6 vol-hedge: insufficient data."
    keep = (sh["Sharpe"] > so["Sharpe"]) and (sh["MaxDD"] > so["MaxDD"])  # less-negative DD
    return (f"#6 vol-hedge: V5_only Sh{so['Sharpe']:.2f}/DD{so['MaxDD']:.1f} vs "
            f"V5_hedged Sh{sh['Sharpe']:.2f}/DD{sh['MaxDD']:.1f} → "
            f"{'KEEP' if keep else 'DROP (no risk-adj improvement — redundant w/ DT5G)'}")


def review_fsleeve():
    p = WORKDIR + r"\data\f_sleeve_pt_log.csv"
    vp = WORKDIR + r"\data\vol_spike_hedge_pt_log.csv"
    if not os.path.exists(p): return "#7 F-sleeve: NO DATA → DROP."
    d = pd.read_csv(p, parse_dates=["time"]).set_index("time")
    st = daily_stats(d["nav"])
    corr = np.nan
    if os.path.exists(vp):
        v = pd.read_csv(vp, parse_dates=["time"]).set_index("time")["v5_ret"]
        fr = d["sleeve_ret"] if "sleeve_ret" in d else d["nav"].pct_change()
        j = pd.concat([fr.rename("f"), v.rename("v5")], axis=1).dropna()
        if len(j) > 10: corr = j["f"].corr(j["v5"])
    if not st: return "#7 F-sleeve: insufficient data."
    keep = (st["Sharpe"] > 0.3) and (pd.notna(corr) and abs(corr) < 0.30) and (st["totRet"] > 0)
    return (f"#7 F-sleeve: Sharpe {st['Sharpe']:.2f}, totRet {st['totRet']:.1f}%, corr-to-V5 "
            f"{corr:.2f} → {'KEEP (orthogonal+positive)' if keep else 'DROP/FOLD (not orthogonal or not additive)'}")


def review_dt4ab():
    rp = WORKDIR + r"\data\pt_dt4_vs_tq34b_ab_report.md"
    note = "production foundation is already DT5G (= DT4-gate + macro) per CLAUDE.md → A/B can RESOLVE/RETIRE."
    if os.path.exists(rp):
        try:
            with open(rp, encoding="utf-8") as f:
                head = f.read().strip().splitlines()[:6]
            return "#10 DT4-vs-TQ34b A/B: report says →\n      " + "\n      ".join(head) + f"\n      VERDICT: {note}"
        except Exception:
            pass
    return f"#10 DT4-vs-TQ34b A/B: {note}"


def review_v6_merge():
    p = WORKDIR + r"\data\v6_vs_v5_paper.csv"
    if not os.path.exists(p): return "merge: V6-v2 forward not started — keep shadow sleeves standalone."
    d = pd.read_csv(p, parse_dates=["date"]).set_index("date")
    states = set(d["state"].unique()) if "state" in d else set()
    multi = len(states) > 1
    sp = (d["V6_nav"].iloc[-1] - d["V5_nav"].iloc[-1]) * 100
    return (f"merge: V6-v2 forward {len(d)} sessions, states seen {sorted(states)} "
            f"({'MULTI-regime ✓' if multi else 'SINGLE regime ✗ (need a drawdown window)'}), "
            f"V6−V5 spread {sp:+.2f}pp.\n      → {'READY to fold capit-shadow(#9) + dropped sleeves INTO V6-v2 unified budget.' if multi else 'NOT ready — keep capit-shadow standalone (still feeds capit-edge); re-check after a non-NEUTRAL window.'}")


def main():
    stage = "DECISION" if TODAY >= DEC_DATE else "PRELIMINARY (decision date 2026-06-30)"
    L = [f"# Paper-trade roster review — {stage}  (as of {TODAY.date()})", ""]
    L += ["## Time-boxed sleeves (decision 2026-06-30)",
          "- " + review_volhedge(), "- " + review_fsleeve(), "- " + review_dt4ab(), ""]
    L += ["## V6-v2 absorption check", "- " + review_v6_merge(), ""]
    L += ["## Proposed bat cleanup (apply manually after review)",
          "- If #6 DROP → comment papertrade_daily.bat step [5b] vol_spike_hedge_pt.py",
          "- If #7 DROP → comment step [5c] f_sleeve_pt.py",
          "- If #10 RESOLVED → comment step [7] pt_dt4_vs_tq34b_ab.py (decision logged)",
          "- If V6-v2 MULTI-regime+ahead → fold step [9] pt_capitulation_shadow into V6-v2; keep [14] pt_sleeve_allocator as the unified successor",
          "- Always KEEP core books [1-4b], monitors [11-13], ORB [5d] (orthogonal edge)."]
    out = "\n".join(L)
    with open(WORKDIR + r"\data\paper_trade_review.md", "w", encoding="utf-8") as f:
        f.write(out)
    print(out)
    print("\nSaved: data/paper_trade_review.md  (recommendation only — live bat untouched)")


if __name__ == "__main__":
    main()
