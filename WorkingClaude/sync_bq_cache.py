#!/usr/bin/env python3
"""Download BQ tables to local parquet cache + verify integrity once daily.

Usage:
  python3 sync_bq_cache.py              # full sync + verify
  python3 sync_bq_cache.py --delta      # delta only (append today's rows)
  python3 sync_bq_cache.py --verify     # verify only (no download)
  python3 sync_bq_cache.py --tables ticker ticker_financial   # sync specific tables

Cache dir: data/bq_cache/ (relative to WORKDIR).
Manifest: data/bq_cache/manifest.json — records row counts, max dates, verification.
"""
import argparse
import fcntl
import io
import json
import os
import subprocess
import sys
import time

import pandas as pd
import pyarrow.parquet as _pq

# Đăng ký extension dtype "dbdate" của google (nếu package có) TRƯỚC mọi read_parquet —
# một số chunk parquet cũ trên đĩa (vd ticker/2026.parquet, ghi bởi phiên bản trước dùng
# BigQuery to_dataframe) mang dtype này; thiếu import thì pd.read_parquet crash
# "TypeError: data type 'dbdate' not understood". Chính crash đó làm delta sync bảng
# `ticker` chết ÂM THẦM mỗi đêm từ ~2026-06-26 → cache thối → macro_healthcheck đọc
# VNINDEX từ cache báo stale 7 ngày → FAILED/SEV1 giả (2026-07-06, kb/INCIDENTS.md).
try:
    import db_dtypes  # noqa: F401  (side-effect import: registers dbdate/dbtime dtypes)
except ImportError:
    pass

WORKDIR = "/home/trido/thanhdt/WorkingClaude"

# Columns that must be stored as date32 (not VARCHAR) in parquet.
# quarter is intentionally excluded — it's a string like "2025Q3".
DATE_COLS = {"time", "Release_Date", "rebal_date", "effective_from", "effective_to"}


