#!/usr/bin/env python3
"""Selfcheck cho mike/bin/filter_lag_entry_window.py.

Neo vào DỮ LIỆU THẬT của 2 ca đã biết đáp án (không dùng fixture tự bịa cho ca chính):
  · signal 2026-08-03 → plan 2026-08-04: T+1 = APF/MAC/TV2/TV3; DCM/PVT = T+2; DRI/POW = T+3.
    Đây đúng là ca ZaloPay lọc sai (đưa DCM/DRI/POW vào deferred_orders hôm nay, bỏ sót APF).
  · signal 2026-07-27 → plan 2026-07-28: EVF/PSI/VCI đều T+1 (cả 2 plan hôm đó xét đúng cửa sổ).

Chạy: python3 mike/bin/filter_lag_entry_window_selfcheck.py
Phải chạy được cả khi KHÔNG có biến TZ (`env -u TZ ...`) — xem §16 coding_guidelines.
"""
import csv
import datetime as dt
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
WC_ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, WC_ROOT)

import filter_lag_entry_window as F      # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  ✓ " if cond else "  ✗ ") + name + (f"  [{detail}]" if detail and not cond else ""))


def tickers(items):
    return sorted(x["ticker"] for x in items)


# ── 1. Ca thật 2026-08-03 → 2026-08-04 (ca ZaloPay lọc sai) ───────────────────
print("\n[1] signal 2026-08-03 → plan 2026-08-04 (dữ liệu thật)")
r = F.filter_window("2026-08-04", "2026-08-03")
check("cổng lịch PASS", r["calendar_check"]["ok"], str(r["calendar_check"]))
check("due_today == APF/MAC/TV2/TV3",
      tickers(r["due_today"]) == ["APF", "MAC", "TV2", "TV3"], tickers(r["due_today"]))
up = tickers(r["upcoming_next_plans"])
check("DCM/PVT (T+2) + DRI/POW (T+3) nằm ở upcoming, KHÔNG ở due_today",
      all(t in up for t in ("DCM", "PVT", "DRI", "POW"))
      and not any(t in tickers(r["due_today"]) for t in ("DCM", "PVT", "DRI", "POW")), str(up))
check("APF bị ZaloPay bỏ sót → script BẮT được", "APF" in tickers(r["due_today"]))
check("không có dòng nào unparsed", r["counts"]["unparsed"] == 0, str(r["unparsed"]))
check("tổng số dòng LAG = 4+14+7 = 25",
      sum(r["counts"][k] for k in ("due_today", "upcoming_next_plans", "window_passed",
                                   "unparsed")) == 25, str(r["counts"]))
check("entry_date của due_today == plan_date",
      all(x["entry_date"] == "2026-08-04" for x in r["due_today"]))
check("cờ đỏ DD được echo (MAC/TV3 thanh khoản chết)",
      all("THANH_KHOAN_CHET" in (x["dd_red_flags"] or [])
          for x in r["due_today"] if x["ticker"] in ("MAC", "TV3")))

# ── 2. Account-agnostic ───────────────────────────────────────────────────────
print("\n[2] account-agnostic (2 account cùng CSV phải ra cùng due_today)")
a = F.filter_window("2026-08-04", "2026-08-03")
b = F.filter_window("2026-08-04", "2026-08-03")
check("SpaceX vs ZaloPay cùng kết quả", tickers(a["due_today"]) == tickers(b["due_today"]))

# ── 3. Ca thật 2026-07-27 → 2026-07-28 (ca FLOOR_FAIL) ────────────────────────
print("\n[3] signal 2026-07-27 → plan 2026-07-28 (dữ liệu thật)")
r2 = F.filter_window("2026-07-28", "2026-07-27")
check("cổng lịch PASS", r2["calendar_check"]["ok"])
check("EVF/PSI/VCI đều T+1 (due_today)",
      all(t in tickers(r2["due_today"]) for t in ("EVF", "PSI", "VCI")),
      str(tickers(r2["due_today"])))

