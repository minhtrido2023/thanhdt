#!/usr/bin/env python3
"""
build_universe_pit_quality.py — cờ chất lượng ex-ante đi kèm `universe_pit` (Q-C, §3.2b).

QUYẾT ĐỊNH GỐC (user chốt 2026-07-22, job Taylor_20260722_062405): **A′ + Q-C**.
    A′ = sàn thanh khoản riêng của consumer (custom30V ≥13,1 tỷ, CAPIT ≥2 tỷ) được tính là lớp
         chặn chất lượng hợp lệ ⇒ KHÔNG sửa B1-B8 của `universe_pit`.
    Q-C = xuất CỜ chất lượng để tầng chiến lược/due-diligence tự đọc — **không đổi hành vi chọn
         universe**, chỉ minh bạch hoá. KHÔNG làm Q-B (không thêm ngưỡng ROE vào tầng universe).

VÌ SAO LÀ BẢNG RIÊNG, KHÔNG PHẢI THÊM CỘT VÀO `universe_pit`
    `universe_pit` là bảng BẤT BIẾN, append-only — thêm cột rồi UPDATE 6.300 partition đã ghi là
    đúng thứ ta đang bỏ chạy (dòng lịch sử bị viết lại). Bảng companion giữ `universe_pit` không
    bị chạm một byte nào, đồng thời cho cờ chất lượng có `quality_ruleset_version` RIÊNG: sau này
    đổi định nghĩa chất lượng không kéo theo re-version membership. Consumer đọc qua view
    `universe_pit_q` (LEFT JOIN sẵn) nên vẫn "như một cột".

PHẠM VI DÒNG
    CHỈ các dòng `in_universe = TRUE` (~1,46M/4,09M). Cờ chất lượng của một mã không nằm trong
    universe là vô nghĩa với mọi consumer.

NGUỒN (đúng 3 nguồn đã dùng ở G2b — KHÔNG thêm nguồn mới)
    1. `tav2_bq.ticker.ROE_Min3Y`        — dòng cùng ngày (point-in-time theo cấu trúc)
    2. `tav2_bq.ticker_financial.CF_OA_3Y` — as-of quý gần nhất <= ngày, hiệu lực tối đa 400 ngày
    3. `tav2_bq.fa_ratings_8l`           — panel 8L as-of (CANONICAL, kb/data_registry/rating-8l/fa_ratings_8l.md)
    + BANNED list (hằng số dưới, = danh sách trong `context_pack.md`)

CỜ (`quality_flag`) — thứ tự ưu tiên, loại trừ nhau:
    BANNED          mã trong danh sách cấm vĩnh viễn
    UNKNOWN_FLOOR   thiếu ROE_Min3Y hoặc CF_OA_3Y as-of ⇒ không kết luận được
    FLOOR_FAIL      có dữ liệu nhưng trượt golden floor (ROE_Min3Y >= 0 ∧ CF_OA_3Y > 0)
    UNKNOWN_RATING  qua floor nhưng chưa có rating 8L as-of (vd trước 2014-07-09 panel chưa bắt đầu)
    RATING_FAIL     qua floor, rating 8L as-of > 3
    QUALITY_OK      qua cả 3: không banned ∧ qua floor ∧ rating <= 3

    `QUALITY_OK` = ĐÚNG định nghĩa "leak" của G2b ⇒ selfcheck tái lập được 45/77/61 (2018/2022/2026).
    ⚠️ Cờ này KHÔNG chặn gì cả. Nó không đổi `in_universe`, không đổi rổ, không đổi lệnh.

CÁCH DÙNG
    python3 build_universe_pit_quality.py --backfill        # toàn bộ lịch sử đã có trong universe_pit
    python3 build_universe_pit_quality.py --date 2026-07-21
    python3 build_universe_pit_quality.py --date ... --dry-run
"""

import os
# LIVE BigQuery — pop TRƯỚC mọi import chạm cache (coding_guidelines §11).
os.environ.pop("BQ_LOCAL_CACHE", None)

import argparse
import datetime as dt
import json
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google.cloud import bigquery
from google.cloud.bigquery import SchemaField, TimePartitioning, TimePartitioningType

from build_universe_pit import (  # tái dùng, không copy
    ADC_PATH, ARTIFACT_DIR, DATASET, LOCATION, PROJECT, SRC_TABLE, TABLE,
    atomic_write_json, get_client, _q, _run_dml,
)

QTABLE = os.environ.get("UNIVERSE_PIT_QUALITY_TABLE", "universe_pit_quality")
QVIEW = os.environ.get("UNIVERSE_PIT_QUALITY_VIEW", "universe_pit_q")
QUALITY_RULESET_VERSION = 1
JOB_SUFFIX = os.environ.get("UNIVERSE_PIT_QUALITY_JOB_SUFFIX", "")
BACKFILL_CHUNK_DAYS = 3500       # BigQuery: 1 DML chạm tối đa 4000 partition
FIN_VALID_DAYS = 400             # CF_OA_3Y as-of hết hiệu lực sau 400 ngày (giống G2b)

