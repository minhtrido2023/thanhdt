#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dt5g_writer_watch.py — giám sát WRITER LẠ trên bảng PRODUCTION tav2_bq.vnindex_5state_dt5g_live.

BỐI CẢNH (quyết định của user 2026-07-31, job Winston_20260731_014953)
---------------------------------------------------------------------
Bảng production DT5G có **HAI writer độc lập**:
  1. Của TA — `macro_state_live.py` → `deploy_golive_dt5g_v4/publish_gated_state.py` →
     `state_publish_immutable.py`, chạy trong `daily_refresh_v34b_linux.sh` step [12]
     (~18:35 ICT) và lại lần nữa trong `mike/bin/bq_freshness_check.sh` [pipeline-1] (~19:01).
  2. Của TEAM DỮ LIỆU (kaffa_v2, `/workspace/kaffa_v2/worker/tasks/market_state_tasks.py`,
     task `update_market_regime_state`) — implementation DT5G RIÊNG, DELETE+APPEND 5 phiên
     gần nhất, chạy trong EOD pipeline của họ (~17:12 ICT). Từ commit c794dd1 (2026-06-08).
     Truy vết đầy đủ: `mike/agents/Winston/dt5g_live_second_writer_20260729.md`.

**User đã quyết PHƯƠNG ÁN B**: team dữ liệu tự quản writer của họ; ta **KHÔNG** yêu cầu họ đổi
bảng đích, **KHÔNG** đụng vào hệ thống của họ. Ta chỉ **TIÊU THỤ + GIÁM SÁT**, và **BÁO** cho
team dữ liệu khi có sự cố. Script này chính là phần "giám sát + báo" đó — nó **KHÔNG chặn gì,
KHÔNG sửa gì**, luôn exit 0.

CÁC TÍN HIỆU ĐO (tất cả đều chỉ ĐỌC)
------------------------------------
A. `lastModifiedTime` của bảng → giờ ICT → phân lớp writer theo cửa sổ thời gian:
     OURS         18:25–19:20  (2 lần publish của ta ở trên, có biên)
     KAFFA_KNOWN  16:30–18:00  (EOD pipeline của team dữ liệu, đã biết + user chấp nhận)
     OTHER        còn lại      → writer LẠ / kaffa chạy lệch giờ / ai đó ghi tay
   Hạn chế đã biết (ghi ra để không ai hiểu nhầm số liệu này): `lastModifiedTime` chỉ giữ lần
   ghi CUỐI. Lấy mẫu lúc 19:00 sẽ luôn thấy chính ta (18:35 đè lên 17:12 của kaffa) ⇒ điểm lấy
   mẫu QUAN TRỌNG NHẤT là lần gọi TRƯỚC publish (đầu `daily_refresh_v34b_linux.sh`, ~18:30).

B. `asof_date IS NULL` — **dấu vân tay chính xác của writer ngoài**, tin cậy hơn (A):
   publisher của ta LUÔN ghi `asof_date`; MERGE bất biến chỉ cập nhật `asof_date` khi GIÁ TRỊ
   đổi (`state IS DISTINCT FROM`), nên một dòng do kaffa INSERT mà giá trị TRÙNG với ta sẽ
   giữ nguyên `asof_date = NULL` mãi mãi. Đo thật 2026-07-31: đúng 5 dòng cuối (07-24→07-30)
   NULL = đúng 5 phiên kaffa append. NULL ở vùng ĐÃ CHỐT (cũ hơn đuôi 25 phiên) = ai đó viết
   lại LỊCH SỬ ⇒ nghiêm trọng.

C. **Diff giá trị**: bảng BQ vs `data/vnindex_5state_dt5g_live.csv` (bản ta CÔNG BỐ lần cuối)
   trên các ngày CHUNG. Vì CSV = ảnh chụp bảng ngay sau publish của ta, mọi chênh lệch trên
   ngày chung nghĩa là **bảng production hiện đang phục vụ giá trị mà ta CHƯA BAO GIỜ công bố**.
   Đây là mục 3 của dispatch. NGƯỠNG = **>= 1 phiên lệch `state`** (không dùng ngưỡng phần
   trăm): hai engine đã biết lệch 27/3134 phiên lịch sử (0,86%) nên lệch KHÔNG phải chuyện
   bất khả thi — nhưng mỗi lần lệch là consumer thật (golive/pt_v4/dna_report) có thể đọc
   trúng giá trị của engine kia trong cửa sổ 17:12→18:35, nên 1 phiên cũng phải báo NGƯỜI,
   không chỉ log. `state_raw` lệch mà `state` trùng = tầng thấp hơn (WARN): chỉ là cột audit.

