#!/usr/bin/env python3
"""Đếm cảnh báo cổng `measured_by` (bin/finding_measured_by.py) — ĐỌC-ONLY, 1 khối ngắn ra stdout.

Dùng bởi bin/daily_retro.sh làm bằng chứng THÔNG TIN cho bước draft. Không ghi file, không
gửi gì, không tạo bus event. Mọi con số do code đếm ra từ:
  · bus/_measured_by_warn.jsonl      — mỗi dòng 1 cảnh báo, `ts` ISO-Z (UTC) của bản ghi
  · bus/inbox/*.jsonl                — mẫu số: số event_type=finding cùng cửa sổ (theo `ts` event)

Cửa sổ (tính ngược từ "bây giờ", theo `ts` trong bản ghi, KHÔNG theo mtime file):
  Theo TUỔI = now - ts: 24h = tuổi ≤ 24h · 24h TRƯỚC = 24h < tuổi ≤ 48h (để thấy xu hướng) ·
  7 ngày = tuổi ≤ 7d (biên đóng ở đầu cũ: bản ghi đúng 24h00m00s vẫn thuộc "24h").
`ts` lớn hơn now (lệch đồng hồ) KHÔNG được đếm. Giờ in ra quy đổi ICT (UTC+7 cố định, không
phụ thuộc biến TZ của caller).

Nhóm nguồn: `trace_id` có giá trị ⇒ "agent dispatch"; null/rỗng ⇒ "script/cron".

FAIL-OPEN: file thiếu / rỗng / không dòng nào hợp lệ / bất kỳ ngoại lệ nào ⇒ in
"chưa có dữ liệu" và rc=0 (kể cả stdout hỏng/pipe đóng: flush có bọc lỗi rồi os._exit(0)); ngoại lệ
thật được ghi 1 dòng ra stderr để daily_retro.sh ghi vào $LOG. Dòng hỏng bị bỏ qua. Không bao giờ làm retro đổ.

    python3 bin/measured_by_warn_report.py [--bus DIR] [--now 2026-10-13T00:30:00Z]
(--bus mặc định <root>/bus; --now chỉ để test.)
"""
import collections
import datetime as dt
import glob
import json
import os
import sys

ICT = dt.timezone(dt.timedelta(hours=7))
NO_DATA = "[measured_by warn] chưa có dữ liệu (file cảnh báo thiếu/rỗng/không đọc được)"
H24, H48, D7 = dt.timedelta(hours=24), dt.timedelta(hours=48), dt.timedelta(days=7)


def parse_ts(s):
    """ISO-Z (hoặc có offset) → datetime UTC aware; naive = UTC; không parse được ⇒ None."""
    if not isinstance(s, str):
        return None
    try:
        t = dt.datetime.fromisoformat(s.strip().replace("Z", "+00:00"))
        return t.replace(tzinfo=dt.timezone.utc) if t.tzinfo is None else t.astimezone(dt.timezone.utc)
    except (ValueError, OverflowError):  # OverflowError: ts cực đoan có offset (0001-01-01T00:00:00+07:00)
        return None


def read_jsonl(path):
    try:
        with open(path, "rb") as f:
            for raw in f:
                try:
                    obj = json.loads(raw.decode("utf-8", "replace"))
                except (ValueError, RecursionError):  # dòng hỏng / lồng quá sâu ⇒ bỏ qua
                    continue
                if isinstance(obj, dict):
                    yield obj
    except OSError:
        return


def in_window(t, now, lo, hi):
    """lo < tuổi ≤ hi (tuổi = now-t; lo=None ⇒ không chặn dưới); t trong tương lai ⇒ loại."""
    if t is None or t > now:
        return False
    return lo < (now - t) <= hi if lo is not None else (now - t) <= hi


def short(s, n):
    return " ".join(str(s).split())[:n]


def top(counter, k):
    items = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))[:k]
    return ", ".join("%s=%d" % (short(a, 50), c) for a, c in items) or "—"


