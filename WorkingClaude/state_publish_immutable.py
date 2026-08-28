# -*- coding: utf-8 -*-
"""
state_publish_immutable.py — BẢNG CÔNG BỐ BẤT BIẾN cho chuỗi 5-state (base v3.4b + DT5G).

NGUYÊN TẮC (user duyệt 2026-07-30, đề xuất §5 rolling_vs_expanding_dt5g_20260729.md):
    State của MỘT PHIÊN ĐÃ CÔNG BỐ là SỰ KIỆN ĐÃ XẢY RA (ta đã hành động theo nó),
    không phải một ước lượng được phép cập nhật.

Publisher chỉ được làm 3 việc:
  (a) APPEND phiên mới;
  (b) RECOMPUTE một ĐUÔI NGẮN chưa chốt (SEAL_N = 25 phiên giao dịch);
  (c) KHÔNG BAO GIỜ ghi đè phiên ĐÃ CHỐT. Nếu công thức/dữ liệu mới cho kết quả khác ở
      phần đã chốt → ghi thành VINTAGE MỚI (`<table>_vintage_YYYYMMDD`), KHÔNG đè bảng cũ.

VÌ SAO (RCA mike/agents/Winston/research/dt5g_history_restate_rca_20260729.md):
chain rebuild TOÀN BỘ lịch sử mỗi đêm rồi `bq load --replace` đè bảng. Upstream (`ticker`,
`ticker_prune`) DROP+CREATE mỗi ngày, nên backfill/điều chỉnh hồi tố (PE backfill 2006+,
corp-action re-adjust Close, ticker_prune membership) lan qua các cửa sổ EXPANDING
(pe_p90, expanding_pct_rank, rank-of-rank, running_max) và VIẾT LẠI state của phiên đã đóng
nhiều năm trước. 2026-07-29: 134 phiên base + 101 phiên dt5g_live bị viết lại IM LẶNG.
Backtest 2018 khi đó đang dùng state tính bằng dữ liệu PE backfill năm 2026 — dữ liệu KHÔNG
HỀ TỒN TẠI vào 2018 (một dạng look-ahead tinh vi). Module này khử 100% lớp sự cố đó, kể cả
kênh corp-action mà đổi rolling-window không chạm tới, với RỦI RO MÔ HÌNH = 0 (công thức
tính state không đổi một dòng nào; chỉ đổi CÁCH GHI).

SEAL_N = 25 — cơ sở, đo thật chứ không đoán (job Taylor_20260730_013951):
  · Chân trên: `enC`/`enX` của DT-4gate = 25 phiên — dưới ngưỡng này một state mới còn CHƯA
    THỂ commit, nên chưa thể coi là chốt.
  · Chân dưới (hiệu ứng viết-lại DO CHÍNH MÔ HÌNH, không do dữ liệu): các bộ làm mượt
    `min_stay_filter` là KHÔNG NHÂN QUẢ — một run ngắn ở cuối chuỗi bị ghi đè bằng state
    trước đó rồi tự phục hồi khi run dài ra. Đo trên chuỗi thật (200 điểm cắt, 2000 phiên
    gần nhất): ew_v1 (mode15+min_stay7) = tối đa **5 phiên**; leg v3.4b (mode3+min_stay2)
    = **0 phiên**. `_dt_4gate` và `_commit` (cap) là nhân quả thuần → 0.
  ⇒ 25 phiên = ~5× biên độ viết-lại nội tại lớn nhất, đồng thời phủ trọn cam kết DT-gate.
  Đổi SEAL_N là ĐỔI NGỮ NGHĨA CÔNG BỐ — cần user duyệt, không phải tham số tinh chỉnh.

CÁCH GHI (không dùng `--replace` nữa):
  new series -> staging table -> MERGE **chỉ trên `time > cutoff`**, với CẢ BA nhánh
  (MATCHED / NOT MATCHED BY TARGET / NOT MATCHED BY SOURCE) đều bị chặn cứng bởi điều kiện
  `time > cutoff`. Phần đã chốt vì thế KHÔNG BAO GIỜ nằm trong phạm vi câu lệnh ghi — đây là
  bảo đảm CẤU TRÚC, không phải bảo đảm bằng cẩn thận. Checksum vùng đã chốt được chụp
  TRƯỚC và SAU mỗi lần MERGE và phải khớp tuyệt đối, nếu không → abort + alert.

CỘT `asof_date`: ngày GIÁ TRỊ của dòng đó được ghi/đổi lần cuối (không phải ngày chạm gần
nhất). Dòng không đổi giá trị thì giữ nguyên asof_date cũ ⇒ đọc được ngay "dòng này ổn định
từ bao giờ". Dòng đã chốt giữ asof_date vĩnh viễn.

TELEMETRY QUAN TRỌNG NHẤT — `n_sealed_diff`: số phiên ĐÃ CHỐT mà bản tính mới hôm nay KHÁC
bản đã công bố. Đây chính là số phiên mà `bq load --replace` cũ SẼ ÂM THẦM VIẾT LẠI. Giờ nó
KHÔNG được áp dụng, chỉ được ĐẾM và cảnh báo — biến sự cố im lặng thành số liệu quan sát được
(`data/immutable_publish_history.jsonl`).

Quan hệ với `restate_guard.sh`: guard là LƯỚI AN TOÀN DỰ PHÒNG, giữ nguyên. Module này chặn
từ gốc; guard bắt trường hợp có bug tương lai vượt qua được chặn đó.

API:
    publish_immutable(new_df|csv_path, table, label, seal_n=25) -> dict(stats)
CLI (dùng trong daily_refresh_v34b_linux.sh):
    python state_publish_immutable.py --csv <file.csv> --table tav2_bq.vnindex_5state \
        --label "vnindex_5state (base v3.4b)"
"""
import os, sys, io, json, subprocess, tempfile
from datetime import datetime, date, timezone
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
PROJECT = "lithe-record-440915-m9"
LOCATION = "asia-southeast1"
SEAL_N = 25                      # phiên giao dịch chưa chốt ở đuôi (xem docstring)
HISTORY = os.path.join(WORKDIR, "data", "immutable_publish_history.jsonl")
# Ngưỡng cảnh báo cho n_sealed_diff. 0 = mọi phân kỳ ở vùng đã chốt đều đáng báo, vì với
# thiết kế này nó KHÔNG còn là "chuyện thường ngày" mà là bằng chứng upstream đã restate.
SEALED_DIFF_ALERT = int(os.environ.get("IMMUTABLE_SEALED_DIFF_ALERT", "0"))


