import re, pathlib, sys
p = pathlib.Path(sys.argv[1])
s = p.read_text()
HELPER = '''

# ---- H3 HARNESS (job Taylor_20260926_164113) — chi them, khong doi hanh vi mac dinh ----
# OSHARES_PIT=1  -> thay `ticker_financial.OShares` (as-of, CO restate = look-ahead) bang
#                   `data/fiinprox_oshares_pit_20260926.csv` (as-of NGAY DOI SO THAT).
# Khong set / =0 -> file nay chay y het custom_basket.py production (chan control).
_OSHPIT_CSV = "mike/data/fiinprox_oshares_pit_20260926.csv"
_OSHPIT_CACHE = {}


def _oshpit_series():
    """{ticker: (dates_sorted, shares)} tu CSV PIT. Bo dong shares <= 0."""
    if _OSHPIT_CACHE:
        return _OSHPIT_CACHE
    import csv as _csv, os as _os
    path = _OSHPIT_CSV
    if not _os.path.exists(path):
        raise FileNotFoundError(f"OSHARES_PIT=1 nhung khong thay {path}")
    by = {}
    for row in _csv.DictReader(open(path)):
        try:
            sh = float(row["shares"])
        except (TypeError, ValueError):
            continue
        if sh <= 0:
            continue
        by.setdefault(row["ticker"], []).append((row["date"], sh))
    for t in by:
        by[t].sort()
    _OSHPIT_CACHE.update(by)
    return _OSHPIT_CACHE


def _apply_oshares_pit(bx):
    """Ghi de cot OShares bang so PIT as-of; GIU nguyen so cu o ma/ngay PIT khong phu.

    Fail-OPEN theo TUNG MA co chu y: file PIT chi phu 647 ma universe_pit tu 2013 — ma ngoai
    do (hoac ngay truoc dong PIT dau tien) khong co so nao de thay, giu `ticker_financial` la
    hanh vi hien tai chu khong phai bo mã khoi ro (bo mã se doi THANH PHAN ro, tron lan hai
    hieu ung khac nhau vao mot con so).
    """
    import os as _os
    if _os.environ.get("OSHARES_PIT", "") != "1":
        return bx, None
    import bisect as _bis, numpy as _np
    ser = _oshpit_series()
    vals, n_pit, n_keep = [], 0, 0
    for tk, d, old in zip(bx["ticker"].values, bx["time"].values, bx["OShares"].values):
        s = ser.get(tk)
        if s:
            ds = str(_np.datetime_as_string(d, unit="D"))
            i = _bis.bisect_right([x[0] for x in s], ds) - 1
            if i >= 0:
                vals.append(s[i][1]); n_pit += 1; continue
        vals.append(old); n_keep += 1
    bx = bx.copy()
    bx["OShares"] = vals
    stat = {"n_rows": len(vals), "n_from_pit": n_pit, "n_kept_fin": n_keep,
            "pct_pit": round(100.0 * n_pit / max(1, len(vals)), 2)}
    print(f"  [oshares_pit] {stat}")
    return bx, stat
'''
# chen helper sau khoi import
m = re.search(r"\n(?=def pxw_sql)", s)
s = s[:m.start()] + HELPER + s[m.start():]
# chen loi goi sau MOI dong ffill().bfill()
old = '    bx["OShares"] = bx.groupby("ticker")["OShares"].ffill().bfill()\n'
new = old + '    bx, _ = _apply_oshares_pit(bx)          # H3 harness: no-op khi OSHARES_PIT != 1\n'
n = s.count(old)
assert n == 2, f"ky vong 2 call-site, thay {n}"
s = s.replace(old, new)
p.write_text(s)
print(f"patched {p}: {n} call-site")
