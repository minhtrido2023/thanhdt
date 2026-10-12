#!/usr/bin/env python3
"""macro_gate_health_tz_selfcheck.py — pin cổng fail-safe `get_gated_state()` đọc `ts` của
data/macro_health.json đúng ở MỌI dạng timestamp và MỌI múi giờ host.

Sự cố gốc (2026-10-11, bus error `dt5g-gate-fallback-dt4-tzaware-health-ts`): commit 3538119f
đổi macro_healthcheck.py sang ghi `ts` CÓ múi giờ (+07:00); macro_state_live.py vẫn lấy
`datetime.now()` naive trừ đi ⇒ TypeError ⇒ nhánh except ⇒ DT4_only ở MỌI lần gọi (cổng không
bao giờ cấp DT5G nữa, và không có alert nào — chỉ một dòng reason trong log).

Kiểm:
  A. ts aware +07:00 tươi                     ⇒ DT5G_macro
  B. ts naive kiểu cũ (= giờ ICT) tươi        ⇒ DT5G_macro
  C. ts aware UTC (+00:00) tươi               ⇒ DT5G_macro (so theo THỜI ĐIỂM, không theo chữ)
  D. ts aware / naive già hơn 1440 phút       ⇒ DT4_only
  C2/D2. offset KHÁC +07:00 ở khoảng mà lệch múi giờ làm đổi kết luận (UTC già 1200 ⇒ DT5G_macro,
     +09:00 già 1500 ⇒ DT4_only) — bắt kiểu cài "đè offset bằng ICT" và "cắt chuỗi rồi parse"
  D3. ngưỡng 1440 bị ghim hai phía: già 1430 ⇒ DT5G_macro, già 1450 ⇒ DT4_only
  I. ts ở TƯƠNG LAI quá 5 phút (aware / naive) ⇒ DT4_only, reason in ra ts + số phút lệch thật;
     tương lai ≤5 phút (lệch đồng hồ) ⇒ vẫn DT5G_macro   (user duyệt 2026-10-11 22:10 ICT)
  I2. con số 5 phút bị ghim hai phía: tương lai 4'30" ⇒ DT5G_macro, 5'30" ⇒ DT4_only
  E. ts rác / thiếu ts / ts không phải chuỗi / JSON hỏng / thiếu file ⇒ DT4_only
  F. ts tươi nhưng status=FAILED hoặc recommended_state_source≠DT5G_macro ⇒ DT4_only
  G. cửa sổ "live" của frozen-state guard (≤10 ngày) tính theo NGÀY ICT, không theo ngày host
  H. writer thật: `ts` mà macro_healthcheck.py ghi (đọc biểu thức NOW từ file thật) ⇒ DT5G_macro

Mỗi nhóm chạy lại dưới nhiều TZ host (đổi TZ trong tiến trình bằng time.tzset), gồm một TZ mà
NGÀY lịch đang lệch với ICT ngay lúc chạy — §16 coding_guidelines: selfcheck thừa hưởng TZ đúng
của tác giả thì xanh bất kể code đúng hay sai.

Hermetic: get_macro_state bị thay bằng stub, bq là stub, health_path là file tạm — KHÔNG đọc/ghi
data/macro_health.json thật, KHÔNG chạm BigQuery, KHÔNG gửi alert.

Chạy: python3 macro_gate_health_tz_selfcheck.py   (rc=0 khi tất cả PASS)
"""
import ast
import contextlib
import io
import json
import os
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import macro_state_live as msl  # noqa: E402

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
UTC = ZoneInfo("UTC")
OLD_END = "2020-01-10"          # xa quá khứ ⇒ frozen-state guard không chạy (không cần bq)

results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail and not ok else ""))


def _stub_macro(start, end, bq=None):
    """macro (state) ≠ base (state_dt4) ở mọi dòng ⇒ cột `state` trả về cho biết cổng chọn bên nào."""
    t = pd.to_datetime([pd.Timestamp(end) - pd.Timedelta(days=k) for k in (2, 1, 0)])
    return pd.DataFrame({"time": t, "state": [2, 2, 2], "state_dt4": [3, 3, 3]})


class _BqStub:
    def __init__(self):
        self.calls = 0

    def __call__(self, sql):
        self.calls += 1
        return pd.DataFrame({"mx": ["2099-01-01"], "gap": [0]})


def _set_tz(tz):
    if tz is None:
        os.environ.pop("TZ", None)
    else:
        os.environ["TZ"] = tz
    time.tzset()


