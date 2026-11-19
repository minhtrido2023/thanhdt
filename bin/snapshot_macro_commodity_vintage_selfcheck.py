#!/usr/bin/env python3
"""Selfcheck snapshot_macro_commodity_vintage.py — ghi vao bang SCRATCH (_selfcheck), roi DROP. Khong cham bang that.
(i) chay 2 lan cung ngay = 0 dong moi lan 2; (ii) 0 dong snapshot_date < observation_date (ke ca --date lui xa);
(iii) so dong == nguon trong ngay; chay duoi `env -u TZ` va TZ=Asia/Tokyo; snapshot_date == ngay ICT doc lap."""
import os, subprocess, sys, datetime as dt
from zoneinfo import ZoneInfo
os.environ.pop("BQ_LOCAL_CACHE", None)
from google.cloud import bigquery
P = "lithe-record-440915-m9"
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "snapshot_macro_commodity_vintage.py")
SFX = "_selfcheck"
c = bigquery.Client(project=P, location="asia-southeast1")
fails = []

def chk(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}", flush=True)
    if not ok: fails.append(name)

def n(sql): return list(c.query(sql).result())[0][0]
def run(env_mods, *args):
    env = dict(os.environ, VINTAGE_SNAP_SUFFIX=SFX)
    for k, v in env_mods.items():
        env.pop(k, None) if v is None else env.__setitem__(k, v)
    return subprocess.run([sys.executable, SCRIPT, *args], env=env, capture_output=True, text=True)
def drop():
    for t in ("macro_indicator_vintage", "commodity_prices_vintage"):
        c.query(f"DROP TABLE IF EXISTS `{P}.tav2_mike.{t}{SFX}`").result()

SRC = {"macro_indicator_vintage": "macro_indicator", "commodity_prices_vintage": "commodity_prices"}
ict = dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()
for label, mods in (("env -u TZ", {"TZ": None}), ("TZ=Asia/Tokyo", {"TZ": "Asia/Tokyo"})):
    drop()
    r1 = run(mods); r2 = run(mods)
    chk(f"[{label}] run1 rc=0", r1.returncode == 0, r1.stdout[-200:] + r1.stderr[-200:])
    chk(f"[{label}] run2 rc=0", r2.returncode == 0)
    for snap, src in SRC.items():
        T = f"`{P}.tav2_mike.{snap}{SFX}`"
        tot = n(f"SELECT COUNT(*) FROM {T}")
        today = n(f"SELECT COUNT(*) FROM {T} WHERE snapshot_date = DATE '{ict}'")
        srcn = n(f"SELECT COUNT(*) FROM `{P}.tav2_bq.{src}` WHERE observation_date <= DATE '{ict}'")
        chk(f"[{label}] (i) {snap}: 2 lan cung ngay, tong = 1 lan", tot == today and tot > 0, f"tong={tot} hom_nay={today}")
        chk(f"[{label}] (i) lan 2 ghi 0 dong (SKIP in log)", "SKIP" in r2.stdout and "INSERT" not in r2.stdout)
        chk(f"[{label}] (ii) {snap}: 0 dong snapshot_date<observation_date",
            n(f"SELECT COUNT(*) FROM {T} WHERE snapshot_date < observation_date") == 0)
        chk(f"[{label}] (iii) {snap}: so dong == nguon", abs(today - srcn) <= max(50, 0.001 * srcn), f"snap={today} nguon={srcn}")
        chk(f"[{label}] snapshot_date == ngay ICT doc lap ({ict})", n(f"SELECT COUNT(DISTINCT snapshot_date) FROM {T} WHERE snapshot_date=DATE '{ict}'") == 1)
# (ii) kiem manh: --date lui xa => bo loc phai loai dong tuong lai
drop()
r = run({"TZ": None}, "--date", "2015-06-30")
for snap, src in SRC.items():
    T = f"`{P}.tav2_mike.{snap}{SFX}`"
    exp = n(f"SELECT COUNT(*) FROM `{P}.tav2_bq.{src}` WHERE observation_date <= DATE '2015-06-30'")
    got = n(f"SELECT COUNT(*) FROM {T}")
    viol = n(f"SELECT COUNT(*) FROM {T} WHERE snapshot_date < observation_date")
    chk(f"(ii-mutation) {snap} --date 2015-06-30: vi pham=0 va dong==nguon<=ngay", viol == 0 and got == exp and got > 0, f"got={got} exp={exp} viol={viol}")
drop()
print("RESULT:", "ALL PASS" if not fails else f"FAIL {fails}")
sys.exit(1 if fails else 0)
