# -*- coding: utf-8 -*-
"""Regression self-check for sync_bq_cache.py's sync lock + atomic parquet/manifest writes.

Bối cảnh (Taylor, 2026-07-29, job re-pin R3 sau restate DT5G): `sync_bq_cache.py` không có
khoá và ghi `to_parquet` trực tiếp lên file đích. Lúc 23:45 ICT cron
`sync_bq_cache_daily.sh --delta` khởi động ĐÈ LÊN CÙNG `data/bq_cache` với một lần full
re-sync thủ công đang chạy. Lần đó không hỏng gì chỉ vì MAY (thứ tự ghi manifest), không
phải do thiết kế: hai lần sync chồng nhau có thể để lại cache TRỘN VINTAGE mà manifest vẫn
`verified=true`, và một lần bị kill giữa lúc ghi để lại parquet cụt.

Fix (2026-07-30): `acquire_sync_lock()` (fcntl trylock trên `data/bq_cache/.sync.lock`, bao
cả download + verify + ghi manifest) + `atomic_to_parquet()`/`save_manifest()` ghi ra file
tạm cùng thư mục rồi `os.replace` (coding_guidelines §5).

Test chạy trên cache dir TẠM với `bq_query_to_df` bị stub — KHÔNG chạm BigQuery và KHÔNG
chạm `data/bq_cache` thật (chạy `--verify` lên cache thật sẽ ghi lại manifest và có thể
flip `verified=false` khi BQ đã có thêm ngày mới → chặn mọi consumer).

Run: python3 sync_cache_lock_selfcheck.py    (exit 0 = all pass)
"""
import importlib.util
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "sync_bq_cache.py")

# ── Bảng giả + stub BQ ────────────────────────────────────────────────────────
# Phủ đủ 4 nhánh ghi của download_table: full chunked, full 1-file, delta chunked,
# delta append 1-file, cộng full_only (bỏ qua delta) và bảng không có partition_col.
BASE_DAYS = ["2024-01-02", "2024-01-03", "2025-01-02", "2025-01-03", "2025-01-06"]
EXTRA_DAY = "2025-01-07"          # ngày "mới" cho lần chạy --delta
FAKE_TABLES = {
    "tbl_chunk": {
        "sql": "SELECT * FROM `{project}.tav2_bq.tbl_chunk` AS t WHERE t.time >= '2024-01-01'",
        "partition_col": "time",
        "chunk_years": [2024, 2025],
        "verify_sql": "SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time FROM `{project}.tav2_bq.tbl_chunk` AS t WHERE t.time >= '2024-01-01'",
    },
    "tbl_single": {
        "sql": "SELECT * FROM `{project}.tav2_bq.tbl_single` AS t",
        "partition_col": "time",
        "verify_sql": "SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time FROM `{project}.tav2_bq.tbl_single` AS t",
    },
    "tbl_fullonly": {
        "sql": "SELECT * FROM `{project}.tav2_bq.tbl_fullonly` AS t",
        "partition_col": "time",
        "full_only": True,
        "verify_sql": "SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time FROM `{project}.tav2_bq.tbl_fullonly` AS t",
    },
    "tbl_nopart": {
        "sql": "SELECT * FROM `{project}.tav2_bq.tbl_nopart` AS t",
        "partition_col": None,
        "verify_sql": "SELECT COUNT(*) AS cnt FROM `{project}.tav2_bq.tbl_nopart` AS t",
    },
}


def _rows(name, with_extra):
    days = BASE_DAYS + ([EXTRA_DAY] if with_extra else [])
    if name == "tbl_nopart":                      # không có cột time
        return pd.DataFrame({"ticker": ["AAA", "BBB"], "val": [1, 2]})
    return pd.DataFrame(
        [{"time": d, "ticker": tk, "val": i}
         for i, d in enumerate(days) for tk in ("AAA", "BBB")]
    )


