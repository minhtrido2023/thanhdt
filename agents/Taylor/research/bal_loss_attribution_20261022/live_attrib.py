"""Q1+Q2 live: NAV DD, BAL (VPI) P&L đối soát broker, P&L theo sổ trong cửa sổ đỉnh→đáy, phân rã VPI.
READ-ONLY. Chạy: python3 live_attrib.py  (theo PREREG.md md5 bbecd438...)."""
import csv, glob, json, re, os
import numpy as np, pandas as pd

W = "/home/trido/thanhdt/WorkingClaude"
E = f"{W}/data/execution_logs"
HERE = os.path.dirname(os.path.abspath(__file__))
FEE = 0.00097
ACCTS = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}


def load_fills(acct):
    rows = []
    for f in sorted(glob.glob(f"{E}/exec_{acct}_*_journal.csv")):
        day = re.search(r"(\d{4}-\d{2}-\d{2})", f).group(1)
        rd = csv.reader(open(f))
        hdr = next(rd)
        for r in rd:
            if len(r) < 9 or r[1] != "FILL":
                continue
            rows.append(dict(day=day, ts=r[0], pid=r[2], ticker=r[3], side=r[4], qty=float(r[6]),
                             price=float(r[7]), book=r[9] if len(r) > 9 else "",
                             play=r[10] if len(r) > 10 else ""))
    return pd.DataFrame(rows)


def broker_fills(acct, ticker, days):
    """Lệnh đã khớp từ dnse_raw (lọc account_no, §12): id -> (side, fillQty, avgPrice)."""
    out = {}
    for d in days:
        p = f"{E}/dnse_raw_{d}.jsonl"
        if not os.path.exists(p):
            continue
        for l in open(p):
            r = json.loads(l)
            if r.get("kind") != "orders" or str(r.get("account_no")) != ACCTS[acct]:
                continue
            for o in r["payload"].get("orders", []):
                if str(o.get("accountNo")) != ACCTS[acct] or o.get("symbol") != ticker:
                    continue
                if (o.get("fillQuantity") or 0) > 0:
                    out[o["id"]] = (d, o["side"], o["fillQuantity"], o["averagePrice"])
    return out


def nav_dd(acct):
    n = pd.read_csv(f"{E}/nav_history_{acct}.csv", parse_dates=["date"])
    n = n.drop_duplicates("date", keep="last").sort_values("date")
    nav = n.set_index("date")["nav"]
    peak = nav.cummax()
    dd = nav / peak - 1
    t = dd.idxmin()
    p = nav.loc[:t].idxmax()
    return nav, p, t, dd.min()


def snapshot(acct, d):
    p = f"{E}/verified_snapshot_{acct}_{d}.json"
    if not os.path.exists(p):
        return None
    js = json.load(open(p))
    return {x["ticker"]: x["mtm_value"] for x in js["positions"]}


def book_map(acct, fills):
    m = {}
    for _, r in fills.sort_values("ts").iterrows():
        if r.book:
            m[r.ticker] = r.book
    for f in sorted(glob.glob(f"{W}/data/trade_plans/plan_{acct}_2026-*.json")):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        for o in d.get("orders") or []:
            b = o.get("book") or o.get("strategy")
            if b and o.get("ticker") and o["ticker"] not in m:
                m[o["ticker"]] = b
    return m


out = {}
bq = pd.read_csv(f"{HERE}/bq_vpi_vni.csv", parse_dates=["time"])
px = bq.pivot(index="time", columns="ticker", values="Close")
for acct in ACCTS:
    F = load_fills(acct)
    nav, p, t, mdd = nav_dd(acct)
    res = dict(nav_first=(str(nav.index[0].date()), float(nav.iloc[0])),
               nav_last=(str(nav.index[-1].date()), float(nav.iloc[-1])),
               peak=(str(p.date()), float(nav[p])), trough=(str(t.date()), float(nav[t])),
               maxdd_pct=round(100 * mdd, 3))
    # --- BAL P&L
    b = F[F.book == "BAL"]
    buy = b[b.side == "buy"]; sell = b[b.side == "sell"]
    bv = (buy.qty * buy.price).sum(); sv = (sell.qty * sell.price).sum()
    fee = FEE * (bv + sv)
    first_buy = buy.day.min()
    nav_pre = float(nav[nav.index < first_buy].iloc[-1])
    bf = broker_fills(acct, "VPI", sorted(set(b.day)))
    bb = sum(q * a for d, s, q, a in bf.values() if s == "NB"); bs = sum(q * a for d, s, q, a in bf.values() if s == "NS")
    bqb = sum(q for d, s, q, a in bf.values() if s == "NB"); bqs = sum(q for d, s, q, a in bf.values() if s == "NS")
    res["bal"] = dict(tickers=sorted(set(b.ticker)), qty_buy=float(buy.qty.sum()), qty_sell=float(sell.qty.sum()),
                      buy_value=bv, sell_value=sv, fee_est=round(fee), pnl_net=round(sv - bv - fee),
                      pnl_gross=round(sv - bv), avg_buy=bv / buy.qty.sum(), avg_sell=sv / sell.qty.sum(),
                      ret_gross_pct=round(100 * (sv / bv - 1), 3), ret_net_pct=round(100 * ((sv * (1 - FEE)) / (bv * (1 + FEE)) - 1), 3),
                      nav_before=nav_pre, pnl_pct_nav=round(100 * (sv - bv - fee) / nav_pre, 3),
                      buy_value_pct_nav=round(100 * bv / nav_pre, 3),
                      broker=dict(qty_buy=bqb, qty_sell=bqs, buy_value=bb, sell_value=bs,
                                  diff_buy_vnd=round(bb - bv), diff_sell_vnd=round(bs - sv)))
    # --- P&L theo sổ trong cửa sổ đỉnh→đáy
    ps, pe = str(p.date()), str(t.date())
    s0, s1 = snapshot(acct, ps), snapshot(acct, pe)
    bm = book_map(acct, F)
    if s0 is not None and s1 is not None:
        w = F[(F.day > ps) & (F.day <= pe)]
        tick = set(s0) | set(s1) | set(w.ticker)
        rows = []
        for tk in tick:
            ww = w[w.ticker == tk]
            bu = (ww[ww.side == "buy"].qty * ww[ww.side == "buy"].price).sum()
            se = (ww[ww.side == "sell"].qty * ww[ww.side == "sell"].price).sum()
            pnl = s1.get(tk, 0) - s0.get(tk, 0) + se - bu - FEE * (bu + se)
            rows.append(dict(ticker=tk, book=bm.get(tk, "UNKNOWN"), mv0=s0.get(tk, 0), mv1=s1.get(tk, 0),
                             buys=bu, sells=se, pnl=pnl))
        R = pd.DataFrame(rows).sort_values("pnl")
        R.to_csv(f"{HERE}/window_pnl_by_ticker_{acct}.csv", index=False)
        bybook = R.groupby("book").pnl.sum().sort_values()
        dnav = float(nav[t] - nav[p])
        res["window_by_book"] = {k: round(v) for k, v in bybook.items()}
        res["window_dnav"] = round(dnav)
        res["window_residual"] = round(dnav - bybook.sum())
        res["window_top_losers"] = R.head(6)[["ticker", "book", "pnl"]].round(0).to_dict("records")
    else:
        res["window_by_book"] = f"thiếu verified_snapshot {ps if s0 is None else ''} {pe if s1 is None else ''}"
    # --- BAL vị thế ngày 21/10
    s21 = snapshot(acct, "2026-10-21")
    res["bal_positions_2026_10_21"] = [tk for tk in (s21 or {}) if bm.get(tk) == "BAL"] if s21 else "không có snapshot"
    out[acct] = res

