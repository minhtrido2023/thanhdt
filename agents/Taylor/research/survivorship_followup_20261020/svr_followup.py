"""B/C follow-up replay survivorship — theo PREREG_BC.md (md5 d9a91be2). EXPLORATORY, job Taylor_20261020_113646.
Import nguyên văn svr_replay/svr_lib; chỉ thêm: cap khớp theo pha (part_in/part_out mỗi ngày), exitval nm, trọng số fixA.
Usage: $DNA_PYEXE svr_followup.py <out_dir> <label>=<ledger.csv> ...
"""
import sys, os, json
import numpy as np, pandas as pd
RP = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/survivorship_replay_20261020"
sys.path.insert(0, RP)
import svr_replay as R

V2FIX = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/survivorship_sensitivity_v2_20261020/out_summary.json"
SETS = {"M": R.M, "M-TGG-GAB": [x for x in R.M if x not in ("TGG", "GAB")], "M-GAB": [x for x in R.M if x != "GAB"]}
CAPS = [(0.20, "phase"), (0.10, "phase"), (0.05, "phase"), (0.10, "all"), (0.05, "all")]


def phase_mask(T, L):
    """PREREG_BC: bơm Close≥2×min250 | xả Close≤0,5×max250 | d∈[LT−365, DL]; trên lịch giá của mã, reindex L."""
    C = T.ind.Close
    pump = C >= 2.0 * C.rolling(250, min_periods=1).min()
    dump = C <= 0.5 * C.rolling(250, min_periods=1).max()
    coll = (C.index >= T.LT - pd.Timedelta(days=365)) & (C.index <= T.DL)
    m = (pump | dump | coll).reindex(L).fillna(False).astype(bool)
    return m


def simulate2(T, sds, d, book, w_tgt, part, val, tgt_ser=None):
    """= R.simulate(xmode='liq', scen='Z') nhưng PART → part[j] (Series theo L), T.val → val. Giữ nguyên mọi dòng khác."""
    L = d.index; nav = d.combined_nav; trades = []; busy_until = None
    pa = part.values; va = val.values
    for sd in sorted(sds):
        i = L.get_loc(sd) + 1
        if i >= len(L) or (busy_until is not None and L[i] <= busy_until):
            continue
        e = L[i]
        if T.vol.iloc[i] <= 0 or pd.isna(T.open.iloc[i]):
            continue
        tgt = w_tgt * (nav.iloc[i] if tgt_ser is None else tgt_ser.iloc[i])
        cap = sum(pa[j] * (T.liq.iloc[j] if not pd.isna(T.liq.iloc[j]) else 0.0) for j in range(i, min(i + R.FILL_DAYS, len(L))))
        if cap < R.MIN_FILL * tgt:
            continue
        filled = min(tgt, cap); epx = float(T.open.iloc[i]); sh = filled / epx; inv = filled * (1 + R.COST)
        cashG = 0.0
        rem = sh; held = 0; exit_from = None; path = {}; stuck = False; closed = None; rows = []
        for j in range(i, len(L)):
            day = L[j]; G = nav.iloc[j] / nav.iloc[i]
            px = T.close.iloc[j]
            if day > T.DL:
                if rem > 0:
                    stuck = True
                    rows.append((day, 0.0, 0.0, 0.0, 0.0)); rem = 0
                path[day] = cashG; closed = day; break
            sold = 0.0
            if exit_from is not None and j >= exit_from and rem > 0 and T.vol.iloc[j] > 0:
                p_sell = T.open.iloc[j] if j == exit_from else px
                if pd.isna(p_sell):
                    p_sell = px
                q = min(rem, pa[j] * va[j] / max(float(px), 1e-9))
                cashG += q * p_sell * (1 - R.COST) / G; rem -= q; sold = q * p_sell
            rows.append((day, max(rem, 0.0), float(px), filled if j == i else 0.0, sold))
            if rem <= 1e-9:
                path[day] = cashG; closed = day; break
            path[day] = cashG + rem * px / G
            if exit_from is None and j > i:
                held += 1
                r = px / epx - 1
                if held >= (R.BAL_HOLD if book == "BAL" else R.LAG_HOLD) or (book == "BAL" and r <= R.BAL_STOP):
                    exit_from = j + 1
        s = pd.Series(path) / inv
        trades.append(dict(tk=T.tk, book=book, sd=sd, entry=e, w=inv / nav.iloc[i], filled_vnd=filled, target_vnd=tgt,
                           closed=closed, stuck=stuck, final_VG=float(s.iloc[-1]), VG=s,
                           pos=pd.DataFrame(rows, columns=["day", "rem", "mark", "buy", "sold"]).set_index("day")))
        busy_until = closed if closed is not None else L[-1]
    return trades


def book_fraction_fix(d, tx):
    """= R.book_fraction nhưng loại ETF_PARK (fix A)."""
    return R.book_fraction(d, tx[~tx.play_type.eq("ETF_PARK")])


