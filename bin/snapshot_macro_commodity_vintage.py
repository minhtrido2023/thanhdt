#!/usr/bin/env python3
"""
snapshot_macro_commodity_vintage.py — chụp vintage HẰNG NGÀY (forward-only, append-only) cho
`tav2_bq.macro_indicator` và `tav2_bq.commodity_prices`.

VÌ SAO: 2 bảng nguồn bị ghi đè tại chỗ (`fetched_at` đổi mỗi lần scrape, giá trị bị revise) ⇒ không
có "ngày ta BIẾT giá trị này" ⇒ không làm được nghiên cứu point-in-time. Bảng này BẮT ĐẦU tích luỹ
vintage từ ngày chạy đầu tiên; KHÔNG phải lịch sử (job Winston_20261119_090441, REPORT.md §5-A1).

KHUÔN: giống `snapshot_corp_action_daily.py` — dataset `tav2_mike` (ngoài tầm TRUNCATE của bq_admin),
mỗi bảng đúng MỘT câu `INSERT ... SELECT` (nguyên tử), idempotent theo partition `snapshot_date`
(đã có dòng ⇒ SKIP), không bao giờ UPDATE/DELETE, cổng row-depth ≥90% so với snapshot trước,
fail-closed + báo Discord `architecture` kèm exception thật (§29).

CỘT: series_key (= series_key macro / metric_key hàng hoá), observation_date, value, unit, source,
snapshot_date (ICT), snapshot_ts (UTC lúc ghi) + giữ nguyên country, name_en, cadence (hàng hoá),
source_fetched_at (= fetched_at của nguồn lúc chụp), extra_json.
Bảng nguồn commodity_prices CÓ khoá (metric_key, source, observation_date) trùng ~15k nhóm (khác cadence) với giá
trị khác nhau ⇒ KHÔNG khử trùng: sao nguyên trạng, mỗi dòng nguồn = 1 dòng vintage.

LỌC: `observation_date <= snapshot_date` (không bao giờ có dòng snapshot_date < observation_date —
dữ liệu "tương lai" nếu có sẽ bị loại và LOG ra số dòng loại; đo 19/11: 0 dòng).

CHẠY
    source wc_env.sh
    python3 mike/bin/snapshot_macro_commodity_vintage.py --dry-run
    python3 mike/bin/snapshot_macro_commodity_vintage.py            # idempotent trong ngày ICT
    --table macro_indicator|commodity_prices|all   --date YYYY-MM-DD (CHỈ cho selfcheck/scratch)
Env: VINTAGE_SNAP_SUFFIX (vd `_selfcheck`) để selfcheck ghi bảng scratch, KHÔNG chạm bảng thật.
EXIT: 0 OK (kể cả SKIP) · 1 ≥1 bảng lỗi (không ghi một phần).
"""
import os
os.environ.pop("BQ_LOCAL_CACHE", None)   # LIVE BQ, không qua cache local

import argparse
import datetime as dt
import subprocess
import sys
import traceback
from zoneinfo import ZoneInfo

from google.cloud import bigquery
from google.cloud.bigquery import SchemaField, TimePartitioning, TimePartitioningType

ADC_PATH = "/home/trido/thanhdt/gcloud_dtienthanh/application_default_credentials.json"
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", ADC_PATH)

PROJECT = "lithe-record-440915-m9"
LOCATION = "asia-southeast1"
SRC_DATASET = "tav2_bq"
SNAP_DATASET = os.environ.get("SNAPSHOT_DATASET", "tav2_mike")
SUFFIX = os.environ.get("VINTAGE_SNAP_SUFFIX", "")
ICT = ZoneInfo("Asia/Ho_Chi_Minh")          # §16
MIN_ROW_RATIO = float(os.environ.get("SNAPSHOT_MIN_ROW_RATIO", "0.90"))
USD_PER_TB = 6.25
NOTIFY_TOPIC = "architecture"
HERE = os.path.dirname(os.path.abspath(__file__))

# (tên cột đích, kiểu, biểu thức SELECT từ bảng nguồn)
COMMON_TAIL = [("observation_date", "DATE", "observation_date"), ("value", "FLOAT", "value"),
               ("unit", "STRING", "unit"), ("source", "STRING", "source")]
