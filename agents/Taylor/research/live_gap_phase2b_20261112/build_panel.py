#!/usr/bin/env python3
"""GĐ2-B (job Taylor_20261112_125912, sửa GĐ2-A theo required_change quant-skeptic).
GĐ2-A (job Taylor_20261112_122858): panel deal BAL/LAG + nhãn excess vs tiết kiệm PIT + đặc trưng PIT tại ngày tín hiệu.

Nguồn deal engine: ledger C1fix_v3 (code vá mergesort, LAG files frozen 11-12, BQ cache 07-29 postrestate, AUDIT_END 06-19).
Đặc trưng: data/bq_cache (manifest verified 2026-11-11) — 1 vintage cho mọi deal (engine + live).
Quy ước thời gian: ngày tín hiệu sig = phiên giao dịch NGAY TRƯỚC lần khớp đầu tiên (engine thực thi T+1);
mọi đặc trưng chỉ dùng thông tin có tại đóng cửa sig (hoặc sớm hơn theo độ trễ công bố ghi ở FEATURE_META).
Chạy: /home/trido/thanhdt/wc_venv/bin/python build_panel.py   -> panel.csv, panel.parquet, feature_meta.csv
"""
import os, sys, glob
import numpy as np, pandas as pd

W = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, W)
sys.path.insert(0, os.path.join(W, "mike/agents/Taylor/research/live_gap_phase0_20261112"))
import hurdle_pit as HP                                   # noqa: E402
P1B = os.path.join(W, "mike/agents/Taylor/research/live_gap_phase1b_20261112")
MODE = os.environ.get("PANEL_MODE", "old")          # old = ledger C1fix_v3 (LIQ_ZERO_BLOCK tắt) | liqz = ledger C1fix_v3_liqz (LIQ_ZERO_BLOCK=lag)
LEDGER = glob.glob(HERE + "/ledgers/*liqzblag*C1fix_v3_liqz_univpit.csv" if MODE == "liqz" else P1B + "/ledgers/*_C1fix_v3_univpit.csv")[0]
TAX_SELL = 0.001                                     # thuế bán 0,1%
FEE_LIVE = 0.00097                                   # phí DNSE thật 0,097%/chiều (§6)
SBX = P1B + "/sb_fix/data"
CACHE = W + "/data/bq_cache"
FILLS = W + "/mike/agents/Taylor/research/live_gap_phase0_20261112/fills_booked.csv"
EXCL_PT = ("ETF_PARK", "CAPITB", "CAPITL")

_masof = pd.merge_asof
def _ns(df):
    df = df.copy()
    for c in df.columns:
        if str(df[c].dtype).startswith("datetime64"):
            df[c] = df[c].astype("datetime64[ns]")
    if "ticker" in df.columns:
        df["ticker"] = df["ticker"].astype(str)
    return df
def _merge_asof_ns(left, right, *a, **k):          # pandas 3: khoá datetime khác đơn vị (s/us/ns) ⇒ chuẩn hoá ns
    return _masof(_ns(left), _ns(right), *a, **k)
pd.merge_asof = _merge_asof_ns

META = []
def meta(col, src, lag):
    META.append(dict(feature=col, source=src, pit_rule=lag))

# ----------------------------------------------------------------- price/fundamental panel
COLS = ["time", "ticker", "Close", "Price", "Volume", "MA200", "D_RSI", "D_CMF", "PE", "PB", "PCF", "OShares",
        "PE_MA5Y", "PE_SD5Y", "PB_MA5Y", "PB_SD5Y", "ROE_Min5Y", "ROIC5Y", "FSCORE", "CF_OA_P0", "ICB_Code", "VNINDEX", "VNINDEX_PE"]
