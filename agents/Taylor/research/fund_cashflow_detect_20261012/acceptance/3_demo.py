#!/usr/bin/env python3
"""Nghiệm thu 3: dòng tiền GIẢ LẬP (dữ liệu giả trong thư mục tạm) — nạp/rút, ngay trên/dưới ngưỡng,
trong phiên / sau đóng cửa / cuối tuần; in kết quả CẢ HAI tài khoản trên cùng ngày.
Dùng: python3 3_demo.py <worktree/bin>"""
import shutil, sys, tempfile
sys.path.insert(0, sys.argv[1])
import cash_identity_selfcheck as S
ci = S.ci
tmp = tempfile.mkdtemp(prefix="fundcf_demo_")
try:
    base = S.internal_only(S.World(tmp, "base")).build()
    print(f"Ngưỡng: {ci.THRESHOLD_PCT}% NAV đầu cửa sổ. Không có dòng tiền ngoài: "
          + ", ".join(f"{a} {len(base.check(a)['suspects'])} chờ khai" for a in S.ACCOUNTS))
    cases = {"trong phiên (thứ Ba 10/03 10:30)": (S.at(10, "10:30"), 10),
             "sau đóng cửa (thứ Ba 10/03 16:00)": (S.at(10, "16:00"), 10),
             "cuối tuần (thứ Bảy 07/03 11:00)": (S.at(7, "11:00"), 9)}
    n = 0
    for label, (moment, day1) in cases.items():
        nav0 = S.window(base.check("SpaceX"), day1)["nav0"]
        edge = nav0 * ci.THRESHOLD_PCT / 100
        for sign, word in ((1, "NẠP"), (-1, "RÚT")):
            for delta in (2_000, -2_000):
                n += 1
                amount = sign * (edge + delta)
                wd = S.internal_only(S.World(tmp, f"c{n}")).add("SpaceX", moment, "external", amount).build()
                res = {a: wd.check(a) for a in S.ACCOUNTS}
                hit = res["SpaceX"]["suspects"]
                print(f"\n[{label}] {word} {abs(amount):,.0f} VND ở SpaceX ({'TRÊN' if delta > 0 else 'DƯỚI'} ngưỡng "
                      f"{edge:,.0f}): SpaceX {len(hit)} chờ khai · ZaloPay {len(res['ZaloPay']['suspects'])} chờ khai")
                for w in hit:
                    print("   " + ci.suspect_line("SpaceX", w))
finally:
    shutil.rmtree(tmp, ignore_errors=True)