class PublishAbort(RuntimeError):
    """Điều kiện an toàn không thoả → KHÔNG ghi gì cả (fail-closed)."""


# ── BQ helpers (subprocess `bq`, không phụ thuộc simulate_holistic_nav) ───────────────────
def _bq_query(sql, dry=False):
    # --max_rows: `bq query` mặc định CHỈ IN 100 DÒNG ĐẦU (mặc định hiển thị, không phải
    # giới hạn query) — đọc thiếu mà không báo lỗi. Bắt buộc đặt tường minh.
    cmd = ["bq", "query", "--use_legacy_sql=false", f"--project_id={PROJECT}",
           "--format=csv", "--quiet", "--max_rows=10000000"]
    if dry:
        cmd.append("--dry_run")
    cmd.append(sql)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise PublishAbort(f"bq query failed (rc={r.returncode}): "
                           f"{(r.stderr or r.stdout).strip()[:500]}")
    txt = (r.stdout or "").strip()
    if not txt:
        return pd.DataFrame()
    return pd.read_csv(io.StringIO(txt))


def _bq_load(table, csv_path, schema):
    cmd = ["bq", "load", "--replace", "--source_format=CSV", "--skip_leading_rows=1",
           f"--location={LOCATION}", f"--schema={schema}",
           f"{PROJECT}:{table}", csv_path]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise PublishAbort(f"bq load {table} failed (rc={r.returncode}): "
                           f"{(r.stderr or r.stdout).strip()[:500]}")


def _table_exists(table):
    r = subprocess.run(["bq", "show", "--format=none", f"{PROJECT}:{table}"],
                       capture_output=True, text=True, timeout=120)
    return r.returncode == 0


