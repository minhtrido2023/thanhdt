# -*- coding: utf-8 -*-
"""b_panel.py — panel THÁNG V2 (PRELOCK §0). Sửa lỗi skeptic 1–3:
 (1) một vintage giá: Close chỉ lấy từ bảng `ticker` (cache + px_pre2013_d.csv), không dùng Close của ticker_financial;
 (2) không gian TỔNG GIÁ TRỊ: vốn chủ E = totalAsset − nợ (không phụ thuộc cơ sở cổ phiếu), vốn hoá MC(rel) = Price × N,
     N chọn giữa {OShares, E/BVPS} theo tính liên tục với bước nhảy hệ số điều chỉnh giá;
 (3) thêm mã vắng BQ từ VNDirect (out/delisted) qua cổng thanh khoản tự dựng theo ruleset v1.
Không dùng profit_*, không dùng ticker_prune. Out: ../out/panel2.parquet, ../out/panel_build.json."""
import os, sys, json, glob
import numpy as np, pandas as pd, duckdb
WC = "/home/trido/thanhdt/WorkingClaude"; HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUT_DIR") or os.path.join(HERE, "..", "out")
sys.path.insert(0, WC)
c = duckdb.connect(); LOG = {}
NS = "datetime64[ns]"

# ============ 1. GIÁ ngày (một vintage) ============
px = c.execute(f"""SELECT ticker, CAST(time AS DATE) AS time, Close, Price, Volume, Trading_Value_1M_P50 AS tv
      FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet') WHERE Close > 0 AND ICB_Code IS NOT NULL""").df()
px["time"] = pd.to_datetime(px.time).astype(NS)
pre = pd.read_csv(os.path.join(OUT, "px_pre2013_d.csv"), parse_dates=["time"]); pre["time"] = pre.time.astype(NS)
ov = pre.merge(px[["ticker", "time", "Close"]], on=["ticker", "time"], suffixes=("_bq", "_cache"))
LOG["vintage_overlap_2013_01"] = {"n": int(len(ov)), "share_abs_dlog_gt_0.5pct": float((np.abs(np.log(ov.Close_bq / ov.Close_cache)) > 0.005).mean()) if len(ov) else None}
pre = pre[pre.time < px.time.min()].copy(); pre["tv"] = np.nan
px = pd.concat([pre[["ticker", "time", "Close", "Price", "Volume", "tv"]], px], ignore_index=True).sort_values(["ticker", "time"]).reset_index(drop=True)
px["src"] = "BQ"

# ---- mã vắng BQ (VNDirect) ----
def load_dead():
    rows = []
    for fp in sorted(glob.glob(os.path.join(OUT, "delisted", "px_*.csv"))):
        d = pd.read_csv(fp)
        if len(d) < 60 or "adClose" not in d.columns:
            continue
        d = d.sort_values("date"); d = d[(d.close > 0) & (d.adClose > 0)]
        d["time"] = pd.to_datetime(d.date).astype(NS)
        d["Close"] = d.adClose * 1000.0; d["Price"] = d.close * 1000.0; d["Volume"] = d.nmVolume.fillna(0)
        d["val"] = d.nmValue.fillna(0)
        rows.append(d[["code", "time", "Close", "Price", "Volume", "val", "floor"]].rename(columns={"code": "ticker"}))
    return pd.concat(rows, ignore_index=True)
dead = load_dead()
dead = dead[~dead.ticker.isin(set(px.ticker))].copy()
# cổng thanh khoản ruleset v1 (tự dựng): ngưỡng danh nghĩa = ngưỡng thực 2026 / 1,07^(số năm tới 2026-07)
def gate(g, valcol):
    yrs = (pd.Timestamp("2026-07-01") - g.time).dt.days.values / 365.25
    thr_in = 1.0e9 / 1.07 ** yrs; thr_out = 0.5e9 / 1.07 ** yrs
    v = g[valcol].values; med60 = pd.Series(v).rolling(60, min_periods=60).median().values
    max20 = pd.Series(v).rolling(20, min_periods=20).max().values
    cl = g.Price.values; gap = g.time.diff().dt.days.fillna(0).values
    inu = np.zeros(len(g), bool); cur = False
    for i in range(len(g)):
        if gap[i] > 20:                      # vắng ≥ ~10 phiên: loại cứng, phải đủ điều kiện lại
            cur = False
        if cur:
            if (max20[i] < thr_out[i]) or cl[i] < 1000 or v[i] <= 0 and (i >= 9 and (v[i - 9:i + 1] <= 0).all()):
                cur = False
        else:
            if i >= 60 and med60[i] >= thr_in[i] and cl[i] >= 1000:
                cur = True
        inu[i] = cur
    return inu
