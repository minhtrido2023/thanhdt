#!/usr/bin/env python3
"""Build Sprint 3 stock-distribution ex-date and AIS panels (BigQuery read-only)."""
from __future__ import annotations

import csv
import gzip
import json
import os
import shutil
import subprocess
from collections import defaultdict
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out3")
SQLDIR = os.path.join(OUT, "sql")
PROJECT = "lithe-record-440915-m9"
EX_MIN, EX_MAX = "2014-01-01", "2026-06-30"
PANEL_START = "2013-01-01"


def bq_csv(sql: str, name: str, timeout: int = 1800) -> list[dict]:
    os.makedirs(SQLDIR, exist_ok=True)
    path = os.path.join(SQLDIR, name + ".sql")
    with open(path, "w") as fh:
        fh.write(sql)
    bq = shutil.which("bq") or "/home/trido/google-cloud-sdk/bin/bq"
    cmd = [bq, "query", "--use_legacy_sql=false", "--format=csv",
           f"--project_id={PROJECT}", "--max_rows=2000000", "--quiet"]
    env = os.environ.copy()
    env["PATH"] = "/home/trido/google-cloud-sdk/bin:" + env.get("PATH", "")
    env.setdefault("CLOUDSDK_CONFIG", "/home/trido/thanhdt/gcloud_dtienthanh")
    with open(path) as fh:
        p = subprocess.run(cmd, stdin=fh, text=True, capture_output=True, timeout=timeout,
                           env=env)
    if p.returncode:
        raise RuntimeError(f"bq failed ({name})\nSTDOUT:\n{p.stdout[-4000:]}\nSTDERR:\n{p.stderr[-4000:]}")
    lines = [x for x in p.stdout.splitlines() if x.strip()]
    return list(csv.DictReader(lines)) if lines else []


def num(v):
    try:
        return float(v) if v not in (None, "", "NULL") else None
    except (TypeError, ValueError):
        return None


def day(v):
    return date.fromisoformat(v[:10]) if v else None


def dump(name: str, rows: list[dict]):
    if not rows:
        return
    with open(os.path.join(OUT, name), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)


# The event SQL mirrors the ledger's survivor preference, then combines same-day stock
# distributions. `Price` is deliberately not selected at k=0.
EVENT_CTE = f"""
WITH raw AS (
  SELECT c.*,
    CASE c.issue_method_code WHEN 'DIV' THEN 'STOCK_DIVIDEND'
                             WHEN 'Bonus' THEN 'BONUS' END AS subtype,
    ROW_NUMBER() OVER (
      PARTITION BY c.ticker, c.exright_date, c.issue_method_code,
                   CAST(c.exercise_ratio AS STRING), CAST(c.issue_volumn AS STRING)
      ORDER BY c.public_date DESC, c.id DESC) AS rn
  FROM `{PROJECT}.tav2_bq.corporate_action` c
  WHERE c.event_code='ISS' AND c.event_status='executed'
    AND c.issue_method_code IN ('DIV','Bonus')
    AND c.exright_date BETWEEN DATE '{EX_MIN}' AND DATE '{EX_MAX}'
    AND c.exercise_ratio > 0
), ev AS (
  SELECT ticker, exright_date AS ex_date,
    SUM(exercise_ratio) AS ratio_total,
    SUM(IFNULL(issue_volumn,0)) AS issue_volume,
    MAX(listing_date) AS listing_date,
    COUNT(DISTINCT subtype) AS n_subtypes,
    STRING_AGG(DISTINCT subtype ORDER BY subtype) AS subtype_list,
    COUNT(*) AS n_components
  FROM raw WHERE rn=1 GROUP BY ticker, ex_date
)
"""

