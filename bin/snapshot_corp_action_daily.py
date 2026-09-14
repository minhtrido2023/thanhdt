#!/usr/bin/env python3
"""
snapshot_corp_action_daily.py — snapshot TIẾN-TỚI (forward-only) cho 2 bảng vendor bị upsert in-place.

VẤN ĐỀ ĐANG GIẢI
    `tav2_bq.corporate_action` và `tav2_bq.insider_transaction` là SNAPSHOT TRẠNG THÁI, không phải
    event-log. Khi 1 sự kiện lật `Đăng ký` → `Đã thực hiện xong`, ETL vendor ghi đè `public_date`
    (+ nhiều field khác) TẠI CHỖ trên cùng `id` ⇒ ngày công bố Ý ĐỊNH mất VĨNH VIỄN.
    Đây là lý do Sprint 1 (corp_action_program_20260815) CẤM mọi announcement study.
    Bảng này KHÔNG phục hồi được lịch sử; nó chỉ bắt đầu tích luỹ vintage TỪ NGÀY CHẠY ĐẦU TIÊN.

    Bằng chứng ghi đè (đo thật 2026-08-17, không phải suy luận): trong batch ingest gần nhất,
    corporate_action rewrite 1.331 dòng thì 1.185 dòng có `public_date` < 2026-08-01 (cũ nhất
    2024-09-13); insider_transaction rewrite 1.332 dòng thì 1.154 dòng là dòng cũ. ⇒ vendor sửa
    dòng LỊCH SỬ mỗi lần chạy, không chỉ append dòng mới.

CƠ CHẾ
    Mỗi ngày append TOÀN BỘ bảng nguồn vào bảng snapshot append-only, gắn `snapshot_date` (ICT) +
    `row_sha256` (hash nội dung để dò amendment sau này). Ghi bằng ĐÚNG MỘT câu `INSERT ... SELECT`
    ⇒ nguyên tử ở tầng BQ, không thể partial-write (§5 coding_guidelines).

    `row_sha256` = TO_HEX(SHA256(TO_JSON_STRING(STRUCT(<mọi cột nguồn TRỪ HASH_EXCLUDE>)))).
    LOẠI `ingested_at` khỏi hash CÓ CHỦ ĐÍCH: nó là dấu vết pipeline, không phải nội dung sự kiện.
    Đo thật: vendor chỉ chạm ~1.3k dòng/lần refresh (không rewrite cả bảng) nên `ingested_at`
    CÓ tương quan với thay đổi thật — nhưng nếu vendor rewrite 1 dòng với nội dung y hệt thì hash
    có `ingested_at` sẽ báo "amendment" giả. Hash phải đo NỘI DUNG. `ingested_at` vẫn được LƯU
    nguyên trong bảng snapshot nên không mất thông tin nào.

DATASET — CỐ Ý KHÔNG PHẢI `tav2_bq` (đọc trước khi đổi)
    Mặc định ghi vào `tav2_mike`, KHÔNG phải `tav2_bq` như phác thảo ban đầu. Lý do: `tav2_bq` là
    dataset của bq_admin và ĐÃ CÓ tiền lệ WRITE_TRUNCATE + rebuild xoá sạch lịch sử
    (`kb/data_registry/price-volume/ticker_prune.md` §2026-07-29: 58 mã biến mất khỏi TOÀN BỘ
    lịch sử). Bảng này là tài sản KHÔNG TÁI TẠO ĐƯỢC — mất 1 lần là mất 12-18 tháng tích luỹ, không
    có đường backfill. `tav2_mike` chính là dataset được dựng để nằm ngoài tầm TRUNCATE đó
    (xem `build_universe_pit.py`). Muốn đổi: `SNAPSHOT_DATASET=tav2_bq`, nhưng nên đọc mục
    "Rủi ro dataset" trong design doc trước.

CHẠY
    source /home/trido/thanhdt/WorkingClaude/wc_env.sh
    python3 mike/bin/snapshot_corp_action_daily.py --dry-run      # kiểm schema + ước phí, KHÔNG ghi
    python3 mike/bin/snapshot_corp_action_daily.py                # ghi thật (idempotent trong ngày)
    python3 mike/bin/snapshot_corp_action_daily.py --table corporate_action
    python3 mike/bin/snapshot_corp_action_daily.py --date 2026-08-17

EXIT CODE
    0 = OK (kể cả SKIP vì hôm nay đã snapshot) · 1 = ít nhất 1 bảng lỗi (fail-closed, KHÔNG ghi một
    phần). Mỗi bảng chạy CÔ LẬP: lỗi bảng này không chặn bảng kia (2 bảng độc lập, mỗi bảng ghi
    đúng 1 câu DML). Có bảng lỗi + không phải --dry-run ⇒ post Discord topic `architecture` kèm
    exception thật (§29) — trước 2026-09-15 lỗi chỉ nằm trong log cron, không ai đọc.

Design doc: mike/agents/Taylor/research/corp_action_snapshot_pipeline_design_20260817.md
"""