def _columns(table):
    r = subprocess.run(["bq", "show", "--schema", "--format=prettyjson",
                        f"{PROJECT}:{table}"], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise PublishAbort(f"bq show schema {table} failed: {(r.stderr or r.stdout)[:300]}")
    return [c["name"] for c in json.loads(r.stdout)]


def _alert(msg):
    """Best-effort, NEVER raises (cùng hợp đồng với macro_state_live._alert).
    IMMUTABLE_NO_ALERT=1 -> chỉ in ra (self-check/dry-run không được spam Telegram đội)."""
    if os.environ.get("IMMUTABLE_NO_ALERT") == "1":
        print(f"  [alert suppressed] {msg}")
        return
    for argv in ([os.path.join(WORKDIR, "mike/bin/notify.sh"), msg],):
        try:
            if os.path.exists(argv[0]):
                subprocess.run(argv, timeout=15)
                return
        except Exception:
            pass
    print(f"[state_publish_immutable._alert] (no channel) {msg}")


# ── migration / vintage ──────────────────────────────────────────────────────────────────
def snapshot_vintage(table, tag=None):
    """Đóng băng bảng hiện tại thành 1 vintage BẤT BIẾN `<table>_vintage_<tag>`.
    Idempotent (IF NOT EXISTS): chạy lại cùng ngày không đè vintage đã chụp.
    KHÔNG bị prune bởi vòng dọn backup 5-bản của daily_refresh (tên khác hẳn) — vintage là
    mỏ neo tái lập backtest, không phải backup vận hành."""
    tag = tag or datetime.now().strftime("%Y%m%d")
    short = table.split(".")[-1]
    vt = f"{table.rsplit('.', 1)[0]}.{short}_vintage_{tag}"
    _bq_query(f"CREATE TABLE IF NOT EXISTS `{PROJECT}.{vt}` AS "
              f"SELECT * FROM `{PROJECT}.{table}`")
    return vt


def ensure_asof_column(table, migration_date=None):
    """Thêm cột `asof_date` nếu chưa có và backfill = ngày migration.

    Ý nghĩa của lần backfill này: TOÀN BỘ lịch sử hiện có được ĐÓNG BĂNG làm BASELINE tại
    thời điểm triển khai (bao gồm cả phần đã bị restate ngày 2026-07-29 — ta chấp nhận bản
    đó là "sự thật đã công bố" và dừng vòng lặp tại đây, đúng yêu cầu migration).
    Idempotent: bảng đã có cột thì không làm gì."""
    if "asof_date" in _columns(table):
        return False
    md = migration_date or date.today().isoformat()
    _bq_query(f"ALTER TABLE `{PROJECT}.{table}` ADD COLUMN IF NOT EXISTS asof_date DATE")
    _bq_query(f"UPDATE `{PROJECT}.{table}` SET asof_date = DATE '{md}' "
              f"WHERE asof_date IS NULL")
    print(f"  [migration] {table}: added asof_date, backfilled = {md} (baseline đóng băng)")
    return True


# ── core ─────────────────────────────────────────────────────────────────────────────────
def _load_new(src):
    df = src if isinstance(src, pd.DataFrame) else pd.read_csv(src)
    missing = {"time", "state", "state_raw"} - set(df.columns)
    if missing:
        raise PublishAbort(f"new series thiếu cột {sorted(missing)}")
    df = df[["time", "state", "state_raw"]].copy()
    df["time"] = pd.to_datetime(df["time"])
    if df["time"].duplicated().any():
        raise PublishAbort("new series có ngày TRÙNG — từ chối publish")
    if df[["state", "state_raw"]].isna().any().any():
        raise PublishAbort("new series có state/state_raw NULL — từ chối publish")
    return df.sort_values("time").reset_index(drop=True)


def publish_immutable(src, table, label, seal_n=SEAL_N, asof=None, project=PROJECT):
    """Công bố `src` vào `table` theo hợp đồng bất biến. Trả về dict thống kê.

    Fail-CLOSED: bất kỳ điều kiện an toàn nào không thoả -> PublishAbort, KHÔNG ghi gì."""
    asof = asof or date.today().isoformat()
    new = _load_new(src)
    short = table.split(".")[-1]
    stage = f"{table.rsplit('.', 1)[0]}.{short}__pubstage"

    print(f"  [immutable] {label}: new series {len(new)} rows "
          f"{new['time'].iloc[0].date()} -> {new['time'].iloc[-1].date()}")

    # ── bootstrap: bảng chưa tồn tại -> nạp toàn bộ, coi như baseline đóng băng ──
    if not _table_exists(table):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="") as f:
            b = new.copy(); b["time"] = b["time"].dt.strftime("%Y-%m-%d"); b["asof_date"] = asof
            b.to_csv(f.name, index=False); path = f.name
        try:
            _bq_load(table, path, "time:DATE,state:INT64,state_raw:INT64,asof_date:DATE")
        finally:
            os.unlink(path)
        st = {"label": label, "table": table, "mode": "bootstrap", "n_rows": len(new),
              "cutoff": None, "asof": asof}
        print(f"  [immutable] BOOTSTRAP: nạp {len(new)} dòng (bảng chưa tồn tại)")
        _record(st)
        return st

    ensure_asof_column(table, migration_date=asof)

    # ── ranh giới CHỐT: seal_n phiên gần nhất CỦA CHUỖI MỚI là chưa chốt ──
    if len(new) <= seal_n:
        raise PublishAbort(f"new series chỉ {len(new)} dòng <= seal_n={seal_n} — "
                           f"không xác định được vùng đã chốt, từ chối publish")
    cutoff = new["time"].iloc[-(seal_n + 1)].date().isoformat()

    pub = _bq_query(f"SELECT COUNT(*) n, MAX(time) mx FROM `{project}.{table}`")
    pub_n = int(pub["n"].iloc[0]); pub_mx = str(pub["mx"].iloc[0])
    if pub_n == 0:
        raise PublishAbort(f"{table} tồn tại nhưng RỖNG — nghi ngờ sự cố, từ chối publish "
                           f"(xử lý tay: drop bảng để đi nhánh bootstrap, hoặc restore vintage)")
    # Chuỗi mới TỤT HẬU so với bản đã công bố => nhánh NOT MATCHED BY SOURCE sẽ XOÁ những
    # phiên mới hơn đã công bố. Đó là mất dữ liệu công bố, không phải "recompute đuôi".
    if new["time"].iloc[-1].date().isoformat() < pub_mx:
        raise PublishAbort(f"new series max={new['time'].iloc[-1].date()} < published max={pub_mx} "
                           f"— chuỗi tính mới BỊ TỤT HẬU (compute lỗi/stale), từ chối publish")

    # MD5 của chuỗi đã SẮP XẾP theo time — chính xác tuyệt đối và nhạy với MỌI thay đổi
    # (giá trị, thêm dòng, mất dòng, đổi thứ tự). Không dùng SUM(FARM_FINGERPRINT): tràn INT64
    # trên ~6.300 dòng (đo thật), và tổng còn có thể trùng khi hai thay đổi triệt tiêu nhau.
    ck_sql = (f"SELECT COUNT(*) n, IFNULL(TO_HEX(MD5(STRING_AGG(FORMAT('%t|%d|%d', time, "
              f"IFNULL(state,-1), IFNULL(state_raw,-1)), ',' ORDER BY time))),'') ck "
              f"FROM `{project}.{table}` WHERE time <= DATE '{cutoff}'")

    # ── staging: nạp TOÀN BỘ chuỗi mới (rẻ) để đo được cả phân kỳ vùng đã chốt ──
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="") as f:
        s = new.copy(); s["time"] = s["time"].dt.strftime("%Y-%m-%d")
        s.to_csv(f.name, index=False); path = f.name
    try:
        _bq_load(stage, path, "time:DATE,state:INT64,state_raw:INT64")
    finally:
        os.unlink(path)

    # ── TELEMETRY: `bq load --replace` cũ SẼ viết lại bao nhiêu phiên đã chốt? ──
    div = _bq_query(f"""
WITH t AS (SELECT * FROM `{project}.{table}`  WHERE time <= DATE '{cutoff}'),
     s AS (SELECT * FROM `{project}.{stage}`  WHERE time <= DATE '{cutoff}')
SELECT
  COUNTIF(t.time IS NOT NULL AND s.time IS NOT NULL
          AND (t.state IS DISTINCT FROM s.state
               OR t.state_raw IS DISTINCT FROM s.state_raw))      AS n_sealed_diff,
  COUNTIF(t.time IS NULL)                                          AS n_sealed_only_new,
  COUNTIF(s.time IS NULL)                                          AS n_sealed_only_pub,
  IFNULL(ARRAY_TO_STRING(ARRAY_AGG(
    IF(t.time IS NOT NULL AND s.time IS NOT NULL AND t.state IS DISTINCT FROM s.state,
       FORMAT('%t %d->%d', t.time, t.state, s.state), NULL)
    IGNORE NULLS ORDER BY t.time LIMIT 8), ' | '), '')             AS sample
FROM t FULL OUTER JOIN s ON t.time = s.time""")
    n_sealed_diff = int(div["n_sealed_diff"].iloc[0])
    n_sealed_only_new = int(div["n_sealed_only_new"].iloc[0])
    n_sealed_only_pub = int(div["n_sealed_only_pub"].iloc[0])
    sample = str(div["sample"].iloc[0]) if not pd.isna(div["sample"].iloc[0]) else ""

    # ── VÁ LỖ HỔNG: phiên nằm trong vùng đã chốt nhưng CHƯA TỪNG được công bố ──
    # Chỉ xảy ra khi publisher chết > seal_n phiên liên tiếp. Chèn chúng KHÔNG vi phạm nguyên
    # tắc bất biến — bất biến = "không ghi đè phiên ĐÃ CÔNG BỐ"; ở đây chưa có gì được công bố
    # cho ngày đó, nên đây là APPEND. Nếu không vá, chuỗi công bố sẽ THỦNG LỖ VĨNH VIỄN
    # (downstream đọc thiếu phiên mà không có gì báo) — hỏng hơn hẳn.
    # An toàn cấu trúc: INSERT + anti-join, câu lệnh này KHÔNG THỂ sửa dòng đã có.
    if n_sealed_only_new > 0:
        _bq_query(f"""
INSERT INTO `{project}.{table}` (time, state, state_raw, asof_date)
SELECT s.time, s.state, s.state_raw, DATE '{asof}'
FROM `{project}.{stage}` s
LEFT JOIN `{project}.{table}` t ON t.time = s.time
WHERE s.time <= DATE '{cutoff}' AND t.time IS NULL""")
        _alert(f"⚠️ GAP-FILL — {label}: {n_sealed_only_new} phiên nằm trong vùng đã chốt "
               f"(<= {cutoff}) nhưng CHƯA TỪNG được công bố → đã APPEND (không ghi đè gì). "
               f"Nghĩa là publisher đã không chạy > {seal_n} phiên liên tiếp — kiểm tra cron.")
        print(f"  [immutable] GAP-FILL: append {n_sealed_only_new} phiên đã chốt chưa từng công bố")

    # ── checksum vùng đã chốt NGAY TRƯỚC MERGE (sau khi đã vá lỗ hổng) ──
    pre = _bq_query(ck_sql)
    pre_n, pre_ck = int(pre["n"].iloc[0]), str(pre["ck"].iloc[0])
    # Ảnh chụp ĐUÔI trước MERGE để đếm ĐÚNG số dòng thực sự đổi giá trị. (Không đếm bằng
    # `asof_date = today`: ngay sau migration MỌI dòng đều mang asof_date hôm nay ⇒ đếm ra
    # 25/25 "đã đổi" trong khi thực tế không dòng nào đổi — số liệu sai lệch, đo thật 07-30.)
    tail_before = _bq_query(f"SELECT time, state, state_raw FROM `{project}.{table}` "
                            f"WHERE time > DATE '{cutoff}' ORDER BY time")

    # ── MERGE: CẢ BA nhánh đều bị chặn cứng bởi `time > cutoff` ──
    # Vùng đã chốt KHÔNG NẰM TRONG phạm vi câu lệnh — bảo đảm cấu trúc, không phải cẩn thận.
    # `OR T.asof_date IS NULL` trong WHEN MATCHED (thêm 2026-08-28): writer thứ hai ngoài luồng
    # (kaffa_v2, xem mike/agents/Winston/dt5g_live_second_writer_20260729.md) ghi lại state
    # ĐÚNG giá trị nhưng KHÔNG set asof_date. Khi state/state_raw không đổi (chuỗi đứng yên
    # nhiều phiên), điều kiện cũ không khớp -> asof_date NULL vĩnh viễn (26 phiên
    # 2026-07-24..2026-08-28 trong tail đo được). Không đổi kết quả state/state_raw.
    merge_sql = f"""
MERGE `{project}.{table}` T
USING (SELECT * FROM `{project}.{stage}` WHERE time > DATE '{cutoff}') S
ON T.time = S.time AND T.time > DATE '{cutoff}'
WHEN MATCHED AND (T.state IS DISTINCT FROM S.state
                  OR T.state_raw IS DISTINCT FROM S.state_raw
                  OR T.asof_date IS NULL) THEN
  UPDATE SET state = S.state, state_raw = S.state_raw, asof_date = DATE '{asof}'
WHEN NOT MATCHED BY TARGET THEN
  INSERT (time, state, state_raw, asof_date)
  VALUES (S.time, S.state, S.state_raw, DATE '{asof}')
WHEN NOT MATCHED BY SOURCE AND T.time > DATE '{cutoff}' THEN DELETE"""
    _bq_query(merge_sql)

    # Dọn staging NGAY sau lần dùng cuối (MERGE là lần đọc `stage` cuối cùng). Nếu không dọn,
    # dataset tích lại bảng `*__pubstage` trông y như một nguồn dữ liệu thật — đúng loại bẫy
    # coding_guidelines §9/§10 cảnh báo (agent sau grep thấy tên gần giống và đọc nhầm).
    # Đặt ở ĐÂY, không phải cuối hàm: mọi nhánh sau đây (kể cả nhánh raise PublishAbort khi
    # phát hiện vi phạm bất biến) đều đã sạch. Ngoại lệ xảy ra TRƯỚC MERGE thì lần chạy sau
    # `bq load --replace` ghi đè, không tích luỹ.
    subprocess.run(["bq", "rm", "-f", "-t", f"{project}:{stage}"],
                   capture_output=True, text=True, timeout=180)

    # ── checksum SAU: vùng đã chốt phải y hệt, từng byte ──
    post = _bq_query(ck_sql)
    post_n, post_ck = int(post["n"].iloc[0]), str(post["ck"].iloc[0])
    sealed_ok = (pre_n == post_n and pre_ck == post_ck)

    tail_after = _bq_query(f"SELECT time, state, state_raw FROM `{project}.{table}` "
                           f"WHERE time > DATE '{cutoff}' ORDER BY time")
    b = {r["time"]: (r["state"], r["state_raw"]) for _, r in tail_before.iterrows()}
    a = {r["time"]: (r["state"], r["state_raw"]) for _, r in tail_after.iterrows()}
    n_tail_changed = sum(1 for k, v in a.items() if b.get(k) != v)
    n_tail_added = sum(1 for k in a if k not in b)
    n_tail_removed = sum(1 for k in b if k not in a)
    st = {"label": label, "table": table, "mode": "merge", "asof": asof, "cutoff": cutoff,
          "seal_n": seal_n, "n_sealed_rows": post_n, "n_tail_rows": len(a),
          "n_tail_changed": n_tail_changed, "n_tail_added": n_tail_added,
          "n_tail_removed": n_tail_removed,
          "n_sealed_diff": n_sealed_diff, "n_sealed_only_new": n_sealed_only_new,
          "n_gapfilled": n_sealed_only_new, "n_sealed_only_pub": n_sealed_only_pub,
          "sealed_immutable": sealed_ok, "sample": sample}

    print(f"  [immutable] cutoff={cutoff} (seal_n={seal_n}) · đã chốt {post_n} dòng "
          f"(BẤT BIẾN: {'OK' if sealed_ok else 'FAIL'}) · đuôi {st['n_tail_rows']} dòng: "
          f"{n_tail_changed} đổi giá trị, {n_tail_added} thêm, {n_tail_removed} bỏ")
    print(f"  [immutable] phân kỳ vùng ĐÃ CHỐT (KHÔNG áp dụng, chỉ đếm): "
          f"{n_sealed_diff} phiên khác giá trị · {n_sealed_only_new} phiên chỉ có ở bản mới · "
          f"{n_sealed_only_pub} phiên chỉ có ở bản đã công bố")
    if sample:
        print(f"  [immutable]   mẫu (đã công bố -> bản tính mới, KHÔNG ghi): {sample}")

    if not sealed_ok:
        msg = (f"🛑 IMMUTABILITY VIOLATION — {label}: vùng đã chốt (time <= {cutoff}) ĐỔI sau MERGE "
               f"(rows {pre_n}->{post_n}, checksum {pre_ck}->{post_ck}). Bảng {table} có thể đã hỏng "
               f"— KIỂM TRA NGAY, khôi phục từ vintage nếu cần.")
        _alert(msg)
        _record(st)
        raise PublishAbort(msg)

    if n_sealed_diff + n_sealed_only_new + n_sealed_only_pub > SEALED_DIFF_ALERT:
        _alert(f"🔁 UPSTREAM RESTATE (đã CHẶN, không ghi vào bảng) — {label}: bản tính hôm nay "
               f"khác bản đã công bố ở {n_sealed_diff} phiên ĐÃ CHỐT "
               f"(+{n_sealed_only_new} phiên thừa / {n_sealed_only_pub} phiên thiếu). "
               f"Bảng công bố GIỮ NGUYÊN (đúng thiết kế bất biến). Mẫu: {sample or 'n/a'}. "
               f"Nghĩa là: upstream (PE/corp-action/universe) đã sửa dữ liệu quá khứ — nếu cần "
               f"dùng bản mới cho nghiên cứu, chụp VINTAGE riêng, đừng đè bảng công bố.")
    _record(st)
    return st


