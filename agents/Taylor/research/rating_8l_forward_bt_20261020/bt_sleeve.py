"""B2 — sleeve G1 có phí theo PREREG_BT.md (commit 2991ee58d). EXPLORATORY, PAPER-ONLY, read-only.
Đầu vào: ../rating_8l_lag_p2_20261020/raw/{fa,tf,univ}.parquet + raw/px_pin.parquet (tav2_pin.ticker_pin_202610)
+ data/benchmark/vnindex_tr_daily.csv (lịch) + idle_rate_proxy_dep1m_aaed41eec.py (tier dep1m).
Ra: out_bt_daily_<run>.csv, out_bt_tx_<run>.csv, out_bt_capacity.csv. Chạy: OMP_NUM_THREADS=1 $DNA_PYEXE bt_sleeve.py"""
import os
import sys

import numpy as np
import pandas as pd
import db_dtypes  # noqa: F401

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
sys.path.insert(0, HERE)
import idle_rate_proxy_dep1m_aaed41eec as irp  # noqa: E402

WC = "/home/trido/thanhdt/WorkingClaude"
RAW1 = "../rating_8l_lag_p2_20261020/raw"
EFF_MIN, EFF_MAX = pd.Timestamp("2014-07-01"), pd.Timestamp("2026-07-31")
TC, NAME_CAP, ADV_PART, RAMP, MAX_DEFER, MIN_TRANCHE = 0.001, 0.10, 0.20, 3, 5, 0.005
ADV_WIN, ADV5 = 60, 5e9


def rd(path):
    df = pd.read_parquet(path)
    for c in ("time", "Release_Date"):
        if c in df:
            df[c] = pd.to_datetime(df[c].astype(str), errors="coerce")
    return df


# ---------- lịch + giá (pin) ----------
px = rd("raw/px_pin.parquet")
PX_END = px.time.max()
cal = pd.read_csv(f"{WC}/data/benchmark/vnindex_tr_daily.csv", parse_dates=["date"]).date.sort_values()
cal = pd.DatetimeIndex(cal[(cal >= "2013-09-01") & (cal <= PX_END)])
close_raw = px.pivot(index="time", columns="ticker", values="Close").reindex(cal)
OBS = close_raw.notna().values
CL = close_raw.ffill().values
TV = (px.assign(tv=px.Price * px.Volume).pivot(index="time", columns="ticker", values="tv").reindex(cal)).values
TIX = {t: j for j, t in enumerate(close_raw.columns)}
univ = rd(f"{RAW1}/univ.parquet").assign(v=True).pivot(index="time", columns="ticker", values="v")
U = univ.reindex(cal).reindex(columns=close_raw.columns).fillna(False).astype(bool).values

# ---------- sự kiện G1 (luật loại ca vòng 2; KHÔNG dùng lọc nhìn sau phiên 0) ----------
fa = rd(f"{RAW1}/fa.parquet").sort_values(["ticker", "time"])
fa["prev"] = fa.groupby("ticker").rating.shift()
ev = fa[fa.prev.notna()].copy()
ev["grp"] = np.select([ev.rating == ev.prev, (ev.prev >= 4) & (ev.rating <= 3), (ev.prev <= 3) & (ev.rating >= 4)],
                      ["G0", "G1", "G2"], "G3")
tf = rd(f"{RAW1}/tf.parquet")
tf["qend"] = pd.PeriodIndex(tf.quarter, freq="Q").end_time.normalize()
tf = tf.sort_values(["ticker", "qend"])
tf["prev_rd"] = tf.groupby("ticker").Release_Date.shift()
tf["rd_lag"] = (tf.Release_Date - tf.qend).dt.days
tf["x_null"] = tf.Release_Date.isna()
tf["x_definite"] = (tf.rd_lag < 0) | (tf.Release_Date.notna() & tf.prev_rd.notna() & (tf.Release_Date <= tf.prev_rd))
tf["x_early7"] = tf.rd_lag.between(0, 7)
tf["eff"] = tf.Release_Date.fillna(tf.time)
tf = tf.sort_values("qend").drop_duplicates(["ticker", "eff"], keep="last")
ev = ev.merge(tf[["ticker", "eff", "quarter", "x_null", "x_definite", "x_early7"]],
              left_on=["ticker", "time"], right_on=["ticker", "eff"], how="left")