dead = dead.sort_values(["ticker", "time"]).reset_index(drop=True)
dead["in_universe"] = np.concatenate([gate(g, "val") for _, g in dead.groupby("ticker", sort=False)])
dead["tv"] = dead.groupby("ticker").val.transform(lambda s: s.rolling(20, min_periods=10).median())
dead["src"] = "VND"
LOG["dead"] = {"tickers_with_px": int(dead.ticker.nunique()), "tickers_ever_in_universe": int(dead[dead.in_universe].ticker.nunique()),
               "in_universe_rows_daily_2014plus": int((dead.in_universe & (dead.time >= "2014-01-01")).sum())}
# kiểm cổng tự dựng trên mã BQ: so với universe_pit thật tại phiên cuối tháng (mẫu 200 mã, seed)
uni = c.execute(f"SELECT ticker, CAST(time AS DATE) AS time FROM read_parquet('{WC}/data/bq_cache/universe_pit/*.parquet') WHERE in_universe").df()
uni["time"] = pd.to_datetime(uni.time).astype(NS); uni["in_universe"] = True
rng = np.random.RandomState(20261124); samp = rng.choice(sorted(px[px.time >= "2014-01-01"].ticker.unique()), 200, replace=False)
chk = px[px.ticker.isin(samp) & (px.time >= "2013-01-01")].copy(); chk["val"] = chk.Price.fillna(chk.Close) * chk.Volume.fillna(0)
chk = chk.sort_values(["ticker", "time"]).reset_index(drop=True)
chk["g"] = np.concatenate([gate(g, "val") for _, g in chk.groupby("ticker", sort=False)])
chk = chk.merge(uni, on=["ticker", "time"], how="left"); chk["in_universe"] = chk.in_universe.fillna(False).astype(bool)
chk = chk[chk.time >= "2014-01-01"]
LOG["gate_check_vs_universe_pit"] = {"n": int(len(chk)), "agree": float((chk.g == chk.in_universe).mean()),
    "recall_of_pit": float(chk[chk.in_universe].g.mean()), "precision_vs_pit": float(chk[chk.g].in_universe.mean())}
print("gate check", LOG["gate_check_vs_universe_pit"], LOG["dead"], flush=True)

# phiên giao dịch cuối cùng thật (Volume > 0) của từng mã
last_trade = pd.concat([px[px.Volume.fillna(0) > 0].groupby("ticker").time.max(), dead[dead.Volume > 0].groupby("ticker").time.max()])
allpx = pd.concat([px[["ticker", "time", "Close", "Price", "Volume", "tv", "src"]], dead[["ticker", "time", "Close", "Price", "Volume", "tv", "src", "in_universe"]]],
                  ignore_index=True)
allpx = allpx[allpx.time <= allpx.ticker.map(last_trade)].sort_values(["ticker", "time"]).reset_index(drop=True)   # bỏ đuôi giá treo không khớp lệnh
allpx["ym"] = allpx.time.dt.to_period("M")
GLAST = allpx.ym.max()
# [V3 NB-2] giá khớp T+1 từ DỮ LIỆU GIÁ ĐẦY ĐỦ (không phụ thuộc panel có BCTC): Close phiên đầu tháng, mỗi (mã, tháng); + phiên cuối của mã
_t1 = allpx.groupby(["ticker", "ym"]).Close.first().rename("c1").reset_index(); _t1["ym"] = _t1.ym.astype(str)
_t1.to_parquet(os.path.join(OUT, "px_t1.parquet"))
_lg = allpx.groupby("ticker").agg(last_ym=("ym", "max"), last_close=("Close", "last")).reset_index(); _lg["last_ym"] = _lg.last_ym.astype(str)
_lg.to_parquet(os.path.join(OUT, "px_last.parquet"))

