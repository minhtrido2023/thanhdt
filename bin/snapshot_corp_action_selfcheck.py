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
                 prev=(dt.date(2026, 8, 16), 1000), snap_schema=None, verify_rows=None,
                 src_schema=None):
        self.src = FakeTable(src_schema or SRC_SCHEMA, src_rows, 14_600_000)
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


# ── T8: A′ — so schema theo TÊN→KIỂU, bỏ qua thứ tự ────────────────────────
# Mô phỏng đúng mốc 2026-09-13: vendor chèn 2 cột vào GIỮA (trước ingested_at), còn
# ALTER TABLE ADD COLUMN chỉ nối được sau 2 cột meta.
NEW_COLS = [FakeField("source_news_id", "STRING"), FakeField("first_disclosure_datetime", "TIMESTAMP")]
META = [FakeField("snapshot_date", "DATE"), FakeField("row_sha256", "STRING")]
SRC_NEW = SRC_SCHEMA[:-1] + NEW_COLS + SRC_SCHEMA[-1:]        # nguồn sau mốc: ..., 2 cột mới, ingested_at
SNAP_AFTER_DDL = SRC_SCHEMA + META + NEW_COLS                  # bảng đích sau ALTER: nối cuối


def t8_schema_by_name():
    print("\nT8 — A′: cot moi noi sau meta khong loi; thieu/thua/lech kieu VAN loi")
    p = M.schema_problems(SRC_NEW, FakeTable(SNAP_AFTER_DDL))
    check("T8.1 cot moi noi SAU meta (sau ALTER) -> 0 van de", p == [], str(p))

    p = M.schema_problems(SRC_NEW, FakeTable(SRC_SCHEMA + META))
    check("T8.2 CHUA chay DDL -> bao THIEU dung 2 cot moi",
          len(p) == 1 and "THIEU" in p[0] and "source_news_id" in p[0]
          and "first_disclosure_datetime" in p[0], str(p))

    bad_type = SRC_SCHEMA + META + [FakeField("source_news_id", "STRING"),
                                    FakeField("first_disclosure_datetime", "STRING")]
    p = M.schema_problems(SRC_NEW, FakeTable(bad_type))
    check("T8.3 lech kieu that (TIMESTAMP vs STRING) -> VAN loi",
          any("LECH KIEU" in x and "first_disclosure_datetime" in x for x in p), str(p))

    p = M.schema_problems(SRC_NEW, FakeTable(SNAP_AFTER_DDL + [FakeField("zombie", "INT64")]))
    check("T8.4 snapshot thua cot -> VAN loi", any("KHONG con o nguon" in x and "zombie" in x for x in p), str(p))

    p = M.schema_problems(SRC_NEW, FakeTable(SRC_SCHEMA + NEW_COLS + META[:1]))
    check("T8.5 dung cot nguon nhung thieu meta row_sha256 -> VAN loi",
          p == ["thieu cot meta `row_sha256`"], str(p))

    c = FakeClient(src_rows=36_352, src_schema=SRC_NEW, snap_schema=SNAP_AFTER_DDL,
                   prev=(dt.date(2026, 9, 13), 36_300))
    try:
        res, _ = run_capture(c, dry_run=False, date=dt.date(2026, 9, 15))
        check("T8.6 run_one sau DDL -> INSERT that", res["action"] == "insert" and c.executed_dml, res["action"])
    except Exception as e:
        check("T8.6 run_one sau DDL -> INSERT that", False, repr(e))
    ins = next((x for x in c.sqls if x.lstrip().upper().startswith("INSERT")), "")
    check("T8.7 INSERT goi TEN cot tuong minh (thu tu bang dich khong quyet dinh cot nao vao dau)",
          "`source_news_id`, `first_disclosure_datetime`, `ingested_at`, `snapshot_date`, `row_sha256`)" in ins,
          ins.split("\n")[0][-110:])

    c2 = FakeClient(src_rows=36_352, src_schema=SRC_NEW, snap_schema=SRC_SCHEMA + META)
    try:
        run_capture(c2, dry_run=False)
        check("T8.8 chua DDL -> run_one fail-closed, khong DML", False, "khong ném exception")
    except RuntimeError as e:
        check("T8.8 chua DDL -> run_one fail-closed, khong DML",
              "SCHEMA LECH" in str(e) and not c2.executed_dml, str(e)[:100])


# ── T9: cô lập từng bảng + báo người ─────────────────────────────────────────
class TableFailClient(FakeClient):
    """get_table ném lỗi cho đúng 1 bảng (src hoặc snapshot) — bảng còn lại bình thường."""

    def __init__(self, fail_src, **kw):
        super().__init__(**kw)
        self.fail_src = fail_src

    def get_table(self, ref):
        if ref.split(".")[-1].startswith(self.fail_src):
            raise RuntimeError(f"SCHEMA LECH gia lap cho {self.fail_src}")
        return super().get_table(ref)


def run_main(argv, client_factory, notifier):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
        rc = M.main(argv, client_factory=client_factory, notifier=notifier)
    return rc, buf.getvalue()