SPECS = [
    {"src": "macro_indicator", "snap": "macro_indicator_vintage",
     "cols": [("series_key", "STRING", "series_key"), ("country", "STRING", "country"),
              ("name_en", "STRING", "name_en"), ("cadence", "STRING", "CAST(NULL AS STRING)")] + COMMON_TAIL
     + [("source_fetched_at", "TIMESTAMP", "fetched_at"), ("extra_json", "STRING", "extra_json")]},
    {"src": "commodity_prices", "snap": "commodity_prices_vintage",
     "cols": [("series_key", "STRING", "metric_key"), ("country", "STRING", "CAST(NULL AS STRING)"),
              ("name_en", "STRING", "name_en"), ("cadence", "STRING", "cadence")] + COMMON_TAIL
     + [("source_fetched_at", "TIMESTAMP", "fetched_at"), ("extra_json", "STRING", "extra_json")]},
]


def log(m):
    print(m, flush=True)


def ict_today():
    return dt.datetime.now(ICT).date()          # §16 — neo ICT tường minh


def snap_schema(spec):
    return ([SchemaField(n, t) for n, t, _ in spec["cols"]] +
            [SchemaField("snapshot_date", "DATE", mode="REQUIRED",
                         description="Ngay ICT chup trang thai bang nguon (khong phai ngay quan sat)"),
             SchemaField("snapshot_ts", "TIMESTAMP", mode="REQUIRED", description="UTC luc ghi")])


def insert_sql(spec, src_ref, snap_ref, sd):
    names = ", ".join(f"`{n}`" for n, _, _ in spec["cols"])
    exprs = ", ".join(e for _, _, e in spec["cols"])
    return (f"INSERT INTO `{snap_ref}` ({names}, `snapshot_date`, `snapshot_ts`)\n"
            f"SELECT {exprs}, DATE '{sd}', CURRENT_TIMESTAMP()\nFROM `{src_ref}`\n"
            f"WHERE observation_date <= DATE '{sd}'")


def q(client, sql, dry=False):
    job = client.query(sql, job_config=bigquery.QueryJobConfig(dry_run=dry, use_query_cache=False))
    return job, (None if dry else list(job.result()))


def scalar(client, sql):
    return list(q(client, sql)[1][0].values())[0]


def ensure_table(client, spec, snap_ref, dry):
    try:
        return client.get_table(snap_ref)
    except Exception:
        pass
    if dry:
        log(f"  [dry-run] bang {snap_ref} CHUA TON TAI — se tao (partition snapshot_date, cluster series_key)")
        return None
    t = bigquery.Table(snap_ref, schema=snap_schema(spec))
    t.time_partitioning = TimePartitioning(type_=TimePartitioningType.DAY, field="snapshot_date")
    t.clustering_fields = ["series_key"]
    t.description = ("Vintage hang ngay, append-only, forward-only cua tav2_bq." + spec["src"] +
                     " (nguon bi ghi de tai cho). Dong dau tien = snapshot 2026-11-19, KHONG phai lich su. "
                     "Writer: mike/bin/snapshot_macro_commodity_vintage.py. KHONG UPDATE/DELETE.")
    client.create_table(t)
    log(f"  [init] da tao {snap_ref}")
    return client.get_table(snap_ref)