# ============ 2. BCTC theo kỳ công bố — không gian tổng giá trị ============
fin = c.execute(f"""SELECT ticker, CAST(time AS DATE) AS time, quarter, Price AS price_fin, Close AS close_fin, BVPS, OShares,
   totalAsset_P0 AS ta, StLiab_P0 AS stl, LtLiab_P0 AS ltl, ROE_Trailing, NP_P0,NP_P1,NP_P2,NP_P3,NP_P4,NP_P5,NP_P6,NP_P7,
   Revenue_P0,Revenue_P1,Revenue_P2,Revenue_P3,Revenue_P4,Revenue_P5,Revenue_P6,Revenue_P7, GPM_P0, NPM_P0, EBITM_P0, ROA_P0,
   Cash_P0, StDebt_P0, LtDebt_P0, DY, CF_OA_P0,CF_OA_P1,CF_OA_P2,CF_OA_P3, CF_Invest_P0,CF_Invest_P1,CF_Invest_P2,CF_Invest_P3,
   CF_OA_3Y, CF_Invest_3Y, FSCORE, IntCov_P0, CashCycle_P0, ROIC5Y, Debt_Eq_P0, STLTDebt_Eq_P0, Inventory_P0, AR_P0
   FROM read_parquet('{WC}/data/bq_cache/ticker_financial.parquet') WHERE BVPS IS NOT NULL AND OShares > 0""").df()
fin["time"] = pd.to_datetime(fin.time).astype(NS)
fin = fin.sort_values(["ticker", "time"]).drop_duplicates(["ticker", "time"], keep="last").reset_index(drop=True)
# giá tại ngày công bố từ bảng ticker (một vintage); Price thô thiếu ⇒ Price thô của fin (giá thô không phụ thuộc vintage)
pk = allpx[allpx.src == "BQ"][["ticker", "time", "Close", "Price"]].rename(columns={"Close": "close_rel", "Price": "price_tk", "time": "ptime"}).sort_values("ptime")
fin = pd.merge_asof(fin.sort_values("time"), pk, left_on="time", right_on="ptime", by="ticker", direction="backward", tolerance=pd.Timedelta(days=7))
fin["price_rel"] = fin.price_tk.fillna(fin.price_fin)
fin = fin[fin.close_rel.notna() & (fin.price_rel > 0)].sort_values(["ticker", "time"]).reset_index(drop=True)
e2 = fin.ta - fin.stl.fillna(0) - fin.ltl.fillna(0); has_liab = (fin.stl.fillna(0) + fin.ltl.fillna(0)) > 0
e1 = fin.BVPS * fin.OShares
fin["E"] = np.where(has_liab & (e2.notna()), e2, e1); fin["E_src"] = np.where(has_liab & e2.notna(), "TA-L", "BVPSxOS")
fin["N_b"] = np.where((fin.BVPS > 0) & (fin.E > 0), fin.E / fin.BVPS, np.nan)

def pick_n(g):
    a = g.OShares.values.astype(float); b = g.N_b.values; pf = np.log(g.price_rel.values / g.close_rel.values)
    n = np.empty(len(g)); how = np.empty(len(g), object); n[0] = a[0]; how[0] = "OS"
    for i in range(1, len(g)):
        if not np.isfinite(b[i]) or abs(np.log(a[i] / b[i])) < 0.05:
            n[i] = a[i]; how[i] = "OS"; continue
        pred = np.log(n[i - 1]) - (pf[i] - pf[i - 1])
        if abs(np.log(b[i]) - pred) < abs(np.log(a[i]) - pred):
            n[i] = b[i]; how[i] = "E/BVPS"
        else:
            n[i] = a[i]; how[i] = "OS*"
    g = g.copy(); g["N"] = n; g["N_how"] = how
    return g
fin = pd.concat([pick_n(g) for _, g in fin.groupby("ticker", sort=False)], ignore_index=True)
fin["MC_rel"] = fin.price_rel * fin.N
fin["src"] = "BQ"
# --- đo ảnh hưởng lỗi 1 và 2 (so với cách vòng 1: B_adj = BVPS × Close_fin / Price_fin) ---
ok = (fin.BVPS > 0) & (fin.E > 0) & (fin.close_fin > 0) & (fin.price_fin > 0)
d1 = np.log(fin.close_rel / fin.close_fin)[ok]                                   # lệch vintage Close
bp_old = (fin.BVPS / fin.price_fin)[ok]; bp_new = (fin.E / fin.MC_rel)[ok]
d2 = np.log(bp_new / bp_old)
LOG["fix1_vintage"] = {"n": int(ok.sum()), "share_abs_gt_2pct": float((d1.abs() > 0.02).mean()), "tickers_gt_2pct": int(fin[ok][d1.abs() > 0.02].ticker.nunique()),
                       "p50_abs": float(d1.abs().median()), "p95_abs": float(d1.abs().quantile(.95))}
LOG["fix2_basis"] = {"n": int(ok.sum()), "rows_N_from_E_over_BVPS": int((fin.N_how == "E/BVPS").sum()), "rows_OS_kept_despite_mismatch": int((fin.N_how == "OS*").sum()),
                     "share_abs_dlogBP_gt_15pct": float((d2.abs() > 0.15).mean()), "rows_abs_dlogBP_gt_15pct": int((d2.abs() > 0.15).sum()),
                     "E_src_counts": fin.E_src.value_counts().to_dict()}
