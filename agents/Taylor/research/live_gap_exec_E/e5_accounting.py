"""E5 (Luồng E, job Taylor_20261112_151839→162006) — replay TỐI THIỂU dạng KẾ TOÁN (không phải engine), cửa sổ = WIN của GĐ0.
W3 DISC (lệnh tay): P&L_VND = MV_DISC(cuối, giá broker thực) − MV_DISC(đầu) + Σbán − Σmua (fills_booked book=DISCRETIONARY_SPECIAL,
   ngày ≤ cuối kỳ). pp = P&L / NAV đầu kỳ (xấp xỉ bậc 1; cổ tức tiền mặt DISC KHÔNG tính — chưa có nguồn đối soát).
W4 fill thật vs giá engine: engine khớp ở OPEN phiên khớp ⇒ chi phí lệnh = sgn·(fill − open)/open (slip_vs_open_bps của GĐ0,
   Price thực + adj_f), notional VND; pp = −Σ cost_bps·notional / NAV_{ngày}. Tách non-DISC (thuộc engine) và DISC (thuộc W3).
W5 egg: Σ_t egg_{t}/NAV_{t} × EGG_DAILY_RATE × số ngày lịch tới phiên kế (rate ĐO 0,023397%/ngày ≈ 8,54%/năm, cash_identity.md).
   ZaloPay: egg nằm trong nav_b (= nav_a − outside_mv DGC) ⇒ W5 sleeve = Σ egg/nav_b; báo kèm egg/NAV TK."""
