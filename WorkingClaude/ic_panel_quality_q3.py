#!/usr/bin/env python3
"""ic_panel_quality_q3.py — job Taylor_20260720_111429, Viec 2.

Backtest tham do 2 candidate da duoc user duyet tu factor_gap_audit_20260718.md:
  F1  ACCRUALS (Sloan 1996)          = NP_TTM/TA  -  CFO_TTM/TA        (ky vong IC AM)
  F2  GROSS PROFITABILITY (Novy-Marx)= GP_TTM / TotalAssets            (ky vong IC DUONG)

MULTIPLE-TESTING DISCIPLINE (khai bao TRUOC khi chay, kb/context_pack.md §Quy chuan 5):
  N trials = 2. Moi factor DUNG 1 dac ta duy nhat, KHONG sweep tham so, khong thu bien the
  quarterly-vs-TTM roi chon cai dep. TTM duoc chon truoc vi (a) dung chuan van ban goc cua
  Sloan/Novy-Marx (du lieu nam), (b) tai dung dung prototype accruals da co trong
  ic_panel_ext_q3.py:57-60 theo dung yeu cau dispatch.

TEST QUAN TRONG NHAT (theo canh bao §4 audit doc): KHONG chi bao IC tho. Rui ro lon nhat la
do lai chinh 1/PE duoi ten khac. Vi vay bao 3 tang:
  L0 raw IC              — IC tho
  L1 marginal vs VALUE   — residualize tren {ey,cfy,ps,neg_pbz}  (CORE_VALUE co san)
  L2 marginal vs VALUE+RATING — them neg_rating (rating 8L) vao bo control  <-- gate quyet dinh
Walk-forward IS(2014-19)/OOS(2020+). Per-year LOO chay khi edge mong.

KHONG WIRE PRODUCTION du ket qua the nao — day la vong tham do, GO/NO-GO chi la khuyen nghi.
Usage: source ./wc_env.sh && $DNA_PYEXE ic_panel_quality_q3.py
"""
import warnings; warnings.filterwarnings("ignore")
import os, importlib.util
import numpy as np, pandas as pd

WORKDIR = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")
spec = importlib.util.spec_from_file_location("ic8l", os.path.join(WORKDIR, "ic_panel_8l.py"))
ic8l = importlib.util.module_from_spec(spec); spec.loader.exec_module(ic8l)
bq, load, summ, ic_series = ic8l.bq, ic8l.load, ic8l.summ, ic8l.ic_series
TARGET, CRASH, N_MIN, _rank = ic8l.TARGET, ic8l.CRASH, ic8l.N_MIN, ic8l._rank

CONTROLS_VALUE = ["ey", "cfy", "ps", "neg_pbz"]
CONTROLS_FULL  = CONTROLS_VALUE + ["neg_rating"]

FACTORS = [  # (tag, col, ky vong dau IC)
    ("F1_accruals",   "accruals",  "neg"),
    ("F2_gross_prof", "gross_prof", "pos"),
]


# ---------------- PIT attach ----------------
def attach(d):
    """Gan 2 factor tu ticker_financial, PIT qua merge_asof tren Release_Date (giong ext_q3)."""
    fin = bq("""
      SELECT f.ticker AS ticker, f.Release_Date AS rel,
             f.NP_P0, f.NP_P1, f.NP_P2, f.NP_P3,
             f.CF_OA_P0, f.CF_OA_P1, f.CF_OA_P2, f.CF_OA_P3,
             f.GPM_P0, f.GPM_P1, f.GPM_P2, f.GPM_P3,
             f.Revenue_P0, f.Revenue_P1, f.Revenue_P2, f.Revenue_P3,
             f.totalAsset_P0
      FROM tav2_bq.ticker_financial AS f
      WHERE f.time >= '2012-06-01' AND f.Release_Date IS NOT NULL
      ORDER BY f.ticker, f.Release_Date
    """)
    fin["rel"] = pd.to_datetime(fin["rel"])
    for c in fin.columns:
        if c not in ("ticker", "rel"):
            fin[c] = pd.to_numeric(fin[c], errors="coerce")

    ta = fin["totalAsset_P0"].where(fin["totalAsset_P0"] > 0)

    # F1 accruals (Sloan): (NP_TTM - CFO_TTM)/TA.
    # ⚠️ UNIT-CHECK 2026-07-20 (job Taylor_20260720_111429): CF_OA_Pi la DONG TIEN THO (VND),
    # KHONG phai CFO/assets — bat chap bigquery_dictionary.json ghi "Cashflow over assets".
    # Bang chung: HPG 2025Q1 CF_OA_P0=-2.78e12 vs NP_P0=+3.34e12 (cung bac VND).
    # Prototype ic_panel_ext_q3.py:58 gia dinh sai dieu nay => ket qua H4 cu KHONG hop le.
    # P0..P3 la gia tri TUNG QUY roi rac (da verify: CF_OA_P1@2024Q2 == CF_OA_P0@2024Q1),
    # khong phai luy ke YTD => cong TTM hop le.
    np_ttm  = fin[["NP_P0", "NP_P1", "NP_P2", "NP_P3"]].sum(axis=1, min_count=4)
    cfo_ttm = fin[["CF_OA_P0", "CF_OA_P1", "CF_OA_P2", "CF_OA_P3"]].sum(axis=1, min_count=4)
    fin["accruals"] = (np_ttm - cfo_ttm) / ta

    # F2 gross profitability (Novy-Marx): GP_TTM/TA.
    # ⚠️ UNIT-CHECK: GPM_Pi la TY LE (0..1), KHONG phai phan tram — bat chap dict ghi "(%)".
    # Bang chung: VNM 2025Q1 GPM_P0=0.4107 (~41% bien gop, dung), FPT 0.3778, HPG 0.1357.
    # => KHONG chia 100.
    gp_q = [fin[f"GPM_P{i}"] * fin[f"Revenue_P{i}"] for i in range(4)]
    gp_ttm = pd.concat(gp_q, axis=1).sum(axis=1, min_count=4)
    fin["gross_prof"] = gp_ttm / ta

    finm = (fin[["ticker", "rel", "accruals", "gross_prof"]]
            .replace([np.inf, -np.inf], np.nan)
            .dropna(subset=["rel"]).sort_values("rel"))
    d = pd.merge_asof(d.sort_values("time"), finm, by="ticker",
                      left_on="time", right_on="rel", direction="backward")
    return d.drop(columns=["rel"])