def _stub(module, with_extra, hold_s=0.0):
    """Thay bq_query_to_df bằng bản sinh dữ liệu tại chỗ, tôn trọng WHERE trong SQL."""
    def fake(sql, max_rows=10_000_000, timeout=None):
        if hold_s:
            time.sleep(hold_s)                    # để tiến trình giữ khoá đủ lâu
        s = sql.format(project=module.PROJECT)
        name = re.search(r"\.(\w+)`\s+AS t", s).group(1)
        df = _rows(name, with_extra)
        for op, val in re.findall(r"t\.time\s*(>=|<=|>|<)\s*'([\d-]+)'", s):
            if "time" not in df.columns:
                continue
            col = df["time"].astype(str)
            df = df[{">=": col >= val, "<=": col <= val,
                     ">": col > val, "<": col < val}[op]]
        if "COUNT(*)" in s:                       # verify query
            out = {"cnt": [len(df)]}
            if "MAX(t.time)" in s:
                out["max_time"] = [max(df["time"].astype(str))]
            return pd.DataFrame(out)
        return module._apply_date_dtypes(df.reset_index(drop=True))
    module.bq_query_to_df = fake


def _load(path, modname):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    spec.loader.exec_module(mod)
    return mod


def _patch_dirs(m, cache_dir):
    m.CACHE_DIR = cache_dir
    m.MANIFEST_PATH = os.path.join(cache_dir, "manifest.json")
    m.LOCK_PATH = os.path.join(cache_dir, ".sync.lock")   # bản cũ không dùng, vô hại
    m.TABLES = FAKE_TABLES


# ── Chế độ chạy trong tiến trình con ─────────────────────────────────────────
def _child():
    mode = sys.argv[1]
    if mode == "hold":                      # giữ khoá rồi ngủ
        cache_dir, sleep_s = sys.argv[2], float(sys.argv[3])
        m = _load(SCRIPT, "sbc_hold")
        _patch_dirs(m, cache_dir)
        os.makedirs(cache_dir, exist_ok=True)
        assert m.acquire_sync_lock(), "child hold: không lấy được khoá"
        open(os.path.join(cache_dir, "HOLDING"), "w").close()
        time.sleep(sleep_s)
        return 0
    if mode == "run":                       # chạy main() thật (stub BQ)
        script, cache_dir = sys.argv[2], sys.argv[3]
        rest = sys.argv[4:]
        m = _load(script, "sbc_run")
        _patch_dirs(m, cache_dir)
        _stub(m, with_extra=os.environ.get("SELFCHECK_EXTRA") == "1",
              hold_s=float(os.environ.get("SELFCHECK_HOLD", "0")))
        sys.argv = ["sync_bq_cache.py"] + rest
        m.main()
        return 0
    if mode == "killwrite":                 # ghi dở dang rồi tự SIGKILL
        cache_dir, flavor = sys.argv[2], sys.argv[3]
        m = _load(SCRIPT, "sbc_kill")
        _patch_dirs(m, cache_dir)
        dest = os.path.join(cache_dir, "tbl_single.parquet")

        class HalfWriter:                   # mô phỏng to_parquet bị cắt giữa đường
            def to_parquet(self, path, index=False):
                with open(path, "wb") as f:
                    f.write(b"PAR1\x00\x00half-written-junk")
                    f.flush()
                os.kill(os.getpid(), signal.SIGKILL)

        if flavor == "new":
            m.atomic_to_parquet(HalfWriter(), dest)     # ghi tmp → chưa replace
        else:
            HalfWriter().to_parquet(dest)               # hành vi CŨ: đè thẳng đích
        return 0
    raise SystemExit(f"unknown child mode {mode}")


if len(sys.argv) > 1 and sys.argv[1] in ("hold", "run", "killwrite"):
    sys.exit(_child())

# ── Driver ───────────────────────────────────────────────────────────────────
fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


def snapshot(cache_dir):
    """Nội dung cache dạng so sánh được: {relpath: rows-as-csv} + manifest (bỏ timestamp)."""
    out = {}
    for root, _d, files in os.walk(cache_dir):
        for fn in sorted(files):
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, cache_dir)
            if fn.endswith(".parquet"):
                out[rel] = pd.read_parquet(p).to_csv(index=False)
            elif fn == "manifest.json":
                man = json.load(open(p))
                man.pop("verified_at", None)
                man.pop("verified_at_epoch", None)
                out[rel] = json.dumps(man, sort_keys=True, indent=2, default=str)
            else:
                out[rel] = f"<other:{os.path.getsize(p)}B>"
    return out


