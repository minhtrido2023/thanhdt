#!/usr/bin/env python3
"""Luồng D2 (job Taylor_20261112_151837): GĐ2B analyze.py sửa theo quant-skeptic. KHÔNG sửa file GĐ2B gốc; đọc panel GĐ2B.
Thay đổi so với GĐ2B:
 (a) dt5g_cand_clock (sai: state_raw≠state) ⇒ dtc_k (streak candidate DT 4-gate, D2/dt_clock_daily.csv, giá trị tại sig_date = phiên trước fill)
     + dtc_active (0/1). dtc_progress = k/need chỉ báo mô tả (tương quan ~1 với k, không thêm vào họ).
 (b) đặc trưng có đúng 2 giá trị ⇒ POINT-BISERIAL (Pearson trên giá trị thô 0/1 × excess thô), báo kèm Spearman; ≥3 giá trị ⇒ Spearman như cũ.
     Hằng (1 giá trị) hoặc n<30 ⇒ không kiểm (liệt kê). Họ FDR = mọi ô kiểm được, tách IS/OOS; BH q<0,10; qua = q<0,10 cả hai era cùng dấu.
 (c) p = block bootstrap THÁNG (B=2000), vector hoá bằng trọng số multinomial theo tháng (tương đương lấy lại tháng có hoàn lại,
     thống kê = tương quan có trọng số trên hạng/giá trị GỐC như GĐ2B).
     Placebo KHỐI THÁNG: trong mỗi năm, hoán vị THỨ TỰ các khối tháng của vector excess (giữ nguyên khối, giữ cụm), gán lại theo vị trí
     sự kiện đã sắp theo sig_date ⇒ phá liên kết đặc trưng–kết cục, giữ tương quan trong-tháng. R=500, B=500 mỗi lần.
     MDE theo LUẬT QUYẾT ĐỊNH THẬT: cấy ρ vào 1 đặc trưng ở CẢ ô IS và OOS (cùng book, cùng dấu), p cấy + (m−1) p THẬT còn lại của era đó
     ⇒ BH q<0,10 ở IS VÀ OOS. nsim=400. Báo ρ đạt lực 80%.
 (d) phí native: excess_native_pp.  (e) tập liqz_adv100.  H5: episodes_d2.py.
Chạy: /home/trido/thanhdt/wc_venv/bin/python analyze_d2.py [tag]"""
import os, sys, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
G2 = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/live_gap_phase2b_20261112"
SEED = 20261112; MIN_N = 30; QCUT = 0.10
FEATS = ["rating8l", "comp_v3", "ey", "cfy", "psy", "PE", "PB", "PCF", "pe_rel5y", "pb_z5y", "ROE_Min5Y", "ROIC5Y", "FSCORE",
         "cfoa_pos", "sue", "np_yoy", "rev_yoy", "mom_200", "D_RSI", "D_CMF", "dd52", "rvol20", "adv_pct", "log_adv20",
         "dt5g_state", "dtc_k", "dtc_active", "vni_dd52", "breadth", "breadth_terc", "radar_score", "vni_pe", "hurdle_pct",
         "hurdle_chg3m", "spread_ey_hurdle", "spread_mkt_hurdle", "cpi_yoy", "refi", "refi_chg6m", "vix", "spx_dd_1y",
         "comm_chg3m", "ic_mom_sec12", "ic_pe_sec12", "lag_edge_pct", "lag_edge_mean12"]
HURDLE_DEP = {"hurdle_pct", "hurdle_chg3m", "spread_ey_hurdle", "spread_mkt_hurdle", "radar_score"}
CELLS = [(e, b) for e in ("IS", "OOS") for b in ("BAL", "LAG")]

def load(mode, filt, native):
    D = pd.read_parquet(f"{G2}/panel_{mode}.parquet")
    if filt == "adv": D = D[(D.src != "engine") | (D.adv_pct <= 100)]
    C = pd.read_csv(os.path.join(HERE, "dt_clock_daily.csv"), parse_dates=["time"])
    D = D.drop(columns=["dt5g_cand_clock"]).merge(C[["time", "k", "active", "progress"]].rename(
        columns={"time": "sig_date", "k": "dtc_k", "active": "dtc_active", "progress": "dtc_progress"}), on="sig_date", how="left")
    eng = D[(D.src == "engine") & D.labelled].copy()
    if native: eng["excess_pp"] = eng.excess_native_pp
    eng = eng.sort_values("first_fill")
    agg = {f: "first" for f in FEATS + ["dtc_progress", "ey_pct", "comm_key"]}
    agg.update(excess_pp="mean", sig_date="first", year="first", era="first", book="first", ticker="first")
    E = eng.groupby("event_id").agg(agg).reset_index()
    E["month"] = E.sig_date.dt.to_period("M").astype(str)
    return E.sort_values("sig_date").reset_index(drop=True)

