#!/usr/bin/env python3
"""
snapshot_corp_action_selfcheck.py — selfcheck cho snapshot_corp_action_daily.py

Chay:
    source /home/trido/thanhdt/WorkingClaude/wc_env.sh
    python3 mike/bin/snapshot_corp_action_selfcheck.py

T4 va T3(phan live) CAN BigQuery that (T4 quet 0 byte — chi UNNEST literal, mien phi).
Cac test con lai chay tren FakeClient, khong cham BQ, khong side effect.

§16/§19: T5 chay lai ict_today() duoi 3 TZ host khac nhau (ke ca TZ bi go) — day dung la lop loi
"selfcheck xanh vi tac gia dang co TZ dung" ma verify-before-done canh bao.
"""

import os
import sys
import io
import time
import datetime as dt
import contextlib
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapshot_corp_action_daily as M  # noqa: E402

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
    return bool(cond)


# ── fakes ────────────────────────────────────────────────────────────────────
class FakeField:
    def __init__(self, name, ftype):
        self.name = name
        self.field_type = ftype


class FakeTable:
    def __init__(self, schema, num_rows=0, num_bytes=0):
        self.schema = schema
        self.num_rows = num_rows
        self.num_bytes = num_bytes


class FakeJob:
    def __init__(self, rows=None, scanned=0, dml=0):
        self._rows = rows or []
        self.total_bytes_processed = scanned
        self.num_dml_affected_rows = dml
        self.job_id = "fake_job"

    def result(self):
        return self._rows


SRC_SCHEMA = [FakeField("id", "STRING"), FakeField("ticker", "STRING"),
              FakeField("public_date", "DATE"), FakeField("ingested_at", "TIMESTAMP")]


class FakeClient:
    """Mo phong be mat BQ ma run_one() thuc su dung: get_table / create_table / query."""

    def __init__(self, src_rows=1000, snap_exists=True, today_rows=0,
                 prev=(dt.date(2026, 8, 16), 1000), snap_schema=None, verify_rows=None):
        self.src = FakeTable(SRC_SCHEMA, src_rows, 14_600_000)
        self.snap_exists = snap_exists
        self.today_rows = today_rows
        self.prev = prev
        self.verify_rows = src_rows if verify_rows is None else verify_rows
        self.snap = FakeTable(
            snap_schema if snap_schema is not None
            else SRC_SCHEMA + [FakeField("snapshot_date", "DATE"), FakeField("row_sha256", "STRING")])
        self.created = []
        self.sqls = []
        # DML DA THUC SU CHAY (dry_run=False). Khong duoc suy tu chuoi SQL: cau INSERT VAN duoc
        # gui di trong dry-run — co dry_run tren job_config moi la thu quyet dinh co ghi hay khong.
        self.executed_dml = False
        self._inserted = False

    def get_table(self, ref):
        if ref.endswith("_snapshots"):
            if not self.snap_exists:
                raise Exception("404 Not found")
            return self.snap
        return self.src

    def create_table(self, tbl):
        self.created.append(tbl)
        self.snap_exists = True
        return self.snap

    def query(self, sql, job_config=None):
        self.sqls.append(sql)
        if getattr(job_config, "dry_run", False):
            return FakeJob(scanned=14_600_000)
        if sql.lstrip().upper().startswith("INSERT"):
            self.executed_dml = True
            self._inserted = True
            return FakeJob(scanned=14_600_000, dml=self.src.num_rows)
        if "GROUP BY 1 ORDER BY 1 DESC" in sql:
            return FakeJob([{"snapshot_date": self.prev[0], "n": self.prev[1]}] if self.prev else [])
        if "COUNT(*)" in sql:
            n = self.verify_rows if self._inserted else self.today_rows
            return FakeJob([{"n": n}])
        raise AssertionError(f"FakeClient khong biet tra loi SQL: {sql[:80]}")


def run_capture(client, dry_run, date=dt.date(2026, 8, 17)):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        res = M.run_one(client, M.SPECS[0], date, dry_run)
    return res, buf.getvalue()


