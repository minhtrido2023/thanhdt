#!/usr/bin/env python3
"""
build_universe_pit.py — builder cho bảng universe point-in-time `universe_pit`.

Nguồn thiết kế: `mike/agents/Taylor/research/ticker_prune_replacement_plan.md` §3.1-§3.4
(user duyệt Q1-Q9 ngày 2026-07-22). Job G1.

MỤC ĐÍCH
    Thay `tav2_bq.ticker_prune` (non-reproducible, circular selection bias, look-ahead 2,74×)
    bằng một bảng universe do đội Mike sở hữu: append-only, bất biến, tính CHỈ từ cột thô
    point-in-time của `tav2_bq.ticker`, KHÔNG đọc `ticker_prune` ở bất kỳ đâu.

BỘ TIÊU CHÍ v1 (ruleset_version = 1) — §3.2
    B1  ICB_Code IS NOT NULL                     (loại pseudo-ticker chỉ số)
    B2  tuổi >= 60 phiên kể từ dòng đầu trong `ticker`
    B3  VÀO: median trading value 60 phiên >= 1,0 tỷ VND thực (neo 2026)
        - trading value TỰ TÍNH từ COALESCE(Price, Close) * Volume  (KHÔNG dùng cột dựng
          sẵn `Volume_3M_P50` của ETL ngoài — §3.2b)
        - khử lạm phát bằng chính cột `Inflation_7` (fallback 1,07^(year-2026))
        - ngưỡng 1e9 = hằng số production `filter.json:18`, KHÔNG hiệu chuẩn lại (Q2)
    B4  RA: trading value < 0,5 tỷ thực trong 20 phiên LIÊN TIẾP (max20 < 0,5e9)
    B5  Close >= 1.000 VND
    B6  Loại cứng: vắng >= 10 phiên liên tiếp trong `ticker` (delist/đình chỉ)
    B7  Đã bị loại thì phải đủ điều kiện B3 lại từ đầu (chống nhấp nháy)
    B8  Integrity gate — §3.3, xem hàm check_b8()

ĐỌC LIVE, KHÔNG QUA CACHE
    `BQ_LOCAL_CACHE` bị pop process-local ngay đầu file (Winston §4 Câu 1): cache sync 23:45
    ⇒ luôn T-1, và về cấu trúc không thấy được dòng lịch sử bị viết lại.

DATASET
    Ghi vào `lithe-record-440915-m9.tav2_mike.universe_pit` — dataset RIÊNG của đội Mike, KHÔNG
    phải `tav2_bq`. Lý do: script của bq_admin dùng WRITE_TRUNCATE trên `tav2_bq` ("chỉ chạy 1
    lần để initial" nhưng vẫn kích hoạt lại thủ công được — đã xảy ra 07-12). Bảng bất biến của
    ta không được nằm trong tầm với của một lệnh TRUNCATE ta không kiểm soát.

CÁCH DÙNG
    python3 build_universe_pit.py                      # 1 ngày = ngày mới nhất trong `ticker`
    python3 build_universe_pit.py --date 2026-06-15
    python3 build_universe_pit.py --backfill           # toàn bộ lịch sử tới ngày mới nhất
    python3 build_universe_pit.py --date ... --dry-run # tính + chạy B8, KHÔNG ghi
"""

import os
# LIVE BigQuery — phải pop TRƯỚC mọi import có thể chạm cache (coding_guidelines §11).
os.environ.pop("BQ_LOCAL_CACHE", None)

import argparse
import datetime as dt
import hashlib
import json
import statistics
import sys

from google.cloud import bigquery
from google.cloud.bigquery import SchemaField, TimePartitioning, TimePartitioningType

# ── config ───────────────────────────────────────────────────────────────────
WORKDIR = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")
ADC_PATH = "/home/trido/thanhdt/gcloud_dtienthanh/application_default_credentials.json"
PROJECT = "lithe-record-440915-m9"
SRC_TABLE = f"{PROJECT}.tav2_bq.ticker"
DATASET = os.environ.get("UNIVERSE_PIT_DATASET", "tav2_mike")
TABLE = os.environ.get("UNIVERSE_PIT_TABLE", "universe_pit")
LOCATION = "asia-southeast1"
RULESET_VERSION = 1
ARTIFACT_DIR = os.path.join(WORKDIR, "data", "universe_pit")

