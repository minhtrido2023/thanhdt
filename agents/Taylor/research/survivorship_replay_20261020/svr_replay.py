"""Survivorship replay BAL/LAG — phantom trades trên mã lớn đã biến mất, overlay lên ledger pin R3.
Job Taylor_20261020_094204, theo PREREG.md (md5 21165fd1, commit 9b0b27912). EXPLORATORY — không ghi registry/pin.
Biến thể *_ALLOC = độ nhạy KHÔNG prereg (xem overlay_alloc).
Usage: $DNA_PYEXE svr_replay.py <out_dir> <label>=<ledger.csv> ...
"""
import sys, os, json
import numpy as np, pandas as pd
from svr_lib import load_px, indicators, ta_px, universe

HERE = os.path.dirname(os.path.abspath(__file__))
WIN = "/home/trido/thanhdt/WorkingClaude/mike/agents/Winston/research/vanished_20261020"
KBP = "/home/trido/thanhdt/WorkingClaude/mike/kb/projects"
V2 = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/survivorship_sensitivity_v2_20261020/out_summary_SUPERSEDED_bookcount_bug.json"  # ghim w v2 gốc mà replay CONFIRMED dùng; bản fix A ở out_summary.json
M = "ROS FLC GAB KLF ART HAI AMD SJF PSH TTB KSA TGG DAG NHP".split()
HVG = ["HVG"]
E = "KSH TNA KHB VIS CAV DPS VMI AVF KSS RDP SIC IBC CEE PPI SPI GTT NDF KSK KPF ASA BGM".split()
REL_LAG = {1: 27, 2: 32, 3: 26, 4: 27}          # PREREG §6 (trung vị trễ công bố, pkl từ 2014)
COST = 0.001
BAL_HOLD, BAL_STOP, LAG_HOLD = 45, -0.20, 25
PART, FILL_DAYS, MIN_FILL = 0.20, 5, 0.30


