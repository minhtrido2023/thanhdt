#!/usr/bin/env python3
"""macro_indicator_freshness.py — kiểm tươi các series HẰNG NGÀY của tav2_bq.macro_indicator
(writer = bq_admin, ngoài repo, ~15:00 UTC). WARN-only (không chặn pipeline), FAIL-CLOSED:
thiếu series / truy vấn lỗi / không parse được ⇒ in WARN, KHÔNG BAO GIỜ in OK.

Stdout: dòng `OK macro_indicator ...` hoặc `WARN macro_indicator ...` (bash wrapper post Discord
khi có WARN). Exit 0 = OK, 1 = có WARN. Hôm nay neo ICT tường minh (§16); env MACRO_FRESH_TODAY
(YYYY-MM-DD) và MACRO_FRESH_CSV (file thay cho bq, để selfcheck) chỉ dùng test.
"""
import datetime as dt
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

PROJECT = "lithe-record-440915-m9"
DAILY = ["us_sp500", "us_bond_10y", "us_dxy", "vn_usdvnd", "vn_bond_10y", "cn_usdcny",
         "vn_interbank_3m", "us_bond_2y", "jp_usdjpy"]
MAX_LAG_DAYS = 3  # lịch; cuối tuần T6→T2 = 3 ngày vẫn OK, >3 ⇒ WARN
# Ngưỡng riêng: vn_interbank_3m quan sát hay trễ 1-2 ngày (đo 05/11: obs cuối 11-02 khi nhóm kia 11-04)
# ⇒ 5 ngày lịch, khớp LIQ_MAX_AGE_IB của dna_report (dòng Thanh khoản VN fail-closed cùng ngưỡng).
MAX_LAG_OVERRIDE = {"vn_interbank_3m": 5}
SQL = ("SELECT t.series_key, CAST(MAX(t.observation_date) AS STRING) AS mx "
       "FROM `%s.tav2_bq.macro_indicator` AS t WHERE t.series_key IN (%s) GROUP BY 1"
       % (PROJECT, ",".join("'%s'" % s for s in DAILY)))


def evaluate(rows, today):
    """rows: {series_key: 'YYYY-MM-DD'}. Trả (warns, oks) — thiếu series ⇒ warn."""
    warns, oks = [], []
    for s in DAILY:
        v = rows.get(s)
        if not v:
            warns.append("%s: KHÔNG CÓ dòng nào trong bảng/view (series bị xoá hoặc đổi tên?)" % s)
            continue
        try:
            lag = (today - dt.date.fromisoformat(v)).days
        except ValueError:
            warns.append("%s: observation_date không parse được: %r" % (s, v))
            continue
        lim = MAX_LAG_OVERRIDE.get(s, MAX_LAG_DAYS)
        if lag > lim:
            warns.append("%s: observation_date=%s cách hôm nay %dd (>%dd)" % (s, v, lag, lim))
        else:
            oks.append("%s=%s(lag %dd)" % (s, v, lag))
    return warns, oks


def fetch():
    """→ (rows, error_text). Lỗi mang nguyên văn bằng chứng (§29)."""
    fake = os.environ.get("MACRO_FRESH_CSV")
    if fake:
        out = open(fake).read()
    else:
        p = subprocess.run(["bq", "query", "--use_legacy_sql=false", "--project_id=" + PROJECT,
                            "--format=csv", "--quiet", SQL], capture_output=True, text=True, timeout=90)
        if p.returncode != 0:
            return None, "bq rc=%d: %s" % (p.returncode, (p.stderr.strip() or p.stdout.strip() or "<rỗng>")[:400])
        out = p.stdout
    lines = [l for l in out.strip().splitlines() if l.strip()]
    if not lines or lines[0].split(",")[0] != "series_key":
        return None, "output bq không có header series_key: %r" % out[:200]
    return {l.split(",")[0]: l.split(",")[1].strip() for l in lines[1:] if "," in l}, None


def main():
    t = os.environ.get("MACRO_FRESH_TODAY")
    today = dt.date.fromisoformat(t) if t else dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()
    try:
        rows, err = fetch()
    except Exception as e:  # timeout, thiếu bq…
        rows, err = None, "%s: %s" % (type(e).__name__, e)
    if err:
        print("WARN macro_indicator: KHÔNG đo được freshness (truy vấn lỗi, KHÔNG phải kết luận 'tươi'): " + err)
        return 1
    warns, oks = evaluate(rows, today)
    if warns:
        print("WARN macro_indicator STALE/thiếu (%s): %s" % (today, " | ".join(warns)))
        return 1
    print("OK   macro_indicator daily: " + ", ".join(oks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