import os
# LIVE BigQuery — pop TRƯỚC mọi import có thể chạm cache local.
os.environ.pop("BQ_LOCAL_CACHE", None)

import argparse
import datetime as dt
import subprocess
import sys
import traceback
from zoneinfo import ZoneInfo

from google.cloud import bigquery
from google.cloud.bigquery import SchemaField, TimePartitioning, TimePartitioningType

# ── config ───────────────────────────────────────────────────────────────────
ADC_PATH = "/home/trido/thanhdt/gcloud_dtienthanh/application_default_credentials.json"
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", ADC_PATH)

PROJECT = "lithe-record-440915-m9"
LOCATION = "asia-southeast1"
SRC_DATASET = "tav2_bq"
# Xem docstring "DATASET" — mặc định KHÔNG phải tav2_bq, có chủ đích.
SNAPSHOT_DATASET = os.environ.get("SNAPSHOT_DATASET", "tav2_mike")

ICT = ZoneInfo("Asia/Ho_Chi_Minh")          # §16: neo timezone tường minh, không tin TZ của host

# Cột KHÔNG vào hash nội dung. Vẫn được LƯU nguyên trong bảng snapshot.
#   - ingested_at: dấu vết pipeline, không phải nội dung sự kiện (docstring đầu file).
#   - source_news_id, first_disclosure_datetime: vendor THÊM vào corporate_action ~2026-09-13
#     (vị trí 34-35, trước ingested_at). Loại khỏi hash để `row_sha256` SO ĐƯỢC LIÊN TỤC qua mốc
#     schema đổi: hash vintage ≤09-13 phủ đúng 34 cột cũ; nếu 2 cột mới vào hash thì MỌI dòng
#     (~36k) sẽ trông như "vừa amend" ở vintage đầu tiên sau mốc — đúng loại amendment giả bảng
#     này sinh ra để tránh. Revision của 2 cột này vẫn dò được bằng LAG() trên chính cột đã lưu.
#     Bảng không có cột này (insider_transaction) thì exclude là no-op.
#     Quyết định A′ — bus question corp-action-snapshot-schema-drift-20260914.
HASH_EXCLUDE = ("ingested_at", "source_news_id", "first_disclosure_datetime")
META_COLS = ("snapshot_date", "row_sha256")

# Cổng chống chụp giữa lúc vendor TRUNCATE+INSERT: nguồn co dưới tỉ lệ này so với snapshot gần
# nhất ⇒ ABORT, không ghi. Tiền lệ thật: `bq_pin_snapshots.md` — pin rơi giữa TRUNCATE...INSERT
# chụp phải bảng rỗng. Snapshot sai vintage là VĨNH VIỄN nên phải fail-closed.
MIN_ROW_RATIO = float(os.environ.get("SNAPSHOT_MIN_ROW_RATIO", "0.90"))

# Đơn giá ƯỚC TÍNH (chưa đối chiếu billing console — dùng để so bậc độ lớn, không phải hoá đơn).
USD_PER_TB_SCANNED = 6.25
USD_PER_GB_MONTH_ACTIVE = 0.02

SPECS = [
    {"src": "corporate_action", "snap": "corporate_action_snapshots"},
    {"src": "insider_transaction", "snap": "insider_transaction_snapshots"},
]

