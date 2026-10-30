"""Đo ảnh hưởng khung r/g_T mới lên consumer của dcf_valuation.py (job Taylor_20261030_041731, PREREG §3).
MÔ PHỎNG: gọi CHÍNH dcf_valuation.fair_value + classify_dcf; đổi khung bằng monkeypatch discount_rate /
terminal_growth_mode TRONG tiến trình này (không sửa file nào). Không gọi broker, không chạy bot.
Đầu vào bất biến: data/ (fetch_v2.py) + ../erp_domestic_20261030/data/snap_universe_pit_qe.csv + out_v2_erp_choice.csv.
Tái lập: $DNA_PYEXE impact_v2.py ⇒ out_imp_*.csv + run_imp_stdout.txt."""
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, "data")
out = lambda n: os.path.join(HERE, n)
WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WC)
_cwd = os.getcwd()
import dcf_valuation as Dv                       # import chdir sang WC — trả lại ngay
os.chdir(_cwd)
ASOF = "2026-10-29"; RF_C = 6.75; G_T_DOM = 0.055
IS_END = pd.Timestamp("2019-12-31")
DEEP = -1.0                                      # mike/bin/lag_dd_pack.py DCF_RICH_DEEP_MOS (cờ DD LAG)
LIVE_HOLD = ["DGC", "DRI", "HT1", "MBB", "MCH", "SCL", "TPB", "TV1", "VIB", "VPB"]   # dnse_raw 2026-10-29 positions (SpaceX ∪ ZaloPay)
PLAN_BUY = ["ACB", "FPT", "HDB", "HPG", "HT1", "MBB", "MCH", "SCL", "VNM", "VPB"]    # plan_*_2026-10-*.json side=buy
L = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s); L.append(s)


ch = pd.read_csv(out("out_v2_erp_choice.csv")).iloc[0]
ERP_LO, ERP_C, ERP_HI = float(ch.c_lo), float(ch.erp_code), float(ch.c_hi)
_DR, _TGM = Dv.discount_rate, Dv.terminal_growth_mode


def _cpi_gdp(asof):
    return _TGM(asof, "cpi_gdp_full", Dv.ERP, with_frac=True)


def make_frame(kind, erp=None):
    """-> (discount_rate, terminal_growth_mode) thay thế, cùng chữ ký với bản gốc."""
    if kind == "L":
        return _DR, _TGM
    if kind == "Ronly":                          # r mới, g_T vẫn cap theo lãi huy động hôm nay (cách đổi NGUY HIỂM)
        r = (RF_C + ERP_C) / 100
        def tgm(asof, mode=None, erp_=Dv.ERP, with_frac=False):
            g, fr = _cpi_gdp(asof); g = min(g, _DR(asof, Dv.ERP) - Dv.ERP / 100)
            return (g, fr) if with_frac else g
        return (lambda asof, erp_=Dv.ERP: r), tgm
    if kind == "N":
        r = (RF_C + erp) / 100
        def tgm(asof, mode=None, erp_=Dv.ERP, with_frac=False):
            g, fr = _cpi_gdp(asof); g = min(g, G_T_DOM)
            return (g, fr) if with_frac else g
        return (lambda asof, erp_=Dv.ERP: r), tgm
    raise ValueError(kind)


FRAMES = {"L": make_frame("L"), "Ronly": make_frame("Ronly"), "N_lo": make_frame("N", ERP_LO),
          "N_c": make_frame("N", ERP_C), "N_hi": make_frame("N", ERP_HI)}


def run_frame(name, items, finmap):
    """items: list of (ticker, date, price). -> DataFrame kết quả theo đúng classify_dcf."""
    Dv.discount_rate, Dv.terminal_growth_mode = FRAMES[name]
    rows = []
    try:
        for tk, d, px in items:
            f = finmap.get(tk)
            if f is None:
                rows.append(dict(ticker=tk, time=d, ok=False, reason="no_fin")); continue
            res = Dv.fair_value(tk, pd.Timestamp(d), price=px, fin=f)
            if not res["ok"]:
                rows.append(dict(ticker=tk, time=d, ok=False, reason=str(res.get("reason"))[:40])); continue
            mos = res.get("margin_of_safety")
            st, rb = Dv.classify_dcf(mos, res.get("sensitivity") or {}, px)
            rows.append(dict(ticker=tk, time=d, ok=True, price=px, fv=res["fair_value_ps"], mos=mos, status=st, robust=rb,
                             r=res["discount_rate"], g_T=res["g_terminal"], g_exp=res["g_explicit"]))
    finally:
        Dv.discount_rate, Dv.terminal_growth_mode = _DR, _TGM
    return pd.DataFrame(rows)


