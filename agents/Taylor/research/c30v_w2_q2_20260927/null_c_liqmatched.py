#!/usr/bin/env python3
"""NULL-300 cho C, POOL KHỚP THANH KHOẢN — job Taylor_20260927_141318.

Vì sao có file này (và vì sao `null_c.py` một mình là KHÔNG ĐỦ): `null_c.py` rút k tên từ TOÀN BỘ
tập đủ điều kiện của quý (`in_universe` ∧ `pass_golden_floor` ∧ `rating_8l≤3` ∧ `!banned`, trung vị
**137 tên**). Nhưng engine KHÔNG chọn từ 137 tên đó — `custom_basket.py:1397-1398` cho
`SELECT_MODE in _V3_MODES` (gồm `v3route3`) lấy `pool = gated[:CFO_POOL]` với
`CFO_POOL = BASKET_CFO_POOL = 60` (dòng 700), tức **60 tên THANH KHOẢN NHẤT** trong số đã qua cổng,
xếp theo thanh khoản QUÝ TRƯỚC (dòng 1263-1266).

Hệ quả: null 137-tên tặng không cho C một phần bù thanh khoản mà null không có — cái đuôi kém thanh
khoản chính là thứ sinh ra MaxDD trung vị −41% và CAGR 6% của null đó. So C với nó là so lệch luật.
PREREG §4 nói "CÙNG pool"; pool THẬT của engine là `gated[:60]`, nên bản này mới là bản THI HÀNH
prereg, không phải bản sửa prereg.

Thanh khoản dựng lại đúng công thức engine (`custom_basket.py:622-628`): AVG(Volume_3M_P50 × giá
RAW COALESCE(Price,Close)) theo ticker×quý, HAVING nd≥20, dùng quý TRƯỚC (PIT).
"""
import glob, io, json, os, sys
import numpy as np, pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
CACHE = f"{WC}/data/bq_cache_asof20260729_postrestate"
LOGS = f"{WC}/mike/agents/Taylor/research/c30v_w2_q2_20260927/logs"
R_DRAW, SEED, CFO_POOL = 300, 20260927, 60

def ledger_of(tag):
    txt = io.open(f"{LOGS}/{tag}.log", encoding="utf-8", errors="replace").read()
    assert f"EXIT=0 ({tag}" in txt, f"{tag}: leg did not exit 0"
    hits = [l.split("->", 1)[1].split("(")[0].strip() for l in txt.splitlines()
            if l.strip().startswith("-> ") and l.strip().endswith("rows)")]
    assert len(hits) == 1, (tag, hits)
    return hits[0]

up = pd.concat([pd.read_parquet(f) for f in sorted(glob.glob(f"{CACHE}/universe_pit_q/*.parquet"))])
up["time"] = pd.to_datetime(up["time"])
elig = up[(up["in_universe"] == True) & (up["pass_golden_floor"] == True)
          & (up["banned"] != True) & (up["rating_8l"] <= 3)]
pool_all = {d: sorted(g["ticker"].unique()) for d, g in elig.groupby("time")}

px = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "Close", "Price", "Volume_3M_P50"])
                for f in sorted(glob.glob(f"{CACHE}/ticker/*.parquet"))])
px["time"] = pd.to_datetime(px["time"])
WIDE = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="last").sort_index()
print(f"price panel {WIDE.shape[0]}d x {WIDE.shape[1]} tickers  {WIDE.index[0].date()}..{WIDE.index[-1].date()}")

# --- thanh khoan quy, DUNG cong thuc engine (raw price basis, nd>=20) ---
px["_pxw"] = px["Price"].where(px["Price"].notna(), px["Close"])
px["_q"] = px["time"].dt.to_period("Q").dt.start_time
px["_tv"] = px["Volume_3M_P50"] * px["_pxw"]
g = px.dropna(subset=["_tv"]).groupby(["ticker", "_q"])["_tv"].agg(["mean", "count"])
g = g[g["count"] >= 20]
LIQ = g["mean"].unstack("ticker")            # index=quy, cols=ticker
LIQ = LIQ.sort_index()
print(f"liq panel {LIQ.shape[0]} quy x {LIQ.shape[1]} ticker  {LIQ.index[0].date()}..{LIQ.index[-1].date()}")

