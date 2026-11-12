#!/usr/bin/env python3
"""D2(f) (job Taylor_20261112_151837): H5 theo episode trên chuỗi PIT thật fiinprox dep1m (logic = GĐ2B episodes.py, import trực tiếp).
Báo HAI band (0,0 = tăng thực sự >0; 0,2pp), Δ thô và Δ TRONG-NĂM (excess trừ TB năm của chính nó), CÓ và KHÔNG có 2026,
kèm số episode / sự kiện mỗi biến thể. Đọc events_<tag>.csv của D2 (đã gộp sự kiện, cùng nhãn excess)."""
import os, sys, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/live_gap_phase2b_20261112")
import episodes as EP
rows = []
for tag in ("liqz_all", "liqz_adv100", "old_adv100"):
    s = EP.known_series()
    E = pd.read_csv(os.path.join(HERE, f"events_{tag}.csv"), parse_dates=["sig_date"])
    E = E[E.sig_date >= "2019-05-01"].copy(); E["ym"] = E.sig_date.dt.to_period("M").dt.to_timestamp()
    for band in (0.0, 0.2):
        eps, _ = EP.episodes_from_months(s, band)
        for excl in (False, True):
            X = E[E.year != 2026] if excl else E
            X = X.assign(ex_dm=X.excess_pp - X.groupby("year").excess_pp.transform("mean"))
            inep = np.zeros(len(X), bool); used = 0
            for a, b in eps:
                m = ((X.ym >= a) & (X.ym <= b)).values
                used += bool(m.any()); inep |= m
            per_ep = []
            for a, b in eps:
                m = ((X.ym >= a) & (X.ym <= b)).values
                if m.any(): per_ep.append(X.ex_dm[m].mean() - X.ex_dm[~inep].mean())
            rows.append(dict(tag=tag, band=band, excl_2026=excl, n_episodes_with_events=used, n_in=int(inep.sum()), n_out=int((~inep).sum()),
                             d_raw=X.excess_pp[inep].mean() - X.excess_pp[~inep].mean(), d_within_year=X.ex_dm[inep].mean() - X.ex_dm[~inep].mean(),
                             n_ep_neg_within=int(np.sum(np.array(per_ep) < 0)), n_ep_pos_within=int(np.sum(np.array(per_ep) > 0)),
                             episodes=";".join(f"{a:%Y-%m}→{b:%Y-%m}" for a, b in eps)))
R = pd.DataFrame(rows); R.to_csv(os.path.join(HERE, "h5_d2.csv"), index=False); print(R.drop(columns="episodes").round(2).to_string())