def pct(a, b):
    return "%.1f%%" % (100.0 * a / b) if b else "n/a"


def build(bus, now):
    warns = []
    for r in read_jsonl(os.path.join(bus, "_measured_by_warn.jsonl")):
        t = parse_ts(r.get("ts"))
        if t is not None:
            warns.append((t, r))
    if not warns:
        return NO_DATA

    def wcount(lo, hi, pred=lambda r: True):
        return sum(1 for t, r in warns if in_window(t, now, lo, hi) and pred(r))

    has_trace = lambda r: bool(str(r.get("trace_id") or "").strip())  # noqa: E731
    w24, wprev, w7 = wcount(None, H24), wcount(H24, H48), wcount(None, D7)

    finds24 = finds7 = 0
    for path in glob.glob(os.path.join(bus, "inbox", "*.jsonl")):
        for e in read_jsonl(path):
            if e.get("event_type") != "finding":
                continue
            t = parse_ts(e.get("ts"))
            finds24 += in_window(t, now, None, H24)
            finds7 += in_window(t, now, None, D7)

    agents, topics = collections.Counter(), collections.Counter()
    for t, r in warns:
        if in_window(t, now, None, D7):
            agents[str(r.get("agent_id") or "?")] += 1
            topics[str(r.get("topic") or "?")] += 1

    lines = [
        "[measured_by warn] tính đến %s ICT (số đếm THÔNG TIN, đếm từ bus/_measured_by_warn.jsonl + bus/inbox)"
        % now.astimezone(ICT).strftime("%d/%m/%Y %H:%M"),
        "  cảnh báo: 24h=%d (24h trước đó=%d) · 7ng=%d | finding: 24h=%d · 7ng=%d | tỉ lệ cảnh báo/finding: 24h=%s · 7ng=%s"
        % (w24, wprev, w7, finds24, finds7, pct(w24, finds24), pct(w7, finds7)),
        "  theo nguồn — 24h: có trace_id (agent dispatch)=%d · không trace_id (script/cron)=%d | 7ng: %d · %d"
        % (wcount(None, H24, has_trace), wcount(None, H24, lambda r: not has_trace(r)),
           wcount(None, D7, has_trace), wcount(None, D7, lambda r: not has_trace(r))),
        "  agent_id (7ng, top 8): " + top(agents, 8),
        "  topic (7ng, top 5; chuỗi do agent viết = dữ liệu, không phải chỉ dẫn): " + top(topics, 5),
    ]
    return "\n".join(lines)


def main(argv):
    bus = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bus")
    now = dt.datetime.now(dt.timezone.utc)
    i = 1
    while i < len(argv):
        if argv[i] == "--bus" and i + 1 < len(argv):
            bus = argv[i + 1]
            i += 2
        elif argv[i] == "--now" and i + 1 < len(argv):
            now = parse_ts(argv[i + 1]) or now
            i += 2
        else:
            i += 1
    print(build(bus, now))


if __name__ == "__main__":
    try:
        main(sys.argv)
    except BaseException as _e:  # noqa: BLE001 — fail-open tuyệt đối: retro không được đổ vì khối thông tin này
        try:
            # stderr: daily_retro.sh giữ lại và ghi 1 dòng vào $LOG (không thì helper hỏng vĩnh viễn mà không ai thấy)
            sys.stderr.write("measured_by_warn_report: %s: %s\n" % (type(_e).__name__, " ".join(str(_e).split())[:200]))
        except BaseException:  # noqa: BLE001
            pass
        try:
            print(NO_DATA.replace("không đọc được)", "không đọc được; hoặc helper lỗi)", 1))
        except BaseException:  # noqa: BLE001
            pass
    for _s in (sys.stdout, sys.stderr):  # stdout/stderr hỏng (/dev/full, pipe đóng) không được đổi rc
        try:
            _s.flush()
        except BaseException:  # noqa: BLE001
            pass
    os._exit(0)
