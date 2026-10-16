"""Selfcheck: moi query doc fa_ratings_8l 'dong moi nhat' PHAI loc f.time <= ngay as-of (PIT).
fa_ratings_8l co dong eff_date TUONG LAI (vd PMT 2026-10-18 do fallback cu q_time+45, da bo 2026-10-16).
Tai hien: (1) tinh — 2 file nguon co `f.time <= DATE`; (2) song — query da loc khong tra dong tuong lai,
con query KHONG loc (mutant) thi tra (neu bang con dong tuong lai thi kiem chung duoc mutant bi bat)."""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
FILES = ["deploy_golive_dt5g_v4/golive_recommend_v23.py", "hit_details.py"]
fail = 0
def chk(ok, msg):
    global fail
    print(("PASS " if ok else "FAIL ") + msg); fail += (not ok)
# bien as-of mong doi theo file (khong chi chu "DATE": mutant DATE '2099-12-31' phai bi bat)
ASOF_VAR = {"deploy_golive_dt5g_v4/golive_recommend_v23.py": r"LATEST", "hit_details.py": r"\{date\}"}
for f in FILES:
    s = open(os.path.join(HERE, f), encoding="utf-8").read()
    ms = list(re.finditer(r"fa_ratings_8l[`\"]?\s+(?:AS\s+)?f\b(.{0,300})", s, re.S))
    chk(len(ms) >= 1, f"{f}: tim thay >=1 query fa_ratings_8l (khong PASS rong)")
    for m in ms:
        blk = m.group(1).split('"""')[0]
        chk(re.search(r"f\.time\s*<=\s*DATE\s*'[^']*" + ASOF_VAR[f], blk) is not None,
            f"{f}: query fa_ratings_8l loc f.time <= DATE '<as-of {ASOF_VAR[f]}>'")
if "--static" not in sys.argv:
    import pandas as pd
    from simulate_holistic_nav import bq
    asof = "2026-10-15"
    q = lambda w: bq(f"""SELECT f.ticker, f.time, f.rating FROM tav2_bq.fa_ratings_8l AS f {w}
QUALIFY ROW_NUMBER() OVER (PARTITION BY f.ticker ORDER BY f.time DESC) = 1""")
    good, bad = q(f"WHERE f.time <= DATE '{asof}'"), q("")
    chk(pd.Timestamp(good["time"].max()) <= pd.Timestamp(asof), f"song: query loc khong tra dong sau {asof} (max={good['time'].max()})")
    fut = bad[pd.to_datetime(bad["time"]) > pd.Timestamp(asof)]
    print(f"INFO mutant khong loc tra {len(fut)} dong tuong lai: {list(fut['ticker'])[:8]}")
    if len(fut):
        chk(all(pd.Timestamp(good.loc[good.ticker == t, "time"].iloc[0]) <= pd.Timestamp(asof) for t in fut["ticker"] if t in set(good["ticker"])),
            "song: ma co dong tuong lai nay lay dong <= as-of (khong lay dong tuong lai)")
print("RESULT", "FAIL" if fail else "PASS"); sys.exit(1 if fail else 0)