def liq_pool(qsrc, names):
    """60 ten THANH KHOAN NHAT trong `names`, xep theo quy TRUOC qsrc (PIT, nhu engine)."""
    q = pd.Timestamp(qsrc).to_period("Q").start_time
    prior = [x for x in LIQ.index if x < q]
    src = max(prior) if prior else (q if q in LIQ.index else None)
    if src is None:
        return list(names), None
    row = LIQ.loc[src].dropna()
    ranked = [t for t in row.sort_values(ascending=False).index if t in set(names)]
    return ranked[:CFO_POOL], src

def calendar_and_segments(ledger):
    df = pd.read_csv(ledger, low_memory=False)
    d = df[df["record_type"] == "DAILY"]
    idx = pd.DatetimeIndex(pd.to_datetime(d["ymd"]).dt.normalize().drop_duplicates().sort_values())
    cm = df[df["record_type"] == "CUSTOM_MEMBERS"].copy()
    cm["eff"] = pd.to_datetime(cm["ymd"]).dt.normalize()
    cm["qsrc"] = cm["reason"].str.extract(r"quarter=(\d{4}-\d{2}-\d{2})")[0].pipe(pd.to_datetime)
    memb = {e: (sorted(g["ticker"].unique()), g["qsrc"].iloc[0]) for e, g in cm.groupby("eff")}
    effs = sorted(memb)
    segs = []
    for i, e in enumerate(effs):
        nxt = effs[i + 1] if i + 1 < len(effs) else idx[-1] + pd.Timedelta(days=1)
        m = (idx[1:] > e) & (idx[1:] <= nxt)
        if m.sum():
            segs.append((m, e, memb[e][0], memb[e][1]))
    return idx, segs

def ew_series(segs, RM, TIC, names_for):
    S = np.zeros(RM.shape[0])
    for seg in segs:
        rows = np.where(seg[0])[0]
        ci = [TIC[n] for n in names_for(seg) if n in TIC]
        if not ci: continue
        with np.errstate(invalid="ignore"):
            S[rows] = np.nan_to_num(np.nanmean(RM[np.ix_(rows, ci)], axis=1))
    return S

def stats(S, yrs):
    nav = np.cumprod(1 + S, axis=-1)
    peak = np.maximum.accumulate(nav, axis=-1)
    return nav[..., -1] ** (1 / yrs) - 1, (nav / peak - 1).min(axis=-1)

tag, k = sys.argv[1], int(sys.argv[2])
ledger = ledger_of(tag)
idx, segs = calendar_and_segments(ledger)
yrs = (idx[-1] - idx[0]).days / 365.25
RET = WIDE.reindex(idx).pct_change()
TIC = {t: i for i, t in enumerate(RET.columns)}
RM = RET.iloc[1:].to_numpy(dtype=float)
nmem = [len(s[2]) for s in segs]
assert max(nmem) <= k, f"{tag}: engine chon {max(nmem)} > k={k}"

S_C = ew_series(segs, RM, TIC, lambda s: s[2])
c_cagr, c_dd = stats(S_C, yrs)

rng = np.random.default_rng(SEED)
NS = np.zeros((R_DRAW, RM.shape[0]))
sizes_all, sizes_liq, inpool = [], [], []
for m, e, mem, qsrc in segs:
    full = [n for n in pool_all.get(qsrc, []) if n in TIC]
    cand, src = liq_pool(qsrc, full)
    sizes_all.append(len(full)); sizes_liq.append(len(cand))
    inpool.append(sum(1 for t in mem if t in set(cand)) / max(len(mem), 1))
    kk = min(k, len(mem), len(cand))
    if kk == 0: continue
    rows = np.where(m)[0]
    picks = np.array([rng.choice(len(cand), size=kk, replace=False) for _ in range(R_DRAW)])
    ci = np.array([TIC[c] for c in cand])
    X = RM[np.ix_(rows, ci[picks.ravel()])].reshape(len(rows), R_DRAW, kk)
    with np.errstate(invalid="ignore"):
        NS[:, rows] = np.nan_to_num(np.nanmean(X, axis=2)).T
