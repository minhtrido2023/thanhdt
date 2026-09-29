#!/usr/bin/env python3
"""Pin a corporate-action vintage for the 204 basket names — DIV + ISS + AIS, full detail.

Why a SEPARATE snapshot from data/snapshots/corp_action_share_20260927.parquet: that one was
dumped for the WEIGHT leg and therefore carries only ISS+AIS (share steps). The position replay
also needs DIV (cash) and the issue-method taxonomy, so it needs its own vintage — the table is
UPSERT-in-place (registry price-volume/corporate_action_bq.md Bay 2b), so a pinned result must be
able to name the vintage it was computed on.
"""
import sys
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import pandas as pd
import corp_action_lib as cal

OUT = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/c30v_position_replay_20260927"
names = sorted(pd.read_parquet(f"{OUT}/members_df.parquet")["ticker"].unique())
print(f"[ca] {len(names)} ten trong union rổ")

rows = []
for i in range(0, len(names), 60):
    rows += cal._events(list(names[i:i + 60]), None, None, ("DIV", "ISS", "AIS"),
                        'event_status != "not_executed"')
ev = pd.DataFrame(rows)
print(f"[ca] {len(ev):,} dong; freshness = {cal.feed_freshness()}")
ev["issue_method_name_vi"] = ev["issue_method_name_vi"].fillna("")   # NaN la float, khong co .strip() (cung bay custom_basket.normalise_corp_action da ghi)
ev["price_adjusting"] = [cal.is_price_adjusting(r) for r in ev.to_dict("records")]
ev.to_parquet(f"{OUT}/ca_vintage.parquet", index=False)
print(ev.groupby(["event_code", "price_adjusting"]).size())
print("\n[ca] ISS theo issue_method:")
print(ev[ev.event_code == "ISS"].groupby(["issue_method_name_vi", "price_adjusting"]).size().to_string())