def load_ticker():
    fs = sorted(glob.glob(CACHE + "/ticker/*.parquet"))
    fs = [f for f in fs if int(os.path.basename(f)[:4]) >= 2012]
    d = pd.concat([pd.read_parquet(f, columns=COLS) for f in fs], ignore_index=True)
    d["time"] = pd.to_datetime(d["time"])
    return d.sort_values(["ticker", "time"]).reset_index(drop=True)

def tech(d):
    g = d.groupby("ticker", sort=False)
    d["mom_200"] = d.Close / d.MA200.replace(0, np.nan) - 1
    d["dd52"] = d.Close / g.Close.transform(lambda s: s.rolling(252, min_periods=120).max()) - 1
    r = g.Close.pct_change()
    d["rvol20"] = r.groupby(d.ticker).transform(lambda s: s.rolling(20, min_periods=15).std()) * np.sqrt(252)
    tv = d.Price * d.Volume                                     # Price THÔ × Volume thô (cùng cơ sở PIT)
    d["adv20"] = tv.groupby(d.ticker).transform(lambda s: s.rolling(20, min_periods=10).mean())
    d["ey"] = np.where(d.PE > 0, 1 / d.PE, np.nan)
    d["cfy"] = np.where(d.PCF > 0, 1 / d.PCF, np.nan)
    # 1/PS = doanh thu TTM (quý đã công bố, as-of Release_Date) / (Price thô × OShares thô) — cùng công thức rating_8l `ps`
    tf = pd.read_parquet(CACHE + "/ticker_financial.parquet", columns=["ticker", "Release_Date", "Revenue_P0", "Revenue_P1", "Revenue_P2", "Revenue_P3"])
    tf["Release_Date"] = pd.to_datetime(tf.Release_Date); tf = tf.dropna(subset=["Release_Date"])
    tf["rev_ttm"] = tf[["Revenue_P0", "Revenue_P1", "Revenue_P2", "Revenue_P3"]].sum(axis=1, min_count=4)
    tf = tf.sort_values("Release_Date")[["ticker", "Release_Date", "rev_ttm"]].drop_duplicates(["ticker", "Release_Date"], keep="last")
    d = d.sort_values("time")
    d = pd.merge_asof(d, tf, left_on="time", right_on="Release_Date", by="ticker", direction="backward")
    d = d.sort_values(["ticker", "time"]).reset_index(drop=True)
    mc = d.Price * d.OShares
    d["psy"] = np.where((mc > 0) & (d.rev_ttm > 0), d.rev_ttm / mc, np.nan)
    d["pe_rel5y"] = np.where((d.PE > 0) & (d.PE_MA5Y > 0), d.PE / d.PE_MA5Y, np.nan)
    d["pb_z5y"] = (d.PB - d.PB_MA5Y) / d.PB_SD5Y.replace(0, np.nan)
    d["cfoa_pos"] = np.where(d.CF_OA_P0.notna(), (d.CF_OA_P0 > 0).astype(float), np.nan)
    return d

def universe():
    fs = sorted(glob.glob(CACHE + "/universe_pit/*.parquet"))
    u = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "in_universe"]) for f in fs])
    u["time"] = pd.to_datetime(u["time"])
    return u[u.in_universe.astype(bool)][["time", "ticker"]]

def composite_and_breadth(d, u):
    x = d.merge(u.assign(inu=1), on=["time", "ticker"], how="left")
    x = x[x.inu == 1]
    # composite v3 = trung bình phân vị cross-section (trong universe_pit cùng phiên) của ey, cfy, psy
    comp = x[["time", "ey", "cfy", "psy"]]          # phân phối cross-section universe_pit từng phiên (để xếp hạng deal, kể cả mã ngoài universe)
    # breadth chuẩn (breadth-tercile-axis-20260822): mẫu số chỉ mã MA200 không NULL
    y = x[x.MA200.notna()]
    br = y.groupby("time").apply(lambda g: (g.Close > g.MA200).mean(), include_groups=False).rename("breadth").reset_index()
    br = br.sort_values("time").reset_index(drop=True)
    b = br.breadth.values; pct = np.full(len(b), np.nan)
    for i in range(252, len(b)):
        pct[i] = (b[i - 252:i] < b[i]).sum() / 253.0
    br["breadth_pct"] = pct
    br["breadth_terc"] = np.select([br.breadth_pct < 1 / 3, br.breadth_pct < 2 / 3, br.breadth_pct >= 2 / 3], [0, 1, 2], np.nan)
    br.loc[br.breadth_pct.isna(), "breadth_terc"] = np.nan
    # phân loại phiên t dùng breadth_{t-1}: ở đây đặc trưng đo tại đóng cửa sig (= t-1 của phiên khớp) ⇒ dùng breadth_sig
    return comp, br