# tham số bộ tiêu chí (hằng số production — KHÔNG tune, xem Q2/§8.4)
ENTER_THRESHOLD_VND = 1.0e9      # B3
EXIT_THRESHOLD_VND = 0.5e9       # B4
ENTER_WINDOW = 60                # B3 (phiên)
EXIT_WINDOW = 20                 # B4 (phiên)
MIN_AGE_SESSIONS = 60            # B2
MIN_CLOSE_VND = 1000.0           # B5
MAX_ABSENT_SESSIONS = 10         # B6

# B8
B8_COUNT_DEV = 0.15              # lệch số mã in_universe so trung vị 20 ngày
B8_RAW_DEPTH = 0.90              # số dòng thô `ticker` so trung vị 20 ngày
B8_LOOKBACK = 20

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", ADC_PATH)

SCHEMA = [
    SchemaField("time", "DATE", mode="REQUIRED"),
    SchemaField("ticker", "STRING", mode="REQUIRED"),
    SchemaField("in_universe", "BOOL", mode="REQUIRED"),
    SchemaField("reason", "STRING", mode="REQUIRED"),
    SchemaField("ruleset_version", "INT64", mode="REQUIRED"),
    SchemaField("backfilled", "BOOL", mode="REQUIRED"),
    SchemaField("computed_at", "TIMESTAMP", mode="REQUIRED"),
]


# ── SQL ──────────────────────────────────────────────────────────────────────
def membership_sql(select_cols: str, day_filter: str) -> str:
    """State machine B1-B7 trên toàn lịch sử <= @asof; `day_filter` giới hạn dòng XUẤT RA.

    Máy trạng thái viết bằng thủ thuật LAST_VALUE(... IGNORE NULLS): mỗi phiên phát ra
    TRUE (đủ điều kiện vào), FALSE (phải ra) hoặc NULL (giữ nguyên trạng thái trước) —
    nên B7 ("bị loại phải đủ điều kiện lại từ đầu") tự động đúng, không cần vòng lặp.
    """
    return f"""
WITH cal AS (
  SELECT time, ROW_NUMBER() OVER (ORDER BY time) AS d_rn
  FROM (SELECT DISTINCT time FROM `{SRC_TABLE}` WHERE time <= @asof)
),
base AS (
  SELECT t.time, t.ticker,
         t.ICB_Code IS NOT NULL AS has_icb,
         t.Close AS close,
         SAFE_DIVIDE(COALESCE(t.Price, t.Close) * t.Volume,
                     COALESCE(NULLIF(t.Inflation_7, 0),
                              POW(1.07, EXTRACT(YEAR FROM t.time) - 2026))) AS tv_real
  FROM `{SRC_TABLE}` t
  WHERE t.time <= @asof
),
j AS (SELECT b.*, c.d_rn FROM base b JOIN cal c USING (time)),
w AS (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY d_rn) AS age_sessions,
    d_rn - LAG(d_rn) OVER (PARTITION BY ticker ORDER BY d_rn) - 1 AS gap_sessions,
    ARRAY_AGG(IFNULL(tv_real, 0)) OVER (PARTITION BY ticker ORDER BY d_rn
      ROWS BETWEEN {ENTER_WINDOW - 1} PRECEDING AND CURRENT ROW) AS win_enter,
    MAX(IFNULL(tv_real, 0)) OVER (PARTITION BY ticker ORDER BY d_rn
      ROWS BETWEEN {EXIT_WINDOW - 1} PRECEDING AND CURRENT ROW) AS tv_max_exit,
    COUNT(1) OVER (PARTITION BY ticker ORDER BY d_rn
      ROWS BETWEEN {EXIT_WINDOW - 1} PRECEDING AND CURRENT ROW) AS n_exit
  FROM j
),
m AS (
  SELECT * EXCEPT(win_enter),
    ARRAY_LENGTH(win_enter) AS n_enter,
    (SELECT IF(MOD(ARRAY_LENGTH(s), 2) = 1,
               s[OFFSET(DIV(ARRAY_LENGTH(s), 2))],
               (s[OFFSET(DIV(ARRAY_LENGTH(s), 2) - 1)] + s[OFFSET(DIV(ARRAY_LENGTH(s), 2))]) / 2)
     FROM (SELECT ARRAY_AGG(x ORDER BY x) AS s FROM UNNEST(win_enter) x)) AS med_enter
  FROM w
),
f AS (
  SELECT *,
    (has_icb AND age_sessions >= {MIN_AGE_SESSIONS} AND n_enter = {ENTER_WINDOW}
     AND IFNULL(close, 0) >= {MIN_CLOSE_VND} AND med_enter >= {ENTER_THRESHOLD_VND}) AS can_enter,
    (IFNULL(gap_sessions, 0) >= {MAX_ABSENT_SESSIONS} OR NOT has_icb
     OR IFNULL(close, 0) < {MIN_CLOSE_VND}
     OR (n_exit = {EXIT_WINDOW} AND tv_max_exit < {EXIT_THRESHOLD_VND})) AS must_exit
  FROM m
),
st AS (
  SELECT *,
    LAST_VALUE(CASE WHEN must_exit THEN FALSE WHEN can_enter THEN TRUE ELSE NULL END
               IGNORE NULLS)
      OVER (PARTITION BY ticker ORDER BY d_rn ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
      AS state
  FROM f
),
final AS (
  SELECT time, ticker,
    IFNULL(state, FALSE) AS in_universe,
    CASE
      WHEN IFNULL(gap_sessions, 0) >= {MAX_ABSENT_SESSIONS} THEN 'EXIT_GAP'
      WHEN NOT has_icb THEN 'EXIT_NO_ICB'
      WHEN IFNULL(close, 0) < {MIN_CLOSE_VND} THEN 'EXIT_PRICE'
      WHEN n_exit = {EXIT_WINDOW} AND tv_max_exit < {EXIT_THRESHOLD_VND} THEN 'EXIT_LIQ'
      WHEN can_enter THEN 'ENTER'
      WHEN IFNULL(state, FALSE) THEN 'CARRY_IN'
      WHEN age_sessions < {MIN_AGE_SESSIONS} THEN 'PENDING_AGE'
      ELSE 'PENDING_LIQ'
    END AS reason,
    can_enter, med_enter
  FROM st
)
SELECT {select_cols} FROM final WHERE {day_filter}
"""


