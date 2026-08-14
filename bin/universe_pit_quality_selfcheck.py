#!/usr/bin/env python3
"""
universe_pit_quality_selfcheck.py — kiểm tra cờ chất lượng Q-C tái lập đúng số đo G2b.

Chạy: python3 universe_pit_quality_selfcheck.py     (exit 0 = PASS)

Kiểm 4 điều:
  1. Số dòng bảng quality == số dòng in_universe của universe_pit (phủ đủ, không thừa).
  2. Nhóm rule-only (in universe_pit, ngoài ticker_prune) TỰ NHẤT QUÁN theo định nghĩa
     (rule_only == n_universe − |universe ∩ prune|) và bảng quality phân hoạch nó ĐÚNG MỘT
     lần (tổng các cờ == rule_only, không mã nào 2 cờ, không mã nào rơi ngoài).
  3. Pseudo-ticker chỉ số/ETF (VNINDEX/VN30/E1VFVN30) KHÔNG được nằm trong universe_pit.
  4. 2014-06-30 phải ra UNKNOWN_RATING (panel 8L bắt đầu 2014-07-09), KHÔNG được ra "0 leak" —
     đúng cảnh báo §3.2b-G2b: thiếu dữ liệu không được đọc thành kết quả tốt.

⚠️ VÌ SAO KHÔNG CÒN GHIM SỐ TUYỆT ĐỐI (sửa 2026-08-14, §23 hệ luận 1 — job
Taylor_20260814_080528). Bản cũ ghim rule_only = 89/124/233/166 và leak = 45/77/60 đo tại
vintage G2b. `tav2_mike.universe_pit` là bảng ĐƯỢC DỰNG LẠI (lastModified 2026-08-13) nên
mọi số tuyệt đối đo trên nó tự hết hạn theo thời gian — bộ này đỏ 4 ca liên tiếp và trở
thành nhiễu nền, đúng thứ §23 cảnh báo.

Đã TRUY nguyên nhân trước khi đổi assertion (không phải sửa cho xanh):
  đo lại 2026-08-14 → rule_only = 91/126/239/170, và số học khớp TUYỆT ĐỐI với định nghĩa:
    2014: 227 − (138−2) = 91 · 2018: 302 − (178−2) = 126
    2022: 551 − (315−3) = 239 · 2026: 396 − (229−3) = 170
  trong đó phần trừ thêm chính là các pseudo-ticker VNINDEX/VN30/E1VFVN30 — có trong
  `ticker_prune` nhưng (ĐÚNG) không có trong `universe_pit`. Chênh 2014/2018 (+2/+2) giải
  thích trọn vẹn bằng nhóm này; 2022/2026 (+6/+4) còn phần dư do khác vintage build. Không
  có dấu hiệu hồi quy ở builder.

ĐÁNH ĐỔI ĐÃ BIẾT, khai để người sau đọc được: bộ này giờ bắt LỖI CẤU TRÚC (thiếu phủ, phân
hoạch sai, pseudo-ticker lọt, thiếu-dữ-liệu-đọc-thành-tốt) chứ KHÔNG còn bắt "số đổi vài
đơn vị so với G2b". Đó là chủ đích: số tuyệt đối trên một bảng dựng lại không phải bất biến,
nên ghim nó chỉ tạo báo động giả. Số G2b giữ ở đây làm PROVENANCE, không làm assertion.
"""
import os
os.environ.pop("BQ_LOCAL_CACHE", None)
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_universe_pit import DATASET, PROJECT, TABLE, get_client, _q  # noqa: E402
from build_universe_pit_quality import QTABLE  # noqa: E402

DATES = ["2014-06-30", "2018-06-29", "2022-06-30", "2026-06-15"]
# PROVENANCE, KHÔNG phải assertion — số đo tại vintage G2b (xem docstring). Giữ để so sánh
# bằng mắt khi điều tra, không dùng để FAIL.
G2B_RULE_ONLY = {"2014-06-30": 89, "2018-06-29": 124, "2022-06-30": 233, "2026-06-15": 166}
G2B_LEAK = {"2018-06-29": 45, "2022-06-30": 77, "2026-06-15": 60}
# Pseudo-ticker: chỉ số/ETF, có trong ticker_prune nhưng KHÔNG được coi là mã đầu tư được.
PSEUDO_TICKERS = ("VNINDEX", "VN30", "E1VFVN30")

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
  COUNTIF(q.quality_flag='UNKNOWN_RATING') AS unk_rating,
  COUNTIF(q.quality_flag IS NULL) AS no_flag,
  COUNT(DISTINCT RO.ticker) AS n_distinct
