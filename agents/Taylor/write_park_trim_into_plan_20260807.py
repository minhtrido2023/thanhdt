#!/usr/bin/env python3
"""Ghi kết quả compute_park_trim.py (bản MỚI, §D1) vào `park_trim_proposal` của plan JSON.

Job Taylor_20260807_032037. CHỈ đụng đúng 1 key `park_trim_proposal` — `orders` (lệnh thực thi),
`approved_by` và mọi field khác GIỮ NGUYÊN tuyệt đối.

Schema: dùng CHÍNH output của `compute_trim()` (không bịa tên field mới) + 2 key vốn đã có trong
bản cũ của plan: `source` (đường dẫn script) và `risk_dial_override` (carry-over từ bản cũ, script
không sinh ra field này).

Ghi ATOMIC (tmp + os.replace) — §5 coding_guidelines: autoheal đang chạy run_bot mỗi 5 phút và
ĐỌC file này; không được để nó thấy file ghi dở.
"""
import json
import os
import sys

WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, os.path.join(WC, "mike", "bin"))
from compute_park_trim import compute_trim  # noqa: E402

PLAN_DIR = os.path.join(WC, "data", "trade_plans")
ACCOUNTS = ["SpaceX", "ZaloPay"]


def main():
    for label in ACCOUNTS:
        path = os.path.join(PLAN_DIR, f"plan_{label}_2026-08-07.json")
        with open(path, encoding="utf-8") as f:
            plan = json.load(f)

        old = plan.get("park_trim_proposal") or {}
        r = compute_trim(label)

        prop = {"source": "mike/bin/compute_park_trim.py"}
        prop.update(json.loads(json.dumps(r, default=str)))
        # carry-over: script không sinh field này, bản cũ của plan có
        prop["risk_dial_override"] = old.get("risk_dial_override")

        orders_before = json.dumps(plan.get("orders"), sort_keys=True)
        approved_before = (plan.get("approved_by"), plan.get("approved_at"))

        plan["park_trim_proposal"] = prop

        assert json.dumps(plan.get("orders"), sort_keys=True) == orders_before, "orders bị đổi!"
        assert (plan.get("approved_by"), plan.get("approved_at")) == approved_before, "approval bị đổi!"

        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(plan, f, ensure_ascii=False, indent=1)
        os.replace(tmp, path)

        print(f"[{label}] {path}")
        print(f"   cũ: {old.get('decision')} asof={old.get('asof')} "
              f"Σ={(old.get('trim_proposed_vnd') or 0)/1e6:,.2f}tr / {len(old.get('orders') or [])} mã")
        print(f"   MỚI: {prop['decision']} asof={prop['asof']} "
              f"Σ={prop['trim_proposed_vnd']/1e6:,.2f}tr / {len(prop['orders'])} mã, "
              f"PARK sau bán {prop['park_pct_after']:.1%}")


if __name__ == "__main__":
    sys.exit(main() or 0)