def rank(v): return pd.Series(v).rank().values

class Cell:
    """Ô (era, book): chuẩn bị ma trận trọng số bootstrap tháng dùng chung cho mọi đặc trưng."""
    def __init__(self, S, B, rng):
        self.S = S; self.months = S.month.values; um, inv = np.unique(self.months, return_inverse=True)
        self.inv = inv; self.nm = len(um)
        cnt = rng.multinomial(self.nm, np.full(self.nm, 1 / self.nm), size=B)          # (B, nm) số lần tháng được rút
        self.W = cnt[:, inv].astype(float)                                              # (B, n)
    def stat(self, x, y, binary):
        ok = np.isfinite(x) & np.isfinite(y)
        x, y = x[ok], y[ok]
        if ok.sum() < MIN_N or len(np.unique(x)) < 2: return None
        if binary: a, c = x.astype(float), y.astype(float)                             # point-biserial = Pearson thô
        else: a, c = rank(x), rank(y)                                                   # Spearman
        r0 = np.corrcoef(a, c)[0, 1]
        Wk = self.W[:, ok]; s0 = Wk.sum(1)
        mx = Wk @ a / s0; my = Wk @ c / s0
        sxx = Wk @ (a * a) / s0 - mx ** 2; syy = Wk @ (c * c) / s0 - my ** 2; sxy = Wk @ (a * c) / s0 - mx * my
        den = np.sqrt(np.clip(sxx, 0, None) * np.clip(syy, 0, None)); st = np.where(den > 0, sxy / np.where(den > 0, den, 1), np.nan)
        st = st[np.isfinite(st)]
        p = max(2 * min((st <= 0).mean(), (st >= 0).mean()), 1 / len(st))
        return r0, p, np.percentile(st, [2.5, 97.5]), int(ok.sum()), int(len(np.unique(self.months[ok])))

def bh(p):
    p = np.asarray(p, float); q = np.full(len(p), np.nan); ok = np.isfinite(p); pv = p[ok]; n = len(pv)
    if n == 0: return q
    o = np.argsort(pv); r = pv[o] * n / (np.arange(n) + 1); r = np.minimum.accumulate(r[::-1])[::-1]
    qq = np.empty(n); qq[o] = np.minimum(r, 1); q[ok] = qq; return q

def univariate(E, B, rng, ycol="excess_pp"):
    rows = []
    for era, book in CELLS:
        S = E[(E.era == era) & (E.book == book)]
        cell = Cell(S, B, rng)
        for f in FEATS:
            x = S[f].values.astype(float); y = S[ycol].values.astype(float); ok = np.isfinite(x) & np.isfinite(y)
            nu = len(np.unique(x[ok])); r = dict(era=era, book=book, feature=f, n_events=int(ok.sum()), nunique=nu)
            if ok.sum() < MIN_N: r["skip"] = f"n<{MIN_N}"
            elif nu < 2: r["skip"] = "hằng (1 giá trị)"
            else:
                binary = nu == 2; res = cell.stat(x, y, binary)
                r.update(method="point-biserial" if binary else "spearman", rho=res[0], p_boot=res[1], ci_lo=res[2][0], ci_hi=res[2][1], n_months=res[4])
                if binary: r["spearman_also"] = np.corrcoef(rank(x[ok]), rank(y[ok]))[0, 1]
            r["hurdle_dep"] = f in HURDLE_DEP; rows.append(r)
    U = pd.DataFrame(rows)
    for era in ("IS", "OOS"):
        m = U.era == era; U.loc[m, "q_bh"] = bh(U.loc[m, "p_boot"].values)
    return U

def passes(U):
    a = U[U.era == "IS"].set_index(["book", "feature"]); b = U[U.era == "OOS"].set_index(["book", "feature"])
    j = a.join(b, lsuffix="_IS", rsuffix="_OOS", how="inner")
    return j[(j.q_bh_IS < QCUT) & (j.q_bh_OOS < QCUT) & (np.sign(j.rho_IS) == np.sign(j.rho_OOS))]

