"""Selfcheck: moi query doc fa_ratings_8l 'dong moi nhat' PHAI loc f.time <= ngay as-of (PIT).
fa_ratings_8l co dong eff_date TUONG LAI (Release_Date NULL ⇒ q_time+45; vd PMT 2026-10-18).
Tai hien: (1) tinh — 2 file nguon co `f.time <= DATE`; (2) song — query da loc khong tra dong tuong lai,
con query KHONG loc (mutant) thi tra (neu bang con dong tuong lai thi kiem chung duoc mutant bi bat)."""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
FILES = ["deploy_golive_dt5g_v4/golive_recommend_v23.py", "hit_details.py"]
fail = 0
def chk(ok, msg):
    global fail
    print(("PASS " if ok else "FAIL ") + msg); fail += (not ok)
for f in FILES:
    s = open(os.path.join(HERE, f), encoding="utf-8").read()
    for m in re.finditer(r"FROM tav2_bq\.fa_ratings_8l AS f(.{0,260})", s, re.S):
        blk = m.group(1).split('"""')[0]
        chk(re.search(r"f\.time\s*<=\s*DATE", blk) is not None, f"{f}: query fa_ratings_8l co loc f.time <= DATE")
if "--static" not in sys.argv:
    from simulate_holistic_nav import bq
    asof = "2026-10-15"
    q = lambda w: bq(f"""SELECT f.ticker, f.time, f.rating FROM tav2_bq.fa_ratings_8l AS f {w}
QUALIFY ROW_NUMBER() OVER (PARTITION BY f.ticker ORDER BY f.time DESC) = 1""")
    good, bad = q(f"WHERE f.time <= DATE '{asof}'"), q("")
    chk(str(good["time"].max()) <= asof, f"song: query loc khong tra dong sau {asof} (max={good['time'].max()})")
    fut = bad[bad["time"].astype(str) > asof]
    print(f"INFO mutant khong loc tra {len(fut)} dong tuong lai: {list(fut['ticker'])[:8]}")
    if len(fut):
        chk(not set(good["ticker"]) >= set() or all(str(good.loc[good.ticker == t, 'time'].iloc[0]) <= asof for t in fut["ticker"] if t in set(good["ticker"])),
            "song: ma co dong tuong lai nay lay dong <= as-of (khong lay dong tuong lai)")
print("RESULT", "FAIL" if fail else "PASS"); sys.exit(1 if fail else 0)
