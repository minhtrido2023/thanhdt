#!/usr/bin/env python3
"""
Hog-price -> GPM lead/lag test (DBC, BAF).  job Taylor_20260706_014930

Question: does the weekly hog-price ("giá heo hơi", near-real-time) LEAD the
quarterly reported gross margin (GPM_P0) of the hog names -- i.e. can a hog-price
TURN warn of a GPM-turn EARLIER than waiting for the financial statement?

Strictly point-in-time: to predict the GPM that will be RELEASED at Release_Date,
only hog prices dated < Release_Date are usable. Since hog price during quarter Q
is fully known by Q-end (~30-45d before GPM_Q is filed), the contemporaneous
quarter-average hog price is itself a legitimate ~1-1.5 month early read on GPM_Q.

Data:
  data/hog_price_vn.csv  -- North (Bac) 2019-01-04+, Trung/Nam only 2024+.
      DBC is a North-based producer -> use the Bac series for the full history.
  /tmp/gpm_dbc_baf.csv   -- DBC/BAF quarterly GPM_P0, GPM_P4, Release_Date (from BQ).

No look-ahead, evaluation only, RESEARCH -- touches no production file.
"""
import pandas as pd, numpy as np

def spearmanr(a, b):
    a = pd.Series(np.asarray(a, float)); b = pd.Series(np.asarray(b, float))
    n = len(a)
    r = a.rank().corr(b.rank())
    # two-sided approx p via t-stat (fine for a sanity flag on small n)
    if n > 2 and abs(r) < 1:
        t = r * np.sqrt((n - 2) / (1 - r * r))
        # normal approx to t tail (df small -> rough, only used as a flag)
        from math import erfc, sqrt
        p = erfc(abs(t) / sqrt(2))
    else:
        p = float("nan")
    return r, p

ROOT = "/home/trido/thanhdt/WorkingClaude"

# ---------- 1. hog price -> calendar-quarter mean (North / Bac) ----------
hog = pd.read_csv(f"{ROOT}/data/hog_price_vn.csv")
hog = hog[hog["region"] == "Bắc"].copy()
hog["date"] = pd.to_datetime(hog["date"], errors="coerce")
hog = hog.dropna(subset=["date"]).sort_values("date")
hog["q"] = hog["date"].dt.to_period("Q")
hq = hog.groupby("q")["price_vnd_kg"].mean().rename("hog").to_frame()
hq["hog_qoq"] = hq["hog"].pct_change(1)      # vs prior quarter
hq["hog_yoy"] = hq["hog"].pct_change(4)      # vs year-ago quarter (turn metric)
print("=== North hog quarterly mean (VND/kg) ===")
print(hq.round(0).to_string())

# ---------- 2. GPM series per ticker ----------
gpm = pd.read_csv("/tmp/gpm_dbc_baf.csv")
gpm["q"] = gpm["quarter"].str.replace("Q", "Q").pipe(lambda s: pd.PeriodIndex(s, freq="Q"))
gpm["Release_Date"] = pd.to_datetime(gpm["Release_Date"])

def analyze(tk):
    d = gpm[gpm["ticker"] == tk].sort_values("q").set_index("q")
    d = d[["GPM_P0", "GPM_P4", "Release_Date"]].copy()
    d["gpm_qoq"] = d["GPM_P0"].diff(1)                 # QoQ margin change
    d["gpm_yoy_turn"] = d["GPM_P0"] - d["GPM_P4"]      # YoY margin turn (framework signal)
    # join hog quarterly at lead L (hog at Q-L aligned to GPM at Q)
    m = d.join(hq, how="left")
    for L in (0, 1, 2):
        m[f"hog_yoy_L{L}"] = hq["hog_yoy"].reindex(m.index - L).values
        m[f"hog_qoq_L{L}"] = hq["hog_qoq"].reindex(m.index - L).values
        m[f"hog_lvl_L{L}"] = hq["hog"].reindex(m.index - L).values
    return m