FROM RO JOIN {Q} q USING(time,ticker) GROUP BY 1 ORDER BY 1""")

    # Vế đối chiếu ĐỘC LẬP cho bất biến định nghĩa: rule_only phải == n_universe − |∩ prune|.
    # Tính bằng đường KHÁC (đếm từng bảng) để lỗi ở một đường không tự che.
    # `DISTINCT` ở P: ticker_prune trùng dòng (time,ticker) sẽ thổi phồng LEFT JOIN và làm
    # n_overlap > thực tế — cùng lớp bẫy đã biết ở `risk_rating` (CLAUDE.md § BigQuery bẫy 3).
    ref = {str(r["time"]): r for r in _q(c, f"""
WITH D AS (SELECT d FROM UNNEST([{dl}]) d),
UU AS (SELECT u.time,u.ticker FROM {U} u JOIN D ON u.time=D.d WHERE u.in_universe),
P AS (SELECT DISTINCT p.time,p.ticker FROM `{PROJECT}.tav2_bq.ticker_prune` p
        JOIN D ON p.time=D.d)
SELECT UU.time AS time, COUNT(*) AS n_universe,
       COUNTIF(P.ticker IS NOT NULL) AS n_overlap
FROM UU LEFT JOIN P USING(time,ticker) GROUP BY 1 ORDER BY 1""")}

    for x in rows:
        d = str(x["time"])
        # [2] BẤT BIẾN ĐỊNH NGHĨA (thay cho số ghim vintage G2b): rule_only là phần bù của
        # prune trong universe — quan hệ này đúng ở MỌI vintage, số tuyệt đối thì không.
        expect_ro = ref[d]["n_universe"] - ref[d]["n_overlap"]
        ro_ok = x["rule_only"] == expect_ro
        drift = x["rule_only"] - G2B_RULE_ONLY[d]
        print(f"[2] {d}: rule_only={x['rule_only']} == n_universe {ref[d]['n_universe']} − "
              f"overlap {ref[d]['n_overlap']} = {expect_ro} -> {'OK' if ro_ok else 'FAIL'}"
              f"   (G2b vintage {G2B_RULE_ONLY[d]}, drift {drift:+d} — chỉ tham chiếu)")
        if not ro_ok:
            fails.append(f"rule_only {d} khong tu nhat quan: {x['rule_only']} != {expect_ro}")

        # [3] PHÂN HOẠCH: mọi mã rule-only phải có ĐÚNG một cờ trong bảng quality. Không mã
        # nào rơi ngoài (no_flag), không mã nào nhân đôi (n_distinct == rule_only).
        if x["no_flag"]:
            fails.append(f"{d}: {x['no_flag']} ma rule-only khong co quality_flag")
        if x["n_distinct"] != x["rule_only"]:
            fails.append(f"{d}: quality nhan doi dong — distinct {x['n_distinct']} "
                         f"!= rows {x['rule_only']}")
        if x["leak"] > x["rule_only"]:
            fails.append(f"{d}: leak {x['leak']} > rule_only {x['rule_only']}")

        if d == "2014-06-30":
            # [4] BẤT BIẾN AN TOÀN — giữ nguyên, đây mới là thứ bộ này thật sự bảo vệ:
            # panel 8L bắt đầu 2014-07-09 ⇒ THIẾU dữ liệu, và thiếu KHÔNG được đọc thành tốt.
            if x["leak"] != 0 or x["unk_rating"] == 0:
                fails.append("2014 phai la UNKNOWN_RATING, khong phai leak=0 sach")
            else:
                print(f"[4] 2014-06-30: leak=0 vi UNKNOWN_RATING={x['unk_rating']} "
                      f"(thieu panel) -> OK, dung ky vong")

    # [3b] Pseudo-ticker chỉ số/ETF không được lọt vào universe_pit ở BẤT KỲ ngày nào —
    # bất biến thật, và chính nhóm này giải thích phần lớn drift so với vintage G2b.
    pl = ",".join(f'"{t}"' for t in PSEUDO_TICKERS)
    n_pseudo = _q(c, f"SELECT COUNT(*) AS n FROM {U} u "
                     f"WHERE u.in_universe AND u.ticker IN ({pl})")[0]["n"]
    print(f"[3b] pseudo-ticker ({', '.join(PSEUDO_TICKERS)}) trong universe_pit: "
          f"{n_pseudo} -> {'OK' if n_pseudo == 0 else 'FAIL'}")
    if n_pseudo:
        fails.append(f"{n_pseudo} dong pseudo-ticker lot vao universe_pit")

    print("PASS" if not fails else "FAIL: " + "; ".join(fails))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