h = fin[(fin.ticker == "HPG") & (fin.time >= "2018-10-01") & (fin.time <= "2019-11-01")]
LOG["fix2_HPG"] = [{"time": str(r.time.date()), "q": r.quarter, "BVPS/Price_cu": round(r.BVPS / r.price_fin, 4), "E/MC_moi": round(r.E / r.MC_rel, 4), "N_how": r.N_how,
                    "N_trieu": round(r.N / 1e6, 1), "OShares_trieu": round(r.OShares / 1e6, 1)} for r in h.itertuples()]
print(json.dumps({k: LOG[k] for k in ("fix1_vintage", "fix2_basis", "fix2_HPG")}, ensure_ascii=False), flush=True)

def ssum(df, cols):
    return df[cols].sum(axis=1, min_count=len(cols))
fin["np_ttm"] = ssum(fin, [f"NP_P{i}" for i in range(4)]); fin["np_prev"] = ssum(fin, [f"NP_P{i}" for i in range(4, 8)])
fin["rev_ttm"] = ssum(fin, [f"Revenue_P{i}" for i in range(4)]); fin["rev_prev"] = ssum(fin, [f"Revenue_P{i}" for i in range(4, 8)])
fin["cfo_ttm"] = ssum(fin, [f"CF_OA_P{i}" for i in range(4)]); fin["capex_ttm"] = -ssum(fin, [f"CF_Invest_P{i}" for i in range(4)])
fin["debt"] = fin.StDebt_P0.fillna(0) + fin.LtDebt_P0.fillna(0); fin["cash"] = fin.Cash_P0
fin["ebit_ttm"] = fin.EBITM_P0 * fin.rev_ttm
fin["div_ttm"] = fin.DY.fillna(0) * fin.MC_rel
fin["roe"] = fin.ROE_Trailing
fin = fin.rename(columns={"GPM_P0": "gpm", "ROA_P0": "roa", "FSCORE": "fscore", "IntCov_P0": "intcov", "CashCycle_P0": "cashcycle", "ROIC5Y": "roic5",
                          "Debt_Eq_P0": "debt_eq", "CF_OA_3Y": "cfo3y", "CF_Invest_3Y": "cfi3y"})
fin["known"] = fin.time

# ---- BCTC mã vắng BQ (VNDirect): 14000 vốn chủ, 14110 vốn góp, 23000 LNST mẹ, 21001 DT thuần ----
def load_dead_fs():
    out = []
    for fp in sorted(glob.glob(os.path.join(OUT, "delisted", "fs_*.csv"))):
        d = pd.read_csv(fp)
        if len(d) == 0 or "numericValue" not in d.columns:
            continue
        w = d.pivot_table(index=["code", "fiscalDate"], columns="itemCode", values="numericValue", aggfunc="last").reset_index()
        w.columns = [str(int(x)) if isinstance(x, float) else str(x) for x in w.columns]
        out.append(w)
    w = pd.concat(out, ignore_index=True).rename(columns={"code": "ticker"})
    w["fq"] = pd.to_datetime(w.fiscalDate).astype(NS)
    for k in ("14000", "14110", "23000", "21001", "12700", "13000", "11100", "13120", "13340", "23800", "23100"):
        if k not in w.columns:
            w[k] = np.nan
    w = w.sort_values(["ticker", "fq"]).reset_index(drop=True)
    KD_Q = int(os.environ.get("KD_Q", 45)); KD_Y = int(os.environ.get("KD_Y", 90))   # [V3.1 mục 7] độ nhạy ngày công bố nhánh VNDirect
    w["known"] = w.fq + pd.to_timedelta(np.where(w.fq.dt.month == 12, KD_Y, KD_Q), unit="D")
    w["E"] = w["14000"]; w["N"] = w["14110"] / 10000.0
    g = w.groupby("ticker")
    w["np_ttm"] = g["23000"].transform(lambda s: s.rolling(4, min_periods=4).sum()); w["np_prev"] = g.np_ttm.shift(4)
    w["rev_ttm"] = g["21001"].transform(lambda s: s.rolling(4, min_periods=4).sum()); w["rev_prev"] = g.rev_ttm.shift(4)
    e_lag = g.E.shift(4); w["roe"] = w.np_ttm / ((w.E + e_lag) / 2).where(lambda x: x > 0)
    w["debt"] = w["13120"].fillna(0) + w["13340"].fillna(0); w["cash"] = w["11100"]
    w["ebit_ttm"] = np.nan; w["gpm"] = g["23100"].transform(lambda s: s.rolling(4, min_periods=4).sum()) / w.rev_ttm
    w["roa"] = w.np_ttm / w["12700"]; w["debt_eq"] = w["13000"] / w.E.where(w.E > 0)
    for k in ("cfo_ttm", "capex_ttm", "div_ttm", "fscore", "intcov", "cashcycle", "roic5", "cfo3y", "cfi3y", "BVPS", "OShares"):
        w[k] = np.nan
    w["quarter"] = w.fq.dt.year.astype(str) + "Q" + w.fq.dt.quarter.astype(str); w["src"] = "VND"; w["E_src"] = "VND"; w["N_how"] = "VND"
    return w[(w.E.notna()) & (w.N > 0)]