def calc_metrics(s):  # nguyên văn pt_v23_audit_2014.py::calc_metrics (phần cần dùng)
    s = s.dropna(); yrs = (s.index[-1] - s.index[0]).days / 365.25
    r = s.pct_change().dropna()
    return dict(cagr=(s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1,
                sharpe_252=r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else 0,
                max_dd=(s / s.cummax() - 1).min())


def load_ledger(path):
    df = pd.read_csv(path, low_memory=False)
    met = df[df.record_type == "METRIC"].set_index("key")["value"]
    d = df[df.record_type == "DAILY"].copy(); d["ymd"] = pd.to_datetime(d.ymd); d = d.set_index("ymd").sort_index()
    for c in ["combined_nav", "state", "w_lag_tgt", "cap_bal", "cap_lag", "nav_bal_ref", "nav_lag_ref",
              "bal_stocks_ref", "lag_stocks_ref"]:
        d[c] = d[c].astype(float)
    tx = df[df.record_type == "TX"].copy(); tx["ymd"] = pd.to_datetime(tx.ymd); tx["shares"] = tx.shares.astype(float)
    return met, d, tx


# ---------------------------------------------------------------- fundamentals (VNDirect)
def load_fin():
    a = pd.read_csv(f"{WIN}/fin_raw.csv"); b = pd.read_csv(f"{HERE}/data/fin_raw_live_ext.csv")
    f = pd.concat([a, b]); f = f[f.item.isin(["npat_parent", "revenue", "cfo"])]
    w = f.pivot_table(index=["ticker", "fiscalDate"], columns="item", values="value", aggfunc="first").reset_index()
    w["fiscalDate"] = pd.to_datetime(w.fiscalDate)
    w["rel"] = [fd + pd.Timedelta(days=REL_LAG[(fd.month - 1) // 3 + 1]) for fd in w.fiscalDate]
    return {tk: g.sort_values("fiscalDate").set_index("fiscalDate") for tk, g in w.groupby("ticker")}


def fin_asof(fq, d):
    """Các quý đã công bố (rel ≤ d)."""
    return fq[fq.rel <= d]


def q_back(fq, fd, k):
    t = fd - pd.DateOffset(months=3 * k)
    t = t + pd.offsets.QuarterEnd(0)
    return fq.loc[t] if t in fq.index else None


def golden(fq_known):
    """Golden floor xấp xỉ (PREREG §6): TTM npat tại ≤3 cuối năm gần nhất ≥0 ∧ tổng CFO ≤12 quý gần nhất >0."""
    if fq_known is None or len(fq_known) == 0:
        return False
    ye = [fd for fd in fq_known.index if fd.month == 12][-3:]
    for fd in ye:
        ttm = fq_known.loc[(fq_known.index > fd - pd.DateOffset(years=1)) & (fq_known.index <= fd), "npat_parent"].sum()
        if ttm < 0:
            return False
    cfo = fq_known.cfo.dropna().iloc[-12:]
    return len(cfo) > 0 and cfo.sum() > 0


# ---------------------------------------------------------------- per-ticker series
class Tk:
    def __init__(self, tk, cal_mkt, infl, vmax, ledger_days, orig=None):
        px = load_px(tk); self.tk = tk
        if orig is None:
            orig = px.floor[px.floor != "UPCOM"].mode().iloc[0] if (px.floor != "UPCOM").any() else px.floor.iloc[0]
        self.orig = orig
        po = px[px.floor == orig]
        self.LT = po.index[po.nmVolume > 0].max(); self.DL = po.index.max()
        post = px[(px.index > self.DL) & (px.nmVolume > 0)]
        self.U_date = post.index.min() if len(post) else None
        self.U_px = float(post.adClose.iloc[0]) * 1000 if len(post) else None
        pre = px[px.index <= self.DL]
        self.ind = indicators(pre, pre.index)
        self.univ = universe(px, cal_mkt, infl)
        self.ta = ta_px(self.ind, vmax)
        L = ledger_days
        self.close = self.ind.Close.reindex(L, method="ffill")          # đã gồm halt (giá đứng)
        self.close[L > self.DL] = np.nan
        self.open = self.ind.Open.reindex(L)
        self.vol = pre.nmVolume.reindex(L).fillna(0.0)
        self.val = pre.val.reindex(L).fillna(0.0)
        self.liq = self.ind.liq.reindex(L)
        self.u = self.univ.reindex(L).fillna(False)
        self.adj = (px.adClose / px.close.replace(0, np.nan)).reindex(L, method="ffill")


# ---------------------------------------------------------------- signals
def bal_signals(T, d, vni, fq, variant):
    L = d.index; st = d.state
    oh = (vni.Close / vni.MA200 > 1.30).reindex(L).fillna(False) & ((st == 5) | (vni.D_RSI.reindex(L) > 0.75))
    base = T.u & (T.liq >= 1e9) & st.isin([4, 5]) & ~oh & T.ta.reindex(L).notna() & (L <= T.LT)
    out = []
    for day in L[base.values]:
        tpx = T.ta.get(day)
        if variant == "UB":
            ok = tpx >= 44
        else:
            k = fin_asof(fq, day) if fq is not None else None
            if k is None or len(k) == 0:
                continue
            fd = k.index[-1]; p0 = k.npat_parent.iloc[-1]
            r1, r4 = q_back(fq, fd, 1), q_back(fq, fd, 4)
            p1 = r1.npat_parent if r1 is not None else np.nan; p4 = r4.npat_parent if r4 is not None else np.nan
            t = tpx + (8 if (p4 > 0 and p0 > p4 * 1.5) else 0) - (8 if (p4 > 0 and p0 < p4 * 0.7) else 0) \
                + (8 if (p1 > 0 and p0 > p1 * 1.2) else 0)
            npy = p0 / p4 - 1 if (p4 and not np.isnan(p4)) else np.nan
            rv4 = r4.revenue if r4 is not None else np.nan
            rvy = k.revenue.iloc[-1] / rv4 - 1 if (rv4 and not np.isnan(rv4)) else np.nan
            grow = (npy > 0.2) or (rvy > 0.2)
            s = st[day]
            ok = (s == 4 and t >= 155) or ((s == 4 and 100 <= t < 155 and grow) or (s == 5 and 100 <= t < 155 and grow))
            if ok and variant == "LIVE":
                ok = golden(k)
        if ok:
            out.append(day)
    return out


def lag_events(T, d, fq, cal_mkt, variant, skip_bear=True):
    """Trả list ngày sd (ngày tín hiệu, vào Open phiên sau)."""
    L = d.index; A = cal_mkt.values
    def off(ref, k):
        p = np.searchsorted(A, np.datetime64(ref), side="right") - 1 + k
        return pd.Timestamp(A[p]) if 0 <= p < len(A) else None
    pxc = T.ind.Close
    def cl(ref, k):
        t = off(ref, k)
        return pxc.get(t, np.nan) if t is not None else np.nan
    if variant == "UB":
        qs = pd.date_range("2013-09-30", T.DL, freq="QE")
        evs = [(q, q + pd.Timedelta(days=REL_LAG[(q.month - 1) // 3 + 1]), True) for q in qs]
    else:
        if fq is None:
            return []
        evs, hist = [], []
        for fd, r in fq.iterrows():
            r4 = q_back(fq, fd, 4)
            if r4 is None or pd.isna(r.npat_parent) or pd.isna(r4.npat_parent) or r4.npat_parent == 0:
                continue
            npr = (r.npat_parent / r4.npat_parent - 1) * 100
            rel = r.rel
            ps = [cl(rel, -30), cl(rel, -1), cl(rel, 5), cl(rel, 30)]
            if any(pd.isna(x) for x in ps) or min(ps) <= 0:
                continue                                  # engine: event không có đủ cửa sổ giá thì bị loại
            post = (ps[3] / ps[2] - 1) * 100
            n_good = len(hist)
            if hist:
                da = np.array([(rel - h[0]).days / 365.25 for h in hist]); w = np.exp(-np.log(2) * da / 3.0)
                pa = float((np.array([h[1] for h in hist]) * w).sum() / w.sum())
            else:
                pa = np.nan
            ok = npr >= 15 and n_good >= 4 and pa >= 5
            if ok and variant == "LIVE":
                ok = golden(fin_asof(fq, rel))
            evs.append((fd, rel, ok))
            if npr >= 15:
                hist.append((rel, post))
    out = []
    for fd, rel, ok in evs:
        if not ok:
            continue
        ent = off(rel, 5)
        if ent is None:
            continue
        sd = off(ent, -1)
        if sd is None or sd < L[0] or ent > L[-1] or sd not in d.index:
            continue
        if skip_bear and d.w_lag_tgt.get(sd, 0) == 0:
            continue
        if pd.isna(T.close.get(sd)) or T.close.get(sd, 0) <= 0:
            continue
        out.append(sd)
    return out


# ---------------------------------------------------------------- trade simulation
def simulate(T, sds, d, book, w_tgt, xmode, scen, tgt_ser=None):
    """Mỗi sd → lô; trả list dict với đường V/G theo ngày + đường vị thế ngày (pos). Một vị thế mở mỗi mã mỗi book.
    tgt_ser=None: mục tiêu = w_tgt × combined_nav (chính); khác: w_tgt × tgt_ser (ALLOC: NAV book ref)."""
    L = d.index; nav = d.combined_nav; trades = []; busy_until = None
    for sd in sorted(sds):
        i = L.get_loc(sd) + 1
        if i >= len(L) or (busy_until is not None and L[i] <= busy_until):
            continue
        e = L[i]
        if T.vol.iloc[i] <= 0 or pd.isna(T.open.iloc[i]):
            continue
        tgt = w_tgt * (nav.iloc[i] if tgt_ser is None else tgt_ser.iloc[i])
        cap = sum(PART * (T.liq.iloc[j] if not pd.isna(T.liq.iloc[j]) else 0.0) for j in range(i, min(i + FILL_DAYS, len(L))))
        if cap < MIN_FILL * tgt:
            continue
        filled = min(tgt, cap); epx = float(T.open.iloc[i]); sh = filled / epx; inv = filled * (1 + COST)
        cashG = 0.0                      # Σ proceeds_s / G(s), G = NAV/NAV(e)
        rem = sh; held = 0; exit_from = None; path = {}; stuck = False; closed = None; rows = []
        for j in range(i, len(L)):
            day = L[j]; G = nav.iloc[j] / nav.iloc[i]
            px = T.close.iloc[j]
            if day > T.DL:                                   # đã hủy niêm yết trên sàn gốc
                if rem > 0:
                    stuck = True
                    if scen == "U" and T.U_px is not None and T.U_date is not None and day >= T.U_date:
                        cashG += rem * T.U_px * (1 - COST) / G; rows.append((day, 0.0, 0.0, 0.0, rem * T.U_px)); rem = 0
                    elif scen == "Z" or T.U_px is None:
                        rows.append((day, 0.0, 0.0, 0.0, 0.0)); rem = 0       # Z: xoá sổ tại DL
                    # U trước U_date: vẫn kẹt, giữ giá khớp cuối
                if rem == 0:
                    path[day] = cashG; closed = day; break
                path[day] = cashG + rem * float(T.ind.Close.iloc[-1]) / G
                rows.append((day, rem, float(T.ind.Close.iloc[-1]), 0.0, 0.0))
                continue
            sold = 0.0
            if exit_from is not None and j >= exit_from and rem > 0 and T.vol.iloc[j] > 0:
                p_sell = T.open.iloc[j] if j == exit_from else px
                if pd.isna(p_sell):
                    p_sell = px
                # X-liq: bán ≤ 20% GTGD thực phiên đó (giá trị lô ≈ số CP điều chỉnh × giá điều chỉnh, bỏ qua CA giữa kỳ)
                q = rem if xmode == "eng" else min(rem, PART * T.val.iloc[j] / max(float(px), 1e-9))
                cashG += q * p_sell * (1 - COST) / G; rem -= q; sold = q * p_sell
            rows.append((day, max(rem, 0.0), float(px), filled if j == i else 0.0, sold))
            if rem <= 1e-9:
                path[day] = cashG; closed = day; break
            path[day] = cashG + rem * px / G
            if exit_from is None and j > i:
                held += 1
                r = px / epx - 1
                if held >= (BAL_HOLD if book == "BAL" else LAG_HOLD) or (book == "BAL" and r <= BAL_STOP):
                    exit_from = j + 1
        s = pd.Series(path) / inv
        trades.append(dict(tk=T.tk, book=book, sd=sd, entry=e, entry_px=epx, filled_vnd=filled, w=inv / nav.iloc[i],
                           target_vnd=tgt, exit_start=(L[exit_from] if exit_from is not None and exit_from < len(L) else None),
                           closed=closed, stuck=stuck, final_VG=float(s.iloc[-1]), VG=s,
                           pos=pd.DataFrame(rows, columns=["day", "rem", "mark", "buy", "sold"]).set_index("day")))
        busy_until = closed if closed is not None else L[-1]
    return trades


def overlay(d, trades):
    F = pd.Series(1.0, index=d.index)
    for t in trades:
        s = t["VG"].reindex(d.index).ffill()                 # sau đóng lô: cố định
        F *= (1 - t["w"] + t["w"] * s).fillna(1.0)
    return F


def overlay_alloc(d, trades):
    """Độ nhạy ALLOC (KHÔNG prereg): phantom là vị thế trong book ref; đóng góp vào NAV tổng theo tỉ trọng vốn thật
    cap_b/combined mỗi ngày (BEAR: cap_lag=0); vốn bị thay thế lẽ ra hưởng lợi suất book ref."""
    F = pd.Series(1.0, index=d.index)
    for t in trades:
        b = t["book"].lower()
        k = (d[f"cap_{b}"] / d.combined_nav / d[f"nav_{b}_ref"]).shift(1)
        rb = d[f"nav_{b}_ref"].pct_change()
        p = t["pos"].reindex(d.index)
        X = (p.rem * p.mark).fillna(0.0)
        Xp = X.shift(1).fillna(0.0)
        pnl = X + p.sold.fillna(0) - p.buy.fillna(0) - Xp
        cost = COST * (p.buy.fillna(0) + p.sold.fillna(0))
        on = p.rem.notna() | (Xp > 0)
        F *= (1 + (k * (pnl - cost - Xp * rb)).where(on, 0.0).fillna(0.0)).cumprod()
    return F


def collapse_exposure(T, trades):
    c0 = T.LT - pd.Timedelta(days=365); out = {}
    for t in trades:
        end = t["closed"] if t["closed"] is not None else T.DL
        a, b = max(t["entry"], c0), min(end, T.DL)
        if b > a:
            for y in range(a.year, b.year + 1):
                ya, yb = max(a, pd.Timestamp(f"{y}-01-01")), min(b, pd.Timestamp(f"{y}-12-31"))
                if yb > ya:
                    out[y] = out.get(y, 0.0) + (yb - ya).days / 365.0
    return out


def book_fraction(d, tx):
    """ALLOC: tỉ trọng 1 vị thế trong book ref = median_d[b_stocks_ref/nav_b_ref/n_b] (n_b như v2 book_counts)."""
    tx = tx.sort_values("ymd", kind="stable")
    tx = tx.assign(q=np.where(tx.action.str.startswith("buy"), 1.0, -1.0) * tx.shares)
    pos, by_day, n = {}, {k: g for k, g in tx.groupby("ymd")}, {"BAL": [], "LAG": []}
    for day in d.index:
        if day in by_day:
            for (b, t), q in by_day[day].groupby(["book", "ticker"]).q.sum().items():
                pos[(b, t)] = pos.get((b, t), 0.0) + q
        for b in n:
            n[b].append(sum(1 for (bb, t), q in pos.items() if bb == b and q > 1e-6))
    out = {}
    for b in n:
        nb = pd.Series(n[b], index=d.index); ok = nb >= 1
        out[b] = float((d[f"{b.lower()}_stocks_ref"] / d[f"nav_{b.lower()}_ref"] / nb.where(ok))[ok].median())
    return out


def main():
    out_dir = sys.argv[1]; legs = dict(a.split("=", 1) for a in sys.argv[2:])
    v2 = json.load(open(V2))["legs"]
    vni = pd.read_csv(f"{HERE}/data/bq_vni.csv", parse_dates=["time"]).set_index("time")
    cal_mkt = vni.index; infl = vni.Inflation_7; vmax = vni.D_RSI.rolling(60, min_periods=1).max()
    fin = load_fin()
    orig = pd.read_csv(f"{KBP}/delisted-big-vanished-prices-20261020.csv").set_index("ticker").exch_orig.to_dict()
    sa = pd.read_csv(f"{WIN}/stats_all.csv").set_index("ticker").exch2.to_dict()
    rows, trade_rows, meta = [], [], {}
    for label, path in legs.items():
        met, d, tx = load_ledger(path)
        base = calc_metrics(d.combined_nav)
        err = abs(base["cagr"] - float(met["cagr"]))
        if not (err <= 1e-9):
            raise SystemExit(f"{label}: không tái tạo METRIC cagr ({err})")
        yrs = (d.index[-1] - d.index[0]).days / 365.25
        w = v2[label]["w_median"]; pf = book_fraction(d, tx)
        meta[label] = dict(metric_err=err, base=base, w_median_v2=w, book_fraction_alloc=pf, years=yrs)
        tks = {tk: Tk(tk, cal_mkt, infl, vmax, d.index, orig.get(tk, sa.get(tk))) for tk in M + HVG + E}
        if "tickers" not in meta:
            meta["tickers"] = {tk: dict(orig=T.orig, LT=str(T.LT.date()), DL=str(T.DL.date()),
                                        U_date=str(T.U_date.date()) if T.U_date is not None else None,
                                        U_px=T.U_px, days_in_univ=int(T.u.sum())) for tk, T in tks.items()}
        runs = []
        for var in ["UB", "MID", "LIVE"]:
            sig = {}
            for tk, T in tks.items():
                fq = fin.get(tk)
                sig[(tk, "BAL")] = bal_signals(T, d, vni, fq, var)
                sig[(tk, "LAG")] = lag_events(T, d, fq, cal_mkt, var)
                sig[(tk, "LAG_nb")] = lag_events(T, d, fq, cal_mkt, var, skip_bear=False)
            for scen in ["Z", "U"]:
                for xm in ["liq", "eng"]:
                    tr = []
                    for (tk, book), sds in sig.items():
                        if book != "LAG_nb":
                            tr += simulate(tks[tk], sds, d, book, w[book], xm, scen)
                    runs.append((var, scen, xm, tr, overlay))
                tr = []                                       # ALLOC: chỉ X-liq, LAG vào cả lúc BEAR
                for (tk, book), sds in sig.items():
                    if book == "LAG":
                        continue
                    bk = "LAG" if book == "LAG_nb" else book
                    tr += simulate(tks[tk], sds, d, bk, pf[bk], "liq", scen, tgt_ser=d[f"nav_{bk.lower()}_ref"])
                runs.append((var + "_ALLOC", scen, "liq", tr, overlay_alloc))
        for var, scen, xm, tr, ovl in runs:
            for t in tr:
                trade_rows.append({k: v for k, v in t.items() if k not in ("VG", "pos")} | dict(leg=label, var=var, scen=scen, xmode=xm))
            for setname, S in [("M", M), ("M-KSA", [x for x in M if x != "KSA"]), ("HVG", HVG), ("E", E), ("M+E", M + E),
                              ("A", "ROS HAI AMD TGG TTB KLF SJF PSH NHP".split())]:
                for cfg, books in [("BAL", ["BAL"]), ("LAG", ["LAG"]), ("MIX", ["BAL", "LAG"])]:
                    sub = [t for t in tr if t["tk"] in S and t["book"] in books]
                    m = calc_metrics(d.combined_nav * ovl(d, sub))
                    ex = {}
                    for t in sub:
                        for y, v in collapse_exposure(tks[t["tk"]], [t]).items():
                            ex[y] = ex.get(y, 0) + v
                    rows.append(dict(leg=label, var=var, scen=scen, xmode=xm, set=setname, cfg=cfg,
                                     n_trades=len(sub), n_tk_traded=len({t["tk"] for t in sub}),
                                     n_stuck=sum(t["stuck"] for t in sub), tk_stuck=",".join(sorted({t["tk"] for t in sub if t["stuck"]})),
                                     tkyr_collapse=sum(ex.values()), lam_replay=sum(ex.values()) / yrs,
                                     d_cagr_pp=(m["cagr"] - base["cagr"]) * 100, d_sharpe=m["sharpe_252"] - base["sharpe_252"],
                                     d_maxdd_pp=(m["max_dd"] - base["max_dd"]) * 100,
                                     expo_by_year=json.dumps({int(k): round(v, 3) for k, v in sorted(ex.items())})))
        print(label, "done", json.dumps(pf), flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(out_dir, "out_replay_results.csv"), index=False)
    pd.DataFrame(trade_rows).to_csv(os.path.join(out_dir, "out_replay_trades.csv"), index=False)
    json.dump(meta, open(os.path.join(out_dir, "out_replay_meta.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