n_cagr, n_dd = stats(NS, yrs)

pct_cagr = float((n_cagr < c_cagr).mean() * 100)
pct_dd = float((n_dd < c_dd).mean() * 100)
p90 = float(np.percentile(n_cagr, 90))
print(f"\n{tag}: k={k}  {len(segs)} doan giu, membership {min(nmem)}/{max(nmem)}")
print(f"  pool day du (nhu null_c.py):  min/med/max = {min(sizes_all)}/{int(np.median(sizes_all))}/{max(sizes_all)}")
print(f"  pool KHOP THANH KHOAN (top-{CFO_POOL}): min/med/max = {min(sizes_liq)}/{int(np.median(sizes_liq))}/{max(sizes_liq)}")
print(f"  ty le ten C NAM TRONG pool khop: min {min(inpool)*100:.0f}%  med {np.median(inpool)*100:.0f}%  max {max(inpool)*100:.0f}%")
print(f"  NULL-{R_DRAW} (pool khop thanh khoan):")
print(f"    CAGR  median {np.median(n_cagr)*100:6.2f}%  p90 {p90*100:6.2f}%  5th {np.percentile(n_cagr,5)*100:6.2f}%  max {n_cagr.max()*100:6.2f}%")
print(f"    MaxDD median {np.median(n_dd)*100:6.1f}%  p90 {np.percentile(n_dd,90)*100:6.1f}%  5th {np.percentile(n_dd,5)*100:6.1f}%")
print(f"  C: CAGR {c_cagr*100:.2f}%  MaxDD {c_dd*100:.1f}%  -> phan vi trong null: CAGR {pct_cagr:.1f}  MaxDD {pct_dd:.1f}")
v = "CO EDGE (vuot p90 CAGR)" if c_cagr > p90 else "KHONG vuot p90 => KHONG duoc goi la co edge"
print(f"  PREREG gate: {v}")
out = {tag: {"k": k, "ledger": ledger, "cfo_pool": CFO_POOL, "n_segments": len(segs), "yrs": round(yrs, 4),
             "pool_full_med": int(np.median(sizes_all)), "pool_liqmatched_med": int(np.median(sizes_liq)),
             "frac_C_names_in_liqpool_med": round(float(np.median(inpool)), 4),
             "frac_C_names_in_liqpool_min": round(float(min(inpool)), 4),
             "C_cagr_pct": round(float(c_cagr)*100, 3), "C_maxdd_pct": round(float(c_dd)*100, 2),
             "null_R": R_DRAW, "null_seed": SEED,
             "null_cagr_median_pct": round(float(np.median(n_cagr))*100, 3),
             "null_cagr_p90_pct": round(p90*100, 3),
             "null_cagr_5th_pct": round(float(np.percentile(n_cagr, 5))*100, 3),
             "null_cagr_max_pct": round(float(n_cagr.max())*100, 3),
             "null_dd_median_pct": round(float(np.median(n_dd))*100, 2),
             "null_dd_p90_pct": round(float(np.percentile(n_dd, 90))*100, 2),
             "null_dd_5th_pct": round(float(np.percentile(n_dd, 5))*100, 2),
             "C_percentile_in_null_cagr": round(pct_cagr, 1), "C_percentile_in_null_dd": round(pct_dd, 1),
             "prereg_gate": v}}
f = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"nullliq_{tag}.json")
json.dump(out, open(f, "w"), indent=1); print(f"-> {f}")
