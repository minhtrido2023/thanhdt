#!/usr/bin/env python3
"""Selfcheck cho intraday_oos_monthly.py (fixture tạm, không chạm data thật)."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import intraday_oos_monthly as M  # noqa: E402

fails = []


def check(name, cond):
    print(("PASS" if cond else "FAIL"), name)
    if not cond:
        fails.append(name)


def w(d, day, lines):
    with open(os.path.join(d, f"shadow_{day}.jsonl"), "w", encoding="utf-8") as f:
        for ln in lines:
            f.write((ln if isinstance(ln, str) else json.dumps(ln, ensure_ascii=False)) + "\n")


with tempfile.TemporaryDirectory() as d:
    scans = [{"kind": "SCAN"}] * 3
    w(d, "2026-10-09", [{"kind": "SCAN"}, {"kind": "EOD_OOS", "rows": [{"kind": "case", "ticker": "OLD"}]}])  # trước OOS_START
    w(d, "2026-10-12", scans + [{"kind": "CRASH"}, '{"kind": "CRA'])                                        # crash + dòng cụt, thiếu EOD_OOS
    w(d, "2026-10-13", scans + [{"kind": "EOD_OOS", "rows": []}])
    w(d, "2026-10-14", scans + [{"kind": "QUOTE_ERROR"}, {"kind": "EOD_OOS", "rows": [
        {"kind": "case", "ticker": "AAA"}, {"kind": "market_wide", "ticker": "BBB"}]}])
    w(d, "2026-11-03", scans + [{"kind": "EOD_OOS", "rows": [{"kind": "case", "ticker": "CCC"}]}])
    r = M.summarize("2026-10", d)
    t, k = r["thang"], r["luy_ke"]
    check("bỏ phiên trước OOS_START", t["phien_co_log"] == 3)
    check("đếm scan", t["scan"] == 9)
    check("đếm crash + dòng hỏng", t["crash"] == 1 and t["dong_hong"] == 1)
    check("phiên thiếu EOD_OOS", t["phien_thieu_eod_oos"] == ["2026-10-12"])
    check("market_wide KHÔNG tính là ca", t["ngay_co_ca"] == ["2026-10-14"] and k["ma_co_ca"] == ["AAA"])
    check("luỹ kế / thiếu tới 30", k["ngay_co_ca"] == 1 and k["con_thieu_toi_muc_tieu"] == 29)
    r2 = M.summarize("2026-11", d)
    check("tháng sau: luỹ kế gồm cả tháng trước, tháng chỉ riêng mình",
          r2["thang"]["ngay_co_ca"] == ["2026-11-03"] and r2["luy_ke"]["ngay_co_ca"] == 2)
    check("tháng rỗng không crash", M.summarize("2027-01", d)["thang"]["phien_co_log"] == 0)
    check("render có luỹ kế", "1/30" in M.render(r))
print("FAILS:", fails or "none")
sys.exit(1 if fails else 0)