def summarize(df):
    ok = df[df.ok]
    return dict(n=len(df), n_ok=len(ok), pct_cheap=100 * (ok.status == "CHEAP").mean(),
                pct_cheap_robust=100 * ((ok.status == "CHEAP") & ok.robust).mean(),
                pct_rich_robust=100 * ((ok.status == "RICH") & ok.robust).mean(),
                pct_deep_rich=100 * (ok.mos < DEEP).mean(), n_deep_rich=int((ok.mos < DEEP).sum()),
                r=float(ok.r.median()) if len(ok) else np.nan, g_T=float(ok.g_T.median()) if len(ok) else np.nan)


def compare(base, other):
    m = base[base.ok].merge(other[other.ok], on=["ticker", "time"], suffixes=("_L", "_X"))
    return dict(fv_chg_med=100 * float((m.fv_X / m.fv_L - 1).median()),
                fv_chg_p10=100 * float((m.fv_X / m.fv_L - 1).quantile(0.1)),
                fv_chg_p90=100 * float((m.fv_X / m.fv_L - 1).quantile(0.9)),
                flip_cheap_to_rich=int(((m.status_L == "CHEAP") & (m.status_X == "RICH")).sum()),
                flip_rich_to_cheap=int(((m.status_L == "RICH") & (m.status_X == "CHEAP")).sum()),
                robust_changed=int((m.robust_L != m.robust_X).sum()),
                deep_on=int(((m.mos_L >= DEEP) & (m.mos_X < DEEP)).sum()),
                deep_off=int(((m.mos_L < DEEP) & (m.mos_X >= DEEP)).sum())), m


def spearman(a, b):
    return float(pd.Series(a).rank().corr(pd.Series(b).rank()))