dfs = load_dead_fs(); dfs = dfs[dfs.ticker.isin(set(dead.ticker))]
dk = dead[["ticker", "time", "Close", "Price"]].rename(columns={"Close": "close_rel", "Price": "price_rel", "time": "ptime"}).sort_values("ptime")
dfs = pd.merge_asof(dfs.sort_values("known"), dk, left_on="known", right_on="ptime", by="ticker", direction="backward", tolerance=pd.Timedelta(days=30))
dfs = dfs[dfs.close_rel.notna()].copy()
# [V3 NB-1] số CP tại NGÀY CÔNG BỐ: vốn góp cuối quý × hệ số sự kiện (bonus/chia tách/quyền) xảy ra trong (cuối quý, ngày công bố], suy từ bước nhảy
# log(Price/Close) giữa hai ngày (cùng nguyên lý pick_n của nhánh BQ). VND_N_OLD=1 ⇒ cách V2 (N = vốn góp cuối quý, không hiệu chỉnh).
dk2 = dk.rename(columns={"close_rel": "close_fq", "price_rel": "price_fq", "ptime": "ptime_fq"}).sort_values("ptime_fq")
dfs = pd.merge_asof(dfs.sort_values("fq"), dk2, left_on="fq", right_on="ptime_fq", by="ticker", direction="backward", tolerance=pd.Timedelta(days=10))
dfs = dfs.sort_values(["ticker", "known"]).reset_index(drop=True)
dfs["N_v2"] = dfs.N
dfs["pf"] = np.log(dfs.price_rel / dfs.close_rel); dfs["pf_fq"] = np.log(dfs.price_fq / dfs.close_fq)
# [V3.1 mục 1] hệ số giá Close/Price gộp CẢ cổ tức tiền lẫn sự kiện cổ phiếu ⇒ chỉ áp bước khi kỳ BCTC kế tiếp xác nhận số CP đổi theo đúng hướng/độ lớn đó
# (cùng nguyên lý pick_n: bước tốt hơn "không bước" khi dự đoán log(N_kế/N)). Thiếu kỳ kế ⇒ KHÔNG áp (bảo thủ, đếm trong LOG).
dfs["N_nxt"] = dfs.groupby("ticker").N_v2.shift(-1)
_stp = (dfs.pf_fq - dfs.pf); _s = np.log(dfs.N_nxt / dfs.N_v2)
_ok = dfs.pf_fq.notna() & _s.notna() & (_stp.abs() > 0.003) & ((_s - _stp).abs() < _s.abs())
if os.environ.get("MC_OLD") == "1":
    _ok = dfs.pf_fq.notna()
dfs["N_v3"] = np.where(_ok, dfs.N_v2 * np.exp(_stp), dfs.N_v2)
LOG["vnd_n_fix31"] = {"rows": int(len(dfs)), "step_applied": int(_ok.sum()), "step_candidate_|pf_fq-pf|>0.3%": int((dfs.pf_fq.notna() & (_stp.abs() > 0.003)).sum()),
                      "no_next_quarter": int(dfs.N_nxt.isna().sum())}
def jump_rate(d, ncol, howcol=None):
    """tỉ lệ dòng có nhảy vốn hoá > 15% sau khi điều chỉnh bước nhảy hệ số giá: (N_i/N_{i-1}) × exp(pf_i − pf_{i-1})."""
    d = d.sort_values(["ticker", "known"]).copy(); g = d.groupby("ticker")
    d["jmp"] = np.log(d[ncol] / g[ncol].shift(1)) + (d.pf - g.pf.shift(1)); ok = d.jmp.notna()
    out = {"n": int(ok.sum()), "share_gt15": float((d.jmp[ok].abs() > np.log(1.15)).mean())}
    if howcol:
        out["by_how"] = {k: [int(len(x)), float((x.abs() > np.log(1.15)).mean())] for k, x in ((k, d.jmp[ok & (d[howcol] == k)]) for k in sorted(d[howcol][ok].unique()))}
    return out