# ── T1: dry-run ──────────────────────────────────────────────────────────────
def t1_dry_run():
    print("\nT1 — dry-run khong throw + log du thong tin, KHONG ghi")
    c = FakeClient(src_rows=36_176)
    try:
        res, out = run_capture(c, dry_run=True)
    except Exception as e:
        return check("T1.0 dry-run khong throw", False, repr(e))
    check("T1.0 dry-run khong throw", True)
    check("T1.1 action=dry-run", res["action"] == "dry-run", res["action"])
    check("T1.2 KHONG thuc su chay DML (cau INSERT co gui, nhung duoi dry_run=True)",
          c.executed_dml is False)
    check("T1.2b van co gui cau INSERT de BQ uoc phi that",
          any(s.lstrip().upper().startswith("INSERT") for s in c.sqls))
    check("T1.3 khong tao bang", c.created == [])
    check("T1.4 log so dong nguon", "36,176 dong" in out)
    check("T1.5 log so cot hash + cot bi loai", "hash phu" in out and "ingested_at" in out)
    check("T1.6 log uoc phi quet", "$" in out and "MB" in out)
    check("T1.7 log uoc storage/nam", "GB/nam" in out)
    check("T1.8 log 'KHONG ghi gi'", "KHONG ghi gi" in out)
    check("T1.9 xac nhan schema KHOP", "schema       : KHOP" in out)


# ── T2: idempotency ──────────────────────────────────────────────────────────
def t2_idempotent():
    print("\nT2 — guard idempotent: hom nay da co dong -> SKIP, khong INSERT")
    c = FakeClient(src_rows=36_176, today_rows=36_176)
    res, out = run_capture(c, dry_run=False)
    check("T2.1 action=skip", res["action"] == "skip", res["action"])
    check("T2.2 KHONG chay DML nao", c.executed_dml is False)
    check("T2.3 log noi ro SKIP + so dong da co", "SKIP" in out and "36,176" in out)

    print("  (doi chung) hom nay CHUA co dong -> phai INSERT that")
    c2 = FakeClient(src_rows=36_176, today_rows=0)
    res2, _ = run_capture(c2, dry_run=False)
    check("T2.4 doi chung: action=insert", res2["action"] == "insert", res2["action"])
    check("T2.5 doi chung: co chay DML that", c2.executed_dml is True)


# ── T3: schema khớp ──────────────────────────────────────────────────────────
def t3_schema():
    print("\nT3 — schema bang snapshot khop schema bang nguon (ten cot)")
    # (a) unit: schema_problems phat hien lech, va im lang khi khop
    ok_tbl = FakeTable(SRC_SCHEMA + [FakeField("snapshot_date", "DATE"),
                                     FakeField("row_sha256", "STRING")])
    check("T3.1 cap khop -> 0 van de", M.schema_problems(SRC_SCHEMA, ok_tbl) == [],
          str(M.schema_problems(SRC_SCHEMA, ok_tbl)))

    drift = FakeTable([f for f in SRC_SCHEMA if f.name != "public_date"] +
                      [FakeField("snapshot_date", "DATE"), FakeField("row_sha256", "STRING")])
    p = M.schema_problems(SRC_SCHEMA, drift)
    check("T3.2 nguon them cot -> bao THIEU o snapshot", any("THIEU" in x for x in p), str(p))

    no_meta = FakeTable(list(SRC_SCHEMA))
    p2 = M.schema_problems(SRC_SCHEMA, no_meta)
    check("T3.3 thieu cot meta -> bao loi", len(p2) >= 2, str(p2))

    # (b) lech schema phai LAM DUNG PIPELINE (fail-closed), khong tu evolve
    c = FakeClient(snap_schema=[f for f in SRC_SCHEMA if f.name != "public_date"] +
                   [FakeField("snapshot_date", "DATE"), FakeField("row_sha256", "STRING")])
    try:
        run_capture(c, dry_run=False)
        check("T3.4 lech schema -> RuntimeError (fail-closed)", False, "khong ném exception")
    except RuntimeError as e:
        check("T3.4 lech schema -> RuntimeError (fail-closed)", "SCHEMA LECH" in str(e))
        check("T3.5 lech schema -> KHONG chay DML", c.executed_dml is False)

    # (c) live: doi chieu voi BQ that
    try:
        client = M.get_client()
    except Exception as e:
        return check("T3.6 live BQ", False, f"khong tao duoc client: {e}")

    for spec in M.SPECS:
        src_ref = f"{M.PROJECT}.{M.SRC_DATASET}.{spec['src']}"
        snap_ref = f"{M.PROJECT}.{M.SNAPSHOT_DATASET}.{spec['snap']}"
        src_schema = list(client.get_table(src_ref).schema)
        built = M.snapshot_schema(src_schema)
        names = [f.name for f in built]
        check(f"T3.6 {spec['src']}: snapshot_schema = cot nguon + 2 meta, dung thu tu",
              names == [f.name for f in src_schema] + list(M.META_COLS),
              f"{len(names)} cot")
        try:
            snap_tbl = client.get_table(snap_ref)
        except Exception:
            print(f"       (bang {snap_ref} chua ton tai — bo qua doi chieu live, dung truoc deploy)")
            continue
        probs = M.schema_problems(src_schema, snap_tbl)
        check(f"T3.7 {spec['src']}: bang snapshot LIVE khop nguon", probs == [], str(probs))


