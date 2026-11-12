#!/usr/bin/env python3
"""GĐ2-A bảng đơn biến + placebo + H1–H5 (job Taylor_20261112_122858). Đọc panel.parquet.
Đơn vị kiểm định = SỰ KIỆN ĐỘC LẬP (event_id: cùng book+mã, vào lại ≤5 phiên sau lần thoát = 1 sự kiện;
excess sự kiện = trung bình excess các deal, đặc trưng = deal đầu tiên).
Thống kê chính: Spearman rho(feature, excess) — Pearson trên hạng toàn mẫu.
p chính = block bootstrap theo THÁNG của sig_date (B=2000, cluster-robust theo thời gian).
p phụ  = hoán vị excess TRONG NĂM (B=1000) — khắt khe: đặc trưng gần hằng trong năm (vĩ mô) ⇒ p≈1.
Họ FDR = mọi đặc trưng × 2 book, tách IS(2014–19) / OOS(2020+); BH q<0,10. Qua = q<0,10 cả IS và OOS, cùng dấu.
Placebo: hoán vị excess trong năm, chạy lại toàn pipeline (bootstrap B=500) R=10 lần, đếm số "qua FDR".
Chạy: /home/trido/thanhdt/wc_venv/bin/python analyze.py
"""
import os
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20261112
FEATS = ["rating8l", "comp_v3", "ey", "cfy", "psy", "PE", "PB", "PCF", "pe_rel5y", "pb_z5y", "ROE_Min5Y", "ROIC5Y", "FSCORE",
         "cfoa_pos", "sue", "np_yoy", "rev_yoy", "mom_200", "D_RSI", "D_CMF", "dd52", "rvol20", "adv_pct", "log_adv20",
         "dt5g_state", "dt5g_cand_clock", "vni_dd52", "breadth", "breadth_terc", "radar_score", "vni_pe", "hurdle_pct",
         "hurdle_chg3m", "spread_ey_hurdle", "spread_mkt_hurdle", "cpi_yoy", "refi", "refi_chg6m", "vix", "spx_dd_1y",
         "comm_chg3m", "ic_mom_sec12", "ic_pe_sec12", "lag_edge_pct", "lag_edge_mean12"]
MIN_N = 30

def events(D):
    D = D.sort_values("first_fill")
    agg = {f: "first" for f in FEATS}
    agg.update(excess_pp="mean", ret_pct="mean", hit="mean", sig_date="first", year="first", era="first", book="first",
               ticker="first", hurdle_accr_pct="mean", hold_sessions="mean")
    E = D.groupby("event_id").agg(agg).reset_index()
    E["hit"] = (E.excess_pp > 0).astype(float)
    E["month"] = E.sig_date.dt.to_period("M").astype(str)
    return E

def rank(x):
    return pd.Series(x).rank().values

def corr_rows(X, y):
    """Pearson theo hàng: X (B,n), y (B,n)."""
    Xc = X - X.mean(1, keepdims=True); yc = y - y.mean(1, keepdims=True)
    den = np.sqrt((Xc ** 2).sum(1) * (yc ** 2).sum(1))
    return np.where(den > 0, (Xc * yc).sum(1) / np.where(den > 0, den, 1), np.nan)

def boot_p(x, y, months, B, rng):
    rx, ry = rank(x), rank(y)
    rho = np.corrcoef(rx, ry)[0, 1]
    um = np.unique(months); idx = {m: np.where(months == m)[0] for m in um}
    draws = rng.integers(0, len(um), size=(B, len(um)))
    stats = np.empty(B)
    for b in range(B):
        ii = np.concatenate([idx[um[k]] for k in draws[b]])
        a, c = rx[ii], ry[ii]
        sa, sc = a.std(), c.std()
        stats[b] = np.nan if sa == 0 or sc == 0 else np.corrcoef(a, c)[0, 1]
    stats = stats[np.isfinite(stats)]
    p = 2 * min((stats <= 0).mean(), (stats >= 0).mean())
    return rho, max(p, 1.0 / len(stats)), np.percentile(stats, [2.5, 97.5])

def perm_year_p(x, y, years, B, rng):
    rx, ry = rank(x), rank(y)
    rho = np.corrcoef(rx, ry)[0, 1]
    groups = [np.where(years == yv)[0] for yv in np.unique(years)]
    Y = np.tile(ry, (B, 1))
    for g in groups:
        if len(g) > 1:
            Y[:, g] = rng.permuted(np.tile(ry[g], (B, 1)), axis=1)
    st = corr_rows(np.tile(rx, (B, 1)), Y)
    return (np.sum(np.abs(st) >= abs(rho) - 1e-12) + 1) / (B + 1)