bq_j = fin.assign(known=fin.known, pf=np.log(fin.price_rel / fin.close_rel))
LOG["jump_VND"] = {"v2_N_vongop_cuoi_quy": jump_rate(dfs, "N_v2"), "v3_hieu_chinh_su_kien": jump_rate(dfs, "N_v3"),
                   "rows_changed_gt5pct": int((np.abs(np.log(dfs.N_v3 / dfs.N_v2)) > 0.05).sum()), "rows": int(len(dfs))}
LOG["jump_BQ"] = jump_rate(bq_j, "N", "N_how")
LOG["jump_BQ_OShares_only"] = jump_rate(bq_j, "OShares")
print("jump", json.dumps(LOG["jump_VND"], ensure_ascii=False), json.dumps(LOG["jump_BQ"], ensure_ascii=False), flush=True)
dfs["N"] = dfs.N_v2 if os.environ.get("VND_N_OLD") == "1" else dfs.N_v3
dfs["MC_rel"] = dfs.price_rel * dfs.N; dfs["time"] = dfs.known
dfs["price_rel"] = dfs.price_rel
KEEP = ["ticker", "known", "price_rel", "quarter", "src", "E", "N", "MC_rel", "close_rel", "roe", "np_ttm", "np_prev", "rev_ttm", "rev_prev", "cfo_ttm", "capex_ttm", "debt", "cash",
        "ebit_ttm", "div_ttm", "gpm", "roa", "fscore", "intcov", "cashcycle", "roic5", "debt_eq", "cfo3y", "cfi3y", "E_src", "N_how", "BVPS", "OShares"]
F = pd.concat([fin[KEEP], dfs[KEEP]], ignore_index=True).sort_values(["ticker", "known"]).reset_index(drop=True)
F = F[F.E.notna() & (F.MC_rel > 0)].copy()
F["N_next"] = F.groupby("ticker").N.shift(-1)
F["roe"] = F.roe.clip(-0.5, 0.6); F["npm"] = (F.np_ttm / F.rev_ttm.where(F.rev_ttm > 0)).clip(-0.5, 0.6)
F["payout_raw"] = np.where(F.np_ttm > 0, (F.div_ttm / F.np_ttm).clip(0, 1), np.nan)
F["revg"] = (F.rev_ttm / F.rev_prev.where(F.rev_prev > 0) - 1).clip(-0.6, 1.5); F["npg"] = np.where((F.np_prev > 0) & (F.np_ttm > 0), (F.np_ttm / F.np_prev - 1), np.nan)
F["npg"] = pd.Series(F.npg).clip(-0.9, 3.0).values

def roll_stats(g):
    g = g.copy(); t = g.known.values; roe = g.roe.values; npm = g.npm.values; po = g.payout_raw.values; dv = (g.div_ttm.fillna(0).values > 0)
    E = g.E.values; n = len(g)
    o = {k: np.full(n, np.nan) for k in ("roe_tc5", "n_tc5", "roe_sd5", "roe_min5", "npm_med5", "payout", "div_cnt20", "E_1y", "E_3y", "np3y", "jump_k")}
    k = 0
    for i in range(n):
        m5 = (t <= t[i]) & (t > t[i] - np.timedelta64(1826, "D")); m3 = (t <= t[i]) & (t > t[i] - np.timedelta64(1096, "D"))
        r5 = roe[m5]; r5 = r5[~np.isnan(r5)]
        if len(r5):
            o["roe_tc5"][i] = np.median(r5); o["n_tc5"][i] = len(r5); o["roe_min5"][i] = r5.min(); o["roe_sd5"][i] = r5.std() if len(r5) >= 4 else np.nan
        x = npm[m5]; x = x[~np.isnan(x)]; o["npm_med5"][i] = np.median(x) if len(x) >= 4 else np.nan
        x = po[m3]; x = x[~np.isnan(x)]; o["payout"][i] = np.median(x) if len(x) else np.nan
        o["div_cnt20"][i] = dv[max(0, i - 19):i + 1].sum() if i >= 19 else np.nan
        j = np.searchsorted(t, t[i] - np.timedelta64(330, "D"), side="right") - 1
        o["E_1y"][i] = E[j] if j >= 0 and (t[i] - t[j]) < np.timedelta64(460, "D") else np.nan
        j3 = np.searchsorted(t, t[i] - np.timedelta64(1060, "D"), side="right") - 1
        o["E_3y"][i] = E[j3] if j3 >= 0 and (t[i] - t[j3]) < np.timedelta64(1250, "D") else np.nan
        # cờ ROE đang nhảy (PRELOCK §1.4)
        flag = (np.isfinite(o["roe_tc5"][i]) and np.isfinite(roe[i]) and roe[i] - o["roe_tc5"][i] >= 0.10 and np.isfinite(g.revg.values[i]) and g.revg.values[i] >= 0.15
                and np.isfinite(npm[i]) and np.isfinite(o["npm_med5"][i]) and npm[i] > o["npm_med5"][i] and np.isfinite(o["E_1y"][i]) and E[i] >= o["E_1y"][i])
        k = k + 1 if flag else 0; o["jump_k"][i] = k
    for kk, v in o.items():
        g[kk] = v
    return g