# ── 4. Cổng lịch fail-closed ──────────────────────────────────────────────────
print("\n[4] cổng lịch — plan_date sai thì TỪ CHỐI phân loại")
r3 = F.filter_window("2026-08-05", "2026-08-03")      # lệch 1 phiên
check("calendar_check.ok == False", r3["calendar_check"]["ok"] is False)
check("due_today rỗng khi cổng lịch FAIL", r3["counts"]["due_today"] == 0)
check("mọi dòng T+N rơi vào unparsed", r3["counts"]["unparsed"] >= 18, str(r3["counts"]))
check("expected_plan_date = 2026-08-04", r3["calendar_check"]["expected_plan_date"] == "2026-08-04")
check("note cảnh báo đứng đầu", str(r3["notes"][0]).startswith("⚠ CỔNG LỊCH FAIL"))

print("\n[4b] cổng lịch qua cuối tuần (signal thứ Sáu 2026-07-31 → thứ Hai 2026-08-03)")
check("thứ Sáu 2026-07-31 là weekday 4", dt.date(2026, 7, 31).weekday() == 4)
r4 = F.filter_window("2026-08-03", "2026-07-31")
check("next_trading_day nhảy qua T7/CN", r4["calendar_check"]["ok"], str(r4["calendar_check"]))
r4b = F.filter_window("2026-08-01", "2026-07-31")     # thứ Bảy — phải FAIL
check("plan_date rơi vào thứ Bảy → FAIL", r4b["calendar_check"]["ok"] is False)

# ── 5. classify_status (đơn vị) ───────────────────────────────────────────────
print("\n[5] classify_status")
cases = [
    ("UPCOMING T+1 phiên tới", ("tplus", 1, None)),
    ("UPCOMING T+12 phiên tới", ("tplus", 12, None)),
    ("UPCOMING 2026-08-11", ("date", None, dt.date(2026, 8, 11))),
    ("WINDOW_PASSED 2026-07-29", ("passed", None, dt.date(2026, 7, 29))),
    ("HALF_SIZE", ("unparsed", None, None)),
    ("", ("unparsed", None, None)),
    (None, ("unparsed", None, None)),
    ("UPCOMING T+ phiên tới", ("unparsed", None, None)),
]
for s, exp in cases:
    got = F.classify_status(s)
    check(f"classify_status({s!r})", got == exp, f"got {got} want {exp}")

# ── 6. Dạng `UPCOMING <ngày>` end-to-end (engine sinh khi entry nằm trong lịch đã biết) ──
print("\n[6] dạng UPCOMING <ngày> — CSV tổng hợp")
tmp = tempfile.mkdtemp(prefix="lagwin_sc_")
p = os.path.join(tmp, "golive_v23_recommendations_2026-08-03.csv")
cols = ["book", "ticker", "play_type", "ta", "close_bq_stale_DO_NOT_USE_AS_REFPRICE", "sector",
        "weight_pct", "weight_base", "status", "capit_cap_total_vnd", "due_diligence"]
