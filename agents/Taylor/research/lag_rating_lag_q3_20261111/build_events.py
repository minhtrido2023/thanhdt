"""Q3/2026 LAG — độ trễ rating 8L so với ngày công bố BCTC (job Taylor_20261111_011218).

Chỉ ĐỌC. Nguồn:
  - data/earnings_surprise_data.pkl + data/earnings_events_classified.csv qua lag_live_schedule.live_lag_candidates
    (đúng hàm golive dùng; qualify tính trên dữ liệu HÔM NAY — priors >=1 quý tuổi nên không đổi theo ngày).
  - tav2_bq.fa_ratings_8l (rating hiện hành + rating quý trước)
  - tav2_bq.fa_ratings_8l / ticker_financial FOR SYSTEM_TIME AS OF (time-travel 7 ngày: 2026-11-04..11-10) ⇒
    ngày ingest BQ + ngày rating Q3 THỰC SỰ xuất hiện trong bảng, đo thật chứ không mô phỏng.
Ra: events_q3.csv, timetravel_q3.csv
"""
import os, sys, subprocess, io, datetime as dt
import pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WC)
OUT = os.path.dirname(os.path.abspath(__file__))
from lag_live_schedule import live_lag_candidates  # noqa: E402


def bq(sql):
    r = subprocess.run(["bq", "query", "--use_legacy_sql=false", "--project_id=lithe-record-440915-m9",
                        "--format=csv", "--max_rows=100000", sql], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr + r.stdout)
    return pd.read_csv(io.StringIO(r.stdout))


cand = live_lag_candidates(start="2026-06-01")
cand = cand[cand["qualify"]].copy()
q3 = cand[(cand["Release_Date"] >= "2026-10-10") & (cand["Release_Date"] <= "2026-11-10")].copy()
q2 = cand[(cand["Release_Date"] >= "2026-07-10") & (cand["Release_Date"] <= "2026-08-10")]
print("qualify Q3 window events:", len(q3), "| Q2 window (cùng hàm, dữ liệu hôm nay):", len(q2))

tl = ",".join(f"'{t}'" for t in sorted(set(q3["ticker"])))
r = bq(f"SELECT ticker, time, rating FROM tav2_bq.fa_ratings_8l WHERE ticker IN ({tl}) AND time >= '2026-04-01'")
r["time"] = pd.to_datetime(r["time"])
rows = []
for e in q3.itertuples():
    rt = r[r.ticker == e.ticker].sort_values("time")
    old = rt[rt.time < e.Release_Date].tail(1)
    new = rt[rt.time >= e.Release_Date].head(1)
    rows.append({"ticker": e.ticker, "quarter": e.quarter, "release": e.Release_Date.date(), "tier": e.tier,
                 "rating_old": int(old.rating.iloc[0]) if len(old) else None,
                 "rating_old_time": old.time.iloc[0].date() if len(old) else None,
                 "rating_new": int(new.rating.iloc[0]) if len(new) else None,
                 "rating_new_time": new.time.iloc[0].date() if len(new) else None})
ev = pd.DataFrame(rows)

# time-travel: ingest BQ (ticker_financial 2026Q3) và hiệu lực rating (fa_ratings_8l time>=release)
snaps = []
for d in pd.date_range("2026-11-04", "2026-11-10"):
    for label, hhmm in (("pre_rerate_17h25", "10:25"), ("pre_golive_18h55", "11:55")):
        ts = f"{d.date()} {hhmm}:00+00"
        tf = bq(f"SELECT ticker, Release_Date FROM tav2_bq.ticker_financial FOR SYSTEM_TIME AS OF TIMESTAMP '{ts}' "
                f"WHERE quarter='2026Q3' AND ticker IN ({tl})")
        fr = bq(f"SELECT ticker, time, rating FROM tav2_bq.fa_ratings_8l FOR SYSTEM_TIME AS OF TIMESTAMP '{ts}' "
                f"WHERE time >= '2026-10-01' AND ticker IN ({tl})")
        snaps.append((d.date(), label, set(tf.ticker), {(t, pd.Timestamp(x).date()) for t, x in zip(fr.ticker, fr.time)}))
tt = []
for e in ev.itertuples():
    first_tf = next((f"{d} {lab}" for d, lab, tf, fr in snaps if e.ticker in tf), None)
    first_fr = next((f"{d} {lab}" for d, lab, tf, fr in snaps
                     if any(t == e.ticker and x >= e.release for t, x in fr)), None)
    stale_at_golive = [str(d) for d, lab, tf, fr in snaps if lab == "pre_golive_18h55" and e.ticker in tf
                       and not any(t == e.ticker and x >= e.release for t, x in fr)]
    tt.append({"ticker": e.ticker, "release": e.release, "tt_first_tf": first_tf, "tt_first_rating": first_fr,
               "tt_days_tf_visible_but_rating_old_at_1855": ";".join(stale_at_golive)})
ev = ev.merge(pd.DataFrame(tt), on=["ticker", "release"], how="left")
ev.to_csv(os.path.join(OUT, "events_q3.csv"), index=False)
print(ev.to_string())
