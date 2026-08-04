#!/usr/bin/env python3
"""Selfcheck cho mike/bin/sector_valuation_lens.py.

Hai lớp kiểm tra:
  A. NEO DỮ LIỆU THẬT — ca 2026-07-28 (signal 07-27): EVF/PSI/VCI phải ra CHEAP +
     `KHONG_SKIP_VI_FLOOR_FAIL`, và CON SỐ phải khớp đúng thứ SpaceX đã viết tay trong
     `plan_SpaceX_2026-07-28.json` (P/B 0,91 / 0,75 / 1,33; ROE_TTM 9,6% / 8,8% / 9,2%).
     Đây là bằng chứng script tái lập được bên làm ĐÚNG và sửa được bên làm THIẾU (ZaloPay
     ghi "FLOOR_FAIL — skip" cho cả 3).
  B. ROUND-TRIP với hàm THẬT — sinh chuỗi bằng chính `alt_valuation_lens.format_alt_lens()`
     cho MỌI nhánh lăng kính rồi parse ngược. Nếu ai đó đổi câu chữ bên module gốc, test này
     vỡ ngay thay vì để script lặng lẽ trả verdict rỗng.

Chạy: python3 mike/bin/sector_valuation_lens_selfcheck.py   (phải PASS cả với `env -u TZ`)
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WC_ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, WC_ROOT)

import sector_valuation_lens as S       # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  ✓ " if cond else "  ✗ ") + name + (f"  [{detail}]" if detail and not cond else ""))


def by_ticker(res):
    return {r["ticker"]: r for r in res["results"]}


# ── A. Ca thật 2026-07-27 → plan 2026-07-28 ───────────────────────────────────
print("\n[A] ca thật signal 2026-07-27 (EVF/PSI/VCI — SpaceX áp lăng kính, ZaloPay skip)")
r = S.lens_report(["EVF", "PSI", "VCI"], signal_date="2026-07-27")
d = by_ticker(r)
check("đủ 3 mã", set(d) == {"EVF", "PSI", "VCI"}, str(sorted(d)))
for t in ("EVF", "PSI", "VCI"):
    check(f"{t} floor_fail=True", d[t]["floor_fail"] is True)
    check(f"{t} verdict CHEAP", d[t]["verdict"] == "CHEAP", str(d[t]["verdict"]))
    check(f"{t} decision KHONG_SKIP_VI_FLOOR_FAIL",
          d[t]["decision"] == "KHONG_SKIP_VI_FLOOR_FAIL", str(d[t]["decision"]))
    check(f"{t} dùng lăng kính chứng khoán",
          d[t]["lens"] == "P/B band + ROE (chứng khoán)", str(d[t]["lens"]))
# Số phải khớp ĐÚNG plan_SpaceX_2026-07-28.json (bên làm đúng) — không chỉ khớp nhãn CHEAP.
for t, pb, roe in (("EVF", "0.91", "9.6%"), ("PSI", "0.75", "8.8%"), ("VCI", "1.33", "9.2%")):
    check(f"{t} chi tiết khớp số SpaceX đã viết tay (P/B {pb}, ROE_TTM {roe})",
          f"P/B {pb}" in d[t]["detail"] and f"ROE_TTM {roe}" in d[t]["detail"], d[t]["detail"])
check("nguồn là CSV point-in-time, không phải snapshot hôm nay",
      all(v["source"].startswith("csv:") for v in d.values()))
check("không mã nào mang caveat non-PIT", all("caveat" not in v for v in d.values()))

print("\n[A2] --floor-fail-only trên cùng CSV: có đủ 3 loại quyết định")
r2 = S.lens_report(signal_date="2026-07-27", floor_fail_only=True)
d2 = by_ticker(r2)
check("mọi mã trả về đều FLOOR_FAIL", all(v["floor_fail"] for v in d2.values()))
check("EVF/PSI/VCI nằm trong kết quả", all(t in d2 for t in ("EVF", "PSI", "VCI")))
check("có ca RICH → SKIP_CO_CAN_CU (vd AGR/FTS/HCM)",
      any(v["decision"] == "SKIP_CO_CAN_CU" for v in d2.values()), str(r2["counts"]))
check("có ca fallback 8L → CAN_NGUOI_QUYET",
      any(v["decision"] == "CAN_NGUOI_QUYET" and v["lens"] == "8L (fallback rộng)"
          for v in d2.values()), str(r2["counts"]))
check("counts cộng đúng tổng số kết quả",
      sum(r2["counts"].values()) == len(r2["results"]), str(r2["counts"]))
_rich = [v for v in d2.values() if v["decision"] == "SKIP_CO_CAN_CU"]
check("ca RICH có verdict RICH (không phải nhãn lệch)",
      all(v["verdict"] == "RICH" for v in _rich))

print("\n[A3] ca 2026-08-03: mã KHÔNG có lăng kính, và mã DCF chạy được")
r3 = S.lens_report(["AMC", "APF"], signal_date="2026-08-03")
d3 = by_ticker(r3)
check("AMC (không có lăng kính) → CAN_NGUOI_QUYET",
      d3["AMC"]["decision"] == "CAN_NGUOI_QUYET" and d3["AMC"]["lens"] is None,
      f"{d3['AMC']['decision']} / {d3['AMC']['lens']}")
check("APF có DCF chạy được → trục DCF, không dùng fallback",
      d3["APF"]["valuation_axis_used"] == "DCF" and d3["APF"]["verdict"] == "CHEAP",
      f"{d3['APF']['valuation_axis_used']} / {d3['APF']['verdict']}")

# ── B. Round-trip với alt_valuation_lens.format_alt_lens() THẬT ───────────────
print("\n[B] round-trip qua hàm thật alt_valuation_lens.format_alt_lens()")
import alt_valuation_lens as A          # noqa: E402

if not os.path.exists(A.RATING_8L_CSV):
    check("data/rating_8l.csv tồn tại (cần cho round-trip)", False, A.RATING_8L_CSV)
else:
    fake = {
        "TBANK": dict(route="BANK", PB="1.10", ROE5Y="0.174", ICB_Code="8355.0"),
        "TSEC": dict(route="SECURITIES", PB="1.24", ROE_Trailing="0.092", ICB_Code="8777.0"),
        "TINS": dict(route="INSURANCE", PB="1.62", ROE5Y="0.149", ICB_Code="8532.0"),
        "TSHIP": dict(route="COMPOUNDER", PB="0.77", ICB_Code="2773.0"),
        "TPORT": dict(route="COMPOUNDER", eveb_yield="0.20", ICB_Code="2777.0"),
        "TTEL": dict(route="COMPOUNDER", eveb_yield="0.05", ICB_Code="6535.0"),
        "TFALL": dict(route="COMPOUNDER", rating="3", earn_yield="0.158", ICB_Code="9999.0"),
    }
    A._cache.clear()
    A._cache.update(_mtime=os.path.getmtime(A.RATING_8L_CSV), rows=fake)
    expect = {
        "TBANK": ("Gordon P/B (ngân hàng)", "CHEAP"),
        "TSEC": ("P/B band + ROE (chứng khoán)", "CHEAP"),
        "TINS": ("P/B thô (bảo hiểm)", "N/A"),
        "TSHIP": ("P/B trough (vận tải biển)", "CHEAP"),
        "TPORT": ("EV/EBITDA (cảng/hạ tầng)", "CHEAP"),      # 1/0.20 = 5x < 8
        "TTEL": ("EV/EBITDA (viễn thông-hạ tầng)", "RICH"),  # 1/0.05 = 20x > 8
        "TFALL": ("8L (fallback rộng)", "N/A"),
    }
    for tk, (lens_name, verdict) in expect.items():
        text = "DCF: NOT_COMPUTED (test)" + A.format_alt_lens(tk)
        got = S._parse_lens(text)
        check(f"{tk}: parse ngược ra đúng lens+verdict",
              got is not None and got["lens"] == lens_name and got["verdict"] == verdict,
              f"got {got}")
        if got:
            code, _ = S._decide(got["verdict"])
            want = {"CHEAP": "KHONG_SKIP_VI_FLOOR_FAIL", "RICH": "SKIP_CO_CAN_CU",
                    "N/A": "CAN_NGUOI_QUYET"}[verdict]
            check(f"{tk}: decision = {want}", code == want, code)
    # mã không có dòng → format_alt_lens ra câu "chưa có lăng kính"
    got = S._parse_lens("DCF: NOT_COMPUTED (x)" + A.format_alt_lens("KHONG_TON_TAI_XYZ"))
    check("mã không có dữ liệu → parse trả None (không bịa verdict)", got is None, str(got))
    A._cache.clear()

# ── C. Đầu vào rác / thiếu file → không raise ─────────────────────────────────
print("\n[C] fail-safe")
for bad in ("", None, "DCF: NOT_COMPUTED", "→ thay thế: rác không đóng ngoặc",
            "🔴 DD cờ đỏ: X | DCF: NOT_COMPUTED (y)"):
    try:
        S._parse_lens(bad)
        S._parse_dcf(bad)
        ok = True
    except Exception as e:                                   # noqa: BLE001
        ok = False
        print("      ", e)
    check(f"_parse_* chịu được đầu vào {bad!r}", ok)
r4 = S.lens_report(["ZZZ_KHONG_TON_TAI"], signal_date="2026-07-27")
check("mã lạ → rơi về nhánh live, có caveat, không raise",
      r4["results"][0]["source"].startswith("live:") and "caveat" in r4["results"][0],
      json.dumps(r4["results"][0], ensure_ascii=False)[:200])
check("mã lạ không có lăng kính → CAN_NGUOI_QUYET",
      r4["results"][0]["decision"] == "CAN_NGUOI_QUYET")
r5 = S.lens_report(["EVF"], csv_path=os.path.join(WC_ROOT, "khong_ton_tai_xyz.csv"))
check("CSV thiếu → note cảnh báo + vẫn chạy live",
      any("không thấy CSV" in n for n in r5["notes"]), str(r5["notes"])[:200])

# ── D. CLI + độc lập TZ (§16) ─────────────────────────────────────────────────
print("\n[D] CLI + độc lập TZ")
script = os.path.join(HERE, "sector_valuation_lens.py")
outs = []
for tzv, unset in ((None, True), ("UTC", False), ("Asia/Ho_Chi_Minh", False),
                   ("America/New_York", False)):
    env = dict(os.environ)
    if unset:
        env.pop("TZ", None)
    else:
        env["TZ"] = tzv
    c = subprocess.run([sys.executable, script, "--signal-date", "2026-07-27",
                        "--ticker", "EVF", "--ticker", "PSI", "--ticker", "VCI", "--json"],
                       capture_output=True, text=True, env=env, cwd=WC_ROOT)
    outs.append(c.stdout)
    if c.returncode != 0:
        print("      stderr:", c.stderr[-300:])
check("CLI exit 0 + JSON hợp lệ", outs[0].strip().startswith("{") and json.loads(outs[0]))
check("kết quả giống hệt ở 4 cấu hình TZ (kể cả env -u TZ)", len(set(outs)) == 1,
      f"{len(set(outs))} biến thể")

print(f"\n=== {len(PASS)}/{len(PASS) + len(FAIL)} PASS ===")
if FAIL:
    print("FAIL:")
    for x in FAIL:
        print("  -", x)
sys.exit(1 if FAIL else 0)
