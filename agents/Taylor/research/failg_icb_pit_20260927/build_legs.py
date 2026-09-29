"""Build the two A/B rating inputs + symlink-farm cache dirs for the pinned R3 legs.

One variable only: the ICB route code path inside rating_8l_history.py.
  ctl  = data/rating_8l_history.csv            (main @f2cfb124, ANY_VALUE route, HDG=POWER)
  new  = r8l_hist_EXP_icbpit_v2.csv            (branch @7cdc08cc, ICB-PIT, HDG=REALESTATE)
Both were produced from the SAME live-BQ vintage today (rating_8l_history.py's own bq() shells out
to the bq CLI and does NOT honour BQ_LOCAL_CACHE, so neither leg is reading a stale cache).

Dedupe per (ticker, eff_date) reproduces refresh_bq_table()'s SQL exactly: keep the row with the
LATEST q_time, then project to the 5 columns the engine's rating query reads.
Everything else in the cache is SYMLINKED to the pinned 2.0GB snapshot -> zero data drift, no copy.
"""
import os, pandas as pd, hashlib, json

WC = "/home/trido/thanhdt/WorkingClaude"
PIN = os.path.join(WC, "data/bq_cache_asof20260729_postrestate")
HERE = os.path.dirname(os.path.abspath(__file__))
LEGS = {"ctl_anyvalue": os.path.join(WC, "data/rating_8l_history.csv"),
        "new_icbpit":   os.path.join(HERE, "r8l_hist_EXP_icbpit_v2.csv")}

def dedupe(csv):
    d = pd.read_csv(csv)
    d["eff_date"] = pd.to_datetime(d["eff_date"])
    d["q_time"] = pd.to_datetime(d["q_time"])
    d = d.sort_values(["ticker", "eff_date", "q_time"])
    d = d.drop_duplicates(["ticker", "eff_date"], keep="last")
    out = pd.DataFrame({"ticker": d.ticker.values, "time": d.eff_date.dt.date.values,
                        "route": d.route.values, "rating": d.rating.astype("int64").values,
                        "tier": d.tier.values})
    return out.sort_values(["ticker", "time"]).reset_index(drop=True)

ref = pd.read_parquet(os.path.join(PIN, "fa_ratings_8l.parquet"))
print(f"pinned snapshot fa_ratings_8l: {len(ref)} rows, dtypes {dict(ref.dtypes.astype(str))}")

summary = {}
for tag, csv in LEGS.items():
    t = dedupe(csv)
    farm = os.path.join(HERE, f"cache_{tag}")
    os.makedirs(farm, exist_ok=True)
    for name in os.listdir(PIN):
        dst = os.path.join(farm, name)
        if name == "fa_ratings_8l.parquet":
            continue
        if os.path.islink(dst) or os.path.exists(dst):
            continue
        os.symlink(os.path.join(PIN, name), dst)
    pq = os.path.join(farm, "fa_ratings_8l.parquet")
    # match the pinned parquet's dtypes exactly (bq_local_cache casts on mismatch and warns)
    for c in ref.columns:
        if str(ref[c].dtype) == "int64":
            t[c] = t[c].astype("int64")
    t.to_parquet(pq, index=False)
    md5 = hashlib.md5(open(pq, "rb").read()).hexdigest()
    hdg = t[t.ticker == "HDG"]; dih = t[t.ticker == "DIH"]
    print(f"\n[{tag}] {len(t)} rows -> {pq}\n  md5 {md5}")
    print(f"  HDG routes {sorted(hdg.route.unique())} last rating {hdg.iloc[-1].rating if len(hdg) else None}")
    print(f"  DIH routes {sorted(dih.route.unique())} last rating {dih.iloc[-1].rating if len(dih) else None}")
    summary[tag] = {"rows": int(len(t)), "parquet_md5": md5, "src_csv": csv,
                    "src_csv_md5": hashlib.md5(open(csv, "rb").read()).hexdigest()}

a = dedupe(LEGS["ctl_anyvalue"]); b = dedupe(LEGS["new_icbpit"])
j = a.merge(b, on=["ticker", "time"], how="outer", suffixes=("_c", "_n"), indicator=True)
assert (j["_merge"] == "both").all(), j["_merge"].value_counts().to_dict()
diff = j[(j.route_c != j.route_n) | (j.rating_c != j.rating_n) | (j.tier_c != j.tier_n)]
print(f"\nengine-visible rows differing between legs: {len(diff)} "
      f"(tickers {sorted(diff.ticker.unique())})")
# The engine's window ends at AUDIT_END; anything after is never read.
AUDIT_END = pd.Timestamp("2026-06-19").date()
inwin = diff[diff.time <= AUDIT_END]
print(f"  of those, INSIDE the backtest window (time <= {AUDIT_END}): {len(inwin)}")
print(f"  rating differs inside window: {int((inwin.rating_c != inwin.rating_n).sum())}")
print(f"  <=3 gate flips inside window: "
      f"{int((((inwin.rating_c<=3) & (inwin.rating_n>=4)) | ((inwin.rating_c>=4) & (inwin.rating_n<=3))).sum())}")
inwin.to_csv("engine_visible_diff_in_window.csv", index=False)
summary["engine_visible_diff_rows"] = int(len(diff))
summary["engine_visible_diff_in_window"] = int(len(inwin))
json.dump(summary, open("legs_summary.json", "w"), indent=1)
print("\nwrote legs_summary.json + engine_visible_diff_in_window.csv")
