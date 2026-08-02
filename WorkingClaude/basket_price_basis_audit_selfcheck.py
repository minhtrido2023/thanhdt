# -*- coding: utf-8 -*-
"""basket_price_basis_audit_selfcheck.py — two-way self-check for the 2026-08-02 price-basis fix in
the three SQL-based AUDIT/RESEARCH scripts (job Taylor_20260802_154231, Việc 2):

    basket_concentration.py         mcap  = Close x OShares  -> COALESCE(Price,Close) x OShares
    basket_scheme_concentration.py  mcap  = Close x OShares  -> COALESCE(Price,Close) x OShares
    custom30_core_select_audit.py   liq   = Volume_3M_P50 x Close -> x COALESCE(Price,Close)   [SELECTION]
                                    mcap  = Close x OShares       -> COALESCE(Price,Close) x OShares [WEIGHT]

TWO-WAY by design — a fix that only ever changes nothing is indistinguishable from a fix that is
never reached, and a fix that changes everything is indistinguishable from a broken one:
  POSITIVE control — on data where Close != Price the two bases MUST diverge (the expression is
                     live and discriminating).
  NEGATIVE control — on the current 30-name basket, where every member trades through the latest
                     session and Close == Price, the two bases MUST agree to the cent (the fix
                     introduces no spurious change into today's published reports).

The RETURN leg (`cls` in custom30_core_select_audit.py) is deliberately NOT touched by the fix and
is asserted to still be adjusted Close — the whole point is SPLIT BY ROLE, not "replace Close".
v4final_lib.py is covered by v4final_selector_selfcheck.py instead (it has no SQL; its weight base
is an in-memory pivot), so it is out of scope here.
"""
import io, subprocess, sys
import pandas as pd

PROJ = "lithe-record-440915-m9"
fails = []


def check(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        fails.append(name)


def bq(sql):
    r = subprocess.run(["bq", "query", "--use_legacy_sql=false", f"--project_id={PROJ}",
                        "--format=csv", "--max_rows=3000000", sql],
                       capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-800:])
    return pd.read_csv(io.StringIO(r.stdout))


# The live basket (2026-05-05 rebal of tav2_bq.custom30v_8l) — the exact name set the two
# concentration scripts report on.
BASKET = ['ACB', 'BID', 'CTG', 'DBC', 'DCM', 'DGC', 'EVF', 'HAH', 'HDB', 'HHV', 'IDC', 'LPB',
          'MBB', 'MBS', 'MSB', 'PC1', 'PVT', 'SHB', 'SHS', 'TCB', 'TPB', 'VCB', 'VGC', 'VHC',
          'VHM', 'VIB', 'VIX', 'VND', 'VPB', 'VRE']
# Names whose last bar is STALE (stopped trading) — where the adjusted series keeps being restated
# after the last real print, so Close/Price has drifted off 1.0. This is the failure mode the fix
# exists for, not a hypothetical.
STALE = ['TRT', 'VHF', 'DKC', 'BCB', 'VTS', 'DLT', 'CDG', 'DNN', 'HLY', 'STS', 'PTE', 'SSN']


def last_bar(tickers):
    inl = ",".join(f"'{t}'" for t in tickers)
    return bq(f"""
    WITH last AS (SELECT t.ticker, t.time, t.Close, COALESCE(t.Price,t.Close) AS pxw,
             ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY t.time DESC) rn
           FROM tav2_bq.ticker AS t WHERE t.ticker IN ({inl}) AND t.Close IS NOT NULL)
    SELECT ticker, time, Close, pxw FROM last WHERE rn=1""")


print("[1] concentration scripts — mcap cross-sectional weight base")
b = last_bar(BASKET)
b["w_close"] = b.Close / b.Close.sum()
b["w_pxw"] = b.pxw / b.pxw.sum()
gap_basket = (b.w_close - b.w_pxw).abs().max()
check("NEGATIVE: current basket weights identical on both bases",
      gap_basket < 1e-12,
      f"n={len(b)}, max |Δweight| = {gap_basket:.3e} (Close==Price for every member)")

s = last_bar(STALE)
s["ratio"] = s.Close / s.pxw
check("POSITIVE: stale/suspended names diverge between bases",
      (s.ratio.sub(1).abs() > 0.005).sum() >= 8,
      f"{(s.ratio.sub(1).abs() > 0.005).sum()}/{len(s)} names differ >0.5%, "
      f"ratio range {s.ratio.min():.3f}..{s.ratio.max():.3f}")