# Topic lỗi theo TÊN (registry kb/discord_channels.json) — cùng topic với corp_action_feed_canary.
NOTIFY_TOPIC = "architecture"
HERE = os.path.dirname(os.path.abspath(__file__))


def log(msg):
    print(msg, flush=True)


def ict_today():
    """Ngày lịch ICT. §16 — KHÔNG bao giờ dùng datetime.now() trần."""
    return dt.datetime.now(ICT).date()


# ── SQL builders ─────────────────────────────────────────────────────────────
def hash_columns(src_cols):
    """Cột đi vào row_sha256: mọi cột nguồn TRỪ HASH_EXCLUDE, giữ nguyên thứ tự bảng nguồn."""
    return [c for c in src_cols if c not in HASH_EXCLUDE]


def row_hash_sql(src_cols):
    """Biểu thức SHA256 nội dung 1 dòng.

    TO_JSON_STRING(STRUCT(...)) được chọn vì: null-safe (NULL → `null`, không lẫn với chuỗi rỗng),
    delimiter-safe (JSON tự escape, không cần ký tự phân cách "chắc không xuất hiện trong data"),
    và mang theo TÊN cột nên hash tự mô tả tập cột nó phủ.
    """
    cols = ", ".join(f"`{c}`" for c in hash_columns(src_cols))
    return f"TO_HEX(SHA256(TO_JSON_STRING(STRUCT({cols}))))"


def insert_sql(src_ref, snap_ref, src_cols, snapshot_date):
    cols = ", ".join(f"`{c}`" for c in src_cols)
    return (
        f"INSERT INTO `{snap_ref}` ({cols}, `snapshot_date`, `row_sha256`)\n"
        f"SELECT {cols}, DATE '{snapshot_date.isoformat()}', {row_hash_sql(src_cols)}\n"
        f"FROM `{src_ref}`"
    )


# ── BQ helpers ───────────────────────────────────────────────────────────────
def get_client():
    return bigquery.Client(project=PROJECT, location=LOCATION)


def run_query(client, sql, dry_run=False):
    cfg = bigquery.QueryJobConfig(dry_run=dry_run, use_query_cache=False)
    job = client.query(sql, job_config=cfg)
    if dry_run:
        return job, None
    return job, list(job.result())


def scalar(client, sql):
    _, rows = run_query(client, sql)
    return list(rows[0].values())[0] if rows else None


def snapshot_schema(src_schema):
    """Schema bảng snapshot = schema nguồn (nguyên vẹn) + snapshot_date + row_sha256."""
    return list(src_schema) + [
        SchemaField("snapshot_date", "DATE", mode="REQUIRED",
                    description="Ngay ICT quan sat trang thai bang nguon (khong phai ngay su kien)"),
        SchemaField("row_sha256", "STRING", mode="REQUIRED",
                    description=f"SHA256 noi dung dong (moi cot nguon TRU {', '.join(HASH_EXCLUDE)})"),
    ]


def ensure_snapshot_table(client, snap_ref, src_schema, dry_run):
    """Trả (exists_before, table_or_None). Dry-run KHÔNG tạo gì."""
    try:
        return True, client.get_table(snap_ref)
    except Exception:
        pass
    if dry_run:
        log(f"  [dry-run] bang {snap_ref} CHUA TON TAI — se tao (partition snapshot_date, cluster ticker,id)")
        return False, None
    tbl = bigquery.Table(snap_ref, schema=snapshot_schema(src_schema))
    tbl.time_partitioning = TimePartitioning(type_=TimePartitioningType.DAY, field="snapshot_date")
    tbl.clustering_fields = ["ticker", "id"]
    tbl.description = (
        "Snapshot tien-toi (forward-only, append-only) cua bang nguon cung ten trong tav2_bq. "
        "1 dong = trang thai 1 su kien NHU QUAN SAT DUOC vao snapshot_date. Bang nguon bi upsert "
        "in-place (public_date bi ghi de khi su kien lat trang thai) nen day la nguon point-in-time "
        "DUY NHAT. KHONG BACKFILL DUOC. Writer: mike/bin/snapshot_corp_action_daily.py"
    )
    client.create_table(tbl)
    log(f"  [init] da tao bang {snap_ref}")
    return False, client.get_table(snap_ref)