# --- Q2 VPI phân rã
r = np.log(px).diff()
entry_day = pd.Timestamp("2026-09-17"); exit_day = pd.Timestamp("2026-10-16")
pre = r.loc[:entry_day - pd.Timedelta(days=1)].dropna().tail(250)
beta = float(np.polyfit(pre["VNINDEX"], pre["VPI"], 1)[0])
corr = float(pre.corr().loc["VPI", "VNINDEX"])
vni0 = float(px["VNINDEX"].loc[:entry_day - pd.Timedelta(days=1)].iloc[-1]); vni1 = float(px.loc[exit_day, "VNINDEX"])
R_vni = vni1 / vni0 - 1
sx = out["SpaceX"]["bal"]; zp = out["ZaloPay"]["bal"]
R_vpi = (sx["sell_value"] + zp["sell_value"]) / (sx["buy_value"] + zp["buy_value"]) - 1
close = px["VPI"].dropna()
pre_c = close.loc[:entry_day - pd.Timedelta(days=1)]
avg_buy = (sx["buy_value"] + zp["buy_value"]) / (sx["qty_buy"] + zp["qty_buy"])
out["VPI"] = dict(beta_250d=round(beta, 3), corr_250d=round(corr, 3), n_obs=len(pre),
                  vni_close_pre_entry=vni0, vni_close_exit=vni1, R_vni_pct=round(100 * R_vni, 3),
                  R_vpi_gross_pct=round(100 * R_vpi, 3),
                  beta_part_pct=round(100 * beta * R_vni, 3), resid_pct=round(100 * (R_vpi - beta * R_vni), 3),
                  resid_beta1_pct=round(100 * (R_vpi - R_vni), 3),
                  icb=int(bq[bq.ticker == "VPI"].ICB_Code.dropna().iloc[-1]),
                  avg_buy=round(avg_buy), max20=float(pre_c.tail(20).max()), max250=float(pre_c.tail(250).max()),
                  buy_vs_max20_pct=round(100 * (avg_buy / pre_c.tail(20).max() - 1), 2),
                  buy_vs_max250_pct=round(100 * (avg_buy / pre_c.tail(250).max() - 1), 2),
                  ret60_pre_pct=round(100 * (pre_c.iloc[-1] / pre_c.iloc[-61] - 1), 2),
                  close_2026_10_21=float(close.loc["2026-10-21"]), vni_ret_2026_10_21_pct=round(100 * (px.loc["2026-10-21", "VNINDEX"] / px.loc["2026-10-20", "VNINDEX"] - 1), 3),
                  vpi_ret_2026_10_21_pct=round(100 * (close.loc["2026-10-21"] / close.loc["2026-10-20"] - 1), 3),
                  vpi_21_vs_avg_sell_pct=round(100 * (close.loc["2026-10-21"] / ((sx["sell_value"] + zp["sell_value"]) / (sx["qty_sell"] + zp["qty_sell"])) - 1), 2),
                  vpi_min_close_window=float(close.loc[entry_day:"2026-10-21"].min()),
                  vpi_min_close_date=str(close.loc[entry_day:"2026-10-21"].idxmin().date()))
json.dump(out, open(f"{HERE}/live_attrib.json", "w"), ensure_ascii=False, indent=1, default=float)
print(json.dumps(out, ensure_ascii=False, indent=1, default=float))