F = pd.concat([roll_stats(g) for _, g in F.groupby("ticker", sort=False)], ignore_index=True)
print("fin rows", len(F), F.src.value_counts().to_dict(), "jump rows k>=2:", int((F.jump_k >= 2).sum()), flush=True)

# ============ 3. lưới tháng ============
me = allpx.groupby(["ticker", "ym"]).tail(1).copy()
fn = allpx.groupby(["ticker", "ym"]).head(1)[["ticker", "ym", "time", "Close"]].rename(columns={"time": "t1_time", "Close": "t1_close"}); fn["ym"] = fn.ym - 1
me = me.merge(fn, on=["ticker", "ym"], how="left")
me = me[me.ym >= pd.Period("2008-01")].sort_values(["time", "ticker"]).reset_index(drop=True)
pan = pd.merge_asof(me, F.sort_values("known"), left_on="time", right_on="known", by="ticker", direction="backward", suffixes=("", "_f"))
pan = pan[pan.known.notna() & ((pan.time - pan.known).dt.days <= 200)].copy()
assert (pan.known <= pan.time).all(), "PIT violation"
pan["mc_old"] = pan.MC_rel * pan.Close / pan.close_rel          # V3: Close đã điều chỉnh cổ tức tiền ⇒ mc phồng đúng bằng tỉ suất cổ tức (skeptic đòn 8)
# [V3.1 mục 1] mc = Price_thô(d) × N(d); N chỉ bước theo sự kiện CỔ PHIẾU: có sự kiện (hệ số Close/Price đổi so với ngày công bố) VÀ kỳ BCTC kế xác nhận N đổi (>1%)
# ⇒ N = N_kế (số CP sau sự kiện); ngược lại N = N tại ngày công bố (cổ tức tiền không đổi số CP). Giá thô thiếu ⇒ rơi về mc_old (đếm trong LOG).
_lr_now = np.log(pan.Close / pan.Price); _lr_k = np.log(pan.close_rel / pan.price_rel)
_sevent = ((_lr_now - _lr_k).abs() > 0.003)
_nn = pan.N_next.where(pan.N_next.notna() & (np.log(pan.N_next / pan.N).abs() > 0.01))
_N = np.where(_sevent & _nn.notna(), _nn, pan.N)
_mc_new = pan.Price * _N
pan["mc"] = np.where(np.isfinite(_mc_new) & (pan.Price > 0), _mc_new, pan.mc_old)
if os.environ.get("MC_OLD") == "1":
    pan["mc"] = pan.mc_old
pan = pan.merge(uni[["ticker", "time"]].assign(iu_bq=True), on=["ticker", "time"], how="left")
pan["in_universe"] = np.where(pan.src == "BQ", pan.iu_bq.fillna(False), pan.in_universe.fillna(False)).astype(bool); pan = pan.drop(columns=["iu_bq", "src_f"], errors="ignore")
LOG["mc_fix31"] = {"rows": int(len(pan)), "price_missing_fallback": int((~np.isfinite(_mc_new.values) | ~(pan.Price.values > 0)).sum()), "rows_event_since_filing": int(_sevent.sum()),
                   "rows_stock_step_applied": int((_sevent & _nn.notna()).sum()), "rows_event_no_next_confirm": int((_sevent & _nn.isna()).sum()),
                   "p50_abs_dlog_mc_new_vs_old_in_univ": float(np.log(pan.mc / pan.mc_old).abs()[pan.in_universe].median()),
                   "share_abs_dlog_gt_0.2pct_in_univ": float((np.log(pan.mc / pan.mc_old).abs() > 0.002)[pan.in_universe].mean()),
                   "share_abs_dlog_gt_10pct_in_univ": float((np.log(pan.mc / pan.mc_old).abs() > 0.10)[pan.in_universe].mean())}