def month_block_perm(E, rng):
    """trong mỗi năm: vector excess (sắp theo sig_date) cắt thành khối tháng, hoán vị thứ tự khối, ghép lại, gán theo vị trí."""
    y = E.excess_pp.values.copy(); out = y.copy()
    for yr, gi in E.groupby("year").indices.items():
        gi = np.sort(gi); mon = E.month.values[gi]
        blocks = [gi[mon == m] for m in pd.unique(mon)]
        order = rng.permutation(len(blocks))
        out[gi] = np.concatenate([y[blocks[k]] for k in order])
    return out

def placebo(E, R, rng):
    rows = []
    for r in range(R):
        P = E.copy(); P["excess_pp"] = month_block_perm(E, rng)
        U = univariate(P, 500, rng)
        rows.append(dict(rep=r, n_q10_IS=int((U[U.era == "IS"].q_bh < QCUT).sum()), n_q10_OOS=int((U[U.era == "OOS"].q_bh < QCUT).sum()),
                         n_pass_both=int(passes(U).shape[0]), min_q_IS=float(U[U.era == "IS"].q_bh.min()), min_q_OOS=float(U[U.era == "OOS"].q_bh.min())))
    return pd.DataFrame(rows)

def mde_rule(E, U, rng, nsim=400, B=500, grid=(0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50)):
    """Lực theo LUẬT: cấy ρ vào đặc trưng giả ở cả IS & OOS (cùng book); p cấy ghép với m−1 p thật của era; BH q<0,10 cả hai era + cùng dấu."""
    rows = []
    pr = {era: U[(U.era == era) & U.p_boot.notna()].p_boot.values for era in ("IS", "OOS")}
    m = {era: len(pr[era]) for era in pr}
    cells = {(era, book): Cell(E[(E.era == era) & (E.book == book)], B, rng) for era, book in CELLS}
    for book in ("BAL", "LAG"):
        for rho in grid:
            ok = 0; okIS = okOOS = 0
            for _ in range(nsim):
                res = {}
                for era in ("IS", "OOS"):
                    c = cells[(era, book)]; y = c.S.excess_pp.values.astype(float); ry = rank(y); ry = (ry - ry.mean()) / ry.std()
                    x = rho * ry + np.sqrt(1 - rho ** 2) * rng.standard_normal(len(y))
                    r0, p, *_ = c.stat(x, y, False)
                    others = np.delete(pr[era], rng.integers(0, m[era]))              # thay 1 ô thật bằng ô cấy ⇒ họ giữ cỡ m
                    q = bh(np.r_[p, others])[0]; res[era] = (q < QCUT, np.sign(r0))
                okIS += res["IS"][0]; okOOS += res["OOS"][0]
                ok += res["IS"][0] and res["OOS"][0] and res["IS"][1] == res["OOS"][1]
            n = {era: len(cells[(era, book)].S) for era in ("IS", "OOS")}; nm = {era: cells[(era, book)].nm for era in ("IS", "OOS")}
            rows.append(dict(book=book, rho_true=rho, power_rule=ok / nsim, power_IS_only=okIS / nsim, power_OOS_only=okOOS / nsim,
                             m_IS=m["IS"], m_OOS=m["OOS"], n_IS=n["IS"], n_OOS=n["OOS"], months_IS=nm["IS"], months_OOS=nm["OOS"], nsim=nsim))
    R = pd.DataFrame(rows)
    return R

def value_lag_decay(E, rng, B=2000):
    """claim 7: ρ IS − ρ OOS cho value LAG (ey, comp_v3, cfy, psy): bootstrap tháng độc lập hai era."""
    rows = []
    for f in ("ey", "comp_v3", "cfy", "psy"):
        st = {}
        for era in ("IS", "OOS"):
            S = E[(E.era == era) & (E.book == "LAG")]; c = Cell(S, B, rng)
            x, y = S[f].values.astype(float), S.excess_pp.values.astype(float); ok = np.isfinite(x) & np.isfinite(y)
            a, cc = rank(x[ok]), rank(y[ok]); Wk = c.W[:, ok]; s0 = Wk.sum(1)
            mx = Wk @ a / s0; my = Wk @ cc / s0
            sxy = Wk @ (a * cc) / s0 - mx * my; sxx = Wk @ (a * a) / s0 - mx ** 2; syy = Wk @ (cc * cc) / s0 - my ** 2
            st[era] = (np.corrcoef(a, cc)[0, 1], sxy / np.sqrt(sxx * syy))
        d = st["IS"][1] - st["OOS"][1]
        rows.append(dict(feature=f, rho_IS=st["IS"][0], rho_OOS=st["OOS"][0], d_rho=st["IS"][0] - st["OOS"][0],
                         d_ci_lo=np.percentile(d, 5), d_ci_hi=np.percentile(d, 95), p_d_le0=(d <= 0).mean()))
    return pd.DataFrame(rows)

