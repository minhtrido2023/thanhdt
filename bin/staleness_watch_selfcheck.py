#!/usr/bin/env python3
"""Selfcheck cho bin/staleness_watch.py::age_hours — múi giờ của field "ts".

Ca cần giữ: ts naive = giờ tường ICT (quy ước ghi của macro_healthcheck.py) ⇒ gắn ICT; ts ĐÃ có
múi giờ ⇒ quy đổi (astimezone), KHÔNG ghi đè. Bản cũ `.replace(tzinfo=ICT)` ép mọi ts thành ICT
nên một ts UTC bị đọc lệch đúng 7 giờ mà không báo gì.

Chỉ đọc/ghi trong thư mục tạm. Chạy dưới `env -u TZ` và một múi giờ lạ (§16): kết quả không được
phụ thuộc TZ của tiến trình.
"""
import datetime
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from zoneinfo import ZoneInfo

BIN = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("staleness_watch", BIN / "staleness_watch.py")
sw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sw)

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
PASS = FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"PASS {name}")
    else:
        FAIL += 1
        print(f"FAIL {name}: {detail}")


def age_of(td: Path, ts_text) -> float:
    p = td / "artifact.json"
    p.write_text(json.dumps({"ts": ts_text}), encoding="utf-8")
    return sw.age_hours(str(p))


def main():
    with tempfile.TemporaryDirectory() as d:
        td = Path(d)
        # Cùng MỘT thời điểm (3 giờ trước), viết theo 4 cách — tuổi phải như nhau.
        t = datetime.datetime.now(ICT).replace(microsecond=0) - datetime.timedelta(hours=3)
        utc = t.astimezone(datetime.timezone.utc)
        forms = {
            "naive (giờ tường ICT)": t.replace(tzinfo=None).isoformat(),
            "aware +07:00": t.isoformat(),
            "aware UTC +00:00": utc.isoformat(),
            "aware -05:00": t.astimezone(datetime.timezone(datetime.timedelta(hours=-5))).isoformat(),
        }
        check("S0 fixture đúng dạng: naive không offset, +07:00, +00:00, -05:00",
              "+" not in forms["naive (giờ tường ICT)"] and forms["aware +07:00"].endswith("+07:00")
              and forms["aware UTC +00:00"].endswith("+00:00") and forms["aware -05:00"].endswith("-05:00"),
              forms)
        for i, (label, text) in enumerate(forms.items(), 1):
            age = age_of(td, text)
            check(f"S{i} ts {label} ⇒ tuổi 3,0 giờ", abs(age - 3.0) <= 0.1, (text, age))

        check("S5 ts không parse được ⇒ -1 (UNKNOWN), không ném lỗi", age_of(td, "khong-phai-ngay") == -1.0)
        (td / "artifact.json").write_text("{}", encoding="utf-8")
        check("S6 thiếu field ts ⇒ -1 (UNKNOWN)", sw.age_hours(str(td / "artifact.json")) == -1.0)
        check("S7 file không tồn tại ⇒ -1 (UNKNOWN)", sw.age_hours(str(td / "khong_co.json")) == -1.0)

    print(f"=== {PASS} PASS / {FAIL} FAIL ===")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
