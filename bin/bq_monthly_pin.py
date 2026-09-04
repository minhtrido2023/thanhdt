#!/usr/bin/env python3
"""bq_monthly_pin.py — monthly BigQuery table PIN (snapshot) + silent-restate detection.

WHY THIS EXISTS (2026-07-29, user directive after 3 restate incidents in one day)
---------------------------------------------------------------------------------
Production BQ tables are rewritten under us with no announcement and no diff:
  * `ticker_prune` was TRUNCATE+rebuilt 2026-07-29 07:27 — 58 tickers vanished from the
    ENTIRE history, not just from today forward.
  * `VNINDEX_PE` was back-filled to 2006 this week (bug fix) — every prior study that read
    that column silently referred to a different series afterwards.
  * corp-action restatement runs continuously, ~2-3% of `ticker`/`ticker_financial` per week.
BQ time-travel on this project is wiped every morning, so an old vintage CANNOT be recovered
after the fact. Every "pinned" backtest result (R3, the DT5G audit, ...) is therefore anchored
to a snapshot nobody can reproduce. All three incidents above were found by ACCIDENT.

This script fixes both halves of that:
  (a) AUDIT TRAIL  — a real, queryable copy of each restate-prone table, once a month, kept
      forever, independent of BQ time travel.
  (b) EARLY WARNING — each new pin is diffed against the previous pin and anything beyond a
      routine restate is alerted, instead of being discovered by luck months later.

MECHANISM — BigQuery table SNAPSHOT (`bq cp --snapshot`), not CSV export:
  * metadata-only, server-side: the 4.8 GB `ticker` table pins in ~10 s;
  * storage is billed only on bytes that DIVERGE from the base table, so an append-only table
    costs ~nothing per pin and a rebuilt one costs at most its own size (see COST below);
  * read-only by construction (a snapshot cannot be written to) => immutable audit evidence;
  * stays a first-class BQ table: `SELECT ... FROM tav2_pin.ticker_pin_202608` just works,
    same schema, same types — a CSV export would lose types and be far more awkward to diff.

NAMING / NAMESPACE (coding_guidelines §8 — never shadow a canonical name):
  pins live in their OWN dataset `tav2_pin`, never in `tav2_bq`/`tav2_mike`, and are named
  `<table>_pin_YYYYMM` where YYYYMM is the ICT month the pin was TAKEN. Cron runs on day 1, so
  `ticker_pin_202608` == "state of `ticker` as at the start of 2026-08" == what every analysis
  run during 2026-08 was reading at the time.

DIFF / ALERT MODEL
  Pins are compared PIN-to-PIN (never pin-to-live) so the comparison is itself reproducible.
  Rows newer than the previous pin's MAX(time) are expected growth and are excluded; only the
  OVERLAP window is compared, per group (`ticker`, or year for tables with no ticker column):
      group disappeared  -> a name was deleted from history      (the ticker_prune failure)
      group appeared     -> back-fill of a name                  (usually benign)
      group restated     -> same key, different bytes            (corp-action / column back-fill)
  Bytes are compared with BIT_XOR(FARM_FINGERPRINT(TO_JSON_STRING(STRUCT(<common cols>)))):
  order-independent, no INT64 overflow (SUM would overflow), and restricted to columns present
  in BOTH pins so that a newly ADDED column does not mass-flag every row as restated. Added and
  removed columns are reported separately as schema drift — a removed column is a hard failure.

SEVERITY (thresholds in THRESH below; tuned to the observed ~2-3%/week corp-action churn)
  CRITICAL — history was destroyed or the shape broke: groups removed >5%, rows in the overlap
             window moved >5%, MIN(time) moved forward (history truncated), a column removed,
             or a pinned table missing entirely.
  WARN     — groups removed 1-5%, or >25% of groups restated (churn well above the usual rate),
             or a column added.
  OK       — routine restatement / pure growth.

Quiet-heartbeat convention: this posts a one-line summary EVERY month even when clean (silence
is indistinguishable from a dead cron), and the full per-table detail only on WARN/CRITICAL.

COST (measured 2026-07-29): full pin set = 6.3 GB logical. Snapshot storage in
asia-southeast1 is ~$0.025/GB/month and is charged only on divergence, so a worst case of one
full extra copy per month is ~$0.16/month/generation — i.e. under $2 for the first year, and
in practice far less because `ticker`/`ticker_financial` are mostly append-only. The compare
queries scan both pins' common columns, ~12 GB/month => ~$0.08/month. RETENTION IS THEREFORE
"KEEP EVERYTHING" — deleting an old pin destroys the only copy of a vintage for a few cents of
saving. Revisit only if `--cost` reports the pin dataset above ~100 GB.

USAGE
  bq_monthly_pin.py                      # pin current ICT month + diff vs previous pin
  bq_monthly_pin.py --dry-run            # show what would happen, no snapshot, no notify
  bq_monthly_pin.py --month 202608       # explicit month label (idempotent: existing pin kept)
  bq_monthly_pin.py --compare-only       # re-run the diff over existing pins, create nothing
  bq_monthly_pin.py --tables ticker,fa_ratings_8l
  bq_monthly_pin.py --selftest           # build a known-broken pair, assert the diff detects it
  bq_monthly_pin.py --cost               # report pin dataset size, no side effects

EXIT CODES: 0 = OK, 1 = CRITICAL, 2 = WARN only, 3 = operational error (snapshot/query failed).
Re-running the same month is a no-op for snapshots already taken (idempotent side effects,
context_safety_core.md) — the diff is recomputed and re-reported, which is harmless.
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
ROOT = "/home/trido/thanhdt/WorkingClaude"
MIKE = os.path.join(ROOT, "mike")
PROJECT = "lithe-record-440915-m9"
PIN_DATASET = "tav2_pin"
LOCATION = "asia-southeast1"
REPORT_DIR = os.path.join(MIKE, "logs", "bq_pin")
DISCORD_STALE_CHANNEL = "trading_daily"   # tên trong kb/discord_channels.json — same target as bq_freshness_check.sh

# ── what gets pinned ──────────────────────────────────────────────────────────────────────
# compare=False => snapshot it, but never diff it: `ticker_1m` is a ROLLING ~1-month window by
# design, so month-over-month "rows disappeared" is its normal behaviour and would be pure
# alert noise. It is still pinned because it is what live screening actually saw that month.
# group: the diff key. 'ticker' wherever the table has one; year buckets for the state series
# (one row per session, no ticker column) so the diff still localises WHERE it changed.
PINS = [
    # (dataset, table, compare, group_expr)
    ("tav2_bq",   "ticker",                          True,  "ticker"),
    ("tav2_bq",   "ticker_prune",                    True,  "ticker"),
    ("tav2_bq",   "ticker_financial",                True,  "ticker"),
    ("tav2_bq",   "ticker_1m",                       False, "ticker"),
    ("tav2_mike", "universe_pit",                    True,  "ticker"),
    ("tav2_mike", "universe_pit_quality",            True,  "ticker"),
    ("tav2_bq",   "vnindex_5state_dt5g_live",        True,  "CAST(EXTRACT(YEAR FROM time) AS STRING)"),
    ("tav2_bq",   "vnindex_5state",                  True,  "CAST(EXTRACT(YEAR FROM time) AS STRING)"),
    ("tav2_bq",   "vnindex_5state_tam_quan_v34b_clean", True, "CAST(EXTRACT(YEAR FROM time) AS STRING)"),
    # fa_ratings*: not in the dispatch list, added because they are the most restate-prone
    # tables we own — the source is DELETE+INSERT re-ranked every week (that is exactly why
    # sync_bq_cache_daily.sh keeps them full_only), and they are ~2 MB, so pinning is free.
    ("tav2_bq",   "fa_ratings_8l",                   True,  "ticker"),
    ("tav2_bq",   "fa_ratings",                      True,  "ticker"),
]

THRESH = {
    "groups_removed_crit_pct": 5.0,
    "groups_removed_warn_pct": 1.0,
    "rows_moved_crit_pct": 5.0,
    "groups_restated_warn_pct": 25.0,
}

OK, WARN, CRIT = "OK", "WARN", "CRITICAL"
RANK = {OK: 0, WARN: 1, CRIT: 2}


def run(cmd, check=True, timeout=900):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if check and p.returncode != 0:
        # `bq` ghi thông điệp lỗi ra STDOUT chứ không phải stderr (kb/incidents/2026-08/
        # 2026-08-29-bq-error-on-stdout-empty-diagnosis.md) => chỉ đọc stderr là được chuỗi RỖNG,
        # người vận hành mù hoàn toàn. Đọc cả hai kênh, ưu tiên kênh nào có nội dung.
        msg = (p.stderr.strip() or p.stdout.strip())[:2000]
        raise RuntimeError(f"cmd failed ({p.returncode}): {' '.join(cmd)}\n{msg}")
    return p


def bq_json(sql):
    """Run a query, return list[dict]. --format=json gives typed-ish JSON (numbers as strings)."""
    p = run(["bq", "query", "--use_legacy_sql=false", "--format=json",
             f"--project_id={PROJECT}", sql])
    out = p.stdout.strip()
    return json.loads(out) if out else []


def ensure_dataset():
    p = run(["bq", "show", "--format=none", f"--project_id={PROJECT}", PIN_DATASET], check=False)
    if p.returncode != 0:
        # check-then-act KHÔNG idempotent: `bq show` fail vì lý do KHÁC "chưa tồn tại"
        # (auth hỏng, mạng) sẽ rơi vào nhánh mk, rồi mk fail "already exists" => crash.
        # Chấp nhận "already exists" như thành công; mọi lỗi khác vẫn raise kèm nguyên văn.
        mk = run(["bq", "mk", f"--location={LOCATION}", "--dataset",
                  "--description", "BQ monthly pin/snapshot archive (audit trail vs silent restates)",
                  f"{PROJECT}:{PIN_DATASET}"], check=False)
        if mk.returncode != 0:
            out = (mk.stderr.strip() or mk.stdout.strip())
            if "already exists" not in out.lower():
                raise RuntimeError(f"ensure_dataset: bq mk failed ({mk.returncode})\n{out[:2000]}")


def list_pins():
    """-> {table: {YYYYMM: pin_table_name}} for everything currently in the pin dataset."""
    p = run(["bq", "ls", "--max_results=10000", "--format=json",
             f"--project_id={PROJECT}", PIN_DATASET], check=False)
    if p.returncode != 0 or not p.stdout.strip():
        return {}
    out = {}
    for t in json.loads(p.stdout):
        name = t["tableReference"]["tableId"]
        m = re.fullmatch(r"(.+)_pin_(\d{6})", name)
        if m:
            out.setdefault(m.group(1), {})[m.group(2)] = name
    return out


def table_exists(dataset, table):
    return run(["bq", "show", "--format=none", f"--project_id={PROJECT}",
                f"{dataset}.{table}"], check=False).returncode == 0


def columns_of(dataset, table):
    p = run(["bq", "show", "--schema", "--format=prettyjson",
             f"--project_id={PROJECT}", f"{dataset}.{table}"], check=False)
    if p.returncode != 0:
        return []
    return [c["name"] for c in json.loads(p.stdout)]


def snapshot(src_dataset, src_table, dst_table, dry_run):
    """Idempotent: an already-existing pin for this month is kept, never re-taken."""
    if table_exists(PIN_DATASET, dst_table):
        return "exists"
    if dry_run:
        return "would-create"
    run(["bq", "cp", "--snapshot", "--no_clobber", f"--project_id={PROJECT}",
         f"{src_dataset}.{src_table}", f"{PIN_DATASET}.{dst_table}"])
    return "created"


# ── diff ──────────────────────────────────────────────────────────────────────────────────
def headline_sql(pin, group_expr):
    return f"""