rows = [
    dict(book="LAG", ticker="AAA", play_type="LAG_HI", status="UPCOMING 2026-08-04",
         due_diligence="DD AAA [LAG]: ok"),
    dict(book="LAG", ticker="BBB", play_type="LAG_HI", status="UPCOMING 2026-08-07",
         due_diligence="DD BBB [LAG]: ⚠ cờ chất lượng FLOOR_FAIL"),
    dict(book="LAG", ticker="CCC", play_type="LAG_LO", status="UPCOMING 2026-08-03",
         due_diligence="DD CCC [LAG]: 🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason"),
    dict(book="LAG", ticker="DDD", play_type="LAG_HI", status="XYZ_KHONG_BIET",
         due_diligence=""),
    dict(book="BAL", ticker="EEE", play_type="MOMENTUM", status="UPCOMING 2026-08-04",
         due_diligence=""),          # book khác → phải bị bỏ qua
]
with open(p, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for x in rows:
        w.writerow({c: x.get(c, "") for c in cols})
r5 = F.filter_window("2026-08-04", csv_path=p)
check("AAA (ngày == plan_date) → due_today", tickers(r5["due_today"]) == ["AAA"],
      str(tickers(r5["due_today"])))
check("BBB (ngày > plan_date) → upcoming", tickers(r5["upcoming_next_plans"]) == ["BBB"])
check("CCC (ngày < plan_date) → window_passed", tickers(r5["window_passed"]) == ["CCC"])
check("DDD (status lạ) → unparsed", tickers(r5["unparsed"]) == ["DDD"])
check("dòng book=BAL bị bỏ qua",
      "EEE" not in (tickers(r5["due_today"]) + tickers(r5["upcoming_next_plans"])
                    + tickers(r5["window_passed"]) + tickers(r5["unparsed"])))
check("BBB floor_fail=True", r5["upcoming_next_plans"][0]["floor_fail"] is True)
check("CCC dd_red_flags parse đúng 2 cờ",
      r5["window_passed"][0]["dd_red_flags"] == ["THANH_KHOAN_CHET", "NGOAI_UNIVERSE"],
      str(r5["window_passed"][0]["dd_red_flags"]))
check("có unparsed → note cảnh báo", any("không phân loại được" in n for n in r5["notes"]))

# ── 7. Thiếu CSV → lỗi tường minh, KHÔNG raise ────────────────────────────────
print("\n[7] thiếu CSV")
r6 = F.filter_window("2026-08-04", csv_path=os.path.join(tmp, "khong_ton_tai.csv"))
check("trả error thay vì raise", bool(r6.get("error")))
check("calendar_check.ok == False", r6["calendar_check"]["ok"] is False)

# ── 8. Chạy như CLI + exit code + TZ độc lập (§16) ────────────────────────────
print("\n[8] CLI + độc lập TZ")
script = os.path.join(HERE, "filter_lag_entry_window.py")


def run(env_extra, args, unset_tz=False):
    env = dict(os.environ)
    if unset_tz:
        env.pop("TZ", None)
    env.update(env_extra)
    return subprocess.run([sys.executable, script] + args, capture_output=True,
                          text=True, env=env, cwd=WC_ROOT)


out_json = os.path.join(tmp, "out.json")
c = run({}, ["--account", "SpaceX", "--plan-date", "2026-08-04",
             "--signal-date", "2026-08-03", "--out", out_json], unset_tz=True)
check("exit 0 khi cổng lịch PASS (env -u TZ)", c.returncode == 0, c.stderr[-300:])
check("file JSON được ghi", os.path.exists(out_json))
c2 = run({}, ["--plan-date", "2026-08-05", "--signal-date", "2026-08-03"], unset_tz=True)
check("exit 2 khi cổng lịch FAIL", c2.returncode == 2, str(c2.returncode))

outs = []
for tzv, unset in ((None, True), ("UTC", False), ("Asia/Ho_Chi_Minh", False),
                   ("America/New_York", False)):
    c3 = run({} if tzv is None else {"TZ": tzv},
             ["--plan-date", "2026-08-04", "--signal-date", "2026-08-03", "--json"],
             unset_tz=unset)
    outs.append(c3.stdout)
check("kết quả giống hệt nhau ở 4 cấu hình TZ (kể cả env -u TZ)",
      len(set(outs)) == 1 and outs[0].strip().startswith("{"),
      f"{len(set(outs))} biến thể")

# plan_date mặc định (dùng today_ict) phải là ngày ICT, không phải ngày của TZ process
from trading_bot.vn_market import next_trading_day, today_ict   # noqa: E402
import zoneinfo                                                 # noqa: E402
ict_today = dt.datetime.now(zoneinfo.ZoneInfo("Asia/Ho_Chi_Minh")).date()
check("today_ict() == ngày ICT thật", today_ict() == ict_today)
check("plan_date mặc định = phiên kế tiếp của ngày ICT",
      next_trading_day(today_ict()) > ict_today)

print(f"\n=== {len(PASS)}/{len(PASS) + len(FAIL)} PASS ===")
if FAIL:
    print("FAIL:")
    for x in FAIL:
        print("  -", x)
sys.exit(1 if FAIL else 0)