# ----------------------------------------------------------------- deals
def engine_deals():
    L = pd.read_csv(LEDGER, low_memory=False)
    t = L[L.record_type == "TX"].copy()
    t["ymd"] = pd.to_datetime(t["ymd"])
    t["pt"] = t.play_type.fillna("NA").str.replace(r"_E\d+$", "", regex=True)
    t = t[~t.pt.isin(EXCL_PT)]
    rows = []
    for hid, x in t.groupby("holding_id"):
        b = x[x.action == "buy"]; s = x[x.action == "sell"]
        if b.empty or s.empty:
            continue
        reasons = set(s.reason)
        rows.append(dict(src="engine", holding_id=hid, ticker=x.ticker.iloc[0], book=x.book.iloc[0], play_type=x.pt.iloc[0],
                         first_fill=b.ymd.min(), exit_date=s.ymd.max(),
                         buy_cash_native=(b.buy_amount + b.fee).sum(), sell_cash_native=(s.sell_amount - s.fee).sum(),
                         buy_cash=b.buy_amount.sum() * (1 + FEE_LIVE), sell_cash=s.sell_amount.sum() * (1 - FEE_LIVE - TAX_SELL),
                         buy_notional=b.buy_amount.sum(),
                         exit_reason="|".join(sorted(reasons)),
                         abandoned="ABANDONED_REFUND" in reasons, open_at_end="MTM_UNREALIZED" in reasons))
    D = pd.DataFrame(rows)
    D["ret_pct"] = (D.sell_cash / D.buy_cash - 1) * 100
    D["ret_native_pct"] = (D.sell_cash_native / D.buy_cash_native - 1) * 100
    return D