def schema_problems(src_schema, snap_table):
    """So khớp schema nguồn vs bảng snapshot theo TÊN→KIỂU. Trả list mô tả lệch (rỗng = khớp).

    CỐ Ý fail-closed thay vì tự evolve schema: thêm/bớt cột nguồn làm ĐỔI TẬP CỘT VÀO HASH ⇒ mọi
    dòng sẽ trông như "vừa bị amend" ở snapshot kế tiếp, làm hỏng chính thứ bảng này sinh ra để đo.
    Lệch schema là quyết định của người, không phải của cron. Vẫn báo: thiếu cột, thừa cột, lệch
    kiểu, thiếu cột meta.

    BỎ QUA THỨ TỰ cột (A′, 2026-09-15): `ALTER TABLE ADD COLUMN` chỉ nối được vào CUỐI bảng (sau
    snapshot_date/row_sha256), còn vendor chèn cột mới vào GIỮA ⇒ so thứ tự nghiêm ngặt khiến
    không có đường DDL nào qua được cổng. Thứ tự không ảnh hưởng tính đúng: `insert_sql` gọi tên
    cột tường minh, và hash lấy thứ tự từ bảng NGUỒN (`hash_columns(src_cols)`), không từ bảng
    snapshot.
    """
    src = {f.name: f.field_type for f in src_schema}
    snap = {f.name: f.field_type for f in snap_table.schema if f.name not in META_COLS}
    snap_meta = {f.name for f in snap_table.schema if f.name in META_COLS}

    probs = []
    missing = [n for n in src if n not in snap]
    extra = [n for n in snap if n not in src]
    retyped = [f"{n}: nguon={src[n]} snapshot={snap[n]}" for n in src if n in snap and src[n] != snap[n]]
    if missing:
        probs.append(f"cot CO o nguon nhung THIEU o snapshot: {missing}")
    if extra:
        probs.append(f"cot CO o snapshot nhung KHONG con o nguon: {extra}")
    if retyped:
        probs.append(f"cot LECH KIEU: {retyped}")
    for m in META_COLS:
        if m not in snap_meta:
            probs.append(f"thieu cot meta `{m}`")
    return probs


