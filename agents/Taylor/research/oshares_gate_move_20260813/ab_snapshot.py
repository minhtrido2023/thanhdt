#!/usr/bin/env python3
"""ab_snapshot.py — chụp OUTPUT của cả hai tầng để so TRƯỚC/SAU khi dời cổng chứng nhận.

Việc dời cổng từ `oshares_pit` vào `oshares_live` là refactor: giá trị CUỐI CÙNG mà consumer
nhận phải KHÔNG ĐỔI. Cách duy nhất chứng minh điều đó không phải bằng lập luận là chụp lại
output thật trên một rổ đủ rộng, trước và sau, rồi diff từng ô.

Chụp 2 tầng:
  * `oshares_pit` / `oshares_reconciled` — hợp đồng với consumer. PHẢI trùng tuyệt đối
    (`value`, `source`, `rel_diff`, `live_value`); `reason`/`method` được chụp riêng vì cổng
    đổi CHỖ nên nhãn có quyền đổi tên — nhưng giá trị thì không.
  * `oshares_at` — hàm gốc. Ở đây output CỐ Ý đổi: đó chính là việc cần làm.

Số nền (fallback) lấy từ `ticker_financial` đúng cách consumer đang lấy, để không tự bịa
một baseline khác với thực tế.
"""
import json
import os
import sys

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

from corp_action_lib import bq                                              # noqa: E402
from oshares_live import oshares_at                                         # noqa: E402
from oshares_pit import fetch_cache, oshares_pit, oshares_reconciled        # noqa: E402

FIN = "lithe-record-440915-m9.tav2_bq.ticker_financial"

# rổ cố ý trộn: 3 mã có ca đã kiểm tay (IDC/AAA/FPT), 2 mã "sạch" (VNM/TCB), 1 mã không có AIS
# nào (DHG), 1 mã có 2 đợt cùng ngày (MBB), 1 mã ISS chặn đường (HAH), + nhóm ngân hàng/lớn.
TICKERS = ["IDC", "AAA", "FPT", "VNM", "TCB", "DHG", "MBB", "HAH", "ACB", "HDB", "PVT",
           "VCB", "SSI", "HPG", "VIC", "GAS", "REE", "DGC", "NLG", "PNJ"]
DATES = ["2016-01-05", "2018-01-03", "2019-08-05", "2020-05-05", "2021-02-05",
         "2022-10-03", "2024-01-03", "2026-06-16"]
UNTIL = max(DATES)


def _fallback(tickers, asof):
    """Số quý gần nhất <= asof cho từng mã — đúng nguồn consumer đang dùng làm số nền."""
    tk = ",".join(f'"{t}"' for t in tickers)
    rows = bq(f"""
        SELECT ticker, CAST(time AS STRING) time, OShares
        FROM `{FIN}`
        WHERE ticker IN ({tk}) AND time <= DATE "{asof}" AND OShares IS NOT NULL AND OShares > 0
        QUALIFY ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC) = 1
    """)
    return {r["ticker"]: float(r["OShares"]) for r in rows}


def main(out_path):
    cache = fetch_cache(TICKERS, UNTIL)
    snap = {}
    for d in DATES:
        fb = _fallback(TICKERS, d)
        raw = oshares_at(TICKERS, d, _cache=cache)
        pit = oshares_pit(TICKERS, d, fb, cache=cache)
        rec = oshares_reconciled(TICKERS, d, fb, cache=cache)
        for t in TICKERS:
            snap[f"{d}|{t}"] = {
                "fallback": fb.get(t),
                "raw_value": raw[t]["value"], "raw_method": raw[t]["method"],
                "raw_anchor": raw[t].get("anchor_date"), "raw_src": raw[t].get("anchor_source"),
                "pit_value": pit[t]["value"], "pit_source": pit[t]["source"],
                "pit_live": pit[t]["live_value"], "pit_rel": pit[t]["rel_diff"],
                "pit_reason": pit[t]["reason"], "pit_method": pit[t]["method"],
                "rec_value": rec[t]["value"], "rec_source": rec[t]["source"],
                "rec_live": rec[t]["live_value"], "rec_rel": rec[t]["rel_diff"],
                "rec_reason": rec[t]["reason"], "rec_method": rec[t]["method"],
            }
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(snap, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print(f"đã ghi {len(snap)} ô -> {out_path}")


if __name__ == "__main__":
    main(sys.argv[1])