def _date_shifted_tz():
    """Một TZ mà NGÀY lịch hiện đang KHÁC ngày ICT (luôn tồn tại: UTC+14 hoặc UTC-11)."""
    now = datetime.now(UTC)
    for tz in ("Pacific/Kiritimati", "Pacific/Pago_Pago"):
        if now.astimezone(ZoneInfo(tz)).date() != now.astimezone(ICT).date():
            return tz
    raise RuntimeError("không tìm được TZ lệch ngày với ICT")


def _gate(tmp, payload, end=OLD_END, bq=None, raw=None):
    """Ghi fixture health rồi gọi cổng. payload=None ⇒ KHÔNG tạo file. raw ⇒ ghi nguyên văn."""
    p = Path(tmp) / "health.json"
    if p.exists():
        p.unlink()
    if raw is not None:
        p.write_text(raw, encoding="utf-8")
    elif payload is not None:
        p.write_text(json.dumps(payload), encoding="utf-8")
    g = msl.get_gated_state("2020-01-01", end, bq=bq or _BqStub(), health_path=str(p), alert=False)
    return str(g["source"].iloc[0]), int(g["state"].iloc[-1])


def _health(ts, status="HEALTHY", rec="DT5G_macro"):
    return {"ts": ts, "status": status, "recommended_state_source": rec}


