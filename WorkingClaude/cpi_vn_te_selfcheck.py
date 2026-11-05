#!/usr/bin/env python3
"""cpi_vn_te_selfcheck.py — Tier 1.4 (TE snapshot) cua cpi_vn.py + writer trong te_macro_crosscheck.py.
Chay: env -u TZ python3 cpi_vn_te_selfcheck.py   va   TZ=America/New_York python3 cpi_vn_te_selfcheck.py
Hermetic (fiin/TE gia lap trong thu muc tam). "old" = cpi_vn.py o commit bb0f8f4ba (cha cua thay doi), doc bang git show."""
import contextlib, importlib.util, io, os, subprocess, sys, tempfile
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OLD_REF = os.environ.get("CPI_OLD_REF", "bb0f8f4ba")
tmp = tempfile.mkdtemp(); FAIL = []
def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: FAIL.append(m)

fiin = os.path.join(tmp, "fiin.csv")
months = [str(d)[:7] for d in pd.date_range("2008-01-01", "2026-08-01", freq="MS")]
open(fiin, "w").write("month,cpi_yoy_pct\n" + "".join(f"{m},{3.0 + (i % 7) * 0.1:.2f}\n" for i, m in enumerate(months)))

def snap(path, rows, snapshot_at="2026-11-04T18:00:00Z", hdr="month,te_cpi_yoy_pct,obs_date,fetched_at,snapshot_at"):
    open(path, "w").write(hdr + "\n" + "".join(f"{m},{v},{m}-28,{snapshot_at},{sa or snapshot_at}\n" for m, v, sa in rows))

def load(path, name, env):
    for k in ("TE_CPI_CSV", "TE_CPI_FAKE_NOW", "FIINPRO_CPI_CSV"): os.environ.pop(k, None)
    os.environ.update(env); os.environ["TE_CPI_SELFCHECK"] = "1"
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    err = io.StringIO()
    with contextlib.redirect_stderr(err): sp.loader.exec_module(m)
    return m, err

def run(M, end):
    err = io.StringIO()
    with contextlib.redirect_stderr(err): df = M.cpi_monthly_df(end=end)
    return df, err.getvalue()

old_src = subprocess.run(["git", "show", f"{OLD_REF}:WorkingClaude/cpi_vn.py"], cwd=HERE, capture_output=True, text=True)
oldp = os.path.join(tmp, "cpi_old.py"); open(oldp, "w").write(old_src.stdout)
ok(old_src.returncode == 0 and "TIER 1.5" in old_src.stdout, f"old ref {OLD_REF} doc duoc")
NEWP = os.path.join(HERE, "cpi_vn.py")
NOW = "2026-11-05T01:00:00Z"
E_ = {"FIINPRO_CPI_CSV": fiin, "TE_CPI_FAKE_NOW": NOW}
te = os.path.join(tmp, "te.csv")
base = [("2007-01", 6.50, None), ("2007-12", 12.70, None), ("2026-06", 4.69, None), ("2026-07", 4.45, None),
        ("2026-08", 4.89, None), ("2026-09", 5.08, None), ("2026-10", 5.09, None)]
END = "2026-12-01"
O, _ = load(oldp, "old", E_); dold, _ = run(O, END)

# 1) tang uu tien: TE chi phuc vu thang ngoai fiinprox/NSO
snap(te, base)
N, e = load(NEWP, "n1", {**E_, "TE_CPI_CSV": te}); d, w = run(N, END); d = d.set_index("time")
ok(abs(d.loc["2026-09-01", "cpi_yoy"] - 5.08) < 1e-9 and bool(d.loc["2026-09-01", "is_te"]), "2026-09 = TE 5.08, is_te")
ok(abs(d.loc["2026-10-01", "cpi_yoy"] - 5.09) < 1e-9, "2026-10 = TE 5.09")
ok(abs(d.loc["2007-01-01", "cpi_yoy"] - 6.50) < 1e-9 and not bool(d.loc["2007-01-01", "is_backfill_2007_2010"]), "2007-01 TE thay Tier 3")
ok(abs(d.loc["2026-06-01", "cpi_yoy"] - 4.69) < 1e-9 and bool(d.loc["2026-06-01", "is_real_nso"]) and not bool(d.loc["2026-06-01", "is_te"]), "NSO > TE (06/2026)")
ok(abs(d.loc["2026-07-01", "cpi_yoy"] - dold.set_index("time").loc["2026-07-01", "cpi_yoy"]) < 1e-9 and not bool(d.loc["2026-07-01", "is_te"]),
   "fiinprox >= TE: 2026-07 giu gia tri fiinprox (TE 4.45 lech > 0.3 khong duoc dung)")