SELECT COUNT(*) AS n,
       COUNT(DISTINCT {group_expr}) AS ngroups,
       CAST(MIN(time) AS STRING) AS min_time,
       CAST(MAX(time) AS STRING) AS max_time
FROM `{PROJECT}.{PIN_DATASET}.{pin}`"""


def diff_sql(prev_pin, cur_pin, group_expr, common_cols):
    """Compare the two pins over the OVERLAP window only (time <= prev MAX(time)).

    Rows newer than the previous pin are this month's legitimate new data, not a restate, so
    including them would flag every table every month. The fingerprint covers only columns
    present in BOTH pins — a column ADDED between pins is schema drift, reported separately,
    and must not masquerade as "every row changed"."""
    struct = ", ".join(f"`{c}`" for c in common_cols)
    return f"""
WITH
prv_all AS (SELECT * FROM `{PROJECT}.{PIN_DATASET}.{prev_pin}`),
cur_all AS (SELECT * FROM `{PROJECT}.{PIN_DATASET}.{cur_pin}`),
bound   AS (SELECT MAX(time) AS mx FROM prv_all),
prv AS (SELECT * FROM prv_all WHERE time <= (SELECT mx FROM bound)),
cur AS (SELECT * FROM cur_all WHERE time <= (SELECT mx FROM bound)),
a AS (SELECT CAST({group_expr} AS STRING) AS g, COUNT(*) AS n,
             BIT_XOR(FARM_FINGERPRINT(TO_JSON_STRING(STRUCT({struct})))) AS chk
      FROM prv GROUP BY 1),