def _q(client, sql, params=None):
    cfg = bigquery.QueryJobConfig(query_parameters=params or [])
    return list(client.query(sql, job_config=cfg, location=LOCATION).result())


# ── B8 integrity gate (§3.3) — hàm THUẦN để selfcheck được ────────────────────
def check_b8(n_in, prev_in_counts, raw_rows, prev_raw_counts, existing_rows,
             enforce_deviation=True):
    """Trả về list vi phạm (rỗng = pass). Thuần: không I/O, unit-test được.

    - existing_rows > 0   → LUÔN chặn (chống double-append, coding_guidelines §5)
    - lệch số mã in_universe > ±15% so trung vị <=20 ngày trước → chặn
    - số dòng thô `ticker` < 90% trung vị <=20 ngày trước → chặn
    Hai gate sau chỉ áp khi có đủ mẫu tham chiếu (>=5 ngày) và enforce_deviation=True
    (backfill lịch sử: tính + báo cáo nhưng không chặn — universe 2000-2008 tăng trưởng
    cấu trúc, gate ±15% ngày-qua-ngày không có nghĩa ở đó).
    """
    v = []
    if existing_rows:
        v.append(f"B8_DUPLICATE: da co {existing_rows} dong cho ngay nay trong universe_pit")
    if enforce_deviation and len(prev_in_counts) >= 5:
        med = statistics.median(prev_in_counts)
        if med > 0 and abs(n_in / med - 1.0) > B8_COUNT_DEV:
            v.append(f"B8_COUNT_DEV: n_in={n_in} lech {n_in/med-1:+.1%} so trung vi {med:.0f} "
                     f"({len(prev_in_counts)} ngay truoc), nguong ±{B8_COUNT_DEV:.0%}")
    if enforce_deviation and len(prev_raw_counts) >= 5:
        medr = statistics.median(prev_raw_counts)
        if medr > 0 and raw_rows / medr < B8_RAW_DEPTH:
            v.append(f"B8_RAW_DEPTH: `ticker` co {raw_rows} dong = {raw_rows/medr:.1%} trung vi "
                     f"{medr:.0f}, nguong {B8_RAW_DEPTH:.0%}")
    return v


# ── helpers ──────────────────────────────────────────────────────────────────
def get_client():
    return bigquery.Client(project=PROJECT, location=LOCATION)