import json, os, sys
import pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../live_gap_phase1c_20261112")))
import decompose3 as D3
R = os.path.dirname(os.path.abspath(__file__)); P0 = f"{R}/../live_gap_phase0_20261112"; LB = f"{D3.R}/live_books"
EGG_DAILY = 0.00023397
out = []
for acct in ("SpaceX", "ZaloPay"):
    a, b = D3.WIN[acct]
    h = pd.read_csv(f"{D3.EL}/nav_history_{acct}.csv").drop_duplicates("date", keep="last").set_index("date").sort_index()
    if acct == "ZaloPay":
        s = pd.read_csv(f"{D3.EL}/nav_sleeve_history_ZaloPay.csv").drop_duplicates("date", keep="last").set_index("date").sort_index()
        navS = s["nav_b"].astype(float)
    else:
        navS = h["nav"].astype(float)
    nav0 = float(navS[navS.index <= a].iloc[-1]) if (navS.index <= a).any() else float(navS.iloc[0])
    # W3
    F = pd.read_csv(f"{P0}/fills_booked.csv"); F = F[(F.acct == acct) & (F.date > a) & (F.date <= b)]
    Fd = F[F.book == "DISCRETIONARY_SPECIAL"]
    buy = float(Fd[Fd.side == "buy"].notional.sum()); sell = float(Fd[Fd.side == "sell"].notional.sum())
    H = json.load(open(f"{LB}/{acct}_{b}.json"))
    disc_t = {l["ticker"] for l in H["lots"] if l["book"] == "DISCRETIONARY_SPECIAL"}
    qd = {}
    for l in H["lots"]:
        if l["book"] == "DISCRETIONARY_SPECIAL": qd[l["ticker"]] = qd.get(l["ticker"], 0) + l["qty"]
    mv_end = sum(q * (H["broker_positions"][t].get("broker_market_price") or H["broker_positions"][t]["market_price"]) for t, q in qd.items())
    pnl3 = mv_end - 0.0 + sell - buy
    per = {}
    for t in set(Fd.ticker) | set(qd):
        g = Fd[Fd.ticker == t]; bp = H["broker_positions"].get(t, {})
        per[t] = qd.get(t, 0) * (bp.get("broker_market_price") or bp.get("market_price") or 0) + g[g.side == "sell"].notional.sum() - g[g.side == "buy"].notional.sum()
    # W4
    S = pd.read_csv(f"{P0}/slippage_all.csv"); S = S[(S.account == acct) & (S.trans_date > a) & (S.trans_date <= b) & (S.fill_qty > 0)].copy()
    bk = pd.read_csv(f"{P0}/fills_booked.csv", dtype={"child_oid": str})[["child_oid", "book"]].dropna().drop_duplicates("child_oid")
    S["order_id"] = S["order_id"].astype(str); S = S.merge(bk, left_on="order_id", right_on="child_oid", how="left")
    S["notional"] = S["fill_qty"] * S["avg_fill_price"]
    navd = navS.copy(); navd.index = navd.index.astype(str)
    S["nav"] = S["trans_date"].map(lambda d: float(navd[navd.index <= d].iloc[-1]) if (navd.index <= d).any() else nav0)
    S["pp"] = -S["slip_vs_open_bps"] / 1e4 * S["notional"] / S["nav"] * 100
    if acct == "ZaloPay": S = S[S.ticker != "DGC"]
    isd = S["book"].eq("DISCRETIONARY_SPECIAL")
    w4 = float(S.loc[~isd, "pp"].sum()); w4d = float(S.loc[isd, "pp"].sum()); w4_unbooked = int(S["book"].isna().sum())
    w4_pre = float(S.loc[~isd & (S.trans_date <= "2026-08-25"), "pp"].sum()); w4_post = float(S.loc[~isd & (S.trans_date > "2026-08-25"), "pp"].sum())
    # W5
    eg = h["egg_assets"].fillna(0).astype(float); dts = pd.to_datetime(h.index)
    days = pd.Series(dts, index=h.index).diff().shift(-1).dt.days.fillna(1)
    m = (h.index > a) & (h.index <= b)
    # lãi tích luỹ trong khoảng (t, t_next]: dùng egg cuối phiên t × số ngày; phiên cuối kỳ không cộng tiếp
    m2 = (h.index >= a) & (h.index < b)
    navTK = h["nav"].astype(float)
    w5_tk = float((eg[m2] / navTK[m2] * EGG_DAILY * days[m2]).sum()) * 100
    if acct == "ZaloPay":
        nb = navS.reindex(h.index).ffill()
        w5_sl = float((eg[m2] / nb[m2] * EGG_DAILY * days[m2]).sum()) * 100  # egg nằm TRONG nav_b (nav_a − outside_mv) ⇒ mẫu số sleeve
        egg_share = float((eg[m2] / navTK[m2]).mean())
    else:
        w5_sl = w5_tk; egg_share = float((eg[m2] / navTK[m2]).mean())
    out.append(dict(TK=acct, win=f"{a}->{b}", nav0=nav0, W3_disc_pnl_vnd=pnl3, W3_pp=100 * pnl3 / nav0, W3_detail=";".join(f"{t}:{v/1e6:+.1f}M" for t, v in sorted(per.items(), key=lambda x: x[1])),
                    W3_buy=buy, W3_sell=sell, W3_mv_end=mv_end, W4_nonDISC_pp=w4, W4_pre0825_pp=w4_pre, W4_post0825_pp=w4_post, W4_DISC_pp=w4d,
                    W4_n_orders=len(S), W4_unbooked=w4_unbooked, W4_notional=float(S.notional.sum()), W5_pp_TK=w5_tk, W5_pp_sleeve=w5_sl, egg_share_mean=egg_share))
T = pd.DataFrame(out)
# W3 CHÍNH = P&L nắm giữ theo SỔ (lots book=DISCRETIONARY_SPECIAL, Close điều chỉnh ⇒ gồm cổ tức/thưởng), từ resid_bybook.py.
# Lý do: fills_booked THIẾU lệnh bán DISC (SpaceX DRI 3700 mua − 2500 bán nhưng 11/11 broker 0 cp; tương tự ZaloPay) ⇒ W3 theo fills sai dấu.
RB = pd.read_csv(f"{R}/resid_bybook_live.csv"); RB = RB[RB.book == "DISCRETIONARY_SPECIAL"].groupby("TK").pp.sum()
T["W3_lots_pp"] = T.TK.map(RB)
T.to_csv(f"{R}/e5_accounting.csv", index=False, float_format="%.4f")
pd.set_option("display.width", 250); print(T.T.to_string())