EX_PANEL = EVENT_CTE + f"""
, px AS (
  SELECT t.ticker,t.time,t.Close,t.Price,t.Volume,t.ICB_Code,
    SAFE_DIVIDE(t.Close,LAG(t.Close) OVER(PARTITION BY t.ticker ORDER BY t.time))-1 ret,
    ROW_NUMBER() OVER(PARTITION BY t.ticker ORDER BY t.time) si
  FROM `{PROJECT}.tav2_bq.ticker` t
  WHERE t.time>=DATE '{PANEL_START}' AND t.Close>0
    AND t.ticker IN (SELECT DISTINCT ticker FROM ev)
), anchor AS (
  SELECT e.*,p.si si0 FROM ev e JOIN px p
    ON p.ticker=e.ticker AND p.time=e.ex_date
), w AS (
  SELECT a.*,p.si-a.si0 k,p.time dt,p.Close,p.Price,p.Volume,p.ICB_Code,p.ret
  FROM anchor a JOIN px p ON p.ticker=a.ticker AND p.si BETWEEN a.si0-260 AND a.si0+62
)
SELECT ticker,ex_date,ANY_VALUE(ratio_total) ratio_total,
  ANY_VALUE(issue_volume) issue_volume,ANY_VALUE(listing_date) listing_date,
  ANY_VALUE(n_subtypes) n_subtypes,ANY_VALUE(subtype_list) subtype_list,
  ANY_VALUE(n_components) n_components,
  MAX(IF(k=-250,Close,NULL)) c_m250, MAX(IF(k=-250,dt,NULL)) d_m250,
  MAX(IF(k=-230,Close,NULL)) c_m230, MAX(IF(k=-230,dt,NULL)) d_m230,
  MAX(IF(k=-40,Close,NULL)) c_m40, MAX(IF(k=-40,dt,NULL)) d_m40,
  MAX(IF(k=-21,Close,NULL)) c_m21, MAX(IF(k=-21,dt,NULL)) d_m21,
  MAX(IF(k=-20,Close,NULL)) c_m20, MAX(IF(k=-20,dt,NULL)) d_m20,
  MAX(IF(k=-1,Close,NULL)) c_m1,MAX(IF(k=-1,Price,NULL)) p_m1,
  MAX(IF(k=-1,dt,NULL)) d_m1,MAX(IF(k=-1,ICB_Code,NULL)) icb,
  MAX(IF(k=0,Close,NULL)) c_0,MAX(IF(k=0,dt,NULL)) d_0,
  MAX(IF(k=0,Volume,NULL)) v_0,
  MAX(IF(k=1,Close,NULL)) c_1,MAX(IF(k=1,Price,NULL)) p_1,
  MAX(IF(k=2,Close,NULL)) c_2,MAX(IF(k=2,Price,NULL)) p_2,
  MAX(IF(k=3,Close,NULL)) c_3,MAX(IF(k=3,Price,NULL)) p_3,
  MAX(IF(k=5,Close,NULL)) c_5,MAX(IF(k=5,dt,NULL)) d_5,
  MAX(IF(k=10,Close,NULL)) c_10,MAX(IF(k=10,dt,NULL)) d_10,
  MAX(IF(k=20,Close,NULL)) c_20,MAX(IF(k=20,dt,NULL)) d_20,
  MAX(IF(k=60,Close,NULL)) c_60,MAX(IF(k=60,dt,NULL)) d_60,
  AVG(IF(k BETWEEN -60 AND -6,Volume,NULL)) avol_pre,
  AVG(IF(k BETWEEN 1 AND 5,Volume,NULL)) avol_0_5,
  APPROX_QUANTILES(IF(k BETWEEN -60 AND -6,Price*Volume,NULL),2)[OFFSET(1)] adtv_pre,
  APPROX_QUANTILES(IF(k BETWEEN 6 AND 60,Price*Volume,NULL),2)[OFFSET(1)] adtv_post,
  COUNTIF(k BETWEEN -60 AND -6 AND IFNULL(Volume,0)=0) zero_pre,
  COUNTIF(k BETWEEN 6 AND 60 AND IFNULL(Volume,0)=0) zero_post,
  STDDEV(IF(k BETWEEN -60 AND -1,ret,NULL)) rvol60,
  EXP(SUM(IF(k BETWEEN -126 AND -21,LN(1+ret),0)))-1 mom6m
FROM w GROUP BY ticker,ex_date ORDER BY ticker,ex_date
"""

UNIVERSE = EVENT_CTE + f"""
SELECT e.ticker,e.ex_date,IFNULL(u.in_universe,FALSE) in_universe,
  IFNULL(u.backfilled,FALSE) backfilled
FROM ev e LEFT JOIN `{PROJECT}.tav2_mike.universe_pit` u
ON u.ticker=e.ticker AND u.time=e.ex_date
"""