BANNED = ["PC1", "VVS", "KSF", "NKG", "HSG", "HVN", "VJC", "NVL", "GEG", "SBA",
          "DMC", "IMP", "TRA", "TOS", "VTP"]

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", ADC_PATH)

QSCHEMA = [
    SchemaField("time", "DATE", mode="REQUIRED"),
    SchemaField("ticker", "STRING", mode="REQUIRED"),
    SchemaField("quality_flag", "STRING", mode="REQUIRED"),
    SchemaField("banned", "BOOL", mode="REQUIRED"),
    SchemaField("pass_golden_floor", "BOOL", mode="REQUIRED"),
    SchemaField("roe_min3y", "FLOAT64"),
    SchemaField("cf_oa_3y", "FLOAT64"),
    SchemaField("rating_8l", "FLOAT64"),
    SchemaField("rating_asof", "DATE"),
    SchemaField("quality_ruleset_version", "INT64", mode="REQUIRED"),
    SchemaField("computed_at", "TIMESTAMP", mode="REQUIRED"),
]


def quality_sql(select_cols: str) -> str:
    """Cờ chất lượng cho các dòng in_universe trong khoảng @lo..@hi."""
    upit = f"`{PROJECT}.{DATASET}.{TABLE}`"
    banned_lit = ",".join(f'"{b}"' for b in BANNED)
    return f"""
WITH U AS (
  SELECT u.time, u.ticker FROM {upit} u
  WHERE u.in_universe AND u.time BETWEEN @lo AND @hi
),
R AS (
  SELECT t.time, t.ticker, t.ROE_Min3Y FROM `{SRC_TABLE}` t
  WHERE t.time BETWEEN @lo AND @hi
),
FQ AS (
  SELECT ticker, time AS f_time, CF_OA_3Y,
         LEAD(time) OVER (PARTITION BY ticker ORDER BY time) AS f_next
  FROM `{PROJECT}.tav2_bq.ticker_financial`
),
RT AS (
  SELECT ticker, time AS r_time, rating,
         LEAD(time) OVER (PARTITION BY ticker ORDER BY time) AS r_next
  FROM `{PROJECT}.tav2_bq.fa_ratings_8l`
),
J AS (
  SELECT U.time, U.ticker,
         R.ROE_Min3Y AS roe_min3y,
         FQ.CF_OA_3Y AS cf_oa_3y,
         CAST(RT.rating AS FLOAT64) AS rating_8l,
         RT.r_time AS rating_asof,
         U.ticker IN ({banned_lit}) AS banned
  FROM U
  LEFT JOIN R ON R.time = U.time AND R.ticker = U.ticker
  LEFT JOIN FQ ON FQ.ticker = U.ticker AND U.time >= FQ.f_time
              AND (FQ.f_next IS NULL OR U.time < FQ.f_next)
              AND U.time <= DATE_ADD(FQ.f_time, INTERVAL {FIN_VALID_DAYS} DAY)
  LEFT JOIN RT ON RT.ticker = U.ticker AND U.time >= RT.r_time
              AND (RT.r_next IS NULL OR U.time < RT.r_next)
),
F AS (
  SELECT J.*,
    (roe_min3y IS NOT NULL AND roe_min3y >= 0 AND cf_oa_3y IS NOT NULL AND cf_oa_3y > 0)
      AS pass_golden_floor
  FROM J
),
final AS (
  SELECT time, ticker, banned, pass_golden_floor, roe_min3y, cf_oa_3y, rating_8l, rating_asof,
    CASE
      WHEN banned THEN 'BANNED'
      WHEN roe_min3y IS NULL OR cf_oa_3y IS NULL THEN 'UNKNOWN_FLOOR'
      WHEN NOT pass_golden_floor THEN 'FLOOR_FAIL'
      WHEN rating_8l IS NULL THEN 'UNKNOWN_RATING'
      WHEN rating_8l > 3 THEN 'RATING_FAIL'
      ELSE 'QUALITY_OK'
    END AS quality_flag
  FROM F
)
SELECT {select_cols} FROM final
"""


def ensure_qtable(client):
    ref = f"{PROJECT}.{DATASET}.{QTABLE}"
    try:
        client.get_table(ref)
    except Exception:
        tbl = bigquery.Table(ref, schema=QSCHEMA)
        tbl.time_partitioning = TimePartitioning(type_=TimePartitioningType.DAY, field="time")
        tbl.clustering_fields = ["ticker"]
        tbl.description = ("Co chat luong ex-ante di kem universe_pit (Q-C, quality ruleset v1). "
                           "CHI dong in_universe=TRUE. KHONG doi hanh vi chon universe.")
        client.create_table(tbl)
        print(f"  [init] tao bang {ref}")
    return ref


