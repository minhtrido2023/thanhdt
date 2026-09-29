#!/usr/bin/env python3
"""NULL-300 cho ung vien C — job Taylor_20260927_141318, khuon conc_tail.py (Job U).

Cau hoi: rổ tập trung k tên do `v3route3` CHỌN có hơn k tên RÚT NGẪU NHIÊN từ CÙNG pool không?

Thiết kế (điểm khác conc_tail.py, có chủ đích): chân C **không** được tính lại bằng một công thức
riêng. Nó dùng ĐÚNG membership engine đã chọn (đọc từ dòng `CUSTOM_MEMBERS` của ledger chân C) rồi
chạy qua **cùng một hàm** dựng chuỗi EW như 300 draw ngẫu nhiên. Nhờ vậy C và null khác nhau ĐÚNG
một thứ — TÊN NÀO được chọn — chứ không lẫn thêm khác biệt về giá, lịch, hay quy ước trọng số.
(conc_tail.py so chuỗi ngẫu nhiên với chuỗi engine dựng bằng đường khác; ở đây cả hai cùng đường.)

Cache = `bq_cache_asof20260729_postrestate` — ĐÚNG cache engine đọc, không phải `bq_cache` mặc định.
"""
import glob, io, json, os, sys
import numpy as np, pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
CACHE = f"{WC}/data/bq_cache_asof20260729_postrestate"
LOGS = f"{WC}/mike/agents/Taylor/research/c30v_w2_q2_20260927/logs"
R_DRAW, SEED = 300, 20260927

def ledger_of(tag):
    txt = io.open(f"{LOGS}/{tag}.log", encoding="utf-8", errors="replace").read()
    assert f"EXIT=0 ({tag}" in txt, f"{tag}: leg did not exit 0"
    hits = [l.split("->", 1)[1].split("(")[0].strip() for l in txt.splitlines()
            if l.strip().startswith("-> ") and l.strip().endswith("rows)")]
    assert len(hits) == 1, (tag, hits)
    return hits[0]

# ---- pool PIT theo quarter: dung DUNG bo loc ke hoach §3.1 / conc_tail.py ----
up = pd.concat([pd.read_parquet(f) for f in sorted(glob.glob(f"{CACHE}/universe_pit_q/*.parquet"))])
up["time"] = pd.to_datetime(up["time"])
elig = up[(up["in_universe"] == True) & (up["pass_golden_floor"] == True)
          & (up["banned"] != True) & (up["rating_8l"] <= 3)]
pool = {d: sorted(g["ticker"].unique()) for d, g in elig.groupby("time")}
print(f"pool: {len(pool)} quarter dates, size med={int(np.median([len(v) for v in pool.values()]))}")

px = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "Close"])
                for f in sorted(glob.glob(f"{CACHE}/ticker/*.parquet"))])
px["time"] = pd.to_datetime(px["time"])
WIDE = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="last").sort_index()
print(f"price panel {WIDE.shape[0]}d x {WIDE.shape[1]} tickers  {WIDE.index[0].date()}..{WIDE.index[-1].date()}")

def calendar_and_segments(ledger):
    """Lich giao dich + cac doan giu (tu dong CUSTOM_MEMBERS: ngay rebal quy engine that dung)."""
    df = pd.read_csv(ledger, low_memory=False)
    d = df[df["record_type"] == "DAILY"]
    idx = pd.to_datetime(d["ymd"]).dt.normalize().drop_duplicates().sort_values().reset_index(drop=True)
    idx = pd.DatetimeIndex(idx)
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
    """Chuoi return EW ghep theo doan. names_for(seg) -> list ten. Cung ham cho C va cho null."""
    S = np.zeros(RM.shape[0])
    for seg in segs:
        m = seg[0]; rows = np.where(m)[0]
        ci = [TIC[n] for n in names_for(seg) if n in TIC]
        if not ci: continue
        with np.errstate(invalid="ignore"):
            S[rows] = np.nan_to_num(np.nanmean(RM[np.ix_(rows, ci)], axis=1))
    return S

def stats(S, yrs):
    nav = np.cumprod(1 + S, axis=-1)
    peak = np.maximum.accumulate(nav, axis=-1)
    dd = (nav / peak - 1).min(axis=-1)
    return nav[..., -1] ** (1 / yrs) - 1, dd

