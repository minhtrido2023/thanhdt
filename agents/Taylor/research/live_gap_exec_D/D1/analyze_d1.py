#!/usr/bin/env python3
"""Luồng D1 (job Taylor_20261112_151837 → resume Taylor_20261112_162001): sửa GĐ3 theo quant-skeptic.
Usage: analyze_d1.py <ledger_P0_off.csv> <ledger_P0_dep1m.csv>
(a) P(thắng 12T) ở HAI đầu dải lãi nhàn rỗi (pin0% / pin1M), có/không trừ 1,5pp/năm.
(b) chính sách "tiết kiệm khi DT5G∈{CRISIS,BEAR}": engine và chính sách CÙNG ledger (cùng quy ước lãi nhàn rỗi),
    chân tiết kiệm hưởng lãi kỳ hạn 1T (idle_rate_proxy tier dep1m: số thật 2019-02+, trước đó DỰNG LẠI, không PIT),
    trễ T+1, phí 0,1%/lần đổi; placebo KHỐI THÁNG trong năm (≥500).
(c) CI P(thắng) theo N_eff: Wilson + Clopper–Pearson (n_eff 9 và 12; và đếm thật cửa sổ không chồng), bootstrap khối 12/36 tháng.
(f) sizing w·engine + (1−w)·tiết kiệm 1T (thay 12T cân lại hằng ngày — không thực hiện được).
Hàm dùng chung import nguyên từ GĐ3 analyze.py. Seed 20261112."""
import sys, os, json
import numpy as np, pandas as pd
from scipy import stats

W = "/home/trido/thanhdt/WorkingClaude"
G3 = W + "/mike/agents/Taylor/research/live_gap_phase3_20261112"
SB = W + "/mike/agents/Taylor/research/live_gap_exec_D/sb_D"
sys.path.insert(0, SB)
import idle_rate_proxy as IRP  # noqa: E402  (bản sb_D có tier dep1m — PHẢI import trước khi GĐ3 chèn W vào sys.path)
assert "dep1m" in IRP.TIERS, IRP.__file__
sys.path.insert(0, G3)
import analyze as A  # noqa: E402  (GĐ3)
from deposit_rate_vn import deposit_events_df  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(20261112)
A.RNG = RNG
HAIRCUT = 0.015


def dep1m_full_daily(start, end):
    """Lãi 1T theo NGÀY LỊCH, quy tắc PIT giống engine (mốc tháng T dùng từ đầu tháng T+1)."""
    t = IRP.monthly_table()[["dep1m_pct", "dep1m_src"]].dropna(subset=["dep1m_pct"])
    df = pd.DataFrame({"time": pd.to_datetime(t.index + "-01") + pd.offsets.MonthBegin(1),
                       "dep1m": t.dep1m_pct.values, "src": t.dep1m_src.values})
    return df


def haircut(nav):
    yrs = (nav.index - nav.index[0]).days / 365.25
    return nav * (1 - HAIRCUT) ** yrs


def wilson(p, n, z=1.6449):
    c = p + z * z / (2 * n); h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)); d = 1 + z * z / n
    return (c - h) / d, (c + h) / d


def clopper(x, n, a=0.10):
    lo = stats.beta.ppf(a / 2, x, n - x + 1) if x > 0 else 0.0
    hi = stats.beta.ppf(1 - a / 2, x + 1, n - x) if x < n else 1.0
    return lo, hi


def nonoverlap_counts(ex):
    """Mỗi offset tháng m∈1..12: cửa sổ 12T bắt đầu phiên đầu tiên của tháng m mỗi năm ⇒ không chồng."""
    rows = []
    s = ex.exc.dropna()
    first = s.groupby(s.index.to_period("M")).head(1)
    for m in range(1, 13):
        x = first[first.index.month == m]
        rows.append(dict(month=m, n=len(x), k=int((x > 0).sum())))
    return pd.DataFrame(rows)