def export_published_csv(table, csv_path, project=PROJECT):
    """Ghi `csv_path` = ảnh chụp bảng ĐÃ CÔNG BỐ (time,state,state_raw), atomic.

    Vì sao cần: với publish bất biến, chuỗi VỪA TÍNH LẠI (input của publisher) KHÁC bảng đã
    công bố ở vùng đã chốt. Consumer đọc CSV phải nhận đúng bản đã công bố, không phải bản
    tính lại — nếu không thì cùng một "chuỗi DT5G" lại có hai phiên bản lệch nhau, và backtest
    (nhóm đọc CSV nhiều nhất) rơi lại đúng cái look-ahead mà thiết kế này khử.
    Schema giữ NGUYÊN 3 cột — `asof_date` là cột audit chỉ sống ở BQ (đổi schema CSV sẽ đụng
    ~7 script nghiên cứu đang đọc file này).
    Atomic (tmp + os.replace) theo coding_guidelines §5: bị kill giữa lúc ghi không được để lại
    file cụt cho lần chạy sau tin."""
    df = _bq_query(f"SELECT time, state, state_raw FROM `{project}.{table}` ORDER BY time")
    if len(df) == 0:
        raise PublishAbort(f"export CSV: {table} trả về 0 dòng")
    df["time"] = pd.to_datetime(df["time"]).dt.strftime("%Y-%m-%d")
    df["state"] = df["state"].astype(int); df["state_raw"] = df["state_raw"].astype(int)
    tmp = f"{csv_path}.tmp"
    df.to_csv(tmp, index=False)
    os.replace(tmp, csv_path)
    return len(df)


def _record(stats):
    try:
        os.makedirs(os.path.dirname(HISTORY), exist_ok=True)
        with open(HISTORY, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                **stats}, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"  WARN: không ghi được {HISTORY}: {e}")


if __name__ == "__main__":
    import argparse
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--csv", required=True, help="CSV [time,state,state_raw]")
    ap.add_argument("--table", required=True, help="dataset.table (không kèm project)")
    ap.add_argument("--label", required=True)
    ap.add_argument("--seal-n", type=int, default=SEAL_N)
    ap.add_argument("--vintage", action="store_true",
                    help="chụp vintage bất biến của bảng TRƯỚC khi publish")
    a = ap.parse_args()
    if a.vintage:
        print(f"  [immutable] vintage -> {snapshot_vintage(a.table)}")
    try:
        publish_immutable(a.csv, a.table, a.label, seal_n=a.seal_n)
    except PublishAbort as e:
        print(f"!!! PUBLISH ABORT ({a.label}): {e}")
        sys.exit(1)