def live_deals():
    """FIFO theo acct×mã trên MỌI lô PARK/BAL/LAG. Sửa vs GĐ2-A (skeptic):
    (1) lô đóng MỘT PHẦN tách thành deal ĐÓNG (đủ nhãn) + deal MỞ — trước đây gộp lại làm NaN toàn bộ;
    (2) lệnh bán gán book X nhưng X hết lô (vd PARKMERGE-SELL-VPB bán phần LAG) ⇒ trừ lô book khác, cũ nhất trước."""
    f = pd.read_csv(FILLS, parse_dates=["date"])
    f = f[f.book_inferred.isin(["PARK", "BAL", "LAG"])].sort_values(["acct", "ticker", "ts"])
    rows = []
    def emit(ac, tk, lot, take, px, d):
        rows.append(dict(src="live_" + ac, holding_id=f"{ac}_{tk}_{lot['date'].date()}_{lot['book']}", ticker=tk, book=lot["book"],
                         play_type="LIVE", first_fill=lot["date"], exit_date=d,
                         buy_cash=take * lot["px"] * (1 + FEE_LIVE),
                         sell_cash=(take * px * (1 - FEE_LIVE - TAX_SELL)) if d is not pd.NaT else np.nan,
                         buy_notional=take * lot["px"], exit_reason="LIVE_SELL" if d is not pd.NaT else "LIVE_OPEN",
                         abandoned=False, open_at_end=d is pd.NaT, sold_by_other_book=lot.get("xb", False)))
    for (ac, tk), x in f.groupby(["acct", "ticker"]):
        lots = []
        for _, r in x.iterrows():
            q = float(r.qty); px = float(r.price); bk = r.book_inferred
            if r.side == "buy":
                lots.append(dict(q=q, px=px, date=r.date, book=bk, sold=[]))
                continue
            order = [l for l in lots if l["book"] == bk] + [l for l in lots if l["book"] != bk]
            for l in order:
                if q <= 1e-9: break
                take = min(q, l["q"])
                l["sold"].append((take, px, r.date, l["book"] != bk))
                l["q"] -= take; q -= take
            lots = [l for l in lots if l["q"] > 1e-9 or l["sold"]]
            for l in lots:
                pass
        for l in lots:
            if l["book"] == "PARK": continue
            for take, px, d, xb in l["sold"]:
                emit(ac, tk, dict(l, xb=xb), take, px, d)
            if l["q"] > 1e-9:
                emit(ac, tk, l, l["q"], np.nan, pd.NaT)
    D = pd.DataFrame(rows)
    D["exit_date"] = pd.to_datetime(D.exit_date)
    # gộp theo (acct,mã,book,ngày mua đầu) PHÂN BIỆT đóng / mở: các mảnh đóng cùng lô ⇒ 1 deal đóng (exit = ngày bán cuối)
    D["closed"] = ~D.open_at_end
    D = D.groupby(["src", "holding_id", "ticker", "book", "play_type", "first_fill", "closed"], as_index=False).agg(
        exit_date=("exit_date", "max"), buy_cash=("buy_cash", "sum"), sell_cash=("sell_cash", lambda s: s.sum(min_count=1)),
        buy_notional=("buy_notional", "sum"), exit_reason=("exit_reason", lambda s: "|".join(sorted(set(s)))),
        abandoned=("abandoned", "max"), open_at_end=("open_at_end", "max"), sold_by_other_book=("sold_by_other_book", "max"))
    D["holding_id"] = D.holding_id + np.where(D.closed, "_C", "_O")
    D = D.drop(columns="closed")
    D["ret_pct"] = (D.sell_cash / D.buy_cash - 1) * 100
    D["ret_native_pct"] = D.ret_pct
    return D

def label(D, cal):
    D = D.copy()
    ci = pd.Index(cal)
    D["sig_date"] = [cal[ci.searchsorted(x) - 1] if ci.searchsorted(x) > 0 else pd.NaT for x in D.first_fill]
    D["hold_sessions"] = [ci.searchsorted(e) - ci.searchsorted(s) if pd.notna(e) else np.nan for s, e in zip(D.first_fill, D.exit_date)]
    D["hold_cal_days"] = (D.exit_date - D.first_fill).dt.days
    D["hurdle_accr_pct"] = [HP.accrual_pct(s, e) if pd.notna(e) else np.nan for s, e in zip(D.first_fill, D.exit_date)]
    D["excess_pp"] = D.ret_pct - D.hurdle_accr_pct
    D["excess_native_pp"] = D.ret_native_pct - D.hurdle_accr_pct          # độ nhạy: phí engine gốc (gồm thuế+trượt giá engine)
    D["hit"] = np.where(D.excess_pp.notna(), (D.excess_pp > 0).astype(float), np.nan)
    D["labelled"] = (~D.abandoned) & (~D.open_at_end) & D.excess_pp.notna()
    D["era"] = np.where(D.sig_date < "2020-01-01", "IS", "OOS")
    D.loc[D.src.str.startswith("live"), "era"] = "LIVE"
    return D

