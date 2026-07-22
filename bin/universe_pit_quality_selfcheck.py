#!/usr/bin/env python3
"""
universe_pit_quality_selfcheck.py — kiểm tra cờ chất lượng Q-C tái lập đúng số đo G2b.

Chạy: python3 universe_pit_quality_selfcheck.py     (exit 0 = PASS)

Kiểm 4 điều:
  1. Số dòng bảng quality == số dòng in_universe của universe_pit (phủ đủ, không thừa).
  2. Nhóm rule-only (in universe_pit, ngoài ticker_prune) tại 4 mốc = 89/124/233/166 (G2b).
  3. `quality_flag = QUALITY_OK` trên nhóm rule-only = "leak" của G2b: 45/77/60 (2018/2022/2026).
     ⚠️ 2026 kỳ vọng **60**, KHÔNG phải 61 như G2b ghi: G2b đọc panel snapshot local
     `data/fa_ratings_8l_hist.csv` (mtime 06-16), còn cờ này đọc bảng CANONICAL
     `tav2_bq.fa_ratings_8l` đã refresh — TLD bị re-rank 3→5 tại cùng eff-date 2026-05-04
     (refresh weekly re-rank 2 quý mở, data_registry.md dòng 117). Đây là dữ liệu tươi hơn,
     không phải sai lệch tính toán. Mọi mã khác trùng khít.
  4. 2014-06-30 phải ra UNKNOWN_RATING (panel 8L bắt đầu 2014-07-09), KHÔNG được ra "0 leak" —
     đúng cảnh báo §3.2b-G2b: thiếu dữ liệu không được đọc thành kết quả tốt.
"""
import os
os.environ.pop("BQ_LOCAL_CACHE", None)
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_universe_pit import DATASET, PROJECT, TABLE, get_client, _q  # noqa: E402
from build_universe_pit_quality import QTABLE  # noqa: E402

DATES = ["2014-06-30", "2018-06-29", "2022-06-30", "2026-06-15"]
EXP_RULE_ONLY = {"2014-06-30": 89, "2018-06-29": 124, "2022-06-30": 233, "2026-06-15": 166}
EXP_LEAK = {"2018-06-29": 45, "2022-06-30": 77, "2026-06-15": 60}

U = f"`{PROJECT}.{DATASET}.{TABLE}`"
Q = f"`{PROJECT}.{DATASET}.{QTABLE}`"


def main():
    c = get_client()
    fails = []

    r = _q(c, f"SELECT (SELECT COUNT(*) FROM {U} WHERE in_universe) AS n_in, "
              f"(SELECT COUNT(*) FROM {Q}) AS n_q")[0]
    ok = r["n_in"] == r["n_q"]
    print(f"[1] phu dong: in_universe={r['n_in']} quality={r['n_q']} -> {'OK' if ok else 'FAIL'}")
    if not ok:
        fails.append("row coverage")

    dl = ",".join(f'DATE"{d}"' for d in DATES)
    rows = _q(c, f"""
WITH D AS (SELECT d FROM UNNEST([{dl}]) d),
UU AS (SELECT u.time,u.ticker FROM {U} u JOIN D ON u.time=D.d WHERE u.in_universe),
P AS (SELECT p.time,p.ticker FROM `{PROJECT}.tav2_bq.ticker_prune` p JOIN D ON p.time=D.d),
RO AS (SELECT UU.time,UU.ticker FROM UU LEFT JOIN P USING(time,ticker) WHERE P.ticker IS NULL)
SELECT RO.time, COUNT(*) AS rule_only,
  COUNTIF(q.quality_flag='QUALITY_OK') AS leak,
  COUNTIF(q.quality_flag='UNKNOWN_RATING') AS unk_rating
FROM RO JOIN {Q} q USING(time,ticker) GROUP BY 1 ORDER BY 1""")

    for x in rows:
        d = str(x["time"])
        ro_ok = x["rule_only"] == EXP_RULE_ONLY[d]
        print(f"[2/3] {d}: rule_only={x['rule_only']} (ky vong {EXP_RULE_ONLY[d]}) "
              f"leak={x['leak']} unk_rating={x['unk_rating']} -> {'OK' if ro_ok else 'FAIL'}")
        if not ro_ok:
            fails.append(f"rule_only {d}")
        if d in EXP_LEAK and x["leak"] != EXP_LEAK[d]:
            fails.append(f"leak {d}: {x['leak']} != {EXP_LEAK[d]}")
        if d == "2014-06-30":
            if x["leak"] != 0 or x["unk_rating"] == 0:
                fails.append("2014 phai la UNKNOWN_RATING, khong phai leak=0 sach")
            else:
                print("[4] 2014-06-30: leak=0 vi UNKNOWN_RATING (thieu panel) -> OK, dung ky vong")

    print("PASS" if not fails else "FAIL: " + "; ".join(fails))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