def hyp_native(E, rng):
    sys.path.insert(0, G2); import analyze as A
    H, _ = A.hypotheses(E, 2000, rng); return H

def main():
    jobs = {"liqz_all": ("liqz", None, False), "liqz_adv100": ("liqz", "adv", False), "old_adv100": ("old", "adv", False),
            "liqz_all_nativefee": ("liqz", None, True)}
    only = sys.argv[1:] or list(jobs)
    for tag in only:
        mode, filt, native = jobs[tag]; rng = np.random.default_rng(SEED)
        E = load(mode, filt, native); E.to_csv(os.path.join(HERE, f"events_{tag}.csv"), index=False)
        U = univariate(E, 2000, rng); U.to_csv(os.path.join(HERE, f"univariate_{tag}.csv"), index=False)
        P = passes(U); P.to_csv(os.path.join(HERE, f"univariate_pass_{tag}.csv"))
        out = dict(tag=tag, n_events={f"{b}_{e}": int(((E.book == b) & (E.era == e)).sum()) for e, b in CELLS},
                   n_months={f"{b}_{e}": int(E[(E.book == b) & (E.era == e)].month.nunique()) for e, b in CELLS},
                   family_IS=int(((U.era == "IS") & U.p_boot.notna()).sum()), family_OOS=int(((U.era == "OOS") & U.p_boot.notna()).sum()),
                   q10_IS=U[(U.era == "IS") & (U.q_bh < QCUT)][["book", "feature", "rho", "q_bh"]].values.tolist(),
                   q10_OOS=U[(U.era == "OOS") & (U.q_bh < QCUT)][["book", "feature", "rho", "q_bh"]].values.tolist(),
                   n_pass=len(P), not_tested=U[U.skip.notna()][["era", "book", "feature", "skip"]].values.tolist(),
                   binary_tested=U[U.method == "point-biserial"][["era", "book", "feature", "rho", "spearman_also", "p_boot", "q_bh"]].values.tolist())
        if tag == "liqz_all_nativefee":
            H = hyp_native(E, rng); H.to_csv(os.path.join(HERE, f"hypotheses_{tag}.csv"), index=False)
        else:
            PL = placebo(E, 500, rng); PL.to_csv(os.path.join(HERE, f"placebo_mblock_{tag}.csv"), index=False)
            out["placebo"] = dict(R=len(PL), mean_q10_IS=PL.n_q10_IS.mean(), mean_q10_OOS=PL.n_q10_OOS.mean(),
                                  p95_q10_OOS=float(PL.n_q10_OOS.quantile(0.95)), frac_pass_both_ge1=float((PL.n_pass_both >= 1).mean()),
                                  real_q10_IS=len(out["q10_IS"]), real_q10_OOS=len(out["q10_OOS"]), real_pass=len(P),
                                  p_real_OOS=float((PL.n_q10_OOS >= len(out["q10_OOS"])).mean()), p_real_IS=float((PL.n_q10_IS >= len(out["q10_IS"])).mean()))
            M = mde_rule(E, U, rng); M.to_csv(os.path.join(HERE, f"mde_rule_{tag}.csv"), index=False)
            out["mde80_rule"] = {b: (float(M[(M.book == b) & (M.power_rule >= 0.8)].rho_true.min()) if (M[(M.book == b)].power_rule >= 0.8).any() else ">0.50") for b in ("BAL", "LAG")}
            V = value_lag_decay(E, rng); V.to_csv(os.path.join(HERE, f"value_lag_decay_{tag}.csv"), index=False)
        json.dump(out, open(os.path.join(HERE, f"summary_{tag}.json"), "w"), indent=1, default=str)
        print("=====", tag, json.dumps(out, default=str)[:3000], flush=True)

if __name__ == "__main__":
    main()
