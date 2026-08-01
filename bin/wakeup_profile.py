#!/usr/bin/env python3
"""wakeup_profile.py — hồ sơ thời lượng job theo (agent, model, effort), để Mike chọn
độ trễ cho lần `ScheduleWakeup` ĐẦU TIÊN sau khi dispatch `--bg`, thay vì ladder cố định.

Vì sao cần: ladder hiện tại (MIKE.md §8) tỉnh 240-270s cho MỌI job. Đo trên toàn bộ job
record: `Winston` job đồng bộ không gắn model/effort có median 16s / p75 18s (cực đều)
→ tỉnh ở 240s lãng phí ~220s độ trễ vô ích; ngược lại `Taylor|opus|high` median 530s và
`Wags|opus|high` median ~751s → ladder tỉnh 2-3 lần TRƯỚC KHI job xong, mỗi lần tỉnh nạp
lại toàn bộ context (~90KB) = tốn token thật.

Script này CHỈ sinh số liệu. Nó KHÔNG gọi ScheduleWakeup, không dispatch, không sửa
MIKE.md — Mike tự đọc `state/wakeup_profile.json` và tự quyết. Thiếu file / file hỏng →
Mike rơi về ladder mặc định, không bao giờ chặn.

Dùng:
    python3 bin/wakeup_profile.py                       # ghi state/wakeup_profile.json
    python3 bin/wakeup_profile.py --print               # in ra stdout, không ghi file
    WAKEUP_PROFILE_WINDOW_WEEKS=8 python3 bin/wakeup_profile.py
    python3 bin/wakeup_profile.py --jobs-dir /tmp/x --out /tmp/x.json   # dùng cho selfcheck
"""
import argparse
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ngưỡng mẫu tối thiểu cho 1 bucket. Dưới ngưỡng này KHÔNG ghi ra output — thà để Mike
# rơi về global_fallback/ladder mặc định còn hơn tin vào 3-4 mẫu nhiễu.
MIN_SAMPLES = 8

# Job dài bất thường (>2h) không đại diện cho "job dạng này chạy bao lâu" — thường là job
# bị treo rồi mới được reap, hoặc phiên usage-limit chờ hồi. Loại khỏi thống kê.
MAX_DURATION_S = 7200

DEFAULT_WINDOW_WEEKS = 6


def iter_job_records(jobs_dir, warn):
    """Đọc mọi job record trong <jobs_dir> và <jobs_dir>/archive.

    Một file VỀ NGUYÊN TẮC là 1 JSON object, nhưng dispatch.sh ghi bằng cách append nên
    một file CÓ THỂ chứa nhiều object nối liền nhau (không phải JSON array). Parse bằng
    raw_decode lặp để không âm thầm mất dữ liệu nếu điều đó xảy ra.
    (Đo 2026-08-01 trên 1294 file thật: 0 file multi-object — nhưng parse kiểu này không
    tốn gì thêm và chịu được nếu format đổi.)
    """
    decoder = json.JSONDecoder()
    dirs = [jobs_dir, os.path.join(jobs_dir, "archive")]
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not name.endswith(".json"):
                continue
            path = os.path.join(d, name)
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
            except OSError as exc:
                warn(f"không đọc được {path}: {exc}")
                continue
            idx = 0
            n_obj = 0
            while idx < len(text):
                while idx < len(text) and text[idx].isspace():
                    idx += 1
                if idx >= len(text):
                    break
                try:
                    obj, idx = decoder.raw_decode(text, idx)
                except ValueError as exc:
                    warn(f"JSON hỏng ở {path} (offset {idx}): {exc}")
                    break
                if isinstance(obj, dict):
                    n_obj += 1
                    yield obj
                else:
                    warn(f"{path}: object #{n_obj + 1} không phải dict, bỏ qua")
            if n_obj == 0:
                warn(f"{path}: không có record hợp lệ")