def month_block_perm(mask, idx):
    """Hoán vị NGUYÊN KHỐI THÁNG trong từng năm (giữ tổng độ dài năm và mẫu trong-tháng)."""
    s = pd.Series(np.asarray(mask, bool), index=idx)
    out = []
    for _, g in s.groupby(idx.year):
        blocks = [b.values for _, b in g.groupby(g.index.month)]
        order = RNG.permutation(len(blocks))
        out.append(np.concatenate([blocks[i] for i in order]))
    return np.concatenate(out)


def policy_eval(name, nav, savS, off, nplac):
    pn, nsw = A.policy_nav(nav, savS, off)
    c, s, d = A.perf(pn); ce, se, de = A.perf(nav)
    P = np.array([A.perf(A.policy_nav(nav, savS, month_block_perm(off, nav.index))[0]) for _ in range(nplac)])
    return dict(policy=name, off_frac=float(np.mean(off)), n_switch=nsw, eng_cagr=ce, eng_sharpe=se, eng_maxdd=de,
                cagr=c, sharpe=s, maxdd=d, d_cagr_pp=100 * (c - ce), d_sharpe=s - se, d_maxdd_pp=100 * (d - de),
                plac_n=nplac, plac_cagr_p50=np.median(P[:, 0]), plac_cagr_p90=np.quantile(P[:, 0], .9),
                rank_cagr=float(np.mean(P[:, 0] < c)), plac_dd_p50=np.median(P[:, 2]), rank_dd=float(np.mean(P[:, 2] < d)),
                plac_sharpe_p50=np.median(P[:, 1]), rank_sharpe=float(np.mean(P[:, 1] < s)))


