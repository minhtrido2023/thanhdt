"""Dung ban sao cache data/bq_cache_asof20260729_postrestate CHI doi fa_ratings_8l theo dung tac dong cua guard
tren vintage 07-29 (1 truc). Moi file khac = symlink. Tac dong guard tren vintage nay: cac (ticker, 2026Q1) bi co
(RD <= RD 2025Q4 hoac RD < 2026-03-31) ma da co trong TF luc 07-29 => dong tai RD mang rating QUY TRUOC (2025Q4,
lay tu EXP build pin-ICB), them dong tai time=2026-05-04 mang rating cache hien co (rating Q1).
argv: <src_cache> <dst_cache> <exp_build_csv> <flagged_csv> <tf_pin07_csv>"""
import os, sys, json, pandas as pd
src, dst, exp_csv, flag_csv, pin07 = sys.argv[1:6]
os.makedirs(dst, exist_ok=False)
for n in os.listdir(src):
    if n in ("fa_ratings_8l.parquet", "manifest.json"): continue
    os.symlink(os.path.join(os.path.abspath(src), n), os.path.join(dst, n))
c = pd.read_parquet(os.path.join(src, "fa_ratings_8l.parquet"))
fl = pd.read_csv(flag_csv); p7 = pd.read_csv(pin07)
fl = fl.merge(p7[["ticker", "quarter", "time", "Release_Date"]], on=["ticker", "quarter"], suffixes=("", "_p7"))
fl = fl[pd.to_datetime(fl["time_p7"]) != pd.to_datetime(fl["Release_Date_p7"])]   # chi dong doi eff o vintage 07-29
e = pd.read_csv(exp_csv).sort_values(["ticker", "eff_date", "q_time"], ascending=[1, 1, 0]).drop_duplicates(["ticker", "eff_date"])
log = []; add = []
for _, r in fl.iterrows():
    t, rd, tm = r["ticker"], str(r["Release_Date_p7"]), str(r["time_p7"])
    m = (c["ticker"] == t) & (c["time"].astype(str) == rd)
    assert m.sum() == 1, (t, rd, m.sum())
    q1 = c.loc[m].iloc[0].copy()
    er = e[(e["ticker"] == t) & (e["eff_date"] == rd)]
    assert len(er) == 1, (t, rd)
    old = int(q1["rating"]); new = int(er["rating"].iloc[0])
    c.loc[m, "rating"] = new; c.loc[m, "tier"] = er["tier"].iloc[0]
    assert not ((c["ticker"] == t) & (c["time"].astype(str) == tm)).any(), (t, tm)
    q1["time"] = pd.Timestamp(tm).date(); add.append(q1)
    log.append(dict(ticker=t, quarter=r["quarter"], rd=rd, time=tm, rating_at_rd_old=old, rating_at_rd_new=new,
                    rating_added_at_time=old))
c = pd.concat([c, pd.DataFrame(add)], ignore_index=True).sort_values(["ticker", "time"]).reset_index(drop=True)
c["rating"] = c["rating"].astype("int64")
c.to_parquet(os.path.join(dst, "fa_ratings_8l.parquet"), index=False)
man = json.load(open(os.path.join(src, "manifest.json"))); man["tables"]["fa_ratings_8l"]["rows"] = len(c)
man["note_guard"] = "fa_ratings_8l patched by rating_8l_eff_guard_20261020/make_guard_cache.py (1 axis)"
json.dump(man, open(os.path.join(dst, "manifest.json"), "w"), indent=1)
L = pd.DataFrame(log); print(L.to_string(index=False)); print("rows", len(c), "added", len(add))
L.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_guard_cache_patch_0729.csv"), index=False)