# Candidate snapshots for the pre-registered matched-control robustness. Candidate outcomes
# are never used for ranking. We return the 50 closest pre-outcome candidates and perform the
# no-replacement-within-month greedy assignment locally in the analyzer.
MATCH_CANDIDATES = EVENT_CTE + f"""
, px0 AS (
 SELECT t.ticker,t.time,t.Close,t.Price,t.Volume,t.ICB_Code,
   SAFE_DIVIDE(t.Close,LAG(t.Close) OVER(PARTITION BY t.ticker ORDER BY t.time))-1 ret,
   LAG(t.Close,21) OVER(PARTITION BY t.ticker ORDER BY t.time) c_l21,
   LAG(t.Close,126) OVER(PARTITION BY t.ticker ORDER BY t.time) c_l126,
   LEAD(t.Close,20) OVER(PARTITION BY t.ticker ORDER BY t.time) c_f20,
   LEAD(t.time,20) OVER(PARTITION BY t.ticker ORDER BY t.time) d_f20
 FROM `{PROJECT}.tav2_bq.ticker` t WHERE t.time>=DATE '{PANEL_START}' AND t.Close>0
), px AS (
 SELECT *,AVG(Price*Volume) OVER(PARTITION BY ticker ORDER BY time ROWS BETWEEN 60 PRECEDING AND 6 PRECEDING) adv60,
   STDDEV(ret) OVER(PARTITION BY ticker ORDER BY time ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING) rvol60,
   SAFE_DIVIDE(c_l21,c_l126)-1 mom6m
 FROM px0
), focal AS (
 SELECT e.ticker,e.ex_date,p.ICB_Code icb,p.adv60,p.rvol60,p.mom6m,
   p.Close focal_c0,p.c_f20 focal_c20,p.d_f20 end_date
 FROM ev e JOIN px p ON p.ticker=e.ticker AND p.time=e.ex_date
), cand0 AS (
 SELECT f.ticker event_ticker,f.ex_date,f.end_date,f.focal_c0,f.focal_c20,
   c.ticker control_ticker,c.adv60,c.rvol60,c.mom6m,c.Close control_c0,ce.Close control_c20,
   SAFE_DIVIDE(LN(NULLIF(c.adv60,0))-LN(NULLIF(f.adv60,0)),
     NULLIF(STDDEV(LN(NULLIF(c.adv60,0))) OVER(PARTITION BY f.ticker,f.ex_date),0)) z_adv,
   SAFE_DIVIDE(c.mom6m-f.mom6m,
     NULLIF(STDDEV(c.mom6m) OVER(PARTITION BY f.ticker,f.ex_date),0)) z_mom,
   SAFE_DIVIDE(c.rvol60-f.rvol60,
     NULLIF(STDDEV(c.rvol60) OVER(PARTITION BY f.ticker,f.ex_date),0)) z_vol
 FROM focal f JOIN `{PROJECT}.tav2_mike.universe_pit` u ON u.time=f.ex_date AND u.in_universe
 JOIN px c ON c.ticker=u.ticker AND c.time=f.ex_date
 JOIN px ce ON ce.ticker=c.ticker AND ce.time=f.end_date
 WHERE c.ticker!=f.ticker AND c.adv60>0 AND f.adv60>0 AND c.rvol60 IS NOT NULL AND c.mom6m IS NOT NULL
   AND SUBSTR(CAST(c.ICB_Code AS STRING),1,1)=SUBSTR(CAST(f.icb AS STRING),1,1)
), ranked AS (
 SELECT *,SQRT(z_adv*z_adv+z_mom*z_mom+z_vol*z_vol) dist,
   ROW_NUMBER() OVER(PARTITION BY event_ticker,ex_date ORDER BY
     z_adv*z_adv+z_mom*z_mom+z_vol*z_vol,control_ticker) rank
 FROM cand0 WHERE ABS(z_adv)<=0.5 AND ABS(z_mom)<=0.5 AND ABS(z_vol)<=0.5
)
SELECT * FROM ranked WHERE rank<=50 ORDER BY event_ticker,ex_date,rank
"""

AIS_CORE = f"""
SELECT ticker,effective_date ais_date,shares_delta,shares_total_after
FROM `{PROJECT}.tav2_bq.corporate_action`
WHERE event_code='AIS' AND event_status='executed' AND effective_date IS NOT NULL
  AND effective_date BETWEEN DATE '2014-01-01' AND DATE '2027-06-30'
"""
AIS_EVENTS = AIS_CORE + " ORDER BY ticker,ais_date"