def t9_isolation_notify():
    print("\nT9 — loi 1 bang KHONG giet bang kia; rc!=0; bao Discord kem exception that")
    for fail, other in (("corporate_action", "insider_transaction"),
                        ("insider_transaction", "corporate_action")):
        c = TableFailClient(fail, src_rows=36_000, prev=(dt.date(2026, 9, 13), 36_000))
        sent = []
        rc, out = run_main(["--date", "2026-09-15"], lambda: c, lambda m: (sent.append(m) or (True, "")))
        check(f"T9.1 {fail} loi -> rc=1", rc == 1, f"rc={rc}")
        check(f"T9.2 {fail} loi -> {other} VAN INSERT", c.executed_dml and f"{other:<22} insert" in out)
        check(f"T9.3 {fail} loi -> notify dung 1 lan", len(sent) == 1, f"{len(sent)} lan")
        msg = sent[0] if sent else ""
        check(f"T9.4 {fail} loi -> tin nhan trich exception THAT (§29)",
              f"❌ {fail}: RuntimeError: SCHEMA LECH gia lap cho {fail}" in msg and f"✅ {other}: insert" in msg,
              msg[:160])

    c = FakeClient(src_rows=36_000)
    sent = []
    rc, _ = run_main(["--date", "2026-09-15"], lambda: c, lambda m: (sent.append(m) or (True, "")))
    check("T9.5 ca 2 bang OK -> rc=0, KHONG notify", rc == 0 and sent == [], f"rc={rc} sent={len(sent)}")

    c = TableFailClient("corporate_action", src_rows=36_000)
    sent = []
    rc, out = run_main(["--dry-run"], lambda: c, lambda m: (sent.append(m) or (True, "")))
    check("T9.6 dry-run co bang loi -> rc=1 nhung KHONG post Discord", rc == 1 and sent == [] and "dry-run: khong post" in out)

    def boom():
        raise PermissionError("403 Access Denied: gia lap")
    sent = []
    rc, _ = run_main(["--date", "2026-09-15"], boom, lambda m: (sent.append(m) or (True, "")))
    check("T9.7 khong tao duoc client -> rc=1 + notify ca 2 bang kem loi that",
          rc == 1 and len(sent) == 1 and sent[0].count("403 Access Denied: gia lap") == 2, sent[0][:160] if sent else "")

    c = TableFailClient("corporate_action", src_rows=36_000)
    rc, out = run_main(["--date", "2026-09-15"], lambda: c, lambda m: (False, "rc=7 stderr=bridge down"))
    check("T9.8 notify that bai -> van rc=1 + in NOTIFY_FAILED kem detail that",
          rc == 1 and "NOTIFY_FAILED topic=architecture rc=7 stderr=bridge down" in out)


# ── T10: HASH_EXCLUDE giữ hash liên tục qua mốc schema đổi ───────────────────
def t10_hash_continuity():
    print("\nT10 — 2 cot moi co gia tri van cho row_sha256 BANG hash vintage cu (BQ that, 0 byte)")
    old_cols = ["id", "ticker", "public_date", "ingested_at"]
    new_cols = ["id", "ticker", "public_date", "source_news_id", "first_disclosure_datetime", "ingested_at"]
    check("T10.1 bieu thuc hash truoc/sau moc GIONG HET tung ky tu",
          M.row_hash_sql(old_cols) == M.row_hash_sql(new_cols), M.row_hash_sql(new_cols)[:90])
    sql = f"""
SELECT 'old' AS lbl, {M.row_hash_sql(old_cols)} AS h FROM UNNEST([STRUCT(
  'X1' AS id, 'AAA' AS ticker, DATE '2026-09-01' AS public_date, TIMESTAMP '2026-09-12 15:00:00' AS ingested_at)])
UNION ALL
SELECT 'new', {M.row_hash_sql(new_cols)} FROM UNNEST([STRUCT(
  'X1' AS id, 'AAA' AS ticker, DATE '2026-09-01' AS public_date, 'N-778899' AS source_news_id,
  TIMESTAMP '2026-08-30 09:15:00' AS first_disclosure_datetime, TIMESTAMP '2026-09-14 15:46:00' AS ingested_at)])
UNION ALL
SELECT 'new_content_changed', {M.row_hash_sql(new_cols)} FROM UNNEST([STRUCT(
  'X1' AS id, 'AAA' AS ticker, DATE '2026-09-02' AS public_date, 'N-778899' AS source_news_id,
  TIMESTAMP '2026-08-30 09:15:00' AS first_disclosure_datetime, TIMESTAMP '2026-09-14 15:46:00' AS ingested_at)])"""
    try:
        job, rows = M.run_query(M.get_client(), sql)
    except Exception as e:
        return check("T10.2 chay duoc query hash tren BQ", False, repr(e))
    h = {r["lbl"]: r["h"] for r in rows}
    check("T10.2 chay duoc query hash tren BQ", len(h) == 3, f"{len(h)} dong")
    check("T10.3 vintage cu (34 cot) vs moi (2 cot moi CO gia tri) -> hash BANG NHAU (khong amendment gia)",
          h.get("old") == h.get("new"))
    check("T10.4 doi chung: sau moc, doi public_date -> hash VAN DOI (van do duoc amendment that)",
          h.get("new") != h.get("new_content_changed"))
    check("T10.5 mien phi (quet 0 byte)", int(job.total_bytes_processed or 0) == 0)


def main():
    print("=" * 78)
    print("SELFCHECK snapshot_corp_action_daily.py")
    print(f"  dataset dich : {M.SNAPSHOT_DATASET}  (env SNAPSHOT_DATASET de doi)")
    print(f"  nguong depth : {M.MIN_ROW_RATIO:.0%}")
    print("=" * 78)
    for fn in (t1_dry_run, t2_idempotent, t3_schema, t4_hash, t5_tz, t6_row_depth,
               t7_verify_after_write, t8_schema_by_name, t9_isolation_notify, t10_hash_continuity):
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
