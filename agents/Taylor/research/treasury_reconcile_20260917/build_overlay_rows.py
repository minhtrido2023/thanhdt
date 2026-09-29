"""DRY-RUN — dựng dòng cho bảng overlay đề xuất `tav2_mike.treasury_share_events` (hoặc vị trí Mike/user chọn).
KHÔNG ghi BQ. Output: overlay_rows_dryrun.csv. id deterministic ⇒ chạy lại/MERGE không trùng."""
import csv, hashlib, os, sys
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from corp_action_lib import bq
OUT = os.path.dirname(os.path.abspath(__file__))
rows = bq("""
  SELECT ticker, CAST(public_date AS STRING) public_date, action_type,
         MAX(ABS(shares_delta)) abs_delta, COUNT(DISTINCT news_id) n_src,
         STRING_AGG(DISTINCT CAST(news_id AS STRING), ',' ORDER BY CAST(news_id AS STRING)) news_ids,
         MIN(public_datetime) first_public_datetime, MAX(ingested_at) max_ingested_at,
         COUNT(DISTINCT ABS(shares_delta)) n_distinct_delta
  FROM `lithe-record-440915-m9.tav2_bq.treasury_news` AS t
  WHERE action_type IN ('buy_done','sell_done')
  GROUP BY 1,2,3 ORDER BY 1,2,3""")
out = []
for r in rows:
    key = f'{r["ticker"]}|{r["public_date"]}|{r["action_type"]}'
    d = float(r["abs_delta"]) if r["abs_delta"] is not None else None
    out.append({"id": "TRSY-" + hashlib.sha1(key.encode()).hexdigest()[:16], "ticker": r["ticker"],
                "event_date": r["public_date"], "action_type": r["action_type"],
                "outstanding_delta": (-d if r["action_type"] == "buy_done" else d) if d else None,
                "size_status": "SIZED" if d and int(r["n_distinct_delta"]) == 1 else ("CONFLICT" if d else "UNSIZED"),
                "source_news_ids": r["news_ids"], "n_sources": r["n_src"],
                "first_public_datetime": r["first_public_datetime"], "source_max_ingested_at": r["max_ingested_at"],
                "source_url": f'treasury_news://{r["news_ids"]}'})
with open(f"{OUT}/overlay_rows_dryrun.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
from collections import Counter
print(len(out), "rows;", Counter(o["size_status"] for o in out), "; ids unique:", len({o["id"] for o in out}) == len(out))
