"""EXPLORATORY (post-hoc, NGOÀI prereg) — độ nhạy ngưỡng.

Động cơ: self-check §5.3.2 cho thấy các case CHỦ CHỐT của playbook (HPG 2022, TV1 2026,
PNJ 2015, OGC 10/2014) đều bị LOẠI bởi bộ lọc TỐC ĐỘ (<=20 phiên) chứ không phải bởi biên độ.
Chạy để trả lời "bước tiếp theo nên là gì", KHÔNG dùng để tuyên bố verdict — p thô, không BH.
"""
import os
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "1"
import numpy as np, pandas as pd, db_dtypes  # noqa
import postshock_base_formation_20260823 as M

panel = pd.read_parquet(M.HERE/"panel.parquet"); panel["time"]=pd.to_datetime(panel["time"]).astype("datetime64[ns]")
vni = pd.read_parquet(M.HERE/"vnindex.parquet"); vni["time"]=pd.to_datetime(vni["time"]).astype("datetime64[ns]")
rt = pd.read_parquet(M.HERE/"ratings8l.parquet"); rt["time"]=pd.to_datetime(rt["time"]).astype("datetime64[ns]")
sessions = pd.DatetimeIndex(sorted(vni["time"].unique()))

rows, ev_store = [], {}
for speed in (20, 40, 60):
    for ratio in (0.5, 0.7):
        M.MAX_SPEED, M.VOL_RATIO, M.TURN_RATIO = speed, ratio, ratio
        ev = M.build_events(panel)
        ev = ev[ev["t_s"] >= "2008-01-01"].reset_index(drop=True)
        for c in ("t_peak","t_s","t_b","t_conf"):
            ev[c] = pd.to_datetime(ev[c]).astype("datetime64[ns]")
        ev = M.attach_rating(ev, rt); ev = M.attach_vni(ev, vni)
        ev["blk"] = M.block_ids(ev["t_s"], sessions)
        ev["ym"] = ev["t_s"].dt.to_period("M").astype(str)
        key = f"speed{speed}_ratio{ratio}"
        ev_store[key] = ev
        base = ev[ev.base_formed]
        for grp in ("RATING_OK","RATING_BAD","RATING_NA"):
            s = base[base.rating_group==grp]
            r = dict(speed=speed, ratio=ratio, group=grp, n_shock=int((ev.rating_group==grp).sum()),
                     n_base=len(s), n_months=s["ym"].nunique())
            for H in (60,120,250):
                v = s[f"exc{H}_b"].to_numpy(float)
                d = (s[f"fwd{H}_b"]-s[f"fwd{H}_a"]).to_numpy(float)
                th,lo,hi,p,ne = M.boot_stat(v, s["blk"].to_numpy(), rng=np.random.default_rng(1+H))
                r[f"exc{H}_med"], r[f"exc{H}_p"], r[f"exc{H}_n"] = th, p, ne
                th2,_,_,p2,_ = M.boot_stat(d, s["blk"].to_numpy(), rng=np.random.default_rng(2+H))
                r[f"pair{H}_med"], r[f"pair{H}_p"] = th2, p2
            m = s["dd250_a"].notna() & s["dd250_b"].notna()
            r["p_tail_a"] = float((s.loc[m,"dd250_a"]<=M.TAIL_DD).mean()) if m.any() else np.nan
            r["p_tail_b"] = float((s.loc[m,"dd250_b"]<=M.TAIL_DD).mean()) if m.any() else np.nan
            rows.append(r)
        print(f"[{key}] shock={len(ev)} base={len(base)} "
              f"OK={len(base[base.rating_group=='RATING_OK'])}", flush=True)

S = pd.DataFrame(rows)
S.to_csv(M.RES/"postshock_sensitivity_20260823.csv", index=False)
ev_store["speed60_ratio0.5"].to_csv(M.RES/"postshock_events_speed60_20260823.csv", index=False)
pd.set_option("display.width",250,"display.max_columns",40,"display.float_format",lambda x:f"{x:,.4f}")
print("\n=== ĐỘ NHẠY (EXPLORATORY) ===")
print(S[["speed","ratio","group","n_shock","n_base","n_months",
         "exc60_med","exc60_p","exc120_med","exc120_p","exc250_med","exc250_p",
         "pair60_med","pair120_med","pair250_med","p_tail_a","p_tail_b"]].to_string(index=False))

# --- KB case nào lọt vào ở speed<=60 ---
e60 = ev_store["speed60_ratio0.5"]
print("\n=== KB case ở speed<=60 ===")
for tk in ("PNJ","VEA","HPG","TV1","OGC","HVN","TIS","PC1","TV2","DGC"):
    s = e60[e60.ticker==tk]
    if len(s):
        print(f"\n{tk}:")
        print(s[["t_s","t_b","dd_shock","speed","base_formed","base_reason","rating_group",
                 "fwd60_a","fwd60_b","fwd250_a","fwd250_b"]].to_string(index=False))