def duration_of(rec):
    """Trả về (started_at_epoch, duration_s) nếu record dùng được, ngược lại None."""
    if rec.get("status") != "done":
        return None
    try:
        started = int(float(rec["started_at"]))
        ended = int(float(rec["ended_at"]))
    except (KeyError, TypeError, ValueError):
        return None
    dur = ended - started
    if dur <= 0 or dur > MAX_DURATION_S:
        return None
    return started, dur


def bucket_key(rec):
    """(to, model, effort) — field thiếu → "?". KHÔNG bỏ record thiếu field: job đồng bộ
    và job cũ không gắn model/effort là nhóm THẬT lớn (n=307 cho Winston|?|?)."""
    def f(name):
        v = rec.get(name)
        return v if isinstance(v, str) and v.strip() else "?"
    return "|".join((f("to"), f("model"), f("effort")))


def pctile(sorted_vals, p):
    """Nearest-rank trên list đã sắp xếp. n>=1 luôn được đảm bảo bởi caller."""
    i = int(round(p * (len(sorted_vals) - 1)))
    return sorted_vals[min(max(i, 0), len(sorted_vals) - 1)]


def stats(vals):
    v = sorted(vals)
    return {"n": len(v), "median_s": int(pctile(v, 0.50)), "p75_s": int(pctile(v, 0.75))}


def build_profile(jobs_dir, window_weeks, now=None, warn=None):
    warnings = []
    warn = warn or warnings.append
    now = now if now is not None else time.time()
    cutoff = now - window_weeks * 7 * 86400

    buckets = {}
    all_durs = []
    for rec in iter_job_records(jobs_dir, warn):
        d = duration_of(rec)
        if d is None:
            continue
        started, dur = d
        if started < cutoff:
            continue
        buckets.setdefault(bucket_key(rec), []).append(dur)
        all_durs.append(dur)

    out_buckets = {
        k: stats(v) for k, v in buckets.items() if len(v) >= MIN_SAMPLES
    }
    profile = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
        "window_weeks": window_weeks,
        "min_samples": MIN_SAMPLES,
        "buckets": dict(sorted(out_buckets.items())),
        "global_fallback": stats(all_durs) if all_durs else {"n": 0},
    }
    return profile, warnings


def atomic_write_json(path, obj):
    """tmp + os.replace trong CÙNG thư mục đích (khác thư mục → os.replace có thể fail
    cross-device). File này bị Mike đọc mỗi lần dispatch — không được để dở dang."""
    d = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(d, exist_ok=True)
    tmp = os.path.join(d, f".{os.path.basename(path)}.tmp.{os.getpid()}")
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--jobs-dir", default=os.path.join(ROOT, "bus", "jobs"))
    ap.add_argument("--out", default=os.path.join(ROOT, "state", "wakeup_profile.json"))
    ap.add_argument("--weeks", type=int, default=None,
                    help="ghi đè WAKEUP_PROFILE_WINDOW_WEEKS")
    ap.add_argument("--print", dest="do_print", action="store_true",
                    help="in JSON ra stdout, KHÔNG ghi file")
    args = ap.parse_args(argv)

    weeks = args.weeks
    if weeks is None:
        try:
            weeks = int(os.environ.get("WAKEUP_PROFILE_WINDOW_WEEKS", DEFAULT_WINDOW_WEEKS))
        except ValueError:
            weeks = DEFAULT_WINDOW_WEEKS
    if weeks < 1:
        weeks = DEFAULT_WINDOW_WEEKS

    profile, warnings = build_profile(args.jobs_dir, weeks)
    for w in warnings:
        print(f"[warn] {w}", file=sys.stderr)

    text = json.dumps(profile, ensure_ascii=False, indent=2)
    if args.do_print:
        print(text)
    else:
        atomic_write_json(args.out, profile)
        print(
            f"wakeup_profile: {len(profile['buckets'])} bucket (n>={MIN_SAMPLES}), "
            f"cửa sổ {weeks} tuần, global n={profile['global_fallback'].get('n', 0)} "
            f"-> {args.out}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