_v = pan[(pan.ticker == "VNM") & (pan.ym.between(pd.Period("2019-04"), pd.Period("2019-08")))]
LOG["mc_fix31_VNM_2019"] = [{"ym": str(r.ym), "mc_old_tyVND": round(r.mc_old / 1e9), "mc_new_tyVND": round(r.mc / 1e9), "dlog": round(float(np.log(r.mc / r.mc_old)), 4)} for r in _v.itertuples()]
rat = c.execute(f"SELECT ticker, CAST(time AS DATE) AS time, route, rating FROM read_parquet('{WC}/data/bq_cache/fa_ratings_8l.parquet')").df()
rat["time"] = pd.to_datetime(rat.time).astype(NS); rat = rat.sort_values("time"); route = rat.groupby("ticker").route.last()
pan["route"] = pan.ticker.map(route).fillna("COMPOUNDER")
pan = pd.merge_asof(pan.sort_values("time"), rat[["ticker", "time", "rating"]].rename(columns={"time": "rat_time"}), left_on="time", right_on="rat_time", by="ticker", direction="backward")
rr = c.execute(f"SELECT DISTINCT quarter, ticker, Risk_Rating AS risk_rating, Beta AS beta FROM read_parquet('{WC}/data/bq_cache/risk_rating.parquet')").df().drop_duplicates(["quarter", "ticker"])
pan = pan.merge(rr, on=["quarter", "ticker"], how="left")
st = pd.read_parquet(f"{WC}/data/bq_cache/vnindex_5state_dt5g_live.parquet")[["time", "state"]]; st["time"] = pd.to_datetime(st.time).astype(NS)
pan = pd.merge_asof(pan.sort_values("time"), st.sort_values("time").rename(columns={"state": "dt5g"}), on="time", direction="backward")

# ============ 4. nhãn: lợi suất tương lai, có xử lý mã ngừng giao dịch ============
pan = pan.sort_values(["ticker", "ym"]).reset_index(drop=True)
cl = allpx.groupby(["ticker", "ym"]).Close.last()                      # dùng mọi tháng có giá (kể cả tháng thiếu BCTC)
lastym = allpx.groupby("ticker").ym.max(); lastcl = allpx.groupby("ticker").Close.last()
pan["last_ym"] = pan.ticker.map(lastym); pan["last_close"] = pan.ticker.map(lastcl)
for N in (12, 24, 36):
    tgt = pan.ym + N
    f = np.log(cl.reindex(pd.MultiIndex.from_arrays([pan.ticker, tgt])).values / pan.Close.values)
    ended = np.isnan(f) & (tgt <= GLAST).values & (pan.last_ym < tgt).values         # mã đã ngừng giao dịch trước mốc
    pan[f"fwd{N}_raw"] = f; pan[f"ended{N}"] = ended
    base = np.log(pan.last_close.values / pan.Close.values)
    for H, tag in ((0.0, "h0"), (0.5, "h50"), (0.99, "h100")):
        pan[f"fwd{N}_{tag}"] = np.where(ended, base + np.log(1 - H), f)
pan["ym"] = pan.ym.astype(str); pan["last_ym"] = pan.last_ym.astype(str)
pan.to_parquet(os.path.join(OUT, "panel2.parquet"))
u = pan[pan.in_universe & (pan.ym >= "2014-01")]
LOG["panel"] = {"rows": int(len(pan)), "tickers": int(pan.ticker.nunique()), "in_universe_rows_2014plus": int(len(u)), "by_src": u.src.value_counts().to_dict(),
                "tickers_in_universe_by_src": u.groupby("src").ticker.nunique().to_dict(),
                "ended36_rows_in_universe_asof<=2023-10": u[u.ym <= "2023-10"].groupby("src").ended36.sum().astype(int).to_dict(),
                "rows_in_universe_asof<=2023-10": u[u.ym <= "2023-10"].groupby("src").size().to_dict()}
chk9 = sorted(set(u.ticker) & {"FLC", "ROS", "HVG", "KSA", "AMD", "HAI", "ART", "GTN", "TGG"}); LOG["dead_named_in_universe"] = chk9
json.dump(LOG, open(os.path.join(OUT, "panel_build.json"), "w"), ensure_ascii=False, indent=1, default=str)
print(json.dumps({k: LOG[k] for k in ("vintage_overlap_2013_01", "panel", "dead_named_in_universe")}, ensure_ascii=False, default=str))