def bh(p):
    p = np.asarray(p, float); q = np.full(len(p), np.nan); ok = np.isfinite(p)
    pv = p[ok]; n = len(pv)
    if n == 0: return q
    o = np.argsort(pv); r = pv[o] * n / (np.arange(n) + 1)
    r = np.minimum.accumulate(r[::-1])[::-1]
    qq = np.empty(n); qq[o] = np.minimum(r, 1); q[ok] = qq
    return q

def univariate(E, B, rng, with_perm=True):
    rows = []
    for era in ("IS", "OOS"):
        for book in ("BAL", "LAG"):
            S = E[(E.era == era) & (E.book == book)]
            for f in FEATS:
                s = S[[f, "excess_pp", "month", "year"]].dropna()
                r = dict(era=era, book=book, feature=f, n_events=len(s), n_months=s.month.nunique())
                if len(s) >= MIN_N and s[f].nunique() >= 3:
                    rho, p, ci = boot_p(s[f].values, s.excess_pp.values, s.month.values, B, rng)
                    r.update(rho=rho, p_boot=p, ci_lo=ci[0], ci_hi=ci[1])
                    if with_perm:
                        r["p_perm_year"] = perm_year_p(s[f].values, s.excess_pp.values, s.year.values, 1000, rng)
                    lo, hi = s[f].quantile([0.2, 0.8])
                    bot, top = s[s[f] <= lo], s[s[f] >= hi]
                    r.update(hit_q1=(bot.excess_pp > 0).mean(), hit_q5=(top.excess_pp > 0).mean(),
                             med_q1=bot.excess_pp.median(), med_q5=top.excess_pp.median())
                rows.append(r)
    U = pd.DataFrame(rows)
    for era in ("IS", "OOS"):
        m = U.era == era
        U.loc[m, "q_bh"] = bh(U.loc[m, "p_boot"].values)
    return U

def deciles(E):
    out = []
    for era in ("IS", "OOS"):
        for book in ("BAL", "LAG"):
            S = E[(E.era == era) & (E.book == book)]
            for f in FEATS:
                s = S[[f, "excess_pp"]].dropna()
                if len(s) < MIN_N or s[f].nunique() < 3: continue
                k = min(10, s[f].nunique())
                try: s["bin"] = pd.qcut(s[f].rank(method="first"), k, labels=False)
                except ValueError: continue
                g = s.groupby("bin").agg(lo=(f, "min"), hi=(f, "max"), n=("excess_pp", "size"),
                                         hit=("excess_pp", lambda v: (v > 0).mean()), med_excess=("excess_pp", "median")).reset_index()
                g.insert(0, "feature", f); g.insert(0, "book", book); g.insert(0, "era", era)
                out.append(g)
    return pd.concat(out, ignore_index=True)

def placebo(E, R, rng):
    cnt = []
    for r in range(R):
        P = E.copy()
        for y, idx in P.groupby("year").groups.items():
            P.loc[idx, "excess_pp"] = rng.permutation(P.loc[idx, "excess_pp"].values)
        U = univariate(P, 500, rng, with_perm=False)
        cnt.append(dict(rep=r, n_q10_IS=int((U[U.era == "IS"].q_bh < 0.10).sum()), n_q10_OOS=int((U[U.era == "OOS"].q_bh < 0.10).sum()),
                        n_pass_both=int(passes(U).shape[0])))
    return pd.DataFrame(cnt)

def passes(U):
    a = U[U.era == "IS"].set_index(["book", "feature"]); b = U[U.era == "OOS"].set_index(["book", "feature"])
    j = a.join(b, lsuffix="_IS", rsuffix="_OOS", how="inner")
    return j[(j.q_bh_IS < 0.10) & (j.q_bh_OOS < 0.10) & (np.sign(j.rho_IS) == np.sign(j.rho_OOS))]

# ----------------------------------------------------------------- H1-H5 (khai trước: đúng 5 phép thử, ngưỡng cố định trước khi nhìn OOS)
def diff_test(S, mask, B, rng):
    """So excess sự kiện trong nhóm mask vs ngoài: Δ trung bình, Δ trung vị, Δ hit; p block-bootstrap tháng cho Δ trung bình."""
    a, b = S[mask], S[~mask]
    r = dict(n_in=len(a), n_out=len(b), mean_in=a.excess_pp.mean(), mean_out=b.excess_pp.mean(),
             med_in=a.excess_pp.median(), med_out=b.excess_pp.median(), hit_in=(a.excess_pp > 0).mean(), hit_out=(b.excess_pp > 0).mean())
    r["d_mean"] = r["mean_in"] - r["mean_out"]
    if len(a) < 10 or len(b) < 10:
        r["p_boot"] = np.nan; return r
    um = S.month.unique(); idx = {m: np.where(S.month.values == m)[0] for m in um}
    ex = S.excess_pp.values; mk = mask.values; st = []
    for _ in range(B):
        ii = np.concatenate([idx[um[k]] for k in rng.integers(0, len(um), len(um))])
        e, m = ex[ii], mk[ii]
        if m.sum() and (~m).sum(): st.append(e[m].mean() - e[~m].mean())
    st = np.array(st); r["p_boot"] = max(2 * min((st <= 0).mean(), (st >= 0).mean()), 1 / len(st))
    return r