# A basket is a RELATIVE weight vector: the fix only matters if it reorders names against each
# other. Mixing one stale name into the live basket is the realistic incident (a held member gets
# suspended) — it must visibly move the reported weights.
mix = pd.concat([b[["ticker", "Close", "pxw"]], s[["ticker", "Close", "pxw"]].head(3)])
mix["w_close"] = mix.Close / mix.Close.sum()
mix["w_pxw"] = mix.pxw / mix.pxw.sum()
check("POSITIVE: one suspended member deforms the whole reported weight vector",
      (mix.w_close - mix.w_pxw).abs().max() > 1e-4,
      f"max |Δweight| = {(mix.w_close - mix.w_pxw).abs().max():.4f} over {len(mix)} names")

print("\n[2] custom30_core_select_audit.py — SELECTION leg (quarterly liquidity ranking)")
# Reproduces the script's own liq expression on both bases, over its own universe/window.
liq = bq("""
SELECT t.ticker, DATE_TRUNC(t.time, QUARTER) AS q,
       AVG(t.Volume_3M_P50*t.Close) AS liq_close,
       AVG(t.Volume_3M_P50*COALESCE(t.Price,t.Close)) AS liq_pxw, COUNT(*) nd
FROM tav2_bq.ticker t
WHERE t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)
  AND t.ICB_Code IS NOT NULL AND t.time BETWEEN DATE '2013-06-01' AND DATE '2026-06-16'
GROUP BY t.ticker, q HAVING nd>=20""")
liq = liq.dropna(subset=["liq_close", "liq_pxw"])
liq["q"] = pd.to_datetime(liq["q"])

TOPN, POOL = 30, 60
diff_top30, diff_top60, quarters = 0, 0, 0
for q, g in liq.groupby("q"):
    a = set(g.sort_values("liq_close", ascending=False).ticker.head(TOPN))
    c = set(g.sort_values("liq_pxw", ascending=False).ticker.head(TOPN))
    a6 = set(g.sort_values("liq_close", ascending=False).ticker.head(POOL))
    c6 = set(g.sort_values("liq_pxw", ascending=False).ticker.head(POOL))
    diff_top30 += len(a - c)
    diff_top60 += len(a6 - c6)
    quarters += 1
check("POSITIVE: liquidity basis reorders the selected cross-section",
      diff_top30 > 0,
      f"{diff_top30} top-30 name-slots differ across {quarters} quarters "
      f"({diff_top30/quarters:.2f}/quarter); top-60 pool {diff_top60}")

# In-period constancy: within a quarter with no corporate action the ratio is a CONSTANT, so it
# cancels out of a same-quarter ranking. Where the two bases disagree it must be because the ratio
# actually varies across names in that quarter — not noise.
last_q = liq[liq.q == liq.q.max()].copy()
last_q["ratio"] = last_q.liq_close / last_q.liq_pxw
check("in-period constancy: divergence tracks a real cross-sectional ratio spread",
      last_q.ratio.std() > 0,
      f"latest quarter ratio spread {last_q.ratio.min():.3f}..{last_q.ratio.max():.3f} "
      f"(sd {last_q.ratio.std():.4f}); a flat ratio would cancel out of the ranking")

print("\n[3] RETURN leg must be UNTOUCHED (split by role, not blanket replace)")
src = open("/home/trido/thanhdt/WorkingClaude/custom30_core_select_audit.py", encoding="utf-8").read()
check("custom30_core_select_audit.py keeps adjusted Close for returns",
      "cls = {t:dict(zip(g.time,g.Close.astype(float)))" in src,
      "`cls` still built from g.Close")
check("custom30_core_select_audit.py weight base moved to raw price",
      "mcap = {t:dict(zip(g.time,(g.pxw*g.OShares)" in src,
      "`mcap` built from g.pxw")
for f in ("basket_concentration.py", "basket_scheme_concentration.py"):
    t = open(f"/home/trido/thanhdt/WorkingClaude/{f}", encoding="utf-8").read()
    check(f"{f} mcap uses COALESCE(Price,Close)",
          "p.pxw*s.OShares AS mcap" in t and "p.Close*s.OShares" not in t)

print("\n" + "=" * 70)
print(f"RESULT: {'ALL PASS' if not fails else 'FAILED: ' + ', '.join(fails)}")
sys.exit(1 if fails else 0)
