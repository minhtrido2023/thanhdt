# -*- coding: utf-8 -*-
"""make_ca_extract.py — tạo out/ca/ca_extract_<YYYYMM>.csv + .md5 + .meta.json (YYYYMM = tháng CHẠY theo ICT; phục vụ as-of tháng trước).
SQL: calc/ca_extract.sql trên tav2_mike.corporate_action_snapshots. Atomic (tmp + os.link), KHÔNG BAO GIỜ ghi đè.
Idempotent: đã có csv + md5 khớp ⇒ SKIP rc 0 (giữ bản cũ, không query). Có csv thiếu md5 (bị kill giữa chừng) ⇒ chỉ ghi md5 nếu query lại ra đúng byte.
Fail-closed rc 3: không có snapshot · ingest mới nhất của vendor chưa tới 22:00 ICT ngày làm việc cuối tháng trước · thiếu loại sự kiện / < 30.000 dòng ·
tạo mới cho tháng khác tháng hiện hành mà không chỉ định --snapshot-date · file có sẵn nhưng md5 lệch.
Dùng: python make_ca_extract.py [--ym YYYYMM] [--snapshot-date YYYY-MM-DD] [--out-dir DIR]   (cần `bq` đã auth: source wc_env.sh)"""
import argparse, csv, hashlib, io, json, os, subprocess, sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__)); _ICT = ZoneInfo("Asia/Ho_Chi_Minh"); PROJECT = "lithe-record-440915-m9"
BQ_BIN = os.environ.get("BQ_BIN", "/home/trido/google-cloud-sdk/bin/bq"); MIN_ROWS = 30000


def fail(msg):
    print("FAIL-CLOSED: " + msg, file=sys.stderr); raise SystemExit(3)


def bq_csv(sql):
    env = {**os.environ, "PATH": os.environ.get("PATH", "") + ":" + os.path.dirname(BQ_BIN)}
    r = subprocess.run([BQ_BIN, "query", "--use_legacy_sql=false", f"--project_id={PROJECT}", "--format=csv", "--max_rows=1000000"],
                       input=sql.encode(), capture_output=True, env=env, timeout=600)
    if r.returncode != 0:
        fail(f"bq rc={r.returncode}: {(r.stderr + r.stdout).decode(errors='replace')[-600:]}")
    return r.stdout


def put_new(path, data):
    """Tạo file mới, atomic, không ghi đè (os.link lỗi nếu đích đã có)."""
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, "wb") as f:
        f.write(data); f.flush(); os.fsync(f.fileno())
    try:
        os.link(tmp, path)
    except FileExistsError:
        fail(f"{path} đã tồn tại — không ghi đè")
    finally:
        os.remove(tmp)


def required_ingest(ym):
    d = datetime(int(ym[:4]), int(ym[4:]), 1).date() - timedelta(days=1)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return datetime(d.year, d.month, d.day, 22, 0, tzinfo=_ICT)


def main():
    now_ym = datetime.now(_ICT).strftime("%Y%m")
    ap = argparse.ArgumentParser(); ap.add_argument("--ym", default=now_ym); ap.add_argument("--snapshot-date"); ap.add_argument("--out-dir", default=os.path.join(HERE, "..", "out", "ca"))
    a = ap.parse_args()
    dest = os.path.join(a.out_dir, f"ca_extract_{a.ym}.csv"); md5p = dest + ".md5"
    if os.path.exists(dest) and os.path.exists(md5p):
        have = hashlib.md5(open(dest, "rb").read()).hexdigest(); want = open(md5p).read().split()[0]
        if have != want:
            fail(f"{dest} md5 {have} ≠ {md5p} {want}")
        print(f"SKIP: {dest} đã có (md5 {have}), giữ nguyên"); return 0
    snap = a.snapshot_date
    if not snap:
        if a.ym != now_ym:
            fail(f"--ym {a.ym} ≠ tháng hiện hành {now_ym}: dựng lại tháng cũ phải chỉ định --snapshot-date")
        out = bq_csv("SELECT MAX(snapshot_date) AS s FROM tav2_mike.corporate_action_snapshots").decode().split()
        if len(out) < 2:
            fail("corporate_action_snapshots không có snapshot_date nào")
        snap = out[1]
    datetime.strptime(snap, "%Y-%m-%d")
    sql = open(os.path.join(HERE, "ca_extract.sql"), encoding="utf-8").read().replace("{snapshot_date}", snap)
    data = bq_csv(sql)
    rows = list(csv.DictReader(io.StringIO(data.decode("utf-8"))))
    codes = {r["event_code"] for r in rows}
    if len(rows) < MIN_ROWS or codes != {"AIS", "DIV", "ISS"}:
        fail(f"snapshot {snap}: {len(rows)} dòng, event_code {sorted(codes)} (cần ≥ {MIN_ROWS} dòng, đủ AIS/DIV/ISS)")
    mx = max(r["ingested_at"] for r in rows)                    # 'YYYY-MM-DD HH:MM:SS[.ffffff]+00'
    mx_ict = datetime.strptime(mx[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).astimezone(_ICT)
    need = required_ingest(a.ym)
    if mx_ict < need:
        fail(f"snapshot {snap}: ingest mới nhất {mx_ict.isoformat()} < {need.isoformat()} — sự kiện công bố tới cuối tháng trước có thể chưa vào")
    md5 = hashlib.md5(data).hexdigest()
    os.makedirs(a.out_dir, exist_ok=True)
    if os.path.exists(dest):
        if hashlib.md5(open(dest, "rb").read()).hexdigest() != md5:
            fail(f"{dest} đã có (thiếu .md5) và khác kết quả query snapshot {snap} — kiểm thủ công")
    else:
        put_new(dest, data)
    put_new(md5p, f"{md5}  {os.path.basename(dest)}\n".encode())
    meta = {"ym": a.ym, "snapshot_date": snap, "max_ingested_ict": mx_ict.isoformat(), "rows": len(rows), "md5": md5, "sql": sql,
            "created_at_ict": datetime.now(_ICT).isoformat(timespec="seconds")}
    mp = dest + ".meta.json"
    if not os.path.exists(mp):
        put_new(mp, json.dumps(meta, ensure_ascii=False, indent=1).encode())
    print(f"ĐÃ GHI {dest}: {len(rows)} dòng, md5 {md5}, snapshot {snap}, ingest mới nhất {mx_ict.isoformat()}"); return 0


if __name__ == "__main__":
    sys.exit(main())