# ── 1 bảng ───────────────────────────────────────────────────────────────────
def run_one(client, spec, snapshot_date, dry_run):
    """Snapshot 1 bảng. Trả dict kết quả. Ném exception ⇒ caller fail-closed."""
    src_ref = f"{PROJECT}.{SRC_DATASET}.{spec['src']}"
    snap_ref = f"{PROJECT}.{SNAPSHOT_DATASET}.{spec['snap']}"
    log(f"\n=== {spec['src']} -> {SNAPSHOT_DATASET}.{spec['snap']} ===")

    src_tbl = client.get_table(src_ref)
    src_schema = list(src_tbl.schema)
    src_cols = [f.name for f in src_schema]
    src_rows = int(src_tbl.num_rows)
    src_bytes = int(src_tbl.num_bytes)
    log(f"  nguon        : {src_rows:,} dong · {src_bytes/1e6:.1f} MB · {len(src_cols)} cot")
    log(f"  hash phu     : {len(hash_columns(src_cols))} cot (loai: {', '.join(HASH_EXCLUDE)})")

    existed, snap_tbl = ensure_snapshot_table(client, snap_ref, src_schema, dry_run)

    if snap_tbl is not None:
        probs = schema_problems(src_schema, snap_tbl)
        if probs:
            raise RuntimeError(
                f"SCHEMA LECH giua {src_ref} va {snap_ref}:\n    - " + "\n    - ".join(probs) +
                "\n  KHONG tu dong evolve (doi tap cot = doi tap cot vao hash = moi dong trong nhu "
                "vua amend). Can nguoi quyet dinh: hoac them cot vao bang snapshot va ghi ro "
                "vintage doi hash trong data_registry, hoac dung pipeline."
            )
        log("  schema       : KHOP (cot nguon trung khop ten+kieu + du 2 cot meta; thu tu khong so)")

    # ── idempotency: hôm nay đã có dòng nào chưa
    already = 0
    prev_rows = None
    if existed or snap_tbl is not None:
        already = int(scalar(
            client,
            f"SELECT COUNT(*) FROM `{snap_ref}` WHERE snapshot_date = DATE '{snapshot_date.isoformat()}'"
        ) or 0)
        _, prows = run_query(client, (
            f"SELECT snapshot_date, COUNT(*) AS n FROM `{snap_ref}` "
            f"WHERE snapshot_date < DATE '{snapshot_date.isoformat()}' "
            f"GROUP BY 1 ORDER BY 1 DESC LIMIT 1"
        ))
        if prows:
            prev_rows = (prows[0]["snapshot_date"], int(prows[0]["n"]))

    if prev_rows:
        log(f"  snapshot truoc: {prev_rows[0]} · {prev_rows[1]:,} dong")
    else:
        log("  snapshot truoc: (chua co) — day la lan chay dau tien")

    if already > 0:
        log(f"  SKIP         : snapshot_date={snapshot_date} DA CO {already:,} dong (idempotent, khong ghi lai)")
        return {"table": spec["src"], "action": "skip", "rows": already, "bytes_scanned": 0}

    # ── cổng chống chụp giữa lúc vendor rebuild
    if prev_rows and prev_rows[1] > 0:
        ratio = src_rows / prev_rows[1]
        if ratio < MIN_ROW_RATIO:
            raise RuntimeError(
                f"ABORT ROW_DEPTH: nguon co {src_rows:,} dong = {ratio:.1%} cua snapshot "
                f"{prev_rows[0]} ({prev_rows[1]:,} dong), nguong {MIN_ROW_RATIO:.0%}. "
                "Nhieu kha nang dang chup giua luc vendor TRUNCATE+INSERT. KHONG ghi."
            )
        log(f"  row-depth    : {ratio:.1%} so voi snapshot truoc (nguong {MIN_ROW_RATIO:.0%}) OK")

    sql = insert_sql(src_ref, snap_ref, src_cols, snapshot_date)

    if dry_run:
        if snap_tbl is not None:
            job, _ = run_query(client, sql, dry_run=True)
            scanned = int(job.total_bytes_processed or 0)
            src_note = "do bang dry-run DML that"
        else:
            scanned = src_bytes
            src_note = "uoc tu num_bytes bang nguon (bang snapshot chua ton tai, khong dry-run DML duoc)"
        log(f"  [dry-run] se append : {src_rows:,} dong vao snapshot_date={snapshot_date}")
        log(f"  [dry-run] quet      : {scanned/1e6:.1f} MB ({src_note}) "
            f"~ ${scanned/1e12*USD_PER_TB_SCANNED:.5f}/lan")
        log(f"  [dry-run] storage   : +{src_bytes/1e6:.1f} MB/ngay ~ {src_bytes*365/1e9:.2f} GB/nam "
            f"~ ${src_bytes*365/1e9*USD_PER_GB_MONTH_ACTIVE*12/2:.2f}/nam dau (logical, trung binh tich luy)")
        log("  [dry-run] KHONG ghi gi.")
        return {"table": spec["src"], "action": "dry-run", "rows": src_rows, "bytes_scanned": scanned}

    # ── ghi thật: ĐÚNG 1 câu DML ⇒ nguyên tử, không có trạng thái ghi-một-nửa
    job, _ = run_query(client, sql)
    scanned = int(job.total_bytes_processed or 0)
    written = int(job.num_dml_affected_rows or 0)
    log(f"  INSERT       : {written:,} dong · quet {scanned/1e6:.1f} MB "
        f"~ ${scanned/1e12*USD_PER_TB_SCANNED:.5f} · job {job.job_id}")

    # ── verify sau ghi (đừng tin self-report của job)
    check = int(scalar(
        client,
        f"SELECT COUNT(*) FROM `{snap_ref}` WHERE snapshot_date = DATE '{snapshot_date.isoformat()}'"
    ) or 0)
    if check != src_rows:
        raise RuntimeError(
            f"VERIFY FAIL: partition {snapshot_date} co {check:,} dong nhung nguon co {src_rows:,}. "
            "Bang snapshot dang o trang thai KHONG khop — kiem tra tay truoc khi chay lai."
        )
    log(f"  verify       : partition {snapshot_date} = {check:,} dong == nguon OK")
    return {"table": spec["src"], "action": "insert", "rows": written, "bytes_scanned": scanned}


