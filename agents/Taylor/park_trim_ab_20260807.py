#!/usr/bin/env python3
"""A/B công thức park_trim CŨ (pro-rata trọng số sống) vs MỚI (tgt_i − mv_i) trên dữ liệu SỐNG.

Gọi `park_holdings` ĐÚNG MỘT LẦN cho mỗi account rồi bơm cùng snapshot vào cả hai phiên bản ⇒
mọi khác biệt là do CÔNG THỨC, không phải do giá/vị thế trôi giữa 2 lần đọc.
CHỈ ĐỌC — không ghi plan, không đặt lệnh.
"""
import json
import os
import sys

BIN = "/home/trido/thanhdt/WorkingClaude/mike/bin"
sys.path.insert(0, BIN)
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")

import compute_park_trim as new                      # noqa: E402
import _park_trim_old_ref as old                     # noqa: E402
from park_holdings import park_holdings, today_ict   # noqa: E402

ASOF = today_ict()
OUT = os.path.dirname(os.path.abspath(__file__))

for acct in ("SpaceX", "ZaloPay"):
    print(f"\n{'='*78}\n### {acct}  asof={ASOF}\n{'='*78}")
    h = park_holdings(acct, ASOF)
    r_old = old.compute_trim(acct, ASOF, old.PARK_TARGET_F1, holdings=h)
    r_new = new.compute_trim(acct, ASOF, new.PARK_TARGET_F1, holdings=h)
    for tag, r in (("OLD", r_old), ("NEW", r_new)):
        with open(os.path.join(OUT, f"park_trim_ab_{acct}_{tag}.json"), "w",
                  encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=1, default=str)

    print(f"pool {r_new.get('pool_vnd', 0)/1e6:,.2f}tr  PARK {r_new['park_mv_vnd']/1e6:,.2f}tr  "
          f"cash {r_new['cash_available_vnd']/1e6:,.2f}tr  "
          f"target {r_new.get('target_park_vnd', 0)/1e6:,.2f}tr")
    print(f"decision  OLD={r_old['decision']}   NEW={r_new['decision']}")
    print(f"rổ kỳ {r_new.get('basket_rebal_date')}: {r_new.get('basket_feasible_n')}"
          f"/{r_new.get('basket_n')} khả thi, bỏ Σ{(r_new.get('basket_dropped_weight') or 0)*100:.2f}%")
    for d in (r_new.get("basket_dropped") or []):
        print(f"    – bỏ {d['ticker']:<5} w={d['weight']*100:5.2f}%  {d['reason']}")

    o_old = {o["ticker"]: o for o in r_old.get("orders", [])}
    o_new = {o["ticker"]: o for o in r_new.get("orders", [])}
    per = {}
    for l in h["park_lots"]:
        per[l["ticker"]] = per.get(l["ticker"], 0.0) + l["mv_vnd"]
    print(f"\n{'mã':<6}{'MV(tr)':>10}{'tgt(tr)':>10}{'OLD bán':>12}{'NEW bán':>12}  ghi chú")
    for tk in sorted(set(per) | set(o_old) | set(o_new)):
        tg = (r_new.get("target_value_vnd") or {}).get(tk, 0.0)
        vo = o_old.get(tk, {}).get("value_vnd", 0.0)
        vn = o_new.get(tk, {}).get("value_vnd", 0.0)
        note = ""
        if tk not in (r_new.get("target_weights") or {}):
            note = "NGOÀI rổ khả thi ⇒ tgt=0"
        if tk in o_new and o_new[tk]["qty"] >= sum(
                l["qty"] for l in h["park_lots"] if l["ticker"] == tk):
            note += "  ⇒ BÁN SẠCH"
        print(f"{tk:<6}{per.get(tk,0)/1e6:>10,.2f}{tg/1e6:>10,.2f}"
              f"{vo/1e6:>12,.2f}{vn/1e6:>12,.2f}  {note}")
    print(f"{'Σ':<6}{h['park_mv_vnd']/1e6:>10,.2f}{'':>10}"
          f"{r_old.get('trim_proposed_vnd', 0)/1e6:>12,.2f}"
          f"{r_new.get('trim_proposed_vnd', 0)/1e6:>12,.2f}")
    print(f"\nNEW: lệch cấu trúc {r_new.get('structural_excess_vnd', 0)/1e6:,.2f}tr, "
          f"đề xuất {r_new.get('trim_proposed_vnd', 0)/1e6:,.2f}tr, "
          f"PARK sau = {r_new.get('park_mv_after_vnd', 0)/1e6:,.2f}tr "
          f"({(r_new.get('park_pct_after') or 0)*100:.1f}% pool), "
          f"dưới target {r_new.get('underpark_after_vnd', 0)/1e6:,.2f}tr")
    for b in r_new.get("blocked", []):
        print(f"  – blocked {b['ticker']}: {b['reason']}")
    for a in r_new.get("at_or_below_target", []):
        print(f"  · {a['ticker']} {a['mv_vnd']/1e6:,.2f}tr ≤ tgt {a['target_vnd']/1e6:,.2f}tr "
              f"(thiếu {a['gap_vnd']/1e6:,.2f}tr)")
    for n in r_new.get("notes", []):
        print(f"  ⚠ {n}")