def level_test(S, mask, B, rng):
    """Nhóm mask có excess TB < 0 không (thua tiết kiệm)? p block-bootstrap tháng cho trung bình nhóm."""
    a = S[mask]; r = dict(n_in=len(a), mean_in=a.excess_pp.mean(), med_in=a.excess_pp.median(), hit_in=(a.excess_pp > 0).mean())
    if len(a) < 10: r["p_boot"] = np.nan; return r
    um = a.month.unique(); idx = {m: np.where(a.month.values == m)[0] for m in um}; ex = a.excess_pp.values
    st = np.array([ex[np.concatenate([idx[um[k]] for k in rng.integers(0, len(um), len(um))])].mean() for _ in range(B)])
    r["p_boot"] = max(2 * min((st <= 0).mean(), (st >= 0).mean()), 1 / len(st)); return r

def hypotheses(E, B, rng):
    rows = []
    lagIS = E[(E.book == "LAG") & (E.era == "IS")]
    sue_cut = lagIS.sue.quantile(2 / 3)                        # ngưỡng lấy từ IS, áp nguyên sang OOS
    for era in ("IS", "OOS"):
        L = E[(E.book == "LAG") & (E.era == era)].dropna(subset=["sue", "ey_pct" if "ey_pct" in E else "ey"])
        m = (L.sue >= sue_cut) & (L.ey_pct >= 2 / 3)
        rows.append(dict(H="H1 LAG: SUE≥P67(IS) & ey_pct≥2/3 vs phần còn lại", era=era, **diff_test(L, m, B, rng)))
        Bk = E[(E.book == "BAL") & (E.era == era)].dropna(subset=["spread_ey_hurdle"])
        rows.append(dict(H="H2 BAL: ey−hurdle > 0 vs ≤ 0", era=era, **diff_test(Bk, Bk.spread_ey_hurdle > 0, B, rng)))
        C = E[(E.era == era) & E.comm_chg3m.notna() & (E.comm_key != "oni")]
        rows.append(dict(H="H3 deal ngành hàng hoá: giá HH 3T tăng vs giảm (BAL+LAG)", era=era, **diff_test(C, C.comm_chg3m > 0, B, rng)))
        L2 = E[(E.book == "LAG") & (E.era == era)].dropna(subset=["lag_edge_pct"])
        rows.append(dict(H="H4 LAG vào khi LAG edge pctile<20: excess TB<0?", era=era, **level_test(L2, L2.lag_edge_pct < 20, B, rng)))
        rows.append(dict(H="H4b (đối chứng) LAG edge<20 vs ≥20", era=era, **diff_test(L2, L2.lag_edge_pct < 20, B, rng)))
        A = E[(E.era == era)].dropna(subset=["hurdle_chg3m"])
        rows.append(dict(H="H5 BAL+LAG: hurdle 3T TĂNG (>0) vs không", era=era, **diff_test(A, A.hurdle_chg3m > 0, B, rng)))
    return pd.DataFrame(rows), sue_cut

def main():
    rng = np.random.default_rng(SEED)
    D = pd.read_parquet(os.path.join(HERE, "panel.parquet"))
    FEATS_X = FEATS + ["ey_pct", "comm_key"]
    eng = D[(D.src == "engine") & D.labelled].copy()
    agg_extra = eng.groupby("event_id").agg(ey_pct=("ey_pct", "first"), comm_key=("comm_key", "first"))
    E = events(eng).merge(agg_extra, on="event_id", how="left")
    E.to_csv(os.path.join(HERE, "events.csv"), index=False)
    U = univariate(E, 2000, rng); U.to_csv(os.path.join(HERE, "univariate.csv"), index=False)
    deciles(E).to_csv(os.path.join(HERE, "deciles.csv"), index=False)
    P = passes(U); P.to_csv(os.path.join(HERE, "univariate_pass.csv"))
    H, sue_cut = hypotheses(E, 2000, rng); H.to_csv(os.path.join(HERE, "hypotheses.csv"), index=False)
    PL = placebo(E, 10, rng); PL.to_csv(os.path.join(HERE, "placebo.csv"), index=False)
    print("events by book/era:\n", E.groupby(["book", "era"]).size())
    print("pass both:", len(P)); print(P[["rho_IS", "q_bh_IS", "rho_OOS", "q_bh_OOS", "n_events_IS", "n_events_OOS"]].round(4).to_string())
    print("placebo:\n", PL.describe().round(2).to_string())
    print("sue_cut", sue_cut); print(H.round(3).to_string())

if __name__ == "__main__":
    main()