ev = ev[ev.quarter.notna() & (ev.time >= EFF_MIN) & (ev.time <= EFF_MAX) & (ev.grp == "G1")].copy()
peek7 = pd.read_csv(f"{WC}/mike/agents/Taylor/research/rating_8l_lag_20261020/out_phase3_definite_peek_cases.csv")
ev["x_peek7"] = pd.MultiIndex.from_frame(ev[["ticker", "quarter"]]).isin(pd.MultiIndex.from_frame(peek7[["ticker", "quarter"]]))
n_raw = len(ev)
ev = ev[~(ev.x_null | ev.x_definite | ev.x_early7 | ev.x_peek7)].copy()
ev["i0"] = cal.searchsorted(ev.time.values)
ev["j"] = ev.ticker.map(TIX)
n_nopx = int(ev.j.isna().sum())
ev = ev[ev.j.notna()].copy()
ev["j"] = ev.j.astype(int)
ev = ev[ev.i0 + 1 < len(cal)]
ev["in_univ0"] = U[ev.i0.values, ev.j.values]
n_notuniv = int((~ev.in_univ0).sum())
ev = ev[ev.in_univ0].copy()
adv = []
for i0, j in zip(ev.i0, ev.j):
    w = TV[max(i0 - ADV_WIN, 0):i0, j]
    adv.append(np.nanmedian(w) if np.isfinite(w).any() else 0.0)
ev["adv"] = adv
ev = ev.sort_values(["i0", "ticker"]).reset_index(drop=True)
EV_STATS = dict(g1_in_window=n_raw, after_excl_rules=n_raw - 0, no_px=n_nopx, not_univ0=n_notuniv, eligible=len(ev))
print(f"G1 eff∈[{EFF_MIN.date()},{EFF_MAX.date()}]: {n_raw} | sau luật loại ca+giá+universe: {len(ev)} "
      f"(không giá {n_nopx}, không in_universe phiên 0 {n_notuniv}) | giá pin tới {PX_END.date()}")

# ---------- lãi tiền nhàn rỗi ----------
DAYS = np.r_[0, np.diff(cal.values).astype("timedelta64[D]").astype(int)]
RATE = {"pin0": np.zeros(len(cal)),
        "pin1M": np.array([irp.r_idle(d.date(), tier="dep1m") / 100.0 if d >= pd.Timestamp("2014-01-01") else np.nan
                           for d in cal])}


def simulate(H, cap0, idle, adv_min=0.0, tag=""):
    """Một chân. Thứ tự trong phiên t: lãi (cash ngày t−1 × r × ngày lịch/365) → bán đến hạn → mua tranche. Khớp ở Close."""
    t0 = int(cal.searchsorted(EFF_MIN))
    cash, nav = float(cap0), float(cap0)
    lots = []                       # dict(ticker j, sh, exit_i, ev_id)
    pend_buy = []                   # dict(ev_id, j, due_i, val, tries)
    held_ev = {}                    # j -> ev_id đang giữ (chặn trùng mã)
    tx, daily = [], []
    cnt = dict(events=0, adv_capped=0, adv_zero=0, adv5_filtered=0, dup_ticker=0, tranche_cash_short=0,
               tranche_skipped_small=0, tranche_no_price=0, exit_deferred=0, exit_forced_lastpx=0)
    by_i0 = {i: g for i, g in ev.groupby("i0")}
    rate = RATE[idle]
    for t in range(t0, len(cal)):
        # 1) lãi
        intr = cash * rate[t] * DAYS[t] / 365.0 if cash > 0 and t > t0 else 0.0
        cash += intr
        # 2) bán
        keep = []
        for L in lots:
            if t < L["exit_i"]:
                keep.append(L); continue
            j = L["j"]
            if not OBS[t, j] and t - L["exit_i"] < MAX_DEFER and t < len(cal) - 1:
                if t == L["exit_i"]:
                    cnt["exit_deferred"] += 1
                keep.append(L); continue
            if not OBS[t, j]:
                cnt["exit_forced_lastpx"] += 1
            amt = L["sh"] * CL[t, j]; fee = amt * TC
            cash += amt - fee
            tx.append((cal[t], "SELL", close_raw.columns[j], L["sh"], CL[t, j], amt, fee, L["ev"]))
        lots = keep
        open_j = {L["j"] for L in lots} | {p["j"] for p in pend_buy}
        held_ev = {j: e for j, e in held_ev.items() if j in open_j}
        # 3) mua tranche đến hạn
        nav_now = cash + sum(L["sh"] * CL[t, L["j"]] for L in lots)
        still = []
        for p in pend_buy:
            if p["due_i"] > t:
                still.append(p); continue
            j = p["j"]
            if not OBS[t, j]:
                if t - p["due_i"] < MAX_DEFER:
                    still.append(p)
                else:
                    cnt["tranche_no_price"] += 1
                continue
            val = p["val"]
            if val * (1 + TC) > cash:
                cnt["tranche_cash_short"] += 1
                val = cash / (1 + TC)
            if val < MIN_TRANCHE * nav_now:
                cnt["tranche_skipped_small"] += 1; continue
            sh = val / CL[t, j]; fee = val * TC
            cash -= val + fee
            lots.append(dict(j=j, sh=sh, exit_i=t + H, ev=p["ev"]))
            tx.append((cal[t], "BUY", close_raw.columns[j], sh, CL[t, j], val, fee, p["ev"]))
        pend_buy = still
        # 4) tín hiệu phiên t (đóng cửa phiên 0) ⇒ lên lịch tranche +1..+3
        nav = cash + sum(L["sh"] * CL[t, L["j"]] for L in lots)
        if t in by_i0:
            for e in by_i0[t].itertuples():
                cnt["events"] += 1
                if e.adv < adv_min:
                    cnt["adv5_filtered"] += 1; continue
                if e.j in held_ev:
                    cnt["dup_ticker"] += 1; continue
                if e.adv <= 0:
                    cnt["adv_zero"] += 1; continue
                tgt = NAME_CAP * nav
                if tgt > RAMP * ADV_PART * e.adv:
                    cnt["adv_capped"] += 1; tgt = RAMP * ADV_PART * e.adv
                held_ev[e.j] = e.Index
                for k in range(1, RAMP + 1):
                    pend_buy.append(dict(ev=e.Index, j=e.j, due_i=t + k, val=tgt / RAMP))
        stock = sum(L["sh"] * CL[t, L["j"]] for L in lots)
        daily.append((cal[t], cash, stock, cash + stock, intr, len({L["j"] for L in lots})))
    D = pd.DataFrame(daily, columns=["date", "cash", "stock", "nav", "interest", "n_names"])
    T = pd.DataFrame(tx, columns=["date", "side", "ticker", "shares", "price", "amount", "fee", "ev_id"])
    D.to_csv(f"out_bt_daily_{tag}.csv", index=False); T.to_csv(f"out_bt_tx_{tag}.csv", index=False)
    return D, T, cnt