# ── main ─────────────────────────────────────────────────────────────────────
def default_notifier(msg):
    """(ok, detail). Topic theo TÊN qua registry `kb/discord_channels.json`."""
    try:
        p = subprocess.run([os.path.join(HERE, "notify_thread.sh"), msg, NOTIFY_TOPIC],
                           capture_output=True, text=True, timeout=90)
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"
    return p.returncode == 0, f"rc={p.returncode} stderr={p.stderr.strip()[-300:]}"


def failure_message(snapshot_date, failures, results):
    """Tin lỗi cho người. Chỉ trích exception THẬT đã bắt được (§29) — không đoán nguyên nhân."""
    lines = [f"🛠️ snapshot_corp_action_daily FAIL · snapshot_date={snapshot_date} (ICT) · "
             f"{len(failures)} bang loi, {len(results)} bang OK"]
    for f in failures:
        lines.append(f"❌ {f['table']}: {f['error'][:700]}")
    for r in results:
        lines.append(f"✅ {r['table']}: {r['action']} {r['rows']:,} dong")
    lines.append("Vintage bang loi CHUA ghi — bang nguon bi upsert in-place nen moi ngay khong ghi la mat "
                 "vinh vien. Chay lai KHONG kem --date (--date ngay cu se dong dau trang thai HIEN TAI "
                 "voi nhan ngay cu). Log: mike/logs/snapshot_corp_action_YYYYMM.log")
    return "\n".join(lines)


def main(argv=None, client_factory=None, notifier=default_notifier):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true",
                    help="kiem schema + uoc phi + in ke hoach, KHONG ghi BQ")
    ap.add_argument("--date", help="snapshot_date (YYYY-MM-DD), mac dinh = hom nay ICT")
    ap.add_argument("--table", choices=[s["src"] for s in SPECS] + ["all"], default="all")
    args = ap.parse_args(argv)

    snapshot_date = dt.date.fromisoformat(args.date) if args.date else ict_today()
    specs = SPECS if args.table == "all" else [s for s in SPECS if s["src"] == args.table]

    log(f"snapshot_corp_action_daily · snapshot_date={snapshot_date} (ICT) · "
        f"dataset={SNAPSHOT_DATASET} · dry_run={args.dry_run}")

    results, failures = [], []
    try:
        client = (client_factory or get_client)()
    except Exception as e:
        client = None
        log(f"\nFAIL tao BQ client: {type(e).__name__}: {e}")
        traceback.print_exc()
        failures = [{"table": s["src"], "error": f"tao BQ client: {type(e).__name__}: {e}"} for s in specs]

    # Cô lập từng bảng: 2 bảng độc lập, mỗi bảng đúng 1 DML ⇒ lỗi bảng này không được giết vintage
    # của bảng kia (run 2026-09-14: corporate_action lệch schema kéo insider_transaction chết theo).
    for s in specs if client is not None else []:
        try:
            results.append(run_one(client, s, snapshot_date, args.dry_run))
        except Exception as e:
            log(f"\nFAIL {s['src']} (fail-closed, khong ghi mot phan): {type(e).__name__}: {e}")
            traceback.print_exc()
            failures.append({"table": s["src"], "error": f"{type(e).__name__}: {e}"})

    log("\n--- tong ket ---")
    for r in results:
        log(f"  {r['table']:<22} {r['action']:<8} {r['rows']:>8,} dong  "
            f"quet {r['bytes_scanned']/1e6:.1f} MB")
    for f in failures:
        log(f"  {f['table']:<22} FAIL")
    if not failures:
        return 0

    if args.dry_run:
        log("(dry-run: khong post Discord)")
        return 1
    ok, detail = notifier(failure_message(snapshot_date, failures, results))
    if not ok:
        log(f"NOTIFY_FAILED topic={NOTIFY_TOPIC} {detail}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
