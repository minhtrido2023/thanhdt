# -*- coding: utf-8 -*-
"""lvens2_pit2.py (job Taylor_20261125_160331) = lvens2_incremental.py (md5 357f69c5…, master 4a5cba411) + sửa theo quant-skeptic REFUTED:
  (1) mc `stepca`/`stepcar`: bước số CP chỉ theo sự kiện ĐỔI SỐ CP trong corporate_action (extract đóng băng out/ca/, md5 kiểm fail-closed), không bao giờ cổ tức tiền.
  (2) E của dòng BVPS×OShares (ngân hàng…): BVPS đã ghi theo cơ sở CP sau sự kiện (rò vintage) — khi E tụt >7%/kỳ VÀ được giải thích bởi sự kiện CA đổi số CP
      công bố ≤ D ⇒ E = E_raw × Π(1+r); tụt không giải thích được ⇒ giữ E_raw, gắn cờ E_unexpl (xem e_guard).
  (3) poison tách khỏi cut: poison áp cho MỌI nguồn lúc nạp; --mutate-nocut <nguồn> bỏ cắt 1 nguồn (mutation test); --cache-root cho selfcheck vintage.
  (4) freshness fail-closed: manifest cache phải phủ D (ticker) và ticker_financial/fa_ratings_8l max_time ≥ D − FRESH_DAYS.
Phần dưới là docstring gốc (vẫn đúng cho phần không đổi).
lvens2_incremental.py — dựng lv_ENS2 (tâm nội tại ENS2, mù giá) + route cho MỘT as-of tháng, chỉ dùng dữ liệu ≤ ngày as-of (PIT).
Phục vụ sổ paper `dcf_vn_behavioral_20261125/calc/paper_cell_monthly.py --lvens2-from <parquet>`. DISPLAY-ONLY: không sizing, không gate,
KHÔNG import / sửa dcf_valuation.py (ENS2 = trung vị D0B, DDM, EPV, MULT, HEDf — không cần engine production A_pit).

PROVENANCE (copy code, KHÔNG import chéo từ worktree V3.1 chưa merge — nhánh session/Taylor_20261124_170355 commit 1a279d12f):
  build_panel()  ← wt-dcf-v3-20261125/agents/Taylor/research/dcf_vn_redesign_20261125c/calc/b_panel.py  md5 0995ecde7495580a82b127987b490c2b
                   (mục 1–3; bỏ: kiểm cổng vs universe_pit, LOG đo, px_t1/px_last, mục 4 nhãn lợi suất tương lai)
  models()       ← .../calc/c_models2.py  md5 be7b28dd98ffb12cc0edee1935837788  (chỉ D0B, DDM, EPV, MULT, HEDf, ENS2)
  Cờ môi trường V3.1 (KD_Q/KD_Y/PICK_OS/MC_OLD/VND_N_OLD/PITMED) CỐ ĐỊNH ở mặc định V3.1 (45/90/tắt/tắt/tắt/bật) — không đọc env (§8: trục đổi số phải đổi tên file).
Đổi duy nhất về logic = cắt dữ liệu (mode pit): mọi nguồn chỉ giữ dòng có ngày ≤ D (D = phiên cuối tháng as-of trong cache `ticker`):
  giá BQ/VND, BCTC theo ngày công bố (BQ `time`; VND `known` = cuối quý + 45/90 ngày), universe_pit, fa_ratings_8l (route = route cuối ≤ D).
  Mode v31 (không cắt, route = route cuối toàn bảng) chỉ để chứng minh copy trung thành với vp2.parquet.
Nguồn (tra mike/kb/data_registry/): data/bq_cache/ticker (CANONICAL) · ticker_financial (CANONICAL; cột OShares = TRAP restate — xem REPORT) ·
  universe_pit (CANONICAL; không ticker_prune) · fa_ratings_8l route (TRAP: không PIT trước 2026 — xem REPORT).
  Đầu vào ĐÓNG BĂNG ngoài repo (không tái lập được từ repo, kiểm md5 fail-closed): FROZEN/delisted/ (VNDirect, 1.341 file) + FROZEN/px_pre2013_d.csv.
Dùng:  python lvens2_incremental.py --asof-ym 2026-10 [--mode pit|v31] [--out-dir DIR] [--frozen DIR] [--no-vnd]
Ra:    <out-dir>/lvens2_<ym>[_<mode-tag>].parquet + .json (md5 đầu vào, D, số dòng). rc 0 ok · 3 fail-closed."""
import os, sys, json, glob, hashlib, argparse
import numpy as np, pandas as pd, duckdb
WC = os.environ.get("WC_ROOT", "/home/trido/thanhdt/WorkingClaude"); HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN = os.environ.get("LVENS2_FROZEN", f"{WC}/wt-dcf-v3-20261125/agents/Taylor/research/dcf_vn_redesign_20261125c/out")
PRE_MD5 = "d01c7aa84064b7a1024c6c71e6cea08e"
NS = "datetime64[ns]"
KD_Q, KD_Y = 45, 90
R = 0.1225; GT = 0.055; H = 10
FIN_ROUTES = ["BANK", "INSURANCE", "SECURITIES"]
OUTCOLS = ["ticker", "ym", "time", "known", "src", "route", "in_universe", "E", "E_raw", "E_fix", "E_unexpl", "mc", "N", "N_mc", "ca_ratio", "ca_n", "n_next_used", "event_no_next",
           "lv_D0B", "lv_DDM", "lv_EPV", "lv_MULT", "lv_HEDf", "lv_ENS2", "n_ENS2"]
CACHE = f"{WC}/data/bq_cache"                     # đổi bằng --cache-root (selfcheck vintage); universe_pit LUÔN đọc từ WC/data/bq_cache (cache cũ không có)
CA_FILE = os.environ.get("LVENS2_CA", os.path.join(HERE, "..", "out", "ca", "ca_extract_20261125.csv"))
CA_MD5 = "28418e9d4d91abfa8965ac756bb3d9c4"
SHARE_METHODS = {"Trả Cổ tức bằng Cổ phiếu", "Cổ phiếu thưởng"}   # đổi số CP cho cổ đông hiện hữu tại ex-date, không có tiền
RIGHTS = "Quyền mua CP cho Cổ đông hiện hữu"
EGUARD = -0.07                                    # log(E_bo/E_trước) < EGUARD ⇒ BVPS đã ở cơ sở CP sau sự kiện
FRESH_DAYS = 10
MC_TAG = {"strict": "", "step": "_mcstep", "stepca": "_mcstepca", "stepcar": "_mcstepcar"}