D. Trùng `time` (bảng phải 1 dòng/phiên): DELETE+APPEND của writer ngoài lỗi giữa chừng có
   thể sinh dòng đôi ⇒ consumer JOIN sẽ nhân đôi. Bất kỳ dòng đôi nào = HIGH.

PHÂN TẦNG CẢNH BÁO (cố tình chống alert-fatigue — kaffa ghi MỖI NGÀY, báo mỗi ngày = mù)
-------------------------------------------------------------------------------------
  HIGH  → Telegram (notify.sh) + Discord Trading Daily + bus `error`
          khi: state lệch >=1 phiên | dòng đôi | NULL asof_date ở vùng ĐÃ CHỐT
  WARN  → Discord Trading Daily + bus `finding`
          khi: writer_class = OTHER (ghi ngoài mọi cửa sổ đã biết) | state_raw lệch
  QUIET → chỉ ghi CSV lịch sử + stdout: OURS / KAFFA_KNOWN mà không lệch gì
          (đây là trạng thái BÌNH THƯỜNG đã được user chấp nhận, không ping ai)
Chống lặp: mỗi (ngày, tầng, chữ ký sự cố) chỉ ping 1 lần — lịch sử ở
`data/dt5g_writer_watch.csv`.

Usage:  python3 mike/bin/dt5g_writer_watch.py [--label pre-publish|post-publish|manual]
        [--dry-run] [--quiet]
