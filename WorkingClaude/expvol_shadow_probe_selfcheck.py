# -*- coding: utf-8 -*-
"""Self-check `mike/bin/expvol_shadow_probe.py` — công cụ ĐO của paper trial `expvol_pacing`.

Vì sao công cụ đo cũng cần selfcheck: gate của trial (order-day N, %slice bind=ceil, vi phạm
clamp) được đọc TỪ ĐÂY. Một lỗi parse ở đây không làm hỏng lệnh nào, nhưng làm kết luận
"P2 an toàn / P2 vô dụng" sai — mà đó chính là thứ trial sinh ra để trả lời.

Bất biến kiểm ở đây: (1) N đếm theo ORDER-DAY chứ không theo dòng; (2) restart giữa phiên ghi
trùng phút KHÔNG thổi phồng mẫu; (3) journal fixture 2099 (selfcheck khác) không lọt vào số
thật; (4) vi phạm trần 50% tape bị BẮT bằng recompute độc lập, không tin field đã ghi.

Run: /home/trido/thanhdt/wc_venv/bin/python expvol_shadow_probe_selfcheck.py  (exit 0 = pass)
"""
import csv
import importlib.util
import os
import sys
import tempfile
from datetime import timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "expvol_shadow_probe", os.path.join(HERE, "mike", "bin", "expvol_shadow_probe.py"))
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


HDR = ["ts", "event", "parent_id", "ticker", "side", "child_oid", "qty", "price",
       "filled_total", "book", "play_type", "note"]


def note(tape, fleet, floor, base_ceil, p2_ceil, bind, p2_clamp=None):
    """`p2_clamp` mặc định TÍNH RA từ (tape, fleet) theo đúng công thức executor: X ≤ (cV−F)/(1−c).

    Bản nháp file này ghi tay `p2_clamp` cho từng ca và một ca sai số học (V=800, F=500 ⇒ clamp
    thật là −200, tôi ghi 300) — kiểm tra B6/B7 đỏ ngay. Đó là recompute độc lập làm đúng việc
    của nó, nên fixture phải suy ra từ công thức, còn ca phá trần thì truyền tay CÓ CHỦ Ý (C1).
    """
    if p2_clamp is None:
        p2_clamp = int((probe.CLAMP * tape - fleet) / (1.0 - probe.CLAMP))
    base = min(floor, base_ceil)
    p2 = min(floor, p2_ceil, p2_clamp)
    return (f"P2 OFF (đối chứng ghép cặp) f(10:00)=0.198;tape={tape};fleet_filled={fleet};"
            f"exp_basis=6975;floor_allow={floor};base_ceil={base_ceil};base_allow={base};"
            f"p2_ceil={p2_ceil};p2_clamp={p2_clamp};p2_allow={p2};delta={p2 - base};bind={bind}")


def write_journal(root, acc, day, rows):
    d = os.path.join(root, "data", "execution_logs")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f"exec_{acc}_{day}_journal.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(HDR)
        for r in rows:
            w.writerow(r)


def row(ts, pid, event="EXPVOL_SHADOW", nt=""):
    return [ts, event, pid, "TV1", "buy", "", 100, 19900, 0, "DISCRETIONARY_SPECIAL", "", nt]


D1 = (probe.today_ict() - timedelta(days=2)).isoformat()
D2 = (probe.today_ict() - timedelta(days=1)).isoformat()
TODAY = probe.today_ict().isoformat()