ok("TE vs fiinprox LỆCH" in w, "lech TE-fiinprox > 0.3pp => canh bao")
chg = d[(d.cpi_yoy - dold.set_index("time").cpi_yoy).abs() > 1e-9].index
ok(set(str(t)[:7] for t in chg) <= {"2007-01", "2007-12", "2026-09", "2026-10"} and len(chg) >= 4, f"chi doi dung thang TE-only: {sorted(str(t)[:7] for t in chg)}")
ok(N.te_state().startswith("ON"), "te_state ON")

# 2) TE vs NSO lech => canh bao, giu NSO
snap(te, [("2026-06", 4.90, None)] + base[:2])
N, _ = load(NEWP, "n2", {**E_, "TE_CPI_CSV": te}); d, w = run(N, END)
ok("TE vs NSO LỆCH" in w and abs(d.set_index("time").loc["2026-06-01", "cpi_yoy"] - 4.69) < 1e-9, "TE vs NSO lech => canh bao + giu NSO")

# 3) fail-closed: stale / thieu file / header la / rong => y het old
def same_as_old(tag, env, setup):
    setup(); N, e = load(NEWP, "n_" + tag, {**E_, **env}); dn, w = run(N, END)
    cols = ["time", "cpi_yoy", "cpi_yoy_chg3", "is_real_nso", "is_fiinpro", "is_backfill_2007_2010"]
    eq = dn[cols].equals(dold[cols]) and not dn.is_te.any()
    ok(eq, f"{tag}: output GIONG HET old (fail-closed)")
    ok("Tier 1.4 TE UNAVAILABLE" in (e.getvalue() + w) and N.te_state().startswith("OFF"), f"{tag}: noi thang ly do + te_state OFF")
same_as_old("stale", {"TE_CPI_CSV": te, "TE_CPI_FAKE_NOW": "2026-12-01T00:00:00Z"}, lambda: snap(te, base))
same_as_old("thieu_file", {"TE_CPI_CSV": os.path.join(tmp, "khong_co.csv")}, lambda: None)
bad = os.path.join(tmp, "bad.csv")
same_as_old("header_la", {"TE_CPI_CSV": bad}, lambda: snap(bad, base, hdr="a,b,c,d,e"))
emp = os.path.join(tmp, "emp.csv")
same_as_old("rong", {"TE_CPI_CSV": emp}, lambda: snap(emp, []))
# stale sat bien: 14d chua stale, 15d stale
snap(te, base, snapshot_at="2026-10-22T01:00:00Z")
N, _ = load(NEWP, "n_b14", {**E_, "TE_CPI_CSV": te, "TE_CPI_FAKE_NOW": "2026-11-05T00:00:00Z"}); ok(N.te_state().startswith("ON"), "13d23h => van ON")
N, _ = load(NEWP, "n_b15", {**E_, "TE_CPI_CSV": te, "TE_CPI_FAKE_NOW": "2026-11-06T02:00:00Z"}); ok(N.te_state().startswith("OFF"), ">14d => OFF")

# 3b) guard gia tri + snapshot tuong lai => TE OFF (giong old), kem canh bao
for tag, v in (("v50", "50"), ("vm30", "-30"), ("vnan", "nan"), ("vinf", "inf")):
    g = os.path.join(tmp, tag + ".csv")
    snap(g, base[:2] + [("2026-06", v, None)])
    N, e = load(NEWP, "n_" + tag, {**E_, "TE_CPI_CSV": g}); dn, w = run(N, END)
    ok(N.te_state().startswith("OFF") and not dn.is_te.any(), f"guard gia tri {v} => TE OFF")
    if True:
        ok(("ngoài" in N.te_state()) or ("không phải số" in N.te_state()), f"guard gia tri {v}: te_state noi ly do")