def main(p_off, p_dep):
    legs = {"pin0": A.load_ledger(p_off), "pin1M": A.load_ledger(p_dep)}
    i0, i1 = legs["pin0"].index[0], legs["pin0"].index[-1]
    assert legs["pin1M"].index.equals(legs["pin0"].index)
    assert (legs["pin1M"].state.values == legs["pin0"].state.values).all(), "state DT5G phải trùng giữa 2 chân"
    sav12 = A.savings_index(deposit_events_df(), i0 - pd.Timedelta(days=5), i1 + pd.Timedelta(days=5), "deposit_rate")
    d1 = dep1m_full_daily(i0, i1)
    savS = A.savings_index(d1, i0 - pd.Timedelta(days=5), i1 + pd.Timedelta(days=5), "dep1m")
    res = {"ledgers": {"pin0": p_off, "pin1M": p_dep},
           "dep1m_src_counts_2014_2026": d1[(d1.time >= "2014-01-01") & (d1.time <= "2026-07-01")].src.value_counts().to_dict()}
    for k, l in legs.items():
        c, s, d = A.perf(l.combined_nav); res[f"perf_{k}"] = dict(cagr=c, sharpe=s, maxdd=d)

    # ---- (a)+(c) P(thắng 12T)
    R, Y, C = [], [], []
    for leg, l in legs.items():
        for hc in (False, True):
            nav = haircut(l.combined_nav) if hc else l.combined_nav
            for lab, sv in (("hurdle12T", sav12), ("hurdle1T", savS)):
                ex = A.excess_at(nav, sv, nav.index[1:], 12).dropna()
                ex["era"] = [A.era_of(t) for t in ex.index]
                for grp, g in [("ALL", ex)] + [(e, ex[ex.era == e]) for e in ("IS", "BUF", "OOS")]:
                    mo = g.exc.groupby(g.index.to_period("M")).apply(lambda x: (x > 0).mean())
                    p = (g.exc > 0).mean()
                    row = dict(leg=leg, haircut_1p5=hc, label=lab, era=grp, n_days=len(g), n_months=len(mo), p_win=p,
                               exc_med=g.exc.median(), med_loss=g.exc[g.exc <= 0].median())
                    for b in (12, 36):
                        lo, hi = A.block_ci(mo.values, b, 2000); row[f"boot{b}_lo"], row[f"boot{b}_hi"] = lo, hi
                    if grp == "ALL":
                        for ne in (9, 12):
                            row[f"wilson_n{ne}_lo"], row[f"wilson_n{ne}_hi"] = wilson(p, ne)
                            row[f"cp_n{ne}_lo"], row[f"cp_n{ne}_hi"] = clopper(p * ne, ne)
                        nc = nonoverlap_counts(ex); nc["leg"], nc["haircut_1p5"], nc["label"] = leg, hc, lab; C.append(nc)
                        jan = nc[nc.month == 1].iloc[0]
                        row["jan_k"], row["jan_n"] = int(jan.k), int(jan.n)
                        row["jan_cp_lo"], row["jan_cp_hi"] = clopper(jan.k, jan.n)
                        row["offsets_p_min"], row["offsets_p_max"] = (nc.k / nc.n).min(), (nc.k / nc.n).max()
                    R.append(row)
                for y, g in ex.groupby(ex.index.year):
                    Y.append(dict(leg=leg, haircut_1p5=hc, label=lab, year=y, n_days=len(g), p_win=(g.exc > 0).mean(), exc_med=g.exc.median()))
    pd.DataFrame(R).to_csv(os.path.join(OUT, "d1ac_pwin.csv"), index=False)
    pd.DataFrame(Y).to_csv(os.path.join(OUT, "d1a_pwin_by_year.csv"), index=False)
    pd.concat(C).to_csv(os.path.join(OUT, "d1c_nonoverlap_offsets.csv"), index=False)

    # ---- (b) chính sách, hai chân cùng quy ước
    P = []
    for leg, l in legs.items():
        off = (l.state <= 2).values
        P.append(dict(convention=leg, savings="dep1m_1T", **policy_eval("DT5G_CRISIS_BEAR_to_savings1T", l.combined_nav, savS, off, 500)))
        # đoạn 2019-03+ (lãi 1T là số thật, PIT) — báo riêng
        m = l.index >= "2019-03-01"
        P.append(dict(convention=leg, savings="dep1m_1T_2019-03+", **policy_eval("DT5G_CRISIS_BEAR_to_savings1T", l.combined_nav[m], savS, off[m], 500)))
    pd.DataFrame(P).to_csv(os.path.join(OUT, "d1b_policy.csv"), index=False)

    # ---- (f) sizing với tiết kiệm 1T (1−w), cân lại hằng ngày
    S = []
    for leg, l in legs.items():
        n = l.combined_nav; ix = n.index; r_eng = n.pct_change().fillna(0).values
        N = len(ix); b = 252; nb = int(np.ceil(N / b)); yrs = (ix[-1] - ix[0]).days / 365.25
        boots = [np.concatenate([(np.arange(k, k + b) % N) for k in RNG.integers(0, N, nb)])[:N] for _ in range(1000)]
        for sname, sv in (("sav1T", savS), ("sav12T_ref", sav12)):
            v = sv.reindex(ix).values; r_sav = np.r_[0, v[1:] / v[:-1] - 1]
            for w in (0.3, 0.4, 0.5, 0.6, 0.8, 1.0):
                r = w * r_eng + (1 - w) * r_sav
                nv = pd.Series(np.cumprod(1 + r), index=ix); c, s, d = A.perf(nv)
                dd = [(lambda x: (x / np.maximum.accumulate(x) - 1).min())(np.cumprod(1 + r[bi])) for bi in boots]
                cg = [np.cumprod(1 + r[bi])[-1] ** (1 / yrs) - 1 for bi in boots]
                ex = A.excess_at(nv, sav12, ix[1:], 12).dropna()
                S.append(dict(leg=leg, savings_leg=sname, w=w, cagr=c, sharpe=s, maxdd=d, boot_cagr_p5=np.quantile(cg, .05),
                              boot_maxdd_p5=np.quantile(dd, .05), p_win12_vs12T=(ex.exc > 0).mean(), med_loss12=ex.exc[ex.exc <= 0].median()))
    pd.DataFrame(S).to_csv(os.path.join(OUT, "d1f_sizing.csv"), index=False)
    json.dump(res, open(os.path.join(OUT, "d1_summary.json"), "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