# ── T4: row_sha256 ───────────────────────────────────────────────────────────
def t4_hash():
    print("\nT4 — row_sha256 doi khi 1 field doi (chay tren BQ that, quet 0 byte)")
    cols = ["ticker", "public_date", "value_per_share", "note", "ingested_at"]
    hexpr = M.row_hash_sql(cols)
    check("T4.0 ingested_at bi loai khoi hash", "ingested_at" not in hexpr, hexpr[:90])

    sql = f"""
SELECT lbl, {hexpr} AS h FROM UNNEST([
  STRUCT('base' AS lbl, 'AAA' AS ticker, DATE '2026-01-01' AS public_date,
         CAST(1.5 AS FLOAT64) AS value_per_share, CAST(NULL AS STRING) AS note,
         TIMESTAMP '2026-01-01 00:00:00' AS ingested_at),
  STRUCT('field_changed', 'AAA', DATE '2026-01-02', CAST(1.5 AS FLOAT64), CAST(NULL AS STRING),
         TIMESTAMP '2026-01-01 00:00:00'),
  STRUCT('float_changed', 'AAA', DATE '2026-01-01', CAST(1.6 AS FLOAT64), CAST(NULL AS STRING),
         TIMESTAMP '2026-01-01 00:00:00'),
  STRUCT('only_ingested_at_changed', 'AAA', DATE '2026-01-01', CAST(1.5 AS FLOAT64),
         CAST(NULL AS STRING), TIMESTAMP '2026-06-06 00:00:00'),
  STRUCT('null_vs_empty', 'AAA', DATE '2026-01-01', CAST(1.5 AS FLOAT64), CAST('' AS STRING),
         TIMESTAMP '2026-01-01 00:00:00'),
  STRUCT('identical_copy', 'AAA', DATE '2026-01-01', CAST(1.5 AS FLOAT64), CAST(NULL AS STRING),
         TIMESTAMP '2026-01-01 00:00:00')
])"""
    try:
        client = M.get_client()
        job, rows = M.run_query(client, sql)
    except Exception as e:
        return check("T4.1 chay duoc query hash tren BQ", False, repr(e))
    h = {r["lbl"]: r["h"] for r in rows}
    check("T4.1 chay duoc query hash tren BQ", len(h) == 6, f"{len(h)} dong")
    check("T4.2 doi 1 field DATE -> hash DOI", h["base"] != h["field_changed"])
    check("T4.3 doi 1 field FLOAT -> hash DOI", h["base"] != h["float_changed"])
    check("T4.4 noi dung y het -> hash GIONG", h["base"] == h["identical_copy"])
    check("T4.5 chi ingested_at doi -> hash GIONG (khong bao amendment gia)",
          h["base"] == h["only_ingested_at_changed"])
    check("T4.6 NULL phan biet duoc voi chuoi rong", h["base"] != h["null_vs_empty"])
    check("T4.7 hash la hex 64 ky tu", all(len(v) == 64 for v in h.values()))
    scanned = int(job.total_bytes_processed or 0)
    check("T4.8 test hash mien phi (quet 0 byte)", scanned == 0, f"{scanned} bytes")