def _apply_date_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Cast known date columns from string → datetime.date so parquet stores date32.

    Kiểm tra `dtype == object` là KHÔNG đủ: pandas 3.x đọc CSV ra dtype `str`
    (StringDtype) chứ không còn `object`, nên điều kiện cũ bỏ qua cast âm thầm →
    parquet ghi cột time thành `large_string` → verify báo DTYPE_MISMATCH
    (universe_pit_q + ticker_prune, 2026-07-22). Nhận cả object lẫn string dtype.
    """
    for col in DATE_COLS:
        if col not in df.columns:
            continue
        dt = df[col].dtype
        if dt == object or pd.api.types.is_string_dtype(dt):
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
    return df
CACHE_DIR = os.path.join(WORKDIR, "data", "bq_cache")
PROJECT = "lithe-record-440915-m9"
MANIFEST_PATH = os.path.join(CACHE_DIR, "manifest.json")

# Khoá độc quyền cho TOÀN BỘ tiến trình sync (download + verify + ghi manifest).
LOCK_PATH = os.path.join(CACHE_DIR, ".sync.lock")
# Exit code riêng cho "bỏ qua vì tiến trình khác đang sync" — KHÔNG phải lỗi thật.
# 75 = EX_TEMPFAIL (sysexits.h): thử lại sau thì được, không cần người can thiệp.
EXIT_LOCKED = 75
# Hậu tố file tạm khi ghi atomic. CỐ Ý không kết thúc bằng ".parquet": mọi consumer
# quét cache theo `*.parquet` (preflight_bq_cache.py, bq_local_cache.py read_parquet
# glob, phần tính size_mb dưới đây) nên file tạm/rác không bao giờ bị đọc như dữ liệu.
TMP_SUFFIX = ".tmp"

# Timeout mặc định cho 1 lệnh `bq query` (giây). Bảng lớn khai báo riêng qua
# key "query_timeout" trong TABLES — 300s cứng cho MỌI bảng là quá ngắn cho chunk
# năm của `ticker` (~15,2M dòng, chunk 2013 timeout ở resync 2026-07-22).
DEFAULT_QUERY_TIMEOUT = 300

# Use bq CLI (gcloud auth login creds) — no ADC/Application-Default required
BQ_BIN = os.environ.get("BQ_BIN", "/home/trido/google-cloud-sdk/bin/bq")
# bq internally calls gcloud (same SDK dir); ensure it's on PATH for subprocess calls
_SDK_BIN = os.path.dirname(BQ_BIN)
_SUBPROCESS_ENV = {**os.environ, "PATH": os.environ.get("PATH", "") + ":" + _SDK_BIN}

# ── Table definitions ────────────────────────────────────────────────────────
# Each table: full SQL for initial download, partition column for delta,
# and optional WHERE filter for the initial load.
TABLES = {
    "ticker": {
        "sql": """
            SELECT *
            FROM `{project}.tav2_bq.ticker` AS t
            WHERE t.time >= '2013-01-01'
        """,
        "partition_col": "time",
        "chunk_years": list(range(2013, 2028)),
        # Bảng lớn nhất hệ thống (~15,2M dòng, ~1M dòng/chunk năm) — 300s mặc định
        # không đủ cho 1 chunk (fail thật ở resync 2026-07-22).
        "query_timeout": 3600,
        "verify_sql": """
            SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time
            FROM `{project}.tav2_bq.ticker` AS t
            WHERE t.time >= '2013-01-01'
        """,
    },
    # universe_pit_q = the team-owned point-in-time universe (view = universe_pit + quality_flag).
    # Cached because custom_basket.py (custom30V parking basket) reads it per day since the P2
    # cutover 2026-07-22 — without it every cache-routed basket build would fail hard (by design:
    # no silent fallback to ticker_prune, §4.3 of ticker_prune_replacement_plan.md).
    # Full fidelity (in_universe TRUE *and* FALSE rows) so a cache-routed query can never disagree
    # with the same query run against BigQuery.
    "universe_pit_q": {
        "sql": """
            SELECT *
            FROM `{project}.tav2_mike.universe_pit_q` AS t
            WHERE t.time >= '2013-01-01'
        """,
        "partition_col": "time",
        "chunk_years": list(range(2013, 2028)),
        "verify_sql": """
            SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time
            FROM `{project}.tav2_mike.universe_pit_q` AS t
            WHERE t.time >= '2013-01-01'
        """,
    },
    "ticker_prune": {
        "sql": """
            SELECT *
            FROM `{project}.tav2_bq.ticker_prune` AS t
            WHERE t.time >= '2013-01-01'
        """,
        "partition_col": "time",
        "chunk_years": list(range(2013, 2028)),
        # chunk năm nặng nhất đo được ~190s ở resync 2026-07-22 — biên an toàn 900s.
        "query_timeout": 900,
        "verify_sql": """
            SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time
            FROM `{project}.tav2_bq.ticker_prune` AS t
            WHERE t.time >= '2013-01-01'
        """,
    },
    # ticker_financial: upstream backfill/đính chính ghi vào các quý CŨ (time ≤ max đã cache),
    # nên delta-append theo max_time không bao giờ thấy chúng — cache lệch vĩnh viễn (đo thật
    # 2026-07-22: local 66.520 vs BQ 66.600, 80 dòng nằm ở ngày ≤ 2026-07-21, delta chỉ thêm +7).
    # Cùng lớp lỗi với fa_ratings/fa_ratings_8l ở trên; bảng ~54MB nên full mỗi lần là không đáng kể.
    "ticker_financial": {
        "sql": """
            SELECT * FROM `{project}.tav2_bq.ticker_financial` AS t
        """,
        "partition_col": "time",
        "full_only": True,
        "verify_sql": """
            SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time
            FROM `{project}.tav2_bq.ticker_financial` AS t
        """,
    },
    "ticker_1m": {
        "sql": """
            SELECT * FROM `{project}.tav2_bq.ticker_1m` AS t
        """,
        "partition_col": None,  # always full re-download (rolling snapshot)
        "verify_sql": """
            SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time
            FROM `{project}.tav2_bq.ticker_1m` AS t
        """,
    },
    "vnindex_5state_dt5g_live": {
        "sql": """
            SELECT * FROM `{project}.tav2_bq.vnindex_5state_dt5g_live` AS t
        """,
        "partition_col": "time",
        "verify_sql": """
            SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time
            FROM `{project}.tav2_bq.vnindex_5state_dt5g_live` AS t
        """,
    },
    "vnindex_5state": {
        "sql": """
            SELECT * FROM `{project}.tav2_bq.vnindex_5state` AS t
        """,
        "partition_col": "time",
        "verify_sql": """
            SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time
            FROM `{project}.tav2_bq.vnindex_5state` AS t
        """,
    },
    "vnindex_5state_tam_quan_v34b_clean": {
        "sql": """
            SELECT * FROM `{project}.tav2_bq.vnindex_5state_tam_quan_v34b_clean` AS t
        """,
        "partition_col": "time",
        "verify_sql": """
            SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time
            FROM `{project}.tav2_bq.vnindex_5state_tam_quan_v34b_clean` AS t
        """,
    },
    "vnindex_5state_dt_4gate": {
        "sql": """
            SELECT * FROM `{project}.tav2_bq.vnindex_5state_dt_4gate` AS t
        """,
        "partition_col": "time",
        "verify_sql": """
            SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time
            FROM `{project}.tav2_bq.vnindex_5state_dt_4gate` AS t
        """,
    },
    # fa_ratings / fa_ratings_8l: weekly refresh (Sat cron) rewrites history in place —
    # fa_ratings DELETE+INSERTs the 2 open quarters (re-rank), fa_ratings_8l republishes
    # the full table. Delta-append by max_time can never pick up rewritten rows (and the
    # re-rank can even move MAX(time) backwards), so delta leaves the cache permanently
    # diverged and trips the 23:45 count-mismatch verify every week. full_only forces a
    # full re-download even under --delta; both tables are ~MBs, cost is negligible.
    "fa_ratings": {
        "sql": """
            SELECT * FROM `{project}.tav2_bq.fa_ratings` AS t
        """,
        "partition_col": "time",
        "full_only": True,
        "verify_sql": """
            SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time
            FROM `{project}.tav2_bq.fa_ratings` AS t
        """,
    },
    "fa_ratings_8l": {
        "sql": """
            SELECT * FROM `{project}.tav2_bq.fa_ratings_8l` AS t
        """,
        "partition_col": "time",
        "full_only": True,
        "verify_sql": """
            SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time
            FROM `{project}.tav2_bq.fa_ratings_8l` AS t
        """,
    },
    "custom30v_8l": {
        "sql": """
            SELECT * FROM `{project}.tav2_bq.custom30v_8l` AS t
        """,
        "partition_col": None,  # no time column — always full
        "verify_sql": """
            SELECT COUNT(*) AS cnt
            FROM `{project}.tav2_bq.custom30v_8l` AS t
        """,
    },
    # custom30_8l (no "v") = the production table golive_recommend_v23.py reads for the
    # NEUTRAL-state idle-cash parking basket (custom30.py/custom30_history.py's "single
    # source of truth"). Missing from this cache config until 2026-07-06 — every daily
    # recommendation run silently fell back to "lookup lỗi" for the parking sleeve (no
    # live-trade impact found the day this was caught: SpaceX's plan was a HOLD). Verified
    # 2026-07-06 both tables currently hold identical content (1440 rows, same max
    # rebal_date) — added as its own cache entry rather than reusing custom30v_8l's, since
    # they are two distinct BQ tables that could diverge.
    "custom30_8l": {
        "sql": """
            SELECT * FROM `{project}.tav2_bq.custom30_8l` AS t
        """,
        "partition_col": None,  # no time column — always full
        "verify_sql": """
            SELECT COUNT(*) AS cnt
            FROM `{project}.tav2_bq.custom30_8l` AS t
        """,
    },
    "risk_rating": {
        "sql": """
            SELECT DISTINCT * FROM `{project}.tav2_bq.risk_rating` AS t
        """,
        "partition_col": None,
        "verify_sql": """
            SELECT COUNT(*) AS cnt FROM (
                SELECT DISTINCT * FROM `{project}.tav2_bq.risk_rating` AS t
            )
        """,
    },
}


def log(msg: str):
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    print(f"{ts} {msg}", flush=True)


_LOCK_HANDLE = None  # giữ tham chiếu tới khi process thoát (đóng file = nhả khoá)


def acquire_sync_lock() -> bool:
    """Khoá độc quyền LIÊN TIẾN TRÌNH cho cả cache dir. True = giữ được khoá.

    Vì sao cần: hai lần sync chạy chồng lên CÙNG `data/bq_cache` (điển hình: một full
    re-sync thủ công còn đang chạy thì cron 23:45 `--delta` khởi động) có thể để lại
    cache TRỘN VINTAGE mà manifest vẫn `verified=true` — bảng/chunk của bên này lẫn với
    bên kia, còn manifest thì bị bên ghi sau (load lúc bắt đầu, ghi lúc kết thúc) xoá
    mất phần cập nhật của bên ghi trước (lost update). Suýt xảy ra thật 2026-07-29
    (job re-pin R3): tránh được chỉ vì MAY về thứ tự ghi manifest, không phải do thiết kế.

    Non-blocking (trylock) là CHỦ ĐÍCH, khác `_otp_flow_lock` bên bot_execute.py: hai lần
    sync trùng nhau là vô tình, và một lần sync có thể chạy hàng giờ (`ticker` full ~2h)
    — bắt bên đến sau chờ chỉ để làm lại đúng việc bên kia đang làm là vô nghĩa và có
    nguy cơ treo cron. Bên đến sau thoát SẠCH với EXIT_LOCKED, không ghi gì.
    (Sync bị bỏ qua vẫn phát hiện được: `preflight_bq_cache.py` trong cùng wrapper chạy
    độc lập và cảnh báo khi `verified_at` cũ quá 36h.)
    """
    global _LOCK_HANDLE
    f = open(LOCK_PATH, "a")
    try:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        f.close()
        return False
    _LOCK_HANDLE = f
    return True


def _tmp_path(dest: str) -> str:
    """Đường dẫn file tạm CÙNG thư mục với đích (bắt buộc: os.replace chỉ atomic khi
    cùng filesystem) và có PID (phòng xa — khoá đã chặn 2 syncer, nhưng nếu ai đó chạy
    sync ngoài khoá thì 2 tiến trình cũng không cướp file tạm của nhau)."""
    d, base = os.path.split(dest)
    return os.path.join(d, f".{base}.{os.getpid()}{TMP_SUFFIX}")


def atomic_to_parquet(df: pd.DataFrame, dest: str):
    """Ghi parquet kiểu tmp + os.replace (coding_guidelines §5, giống `_save_state()`
    trong trading_bot/executor.py).

    `df.to_parquet(dest)` ghi ĐÈ TRỰC TIẾP lên đích: bị kill/OOM/hết đĩa giữa lúc ghi là
    để lại chunk parquet cụt (footer thiếu) — lần đọc sau crash hoặc, tệ hơn, đọc thiếu
    dòng mà không ai biết. os.replace là một rename atomic trên POSIX: người đọc luôn
    thấy HOẶC bản cũ nguyên vẹn HOẶC bản mới nguyên vẹn, không có ở giữa.
    Lợi ích kèm theo: file mới là inode mới, nên snapshot vintage bằng hardlink không
    còn bị hỏng lặng lẽ (trước đây to_parquet đè lên chính inode đang được hardlink).
    """
    tmp = _tmp_path(dest)
    try:
        df.to_parquet(tmp, index=False)
        os.replace(tmp, dest)
    except BaseException:
        # BaseException để dọn cả khi SIGINT/SystemExit; SIGKILL thì không dọn được —
        # đó là việc của sweep_stale_tmp() ở lần chạy sau (rác .tmp có thể là hàng trăm MB).
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


def sweep_stale_tmp():
    """Xoá file tạm còn sót từ lần chạy bị kill cứng (SIGKILL/reboot). Chỉ gọi khi ĐANG
    GIỮ khoá — lúc đó không tiến trình sync nào khác đang ghi, nên mọi *.tmp đều là rác."""
    n = 0
    for root, _dirs, files in os.walk(CACHE_DIR):
        for fn in files:
            if fn.endswith(TMP_SUFFIX):
                try:
                    os.remove(os.path.join(root, fn))
                    n += 1
                except OSError:
                    pass
    if n:
        log(f"  dọn {n} file tạm sót lại từ lần chạy trước bị kill")


def bq_query_to_df(
    sql: str,
    max_rows: int = 10_000_000,
    timeout: int = DEFAULT_QUERY_TIMEOUT,
) -> pd.DataFrame:
    """Run a BQ query via bq CLI subprocess, return DataFrame.

    Uses gcloud auth login credentials (no ADC/Application-Default required).
    """
    sql = sql.format(project=PROJECT)
    result = subprocess.run(
        [
            BQ_BIN, "query",
            "--use_legacy_sql=false",
            f"--project_id={PROJECT}",
            "--format=csv",
            f"--max_rows={max_rows}",
        ],
        input=sql,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=_SUBPROCESS_ENV,
    )
    if result.returncode != 0:
        raise RuntimeError(f"bq CLI error: {result.stderr.strip()}")
    stdout = result.stdout.strip()
    if not stdout:
        return pd.DataFrame()
    df = pd.read_csv(io.StringIO(stdout))
    return _apply_date_dtypes(df)


def load_manifest() -> dict:
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH) as f:
            return json.load(f)
    return {"tables": {}, "verified": False}


def save_manifest(manifest: dict):
    # tmp + os.replace: manifest.json là "cổng" của cả cache (bq_local_cache.py từ chối
    # chạy nếu verified=false / thiếu bảng) — một bản cụt vì bị kill giữa lúc ghi làm
    # MỌI consumer đọc cache fail cứng, kể cả khi parquet vẫn nguyên.
    tmp = _tmp_path(MANIFEST_PATH)
    try:
        with open(tmp, "w") as f:
            json.dump(manifest, f, indent=2, default=str)
        os.replace(tmp, MANIFEST_PATH)
    except BaseException:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


def download_table(name: str, config: dict, manifest: dict, delta: bool):
    """Download a table to parquet. Delta mode appends only new rows."""
    if config.get("full_only"):
        delta = False  # source table is rewritten in place — delta-append can't track it
    pq_path = os.path.join(CACHE_DIR, f"{name}.parquet")
    table_info = manifest["tables"].get(name, {})
    qtimeout = config.get("query_timeout", DEFAULT_QUERY_TIMEOUT)

    chunk_years = config.get("chunk_years")

    if delta and config["partition_col"] and chunk_years:
        chunk_dir = os.path.join(CACHE_DIR, name)
        max_cached = table_info.get("max_time")
        if max_cached and os.path.isdir(chunk_dir):
            max_year = int(max_cached[:4])
            log(f"  {name}: delta — re-downloading {max_year}+ ...")
            col = config["partition_col"]
            total_rows = 0
            max_time_val = None
            for yr in chunk_years:
                yr_path = os.path.join(chunk_dir, f"{yr}.parquet")
                if yr < max_year and os.path.exists(yr_path):
                    # Chỉ cần ĐẾM dòng — dùng parquet metadata thay vì đọc cả cột qua
                    # pandas: rẻ hơn nhiều và miễn nhiễm với dtype lạ trong file cũ
                    # (dbdate crash ở trên xảy ra đúng tại dòng này trước khi sửa).
                    yr_rows = _pq.read_metadata(yr_path).num_rows
                    total_rows += yr_rows
                    continue
                yr_sql = (
                    config["sql"]
                    + f" AND t.{col} >= '{yr}-01-01' AND t.{col} < '{yr + 1}-01-01'"
                )
                yr_df = bq_query_to_df(yr_sql, timeout=qtimeout)
                if not yr_df.empty:
                    atomic_to_parquet(yr_df, yr_path)
                    total_rows += len(yr_df)
                    yr_max = pd.to_datetime(yr_df[col]).max()
                    if max_time_val is None or yr_max > max_time_val:
                        max_time_val = yr_max
                    log(f"    {yr}: {len(yr_df)} rows")
            table_info["rows"] = total_rows
            if max_time_val is not None:
                table_info["max_time"] = str(max_time_val.date())
            manifest["tables"][name] = table_info
            log(f"  {name}: {total_rows} total rows")
            return

    if delta and config["partition_col"] and os.path.exists(pq_path):
        max_cached = table_info.get("max_time")
        if max_cached:
            log(f"  {name}: delta from {max_cached}")
            col = config["partition_col"]
            # SQL gốc có WHERE (vd ticker: WHERE t.time >= '2013-01-01') → nối AND;
            # KHÔNG có WHERE (vd các bảng vnindex_5state*) → phải mở WHERE mới. Trước
            # 2026-07-06 luôn nối cứng "AND" → SQL sai cú pháp cho nhóm bảng sau, delta
            # các bảng đó fail ÂM THẦM mỗi đêm (bq CLI error với stderr trống) — cache
            # vnindex_5state* kẹt vĩnh viễn ở ngày full-download gần nhất.
            joiner = "AND" if "WHERE" in config["sql"].upper() else "WHERE"
            delta_sql = config["sql"] + f" {joiner} t.{col} > '{max_cached}'"
            new_df = bq_query_to_df(delta_sql, timeout=qtimeout)
            if new_df.empty:
                log(f"  {name}: no new rows")
                return
            existing = pd.read_parquet(pq_path)
            combined = pd.concat([existing, new_df], ignore_index=True)
            atomic_to_parquet(combined, pq_path)
            table_info["rows"] = len(combined)
            if col in combined.columns:
                table_info["max_time"] = str(
                    pd.to_datetime(combined[col]).max().date()
                )
            log(f"  {name}: +{len(new_df)} rows → {len(combined)} total")
            manifest["tables"][name] = table_info
            return

    # Full download — chunk by year for large partitioned tables to avoid token expiry
    chunk_years = config.get("chunk_years")
    if chunk_years:
        log(f"  {name}: chunked download ({chunk_years[0]}–{chunk_years[-1]})...")
        col = config["partition_col"]
        chunk_dir = os.path.join(CACHE_DIR, name)
        os.makedirs(chunk_dir, exist_ok=True)
        total_rows = 0
        max_time_val = None
        for yr in chunk_years:
            yr_sql = (
                config["sql"]
                + f" AND t.{col} >= '{yr}-01-01' AND t.{col} < '{yr + 1}-01-01'"
            )
            yr_df = bq_query_to_df(yr_sql, timeout=qtimeout)
            if not yr_df.empty:
                yr_path = os.path.join(chunk_dir, f"{yr}.parquet")
                atomic_to_parquet(yr_df, yr_path)
                total_rows += len(yr_df)
                yr_max = pd.to_datetime(yr_df[col]).max()
                if max_time_val is None or yr_max > max_time_val:
                    max_time_val = yr_max
                log(f"    {yr}: {len(yr_df)} rows")
        if total_rows == 0:
            log(f"  {name}: 0 rows (empty)")
            return
        total_size = sum(
            os.path.getsize(os.path.join(chunk_dir, f))
            for f in os.listdir(chunk_dir) if f.endswith(".parquet")
        ) / 1e6
        table_info = {
            "file": f"{name}/",
            "rows": total_rows,
            "size_mb": round(total_size, 1),
        }
        if max_time_val is not None:
            table_info["max_time"] = str(max_time_val.date())
        manifest["tables"][name] = table_info
        log(f"  {name}: {total_rows} rows, {total_size:.1f} MB")
        return

    log(f"  {name}: full download...")
    df = bq_query_to_df(config["sql"], timeout=qtimeout)

    if df.empty:
        log(f"  {name}: 0 rows (empty)")
        return

    atomic_to_parquet(df, pq_path)
    size_mb = os.path.getsize(pq_path) / 1e6
    table_info = {
        "file": f"{name}.parquet",
        "rows": len(df),
        "size_mb": round(size_mb, 1),
    }
    if config["partition_col"] and config["partition_col"] in df.columns:
        table_info["max_time"] = str(
            pd.to_datetime(df[config["partition_col"]]).max().date()
        )
    manifest["tables"][name] = table_info
    log(f"  {name}: {len(df)} rows, {size_mb:.1f} MB")


def _check_parquet_date_dtypes(pq_path: str) -> list:
    """Return list of 'col:type' for DATE_COLS stored as non-date in parquet schema."""
    try:
        import pyarrow.parquet as pq
        path = pq_path.rstrip("/")
        if pq_path.endswith("/"):
            files = [
                os.path.join(path, f)
                for f in os.listdir(path)
                if f.endswith(".parquet")
            ]
            if not files:
                return []
            schema = pq.read_schema(files[0])
        else:
            schema = pq.read_schema(path)
        bad = []
        for field in schema:
            if field.name in DATE_COLS:
                t = str(field.type)
                if "date" not in t.lower():
                    bad.append(f"{field.name}:{t}")
        return bad
    except Exception as e:
        return [f"schema_read_error:{e}"]


def verify_all(manifest: dict) -> bool:
    """Compare local cache against BQ row counts, max dates, and date column dtypes."""
    log("Verifying cache against BigQuery...")
    all_ok = True
    for name, config in TABLES.items():
        table_info = manifest["tables"].get(name)
        if not table_info:
            log(f"  {name}: MISSING from cache")
            all_ok = False
            continue

        file_ref = table_info.get("file", f"{name}.parquet")
        pq_path = os.path.join(CACHE_DIR, file_ref)
        # chunked tables store a trailing slash dir; single tables store .parquet
        if not os.path.exists(pq_path.rstrip("/")):
            log(f"  {name}: parquet file/dir missing ({pq_path})")
            all_ok = False
            continue

        verify_sql = config.get("verify_sql")
        if not verify_sql:
            continue

        try:
            bq_stats = bq_query_to_df(verify_sql)
        except Exception as e:
            log(f"  {name}: BQ verify query failed: {e}")
            all_ok = False
            continue

        bq_cnt = int(bq_stats["cnt"].iloc[0])
        local_cnt = table_info["rows"]

        # Allow small tolerance for tables that might have concurrent writes
        tolerance = max(50, int(bq_cnt * 0.001))
        cnt_ok = abs(bq_cnt - local_cnt) <= tolerance

        if "max_time" in bq_stats.columns and "max_time" in table_info:
            bq_max = str(pd.to_datetime(bq_stats["max_time"].iloc[0]).date())
            local_max = table_info["max_time"]
            date_ok = bq_max == local_max
        else:
            bq_max = "n/a"
            local_max = "n/a"
            date_ok = True

        # dtype check: date columns must NOT be stored as VARCHAR/string in parquet
        dtype_bad = _check_parquet_date_dtypes(pq_path)

        if cnt_ok and date_ok and not dtype_bad:
            log(f"  {name}: OK ({local_cnt} rows, max={local_max})")
        else:
            issues = []
            if not cnt_ok:
                issues.append(f"count local={local_cnt} vs BQ={bq_cnt}")
            if not date_ok:
                issues.append(f"max_time local={local_max} vs BQ={bq_max}")
            if dtype_bad:
                issues.append(f"DTYPE_MISMATCH {dtype_bad}")
            log(f"  {name}: FAIL — {'; '.join(issues)}")
            all_ok = False

    manifest["verified"] = all_ok
    manifest["verified_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    manifest["verified_at_epoch"] = time.time()
    return all_ok


def main():
    parser = argparse.ArgumentParser(description="Sync BQ tables to local cache")
    parser.add_argument(
        "--delta", action="store_true",
        help="Delta mode: only download new rows since last sync"
    )
    parser.add_argument(
        "--verify", action="store_true",
        help="Verify only, no download"
    )
    parser.add_argument(
        "--tables", nargs="+",
        help="Sync specific tables (default: all)"
    )
    parser.add_argument(
        "--skip-verify", action="store_true",
        help="Skip verification after download"
    )
    args = parser.parse_args()

    os.makedirs(CACHE_DIR, exist_ok=True)

    # Khoá TRƯỚC load_manifest(): kể cả `--verify` (không tải gì) vẫn ghi lại manifest.json,
    # nên chạy song song với một lần sync sẽ xoá mất phần cập nhật của bên kia.
    if not acquire_sync_lock():
        log(f"BỎ QUA: một tiến trình sync_bq_cache.py khác đang giữ khoá {LOCK_PATH} "
            f"(pgrep -af sync_bq_cache để xem) — thoát sạch, không ghi gì "
            f"(exit {EXIT_LOCKED}, không phải lỗi).")
        sys.exit(EXIT_LOCKED)
    sweep_stale_tmp()

    manifest = load_manifest()

    if not args.verify:
        target_tables = args.tables or list(TABLES.keys())
        # Sort: small tables first (fast feedback), big tables last
        size_order = {
            "custom30v_8l": 0, "custom30_8l": 0, "risk_rating": 1,
            "vnindex_5state": 2, "vnindex_5state_dt5g_live": 2,
            "vnindex_5state_tam_quan_v34b_clean": 2,
            "vnindex_5state_dt_4gate": 2,
            "fa_ratings": 3, "fa_ratings_8l": 3,
            "ticker_financial": 4, "ticker_1m": 5, "universe_pit_q": 5,
            "ticker_prune": 6, "ticker": 7,
        }
        target_tables.sort(key=lambda t: size_order.get(t, 99))

        log(f"Syncing {len(target_tables)} tables ({'delta' if args.delta else 'full'})...")
        for name in target_tables:
            if name not in TABLES:
                log(f"  {name}: unknown table, skipping")
                continue
            try:
                download_table(name, TABLES[name], manifest, args.delta)
            except Exception as e:
                log(f"  {name}: FAILED — {e}")
                import traceback
                traceback.print_exc()
        save_manifest(manifest)

    # Verify
    if not args.skip_verify:
        ok = verify_all(manifest)
        save_manifest(manifest)
        if ok:
            log("Cache verified OK — ready for local queries")
        else:
            log("Cache verification FAILED — some tables are stale or missing")
            sys.exit(1)
    else:
        log("Verification skipped (--skip-verify)")


if __name__ == "__main__":
    main()
