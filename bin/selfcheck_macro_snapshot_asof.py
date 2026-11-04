#!/usr/bin/env python3
"""Selfcheck macro_snapshot_asof: không rò sau as-of (so từng series, tính độc lập từ truy vấn thô),
live khớp macro_indicator_latest, fail-closed. Chạy: env -u TZ python3 ...  và  TZ=America/New_York python3 ..."""
import datetime as dt, os, subprocess, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import macro_snapshot_asof as M

fails = []
def chk(c, msg):
    print(("PASS " if c else "FAIL ") + msg)
    if not c: fails.append(msg)

def raw_all(asof):
    """truy vấn thô độc lập (không lọc theo cách của module): mọi dòng obs<=asof, MỌI fetched_at."""
    sql = ("SELECT t.series_key, CAST(t.observation_date AS STRING) d, t.value FROM `%s.tav2_bq.macro_indicator` AS t "
           "WHERE t.series_key IN (%s) AND t.observation_date <= '%s'" % (M.PROJECT, ",".join("'%s'" % k for k in M.SPEC), asof))
    p = subprocess.run(["bq","query","--use_legacy_sql=false","--project_id="+M.PROJECT,"--format=json","--quiet","--max_rows=1000000",sql],
                       capture_output=True, text=True, timeout=180)
    assert p.returncode == 0, p.stderr
    out = {}
    for r in json.loads(p.stdout):
        out.setdefault(r["series_key"], []).append((dt.date.fromisoformat(r["d"]), r["value"]))
    return out

for asof in ["2022-10-31", "2023-06-30", "2025-03-31"]:
    a = dt.date.fromisoformat(asof)
    snap = M.build(M.fetch(a), a, M.table_max())
    chk(snap["mode"] == "historical-lag", "%s mode historical-lag" % asof)
    raw = raw_all(a)
    leak = 0; mism = 0; n = 0; lagged = 0
    for k, s in snap["series"].items():
        if k == M.SPREAD_KEY: continue
        n += 1
        obs = dt.date.fromisoformat(s["obs"]); lag = M.LAG[k]
        if obs + dt.timedelta(days=lag) > a: leak += 1          # (1) dòng hiện ra phải đã công bố theo lag
        if obs > a: leak += 1
        for key, cut in (("obs3", M.months_back(a, 3)), ("obs12", M.months_back(a, 12))):
            if s[key] and dt.date.fromisoformat(s[key]) + dt.timedelta(days=lag) > cut: leak += 1
        # (2) độc lập: dòng thô mới nhất có obs+lag<=asof
        ok = [d for d, v in raw.get(k, []) if d + dt.timedelta(days=lag) <= a]
        if not ok or max(ok) != obs: mism += 1
        # (3) có dòng thô mới hơn bị lag giấu? (chứng minh test có sức: lag thực sự cắt)
        if any(d > obs for d, v in raw.get(k, [])): lagged += 1
    chk(n >= 10, "%s số series có mặt = %d" % (asof, n))
    chk(leak == 0, "%s 0 dòng lộ sau as-of (obs+lag<=asof, kể cả mốc Δ)" % asof)
    chk(mism == 0, "%s mọi series khớp bản tính độc lập từ dữ liệu thô" % asof)
    chk(lagged > 0, "%s control: %d series có dòng thô MỚI HƠN bị lag chặn (test có sức)" % (asof, lagged))
    # dữ liệu bị bỏ không bịa
    for k in snap["missing"]: chk(k not in snap["series"], "%s %s thiếu ⇒ không in" % (asof, k))

# live khớp macro_indicator_latest
today = M.today_ict()
snap = M.build(M.fetch(today), today, M.table_max())
chk(snap["mode"] == "live", "today mode live")
sql = ("SELECT t.series_key, CAST(t.observation_date AS STRING) d, t.value FROM `%s.tav2_bq.macro_indicator_latest` AS t "
       "WHERE t.series_key IN (%s)" % (M.PROJECT, ",".join("'%s'" % k for k in M.SPEC)))
p = subprocess.run(["bq","query","--use_legacy_sql=false","--project_id="+M.PROJECT,"--format=json","--quiet",sql], capture_output=True, text=True)
lat = {r["series_key"]: (r["d"], float(r["value"])) for r in json.loads(p.stdout)}
bad = [k for k in M.SPEC if k in lat and (k not in snap["series"] or snap["series"][k]["obs"] != lat[k][0] or abs(snap["series"][k]["value"] - lat[k][1]) > 1e-9)]
chk(not bad and len(lat) == len(M.SPEC), "today khớp macro_indicator_latest %d/%d series %s" % (len(lat) - len(bad), len(M.SPEC), bad))

# fail-closed: lỗi bq ⇒ rc 2, không in số
env = dict(os.environ, PATH="/nonexistent")
r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "macro_snapshot_asof.py"), "--asof", "2025-03-31"],
                   capture_output=True, text=True, env=env)
chk(r.returncode == 2 and not r.stdout.strip() and "LỖI" in r.stderr, "bq lỗi ⇒ rc=2, stdout rỗng, stderr nêu lỗi")
# asof tương lai bị từ chối
r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "macro_snapshot_asof.py"), "--asof", "2099-01-01"], capture_output=True, text=True)
chk(r.returncode == 2 and not r.stdout.strip(), "asof tương lai ⇒ rc=2")
# series ngoài SPEC không bao giờ vào snapshot
chk(all(k in M.SPEC or k == M.SPREAD_KEY for k in snap["series"]), "chỉ series có lag khai báo")
print("TZ=%s" % os.environ.get("TZ"), "-> ALL PASS" if not fails else "-> %d FAIL" % len(fails))
sys.exit(1 if fails else 0)