def main():
    out_dir = sys.argv[1]; legs = dict(a.split("=", 1) for a in sys.argv[2:])
    v2o = json.load(open(R.V2))["legs"]; v2f = json.load(open(V2FIX))["legs"]
    vni = pd.read_csv(f"{RP}/data/bq_vni.csv", parse_dates=["time"]).set_index("time")
    cal_mkt = vni.index; infl = vni.Inflation_7; vmax = vni.D_RSI.rolling(60, min_periods=1).max()
    fin = R.load_fin()
    orig = pd.read_csv(f"{R.KBP}/delisted-big-vanished-prices-20261020.csv").set_index("ticker").exch_orig.to_dict()
    sa = pd.read_csv(f"{R.WIN}/stats_all.csv").set_index("ticker").exch2.to_dict()
    rows, meta = [], {}
    for label, path in legs.items():
        met, d, tx = R.load_ledger(path)
        base = R.calc_metrics(d.combined_nav)
        if abs(base["cagr"] - float(met["cagr"])) > 1e-9:
            raise SystemExit(f"{label}: không tái tạo METRIC")
        W = {"orig": (v2o[label]["w_median"], R.book_fraction(d, tx)),
             "fixA": (v2f[label]["w_median"], book_fraction_fix(d, tx))}
        meta[label] = {k: dict(w=v[0], pf=v[1]) for k, v in W.items()}
        tks = {tk: R.Tk(tk, cal_mkt, infl, vmax, d.index, orig.get(tk, sa.get(tk))) for tk in R.M}
        L = d.index
        ph, vnm = {}, {}
        for tk, T in tks.items():
            ph[tk] = phase_mask(T, L)
            nmv = pd.read_csv(f"{R.KBP}/delisted-tickers-survivorship-20261020.d/prices/{tk}.csv") if os.path.exists(
                f"{R.KBP}/delisted-tickers-survivorship-20261020.d/prices/{tk}.csv") else None
            if nmv is None:
                raise SystemExit(f"thiếu file giá {tk}")
            nmv["date"] = pd.to_datetime(nmv.date); nmv = nmv.sort_values("date").drop_duplicates("date", keep="last").set_index("date")
            vnm[tk] = nmv.nmValue.fillna(0.0)[nmv.index <= T.DL].reindex(L).fillna(0.0)
        meta[label]["phase_days"] = {tk: int(m.sum()) for tk, m in ph.items()}
        for var in ["UB", "MID", "LIVE"]:
            sig = {}
            for tk, T in tks.items():
                fq = fin.get(tk)
                sig[(tk, "BAL")] = R.bal_signals(T, d, vni, fq, var)
                sig[(tk, "LAG")] = R.lag_events(T, d, fq, cal_mkt, var)
                sig[(tk, "LAG_nb")] = R.lag_events(T, d, fq, cal_mkt, var, skip_bear=False)
            for wk, (w, pf) in W.items():
                for capv, scope in CAPS:
                    for ev in ["ptin", "nm"]:
                        tr, tra = [], []
                        for (tk, book), sds in sig.items():
                            T = tks[tk]
                            part = pd.Series(np.where(ph[tk].values if scope == "phase" else True, capv, R.PART), index=L) \
                                if capv != R.PART else pd.Series(R.PART, index=L)
                            val = T.val if ev == "ptin" else vnm[tk]
                            if book != "LAG_nb":
                                tr += simulate2(T, sds, d, book, w[book], part, val)
                            if book != "LAG":
                                bk = "LAG" if book == "LAG_nb" else book
                                tra += simulate2(T, sds, d, bk, pf[bk], part, val, tgt_ser=d[f"nav_{bk.lower()}_ref"])
                        for vv, TR, ovl in [(var, tr, R.overlay), (var + "_ALLOC", tra, R.overlay_alloc)]:
                            for sname, S in SETS.items():
                                for cfg, books in [("BAL", ["BAL"]), ("LAG", ["LAG"]), ("MIX", ["BAL", "LAG"])]:
                                    sub = [t for t in TR if t["tk"] in S and t["book"] in books]
                                    m = R.calc_metrics(d.combined_nav * ovl(d, sub))
                                    rows.append(dict(leg=label, w=wk, cap=capv, scope=scope, exitval=ev, var=vv, set=sname, cfg=cfg,
                                                     n_trades=len(sub), n_stuck=sum(t["stuck"] for t in sub),
                                                     d_cagr_pp=(m["cagr"] - base["cagr"]) * 100,
                                                     d_sharpe=m["sharpe_252"] - base["sharpe_252"],
                                                     d_maxdd_pp=(m["max_dd"] - base["max_dd"]) * 100))
        print(label, "done", json.dumps(meta[label], default=str), flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(out_dir, "out_followup_results.csv"), index=False)
    json.dump(meta, open(os.path.join(out_dir, "out_followup_meta.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