Luôn exit 0 (kể cả khi bq lỗi) — đây là monitor, không phải gate.
"""
import argparse
import csv
import datetime as dt
import json
import os
import subprocess
import sys

WORKDIR = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")
MIKE = os.path.join(WORKDIR, "mike")
PROJECT = "lithe-record-440915-m9"
TABLE = "tav2_bq.vnindex_5state_dt5g_live"
LOCAL_CSV = os.path.join(WORKDIR, "data/vnindex_5state_dt5g_live.csv")
STATE_CSV = os.path.join(WORKDIR, "data/dt5g_writer_watch.csv")
DISCORD_TRADING_DAILY = "1521470705563340910"

# Cửa sổ writer (giờ ICT, [start, end)) — đo thật từ log: daily_refresh START 18:30,
# step [9] backup 18:35:47, DONE 18:38:42; bq_freshness [pipeline-1] ~19:01:08.
OURS_WINDOW = (dt.time(18, 25), dt.time(19, 20))
KAFFA_WINDOW = (dt.time(16, 30), dt.time(18, 0))   # đo thật 2026-07-29: 17:12:05 ICT
SEAL_TAIL_SESSIONS = 25   # = seal_n của state_publish_immutable (đuôi chưa chốt)


def sh(cmd, timeout=180):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except Exception as e:                                  # noqa: BLE001
        return 1, "", str(e)


def bq_query_csv(sql):
    # --max_rows BẮT BUỘC: `bq query` mặc định chỉ trả 100 DÒNG ĐẦU và KHÔNG báo lỗi gì —
    # thiếu nó thì diff/NULL-asof chỉ soi 100 phiên cũ nhất (2014) và luôn báo "sạch".
    # (Bắt được khi chạy thật lần đầu, 2026-07-31.)
    rc, out, err = sh(["bq", "query", "--use_legacy_sql=false", "--max_rows=1000000",
                       f"--project_id={PROJECT}", "--format=csv", "--quiet", sql])
    if rc != 0:
        return None, err.strip()[:300]
    rows = list(csv.DictReader(out.splitlines()))
    return rows, None


def table_lastmod():
    rc, out, err = sh(["bq", "show", "--format=prettyjson", f"{PROJECT}:{TABLE}"])
    if rc != 0:
        return None, err.strip()[:300]
    try:
        ms = int(json.loads(out)["lastModifiedTime"])
    except Exception as e:                                  # noqa: BLE001
        return None, f"parse lastModifiedTime: {e}"
    return dt.datetime.fromtimestamp(ms / 1000.0), None     # process TZ = ICT trên host này


def classify(when):
    t = when.time()
    if OURS_WINDOW[0] <= t < OURS_WINDOW[1]:
        return "OURS"
    if KAFFA_WINDOW[0] <= t < KAFFA_WINDOW[1]:
        return "KAFFA_KNOWN"
    return "OTHER"


def read_local_csv():
    """→ {time: (state, state_raw)} từ bản ta công bố lần cuối."""
    out = {}
    if not os.path.exists(LOCAL_CSV):
        return out
    with open(LOCAL_CSV, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            t = (r.get("time") or "").strip()[:10]
            if t:
                out[t] = (r.get("state", "").strip(), r.get("state_raw", "").strip())
    return out


def notify(script, msg, *extra):
    sh([os.path.join(MIKE, "bin", script), msg, *extra], timeout=60)


def bus(etype, topic, payload):
    sh([os.path.join(MIKE, "bin", "append_event.sh"), "Winston", etype, topic,
        json.dumps(payload, ensure_ascii=False)], timeout=60)


def already_alerted(today, tier, signature):
    if not os.path.exists(STATE_CSV):
        return False
    with open(STATE_CSV, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r.get("date") == today and r.get("tier") == tier
                    and r.get("signature") == signature and r.get("alerted") == "1"):
                return True
    return False


def append_state(row):
    new = not os.path.exists(STATE_CSV)
    cols = ["ts", "date", "label", "lastmod", "writer_class", "n_rows", "n_dup_time",
            "n_null_asof", "n_null_sealed", "n_common", "n_state_diff", "n_raw_diff",
            "n_diff_sealed", "tier", "signature", "alerted"]
    with open(STATE_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        if new:
            w.writeheader()
        w.writerow({c: row.get(c, "") for c in cols})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="manual",
                    help="điểm lấy mẫu: pre-publish | post-publish | manual")
    ap.add_argument("--dry-run", action="store_true", help="không ping, không ghi state CSV")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    now = dt.datetime.now()
    today = now.strftime("%Y-%m-%d")
    say = (lambda *x: None) if a.quiet else print

    say(f"=== dt5g_writer_watch ({a.label}) — {now:%Y-%m-%d %H:%M:%S} ===")

    lastmod, err = table_lastmod()
    if lastmod is None:
        # Fail-safe: không đọc được metadata = monitor mù, báo WARN nhưng KHÔNG chặn gì.
        msg = (f"🟡 DT5G WRITER-WATCH ({today} {now:%H:%M} ICT, {a.label}): không đọc được "
               f"metadata bảng {TABLE} ({err}) — monitor writer-lạ đang MÙ hôm nay.")
        say(msg)
        if not a.dry_run:
            notify("notify_thread.sh", msg, DISCORD_TRADING_DAILY)
        return 0
    wclass = classify(lastmod)
    say(f"  lastModifiedTime = {lastmod:%Y-%m-%d %H:%M:%S} ICT  → writer_class={wclass}")

    rows, err = bq_query_csv(f"""
        SELECT CAST(t.time AS STRING) AS time, CAST(t.state AS STRING) AS state,
               CAST(t.state_raw AS STRING) AS state_raw,
               CAST(t.asof_date AS STRING) AS asof_date
        FROM `{PROJECT}.{TABLE}` AS t ORDER BY t.time""")
    if rows is None:
        msg = (f"🟡 DT5G WRITER-WATCH ({today} {now:%H:%M} ICT, {a.label}): query nội dung "
               f"{TABLE} FAIL ({err}) — không so được giá trị 2 engine hôm nay.")
        say(msg)
        if not a.dry_run:
            notify("notify_thread.sh", msg, DISCORD_TRADING_DAILY)
        return 0

    times = [r["time"] for r in rows]
    n_dup_time = len(times) - len(set(times))
    # cutoff vùng ĐÃ CHỐT = phiên thứ (SEAL_TAIL_SESSIONS+1) tính từ cuối
    uniq_sorted = sorted(set(times))
    seal_cutoff = uniq_sorted[-(SEAL_TAIL_SESSIONS + 1)] if len(uniq_sorted) > SEAL_TAIL_SESSIONS else ""

    null_dates = [r["time"] for r in rows if not (r.get("asof_date") or "").strip()]
    null_sealed = [d for d in null_dates if seal_cutoff and d <= seal_cutoff]

    local = read_local_csv()
    common = [r for r in rows if r["time"] in local]
    state_diff = [r["time"] for r in common if r["state"] != local[r["time"]][0]]
    raw_diff = [r["time"] for r in common
                if r["state_raw"] != local[r["time"]][1] and r["time"] not in state_diff]
    diff_sealed = [d for d in state_diff if seal_cutoff and d <= seal_cutoff]

    say(f"  rows={len(rows)} dup_time={n_dup_time} null_asof={len(null_dates)} "
        f"(sealed {len(null_sealed)}) | so CSV công bố: chung={len(common)} "
        f"state_lệch={len(state_diff)} raw_lệch={len(raw_diff)} (sealed {len(diff_sealed)})")

    tier, parts = "QUIET", []
    if state_diff:
        tier = "HIGH"
        parts.append(f"{len(state_diff)} phiên LỆCH `state` so với bản ta công bố "
                     f"({', '.join(state_diff[:10])}{'…' if len(state_diff) > 10 else ''}"
                     f"{f'; {len(diff_sealed)} phiên nằm trong vùng ĐÃ CHỐT' if diff_sealed else ''})")
    if n_dup_time:
        tier = "HIGH"
        parts.append(f"{n_dup_time} dòng TRÙNG `time` (consumer JOIN sẽ nhân đôi)")
    if null_sealed:
        tier = "HIGH"
        parts.append(f"{len(null_sealed)} dòng `asof_date` NULL trong vùng ĐÃ CHỐT "
                     f"({null_sealed[0]}…{null_sealed[-1]}) = LỊCH SỬ bị writer ngoài viết lại")
    if tier != "HIGH":
        if raw_diff:
            tier = "WARN"
            parts.append(f"{len(raw_diff)} phiên lệch `state_raw` (cột audit, `state` vẫn khớp): "
                         f"{', '.join(raw_diff[:5])}")
        if wclass == "OTHER":
            tier = "WARN"
            parts.append(f"bảng được ghi lúc {lastmod:%Y-%m-%d %H:%M} ICT — NGOÀI cả cửa sổ "
                         f"publisher của ta (18:25–19:20) lẫn cửa sổ EOD đã biết của kaffa_v2 "
                         f"(16:30–18:00) ⇒ writer LẠ hoặc kaffa chạy lệch giờ")

    signature = "|".join(sorted(parts))[:200]
    alerted = 0
    if tier != "QUIET" and not already_alerted(today, tier, signature) and not a.dry_run:
        head = ("🛑 DT5G SPLIT-BRAIN" if tier == "HIGH" else "🟡 DT5G WRITER-WATCH")
        msg = (f"{head} ({today} {now:%H:%M} ICT, mẫu={a.label}): bảng PRODUCTION "
               f"{TABLE} — " + "; ".join(parts) +
               f". Bảng này có 2 writer độc lập (publisher của ta + pipeline kaffa_v2 của team "
               f"dữ liệu, ~17:12 ICT). Ta CHỈ giám sát, KHÔNG sửa hệ thống của họ — cần BÁO "
               f"team dữ liệu. Chi tiết: mike/agents/Winston/dt5g_live_second_writer_20260729.md, "
               f"lịch sử đo: data/dt5g_writer_watch.csv")
        notify("notify_thread.sh", msg, DISCORD_TRADING_DAILY)
        if tier == "HIGH":
            notify("notify.sh", msg)
        bus("error" if tier == "HIGH" else "finding",
            "dt5g-live-writer-la",
            {"tier": tier, "label": a.label, "table": TABLE,
             "lastmod_ict": lastmod.strftime("%Y-%m-%d %H:%M:%S"), "writer_class": wclass,
             "n_state_diff": len(state_diff), "state_diff_dates": state_diff[:20],
             "n_raw_diff": len(raw_diff), "n_dup_time": n_dup_time,
             "n_null_asof": len(null_dates), "n_null_sealed": len(null_sealed),
             "detail": parts})
        alerted = 1
        say(f"  [{tier}] đã cảnh báo: {'; '.join(parts)}")
    elif tier != "QUIET":
        say(f"  [{tier}] {'; '.join(parts)} (đã báo hôm nay hoặc --dry-run → không ping lại)")
    else:
        say("  QUIET: không phát hiện bất thường (writer đã biết + giá trị khớp bản công bố)")

    if not a.dry_run:
        append_state({"ts": now.strftime("%Y-%m-%dT%H:%M:%S"), "date": today, "label": a.label,
                      "lastmod": lastmod.strftime("%Y-%m-%dT%H:%M:%S"), "writer_class": wclass,
                      "n_rows": len(rows), "n_dup_time": n_dup_time,
                      "n_null_asof": len(null_dates), "n_null_sealed": len(null_sealed),
                      "n_common": len(common), "n_state_diff": len(state_diff),
                      "n_raw_diff": len(raw_diff), "n_diff_sealed": len(diff_sealed),
                      "tier": tier, "signature": signature, "alerted": alerted})
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:                                  # noqa: BLE001
        # Monitor KHÔNG được làm hỏng caller (daily_refresh / bq_freshness) trong bất kỳ hoàn cảnh nào.
        print(f"dt5g_writer_watch: lỗi không mong đợi ({e}) — bỏ qua, không chặn caller")
        sys.exit(0)
