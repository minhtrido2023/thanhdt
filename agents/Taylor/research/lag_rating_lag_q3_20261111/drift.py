"""Trôi rating của CHÍNH dòng quý Q3 qua các lần re-rate (time-travel 11-04..11-10, mốc 18:55 ICT = trước golive 19:00)."""
import subprocess, io, os, pandas as pd
OUT = os.path.dirname(os.path.abspath(__file__))
ev = pd.read_csv(os.path.join(OUT, "events_q3.csv"))
tl = ",".join(f"'{t}'" for t in sorted(set(ev.ticker)))
def bq(sql):
    r = subprocess.run(["bq","query","--use_legacy_sql=false","--project_id=lithe-record-440915-m9","--format=csv","--max_rows=100000",sql],capture_output=True,text=True)
    assert r.returncode == 0, r.stderr + r.stdout
    return pd.read_csv(io.StringIO(r.stdout))
snaps = [("2026-11-04 01:30","11-04 08:30")] + [(f"{d.date()} 11:55", f"{d.strftime('%m-%d')} 18:55") for d in pd.date_range("2026-11-04","2026-11-10")]
out = ev[["ticker","release","rating_old","rating_new"]].copy()
for ts, lab in snaps:
    f = bq(f"SELECT ticker, CAST(time AS STRING) t, rating FROM tav2_bq.fa_ratings_8l FOR SYSTEM_TIME AS OF TIMESTAMP '{ts}:00+00' WHERE ticker IN ({tl}) AND time>='2026-10-01'")
    m = {(r.ticker, r.t): r.rating for r in f.itertuples()}
    out[lab] = [m.get((t, str(rel))) for t, rel in zip(out.ticker, out.release)]
cols = [l for _, l in snaps]
out["n_distinct"] = out[cols + ["rating_new"]].apply(lambda r: r.dropna().nunique(), axis=1)
out["crosses_3_4"] = out[cols + ["rating_new"]].apply(lambda r: r.dropna().le(3).nunique() > 1, axis=1)
out.to_csv(os.path.join(OUT, "drift_q3.csv"), index=False)
print(out[out.n_distinct > 1].to_string())
print("events with Q3-row rating drift in window:", int((out.n_distinct>1).sum()), "/", len(out), "| crossing 3/4:", int(out.crosses_3_4.sum()))
