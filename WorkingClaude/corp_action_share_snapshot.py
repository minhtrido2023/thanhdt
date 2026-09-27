#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""corp_action_share_snapshot.py — freeze the corp-action share-event vintage for a pinned run.

`tav2_bq.corporate_action` is UPSERTED IN PLACE (`mike/kb/data_registry/price-volume/
corporate_action_bq.md` Bẫy 2b), so a result pinned today cannot be reproduced from a live read
months from now. Dump the whole ISS+AIS set once, pass it back with
`BASKET_CA_SNAPSHOT=<path>` — same role as pinning `BQ_LOCAL_CACHE` to an `asof` cache.

Whole table, no ticker filter, ON PURPOSE: the basket's member union depends on the run, and a
snapshot missing a ticker degrades that name to the quarterly release date SILENTLY.

  python3 corp_action_share_snapshot.py data/snapshots/corp_action_share_YYYYMMDD.parquet
"""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corp_action_lib as cal          # noqa: E402
import custom_basket as cb             # noqa: E402


def main():
    out = sys.argv[1]
    fresh = cal.feed_freshness()
    print(f"[freshness] max_ingested={fresh['max_ingested']} max_public={fresh['max_public']} "
          f"rows={fresh['n']}")
    rows = cal.bq(f"""
        SELECT ticker, event_code, CAST(exright_date AS STRING) exright_date,
               CAST(effective_date AS STRING) effective_date, event_status,
               value_per_share, exercise_ratio, issue_method_name_vi,
               shares_delta, shares_total_after, event_title_vi,
               CAST(public_date AS STRING) public_date
        FROM `{cal.TABLE}`
        WHERE event_code IN ("ISS","AIS") AND event_status != "not_executed"
        ORDER BY ticker, exright_date, public_date""")
    ev = cb.normalise_corp_action(rows)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    ev.to_parquet(out, index=False)
    print(f"  {len(ev)} dòng, {ev['ticker'].nunique()} mã, share_date "
          f"{ev['share_date'].min()}→{ev['share_date'].max()} -> {out}")
    print(f"  digest(share_date+ratio) = "
          f"{pd.util.hash_pandas_object(ev[['ticker','event_code','share_date','exercise_ratio']].astype(str)).sum()}")


if __name__ == "__main__":
    main()