def run_one(client, spec, sd, dry):
    src_ref = f"{PROJECT}.{SRC_DATASET}.{spec['src']}"
    snap_ref = f"{PROJECT}.{SNAP_DATASET}.{spec['snap']}{SUFFIX}"
    log(f"\n=== {spec['src']} -> {SNAP_DATASET}.{spec['snap']}{SUFFIX} ===")
    src_total = int(scalar(client, f"SELECT COUNT(*) FROM `{src_ref}`"))
    src_n = int(scalar(client, f"SELECT COUNT(*) FROM `{src_ref}` WHERE observation_date <= DATE '{sd}'"))
    log(f"  nguon        : {src_total:,} dong, {src_n:,} co observation_date <= {sd} "
        f"(loai {src_total - src_n:,} dong tuong lai)")
    tbl = ensure_table(client, spec, snap_ref, dry)
    already, prev = 0, None
    if tbl is not None:
        already = int(scalar(client, f"SELECT COUNT(*) FROM `{snap_ref}` WHERE snapshot_date = DATE '{sd}'"))
        _, pr = q(client, f"SELECT snapshot_date d, COUNT(*) n FROM `{snap_ref}` "
                          f"WHERE snapshot_date < DATE '{sd}' GROUP BY 1 ORDER BY 1 DESC LIMIT 1")
        prev = (pr[0]["d"], int(pr[0]["n"])) if pr else None
    log(f"  snapshot truoc: {prev[0]} · {prev[1]:,} dong" if prev else "  snapshot truoc: (chua co) — lan dau")
    if already:
        log(f"  SKIP         : snapshot_date={sd} DA CO {already:,} dong (idempotent)")
        return {"table": spec["src"], "action": "skip", "rows": already, "scanned": 0}
    if prev and prev[1] > 0:
        ratio = src_n / prev[1]
        if ratio < MIN_ROW_RATIO:
            raise RuntimeError(f"ABORT ROW_DEPTH: nguon {src_n:,} dong = {ratio:.1%} cua snapshot {prev[0]} "
                               f"({prev[1]:,}), nguong {MIN_ROW_RATIO:.0%}. Co the dang chup giua luc nguon rebuild.")
        log(f"  row-depth    : {ratio:.1%} OK")
    sql = insert_sql(spec, src_ref, snap_ref, sd)
    if dry:
        job, _ = q(client, sql.replace(f"`{snap_ref}`", f"`{snap_ref}`"), dry=True) if tbl is not None else (None, None)
        scanned = int(job.total_bytes_processed or 0) if job is not None else \
            int(client.get_table(src_ref).num_bytes)
        log(f"  [dry-run] se append {src_n:,} dong · quet {scanned/1e6:.1f} MB ~ ${scanned/1e12*USD_PER_TB:.5f}/lan")
        return {"table": spec["src"], "action": "dry-run", "rows": src_n, "scanned": scanned}
    job, _ = q(client, sql)                                  # ĐÚNG 1 câu DML ⇒ nguyên tử
    wrote = int(job.num_dml_affected_rows or 0)
    chk = int(scalar(client, f"SELECT COUNT(*) FROM `{snap_ref}` WHERE snapshot_date = DATE '{sd}'"))
    log(f"  INSERT       : {wrote:,} dong · quet {int(job.total_bytes_processed or 0)/1e6:.1f} MB · job {job.job_id}")
    if chk != wrote or wrote == 0 or abs(src_n - wrote) > max(50, 0.001 * src_n):
        # nguồn có thể được nạp thêm giữa lúc đếm và ghi ⇒ cho dung sai 0,1%; lệch hơn ⇒ báo người
        raise RuntimeError(f"VERIFY FAIL: partition {sd} co {chk:,}, INSERT {wrote:,}, nguon {src_n:,}. Kiem tra tay.")
    log(f"  verify       : partition {sd} = {chk:,} dong, nguon {src_n:,} OK")
    return {"table": spec["src"], "action": "insert", "rows": wrote, "scanned": int(job.total_bytes_processed or 0)}


def notify(msg):
    try:
        p = subprocess.run([os.path.join(HERE, "notify_thread.sh"), msg, NOTIFY_TOPIC],
                           capture_output=True, text=True, timeout=90)
        return p.returncode == 0, f"rc={p.returncode} {p.stderr.strip()[-300:]}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def main(argv=None):
    ap = argparse.ArgumentParser(description="vintage hang ngay macro_indicator + commodity_prices")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--date")
    ap.add_argument("--table", choices=[s["src"] for s in SPECS] + ["all"], default="all")
    a = ap.parse_args(argv)
    sd = dt.date.fromisoformat(a.date) if a.date else ict_today()
    specs = SPECS if a.table == "all" else [s for s in SPECS if s["src"] == a.table]
    log(f"snapshot_macro_commodity_vintage · snapshot_date={sd} (ICT) · dataset={SNAP_DATASET}{SUFFIX} · dry_run={a.dry_run}")
    res, fails = [], []
    try:
        client = bigquery.Client(project=PROJECT, location=LOCATION)
    except Exception as e:
        log(f"FAIL BQ client: {type(e).__name__}: {e}")
        return 1
    for s in specs:
        try:
            res.append(run_one(client, s, sd, a.dry_run))
        except Exception as e:
            log(f"\nFAIL {s['src']} (fail-closed): {type(e).__name__}: {e}")
            traceback.print_exc()
            fails.append({"table": s["src"], "error": f"{type(e).__name__}: {e}"})
    log("\n--- tong ket ---")
    for r in res:
        log(f"  {r['table']:<18} {r['action']:<8} {r['rows']:>8,} dong")
    for f in fails:
        log(f"  {f['table']:<18} FAIL")
    if not fails:
        return 0
    if not a.dry_run and not SUFFIX:
        lines = [f"🛠️ snapshot_macro_commodity_vintage FAIL · snapshot_date={sd} (ICT) · {len(fails)} bang loi"]
        lines += [f"❌ {f['table']}: {f['error'][:700]}" for f in fails]
        lines += [f"✅ {r['table']}: {r['action']} {r['rows']:,} dong" for r in res]
        lines.append("Vintage bang loi CHUA ghi; chay lai KHONG kem --date. Log: mike/logs/snapshot_macro_commodity_vintage.log")
        ok, d = notify("\n".join(lines))
        if not ok:
            log(f"NOTIFY_FAILED {d}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