AIS_PANEL = f"""
WITH ev AS ({AIS_CORE}), px AS (
 SELECT t.ticker,t.time,t.Close,t.Volume,
  ROW_NUMBER() OVER(PARTITION BY t.ticker ORDER BY t.time) si
 FROM `{PROJECT}.tav2_bq.ticker` t WHERE t.time>=DATE '{PANEL_START}' AND t.Close>0
), first_trade AS (
 SELECT e.ticker,e.ais_date,ANY_VALUE(e.shares_delta) shares_delta,
   ANY_VALUE(e.shares_total_after) shares_total_after,MIN(p.time) trading_date
 FROM ev e JOIN px p ON p.ticker=e.ticker AND p.time>=e.ais_date
 GROUP BY e.ticker,e.ais_date
), a AS (
 SELECT f.*,p.si si0 FROM first_trade f JOIN px p
 ON p.ticker=f.ticker AND p.time=f.trading_date
), w AS (
 SELECT a.*,p.si-a.si0 k,p.time dt,p.Close,p.Volume FROM a JOIN px p
 ON p.ticker=a.ticker AND p.si BETWEEN a.si0-61 AND a.si0+62
)
SELECT ticker,ais_date,ANY_VALUE(trading_date) trading_date,
 ANY_VALUE(shares_delta) shares_delta,ANY_VALUE(shares_total_after) shares_total_after,
 MAX(IF(k=-1,Close,NULL)) c_m1,MAX(IF(k=-1,dt,NULL)) d_m1,
 MAX(IF(k=0,Close,NULL)) c_0,MAX(IF(k=0,dt,NULL)) d_0,
 MAX(IF(k=5,Close,NULL)) c_5,MAX(IF(k=5,dt,NULL)) d_5,
 MAX(IF(k=20,Close,NULL)) c_20,MAX(IF(k=20,dt,NULL)) d_20,
 MAX(IF(k=60,Close,NULL)) c_60,MAX(IF(k=60,dt,NULL)) d_60,
 MAX(IF(k=0,Volume,NULL)) v_0,AVG(IF(k BETWEEN -60 AND -6,Volume,NULL)) avol_pre,
 AVG(IF(k BETWEEN 0 AND 5,Volume,NULL)) avol_0_5
FROM w GROUP BY ticker,ais_date ORDER BY ticker,ais_date
"""


def load_ledger():
    with gzip.open(os.path.join(HERE, "out", "event_ledger.csv.gz"), "rt", newline="") as fh:
        return list(csv.DictReader(fh))