def corr_block(m, tag):
    print(f"\n===== {tag} — Spearman corr (n usable in paren) =====")
    print(f"  {'signal':28s} vs GPM_level    vs GPM_yoy_turn  vs GPM_qoq")
    for L in (0, 1, 2):
        for base in ("hog_yoy", "hog_qoq", "hog_lvl"):
            col = f"{base}_L{L}"
            row = f"  {base}(hog@Q-{L})".ljust(30)
            outs = []
            for tgt in ("GPM_P0", "gpm_yoy_turn", "gpm_qoq"):
                sub = m[[col, tgt]].dropna()
                if len(sub) >= 6:
                    r, p = spearmanr(sub[col], sub[tgt])
                    outs.append(f"{r:+.3f}(n={len(sub):2d},p={p:.2f})")
                else:
                    outs.append(f"  n={len(sub):2d} short ")
            print(row + "  ".join(outs))

for tk in ("DBC", "BAF"):
    m = analyze(tk)
    print(f"\n########## {tk} ##########")
    show = m[["GPM_P0", "gpm_yoy_turn", "gpm_qoq", "hog_lvl_L0", "hog_yoy_L0",
              "Release_Date"]].copy()
    show["Release_Date"] = show["Release_Date"].dt.date
    print(show.round(3).to_string())
    corr_block(m, tk)

# ---------- 3. TURN-vs-TURN agreement (sign match), DBC ----------
print("\n\n===== DBC: does hog TURN sign predict GPM TURN sign? =====")
m = analyze("DBC")
for L in (0, 1):
    sub = m[[f"hog_yoy_L{L}", "gpm_yoy_turn"]].dropna()
    agree = (np.sign(sub[f"hog_yoy_L{L}"]) == np.sign(sub["gpm_yoy_turn"])).mean()
    print(f"  hog_yoy(Q-{L}) sign == gpm_yoy_turn sign : {agree:.0%}  (n={len(sub)})")
    sub2 = m[[f"hog_qoq_L{L}", "gpm_qoq"]].dropna()
    agree2 = (np.sign(sub2[f"hog_qoq_L{L}"]) == np.sign(sub2["gpm_qoq"])).mean()
    print(f"  hog_qoq(Q-{L}) sign == gpm_qoq sign      : {agree2:.0%}  (n={len(sub2)})")

# ---------- 4. cycle-window consistency (DBC) ----------
print("\n===== DBC hog_yoy vs gpm_yoy_turn by cycle window =====")
m = analyze("DBC")
wins = {"2019-20 ASF boom": ("2019Q1", "2020Q4"),
        "2021-22 down":      ("2021Q1", "2022Q4"),
        "2023-24 recovery":  ("2023Q1", "2024Q4"),
        "2025-26 up":        ("2025Q1", "2026Q4")}
for name, (a, b) in wins.items():
    seg = m.loc[pd.Period(a, "Q"):pd.Period(b, "Q")]
    print(f"\n  -- {name} --")
    for q, r in seg.iterrows():
        print(f"   {q}  hog_yoy={r['hog_yoy_L0']:+.2%}  gpm_turn={r['gpm_yoy_turn']:+.3f}"
              f"  GPM={r['GPM_P0']:.3f}")

# ---------- 5. NOW read ----------
print("\n\n===== NOW: what does the latest hog price say for DBC 2026Q2? =====")
print(hq.tail(8).round(0).to_string())
latest_q = hq.index[-1]
print(f"\n latest hog quarter in data: {latest_q}  (may be partial)")
print(f"   hog mean {latest_q}: {hq.loc[latest_q,'hog']:.0f}  yoy={hq.loc[latest_q,'hog_yoy']:+.2%}"
      f"  qoq={hq.loc[latest_q,'hog_qoq']:+.2%}")
prev = hq.index[-2]
print(f"   hog mean {prev}: {hq.loc[prev,'hog']:.0f}  yoy={hq.loc[prev,'hog_yoy']:+.2%}"
      f"  qoq={hq.loc[prev,'hog_qoq']:+.2%}")