with tempfile.TemporaryDirectory() as tmp:
    probe.WC_ROOT = tmp
    # Phiên 1: 1 lệnh, 3 slice — trong đó 2 dòng CÙNG PHÚT (mô phỏng restart giữa phiên).
    write_journal(tmp, "SpaceX", D1, [
        row(f"{D1}T10:00:05", "P1", nt=note(500, 0, 3522, 150, 2092, "ceil")),
        row(f"{D1}T10:00:25", "P1", nt=note(500, 0, 3522, 150, 2092, "ceil")),    # trùng phút
        row(f"{D1}T10:08:05", "P1", nt=note(800, 50, 3472, 190, 2042, "ceil")),
    ])
    # Phiên 2: 2 account, tape dày ⇒ floor bind, P2 không nới thêm (delta=0).
    write_journal(tmp, "SpaceX", D2, [
        row(f"{D2}T10:00:05", "P1", nt=note(42700, 0, 3522, 12810, 12810, "floor"))])
    write_journal(tmp, "ZaloPay", D2, [
        row(f"{D2}T10:00:05", "P9", nt=note(500, 0, 3522, 150, 2092, "ceil")),
        row(f"{D2}T10:16:05", "P9", event="EXPVOL_SHADOW_ERR", nt="ValueError: curve rác")])
    # Fixture selfcheck khác (2099) — KHÔNG được lẫn vào số thật.
    write_journal(tmp, "SpaceX", "2099-01-04", [
        row("2099-01-04T10:00:05", "Z1", nt=note(500, 0, 3522, 150, 2092, "ceil"))])

    rows, errs = probe.load_rows(0)
    check("A1 dedupe theo phút: 2 dòng cùng phút/cùng lệnh ⇒ 1 quan sát",
          len(rows) == 4, f"{len(rows)} dòng (kỳ vọng 4)")
    check("A2 journal fixture 2099 bị loại khỏi số thật",
          all("2099" not in str(d) for d, _, _ in rows))
    check("A3 EXPVOL_SHADOW_ERR tách riêng, KHÔNG tính là quan sát", len(errs) == 1, f"{len(errs)}")

    lines, s = probe.summarize(rows, errs, probe.today_ict())
    check("B1 N đếm theo ORDER-DAY (date×account×parent), không theo dòng",
          s["order_days"] == 3, f"{s['order_days']} (kỳ vọng 3: SpaceX/D1/P1, SpaceX/D2/P1, ZaloPay/D2/P9)")
    check("B2 phiên đếm đúng", s["sessions"] == 2, str(s["sessions"]))
    check("B3 chỉ slice bind=ceil vào thống kê delta", s["ceil_slices"] == 3, str(s["ceil_slices"]))
    check("B4 trung vị delta tính trên nhóm bind=ceil (350/510/350 ⇒ 350)",
          s["median_delta"] == 350, str(s["median_delta"]))
    check("B5 số lỗi được báo cáo lên, không nuốt", s["errors"] == 1)
    check("B6 không có vi phạm clamp ở dữ liệu hợp lệ", s["clamp_breaches"] == 0)
    check("B7 %tape tối đa ≤ 50% ở dữ liệu hợp lệ", s["worst_tape_share"] <= 0.5 + 1e-9,
          f"{s['worst_tape_share']:.3f}")

# Ca NGƯỢC: một dòng cố tình phá trần (p2_allow quá lớn so với tape) phải bị BẮT — nếu không,
# gate an toàn của trial chỉ là trang trí.
with tempfile.TemporaryDirectory() as tmp:
    probe.WC_ROOT = tmp
    bad = note(500, 0, 999_999, 150, 999_999, "ceil", p2_clamp=999_999)  # phá trần CÓ CHỦ Ý
    write_journal(tmp, "SpaceX", TODAY, [row(f"{TODAY}T10:00:05", "P1", nt=bad)])
    rows, errs = probe.load_rows(0)
    _, s = probe.summarize(rows, errs, probe.today_ict())
    check("C1 [CHỨNG MINH NGƯỢC] p2_allow phá trần 50% tape ⇒ đếm vi phạm ≥1 (recompute độc "
          "lập, không tin field đã ghi)", s["clamp_breaches"] == 1, str(s["clamp_breaches"]))
    check("C2 %tape tối đa phản ánh đúng mức phá trần", s["worst_tape_share"] > 0.5,
          f"{s['worst_tape_share']:.3f}")
    check("C3 hoạt động HÔM NAY được tách khỏi luỹ kế", "hôm nay" in "\n".join(
        probe.summarize(rows, errs, probe.today_ict())[0]))

print()
if fails:
    print(f"❌ {len(fails)} FAIL: {fails}")
    sys.exit(1)
print("✅ tất cả PASS — probe đếm N theo order-day, chống ghi trùng khi restart, loại fixture "
      "2099, và BẮT được vi phạm trần 50% tape bằng recompute độc lập.")