def load_ca(path=None, verify=True):
    """Extract corporate_action đóng băng (ISS/DIV/AIS). Chỉ trả ISS đổi-số-CP (+ quyền mua), đã dedup (Bẫy 3 registry)."""
    path = path or CA_FILE
    if verify and md5f(path) != CA_MD5:
        raise SystemExit(f"FAIL-CLOSED: md5 {path} != {CA_MD5}")
    ca = pd.read_csv(path)
    ca = ca[(ca.event_code == "ISS") & (ca.event_status != "not_executed") & (ca.exercise_ratio > 0)
            & ca.issue_method_name_vi.isin(SHARE_METHODS | {RIGHTS}) & ca.exright_date.notna() & ca.public_date.notna()].copy()
    ca["ex"] = pd.to_datetime(ca.exright_date).astype(NS); ca["pub"] = pd.to_datetime(ca.public_date).astype(NS)
    ca["rights"] = ca.issue_method_name_vi == RIGHTS
    return ca.drop_duplicates(["ticker", "ex", "issue_method_name_vi", "exercise_ratio"])[["ticker", "ex", "pub", "exercise_ratio", "rights"]].reset_index(drop=True)


def ca_factor(rows, ca, include_rights=False):
    """rows: DataFrame[ticker, known, time] (time = ngày as-of của dòng). Trả (factor, n): Π(1+r) trên sự kiện known < ex ≤ time, pub ≤ time."""
    r = rows[["ticker", "known", "time"]].reset_index().rename(columns={"index": "_i"})
    e = ca if include_rights else ca[~ca.rights]
    m = r.merge(e, on="ticker", how="inner")
    m = m[(m.ex > m.known) & (m.ex <= m.time) & (m.pub <= m.time)]
    g = m.groupby("_i").exercise_ratio.agg(lambda s: float(np.prod(1.0 + s.values)))
    n = m.groupby("_i").size()
    return (pd.Series(1.0, index=rows.index).where(~rows.index.isin(g.index), g.reindex(rows.index)).values,
            n.reindex(rows.index).fillna(0).astype(int).values)


def e_guard(F, ca, Dcut=None, tol=0.06):
    """F (đã sort ticker,known): dòng E_src=BVPSxOS. BVPS có thể đã ghi theo cơ sở CP SAU sự kiện trong khi OShares còn cũ ⇒ E_raw tụt giả.
    Chỉ sửa khi mức tụt được GIẢI THÍCH bởi sự kiện đổi số CP (thưởng/cổ tức CP/quyền mua) đã CÔNG BỐ ≤ Dcut (as-of; None = ≤ known+400 ngày, chỉ mode v31):
    có tích tiền tố P = Π(1+r) (theo thứ tự ex, ex trong (known_trước−90, known+400]) với |log(E_trước/E_raw) − log P| < tol ⇒ E = E_raw × P.
    Hệ số mang theo qua các dòng CÙNG OShares, reset khi OShares đổi. Tụt KHÔNG giải thích được (cổ tức tiền, lỗ, dòng đầu sai) ⇒ giữ E_raw (không lan truyền)."""
    Er = F.E.values.astype(float); E = Er.copy(); fix = np.zeros(len(F), bool); unex = np.zeros(len(F), bool)
    bo = (F.E_src.values == "BVPSxOS"); t = F.known.values; tk = F.ticker.values; os_ = F.OShares.values.astype(float)
    ev = {k: g.sort_values("ex") for k, g in ca.groupby("ticker")}
    k = 1.0
    for i in range(len(F)):
        if i == 0 or not bo[i] or tk[i] != tk[i - 1] or not bo[i - 1] or (t[i] - t[i - 1]) > np.timedelta64(200, "D") or not (np.isfinite(E[i - 1]) and E[i - 1] > 0):
            k = 1.0; continue
        if not np.isfinite(os_[i]) or not np.isfinite(os_[i - 1]) or abs(np.log(os_[i] / os_[i - 1])) > 1e-6:
            k = 1.0
        cand = Er[i] * k
        if np.isfinite(cand) and cand > 0 and np.log(cand / E[i - 1]) < EGUARD:
            unex[i] = True
        if unex[i] and tk[i] in ev:
            g = ev[tk[i]]; lim = Dcut if Dcut is not None else t[i] + np.timedelta64(400, "D")
            g = g[(g.ex.values > t[i - 1] - np.timedelta64(90, "D")) & (g.ex.values <= t[i] + np.timedelta64(400, "D")) & (g.pub.values <= lim)]
            if len(g):
                P = np.cumprod(1.0 + g.exercise_ratio.values); drop = np.log(E[i - 1] / cand)
                j = np.argmin(np.abs(np.log(P) - drop))
                if abs(np.log(P[j]) - drop) < tol:
                    k = k * P[j]; unex[i] = False
        E[i] = Er[i] * k; fix[i] = k != 1.0
    return E, fix, unex