def ensure_table(client):
    ds_ref = bigquery.DatasetReference(PROJECT, DATASET)
    try:
        client.get_dataset(ds_ref)
    except Exception:
        ds = bigquery.Dataset(ds_ref)
        ds.location = LOCATION
        ds.description = "Mike-owned tables (universe_pit). KHONG nam trong tam TRUNCATE cua bq_admin."
        client.create_dataset(ds)
        print(f"  [init] tao dataset {DATASET}")
    ref = f"{PROJECT}.{DATASET}.{TABLE}"
    try:
        client.get_table(ref)
    except Exception:
        tbl = bigquery.Table(ref, schema=SCHEMA)
        tbl.time_partitioning = TimePartitioning(type_=TimePartitioningType.DAY, field="time")
        tbl.clustering_fields = ["ticker"]
        tbl.description = ("Universe point-in-time, append-only, ruleset v1. "
                           "Nguon: tav2_bq.ticker (LIVE). KHONG doc ticker_prune.")
        client.create_table(tbl)
        print(f"  [init] tao bang {ref}")
    return ref


def latest_source_date(client):
    return _q(client, f"SELECT MAX(time) AS d FROM `{SRC_TABLE}`")[0]["d"]


def atomic_write_json(path, obj):
    """tmp + os.replace — kill giữa chừng không để lại file dở dang (guidelines §5)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2, default=str)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def membership_sha(tickers):
    """SHA của tập membership (§3.4) — thứ lẽ ra đã bắt được drift ngay lập tức."""
    return hashlib.sha256(",".join(sorted(tickers)).encode()).hexdigest()


# ── build 1 ngày ─────────────────────────────────────────────────────────────
def build_day(client, target_ref, day, asof, dry_run=False):
    p_asof = [bigquery.ScalarQueryParameter("asof", "DATE", asof),
              bigquery.ScalarQueryParameter("day", "DATE", day)]

    # (1) trạng thái hiện có + tham chiếu cho B8 — đọc từ chính BQ (source of truth)
    existing = _q(client, f"SELECT COUNT(*) AS n FROM `{target_ref}` WHERE time = @day",
                  [bigquery.ScalarQueryParameter("day", "DATE", day)])[0]["n"]
    prev_in = [r["n"] for r in _q(
        client,
        f"SELECT time, COUNTIF(in_universe) AS n FROM `{target_ref}` WHERE time < @day "
        f"GROUP BY time ORDER BY time DESC LIMIT {B8_LOOKBACK}",
        [bigquery.ScalarQueryParameter("day", "DATE", day)])]
    prev_raw = [r["n"] for r in _q(
        client,
        f"SELECT time, COUNT(*) AS n FROM `{SRC_TABLE}` WHERE time < @day "
        f"GROUP BY time ORDER BY time DESC LIMIT {B8_LOOKBACK}",
        [bigquery.ScalarQueryParameter("day", "DATE", day)])]
    raw_rows = _q(client, f"SELECT COUNT(*) AS n FROM `{SRC_TABLE}` WHERE time = @day",
                  [bigquery.ScalarQueryParameter("day", "DATE", day)])[0]["n"]

    # (2) tính membership ngày đó
    rows = _q(client, membership_sql("time, ticker, in_universe, reason", "time = @day"), p_asof)
    n_in = sum(1 for r in rows if r["in_universe"])
    in_tickers = [r["ticker"] for r in rows if r["in_universe"]]

    # (3) B8
    viol = check_b8(n_in, prev_in, raw_rows, prev_raw, existing)
    print(f"  [{day}] n_rows={len(rows)} n_in={n_in} raw_ticker_rows={raw_rows} "
          f"prev_ref={len(prev_in)}d existing={existing}")
    if viol:
        for x in viol:
            print(f"  ✗ {x}", file=sys.stderr)
        return {"date": str(day), "status": "REFUSED", "violations": viol,
                "n_in": n_in, "n_rows": len(rows)}
    if not rows:
        return {"date": str(day), "status": "NO_DATA", "n_in": 0, "n_rows": 0}

    art = {"date": str(day), "asof": str(asof), "ruleset_version": RULESET_VERSION,
           "n_rows": len(rows), "n_in_universe": n_in,
           "membership_sha256": membership_sha(in_tickers),
           "raw_ticker_rows": raw_rows, "backfilled": False,
           "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}

    if dry_run:
        art["status"] = "DRY_RUN"
        print(f"  [dry-run] khong ghi. sha={art['membership_sha256'][:16]}")
        return art

    # (4) INSERT (side-effect duy nhất, đặt CUỐI cùng; job BQ atomic — all-or-nothing)
    ins = f"""
INSERT INTO `{target_ref}` (time, ticker, in_universe, reason, ruleset_version, backfilled, computed_at)
{membership_sql(f"time, ticker, in_universe, reason, {RULESET_VERSION} AS ruleset_version, "
                f"FALSE AS backfilled, CURRENT_TIMESTAMP() AS computed_at", "time = @day")}
