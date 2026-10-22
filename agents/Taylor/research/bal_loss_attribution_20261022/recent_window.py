"""NGOÀI PREREG (post-hoc, gắn nhãn): cửa sổ 'đợt vừa rồi' = đỉnh NAV từ 2026-09-01 → đáy sau đó,
và cửa sổ cố định 2026-09-16 (trước lệnh BAL đầu) → 2026-10-20 (dòng NAV cuối). P&L theo sổ như PREREG Q1."""
import json, os, pandas as pd
import live_attrib as L   # chạy lại module (in JSON cũ) — chấp nhận, read-only
HERE = os.path.dirname(os.path.abspath(__file__))
res = {}
for acct in L.ACCTS:
    F = L.load_fills(acct); bm = L.book_map(acct, F)
    nav = pd.read_csv(f"{L.E}/nav_history_{acct}.csv", parse_dates=["date"]).drop_duplicates("date", keep="last").set_index("date")["nav"].sort_index()
    sub = nav.loc["2026-09-01":]
    dd = sub / sub.cummax() - 1; t = dd.idxmin(); p = sub.loc[:t].idxmax()
    out = {}
    for name, (ps, pe) in {"peak_trough_since_0901": (str(p.date()), str(t.date())),
                           "fixed_0916_1020": ("2026-09-16", "2026-10-20")}.items():
        s0, s1 = L.snapshot(acct, ps), L.snapshot(acct, pe)
        w = F[(F.day > ps) & (F.day <= pe)]
        rows = []
        for tk in set(s0) | set(s1) | set(w.ticker):
            ww = w[w.ticker == tk]
            bu = (ww[ww.side == "buy"].qty * ww[ww.side == "buy"].price).sum()
            se = (ww[ww.side == "sell"].qty * ww[ww.side == "sell"].price).sum()
            rows.append(dict(ticker=tk, book=bm.get(tk, "UNKNOWN"), pnl=s1.get(tk, 0) - s0.get(tk, 0) + se - bu - L.FEE * (bu + se)))
        R = pd.DataFrame(rows).sort_values("pnl"); R.to_csv(f"{HERE}/window_{name}_{acct}.csv", index=False)
        dn = float(nav[pe] - nav[ps]); bb = R.groupby("book").pnl.sum()
        out[name] = dict(start=ps, end=pe, nav0=float(nav[ps]), nav1=float(nav[pe]), dnav=round(dn),
                         dnav_pct=round(100 * dn / nav[ps], 3), by_book={k: round(v) for k, v in bb.sort_values().items()},
                         by_book_pct_nav={k: round(100 * v / nav[ps], 3) for k, v in bb.sort_values().items()},
                         residual=round(dn - bb.sum()), top_losers=R.head(5).round(0).to_dict("records"))
    res[acct] = out
json.dump(res, open(f"{HERE}/recent_window.json", "w"), ensure_ascii=False, indent=1, default=float)
print("=====RECENT"); print(json.dumps(res, ensure_ascii=False, indent=1, default=float))