def run_sync(script, cache_dir, *args, extra=False, hold=0.0):
    env = {**os.environ, "SELFCHECK_EXTRA": "1" if extra else "0",
           "SELFCHECK_HOLD": str(hold)}
    return subprocess.run([sys.executable, __file__, "run", script, cache_dir, *args],
                          capture_output=True, text=True, env=env)


tmp_root = tempfile.mkdtemp(prefix="sync_selfcheck_")
try:
    # Bản "cũ" (trước fix) lấy từ git HEAD để so sánh hành vi — không phụ thuộc file tạm.
    legacy = os.path.join(tmp_root, "legacy_sync_bq_cache.py")
    with open(legacy, "w") as f:
        # "HEAD:./x" = đường dẫn tương đối so với cwd — repo root nằm TRÊN thư mục này
        # (/home/trido/thanhdt), nên "HEAD:sync_bq_cache.py" (tính từ root) không tồn tại.
        f.write(subprocess.run(["git", "-C", HERE, "show", "HEAD:./sync_bq_cache.py"],
                               capture_output=True, text=True, check=True).stdout)

    # ── C. Không xung đột → kết quả GIỐNG HẾT bản trước khi sửa ──────────────
    print("C. Chạy bình thường (không xung đột): mới vs cũ (git HEAD)")
    snaps = {}
    for tag, script in (("new", SCRIPT), ("old", legacy)):
        cd = os.path.join(tmp_root, f"cache_{tag}")
        r_full = run_sync(script, cd)                       # full sync + verify
        r_delta = run_sync(script, cd, "--delta", extra=True)   # delta + verify
        r_ver = run_sync(script, cd, "--verify", extra=True)
        snaps[tag] = (snapshot(cd), r_full, r_delta, r_ver)
        check(f"C1 {tag}: full/delta/verify đều exit 0",
              all(r.returncode == 0 for r in (r_full, r_delta, r_ver)),
              f"rc={[r.returncode for r in (r_full, r_delta, r_ver)]} "
              f"{(r_full.stderr or r_delta.stderr or r_ver.stderr)[-300:]}")
    new_s, old_s = snaps["new"][0], snaps["old"][0]
    # Sản phẩm mới DUY NHẤT được phép xuất hiện so với bản cũ là file khoá (0 byte, không
    # đuôi .parquet nên mọi consumer quét cache bỏ qua).
    check("C2 tập file cache giống bản cũ, chỉ thêm đúng .sync.lock",
          set(new_s) - set(old_s) == {".sync.lock"} and not set(old_s) - set(new_s),
          f"chỉ ở new={set(new_s) - set(old_s)}, chỉ ở old={set(old_s) - set(new_s)}")
    diff = [k for k in set(new_s) & set(old_s) if new_s[k] != old_s[k]]
    check("C3 nội dung mọi parquet + manifest giống nhau", not diff, f"khác: {diff}")
    check("C4 manifest verified=true cả 2 bên",
          '"verified": true' in new_s.get("manifest.json", "")
          and '"verified": true' in old_s.get("manifest.json", ""))
    check("C5 không để lại file tạm sau khi chạy xong",
          not [k for k in new_s if k.endswith(".tmp")], str(list(new_s)))

    # ── A. Hai tiến trình sync đồng thời trên cùng cache dir ─────────────────
    print("A. Hai tiến trình sync cùng lúc (1 manual + 1 cron)")
    cd = os.path.join(tmp_root, "cache_new")               # cache đã đầy đủ ở bước C
    before = snapshot(cd)
    holder = subprocess.Popen([sys.executable, __file__, "hold", cd, "6"],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for _ in range(60):                                     # chờ nó thật sự giữ khoá
        if os.path.exists(os.path.join(cd, "HOLDING")):
            break
        time.sleep(0.1)
    check("A1 tiến trình 1 đã giữ khoá", os.path.exists(os.path.join(cd, "HOLDING")))
    r2 = run_sync(SCRIPT, cd, "--delta", extra=True)
    check("A2 tiến trình 2 thoát với EXIT_LOCKED=75", r2.returncode == 75,
          f"rc={r2.returncode}")
    check("A3 thông báo rõ ràng (BỎ QUA + đường dẫn khoá)",
          "BỎ QUA" in r2.stdout and ".sync.lock" in r2.stdout, r2.stdout.strip()[-200:])
    check("A4 thông báo KHÔNG khớp grep FAILED/FAIL — của wrapper (không dispatch autofix giả)",
          not re.search(r"FAILED|FAIL —|RESULT: FAIL", r2.stdout))
    check("A5 tiến trình 2 KHÔNG ghi gì lên cache (file của tiến trình 1 nguyên vẹn)",
          snapshot(cd) == {k: v for k, v in before.items() if k != "HOLDING"}
          or snapshot(cd) == {**before, "HOLDING": "<other:0B>"},
          f"khác: {[k for k in set(snapshot(cd)) | set(before) if snapshot(cd).get(k) != before.get(k) and k != 'HOLDING']}")
    holder.kill(); holder.wait()
    os.remove(os.path.join(cd, "HOLDING"))
    r3 = run_sync(SCRIPT, cd, "--delta", extra=True)
    check("A6 sau khi tiến trình 1 thoát, lần chạy sau lấy được khoá bình thường",
          r3.returncode == 0, f"rc={r3.returncode} {r3.stdout[-200:]}")
    # Khoá phải tự nhả cả khi bị SIGKILL (OS nhả theo open-file-description).
    check("A7 khoá tự nhả khi tiến trình giữ bị SIGKILL (không cần dọn tay)",
          r3.returncode != 75)

    # ── B. Bị kill giữa lúc ghi 1 file ──────────────────────────────────────
    print("B. SIGKILL giữa lúc ghi parquet")
    dest = os.path.join(cd, "tbl_single.parquet")
    good_csv = pd.read_parquet(dest).to_csv(index=False)
    kr = subprocess.run([sys.executable, __file__, "killwrite", cd, "new"],
                        capture_output=True, text=True)
    check("B1 tiến trình đã bị SIGKILL thật", kr.returncode == -signal.SIGKILL,
          f"rc={kr.returncode}")
    still_good = False
    try:
        still_good = pd.read_parquet(dest).to_csv(index=False) == good_csv
    except Exception as e:
        still_good = f"đọc lỗi: {e}"
    check("B2 file đích KHÔNG bị ghi đè thành bản cụt — vẫn đọc được bản cũ nguyên vẹn",
          still_good is True, str(still_good))
    junk = [f for f in os.listdir(cd) if f.endswith(".tmp")]
    check("B3 bản ghi dở nằm ở file tạm (không đuôi .parquet → consumer glob không thấy)",
          len(junk) == 1 and not junk[0].endswith(".parquet"), str(junk))
    r4 = run_sync(SCRIPT, cd, "--delta", extra=True)
    check("B4 lần chạy sau dọn file tạm rác + chạy OK",
          r4.returncode == 0 and not [f for f in os.listdir(cd) if f.endswith(".tmp")],
          f"rc={r4.returncode} còn lại={[f for f in os.listdir(cd) if f.endswith('.tmp')]}")
    check("B5 dữ liệu sau khi hồi phục vẫn khớp BQ (verify OK)",
          '"verified": true' in open(os.path.join(cd, "manifest.json")).read())

    # Đối chứng: hành vi CŨ (ghi thẳng đích) đúng là làm hỏng file — chứng minh test có ý nghĩa.
    kr2 = subprocess.run([sys.executable, __file__, "killwrite", cd, "legacy"],
                         capture_output=True, text=True)
    legacy_broken = False
    try:
        pd.read_parquet(dest)
    except Exception:
        legacy_broken = True
    check("B6 đối chứng: cách ghi CŨ (to_parquet thẳng đích) bị kill → file đích hỏng thật",
          kr2.returncode == -signal.SIGKILL and legacy_broken)
finally:
    shutil.rmtree(tmp_root, ignore_errors=True)

print()
if fails:
    print(f"SELFCHECK FAILED: {len(fails)} — {fails}")
    sys.exit(1)
print("SELFCHECK OK — tất cả kiểm tra đạt")