def ensure_view(client):
    """View tiện dụng: membership + cờ chất lượng trong một chỗ (consumer đọc như 1 bảng)."""
    ref = f"{PROJECT}.{DATASET}.{QVIEW}"
    sql = f"""
SELECT u.time, u.ticker, u.in_universe, u.reason, u.ruleset_version,
       q.quality_flag, q.banned, q.pass_golden_floor, q.rating_8l, q.rating_asof,
       q.quality_ruleset_version
FROM `{PROJECT}.{DATASET}.{TABLE}` u
LEFT JOIN `{PROJECT}.{DATASET}.{QTABLE}` q ON q.time = u.time AND q.ticker = u.ticker
"""
    v = bigquery.Table(ref)
    v.view_query = sql
    v.description = ("universe_pit + quality_flag. quality_flag NULL <=> in_universe FALSE "
                     "(co chat luong chi tinh cho dong in_universe).")
    try:
        client.get_table(ref)
        client.update_table(v, ["view_query", "description"])
    except Exception:
        client.create_table(v)
        print(f"  [init] tao view {ref}")
    return ref


def build_range(client, qref, lo, hi, dry_run=False, tag=""):
    params = [bigquery.ScalarQueryParameter("lo", "DATE", lo),
              bigquery.ScalarQueryParameter("hi", "DATE", hi)]
    existing = _q(client, f"SELECT COUNT(*) AS n FROM `{qref}` WHERE time BETWEEN @lo AND @hi",
                  params)[0]["n"]
    if existing:
        print(f"  [skip] {lo}..{hi} da co {existing} dong — KHONG ghi de (append-only)")
        return {"status": "SKIP_EXISTING", "lo": str(lo), "hi": str(hi), "existing": existing}

    if dry_run:
        rows = _q(client, f"SELECT quality_flag, COUNT(*) AS n FROM ("
                          f"{quality_sql('time, ticker, quality_flag')}) "
                          f"GROUP BY quality_flag ORDER BY n DESC", params)
        dist = {r["quality_flag"]: r["n"] for r in rows}
        print(f"  [dry-run] {lo}..{hi} phan bo co: {dist}")
        return {"status": "DRY_RUN", "lo": str(lo), "hi": str(hi), "dist": dist}

    ins = f"""
INSERT INTO `{qref}` (time, ticker, quality_flag, banned, pass_golden_floor, roe_min3y, cf_oa_3y,
                      rating_8l, rating_asof, quality_ruleset_version, computed_at)
{quality_sql("time, ticker, quality_flag, banned, pass_golden_floor, roe_min3y, cf_oa_3y, "
             f"rating_8l, rating_asof, {QUALITY_RULESET_VERSION} AS quality_ruleset_version, "
             "CURRENT_TIMESTAMP() AS computed_at")}
"""
    job = _run_dml(client, ins, params,
                   f"upitq_v{QUALITY_RULESET_VERSION}{JOB_SUFFIX}_{tag}_{lo}_{hi}")
    n = job.num_dml_affected_rows or 0
    print(f"  ✓ {lo}..{hi}  +{n} dong", flush=True)
    return {"status": "APPENDED", "lo": str(lo), "hi": str(hi), "inserted_rows": n}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", help="YYYY-MM-DD (mac dinh: ngay moi nhat trong universe_pit)")
    ap.add_argument("--backfill", action="store_true", help="toan bo lich su co trong universe_pit")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    client = get_client()
    upit = f"{PROJECT}.{DATASET}.{TABLE}"
    qref = ensure_qtable(client)
    print(f"[build_universe_pit_quality] src={upit} target={qref} qruleset_v{QUALITY_RULESET_VERSION}")

    if args.backfill:
        days = [r["d"] for r in _q(
            client, f"SELECT DISTINCT time AS d FROM `{upit}` WHERE in_universe ORDER BY d")]
        chunks = [(days[i], days[min(i + BACKFILL_CHUNK_DAYS, len(days)) - 1])
                  for i in range(0, len(days), BACKFILL_CHUNK_DAYS)]
        print(f"  {len(days)} phien -> {len(chunks)} lo")
        res = {"status": "BACKFILLED", "chunks": []}
        for ci, (lo, hi) in enumerate(chunks):
            r = build_range(client, qref, lo, hi, dry_run=args.dry_run, tag=f"c{ci}")
            res["chunks"].append(r)
            if r["status"] not in ("APPENDED", "SKIP_EXISTING", "DRY_RUN"):
                res["status"] = "FAILED"
                break
        if args.dry_run:
            res["status"] = "DRY_RUN"
        res["inserted_rows"] = sum(c.get("inserted_rows", 0) for c in res["chunks"])
    else:
        day = (dt.date.fromisoformat(args.date) if args.date
               else _q(client, f"SELECT MAX(time) AS d FROM `{upit}`")[0]["d"])
        res = build_range(client, qref, day, day, dry_run=args.dry_run, tag="day")

    if not args.dry_run:
        ensure_view(client)
        res["quality_ruleset_version"] = QUALITY_RULESET_VERSION
        res["built_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        atomic_write_json(os.path.join(ARTIFACT_DIR, "quality_last_build.json"), res)

    print(json.dumps(res, ensure_ascii=False, default=str))
    return 0 if res.get("status") in ("APPENDED", "BACKFILLED", "DRY_RUN", "SKIP_EXISTING") else 1


if __name__ == "__main__":
    sys.exit(main())