def independent_events(D, cal, gap=5):
    """Cùng book + cùng mã: deal mới vào ≤ gap phiên sau lần thoát cuối của cụm ⇒ cùng 1 sự kiện."""
    ci = pd.Index(cal); D = D.sort_values(["book", "ticker", "first_fill"]).copy(); ev = []; k = 0
    for (bk, tk), x in D.groupby(["book", "ticker"], sort=False):
        last_exit = None
        for i, r in x.iterrows():
            if last_exit is None or ci.searchsorted(r.first_fill) - ci.searchsorted(last_exit) > gap:
                k += 1
            ev.append((i, k))
            e = r.exit_date if pd.notna(r.exit_date) else r.first_fill
            last_exit = e if last_exit is None else max(last_exit, e)
    m = dict(ev); D["event_id"] = [m[i] for i in D.index]
    return D

# ----------------------------------------------------------------- market / macro / commodity
def market_state(cal):
    s = pd.read_parquet(CACHE + "/vnindex_5state_dt5g_live.parquet"); s["time"] = pd.to_datetime(s["time"])
    s = s.sort_values("time").reset_index(drop=True)
    clk = np.zeros(len(s)); c = 0
    for i in range(len(s)):
        c = c + 1 if s.state_raw.iloc[i] != s.state.iloc[i] else 0
        clk[i] = c
    s["dt5g_cand_clock"] = clk
    return s.rename(columns={"state": "dt5g_state"})[["time", "dt5g_state", "dt5g_cand_clock"]]

def macro(cal):
    m = pd.DataFrame({"time": pd.DatetimeIndex(cal)})
    h = HP.H[["date", "hurdle_pct"]].rename(columns={"date": "time"})
    m = pd.merge_asof(m, h, on="time")
    h63 = h.copy(); h63["time"] = h63.time + pd.Timedelta(days=91)
    m = pd.merge_asof(m, h63.rename(columns={"hurdle_pct": "h_3m_ago"}), on="time")
    m["hurdle_chg3m"] = m.hurdle_pct - m.h_3m_ago
    import sbv_macro_overlay as S
    ev = pd.DataFrame(S.SBV_REFI_EVENTS, columns=["time", "refi"]); ev["time"] = pd.to_datetime(ev.time)
    m = pd.merge_asof(m, ev.sort_values("time"), on="time")
    e6 = ev.copy(); e6["time"] = e6.time + pd.Timedelta(days=182)
    m = pd.merge_asof(m, e6.sort_values("time").rename(columns={"refi": "refi_6m_ago"}), on="time")
    m["refi_chg6m"] = m.refi - m.refi_6m_ago
    import cpi_vn
    m = cpi_vn.merge_cpi(m, "time", end="2026-11-01", pit=True)
    m = m.rename(columns={c: c for c in m.columns})
    us = pd.read_csv(W + "/data/us_market_history.csv", parse_dates=["time"]).sort_values("time")
    m["jt"] = m.time - pd.Timedelta(days=1)                       # US phiên T-1 (như macro_state_live)
    m = pd.merge_asof(m.sort_values("jt"), us[["time", "vix", "spx_dd_1y"]].rename(columns={"time": "us_t"}),
                      left_on="jt", right_on="us_t", direction="backward").sort_values("time")
    import value_radar as VR
    v = VR.load_series(update=False)[["time", "score", "label"]].rename(columns={"score": "radar_score", "label": "radar_zone"})
    v["time"] = pd.to_datetime(v.time)
    m = pd.merge_asof(m, v.sort_values("time"), on="time")
    keep = ["time", "hurdle_pct", "hurdle_chg3m", "refi", "refi_chg6m", "vix", "spx_dd_1y", "radar_score", "radar_zone"]
    cc = [c for c in m.columns if c.startswith("cpi_yoy")]
    return m[keep + cc]