def _writer_ts_expr():
    """Biểu thức gán NOW trong macro_healthcheck.py THẬT (không chạy file — nó ghi data/ thật)."""
    tree = ast.parse((HERE / "macro_healthcheck.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "NOW" for t in node.targets):
            return ast.unparse(node.value)
    raise RuntimeError("macro_healthcheck.py không còn gán NOW ở top-level")


def run_cases(tz_label):
    now = datetime.now(ICT)
    aware = lambda m: (now - timedelta(minutes=m)).isoformat(timespec="seconds")
    naive = lambda m: (now - timedelta(minutes=m)).replace(tzinfo=None).isoformat(timespec="seconds")
    utc = lambda m: (now - timedelta(minutes=m)).astimezone(UTC).isoformat(timespec="seconds")
    plus9 = lambda m: (now - timedelta(minutes=m)).astimezone(timezone(timedelta(hours=9))).isoformat(timespec="seconds")
    DT5G, DT4 = ("DT5G_macro", 2), ("DT4_only", 3)
    T = f"[TZ={tz_label}] "

    with tempfile.TemporaryDirectory() as tmp:
        for name, ts, want in [
            ("A. aware +07:00, 5 phút", aware(5), DT5G),
            ("A. aware +07:00, 1380 phút (<1440)", aware(1380), DT5G),
            ("B. naive kiểu cũ, 5 phút", naive(5), DT5G),
            ("B. naive kiểu cũ, 1380 phút (<1440)", naive(1380), DT5G),
            ("C. aware UTC +00:00, 5 phút", utc(5), DT5G),
            ("D. aware +07:00, 1500 phút (>1440)", aware(1500), DT4),
            ("D. naive kiểu cũ, 1500 phút (>1440)", naive(1500), DT4),
            ("D. aware UTC +00:00, 1500 phút (>1440)", utc(1500), DT4),
            ("C2. aware UTC +00:00, 1200 phút (<1440; đè offset thành ICT ⇒ 1620)", utc(1200), DT5G),
            ("D2. aware +09:00, 1500 phút (>1440; đè offset thành ICT ⇒ 1380)", plus9(1500), DT4),
            ("D3. aware +07:00, 1430 phút (<1440)", aware(1430), DT5G),
            ("D3. aware +07:00, 1450 phút (>1440)", aware(1450), DT4),
            ("I. aware tương lai +120 phút", aware(-120), DT4),
            ("I. aware tương lai +10 ngày", aware(-10 * 1440), DT4),
            ("I. naive tương lai +10 năm", naive(-3650 * 1440), DT4),
            ("I. aware tương lai +3 phút (lệch đồng hồ ≤5)", aware(-3), DT5G),
            ("E. ts rác", "khong-phai-ngay", DT4),
            ("E. ts rỗng", "", DT4),
            ("E. ts là số", 1760000000, DT4),
            ("E. ts null", None, DT4),
        ]:
            got = _gate(tmp, _health(ts))
            check(T + name + f" ⇒ {want[0]}", got == want, f"got={got} ts={ts!r}")

        # I2. ghim CON SỐ 5 phút hai phía. ts dựng ngay trước lệnh gọi cổng (không dùng `now` đầu
        # hàm) để biên an toàn 30 giây không bị thời gian chạy các ca trên ăn mất. Đổi hằng số
        # sang bất kỳ số nguyên phút nào khác (4, 6, …) đều làm đúng một trong hai ca đỏ.
        for name, ahead_s, want in [
            ("I2. aware tương lai +4 phút 30 giây (ngay DƯỚI ngưỡng 5)", 270, DT5G),
            ("I2. aware tương lai +5 phút 30 giây (ngay TRÊN ngưỡng 5)", 330, DT4),
        ]:
            ts = (datetime.now(ICT) + timedelta(seconds=ahead_s)).isoformat(timespec="seconds")
            got = _gate(tmp, _health(ts))
            check(T + name + f" ⇒ {want[0]}", got == want, f"got={got} ts={ts!r}")

        got = _gate(tmp, {"status": "HEALTHY", "recommended_state_source": "DT5G_macro"})
        check(T + "E. thiếu khoá ts ⇒ DT4_only", got == DT4, f"got={got}")
        got = _gate(tmp, None, raw="{ day khong phai json")
        check(T + "E. JSON hỏng ⇒ DT4_only", got == DT4, f"got={got}")
        got = _gate(tmp, None)
        check(T + "E. thiếu file ⇒ DT4_only", got == DT4, f"got={got}")

        # I. reason của nhánh tương lai phải in GIÁ TRỊ THẬT đọc được (§29): ts + số phút lệch.
        ts = aware(-120)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _gate(tmp, _health(ts))
        check(T + "I. reason tương lai in ra ts thật + số phút lệch (120)",
              ts in buf.getvalue() and "120min" in buf.getvalue(), f"printed={buf.getvalue()!r}")

        got = _gate(tmp, _health(aware(5), status="FAILED"))
        check(T + "F. tươi nhưng status=FAILED ⇒ DT4_only", got == DT4, f"got={got}")
        got = _gate(tmp, _health(aware(5), status="DEGRADED", rec="DT4_only"))
        check(T + "F. tươi nhưng rec=DT4_only ⇒ DT4_only", got == DT4, f"got={got}")
        got = _gate(tmp, _health(aware(5), status="DEGRADED"))
        check(T + "F. tươi, DEGRADED + rec=DT5G_macro ⇒ DT5G_macro (hành vi cũ)", got == DT5G, f"got={got}")

        # G. frozen-state guard: "live" = end cách hôm nay (ICT) ≤ 10 ngày ⇒ có gọi bq kiểm freshness.
        today_ict = now.date()
        for lag, want_calls in ((10, 1), (11, 0)):
            bq = _BqStub()
            _gate(tmp, _health(aware(5)), end=str(today_ict - timedelta(days=lag)), bq=bq)
            check(T + f"G. end = hôm nay ICT − {lag} ngày ⇒ freshness probe gọi {want_calls} lần",
                  bq.calls == want_calls, f"calls={bq.calls}")

        # H. writer thật ⇄ reader thật: ts đúng như macro_healthcheck.py sẽ ghi.
        expr = _writer_ts_expr()
        writer_now = eval(expr, {"datetime": datetime, "ZoneInfo": ZoneInfo})  # noqa: S307
        ts = writer_now.isoformat(timespec="seconds")
        got = _gate(tmp, _health(ts))
        check(T + f"H. ts do writer thật sinh (NOW = {expr}) ⇒ DT5G_macro", got == DT5G,
              f"got={got} ts={ts!r}")


def main():
    msl.get_macro_state = _stub_macro
    inherited = os.environ.get("TZ")
    shifted = _date_shifted_tz()
    print(f"macro_gate_health_tz_selfcheck — TZ thừa hưởng={inherited or '<unset>'}, "
          f"TZ lệch ngày với ICT lúc này={shifted}")
    seen = set()
    for label, tz in [(f"thừa hưởng:{inherited or '<unset>'}", inherited), ("<unset>", None),
                      ("UTC", "UTC"), ("America/New_York", "America/New_York"), (shifted, shifted)]:
        if tz in seen:
            continue
        seen.add(tz)
        _set_tz(tz)
        print(f"\n--- host TZ = {label} (giờ host {time.strftime('%Y-%m-%d %H:%M')}) ---")
        run_cases(label)
    _set_tz(inherited)

    n, ok = len(results), sum(results)
    print(f"\n===== macro_gate_health_tz_selfcheck: {ok}/{n} PASS =====")
    return 0 if ok == n else 1


if __name__ == "__main__":
    sys.exit(main())
