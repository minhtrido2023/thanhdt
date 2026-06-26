"""#12 deep-discount sleeve — PROXY gate (cheap, no NAV sim) before committing a full pt_v23 harness.
Per registry discipline (line ~226): proxy first, only escalate forms that beat base IS *and* OOS.

Event = QUALITY name (ROIC5Y>0.08 & ROE_Min5Y>0 & FSCORE>=5) at own-history deep discount
pbz=(PB-PB_MA5Y)/PB_SD5Y <= -1.5. Forward = profit_2M (T+40). VERIFIED: profit_2M is ALREADY in
PERCENT (median 0.93%, p5 -21%, p95 +33%) — the prior probe's ``*100`` was a 100x bug; we report it
raw. Both winrate and mean-% are usable. LAG-overlap uses a YoY-growth proxy g=NP_P0/NP_P4-1>=0.15
(NP_R itself is not in the ticker_prune cache; this mirrors LAG's NP_R>=15 earnings-momentum gate).

Three questions, each a go/no-go for #12:
 Q1  Does the NEUTRAL/BULL edge survive an IS(<2020)/OOS(>=2020) split? (fragile if one half only)
 Q2  Is it ADDITIVE to LAG? LAG already owns earnings-surprise names (NP_R>=0.15). Strip those;
     does the LAG-orthogonal remainder still carry the edge?
 Q3  Is it ADDITIVE to the value pick already in custom30V? custom30V ranks by 1/PE (earnings yield).
     Compare deep-discount (own pbz) vs a same-universe cheap-by-PE cut: does pbz add beyond ey?
Reference baseline within the SAME quality universe = all non-discount obs (pbz>0) — the alpha claim
is deep-discount winrate ABOVE this same-quality baseline, not above the whole market.
"""
import os, sys
os.environ.setdefault("BQ_LOCAL_CACHE", "data/bq_cache")
os.chdir("/home/trido/thanhdt/WorkingClaude"); sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from bq_local_cache import get_cache
lc = get_cache()

QUAL = "t.ROIC5Y>0.08 AND t.ROE_Min5Y>0 AND t.FSCORE>=5"
PBZ  = "(t.PB-t.PB_MA5Y)/NULLIF(t.PB_SD5Y,0)"
# DT5G: 1=CRISIS 2=BEAR 3=NEUTRAL 4=BULL 5=EXBULL. Sleeve targets NEUTRAL/BULL (3,4), OFF EXBULL(5).
BASE = f"""FROM tav2_bq.ticker_prune t JOIN tav2_bq.vnindex_5state_dt5g_live s ON t.time=s.time
WHERE t.time>=DATE '2014-01-01' AND t.PB_SD5Y>0 AND t.profit_2M IS NOT NULL AND {QUAL}"""

def tbl(df): return df.to_string(index=False)

# ---------- Q1: IS/OOS x state split of the deep-discount edge ----------
print("=== Q1: deep-discount (pbz<=-1.5) edge by ERA x state — does NEUTRAL/BULL survive IS & OOS? ===")
q1 = lc.query(f"""
SELECT CASE WHEN t.time < DATE '2020-01-01' THEN '1.IS(14-19)' ELSE '2.OOS(20+)' END era,
       s.state, COUNT(*) n,
       ROUND(AVG(CASE WHEN t.profit_2M>0 THEN 1.0 ELSE 0 END)*100,1) winrate,
       ROUND(AVG(t.profit_2M),2) mean_fwd2M
{BASE} AND {PBZ}<=-1.5
GROUP BY era, s.state ORDER BY s.state, era""")
print(tbl(q1))

print("\n--- same-quality NON-discount baseline (pbz>0) by ERA x state (the bar to beat) ---")
q1b = lc.query(f"""
SELECT CASE WHEN t.time < DATE '2020-01-01' THEN '1.IS(14-19)' ELSE '2.OOS(20+)' END era,
       s.state, COUNT(*) n,
       ROUND(AVG(CASE WHEN t.profit_2M>0 THEN 1.0 ELSE 0 END)*100,1) winrate,
       ROUND(AVG(t.profit_2M),2) mean_fwd2M
{BASE} AND {PBZ}>0
GROUP BY era, s.state ORDER BY s.state, era""")
print(tbl(q1b))

# ---------- Q2: additive to LAG? strip NP_R>=0.15 (LAG-eligible) and re-measure ----------
print("\n=== Q2: LAG additivity — split deep-disc NEUTRAL/BULL by LAG-overlap (NP_R>=0.15) ===")
# LAG-overlap proxy: YoY net-profit growth g = NP_P0/NP_P4 - 1 (current vs 4Q-ago), strong if NP_P4>0 & g>=0.15.
GYOY = "CASE WHEN t.NP_P4>0 THEN t.NP_P0/t.NP_P4 - 1 ELSE NULL END"
q2 = lc.query(f"""
SELECT CASE WHEN {GYOY}>=0.15 THEN 'LAG-overlap (gYoY>=.15)' WHEN {GYOY} IS NULL THEN 'gYoY null/neg-base'
            ELSE 'LAG-orthogonal (gYoY<.15)' END grp,
       CASE WHEN t.time < DATE '2020-01-01' THEN 'IS' ELSE 'OOS' END era,
       COUNT(*) n, ROUND(AVG(CASE WHEN t.profit_2M>0 THEN 1.0 ELSE 0 END)*100,1) winrate,
       ROUND(AVG(t.profit_2M),2) mean_fwd2M
{BASE} AND {PBZ}<=-1.5 AND s.state IN (3,4)
GROUP BY grp, era ORDER BY grp, era""")
print(tbl(q2))

# ---------- Q3: additive to value (1/PE)? deep-disc vs cheap-by-PE in same universe/states ----------
print("\n=== Q3: value additivity — within QUALITY+NEUTRAL/BULL, does OWN-pbz add beyond cheap-by-PE? ===")
print("    Compare the 4 cells of {pbz<=-1.5 ?} x {ey high (PE<=median) ?}. If the edge lives in the")
print("    pbz column independent of the ey column, pbz is additive to custom30V's 1/PE rank.")
q3 = lc.query(f"""
WITH u AS (
  SELECT t.profit_2M f, CASE WHEN {PBZ}<=-1.5 THEN 'deep_pbz' ELSE 'not_deep' END pbz_grp,
         t.PE pe
  {BASE} AND s.state IN (3,4) AND t.PE>0),
m AS (SELECT APPROX_QUANTILES(pe,2)[OFFSET(1)] med FROM u)
SELECT u.pbz_grp, CASE WHEN u.pe<=m.med THEN 'cheap_PE' ELSE 'exp_PE' END pe_grp,
       COUNT(*) n, ROUND(AVG(CASE WHEN u.f>0 THEN 1.0 ELSE 0 END)*100,1) winrate,
       ROUND(AVG(u.f),2) mean_fwd2M
FROM u CROSS JOIN m GROUP BY u.pbz_grp, pe_grp ORDER BY u.pbz_grp, pe_grp""")
print(tbl(q3))

print("\nREAD: Q1 PASS if NEUTRAL(3)/BULL(4) deep-disc winrate > non-disc baseline in BOTH eras.")
print("      Q2 PASS if LAG-orthogonal remainder keeps the edge (not just the NP_R>=.15 overlap).")
print("      Q3 PASS if deep_pbz beats not_deep WITHIN each PE bucket (edge not subsumed by cheap-PE).")
print("      Any FAIL => sleeve is fragile/redundant => do NOT burn a full harness; report & park.")