TICK_COMM = {}
for tk in "PVD PVS PVC PVB GAS BSR PLX OIL PVT CNG PGC PGS PGD PVE POS".split(): TICK_COMM[tk] = "brent"
for tk in "DPM DCM LAS BFC DDV".split(): TICK_COMM[tk] = "urea"
for tk in "HPG HSG NKG TLH SMC POM VGS TVN DTL HMC".split(): TICK_COMM[tk] = "iron_ore"
for tk in "GVR PHR DPR TRC DRI TNC HRC".split(): TICK_COMM[tk] = "rubber"
for tk in "SBT LSS QNS SLS".split(): TICK_COMM[tk] = "sugar"
for tk in "DBC MML".split(): TICK_COMM[tk] = "hog"
for tk in "VSH SJD CHP TBC HJS SHP GHC TMP AVC DRL S4A SBH ISH HNA".split(): TICK_COMM[tk] = "oni"

def commodities():
    """Trả dict name -> DataFrame(avail_date, value). Độ trễ công bố áp ở avail_date."""
    out = {}
    raw = pd.read_excel(W + "/data/CMO-Historical-Data-Monthly.xlsx", "Monthly Prices", header=None)
    hdr = [str(h) for h in raw.iloc[4].tolist()]; body = raw.iloc[6:].copy()
    body = body[body[0].map(str).str.match(r"^\d{4}M\d{2}$")]
    mon = pd.to_datetime(body[0].map(str).str.replace("M", "-") + "-01")
    pick = {"brent": "Crude oil, Brent", "urea": "Urea", "iron_ore": "Iron ore", "rubber": "Rubber, TSR20", "sugar": "Sugar, world"}
    for k, name in pick.items():
        j = [i for i, h in enumerate(hdr) if h.strip().startswith(name)]
        if not j: continue
        v = pd.to_numeric(body[j[0]], errors="coerce")
        out[k] = pd.DataFrame({"avail": mon + pd.offsets.MonthBegin(1) + pd.Timedelta(days=9), "value": v.values}).dropna()   # CMO tháng M công bố đầu M+1
    hg = pd.read_csv(W + "/data/hog_price_vn.csv", parse_dates=["date"]).groupby("date").price_vnd_kg.mean()
    out["hog"] = pd.DataFrame({"avail": hg.index + pd.Timedelta(days=1), "value": hg.values})
    o = pd.read_csv(W + "/data/oni_index.csv")
    smap = {"DJF": 2, "JFM": 3, "FMA": 4, "MAM": 5, "AMJ": 6, "MJJ": 7, "JJA": 8, "JAS": 9, "ASO": 10, "SON": 11, "OND": 12, "NDJ": 1}
    endm = pd.to_datetime([f"{y + (1 if s == 'NDJ' else 0)}-{smap[s]:02d}-01" for y, s in zip(o.year, o.season)])
    out["oni"] = pd.DataFrame({"avail": endm + pd.offsets.MonthBegin(1) + pd.Timedelta(days=19), "value": o.anom.values})  # CPC ~20 tháng sau
    return out

def comm_feature(D, C):
    lvl = np.full(len(D), np.nan); chg = np.full(len(D), np.nan)
    for i, (tk, sd) in enumerate(zip(D.ticker, D.sig_date)):
        k = TICK_COMM.get(tk)
        if k is None or k not in C or pd.isna(sd): continue
        s = C[k]; a = s[s.avail <= sd]
        if a.empty: continue
        cur = a.value.iloc[-1]
        if k == "oni":
            lvl[i] = cur; chg[i] = cur; continue                    # ONI: mức anom (không phải % thay đổi)
        b = s[s.avail <= sd - pd.Timedelta(days=91)]
        if b.empty or b.value.iloc[-1] <= 0: continue
        chg[i] = np.log(cur / b.value.iloc[-1])
    D["comm_key"] = D.ticker.map(TICK_COMM)
    D["comm_chg3m"] = chg
    return D

# ----------------------------------------------------------------- edge health
def map_sector(icb):
    sys.path.insert(0, W); import edge_health_monitor as E
    return E.map_sector(icb)