def selfcheck(D, T, cap0, tag):
    """0 VND: (i) cash dựng lại ĐỘC LẬP từ TX + lãi; (ii) NAV dựng lại từ vị thế suy từ TX × Close."""
    flow = T.assign(f=np.where(T.side == "SELL", T.amount - T.fee, -(T.amount + T.fee))).groupby("date").f.sum()
    c = cap0 + (flow.reindex(D.date).fillna(0).values + D.interest.values).cumsum()
    r1 = np.abs(c - D.cash.values).max()
    pos = T.assign(s=np.where(T.side == "BUY", T.shares, -T.shares)).pivot_table(
        index="date", columns="ticker", values="s", aggfunc="sum").reindex(D.date).fillna(0).cumsum()
    cl = pd.DataFrame(CL, index=cal, columns=close_raw.columns).reindex(index=D.date, columns=pos.columns)
    mv = np.where(np.abs(pos.values) > 1e-9, pos.values * cl.values, 0.0)       # vị thế 0 × giá NaN (chưa niêm yết) = 0
    r2 = np.abs(mv.sum(axis=1) + D.cash.values - D.nav.values).max()
    print(f"  self-check {tag}: |cash dựng lại − cash| max {r1:.6f} VND · |NAV dựng lại − NAV| max {r2:.6f} VND")
    assert r1 < 1 and r2 < 1, "self-check 0 VND trượt"
    return r1, r2


if __name__ == "__main__":
    RUNS = [("V1_H40", 40, 0.0), ("V2_H20", 20, 0.0), ("V3_H40_adv5", 40, ADV5)]
    caprows = []
    for name, H, amin in RUNS:
        for idle in ("pin0", "pin1M"):
            tag = f"{name}_{idle}_2p5B"
            D, T, cnt = simulate(H, 2.5e9, idle, amin, tag)
            selfcheck(D, T, 2.5e9, tag)
            caprows.append(dict(run=tag, **cnt, n_buy=int((T.side == "BUY").sum()),
                                names_mean=D.n_names.mean(), names_p90=D.n_names.quantile(0.9), names_max=D.n_names.max(),
                                util_mean=(D.stock / D.nav).mean(), final_nav=D.nav.iloc[-1]))
            print(f"{tag}: NAV cuối {D.nav.iloc[-1] / 1e9:.3f} tỷ | {cnt}")
    D, T, cnt = simulate(40, 50e9, "pin0", 0.0, "V1_H40_pin0_50B")
    selfcheck(D, T, 50e9, "V1_H40_pin0_50B")
    caprows.append(dict(run="V1_H40_pin0_50B", **cnt, n_buy=int((T.side == "BUY").sum()), names_mean=D.n_names.mean(),
                        names_p90=D.n_names.quantile(0.9), names_max=D.n_names.max(),
                        util_mean=(D.stock / D.nav).mean(), final_nav=D.nav.iloc[-1]))
    print(f"V1_H40_pin0_50B: NAV cuối {D.nav.iloc[-1] / 1e9:.3f} tỷ | {cnt}")
    pd.DataFrame(caprows).to_csv("out_bt_capacity.csv", index=False)
    pd.Series(EV_STATS).to_csv("out_bt_eventstats.csv")