def md5f(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def verify_frozen(frozen):
    """fail-closed: md5 px_pre2013 + toàn bộ delisted/ khớp MD5SUMS_delisted.txt của V3.1."""
    pre = os.path.join(frozen, "px_pre2013_d.csv")
    if md5f(pre) != PRE_MD5:
        raise SystemExit(f"FAIL-CLOSED: md5 {pre} != {PRE_MD5}")
    ref = os.path.join(frozen, "..", "MD5SUMS_delisted.txt")
    bad = 0; n = 0
    for line in open(ref):
        m, fn = line.split(None, 1); fn = fn.strip()
        p = os.path.join(frozen, "delisted", fn[2:] if fn.startswith("./") else fn)
        n += 1
        if not os.path.exists(p) or md5f(p) != m:
            bad += 1
    if bad:
        raise SystemExit(f"FAIL-CLOSED: {bad}/{n} file delisted lệch md5")
    return n


def gate(g, valcol):
    yrs = (pd.Timestamp("2026-07-01") - g.time).dt.days.values / 365.25
    thr_in = 1.0e9 / 1.07 ** yrs; thr_out = 0.5e9 / 1.07 ** yrs
    v = g[valcol].values; med60 = pd.Series(v).rolling(60, min_periods=60).median().values
    max20 = pd.Series(v).rolling(20, min_periods=20).max().values
    cl = g.Price.values; gap = g.time.diff().dt.days.fillna(0).values
    inu = np.zeros(len(g), bool); cur = False
    for i in range(len(g)):
        if gap[i] > 20:
            cur = False
        if cur:
            if (max20[i] < thr_out[i]) or cl[i] < 1000 or v[i] <= 0 and (i >= 9 and (v[i - 9:i + 1] <= 0).all()):
                cur = False
        else:
            if i >= 60 and med60[i] >= thr_in[i] and cl[i] >= 1000:
                cur = True
        inu[i] = cur
    return inu


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
        flag = (np.isfinite(o["roe_tc5"][i]) and np.isfinite(roe[i]) and roe[i] - o["roe_tc5"][i] >= 0.10 and np.isfinite(g.revg.values[i]) and g.revg.values[i] >= 0.15
                and np.isfinite(npm[i]) and np.isfinite(o["npm_med5"][i]) and npm[i] > o["npm_med5"][i] and np.isfinite(o["E_1y"][i]) and E[i] >= o["E_1y"][i])
        k = k + 1 if flag else 0; o["jump_k"][i] = k
    for kk, v in o.items():
        g[kk] = v
    return g


def ssum(df, cols):
    return df[cols].sum(axis=1, min_count=len(cols))


def build_panel(D, frozen, use_vnd=True, poison=None, route_global=False, mc_pit="strict", nocut=(), eguard=True, ca=None):
    """b_panel.py mục 1–3. D=None ⇒ không cắt (mode v31). poison(df, timecol, name) — selfcheck PIT: phá dữ liệu SAU D, áp cho MỌI nguồn lúc nạp,
    ĐỘC LẬP với bước cắt. nocut = tập tên nguồn KHÔNG cắt (chỉ dùng cho mutation test: phải làm selfcheck đầu độc FAIL)."""
    c = duckdb.connect()
    _hurt = poison or (lambda df, col, name: df)

    def cutonly(df, col, name):
        return df[df[col] <= D] if (D is not None and name not in nocut) else df

    def load(df, col, name):                                  # [pit2] nạp = đầu độc (nếu selfcheck) rồi MỚI cắt; hai bước tách rời
        return cutonly(_hurt(df, col, name), col, name)
    # ---- 1. giá ----
    px = c.execute(f"""SELECT ticker, CAST(time AS DATE) AS time, Close, Price, Volume, Trading_Value_1M_P50 AS tv
          FROM read_parquet('{CACHE}/ticker/*.parquet') WHERE Close > 0 AND ICB_Code IS NOT NULL""").df()
    px["time"] = pd.to_datetime(px.time).astype(NS)
    px = load(px, "time", "px")
    pre = pd.read_csv(os.path.join(frozen, "px_pre2013_d.csv"), parse_dates=["time"]); pre["time"] = pre.time.astype(NS)
    pre = _hurt(pre, "time", "pre")[lambda x: x.time < px.time.min()].copy(); pre["tv"] = np.nan
    px = pd.concat([pre[["ticker", "time", "Close", "Price", "Volume", "tv"]], px], ignore_index=True).sort_values(["ticker", "time"]).reset_index(drop=True)
    px["src"] = "BQ"
    rows = []
    for fp in sorted(glob.glob(os.path.join(frozen, "delisted", "px_*.csv"))) if use_vnd else []:
        d = pd.read_csv(fp)
        if len(d) < 60 or "adClose" not in d.columns:
            continue
        d = d.sort_values("date"); d = d[(d.close > 0) & (d.adClose > 0)]
        d["time"] = pd.to_datetime(d.date).astype(NS)
        d["Close"] = d.adClose * 1000.0; d["Price"] = d.close * 1000.0; d["Volume"] = d.nmVolume.fillna(0)
        d["val"] = d.nmValue.fillna(0)
        rows.append(d[["code", "time", "Close", "Price", "Volume", "val", "floor"]].rename(columns={"code": "ticker"}))
    dead = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(columns=["ticker", "time", "Close", "Price", "Volume", "val", "floor"]).astype({"time": NS})
    dead = load(dead, "time", "vnd_px")
    dead = dead[~dead.ticker.isin(set(px.ticker))].copy()
    dead = dead.sort_values(["ticker", "time"]).reset_index(drop=True)
    dead["in_universe"] = np.concatenate([gate(g, "val") for _, g in dead.groupby("ticker", sort=False)]) if len(dead) else np.array([], bool)
    dead["tv"] = dead.groupby("ticker").val.transform(lambda s: s.rolling(20, min_periods=10).median()) if len(dead) else np.nan
    dead["src"] = "VND"
    uni = c.execute(f"SELECT ticker, CAST(time AS DATE) AS time FROM read_parquet('{WC}/data/bq_cache/universe_pit/*.parquet') WHERE in_universe").df()
    uni["time"] = pd.to_datetime(uni.time).astype(NS); uni["in_universe"] = True
    uni = load(uni, "time", "universe")
    last_trade = pd.concat([px[px.Volume.fillna(0) > 0].groupby("ticker").time.max(), dead[dead.Volume > 0].groupby("ticker").time.max()])
    allpx = pd.concat([px[["ticker", "time", "Close", "Price", "Volume", "tv", "src"]]]
                      + ([dead[["ticker", "time", "Close", "Price", "Volume", "tv", "src", "in_universe"]]] if len(dead) else []), ignore_index=True)
    allpx = allpx[allpx.time <= allpx.ticker.map(last_trade)].sort_values(["ticker", "time"]).reset_index(drop=True)
    allpx["ym"] = allpx.time.dt.to_period("M")
    # ---- 2. BCTC ----
    fin = c.execute(f"""SELECT ticker, CAST(time AS DATE) AS time, quarter, Price AS price_fin, Close AS close_fin, BVPS, OShares,
       totalAsset_P0 AS ta, StLiab_P0 AS stl, LtLiab_P0 AS ltl, ROE_Trailing, NP_P0,NP_P1,NP_P2,NP_P3,NP_P4,NP_P5,NP_P6,NP_P7,
       Revenue_P0,Revenue_P1,Revenue_P2,Revenue_P3,Revenue_P4,Revenue_P5,Revenue_P6,Revenue_P7, GPM_P0, NPM_P0, EBITM_P0, ROA_P0,
       Cash_P0, StDebt_P0, LtDebt_P0, DY, CF_OA_P0,CF_OA_P1,CF_OA_P2,CF_OA_P3, CF_Invest_P0,CF_Invest_P1,CF_Invest_P2,CF_Invest_P3,
       CF_OA_3Y, CF_Invest_3Y, FSCORE, IntCov_P0, CashCycle_P0, ROIC5Y, Debt_Eq_P0, STLTDebt_Eq_P0, Inventory_P0, AR_P0
       FROM read_parquet('{CACHE}/ticker_financial.parquet') WHERE BVPS IS NOT NULL AND OShares > 0""").df()
    fin["time"] = pd.to_datetime(fin.time).astype(NS)
    fin = load(fin, "time", "fin")
    fin = fin.sort_values(["ticker", "time"]).drop_duplicates(["ticker", "time"], keep="last").reset_index(drop=True)
    pk = allpx[allpx.src == "BQ"][["ticker", "time", "Close", "Price"]].rename(columns={"Close": "close_rel", "Price": "price_tk", "time": "ptime"}).sort_values("ptime")
    fin = pd.merge_asof(fin.sort_values("time"), pk, left_on="time", right_on="ptime", by="ticker", direction="backward", tolerance=pd.Timedelta(days=7))
    fin["price_rel"] = fin.price_tk.fillna(fin.price_fin)
    fin = fin[fin.close_rel.notna() & (fin.price_rel > 0)].sort_values(["ticker", "time"]).reset_index(drop=True)
    e2 = fin.ta - fin.stl.fillna(0) - fin.ltl.fillna(0); has_liab = (fin.stl.fillna(0) + fin.ltl.fillna(0)) > 0
    e1 = fin.BVPS * fin.OShares
    fin["E"] = np.where(has_liab & (e2.notna()), e2, e1); fin["E_src"] = np.where(has_liab & e2.notna(), "TA-L", "BVPSxOS")
    fin["N_b"] = np.where((fin.BVPS > 0) & (fin.E > 0), fin.E / fin.BVPS, np.nan)
    fin = pd.concat([pick_n(g) for _, g in fin.groupby("ticker", sort=False)], ignore_index=True)
    fin["MC_rel"] = fin.price_rel * fin.N
    fin["src"] = "BQ"
    fin["np_ttm"] = ssum(fin, [f"NP_P{i}" for i in range(4)]); fin["np_prev"] = ssum(fin, [f"NP_P{i}" for i in range(4, 8)])
    fin["rev_ttm"] = ssum(fin, [f"Revenue_P{i}" for i in range(4)]); fin["rev_prev"] = ssum(fin, [f"Revenue_P{i}" for i in range(4, 8)])
    fin["cfo_ttm"] = ssum(fin, [f"CF_OA_P{i}" for i in range(4)]); fin["capex_ttm"] = -ssum(fin, [f"CF_Invest_P{i}" for i in range(4)])
    fin["debt"] = fin.StDebt_P0.fillna(0) + fin.LtDebt_P0.fillna(0); fin["cash"] = fin.Cash_P0
    fin["ebit_ttm"] = fin.EBITM_P0 * fin.rev_ttm
    fin["div_ttm"] = fin.DY.fillna(0) * fin.MC_rel
    fin["roe"] = fin.ROE_Trailing
    fin["np_q"] = fin.NP_P0
    fin["E_raw"] = fin.E
    if eguard:                                                # [pit2] SAU pick_n (N vẫn từ E gốc = OShares ⇒ không kéo số CP tương lai vào N)
        fin = fin.sort_values(["ticker", "known" if "known" in fin else "time"]).reset_index(drop=True)
        fin["known"] = fin.time
        fin["E"], fin["E_fix"], fin["E_unexpl"] = e_guard(fin, _hurt(ca if ca is not None else load_ca(), "pub", "ca"), Dcut=D if "ca" not in nocut else None)
    else:
        fin["E_fix"] = False; fin["E_unexpl"] = False
    fin = fin.rename(columns={"GPM_P0": "gpm", "ROA_P0": "roa", "FSCORE": "fscore", "IntCov_P0": "intcov", "CashCycle_P0": "cashcycle", "ROIC5Y": "roic5",
                              "Debt_Eq_P0": "debt_eq", "CF_OA_3Y": "cfo3y", "CF_Invest_3Y": "cfi3y"})
    fin["known"] = fin.time
    KEEP = ["ticker", "known", "price_rel", "quarter", "src", "E", "N", "MC_rel", "close_rel", "roe", "np_ttm", "np_prev", "rev_ttm", "rev_prev", "cfo_ttm", "capex_ttm", "debt", "cash",
            "ebit_ttm", "div_ttm", "gpm", "roa", "fscore", "intcov", "cashcycle", "roic5", "debt_eq", "cfo3y", "cfi3y", "E_src", "N_how", "BVPS", "OShares", "E_raw", "E_fix", "E_unexpl"]
    parts = [fin[KEEP]]
    if use_vnd and len(dead):
        dfs = load_dead_fs(frozen)
        dfs = load(dfs, "known", "vnd_fs")              # [PIT] cắt TRƯỚC khi tính N_nxt (kỳ kế) — b_panel tính N_nxt trên toàn bộ kỳ ⇒ look-ahead
        dfs = dfs[dfs.ticker.isin(set(dead.ticker))]
        dk = dead[["ticker", "time", "Close", "Price"]].rename(columns={"Close": "close_rel", "Price": "price_rel", "time": "ptime"}).sort_values("ptime")
        dfs = pd.merge_asof(dfs.sort_values("known"), dk, left_on="known", right_on="ptime", by="ticker", direction="backward", tolerance=pd.Timedelta(days=30))
        dfs = dfs[dfs.close_rel.notna()].copy()
        dk2 = dk.rename(columns={"close_rel": "close_fq", "price_rel": "price_fq", "ptime": "ptime_fq"}).sort_values("ptime_fq")
        dfs = pd.merge_asof(dfs.sort_values("fq"), dk2, left_on="fq", right_on="ptime_fq", by="ticker", direction="backward", tolerance=pd.Timedelta(days=10))
        dfs = dfs.sort_values(["ticker", "known"]).reset_index(drop=True)
        dfs["N_v2"] = dfs.N
        dfs["pf"] = np.log(dfs.price_rel / dfs.close_rel); dfs["pf_fq"] = np.log(dfs.price_fq / dfs.close_fq)
        dfs["N_nxt"] = dfs.groupby("ticker").N_v2.shift(-1)
        _stp = (dfs.pf_fq - dfs.pf); _s = np.log(dfs.N_nxt / dfs.N_v2)
        _ok = dfs.pf_fq.notna() & _s.notna() & (_stp.abs() > 0.003) & ((_s - _stp).abs() < _s.abs())
        dfs["N_v3"] = np.where(_ok, dfs.N_v2 * np.exp(_stp), dfs.N_v2)
        dfs["N"] = dfs.N_v3
        dfs["MC_rel"] = dfs.price_rel * dfs.N; dfs["time"] = dfs.known; dfs["E_raw"] = dfs.E; dfs["E_fix"] = False; dfs["E_unexpl"] = False
        parts.append(dfs[KEEP])
    F = pd.concat(parts, ignore_index=True).sort_values(["ticker", "known"]).reset_index(drop=True)
    F = F[F.E.notna() & (F.MC_rel > 0)].copy()
    F["N_next"] = F.groupby("ticker").N.shift(-1)
    F["roe"] = F.roe.clip(-0.5, 0.6); F["npm"] = (F.np_ttm / F.rev_ttm.where(F.rev_ttm > 0)).clip(-0.5, 0.6)
    F["payout_raw"] = np.where(F.np_ttm > 0, (F.div_ttm / F.np_ttm).clip(0, 1), np.nan)
    F["revg"] = (F.rev_ttm / F.rev_prev.where(F.rev_prev > 0) - 1).clip(-0.6, 1.5); F["npg"] = np.where((F.np_prev > 0) & (F.np_ttm > 0), (F.np_ttm / F.np_prev - 1), np.nan)
    F["npg"] = pd.Series(F.npg).clip(-0.9, 3.0).values
    F = pd.concat([roll_stats(g) for _, g in F.groupby("ticker", sort=False)], ignore_index=True)
    # ---- 3. lưới tháng ----
    me = allpx.groupby(["ticker", "ym"]).tail(1).copy()
    fn = allpx.groupby(["ticker", "ym"]).head(1)[["ticker", "ym", "time", "Close"]].rename(columns={"time": "t1_time", "Close": "t1_close"}); fn["ym"] = fn.ym - 1
    me = me.merge(fn, on=["ticker", "ym"], how="left")
    me = me[me.ym >= pd.Period("2008-01")].sort_values(["time", "ticker"]).reset_index(drop=True)
    pan = pd.merge_asof(me, F.sort_values("known"), left_on="time", right_on="known", by="ticker", direction="backward", suffixes=("", "_f"))
    pan = pan[pan.known.notna() & ((pan.time - pan.known).dt.days <= 200)].copy()
    assert (pan.known <= pan.time).all(), "PIT violation"
    pan["mc_old"] = pan.MC_rel * pan.Close / pan.close_rel
    _lr_now = np.log(pan.Close / pan.Price); _lr_k = np.log(pan.close_rel / pan.price_rel)
    _sevent = ((_lr_now - _lr_k).abs() > 0.003)
    _nn = pan.N_next.where(pan.N_next.notna() & (np.log(pan.N_next / pan.N).abs() > 0.01))
    _N = np.where(_sevent & _nn.notna(), _nn, pan.N)
    _mc_new = pan.Price * _N
    pan["mc"] = np.where(np.isfinite(_mc_new) & (pan.Price > 0), _mc_new, pan.mc_old)
    pan["mc_strict"] = pan.mc
    pan["mc_step"] = np.where(_sevent & pan.N_next.isna() & np.isfinite(pan.mc_old), pan.mc_old, pan.mc)
    if mc_pit == "step":
        # [BIẾN THỂ PIT, không có trong V3.1] có sự kiện từ ngày công bố mà kỳ BCTC kế CHƯA công bố ở D ⇒ dùng mc_old = Price×N×hệ số giá
        # (bắt được thưởng/chia tách; sai số = tỉ suất cổ tức tiền nếu sự kiện chỉ là cổ tức tiền). strict = đúng code V3.1 (N cũ).
        pan["mc"] = np.where(_sevent & pan.N_next.isna() & np.isfinite(pan.mc_old), pan.mc_old, pan.mc)
    # [pit2] stepca/stepcar: chỉ sự kiện ĐỔI SỐ CP (thưởng/cổ tức CP; stepcar + quyền mua) có ex trong (ngày BCTC, as-of] và public_date ≤ as-of; KHÔNG cổ tức tiền
    cae = _hurt(ca if ca is not None else load_ca(), "ex", "ca")
    cae = cutonly(cutonly(cae, "ex", "ca"), "pub", "ca")
    for v, rr in (("stepca", False), ("stepcar", True)):
        f, n = ca_factor(pan, cae, include_rights=rr)
        pan["mc_" + v] = np.where(pan.N_next.isna() & (n > 0) & (pan.Price > 0), pan.Price * pan.N * f, pan.mc_strict)
        pan["ca_ratio_" + v] = f; pan["ca_n_" + v] = n
    pan["ca_ratio"] = pan.get("ca_ratio_" + mc_pit, 1.0); pan["ca_n"] = pan.get("ca_n_" + mc_pit, 0)
    pan["mc"] = pan["mc_" + mc_pit]
    pan["N_mc"] = pan.mc / pan.Price
    pan["event_no_next"] = (_sevent & pan.N_next.isna()).values
    pan["n_next_used"] = (_sevent & _nn.notna()).values
    if "in_universe" not in pan.columns:                      # chỉ khi --no-vnd (không có cột in_universe của nhánh VND)
        pan["in_universe"] = np.nan
    pan = pan.merge(uni[["ticker", "time"]].assign(iu_bq=True), on=["ticker", "time"], how="left")
    pan["in_universe"] = np.where(pan.src == "BQ", pan.iu_bq.fillna(False), pan.in_universe.fillna(False)).astype(bool); pan = pan.drop(columns=["iu_bq", "src_f"], errors="ignore")
    rat = c.execute(f"SELECT ticker, CAST(time AS DATE) AS time, route, rating FROM read_parquet('{CACHE}/fa_ratings_8l.parquet')").df()
    rat["time"] = pd.to_datetime(rat.time).astype(NS)
    rat = _hurt(rat, "time", "rating")
    if not route_global:                                     # chẩn đoán: --route-global giữ route cuối toàn bảng (như vp2) để tách nguồn lệch
        rat = cutonly(rat, "time", "rating")
    rat = rat.sort_values("time"); route = rat.groupby("ticker").route.last()
    pan["route"] = pan.ticker.map(route).fillna("COMPOUNDER")
    pan = pan.sort_values(["ticker", "ym"]).reset_index(drop=True)
    pan["ym"] = pan.ym.astype(str)
    return pan


def load_dead_fs(frozen):
    out = []
    for fp in sorted(glob.glob(os.path.join(frozen, "delisted", "fs_*.csv"))):
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


def rim_vb(roe_n, r, gT, ret, kappa):
    roe_lr = r + kappa * (roe_n - r); B = np.ones_like(roe_n); pv = np.zeros_like(roe_n)
    for t in range(1, H + 1):
        roe_t = roe_n + (roe_lr - roe_n) * t / 10.0
        g_raw = np.clip(roe_t * ret, 0, 0.15); g_t = gT + (g_raw - gT) * (H - t) / (H - 1.0)
        g_t = np.minimum(g_t, np.maximum(roe_t, 0.0))
        pv += (roe_t - r) * B / (1 + r) ** t; B = B * (1 + g_t)
    g_term = np.minimum(gT, np.maximum(roe_lr, 0.0))
    return np.maximum(1 + pv + (roe_lr - r) * B / (r - g_term) / (1 + r) ** H, 0.2)


def ddm_vb(roe_n, p, r, gT):
    B = np.ones_like(roe_n); pv = np.zeros_like(roe_n)
    g1 = np.clip(roe_n * (1 - p), 0, 0.15)
    for t in range(1, H + 1):
        g_t = gT + (g1 - gT) * (H - t) / (H - 1.0); g_t = np.minimum(g_t, np.maximum(roe_n, 0))
        pv += (roe_n - g_t) * B / (1 + r) ** t
        B = B * (1 + g_t)
    d11 = np.where(roe_n > gT, (roe_n - gT) * B, p * roe_n * B)
    return pv + d11 / (r - gT) / (1 + r) ** H


def models(pan):
    """c_models2.py: D0B, DDM, EPV, MULT, HEDf, ENS2 (PITMED=1)."""
    pan = pan.sort_values(["ticker", "ym"]).reset_index(drop=True)
    pan["mi"] = pd.PeriodIndex(pan.ym, freq="M").year * 12 + pd.PeriodIndex(pan.ym, freq="M").month
    E = pan.E.where(pan.E > 0).values; mc = pan.mc.values; lmc = np.log(mc)
    roe = pan.roe.clip(-0.3, 0.5).values; tc = pan.roe_tc5.clip(-0.1, 0.4).values
    ret = (1 - pan.payout.fillna(0.3)).clip(0.1, 1.0).values
    isfin = pan.route.isin(FIN_ROUTES).values
    L = {}
    ev = pan.mc + pan.debt.fillna(0) - pan.cash.fillna(0)
    w = np.where(pan.jump_k.values >= 2, 0.75 * np.minimum(1.0, pan.jump_k.values / 4.0), 0.0)
    rn_j = np.clip(tc + w * (np.clip(roe, -0.1, 0.5) - tc), -0.1, 0.5)
    kap = np.where(pan.route.values == "BANK", 0.7, 0.4)
    L["D0B"] = np.log(rim_vb(rn_j, R, GT, ret, kap) * E) - lmc
    p = pan.payout.clip(0.05, 1.0).values
    elig = (pan.div_cnt20.values >= 16) & (rn_j > 0.01) & np.isfinite(p)
    with np.errstate(all="ignore"):
        L["DDM"] = np.where(elig, np.log(np.maximum(ddm_vb(np.maximum(rn_j, 0.011), np.nan_to_num(p, nan=0.3), R, GT), 1e-6) * E) - lmc, np.nan)
    e_norm = (pan.rev_ttm * pan.npm_med5).values
    gg = np.minimum(GT, rn_j * ret)
    okv = (~isfin) & (e_norm > 0) & (rn_j > gg + 0.005) & np.isfinite(E)
    with np.errstate(all="ignore"):
        L["EPV"] = np.where(okv, np.log(e_norm * (1 - gg / rn_j) / (R - gg)) - lmc, np.nan)
    with np.errstate(all="ignore"):
        M = {"pe": np.log(mc / (tc * E)), "pb": np.log(mc / E), "ps": np.where(isfin, np.nan, np.log(mc / pan.rev_ttm.where(pan.rev_ttm > 0).values)),
             "ee": np.where(isfin, np.nan, np.log(ev.where(ev > 0).values / pan.ebit_ttm.where(pan.ebit_ttm > 0).values))}
    for k in M:
        M[k] = np.where(np.isfinite(M[k]), M[k], np.nan); pan["m_" + k] = M[k]
    iu = pan.in_universe.values
    mult_est = []
    for k in ("pe", "pb", "ps", "ee"):
        d = pan.loc[iu, ["mi", "route", "m_" + k]].dropna()
        rm = d.groupby(["mi", "route"])["m_" + k].agg(["median", "count"]).reset_index()
        mm = d.groupby("mi")["m_" + k].median().rename("mkt")
        rm = rm.merge(mm, on="mi"); rm["v"] = np.where(rm["count"] >= 8, rm["median"], rm.mkt)
        piv = rm.pivot(index="mi", columns="route", values="v").reindex(range(pan.mi.min(), pan.mi.max() + 1))
        piv = piv.apply(lambda s: s.fillna(mm.reindex(piv.index)))
        tr = piv.shift(1).rolling(60, min_periods=24).mean().stack().rename("mult").reset_index()
        x = pan[["mi", "route"]].merge(tr, on=["mi", "route"], how="left").mult.values
        if k == "pe":
            v = np.exp(x) * tc * E
        elif k == "pb":
            v = np.exp(x) * E
        elif k == "ps":
            v = np.where(isfin, np.nan, np.exp(x) * pan.rev_ttm.values)
        else:
            v = np.where(isfin, np.nan, np.exp(x) * pan.ebit_ttm.values - pan.debt.fillna(0).values + pan.cash.fillna(0).values)
        with np.errstate(all="ignore"):
            mult_est.append(np.where(v > 0, np.log(v), np.nan) - lmc)
    me_ = np.vstack(mult_est); cnt = np.isfinite(me_).sum(0)
    with np.errstate(all="ignore"):
        L["MULT"] = np.where(cnt >= 2, np.nanmedian(me_, axis=0), np.nan)
    routes = [r for r in sorted(pan.route.unique()) if r != "COMPOUNDER"]
    # HEDf (extra_liq=False, freeze 2020-01): beta cố định = OLS gộp 60 tháng 2015-01..2019-12 trên mã in_universe
    X = pd.DataFrame({"c": 1.0, "tc": tc, "roe": np.clip(roe, -0.3, 0.5), "loss": (pan.np_ttm.values < 0).astype(float), "revg": pan.revg.fillna(0).values,
                      "po": pan.payout.fillna(0.3).clip(0, 1).values, "lev": (pan.debt.fillna(0) / pan.E.where(pan.E > 0)).clip(0, 3).values,
                      "sd": pan.roe_sd5.fillna(pan.groupby("mi").roe_sd5.transform("median")).values, "le": np.log(E)})
    for r in routes:
        X["r_" + r] = (pan.route.values == r).astype(float)
    y = M["pb"]; Xv = X.values; good = np.isfinite(Xv).all(1) & np.isfinite(y)
    fit = good & iu; mi = pan.mi.values; lo, hi = mi.min(), mi.max(); p_ = Xv.shape[1]
    xtx = np.zeros((hi - lo + 2, p_, p_)); xty = np.zeros((hi - lo + 2, p_)); nm = np.zeros(hi - lo + 2)
    for m in np.unique(mi[fit]):
        s = fit & (mi == m); a = Xv[s]; yy = np.clip(y[s], np.nanpercentile(y[s], 1), np.nanpercentile(y[s], 99))
        xtx[m - lo] = a.T @ a; xty[m - lo] = a.T @ yy; nm[m - lo] = 1
    pred = np.full(len(pan), np.nan); FRZ = 2020 * 12 + 1; beta_frz = None
    for m in range(lo, hi + 1):
        mm_ = min(m, FRZ)
        a0 = max(0, mm_ - lo - 60); a1 = mm_ - lo
        if nm[a0:a1].sum() < 24:
            continue
        b = np.linalg.lstsq(xtx[a0:a1].sum(0) + 1e-6 * np.eye(p_), xty[a0:a1].sum(0), rcond=None)[0]
        if m == FRZ:
            beta_frz = dict(zip(X.columns.tolist(), [float(x) for x in b]))
        s = good & (mi == m); pred[s] = Xv[s] @ b
    L["HEDf"] = pred - y
    for k, v in L.items():
        pan["lv_" + k] = np.where(np.isfinite(v), v, np.nan)
    C2 = ["lv_D0B", "lv_DDM", "lv_EPV", "lv_MULT", "lv_HEDf"]
    a = pan[C2].values; n = np.isfinite(a).sum(1)
    with np.errstate(all="ignore"):
        pan["lv_ENS2"] = np.where(n >= 1, np.nanmedian(a, axis=1), np.nan)
    pan["n_ENS2"] = n
    return pan, beta_frz


def last_session(ym):
    c = duckdb.connect()
    D = c.execute(f"""SELECT MAX(CAST(time AS DATE)) FROM read_parquet('{CACHE}/ticker/*.parquet')
                      WHERE strftime(CAST(time AS DATE), '%Y-%m') = '{ym}'""").fetchone()[0]
    return None if D is None else pd.Timestamp(D)


def freshness(D):
    """[pit2] fail-closed: ticker_financial / fa_ratings_8l trong cache phải tươi tới gần D (manifest max_time ≥ D − FRESH_DAYS). Trả (ok, chi tiết)."""
    man = json.load(open(os.path.join(CACHE, "manifest.json"))).get("tables", {})
    det = {}; ok = True
    for t in ("ticker_financial", "fa_ratings_8l"):
        mt = man.get(t, {}).get("max_time")
        det[t] = mt
        if mt is None or pd.Timestamp(mt) < D - pd.Timedelta(days=FRESH_DAYS):
            ok = False
    return ok, det


def run(yms, mode, out_dir, frozen, use_vnd=True, poison=None, tag="", route_global=False, mc_pit="strict", nocut=(), eguard=True, dump_panel=None):
    n_frozen = verify_frozen(frozen) if use_vnd else 0
    ca = load_ca()                                            # md5 fail-closed kể cả khi mc_pit không dùng CA (ledger ghi md5 nhất quán)
    fresh = None
    if mode == "pit":
        assert len(yms) == 1, "mode pit: một as-of mỗi lần (dữ liệu cắt theo as-of)"
        D = last_session(yms[0])
        if D is None:
            print(f"FAIL-CLOSED: cache ticker không có phiên nào của {yms[0]}", file=sys.stderr); return 3
        u = duckdb.connect().execute(f"SELECT MAX(CAST(time AS DATE)) FROM read_parquet('{WC}/data/bq_cache/universe_pit/*.parquet')").fetchone()[0]
        if pd.Timestamp(u) < D:
            print(f"FAIL-CLOSED: universe_pit max {u} < D {D.date()}", file=sys.stderr); return 3
        now = pd.Timestamp.now(tz="Asia/Ho_Chi_Minh")
        if D.month == now.month and D.year == now.year:
            print(f"FAIL-CLOSED: {yms[0]} là tháng hiện tại — chưa hết tháng", file=sys.stderr); return 3
        ok, fresh = freshness(D)
        if not ok:
            print(f"FAIL-CLOSED: cache không tươi so với D {D.date()}: {fresh} (cần ≥ D−{FRESH_DAYS} ngày)", file=sys.stderr); return 3
    else:
        D = None
    vnd_max = None
    if use_vnd:                                               # snapshot VNDirect đóng băng: as-of sau ngày cuối của snapshot ⇒ mã chỉ-có-ở-VND thiếu giá tháng mới
        _d = [pd.read_csv(f, usecols=["date"]).date.dropna() for f in glob.glob(os.path.join(frozen, "delisted", "px_*.csv"))]
        vnd_max = max((str(x.max()) for x in _d if len(x)), default=None)
        if D is not None and vnd_max is not None and pd.Timestamp(vnd_max) < D:
            print(f"WARN: snapshot VND dừng ở {vnd_max} < D {D.date()} — mã chỉ-có-ở-VND (vd GEL/HPA/DSH) dùng giá cũ/vắng tháng này", file=sys.stderr)
    variants = list(MC_TAG) if mc_pit == "all" else [mc_pit]
    pan0 = build_panel(D, frozen, use_vnd=use_vnd, poison=poison, route_global=route_global, mc_pit=variants[0], nocut=nocut, eguard=eguard, ca=ca)
    for v in variants:
        pan = pan0.copy(); pan["mc"] = pan["mc_" + v]; pan["N_mc"] = pan.mc / pan.Price
        pan["ca_ratio"] = pan.get("ca_ratio_" + v, 1.0); pan["ca_n"] = pan.get("ca_n_" + v, 0)
        rc = _emit(pan, v, yms, mode, D, out_dir, frozen, use_vnd, route_global, eguard, nocut, tag, vnd_max, n_frozen, fresh, dump_panel if v == variants[0] else None)
    return rc


def _emit(pan, mc_pit, yms, mode, D, out_dir, frozen, use_vnd, route_global, eguard, nocut, tag, vnd_max, n_frozen, fresh, dump_panel):
    if dump_panel:                                            # đo sai số mc mọi tháng (mc_err.py) — cột tối thiểu, mọi tháng
        pan[["ticker", "ym", "time", "known", "src", "in_universe", "N", "N_next", "Price", "Close", "price_rel", "close_rel", "E", "E_raw", "E_fix"]].to_parquet(dump_panel, index=False)
    pan, beta = models(pan)
    os.makedirs(out_dir, exist_ok=True)
    sfx = (("" if mode == "pit" else "_" + mode) + ("" if use_vnd else "_novnd") + ("_routeglobal" if route_global else "") + MC_TAG[mc_pit]
           + ("" if eguard else "_noeguard") + ("_nocut-" + "-".join(sorted(nocut)) if nocut else "") + tag)
    vintage = os.path.abspath(CACHE) != os.path.abspath(f"{WC}/data/bq_cache")
    for ym in yms:
        o = pan[pan.ym == ym][OUTCOLS].sort_values("ticker").reset_index(drop=True)
        o["asof_date"] = (D if D is not None else o.time.max())
        o["mode"] = mode; o["mc_pit"] = mc_pit
        fp = os.path.join(out_dir, f"lvens2_{ym}{sfx}.parquet")
        tmp = fp + ".tmp"; o.to_parquet(tmp, index=False); os.replace(tmp, fp)
        iu = o[o.in_universe]
        meta = {"asof_ym": ym, "mode": mode, "D": str(o.asof_date.iloc[0].date()) if len(o) else None, "rows": int(len(o)), "in_universe": int(len(iu)),
                "in_universe_lv_ENS2_ok": int(iu.lv_ENS2.notna().sum()), "n_next_used_in_univ": int(iu.n_next_used.sum()),
                "use_vnd": use_vnd, "vnd_px_max_date": vnd_max, "mc_pit": mc_pit, "route_global": route_global, "eguard": eguard, "nocut": sorted(nocut),
                "event_no_next_in_univ": int(iu.event_no_next.sum()), "ca_step_in_univ": int((iu.ca_n > 0).sum()), "E_fix_in_univ": int(iu.E_fix.sum()), "E_unexpl_in_univ": int(iu.E_unexpl.sum()), "E_unexpl_tickers": sorted(iu[iu.E_unexpl].ticker),
                "frozen_files_verified": n_frozen, "hed_beta_frozen_2020-01": beta, "cache_root": CACHE, "cache_vintage": vintage, "freshness": fresh,
                "inputs_md5": {k: md5f(p) for k, p in (("ticker_financial", f"{CACHE}/ticker_financial.parquet"), ("fa_ratings_8l", f"{CACHE}/fa_ratings_8l.parquet"),
                                                       ("ca_extract", CA_FILE), ("frozen_manifest", os.path.join(frozen, "..", "MD5SUMS_delisted.txt")),
                                                       ("px_pre2013", os.path.join(frozen, "px_pre2013_d.csv")))},
                "script_md5": md5f(os.path.abspath(__file__))}
        json.dump(meta, open(fp.replace(".parquet", ".json"), "w"), ensure_ascii=False, indent=1, default=str)
        print(f"{ym} [{mode}{sfx}] D={meta['D']} rows={meta['rows']} in_univ={meta['in_universe']} ENS2_ok={meta['in_universe_lv_ENS2_ok']} "
              f"ca_step={meta['ca_step_in_univ']} E_fix={meta['E_fix_in_univ']} -> {fp}", flush=True)
    return 0


def main():
    global CACHE
    ap = argparse.ArgumentParser()
    ap.add_argument("--asof-ym", required=True, nargs="+"); ap.add_argument("--mode", choices=["pit", "v31"], default="pit")
    ap.add_argument("--out-dir", default=os.path.join(HERE, "..", "out")); ap.add_argument("--frozen", default=FROZEN)
    ap.add_argument("--no-vnd", action="store_true"); ap.add_argument("--route-global", action="store_true", help="CHẨN ĐOÁN, không dùng cho sổ: route cuối toàn bảng (look-ahead)")
    ap.add_argument("--mc-pit", choices=list(MC_TAG) + ["all"], default="strict", help="all = dựng 1 lần, ghi 4 biến thể")
    ap.add_argument("--no-eguard", action="store_true", help="CHẨN ĐOÁN: tắt chặn E ngân hàng (như bản đã merge)")
    ap.add_argument("--cache-root", default=CACHE, help="selfcheck vintage: thư mục cache cũ (vd data/bq_cache_asof20260728)")
    ap.add_argument("--dump-panel", default=None)
    a = ap.parse_args()
    CACHE = os.path.abspath(a.cache_root)
    return run(a.asof_ym, a.mode, a.out_dir, a.frozen, use_vnd=not a.no_vnd, route_global=a.route_global, mc_pit=a.mc_pit,
               eguard=not a.no_eguard, dump_panel=a.dump_panel)


if __name__ == "__main__":
    sys.exit(main())