b AS (SELECT CAST({group_expr} AS STRING) AS g, COUNT(*) AS n,
             BIT_XOR(FARM_FINGERPRINT(TO_JSON_STRING(STRUCT({struct})))) AS chk
      FROM cur GROUP BY 1),
j AS (SELECT a.g AS ag, b.g AS bg, a.n AS an, b.n AS bn, a.chk AS ac, b.chk AS bc
      FROM a FULL OUTER JOIN b ON a.g = b.g)
SELECT
  COUNTIF(ag IS NOT NULL AND bg IS NULL) AS groups_removed,
  COUNTIF(ag IS NULL AND bg IS NOT NULL) AS groups_added,
  COUNTIF(ag IS NOT NULL AND bg IS NOT NULL AND (ac != bc OR an != bn)) AS groups_restated,
  COUNTIF(ag IS NOT NULL AND bg IS NOT NULL AND ac = bc AND an = bn) AS groups_same,
  IFNULL(SUM(an), 0) AS prev_rows_overlap,
  IFNULL(SUM(bn), 0) AS cur_rows_overlap,
  ARRAY_AGG(IF(bg IS NULL, ag, NULL) IGNORE NULLS ORDER BY ag LIMIT 25) AS sample_removed,
  ARRAY_AGG(IF(ag IS NULL, bg, NULL) IGNORE NULLS ORDER BY bg LIMIT 25) AS sample_added,
  ARRAY_AGG(IF(ag IS NOT NULL AND bg IS NOT NULL AND (ac != bc OR an != bn), ag, NULL)
            IGNORE NULLS ORDER BY ag LIMIT 25) AS sample_restated
