"""V2 — replay survivorship trên tập mã hủy niêm yết enumerate có hệ thống (PREREG_V2.md). EXPLORATORY, job Taylor_20261020_122917.
Import nguyên văn svr_replay (R) + svr_followup (F: simulate2, phase_mask, book_fraction_fix). Chỉ thêm: tập A/N, BCTC N, overlay từng mã.
Usage: $DNA_PYEXE v2_replay.py <label>=<ledger.csv> ...
"""
import sys, os, json
import numpy as np, pandas as pd
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/survivorship_replay_20261020")
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/survivorship_followup_20261020")
import svr_replay as R
import svr_followup as F

HERE = os.path.dirname(os.path.abspath(__file__))
KPD = f"{R.KBP}/delisted-tickers-survivorship-20261020.d"
CFG = {"main": (0.05, "phase", "nm"), "sens20": (0.20, "all", "ptin")}     # PREREG_V2 §4


def load_fin_all():
    a = pd.read_csv(f"{R.WIN}/fin_raw.csv"); b = pd.read_csv(f"{R.HERE}/data/fin_raw_live_ext.csv")
    c = pd.read_csv(f"{HERE}/data/fin_raw_v2.csv")
    f = pd.concat([a, b, c]); f = f[f.item.isin(["npat_parent", "revenue", "cfo"])]
    w = f.pivot_table(index=["ticker", "fiscalDate"], columns="item", values="value", aggfunc="first").reset_index()
    w["fiscalDate"] = pd.to_datetime(w.fiscalDate)
    w["rel"] = [fd + pd.Timedelta(days=R.REL_LAG[(fd.month - 1) // 3 + 1]) for fd in w.fiscalDate]
    return {tk: g.sort_values("fiscalDate").set_index("fiscalDate") for tk, g in w.groupby("ticker")}


def nm_value(tk, T, L):
    for p in (f"{KPD}/prices/{tk}.csv", f"{KPD}/prices_all/{tk}.csv"):
        if os.path.exists(p):
            v = pd.read_csv(p); break
    v["date"] = pd.to_datetime(v.date); v = v.sort_values("date").drop_duplicates("date", keep="last").set_index("date")
    return v.nmValue.fillna(0.0)[v.index <= T.DL].reindex(L).fillna(0.0)


def main():
    legs = dict(a.split("=", 1) for a in sys.argv[1:])
    sets = json.load(open(f"{HERE}/data/v2_sets.json"))
    uni = pd.read_csv(f"{HERE}/data/v2_universe.csv").set_index("ticker")
    N = sets["N"]; M = [t for t in R.M if t in sets["A"]]; MN = M + N
    NBB = [t for t in N if uni.cat.get(t) == "bat_buoc"]
    SETS = {"M": M, "N": N, "M+N": MN, "N_bat_buoc": NBB}
    v2f = json.load(open(F.V2FIX))["legs"]
    vni = pd.read_csv(f"{R.HERE}/data/bq_vni.csv", parse_dates=["time"]).set_index("time")
    cal_mkt = vni.index; infl = vni.Inflation_7; vmax = vni.D_RSI.rolling(60, min_periods=1).max()
    fin = load_fin_all()
    fin_cov = {tk: (tk in fin and fin[tk].npat_parent.notna().any()) for tk in N}
    rows, solo, lots, meta = [], [], [], {"fin_cov_N": fin_cov, "sets": {k: len(v) for k, v in SETS.items()}}
    tks_cache, L0 = None, None
    for label, path in legs.items():
        met, d, tx = R.load_ledger(path)
        base = R.calc_metrics(d.combined_nav)
        if abs(base["cagr"] - float(met["cagr"])) > 1e-9:
            raise SystemExit(f"{label}: không tái tạo METRIC")
        w, pf = v2f[label]["w_median"], F.book_fraction_fix(d, tx)
        L = d.index
        if tks_cache is None or not L.equals(L0):
            tks_cache, errs = {}, {}
            for tk in MN:
                try:
                    T = R.Tk(tk, cal_mkt, infl, vmax, L, uni.orig.get(tk))
                    tks_cache[tk] = (T, F.phase_mask(T, L), nm_value(tk, T, L))
                except Exception as e:
                    errs[tk] = f"{type(e).__name__}: {e}"
            meta["tk_errors"] = errs; L0 = L
            print(f"[{label}] built {len(tks_cache)} tickers, errors {len(errs)}", flush=True)
        for var in ["UB", "MID", "LIVE"]:
            sig = {}
            for tk, (T, ph, vnm) in tks_cache.items():
                fq = fin.get(tk)
                sig[(tk, "BAL")] = R.bal_signals(T, d, vni, fq, var)
                sig[(tk, "LAG")] = R.lag_events(T, d, fq, cal_mkt, var)
                sig[(tk, "LAG_nb")] = R.lag_events(T, d, fq, cal_mkt, var, skip_bear=False)
            for ck, (capv, scope, ev) in CFG.items():
                tr, tra = [], []
                for (tk, book), sds in sig.items():
                    T, ph, vnm = tks_cache[tk]
                    part = pd.Series(np.where(ph.values if scope == "phase" else True, capv, R.PART), index=L)
                    val = T.val if ev == "ptin" else vnm
                    if book != "LAG_nb":
                        tr += F.simulate2(T, sds, d, book, w[book], part, val)
                    if book != "LAG":
                        bk = "LAG" if book == "LAG_nb" else book
                        tra += F.simulate2(T, sds, d, bk, pf[bk], part, val, tgt_ser=d[f"nav_{bk.lower()}_ref"])
                for vv, TR, ovl in [(var, tr, R.overlay), (var + "_ALLOC", tra, R.overlay_alloc)]:
                    for sname, S in SETS.items():
                        Sset = set(S)
                        for cfg, books in [("BAL", ["BAL"]), ("LAG", ["LAG"]), ("MIX", ["BAL", "LAG"])]:
                            sub = [t for t in TR if t["tk"] in Sset and t["book"] in books]
                            m = R.calc_metrics(d.combined_nav * ovl(d, sub))
                            rows.append(dict(leg=label, cfgk=ck, var=vv, set=sname, cfg=cfg, n_trades=len(sub),
                                             n_tk=len({t["tk"] for t in sub}), n_stuck=sum(t["stuck"] for t in sub),
                                             d_cagr_pp=(m["cagr"] - base["cagr"]) * 100,
                                             d_sharpe=m["sharpe_252"] - base["sharpe_252"],
                                             d_maxdd_pp=(m["max_dd"] - base["max_dd"]) * 100))
                    if vv == var:                                   # từng mã một mình (overlay chính)
                        by = {}
                        for t in TR:
                            by.setdefault(t["tk"], []).append(t)
                        for tk, sub in by.items():
                            m = R.calc_metrics(d.combined_nav * R.overlay(d, sub))
                            solo.append(dict(leg=label, cfgk=ck, var=var, tk=tk, inN=tk in N, cat=uni.cat.get(tk),
                                             n_trades=len(sub), n_stuck=sum(t["stuck"] for t in sub),
                                             d_cagr_pp=(m["cagr"] - base["cagr"]) * 100))
                        if ck == "main":
                            for t in TR:
                                lots.append(dict(leg=label, var=var, tk=t["tk"], book=t["book"], entry=t["entry"].date(),
                                                 w=t["w"], filled_vnd=t["filled_vnd"], target_vnd=t["target_vnd"],
                                                 stuck=t["stuck"], final_VG=t["final_VG"]))
            print(f"[{label}] {var} done", flush=True)
    pd.DataFrame(rows).to_csv(f"{HERE}/out_v2_results.csv", index=False)
    pd.DataFrame(solo).to_csv(f"{HERE}/out_v2_solo.csv", index=False)
    pd.DataFrame(lots).to_csv(f"{HERE}/out_v2_lots.csv", index=False)
    json.dump(meta, open(f"{HERE}/out_v2_meta.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