# ── T5: timezone §16 ─────────────────────────────────────────────────────────
def t5_tz():
    print("\nT5 — ict_today() neo ICT tuong minh, KHONG phu thuoc TZ cua host (§16)")
    expect = dt.datetime.now(dt.timezone.utc).astimezone(ZoneInfo("Asia/Ho_Chi_Minh")).date()
    saved = os.environ.get("TZ")
    ok = True
    for tzval in ["UTC", "America/New_York", "Pacific/Kiritimati", None]:
        if tzval is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = tzval
        try:
            time.tzset()
        except AttributeError:
            pass
        got = M.ict_today()
        label = tzval or "(TZ bi go)"
        if not check(f"T5 TZ={label} -> {got}", got == expect, f"ky vong {expect}"):
            ok = False
    if saved is None:
        os.environ.pop("TZ", None)
    else:
        os.environ["TZ"] = saved
    try:
        time.tzset()
    except AttributeError:
        pass
    return ok


# ── T6: cổng row-depth (chống chụp giữa lúc vendor rebuild) ──────────────────
def t6_row_depth():
    print("\nT6 — nguon co dot ngot -> ABORT, khong ghi snapshot sai vintage")
    c = FakeClient(src_rows=100, today_rows=0, prev=(dt.date(2026, 8, 16), 36_000))
    try:
        run_capture(c, dry_run=False)
        check("T6.1 nguon con 0.3% -> RuntimeError", False, "khong ném exception")
    except RuntimeError as e:
        check("T6.1 nguon con 0.3% -> RuntimeError", "ROW_DEPTH" in str(e))
        check("T6.2 khong chay DML khi abort", c.executed_dml is False)

    c2 = FakeClient(src_rows=36_100, today_rows=0, prev=(dt.date(2026, 8, 16), 36_000))
    res, _ = run_capture(c2, dry_run=False)
    check("T6.3 nguon tang binh thuong -> van INSERT", res["action"] == "insert")

    c3 = FakeClient(src_rows=36_176, today_rows=0, prev=None)
    res3, out3 = run_capture(c3, dry_run=False)
    check("T6.4 lan chay dau (chua co snapshot truoc) -> khong bi guard chan",
          res3["action"] == "insert" and "lan chay dau tien" in out3)


# ── T7: verify sau ghi ───────────────────────────────────────────────────────
def t7_verify_after_write():
    print("\nT7 — dem lai sau INSERT lech so nguon -> bao loi, khong bao thanh cong")
    c = FakeClient(src_rows=36_176, today_rows=0, verify_rows=30_000)
    try:
        run_capture(c, dry_run=False)
        check("T7.1 lech sau ghi -> RuntimeError", False, "khong ném exception")
    except RuntimeError as e:
        check("T7.1 lech sau ghi -> RuntimeError", "VERIFY FAIL" in str(e), str(e)[:80])


def main():
    print("=" * 78)
    print("SELFCHECK snapshot_corp_action_daily.py")
    print(f"  dataset dich : {M.SNAPSHOT_DATASET}  (env SNAPSHOT_DATASET de doi)")
    print(f"  nguong depth : {M.MIN_ROW_RATIO:.0%}")
    print("=" * 78)
    for fn in (t1_dry_run, t2_idempotent, t3_schema, t4_hash, t5_tz, t6_row_depth,
               t7_verify_after_write):
        try:
            fn()
        except Exception as e:
            import traceback
            traceback.print_exc()
            check(f"{fn.__name__} chay tron ven", False, repr(e))

    n_ok = sum(1 for _, ok, _ in RESULTS if ok)
    print("\n" + "=" * 78)
    print(f"KET QUA: {n_ok}/{len(RESULTS)} PASS")
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"  FAIL: {name} — {detail}")
    print("=" * 78)
    return 0 if n_ok == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