def main():
    fin = pd.read_parquet(os.path.join(DATA, "fin_snapshot.parquet")); fin["time"] = pd.to_datetime(fin.time)
    finmap = {tk: g.reset_index(drop=True) for tk, g in fin.groupby("ticker")}
    snap = pd.read_csv(os.path.join(HERE, "..", "erp_domestic_20261030", "data", "snap_universe_pit_qe.csv"))
    snap = snap.dropna(subset=["Price"])
    P(f"[khung] ERP lo/code/hi = {ERP_LO:.4f}/{ERP_C:.2f}/{ERP_HI:.4f} ⇒ r N = {RF_C + ERP_LO:.4f}/{RF_C + ERP_C:.2f}/{RF_C + ERP_HI:.4f}%; g_T N = min(CPI5y+GDP15y, 5,5%)")

    # ---------------------------------------------------------------- 1. snapshot asof
    a = snap[snap.time == ASOF]
    items = [(r.ticker, ASOF, float(r.Price)) for r in a.itertuples()]
    RES = {k: run_frame(k, items, finmap) for k in FRAMES}
    rows = []
    for k, df in RES.items():
        s = summarize(df); c = compare(RES["L"], df)[0] if k != "L" else {}
        rows.append(dict(frame=k, **s, **c))
    T = pd.DataFrame(rows); T.round(4).to_csv(out("out_imp_asof_summary.csv"), index=False)
    P(f"[1] universe_pit asof {ASOF}: {len(items)} mã (gồm tài chính ⇒ NOT_COMPUTED)")
    P(T.round(2).to_string(index=False))
    nc = RES["L"][~RES["L"].ok].reason.value_counts()
    P("  NOT_COMPUTED (L): " + "; ".join(f"{k} {v}" for k, v in nc.items()))
    allm = None
    for k in ("Ronly", "N_lo", "N_c", "N_hi"):
        _, m = compare(RES["L"], RES[k]); m = m[["ticker", "mos_L", "status_L", "robust_L", "mos_X", "status_X", "robust_X"]]
        m.columns = ["ticker", "mos_L", "st_L", "rb_L", f"mos_{k}", f"st_{k}", f"rb_{k}"]
        allm = m if allm is None else allm.merge(m[["ticker", f"mos_{k}", f"st_{k}", f"rb_{k}"]], on="ticker")
    allm.round(4).to_csv(out("out_imp_asof_per_ticker.csv"), index=False)
    fl = allm[(allm.st_L != allm.st_N_c) | ((allm.mos_L < DEEP) != (allm.mos_N_c < DEEP))]
    P(f"  mã lật (L→N_c) status hoặc cờ RICH SÂU: {len(fl)}")
    if len(fl):
        P(fl[["ticker", "mos_L", "st_L", "mos_N_c", "st_N_c", "mos_N_lo", "mos_N_hi"]].round(3).to_string(index=False))

    # ---------------------------------------------------------------- 2. lịch sử quý: %cheap + IC
    cl = pd.read_csv(os.path.join(DATA, "close_qe.csv"))
    qd = sorted(d for d in snap.time.unique() if d != ASOF)
    piv = cl[cl.time.isin(qd)].pivot(index="time", columns="ticker", values="Close").reindex(qd)
    fwd1 = piv.shift(-1) / piv - 1; fwd4 = piv.shift(-4) / piv - 1
    hist_frames = ("L", "N_lo", "N_c", "N_hi")
    H = {}
    for k in hist_frames:
        it = [(r.ticker, r.time, float(r.Price)) for r in snap[snap.time.isin(qd)].itertuples()]
        H[k] = run_frame(k, it, finmap)
    rows, ics = [], []
    for d in qd:
        row = dict(time=d)
        base = H["L"][(H["L"].time == d) & H["L"].ok].set_index("ticker")
        for k in hist_frames:
            x = H[k][(H[k].time == d) & H[k].ok].set_index("ticker")
            row[f"pct_cheap_{k}"] = 100 * (x.status == "CHEAP").mean() if len(x) else np.nan
            row[f"pct_deep_{k}"] = 100 * (x.mos < DEEP).mean() if len(x) else np.nan
            row[f"r_{k}"] = float(x.r.median()) if len(x) else np.nan
            row[f"gT_{k}"] = float(x.g_T.median()) if len(x) else np.nan
            for hz, F in (("1q", fwd1), ("4q", fwd4)):
                fr = F.loc[d].reindex(x.index)
                ok = fr.notna() & x.mos.notna()
                row[f"ic{hz}_{k}"] = spearman(x.mos[ok], fr[ok]) if ok.sum() >= 20 else np.nan
                row[f"n{hz}_{k}"] = int(ok.sum())
            if k != "L":
                j = base.mos.index.intersection(x.index)
                row[f"rankcorr_L_{k}"] = spearman(base.mos[j], x.mos[j]) if len(j) >= 20 else np.nan
        rows.append(row)
    Hd = pd.DataFrame(rows); Hd.round(5).to_csv(out("out_imp_history_quarterly.csv"), index=False)
    Hd["t"] = pd.to_datetime(Hd.time)
    P(f"[2] lịch sử {qd[0]}→{qd[-1]} ({len(qd)} quý; IC cắt ngang Spearman MoS vs lợi suất Close điều chỉnh kỳ sau):")
    srows = []
    for k in hist_frames:
        for lab, msk in (("ALL", Hd.t.notna()), ("IS≤2019", Hd.t <= IS_END), ("OOS≥2020", Hd.t > IS_END)):
            h = Hd[msk]
            srows.append(dict(frame=k, period=lab, pct_cheap_mean=h[f"pct_cheap_{k}"].mean(), pct_deep_mean=h[f"pct_deep_{k}"].mean(),
                              ic4q_mean=h[f"ic4q_{k}"].mean(), ic4q_n=int(h[f"ic4q_{k}"].notna().sum()),
                              ic1q_mean=h[f"ic1q_{k}"].mean(), ic1q_n=int(h[f"ic1q_{k}"].notna().sum()),
                              ic4q_minus_L=(h[f"ic4q_{k}"] - h["ic4q_L"]).mean(), ic1q_minus_L=(h[f"ic1q_{k}"] - h["ic1q_L"]).mean(),
                              rankcorr_vs_L_min=h[f"rankcorr_L_{k}"].min() if k != "L" else np.nan,
                              rankcorr_vs_L_mean=h[f"rankcorr_L_{k}"].mean() if k != "L" else np.nan))
    S = pd.DataFrame(srows); S.round(4).to_csv(out("out_imp_history_summary.csv"), index=False)
    P(S.round(3).to_string(index=False))
    P("  %cheap theo năm (cuối Q4 hoặc quý cuối có):")
    yy = Hd.groupby(Hd.t.dt.year).tail(1)[["time", "pct_cheap_L", "pct_cheap_N_lo", "pct_cheap_N_c", "pct_cheap_N_hi", "r_L", "gT_L"]]
    P(yy.round(3).to_string(index=False))

    # ---------------------------------------------------------------- 3. live: nắm giữ + plan + custom30V
    c30 = pd.read_csv(os.path.join(WC, "data", "custom30v_8l_publish.csv"))
    c30 = c30[c30.rebal_date == c30.rebal_date.max()]
    osc = pd.read_csv(os.path.join(DATA, "oshares_check.csv"))
    px = osc[osc.time == ASOF].set_index("ticker").Price
    grp = {}
    for t in LIVE_HOLD: grp.setdefault(t, set()).add("nắm")
    for t in PLAN_BUY: grp.setdefault(t, set()).add("plan-buy")
    for t in c30.ticker: grp.setdefault(t, set()).add("c30V")
    it = [(t, ASOF, float(px[t])) for t in sorted(grp) if t in px.index and pd.notna(px[t])]
    LV = {k: run_frame(k, it, finmap) for k in ("L", "N_lo", "N_c", "N_hi")}
    lv = LV["L"][["ticker", "ok", "reason", "price", "mos", "status", "robust"]].rename(columns={"mos": "mos_L", "status": "st_L", "robust": "rb_L"})
    for k in ("N_lo", "N_c", "N_hi"):
        lv = lv.merge(LV[k][["ticker", "mos", "status", "robust"]].rename(columns={"mos": f"mos_{k}", "status": f"st_{k}", "robust": f"rb_{k}"}), on="ticker")
    lv.insert(1, "group", lv.ticker.map(lambda t: "+".join(sorted(grp[t]))))
    lv.round(4).to_csv(out("out_imp_live.csv"), index=False)
    P(f"[3] live (nắm giữ dnse_raw 2026-10-29 ∪ plan-buy 10/2026 ∪ custom30V rebal {c30.rebal_date.max()}): {len(lv)} mã có giá")
    P(lv[["ticker", "group", "reason", "mos_L", "st_L", "rb_L", "mos_N_c", "st_N_c", "rb_N_c", "mos_N_lo", "mos_N_hi"]].round(3).to_string(index=False))
    okl = lv[lv.ok]
    for k in ("N_lo", "N_c", "N_hi"):
        P(f"  {k}: lật status {int((okl.st_L != okl[f'st_{k}']).sum())}/{len(okl)}; đổi robust {int((okl.rb_L != okl[f'rb_{k}']).sum())}; "
          f"cờ RICH SÂU L {int((okl.mos_L < DEEP).sum())} → {int((okl[f'mos_{k}'] < DEEP).sum())}")

    # ---------------------------------------------------------------- 4. OShares lệch (gửi data-ops, không sửa)
    o = osc.pivot(index="ticker", columns="time", values=["Close", "Price", "OShares"])
    f = (o[("Close", "2026-06-30")] / o[("Price", "2026-06-30")])
    osr = o[("OShares", ASOF)] / o[("OShares", "2026-06-30")]
    chk = pd.DataFrame({"adj_factor_0630": f, "oshares_ratio": osr, "expected_ratio": 1 / f}).dropna()
    flag = chk[(chk.adj_factor_0630 < 0.93) & (chk.oshares_ratio < 0.95 / chk.adj_factor_0630)]
    flag.round(4).to_csv(out("out_imp_oshares_flags.csv"))
    P(f"[4] lệch OShares (hệ số điều chỉnh giá 30/06→29/10 < 0,93 mà OShares tăng < 95% mức kỳ vọng): {len(flag)} mã")
    P(flag.round(3).to_string())
    with open(out("run_imp_stdout.txt"), "w") as fh:
        fh.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
