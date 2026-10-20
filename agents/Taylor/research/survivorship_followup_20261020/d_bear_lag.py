"""D: lô LAG (book ref) mở lúc BEAR (w_lag_tgt=0) trong ledger pin THẬT — có lô nào sau đó halt/hủy/kẹt? Chỉ ĐỌC. Job Taylor_20261020_113646.
Usage: $DNA_PYEXE d_bear_lag.py <label>=<ledger.csv> ...  (giá: cache pin data/bq_cache_asof20260729_postrestate/ticker)"""
import sys, glob, json
import numpy as np, pandas as pd
C = "/home/trido/thanhdt/WorkingClaude/data/bq_cache_asof20260729_postrestate/ticker"
px = pd.concat([pd.read_parquet(f, columns=["ticker", "time", "Close", "Volume"]) for f in sorted(glob.glob(f"{C}/*.parquet"))])
px["time"] = pd.to_datetime(px.time)
last_row = px.groupby("ticker").time.max()
PX = {k: g.set_index("time").sort_index() for k, g in px.groupby("ticker")}
out = {}
for a in sys.argv[1:]:
    label, path = a.split("=", 1)
    df = pd.read_csv(path, low_memory=False)
    d = df[df.record_type == "DAILY"].copy(); d["ymd"] = pd.to_datetime(d.ymd); d = d.set_index("ymd").sort_index()
    for c in ["state", "w_lag_tgt", "cap_lag", "combined_nav", "nav_lag_ref"]:
        d[c] = d[c].astype(float)
    END = d.index[-1]; pos_of = {t: i for i, t in enumerate(d.index)}
    tx = df[(df.record_type == "TX") & (df.book == "LAG") & (df.play_type != "ETF_PARK")].copy()
    tx["ymd"] = pd.to_datetime(tx.ymd); tx["shares"] = tx.shares.astype(float); tx["adj_price"] = tx.adj_price.astype(float)
    rows = []
    for hid, g in tx.groupby("holding_id"):
        b = g[g.action == "buy"]; s = g[g.action == "sell"]
        if b.empty:
            continue
        t0 = b.ymd.min(); t1 = s.ymd.max() if len(s) else END
        tk = g.ticker.iloc[0]
        p = PX.get(tk, px.iloc[0:0].set_index("time")).loc[t0:t1]
        sess = d.index[(d.index >= t0) & (d.index <= t1)]
        miss = sess.difference(p.index)
        zv = p.index[p.Volume.fillna(0) <= 0]
        bad = miss.union(zv)
        # chuỗi phiên liên tiếp không giao dịch dài nhất
        run = mx = 0
        for day in sess:
            run = run + 1 if day in bad else 0; mx = max(mx, run)
        st0 = d.state.get(t0); wt0 = d.w_lag_tgt.get(t0)
        on = d.loc[sess]
        rows.append(dict(hid=hid, tk=tk, play=g.play_type.iloc[0], buy=t0.date(), last_sell=(s.ymd.max().date() if len(s) else None),
                         sessions=len(sess), state0=st0, w_tgt0=wt0, cap_lag0_share=float(d.cap_lag.get(t0) / d.combined_nav.get(t0)),
                         bear_open=bool(wt0 == 0), cap_reenabled=bool((on.cap_lag > 0).any()) and wt0 == 0,
                         sh_buy=float(b.shares.sum()), sh_sell=float(s.shares.sum()),
                         closed_at_end=bool(len(s) and s.ymd.max() == END), nontrade_days=len(bad), max_nontrade_run=mx,
                         tk_last_row=str(last_row.get(tk, pd.NaT).date()) if tk in last_row else None,
                         ret=float(s.adj_price.mean() / b.adj_price.mean() - 1) if len(s) else np.nan,
                         w_in_book=float((b.shares * b.adj_price).sum() / d.nav_lag_ref.get(t0))))
    r = pd.DataFrame(rows)
    r.to_csv(f"d_lots_{label}.csv", index=False)
    bear = r[r.bear_open]
    flag = r[(r.max_nontrade_run >= 5) | (r.sessions > 40) | (r.sh_sell < r.sh_buy * 0.999) | r.closed_at_end]
    out[label] = dict(n_lots=len(r), n_bear_open=len(bear), n_bear_reenabled=int(bear.cap_reenabled.sum()),
                      bear_sessions_med=float(bear.sessions.median()) if len(bear) else None,
                      bear_max_sessions=int(bear.sessions.max()) if len(bear) else None,
                      bear_flagged=bear[(bear.max_nontrade_run >= 5) | (bear.sessions > 40) | (bear.sh_sell < bear.sh_buy * 0.999)
                                        | bear.closed_at_end][["hid", "sessions", "max_nontrade_run", "nontrade_days", "ret",
                                                               "closed_at_end", "tk_last_row", "cap_reenabled"]].to_dict("records"),
                      all_flagged=flag[["hid", "bear_open", "sessions", "max_nontrade_run", "ret", "closed_at_end", "tk_last_row"]].to_dict("records"),
                      bear_ret_med=float(bear.ret.median()) if len(bear) else None,
                      bear_ret_min=float(bear.ret.min()) if len(bear) else None,
                      bear_lots_tk_delisted_before_end=bear[bear.tk_last_row.astype(str) < str(END.date())][["hid", "tk_last_row"]].to_dict("records"))
    print(label, json.dumps(out[label], default=str, indent=0)[:3000], flush=True)
json.dump(out, open("d_bear_lag_summary.json", "w"), indent=1, default=str)