fut = os.path.join(tmp, "fut.csv"); snap(fut, base, snapshot_at="2026-11-08T00:00:00Z")
N, e = load(NEWP, "n_fut", {**E_, "TE_CPI_CSV": fut}); dn, w = run(N, END)
ok(N.te_state().startswith("OFF") and "TƯƠNG LAI" in N.te_state() and not dn.is_te.any(), "snapshot_at tuong lai (+3d) => TE OFF + canh bao")
snap(fut, base, snapshot_at="2026-11-05T12:00:00Z")
N, _ = load(NEWP, "n_fut2", {**E_, "TE_CPI_CSV": fut}); ok(N.te_state().startswith("ON"), "snapshot_at +11h (<1d) => van ON")
N, _ = load(NEWP, "n_nofake", {"FIINPRO_CPI_CSV": fiin, "TE_CPI_CSV": fut, "TE_CPI_FAKE_NOW": "2020-01-01T00:00:00Z"})
os.environ.pop("TE_CPI_SELFCHECK"); import importlib as _il
sp_ = importlib.util.spec_from_file_location("n_nofake2", NEWP); M_ = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(M_)
ok(abs((M_._utcnow() - pd.Timestamp.now(tz="UTC")).total_seconds()) < 5, "TE_CPI_FAKE_NOW bi bo qua khi khong co co TE_CPI_SELFCHECK")

# 4) revision: dong snapshot_at moi nhat thang
snap(te, [("2026-09", 5.08, "2026-10-01T00:00:00Z"), ("2026-09", 5.30, "2026-11-04T18:00:00Z"), ("2026-10", 5.09, "2026-11-04T18:00:00Z")])
N, _ = load(NEWP, "n4", {**E_, "TE_CPI_CSV": te}); d, _ = run(N, END)
ok(abs(d.set_index("time").loc["2026-09-01", "cpi_yoy"] - 5.30) < 1e-9, "revision: lay dong snapshot_at moi nhat")

# 5) writer append-only
os.environ.update(TE_XCHECK_SELFCHECK="1", TE_XCHECK_DATA_DIR=tmp, FIINPRO_CPI_CSV=fiin)
sys.path.insert(0, HERE)
import te_macro_crosscheck as T
from datetime import datetime, timezone
W = os.path.join(tmp, "w.csv"); f0 = datetime(2026, 11, 4, 15, tzinfo=timezone.utc)
t1 = datetime(2026, 11, 5, 1, tzinfo=timezone.utc); t2 = datetime(2026, 11, 12, 1, tzinfo=timezone.utc); t3 = datetime(2026, 11, 19, 1, tzinfo=timezone.utc)
rows = {"2026-08-31": 4.89, "2026-09-30": 5.08, "2026-10-31": 5.09}
n1 = T.write_cpi_snapshot(rows, f0, t1, W); b1 = open(W, "rb").read()
n2 = T.write_cpi_snapshot(rows, f0, t2, W); b2 = open(W, "rb").read()
ok(n1 == 3 and n2 == 1, f"lan 1 ghi 3 dong, lan 2 (khong doi) chi 1 heartbeat (n1={n1}, n2={n2})")
ok(b2.startswith(b1), "append-only: noi dung cu giu nguyen tung byte")
rows2 = {**rows, "2026-09-30": 5.20, "2026-11-30": 5.0}
n3 = T.write_cpi_snapshot(rows2, f0, t3, W); b3 = open(W, "rb").read()
ok(n3 == 2 and b3.startswith(b2), f"revision 09 + thang moi 11 (11 la thang moi nhat nen khong them heartbeat rieng) => 2 dong them, khong sua dong cu (n3={n3})")
N, _ = load(NEWP, "n5", {**E_, "TE_CPI_CSV": W, "TE_CPI_FAKE_NOW": "2026-11-20T00:00:00Z"})
ok(abs(N.te_cpi_series()[pd.Timestamp("2026-09-01")] - 5.20) < 1e-9, "reader doc revision tu writer")
bad2 = os.path.join(tmp, "w2.csv"); open(bad2, "w").write("x,y\n1,2\n")
try: T.write_cpi_snapshot(rows, f0, t1, bad2); ok(False, "header la phai tu choi")
except T.Unavailable: ok(open(bad2).read() == "x,y\n1,2\n", "header la => Unavailable, file khong bi dong")
print(f"\nTZ={os.environ.get('TZ', '(unset)')}  {'ALL PASS' if not FAIL else str(len(FAIL)) + ' FAIL'}")
sys.exit(1 if FAIL else 0)