FROM j"""


def compare(prev_pin, cur_pin, group_expr):
    """-> dict of findings + a severity. Never raises on data content, only on BQ failure."""
    prev_cols, cur_cols = columns_of(PIN_DATASET, prev_pin), columns_of(PIN_DATASET, cur_pin)
    removed_cols = [c for c in prev_cols if c not in cur_cols]
    added_cols = [c for c in cur_cols if c not in prev_cols]
    common = [c for c in prev_cols if c in cur_cols]

    ph = bq_json(headline_sql(prev_pin, group_expr))[0]
    ch = bq_json(headline_sql(cur_pin, group_expr))[0]
    d = bq_json(diff_sql(prev_pin, cur_pin, group_expr, common))[0]

    prev_groups = int(d["groups_removed"]) + int(d["groups_restated"]) + int(d["groups_same"])
    pr, cr = int(d["prev_rows_overlap"]), int(d["cur_rows_overlap"])
    pct = lambda num, den: (100.0 * num / den) if den else 0.0

    res = {
        "prev_pin": prev_pin, "cur_pin": cur_pin,
        "prev": {k: ph[k] for k in ("n", "ngroups", "min_time", "max_time")},
        "cur": {k: ch[k] for k in ("n", "ngroups", "min_time", "max_time")},
        "groups_removed": int(d["groups_removed"]),
        "groups_added": int(d["groups_added"]),
        "groups_restated": int(d["groups_restated"]),
        "groups_same": int(d["groups_same"]),
        "groups_removed_pct": round(pct(int(d["groups_removed"]), prev_groups), 2),
        "groups_restated_pct": round(pct(int(d["groups_restated"]), prev_groups), 2),
        "rows_overlap_prev": pr, "rows_overlap_cur": cr,
        "rows_moved_pct": round(abs(pct(cr - pr, pr)), 2),
        "cols_removed": removed_cols, "cols_added": added_cols,
        "sample_removed": d.get("sample_removed") or [],
        "sample_added": d.get("sample_added") or [],
        "sample_restated": d.get("sample_restated") or [],
        "reasons": [],
    }

    sev = OK
    def bump(level, why):
        nonlocal sev
        res["reasons"].append(f"[{level}] {why}")
        if RANK[level] > RANK[sev]:
            sev = level

    if removed_cols:
        bump(CRIT, f"cột bị XOÁ khỏi schema: {removed_cols}")
    if added_cols:
        bump(WARN, f"cột mới thêm: {added_cols}")
    if res["groups_removed_pct"] > THRESH["groups_removed_crit_pct"]:
        bump(CRIT, f"{res['groups_removed']} nhóm ({res['groups_removed_pct']}%) BIẾN MẤT khỏi lịch sử")
    elif res["groups_removed_pct"] > THRESH["groups_removed_warn_pct"]:
        bump(WARN, f"{res['groups_removed']} nhóm ({res['groups_removed_pct']}%) biến mất khỏi lịch sử")
    elif res["groups_removed"]:
        bump(OK, f"{res['groups_removed']} nhóm biến mất (dưới ngưỡng)")
    if res["rows_moved_pct"] > THRESH["rows_moved_crit_pct"]:
        bump(CRIT, f"số dòng trong cửa sổ chồng lấn đổi {res['rows_moved_pct']}% ({pr}→{cr})")
    # MIN(time) moving FORWARD = history was cut off at the front; moving back = back-fill (fine).
    if ph["min_time"] and ch["min_time"] and ch["min_time"] > ph["min_time"]:
        bump(CRIT, f"MIN(time) tiến lên {ph['min_time']}→{ch['min_time']} (lịch sử bị cắt đầu)")
    if res["groups_restated_pct"] > THRESH["groups_restated_warn_pct"]:
        bump(WARN, f"{res['groups_restated']} nhóm ({res['groups_restated_pct']}%) bị restate")
    elif res["groups_restated"]:
        bump(OK, f"{res['groups_restated']} nhóm restate ({res['groups_restated_pct']}%) — mức thường lệ")

    res["severity"] = sev
    return res


# ── selftest ──────────────────────────────────────────────────────────────────────────────
SELFTEST_A, SELFTEST_B = "zz_selftest_a", "zz_selftest_b"


def selftest():
    """Build a known-broken pin pair and assert the diff finds exactly the planted damage.

    Plants, over an identical base: 1 group deleted from history, 1 group's value changed,
    1 group added, and 1 row appended NEWER than A's max time (must be ignored as growth,
    not counted as a restate). Uses real tables, not mocks — the whole risk in this script is
    that the SQL is subtly wrong, which a mock would not catch."""
    ensure_dataset()
    for t in (SELFTEST_A, SELFTEST_B):
        run(["bq", "rm", "-f", "-t", f"--project_id={PROJECT}", f"{PIN_DATASET}.{t}"], check=False)
    base = f"""