def edge_ic(D, icb_by_tk):
    p = pd.read_csv(W + "/data/edge_panel.csv", parse_dates=["time"])
    import edge_health_monitor as E
    p["sector"] = p.icb.map(E.map_sector); p["ym"] = p.time.dt.to_period("M")
    lo, hi = p.fwd_3m.quantile([0.005, 0.995]); p["fwd_3m"] = p.fwd_3m.clip(lo, hi)
    ics = {}
    for sig in ("mom_200", "PE"):
        for sec, g in p.groupby("sector"):
            ics[(sig, sec)] = E.monthly_ic(g, sig, False, 15)
    out = {}
    for sig, name in (("mom_200", "ic_mom_sec12"), ("PE", "ic_pe_sec12")):
        vals = []
        for tk, sd in zip(D.ticker, D.sig_date):
            s = ics.get((sig, E.map_sector(icb_by_tk.get(tk))))
            if s is None or s.empty or pd.isna(sd): vals.append(np.nan); continue
            # IC tháng m dùng fwd_3m từ phiên đầu tháng m ⇒ chỉ biết sau ~m+3 tháng; dùng tháng m khi m+4 tháng ≤ sig (bảo thủ)
            known = s[(s.index + pd.DateOffset(months=4)) <= sd]
            vals.append(known.tail(12).mean() if len(known) >= 6 else np.nan)
        out[name] = vals
    for k, v in out.items(): D[k] = v
    eh = pd.read_csv(SBX + "/lag_edge_health.csv", parse_dates=["known_date"]).drop_duplicates("known_date").sort_values("known_date")
    m12 = eh.set_index("known_date").mean12
    pct = []
    for sd in D.sig_date:
        h = m12[m12.index <= sd]
        pct.append((h < h.iloc[-1]).mean() * 100 if len(h) >= 24 else np.nan)
    D["lag_edge_pct"] = pct
    D["lag_edge_mean12"] = [m12[m12.index <= sd].iloc[-1] if (m12.index <= sd).any() else np.nan for sd in D.sig_date]
    return D

def sue_feature(D):
    s = pd.read_pickle(SBX + "/earnings_surprise_data.pkl")
    s["Release_Date"] = pd.to_datetime(s.Release_Date)
    dif = np.column_stack([s[f"NP_P{i}"] - s[f"NP_P{i+4}"] for i in range(4)])
    sd = np.nanstd(dif, axis=1, ddof=1)
    s["sue"] = np.where(sd > 0, dif[:, 0] / sd, np.nan)
    s = s.sort_values("Release_Date")[["ticker", "Release_Date", "sue", "NP_R", "Revenue_YoY_P0"]]
    x = D[["sig_date", "ticker"]].reset_index().sort_values("sig_date")
    x = pd.merge_asof(x, s, left_on="sig_date", right_on="Release_Date", by="ticker", direction="backward",
                      tolerance=pd.Timedelta(days=120))
    x = x.set_index("index").reindex(D.index)
    D["sue"] = x.sue.values; D["np_yoy"] = x.NP_R.values; D["rev_yoy"] = x.Revenue_YoY_P0.values
    D["days_since_release"] = (D.sig_date - x.Release_Date.values).dt.days
    return D