out = {}
for tag, k in [(sys.argv[1], int(sys.argv[2]))]:
    ledger = ledger_of(tag)
    idx, segs = calendar_and_segments(ledger)
    yrs = (idx[-1] - idx[0]).days / 365.25
    RET = WIDE.reindex(idx).pct_change()
    TIC = {t: i for i, t in enumerate(RET.columns)}
    RM = RET.iloc[1:].to_numpy(dtype=float)
    nmem = [len(s[2]) for s in segs]
    print(f"\n{tag}: k={k}  {len(segs)} doan giu, {sum(int(s[0].sum()) for s in segs)}/{RM.shape[0]} "
          f"ngay return, membership size min/med/max = {min(nmem)}/{int(np.median(nmem))}/{max(nmem)}")
    assert max(nmem) <= k, f"{tag}: engine chon {max(nmem)} ten > k={k} — sai knob BASKET_TOPN"

    S_C = ew_series(segs, RM, TIC, lambda s: s[2])
    c_cagr, c_dd = stats(S_C, yrs)

    rng = np.random.default_rng(SEED)
    NS = np.zeros((R_DRAW, RM.shape[0]))
    for seg in segs:
        m, e, mem, qsrc = seg
        cand = [n for n in pool.get(qsrc, []) if n in TIC]
        kk = min(k, len(mem), len(cand))
        if kk == 0: continue
        rows = np.where(m)[0]
        picks = np.array([rng.choice(len(cand), size=kk, replace=False) for _ in range(R_DRAW)])
        ci = np.array([TIC[cand[j]] for j in range(len(cand))])
        X = RM[np.ix_(rows, ci[picks.ravel()])].reshape(len(rows), R_DRAW, kk)
        with np.errstate(invalid="ignore"):
            NS[:, rows] = np.nan_to_num(np.nanmean(X, axis=2)).T
    n_cagr, n_dd = stats(NS, yrs)

    pct_cagr = float((n_cagr < c_cagr).mean() * 100)
    pct_dd = float((n_dd < c_dd).mean() * 100)   # dd am: cao hon = it tail hon
    print(f"  NULL-{R_DRAW} standalone EW (cung pool, cung doan, cung ham):")
    print(f"    CAGR  median {np.median(n_cagr)*100:6.2f}%  p90 {np.percentile(n_cagr,90)*100:6.2f}%  "
          f"5th {np.percentile(n_cagr,5)*100:6.2f}%")
    print(f"    MaxDD median {np.median(n_dd)*100:6.1f}%  p90 {np.percentile(n_dd,90)*100:6.1f}%  "
          f"5th {np.percentile(n_dd,5)*100:6.1f}%")
    print(f"  C ({tag}): CAGR {c_cagr*100:.2f}%  MaxDD {c_dd*100:.1f}%  "
          f"-> phan vi trong null: CAGR {pct_cagr:.1f}  MaxDD {pct_dd:.1f}")
    verdict = "CO EDGE (vuot p90 CAGR)" if c_cagr > np.percentile(n_cagr, 90) else "KHONG vuot p90 => KHONG duoc goi la co edge"
    print(f"  PREREG gate: {verdict}")
    out[tag] = {"k": k, "ledger": ledger, "n_segments": len(segs), "yrs": round(yrs, 4),
                "membership_size_min_med_max": [min(nmem), int(np.median(nmem)), max(nmem)],
                "C_cagr_pct": round(float(c_cagr)*100, 3), "C_maxdd_pct": round(float(c_dd)*100, 2),
                "null_R": R_DRAW, "null_seed": SEED,
                "null_cagr_median_pct": round(float(np.median(n_cagr))*100, 3),
                "null_cagr_p90_pct": round(float(np.percentile(n_cagr, 90))*100, 3),
                "null_cagr_5th_pct": round(float(np.percentile(n_cagr, 5))*100, 3),
                "null_dd_median_pct": round(float(np.median(n_dd))*100, 2),
                "null_dd_p90_pct": round(float(np.percentile(n_dd, 90))*100, 2),
                "null_dd_5th_pct": round(float(np.percentile(n_dd, 5))*100, 2),
                "C_percentile_in_null_cagr": round(pct_cagr, 1),
                "C_percentile_in_null_dd": round(pct_dd, 1),
                "prereg_gate": verdict}
HERE = os.path.dirname(os.path.abspath(__file__))
f = os.path.join(HERE, f"null_{sys.argv[1]}.json")
json.dump(out, open(f, "w"), indent=1); print(f"-> {f}")
