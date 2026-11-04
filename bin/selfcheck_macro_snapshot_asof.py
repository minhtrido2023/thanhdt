#!/usr/bin/env python3
"""Selfcheck macro_snapshot_asof: không rò sau as-of (so từng series, tính độc lập từ truy vấn thô),
Δ tính lại độc lập, ranh giới live/historical (asof=tmax-1 vs tmax), live khớp macro_indicator_latest, fail-closed.
KHÔNG kiểm chứng bảng LAG: lag là khai báo từ nguồn lịch công bố (docstring module); selfcheck chỉ chứng minh code
áp lag đúng, không chứng minh con số lag đúng với thực tế.
Chạy: env -u TZ python3 ...  và  TZ=America/New_York python3 ...  (tự source wc_env.sh nếu bq chưa có trên PATH)"""
import datetime as dt, os, shutil, subprocess, sys, json
if not shutil.which("bq"):
    _e = "/home/trido/thanhdt/WorkingClaude/wc_env.sh"
    _p = subprocess.run(["bash", "-c", "source %s >/dev/null 2>&1; env -0" % _e], capture_output=True)
    for _kv in _p.stdout.split(b"\0"):
        if b"=" in _kv:
            _k, _v = _kv.decode().split("=", 1)
            if _k == "PATH":
                os.environ["PATH"] = _v
    if not shutil.which("bq"):
        print("FAIL: không tìm thấy `bq` trên PATH kể cả sau khi source %s — selfcheck KHÔNG chạy được (không phải PASS)" % _e)
        sys.exit(3)
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
        out.setdefault(r["series_key"], []).append((dt.date.fromisoformat(r["d"]), float(r["value"])))
    return out

for asof in ["2022-10-31", "2023-06-30", "2025-03-31"]:
    a = dt.date.fromisoformat(asof)
    snap = M.build(M.fetch(a), a, M.table_max(), M.all_series_keys())
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
    # (4) Δ tính lại độc lập từ dữ liệu thô
    dbad = 0; dn = 0
    for k, s in snap["series"].items():
        if k == M.SPREAD_KEY: continue
        lag = M.LAG[k]; cur = [v for d, v in raw[k] if d == dt.date.fromisoformat(s["obs"])][0]
        for key, cut in (("d3", M.months_back(a, 3)), ("d12", M.months_back(a, 12))):
            if key in M.NO_DELTA.get(k, ()):
                if s[key] is not None: dbad += 1
                continue
            ok = [(d, v) for d, v in raw[k] if d + dt.timedelta(days=lag) <= cut]
            old = max(ok) if ok else None
            exp = None if (old is None or old[0] == dt.date.fromisoformat(s["obs"])) else (
                (cur - old[1]) if s["kind"] == "pp" else (None if old[1] == 0 else (cur / old[1] - 1) * 100))
            if (exp is None) != (s[key] is None) or (exp is not None and abs(exp - s[key]) > 1e-6): dbad += 1
            dn += 1
    chk(dn > 10 and dbad == 0, "%s Δ3T/Δ12T khớp tính lại độc lập (%d phép, %d lệch)" % (asof, dn, dbad))
    chk(snap["series"].get("vn_gdp_construction", {}).get("d3", 0) is None and snap["series"].get("vn_gdp_construction", {}).get("d12", 0) is None,
        "%s vn_gdp_construction không in Δ (định nghĩa gãy)" % asof)
    chk(snap["series"].get("vn_fdi", {}).get("d3", 0) is None, "%s vn_fdi không in Δ3T (luỹ kế YTD)" % asof)
    chk("vn_fdi" not in snap["series"] or snap["series"]["vn_fdi"]["lag"] == 10, "%s lag fdi" % asof)
    chk(M.LAG["vn_interbank_3m"] >= 3, "lag vn_interbank_3m >= 3")
    # dữ liệu bị bỏ không bịa
    for k in snap["missing"]: chk(k not in snap["series"], "%s %s thiếu ⇒ không in" % (asof, k))

# ranh giới live: asof=tmax-1 ⇒ historical-lag; asof=tmax ⇒ live
tmax = M.table_max()
for off, want in ((1, "historical-lag"), (0, "live")):
    a = tmax - dt.timedelta(days=off)
    sn = M.build(M.fetch(a), a, tmax, M.all_series_keys())
    chk(sn["mode"] == want, "asof=tmax-%d (%s) mode=%s" % (off, a, want))
    chk(all(dt.date.fromisoformat(v["obs"].split("/")[0]) <= a for v in sn["series"].values()), "asof=tmax-%d không có obs > asof" % off)
    if want == "historical-lag":
        chk(all(v["lag"] > 0 for v in sn["series"].values()), "tmax-1 mọi series áp lag > 0")
    else:
        chk(all(v["lag"] == 0 for v in sn["series"].values()), "tmax live mọi series lag 0")
chk(set(sn["omitted_no_lag"]) >= set(M.EXCLUDED_ON_PURPOSE) and len(sn["omitted_no_lag"]) > 0,
    "omitted_no_lag không rỗng, chứa %s: %s" % (M.EXCLUDED_ON_PURPOSE, sn["omitted_no_lag"]))
md = M.render_md(sn)
chk("bản hiệu chỉnh HIỆN HÀNH" in md and "CÓ CHỦ ĐÍCH" in md, "header md có caveat vintage + loại có chủ đích")

# live khớp macro_indicator_latest
today = M.today_ict()
snap = M.build(M.fetch(today), today, M.table_max(), M.all_series_keys())
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