# ----------------------------------------------------------------- main
def main():
    T = load_ticker(); T = tech(T)
    cal = sorted(T[T.ticker == "VNINDEX"].time.unique()) if (T.ticker == "VNINDEX").any() else sorted(T.time.unique())
    cal = pd.DatetimeIndex(cal)
    U = universe(); comp, br = composite_and_breadth(T, U)
    D = pd.concat([engine_deals(), live_deals()], ignore_index=True)
    D = label(D, cal); D = independent_events(D, cal)
    f = ["time", "ticker", "PE", "PB", "PCF", "ey", "cfy", "psy", "pe_rel5y", "pb_z5y", "ROE_Min5Y", "ROIC5Y", "FSCORE", "cfoa_pos",
         "mom_200", "D_RSI", "D_CMF", "dd52", "rvol20", "adv20", "ICB_Code"]
    D = D.merge(T[f].rename(columns={"time": "sig_date"}), on=["sig_date", "ticker"], how="left")
    # composite v3 = trung bình (≥2/3 trục có giá trị) phân vị của ey/cfy/psy SO VỚI cross-section universe_pit cùng phiên
    for c in ("ey", "cfy", "psy"):
        ref = {t: np.sort(g.dropna().values) for t, g in comp.groupby("time")[c]}
        D[c + "_pct"] = [(np.searchsorted(ref[t], v, side="left") / len(ref[t])) if (pd.notna(v) and t in ref and len(ref[t]) >= 30) else np.nan
                         for t, v in zip(D.sig_date, D[c])]
    pc = D[["ey_pct", "cfy_pct", "psy_pct"]]
    D["comp_v3"] = pc.mean(axis=1).where(pc.notna().sum(axis=1) >= 2)
    D["adv_pct"] = D.buy_notional / D.adv20 * 100
    D["log_adv20"] = np.log10(D.adv20.where(D.adv20 > 0))
    D["tradable"] = (D.adv_pct <= 100)                                        # tổng mua ≤ 100% ADV20 (Price thô × Volume)
    # biến vĩ mô dựa hurdle (KHÔNG PIT: 26 mốc neo hồi tố 2026-06-19 — registry deposit_rate_vn caveat b)
    vni = T[T.ticker == "VNINDEX"][["time", "Close", "VNINDEX_PE"]].sort_values("time")
    vni["vni_dd52"] = vni.Close / vni.Close.rolling(252, min_periods=120).max() - 1
    if vni.VNINDEX_PE.isna().all():
        vni["VNINDEX_PE"] = np.nan
    D = D.merge(vni[["time", "vni_dd52", "VNINDEX_PE"]].rename(columns={"time": "sig_date", "VNINDEX_PE": "vni_pe"}), on="sig_date", how="left")
    if D.vni_pe.isna().mean() > 0.5:   # VNINDEX row may not carry the mirror col -> take mirror from any stock row
        mir = T.groupby("time").VNINDEX_PE.first().rename("vni_pe2").reset_index().rename(columns={"time": "sig_date"})
        D = D.merge(mir, on="sig_date", how="left"); D["vni_pe"] = D.vni_pe.fillna(D.vni_pe2); D = D.drop(columns="vni_pe2")
    D = D.merge(br.rename(columns={"time": "sig_date"}), on="sig_date", how="left")
    D = D.merge(market_state(cal).rename(columns={"time": "sig_date"}), on="sig_date", how="left")
    D = D.merge(macro(cal).rename(columns={"time": "sig_date"}), on="sig_date", how="left")
    D["spread_ey_hurdle"] = D.ey * 100 - D.hurdle_pct
    D["spread_mkt_hurdle"] = 100 / D.vni_pe - D.hurdle_pct
    r8 = pd.read_parquet(CACHE + "/fa_ratings_8l.parquet"); r8["time"] = pd.to_datetime(r8.time)
    x = pd.merge_asof(D[["sig_date", "ticker"]].reset_index().sort_values("sig_date"), r8.sort_values("time"),
                      left_on="sig_date", right_on="time", by="ticker", direction="backward").set_index("index").reindex(D.index)
    D["rating8l"] = x.rating.values; D["route8l"] = x.route.values
    D = sue_feature(D)
    D = comm_feature(D, commodities())
    icb = T.dropna(subset=["ICB_Code"]).groupby("ticker").ICB_Code.last().to_dict()
    D = edge_ic(D, icb)
    D["year"] = D.sig_date.dt.year
    D.to_csv(os.path.join(HERE, f"panel_{MODE}.csv"), index=False)
    D.to_parquet(os.path.join(HERE, f"panel_{MODE}.parquet"), index=False)
    print("panel rows", len(D)); print(D.groupby(["src", "book", "labelled"]).size())

if __name__ == "__main__":
    main()