# ---------------- marginal IC voi bo control tuy chon ----------------
def marginal_ic(d, lens, target, controls, mask=None):
    sub = d if mask is None else d[mask]
    others = [c for c in controls if c != lens]
    ics, qs = [], []
    for q, g in sub.groupby("q"):
        y = pd.to_numeric(g[target], errors="coerce")
        x = pd.to_numeric(g[lens], errors="coerce")
        X = g[others].apply(pd.to_numeric, errors="coerce")
        ok = x.notna() & y.notna() & X.notna().all(axis=1)
        if ok.sum() < N_MIN:
            continue
        xr = _rank(x[ok]).values
        Xr = np.column_stack([np.ones(int(ok.sum()))] + [_rank(X[c][ok]).values for c in others])
        beta, *_ = np.linalg.lstsq(Xr, xr, rcond=None)
        ic = np.corrcoef(xr - Xr @ beta, _rank(y[ok]))[0, 1]
        if np.isfinite(ic):
            ics.append(ic); qs.append(q)
    return np.array(ics), qs


def quintile_table(d, lens, mask):
    g = d[mask & d[lens].notna() & d[TARGET].notna()].copy()
    if len(g) < 100:
        return None
    g["Q"] = pd.qcut(g[lens].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rows = []
    for q in [1, 2, 3, 4, 5]:
        s = g[g["Q"] == q]
        rows.append(dict(Q=q, n=len(s), lens_mean=s[lens].mean(),
                         fwd2M=s[TARGET].mean(), crash=(s[TARGET] < CRASH).mean() * 100))
    return pd.DataFrame(rows)


def loo_by_year(ics, qs):
    """Per-year leave-one-out tren chuoi IC theo quy: bo tung nam, xem mean IC con lai."""
    yr = np.array([q.year for q in qs])
    out = []
    for y in sorted(set(yr)):
        keep = yr != y
        out.append(dict(drop_year=int(y), n_q_dropped=int((~keep).sum()),
                        mean_ic_wo_year=float(np.mean(ics[keep])) if keep.sum() else np.nan,
                        mean_ic_of_year=float(np.mean(ics[~keep]))))
    return pd.DataFrame(out)


def main():
    print("N TRIALS KHAI BAO TRUOC = 2 (F1 accruals TTM, F2 gross profitability TTM). "
          "Khong sweep tham so.\n")
    d = load()
    d = attach(d)
    d["yr"] = d["q"].dt.year
    gate = d["rating"] <= 3
    IS, OOS = d["yr"] <= 2019, d["yr"] >= 2020

    print(f"panel obs {len(d)}  quarters {d.q.nunique()}  tickers {d.ticker.nunique()}  "
          f"gate-obs {int(gate.sum())}")
    for tag, L, _ in FACTORS:
        print(f"  cov {tag:14} full={d[L].notna().mean():.2f}  gate={d.loc[gate, L].notna().mean():.2f}")

    fmt = lambda v: f"{v:+.3f}" if pd.notna(v) else "  -  "
    rows, quints, loos = [], [], []

    print(f"\n=== IC PANEL — target={TARGET} (T+40), in-gate rating<=3 ===")
    print(f"L1 controls = {CONTROLS_VALUE}")
    print(f"L2 controls = {CONTROLS_FULL}   <-- gate quyet dinh\n")
    hdr = (f"{'factor':14} {'exp':>3} | {'L0raw_IS':>9} {'L0raw_OOS':>10} | "
           f"{'L1val_IS':>9} {'L1val_OOS':>10} | {'L2vr_IS':>8} {'L2vr_OOS':>9} "
           f"{'t_IS':>5} {'t_OOS':>6} {'hitOOS':>7}")
    print(hdr); print("-" * len(hdr))

    for tag, L, exp in FACTORS:
        r = {}
        for lab, ctrl in (("L1", CONTROLS_VALUE), ("L2", CONTROLS_FULL)):
            for half, m in (("IS", IS), ("OOS", OOS)):
                ics, qs = marginal_ic(d, L, TARGET, ctrl, gate & m)
                r[f"{lab}_{half}"] = summ(ics)
                if lab == "L2":
                    r[f"ics_{half}"] = (ics, qs)
        raw_IS = summ(ic_series(d, L, TARGET, gate & IS)[0])
        raw_OOS = summ(ic_series(d, L, TARGET, gate & OOS)[0])

        print(f"{tag:14} {exp:>3} | {fmt(raw_IS['ic']):>9} {fmt(raw_OOS['ic']):>10} | "
              f"{fmt(r['L1_IS']['ic']):>9} {fmt(r['L1_OOS']['ic']):>10} | "
              f"{fmt(r['L2_IS']['ic']):>8} {fmt(r['L2_OOS']['ic']):>9} "
              f"{r['L2_IS']['t']:>5.1f} {r['L2_OOS']['t']:>6.1f} {r['L2_OOS']['hit']:>7.2f}")

        # SURVIVAL: dau dung ky vong VA |IC|>=0.03 tren L2 o CA HAI nua
        thr = -0.03 if exp == "neg" else 0.03
        ok = lambda v: (v <= thr) if exp == "neg" else (v >= thr)
        alive = ok(r["L2_IS"]["ic"]) and ok(r["L2_OOS"]["ic"])
        rows.append(dict(factor=tag, col=L, expect=exp,
                         raw_ic_IS=raw_IS["ic"], raw_ic_OOS=raw_OOS["ic"],
                         mic_value_IS=r["L1_IS"]["ic"], mic_value_OOS=r["L1_OOS"]["ic"],
                         mic_valrat_IS=r["L2_IS"]["ic"], mic_valrat_OOS=r["L2_OOS"]["ic"],
                         t_IS=r["L2_IS"]["t"], t_OOS=r["L2_OOS"]["t"],
                         hit_IS=r["L2_IS"]["hit"], hit_OOS=r["L2_OOS"]["hit"],
                         nq_IS=r["L2_IS"]["n"], nq_OOS=r["L2_OOS"]["n"],
                         verdict="SURVIVE-L2" if alive else "NO-GO-L2"))
        qt = quintile_table(d, L, gate)
        if qt is not None:
            qt.insert(0, "factor", tag); quints.append(qt)
        allics = np.concatenate([r["ics_IS"][0], r["ics_OOS"][0]])
        allqs = list(r["ics_IS"][1]) + list(r["ics_OOS"][1])
        lo = loo_by_year(allics, allqs); lo.insert(0, "factor", tag); loos.append(lo)

    print(f"\n=== quintile (in-gate, Q1..Q5 tang dan theo factor) ===")
    for qt in quints:
        tag = qt["factor"].iloc[0]
        print(f"{tag:14} fwd2M: " + " ".join(f"Q{int(r.Q)}:{r.fwd2M:+6.2f}" for _, r in qt.iterrows()))
        print(f"{'':14} crash: " + " ".join(f"Q{int(r.Q)}:{r.crash:5.1f}%" for _, r in qt.iterrows()))

    print(f"\n=== per-year LOO tren marginal IC L2 (value+rating) ===")
    for lo in loos:
        tag = lo["factor"].iloc[0]
        print(f"{tag}:")
        print(lo.drop(columns=["factor"]).round(4).to_string(index=False))

    out = pd.DataFrame(rows)
    print("\n=== SUMMARY ===")
    print(out.round(4).to_string(index=False))
    out.round(4).to_csv(os.path.join(WORKDIR, "data", "ic_panel_quality_q3.csv"), index=False)
    pd.concat(quints).round(3).to_csv(os.path.join(WORKDIR, "data", "ic_panel_quality_q3_quintile.csv"), index=False)
    pd.concat(loos).round(4).to_csv(os.path.join(WORKDIR, "data", "ic_panel_quality_q3_loo.csv"), index=False)
    print("\nwrote data/ic_panel_quality_q3{,_quintile,_loo}.csv")


if __name__ == "__main__":
    main()