def main():
    os.makedirs(OUT, exist_ok=True)
    ledger = load_ledger()
    print("[1/5] ex-date panel")
    ex = bq_csv(EX_PANEL, "q1_ex_panel")
    print("[2/5] universe membership")
    univ = bq_csv(UNIVERSE, "q2_universe")
    print("[3/5] AIS candidates and panels")
    ais = bq_csv(AIS_EVENTS, "q3_ais_candidates")
    ap = bq_csv(AIS_PANEL, "q4_ais_panel")
    print("[4/5] pre-outcome matched-control candidates")
    mc = bq_csv(MATCH_CANDIDATES, "q5_match_candidates")

    u = {(r["ticker"],r["ex_date"]):r for r in univ}
    # Canonical ledger components and all price-adjusting contamination dates.
    led = defaultdict(list); adjust = defaultdict(list); all_ais = defaultdict(set)
    for r in ledger:
        if r["event_family"] == "ADDITIONAL_LISTING" and r["effective_date"]:
            all_ais[r["ticker"]].add(day(r["effective_date"]))
        if r["actionable"] != "1" or not r["exright_date"]:
            continue
        dd = day(r["exright_date"])
        if r["is_price_adjusting"] == "1":
            adjust[r["ticker"]].append((dd,r["event_subtype"]))
        if r["event_subtype"] in ("STOCK_DIVIDEND","BONUS"):
            led[(r["ticker"],r["exright_date"])].append(r)

    rows=[]
    for r in ex:
        key=(r["ticker"],r["ex_date"]); comps=led.get(key,[]); dt=day(r["ex_date"])
        uu=u.get(key,{})
        # Exempt only the focal stock/bonus components. A same-day cash dividend or rights
        # event is contamination and must not disappear merely because the date is equal.
        nearby=[x for x,sub in adjust[r["ticker"]]
                if not (x==dt and sub in ("STOCK_DIVIDEND","BONUS"))
                and dt-timedelta(21)<=x<=dt+timedelta(90)]
        out={"ticker":r["ticker"],"ex_date":r["ex_date"],
             "ratio_total":num(r["ratio_total"]),"issue_volume":num(r["issue_volume"]),
             "listing_date":r.get("listing_date") or "","subtype_list":r["subtype_list"],
             "n_subtypes":int(r["n_subtypes"]),"n_components":int(r["n_components"]),
             "ledger_components":len(comps),
             "ledger_ratio_total":sum(num(x["exercise_ratio"]) or 0 for x in comps),
             "in_universe_pit":int(uu.get("in_universe")=="true"),
             "univ_backfilled":int(uu.get("backfilled")=="true"),
             "n_other_adjust_21":sum(abs((x-dt).days)<=21 for x in nearby),
             "n_other_adjust_90":len(nearby)}
        for c,v in r.items():
            if c not in out and c not in ("ticker","ex_date","subtype_list","listing_date"):
                out[c]=v if c.startswith("d_") or c=="icb" else num(v)
        rows.append(out)

    # Link AIS exactly as preregistered. Tier A is the issuance listing date. Tier B needs one
    # candidate and a volume match; all candidates and conflicts remain visible.
    ais_by=defaultdict(list)
    for a in ais: ais_by[a["ticker"]].append(a)
    apmap={(r["ticker"],r["ais_date"]):r for r in ap}
    links=[]
    for e in rows:
        exd=day(e["ex_date"]); listing=day(e["listing_date"])
        cand=[a for a in ais_by[e["ticker"]] if 7 <= (day(a["ais_date"])-exd).days <= 365]
        tier="UNLINKED"; chosen=None; conflict=0
        if listing and 0 < (listing-exd).days <= 365:
            tier="A"; chosen=listing
            close=[a for a in cand if abs((day(a["ais_date"])-listing).days)<=5]
            if close:
                a=min(close,key=lambda x:abs((day(x["ais_date"])-listing).days))
                iv=e["issue_volume"] or 0; av=num(a["shares_delta"]) or 0
                if abs((day(a["ais_date"])-listing).days)>5 or (iv and abs(av-iv)>max(.02*iv,1000)):
                    conflict=1
            elif cand:
                # Both sources exist but do not identify the same arrival date.
                conflict=1
        elif len(cand)==1 and e["issue_volume"]:
            a=cand[0]; av=num(a["shares_delta"]) or 0; iv=e["issue_volume"]
            if abs(av-iv)<=max(.02*iv,1000): tier="B"; chosen=day(a["ais_date"])
        if len(cand)>1 and tier=="UNLINKED": tier="AMBIGUOUS"
        n_other_ais21 = 0
        n_adjust_ais21 = 0
        if chosen:
            n_other_ais21 = sum(x != chosen and abs((x-chosen).days) <= 21
                                for x in all_ais[e["ticker"]])
            n_adjust_ais21 = sum(abs((x-chosen).days) <= 21
                                 for x,_ in adjust[e["ticker"]])
        base={**e,"ais_link_tier":tier,"ais_conflict":conflict,"n_ais_candidates":len(cand),
              "ais_date":chosen.isoformat() if chosen else "",
              "n_other_ais_21":n_other_ais21,"n_adjust_at_ais_21":n_adjust_ais21}
        p=apmap.get((e["ticker"],base["ais_date"]),{})
        for c,v in p.items():
            if c not in ("ticker","ais_date"):
                base["ais_"+c]=v if c.startswith("d_") or c=="trading_date" else num(v)
        links.append(base)

    dump("ex_panel.csv",rows); dump("linked_panel.csv",links); dump("ais_candidates.csv",ais)
    dump("match_candidates.csv",mc)
    summary={"n_ex_panel":len(rows),"n_core":sum(x["in_universe_pit"] for x in rows),
      "n_stock_dividend":sum(x["subtype_list"]=="STOCK_DIVIDEND" for x in rows),
      "n_bonus":sum(x["subtype_list"]=="BONUS" for x in rows),
      "n_mixed":sum(x["n_subtypes"]>1 for x in rows),
      "ais_tiers":dict((k,sum(x["ais_link_tier"]==k for x in links))
                       for k in ("A","B","CONFLICT","UNLINKED","AMBIGUOUS")),
      "n_ais_conflict":sum(x["ais_conflict"] for x in links),
      "n_match_candidate_rows":len(mc),
      "n_events_with_match_candidate":len(set((x["event_ticker"],x["ex_date"]) for x in mc))}
    with open(os.path.join(OUT,"build_summary.json"),"w") as fh: json.dump(summary,fh,indent=2)
    print(json.dumps(summary,indent=2)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