SELECT d AS time, g, v FROM UNNEST([
  STRUCT(DATE '2024-01-01' AS d, 'AAA' AS g, 1 AS v), ('2024-01-02','AAA',2),
  ('2024-01-01','BBB',3), ('2024-01-02','BBB',4),
  ('2024-01-01','CCC',5), ('2024-01-02','CCC',6)])"""
    run(["bq", "query", "--use_legacy_sql=false", f"--project_id={PROJECT}",
         "--destination_table", f"{PIN_DATASET}.{SELFTEST_A}", "--replace", base])
    mutated = f"""
SELECT d AS time, g, v FROM UNNEST([
  STRUCT(DATE '2024-01-01' AS d, 'AAA' AS g, 1 AS v), ('2024-01-02','AAA',2),
  ('2024-01-01','BBB',3), ('2024-01-02','BBB',999),
  ('2024-01-01','DDD',7),
  ('2024-06-01','AAA',8)])"""     # CCC deleted, BBB restated, DDD added, AAA row past A's max
    run(["bq", "query", "--use_legacy_sql=false", f"--project_id={PROJECT}",
         "--destination_table", f"{PIN_DATASET}.{SELFTEST_B}", "--replace", mutated])

    r = compare(SELFTEST_A, SELFTEST_B, "g")
    checks = [
        ("CCC bị xoá được phát hiện", r["groups_removed"] == 1 and r["sample_removed"] == ["CCC"]),
        ("BBB restate được phát hiện", r["groups_restated"] == 1 and r["sample_restated"] == ["BBB"]),
        ("DDD mới được phát hiện", r["groups_added"] == 1 and r["sample_added"] == ["DDD"]),
        ("AAA không đổi", r["groups_same"] == 1),
        # B trong cửa sổ chồng lấn = AAA(2) + BBB(2) + DDD(1) = 5; dòng AAA 2024-06-01 phải bị loại
        ("dòng mới sau max(time) cũ bị loại khỏi so sánh",
         r["rows_overlap_cur"] == 5 and r["rows_overlap_prev"] == 6),
        ("severity leo thang (>5% nhóm mất)", r["severity"] == CRIT),
    ]
    for name, okflag in checks:
        print(f"  {'PASS' if okflag else 'FAIL'}  {name}")
    for t in (SELFTEST_A, SELFTEST_B):
        run(["bq", "rm", "-f", "-t", f"--project_id={PROJECT}", f"{PIN_DATASET}.{t}"], check=False)
    passed = sum(1 for _, o in checks if o)
    print(f"selftest {passed}/{len(checks)}")
    return 0 if passed == len(checks) else 1


def cost_report():
    p = run(["bq", "ls", "--max_results=10000", "--format=json",
             f"--project_id={PROJECT}", PIN_DATASET], check=False)
    names = [t["tableReference"]["tableId"] for t in json.loads(p.stdout or "[]")]
    total = 0
    for n in names:
        s = run(["bq", "show", "--format=prettyjson", f"--project_id={PROJECT}",
                 f"{PIN_DATASET}.{n}"], check=False)
        if s.returncode == 0:
            b = int(json.loads(s.stdout).get("numBytes", 0))
            total += b
            print(f"  {n:55s} {b/1024**3:8.3f} GB")
    print(f"TỔNG {len(names)} pin: {total/1024**3:.2f} GB logical "
          f"(~${total/1024**3*0.025:.2f}/tháng nếu KHÔNG dedup với bảng gốc — thực tế rẻ hơn nhiều)")
    return 0


# ── main ──────────────────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", help="YYYYMM label (default: tháng ICT hiện tại)")
    ap.add_argument("--tables", help="chỉ chạy các bảng này (phân tách bằng dấu phẩy)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--compare-only", action="store_true", help="không tạo pin mới, chỉ diff")
    ap.add_argument("--no-notify", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--cost", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if a.cost:
        return cost_report()

    now = datetime.datetime.now(ICT)
    month = a.month or now.strftime("%Y%m")
    only = set(a.tables.split(",")) if a.tables else None

    ensure_dataset()
    existing = list_pins()
    lines, results = [], []
    worst, oper_err = OK, 0

    for dataset, table, do_compare, group_expr in PINS:
        if only and table not in only:
            continue
        dst = f"{table}_pin_{month}"
        try:
            if not table_exists(dataset, table):
                lines.append(f"CRITICAL {table}: BẢNG NGUỒN KHÔNG TỒN TẠI ({dataset}.{table})")
                worst = CRIT
                continue
            status = "skipped" if a.compare_only else snapshot(dataset, table, dst, a.dry_run)
        except Exception as e:
            lines.append(f"ERROR {table}: pin thất bại — {e}")
            oper_err += 1
            continue

        prev_months = sorted(m for m in existing.get(table, {}) if m < month)
        if a.dry_run and status == "would-create":
            lines.append(f"DRY  {table}: sẽ tạo {dst}"
                         + (f", diff vs {existing[table][prev_months[-1]]}" if prev_months else ", chưa có pin trước"))
            continue
        if not do_compare:
            lines.append(f"OK   {table}: pin {status} (rolling table — cố ý KHÔNG diff)")
            continue
        if not prev_months:
            lines.append(f"OK   {table}: pin {status} — BASELINE, chưa có pin tháng trước để so")
            continue

        prev_pin = existing[table][prev_months[-1]]
        try:
            r = compare(prev_pin, dst, group_expr)
        except Exception as e:
            lines.append(f"ERROR {table}: diff thất bại — {e}")
            oper_err += 1
            continue
        r["table"] = table
        results.append(r)
        if RANK[r["severity"]] > RANK[worst]:
            worst = r["severity"]
        lines.append(
            f"{r['severity']:8s} {table}: pin {status} vs {prev_pin} | "
            f"-{r['groups_removed']} +{r['groups_added']} restate {r['groups_restated']} "
            f"({r['groups_restated_pct']}%) | dòng chồng lấn {r['rows_overlap_prev']}→{r['rows_overlap_cur']} "
            f"({r['rows_moved_pct']}%)")

    # ── report ────────────────────────────────────────────────────────────────────────────
    os.makedirs(REPORT_DIR, exist_ok=True)
    stamp = now.strftime("%Y-%m-%dT%H:%M:%S%z")
    body = [f"# BQ monthly pin — {month}", f"chạy lúc {stamp} (ICT)", ""] + lines + [""]
    for r in results:
        if r["severity"] == OK and not r["reasons"]:
            continue
        body += [f"## {r['table']} — {r['severity']}",
                 f"- pin trước: `{r['prev_pin']}` → pin này: `{r['cur_pin']}`",
                 f"- toàn bảng: dòng {r['prev']['n']}→{r['cur']['n']}, nhóm {r['prev']['ngroups']}→{r['cur']['ngroups']}, "
                 f"time {r['prev']['min_time']}..{r['prev']['max_time']} → {r['cur']['min_time']}..{r['cur']['max_time']}"]
        for why in r["reasons"]:
            body.append(f"- {why}")
        for k, label in (("sample_removed", "nhóm biến mất"), ("sample_added", "nhóm mới"),
                         ("sample_restated", "nhóm restate")):
            if r[k]:
                body.append(f"- {label} (tối đa 25): {', '.join(r[k])}")
        body.append("")
    report = "\n".join(body)
    if not a.dry_run:
        with open(os.path.join(REPORT_DIR, f"pin_{month}.md"), "w") as f:
            f.write(report)
        with open(os.path.join(REPORT_DIR, f"pin_{month}.json"), "w") as f:
            json.dump({"month": month, "ts": stamp, "severity": worst,
                       "oper_errors": oper_err, "results": results}, f, indent=1, default=str)
    print(report)

    # ── notify: always one line (quiet heartbeat), detail only when it matters ────────────
    if not a.no_notify and not a.dry_run:
        head = (f"BQ monthly pin {month} — {worst}"
                + (f" | {oper_err} lỗi vận hành" if oper_err else "")
                + f" | {len(results)} bảng đối chiếu, "
                + f"{sum(1 for r in results if r['severity'] != OK)} bảng có cảnh báo")
        clean = worst == OK and not oper_err
        msg = head if clean else head + "\n```\n" + "\n".join(lines)[:1600] + "\n```"
        # Trading Daily luôn nhận 1 dòng (im lặng = không phân biệt được với cron chết);
        # #mikefleet chỉ bị đánh thức khi thật sự có chuyện.
        subprocess.run([f"{MIKE}/bin/notify_thread.sh", msg, DISCORD_STALE_CHANNEL],
                       capture_output=True, text=True)
        if not clean:
            subprocess.run([f"{MIKE}/bin/notify.sh", msg], capture_output=True, text=True)

    if oper_err:
        return 3
    return {OK: 0, WARN: 2, CRIT: 1}[worst]


if __name__ == "__main__":
    sys.exit(main())