"""
    job = client.query(ins, job_config=bigquery.QueryJobConfig(query_parameters=p_asof),
                       location=LOCATION)
    job.result()
    art["status"] = "APPENDED"
    art["inserted_rows"] = job.num_dml_affected_rows
    atomic_write_json(os.path.join(ARTIFACT_DIR, f"build_{day}.json"), art)
    print(f"  ✓ appended {job.num_dml_affected_rows} dong · sha={art['membership_sha256'][:16]}")
    return art


# ── backfill toàn lịch sử ────────────────────────────────────────────────────
def build_backfill(client, target_ref, asof, dry_run=False):
    """Backfill theo LÔ NĂM — BQ chỉ cho 1 lệnh DML chạm <=4000 partition, lịch sử có ~6.339 ngày.

    Resumable & idempotent theo cấu trúc: mỗi lô chỉ ghi `time > MAX(time) đang có`, nên
    chạy lại sau khi bị kill giữa chừng sẽ tiếp tục đúng chỗ, không bao giờ ghi trùng.
    """
    if dry_run:
        rows = _q(client, membership_sql(
            "time, COUNTIF(in_universe) AS n_in, COUNT(*) AS n_rows", "TRUE GROUP BY time"),
            [bigquery.ScalarQueryParameter("asof", "DATE", asof)])
        print(f"  [dry-run] {len(rows)} ngay, "
              f"tong {sum(r['n_rows'] for r in rows)} dong, "
              f"tong in_universe {sum(r['n_in'] for r in rows)}")
        return {"status": "DRY_RUN", "n_days": len(rows)}

    total = 0
    for year in range(2000, asof.year + 1):
        done = _q(client, f"SELECT MAX(time) AS d FROM `{target_ref}`")[0]["d"]
        lo = dt.date(year, 1, 1)
        hi = min(dt.date(year, 12, 31), asof)
        if done is not None and done >= hi:
            continue
        if done is not None and done >= lo:
            lo = done + dt.timedelta(days=1)
        ins = f"""
INSERT INTO `{target_ref}` (time, ticker, in_universe, reason, ruleset_version, backfilled, computed_at)
{membership_sql(f"time, ticker, in_universe, reason, {RULESET_VERSION} AS ruleset_version, "
                f"TRUE AS backfilled, CURRENT_TIMESTAMP() AS computed_at",
                "time BETWEEN @lo AND @hi")}
"""
        job = client.query(ins, job_config=bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("asof", "DATE", asof),
            bigquery.ScalarQueryParameter("lo", "DATE", lo),
            bigquery.ScalarQueryParameter("hi", "DATE", hi)]), location=LOCATION)
        job.result()
        total += job.num_dml_affected_rows or 0
        print(f"  [{year}] {lo}..{hi}  +{job.num_dml_affected_rows} dong (cong don {total})")

    n = total
    art = {"status": "BACKFILLED", "asof": str(asof), "inserted_rows": n,
           "ruleset_version": RULESET_VERSION,
           "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    atomic_write_json(os.path.join(ARTIFACT_DIR, f"backfill_{asof}.json"), art)
    print(f"  ✓ backfill {n} dong toi {asof}")
    return art


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", help="YYYY-MM-DD (mac dinh: ngay moi nhat trong tav2_bq.ticker)")
    ap.add_argument("--backfill", action="store_true", help="dung toan bo lich su (bang phai rong)")
    ap.add_argument("--dry-run", action="store_true", help="tinh + chay B8, KHONG ghi")
    args = ap.parse_args()

    client = get_client()
    target_ref = ensure_table(client)
    asof = latest_source_date(client)
    print(f"[build_universe_pit] src={SRC_TABLE} (LIVE) latest={asof} target={target_ref} "
          f"ruleset_v{RULESET_VERSION}")

    if args.backfill:
        res = build_backfill(client, target_ref, asof, dry_run=args.dry_run)
    else:
        day = dt.date.fromisoformat(args.date) if args.date else asof
        # asof = chính ngày đó: máy trạng thái chỉ nhìn thấy dữ liệu <= day ⇒ point-in-time
        # đúng theo cấu trúc, không phải theo lời hứa.
        res = build_day(client, target_ref, day, day, dry_run=args.dry_run)

    print(json.dumps(res, ensure_ascii=False, default=str))
    return 0 if res.get("status") in ("APPENDED", "BACKFILLED", "DRY_RUN", "NO_DATA") else 1


if __name__ == "__main__":
    sys.exit(main())
