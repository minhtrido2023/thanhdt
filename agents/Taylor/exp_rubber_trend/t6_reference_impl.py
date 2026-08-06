#!/usr/bin/env python3
"""T6 — reference implementation of the proposed TREND_BREAK tier + selfcheck.
NOT wired into rubber_weekly.py (design/research job; wiring waits for user approval).

Design (from T2-T5):
  * line   = MA10 on the WB MONTHLY series (= MA200 daily equivalent). NOT an OLS
             trendline (T5A: precision 49-53% vs 73-85%), NOT the daily feed
             (T5B: daily crosses 5.2x more often than monthly on the same asset).
  * event  = price closes below the line, confirmed on 2 consecutive MONTHS.
  * state  = the tier is a STATE (DOWNTREND / UPTREND), not a one-shot event; the
             cross back above (confirmed 2 months) closes the episode.
  * the current partial month is estimated from the daily feed, and a signal that
    depends on that estimate is flagged PROVISIONAL until WB publishes the month.
"""
import numpy as np, pandas as pd, sys

W = "/home/trido/thanhdt/WorkingClaude"
MA_WIN, CONFIRM = 10, 2


def monthly_with_current(monthly_csv, daily_csv=None):
    """WB monthly series + a provisional point for the current month built from the
    daily feed's REAL prints (src != wb_seed). Returns (series, provisional_month|None)."""
    m = pd.read_csv(monthly_csv)
    s = pd.Series(m["price"].astype(float).values,
                  index=pd.to_datetime(m["month"].astype(str) + "-15"))
    s = s[s.notna()].sort_index()
    prov = None
    if daily_csv:
        d = pd.read_csv(daily_csv)
        d["date"] = pd.to_datetime(d["date"])
        real = d[(d["src"] != "wb_seed") & d["rss3_usdkg"].notna()]
        if len(real):
            last_wb = s.index[-1].to_period("M")
            newer = real[real["date"].dt.to_period("M") > last_wb]
            for per, g in newer.groupby(newer["date"].dt.to_period("M")):
                s.loc[pd.Timestamp(f"{per}-15")] = float(g["rss3_usdkg"].mean())
                prov = str(per)
            s = s.sort_index()
    return s, prov


def trend_state(s, win=MA_WIN, confirm=CONFIRM):
    """Return the current trend state and the episode that produced it."""
    ma = s.rolling(win).mean()
    below = (s < ma) & ma.notna()
    if ma.isna().all():
        return {"state": "UNKNOWN", "note": f"cần >= {win} tháng, mới có {len(s)}"}
    # confirmed regime: flip only after `confirm` consecutive months on the new side
    state, since, states = "UPTREND", s.index[0], []
    for i in range(len(s)):
        if ma.isna().iloc[i]:
            states.append(None); continue
        w = below.iloc[max(0, i - confirm + 1):i + 1]
        if len(w) == confirm and w.all() and state != "DOWNTREND":
            state, since = "DOWNTREND", s.index[i]
        elif len(w) == confirm and (~w).all() and state != "UPTREND":
            state, since = "UPTREND", s.index[i]
        states.append(state)
    cur_ma = float(ma.iloc[-1]); cur = float(s.iloc[-1])
    return {"state": state, "since": since, "price": cur, "ma": cur_ma,
            "dist_pct": (cur / cur_ma - 1) * 100,
            "months_below": int(below.iloc[-confirm:].sum()),
            "states": pd.Series(states, index=s.index)}


# ------------------------------------------------------------------ selfcheck ---
def selfcheck():
    ok = fail = 0
    def chk(name, cond):
        nonlocal ok, fail
        if cond: ok += 1
        else: fail += 1; print(f"  FAIL: {name}")

    idx = pd.date_range("2000-01-15", periods=40, freq="MS") + pd.Timedelta(days=14)

    # 1. flat series -> never below its own MA -> UPTREND, no flip
    flat = pd.Series(2.0, index=idx)
    r = trend_state(flat)
    chk("flat series stays UPTREND", r["state"] == "UPTREND")
    chk("flat series dist 0%", abs(r["dist_pct"]) < 1e-9)

    # 2. monotonic decline -> must end DOWNTREND
    dec = pd.Series(np.linspace(3.0, 1.0, 40), index=idx)
    chk("monotonic decline -> DOWNTREND", trend_state(dec)["state"] == "DOWNTREND")

    # 3. monotonic rise -> must end UPTREND
    chk("monotonic rise -> UPTREND",
        trend_state(pd.Series(np.linspace(1.0, 3.0, 40), index=idx))["state"] == "UPTREND")

    # 4. ONE month below then straight back -> confirm=2 must NOT flip
    v = np.full(40, 2.0); v[30] = 1.0
    chk("single dip does NOT flip (confirm=2)", trend_state(pd.Series(v, index=idx))["state"] == "UPTREND")

    # 5. TWO consecutive months below -> must flip. NOTE: ["state"] is the state at the
    # END of the series; two months after the dip the price is back above the (dragged-
    # down) MA and the episode correctly CLOSES. So assert on the trajectory, not the
    # final value — the first version of this test asserted the final value and failed,
    # which was the test being wrong, not the code (verified by hand: MA10 at i=31 is
    # 1.80 vs price 1.00 -> below; at i=33 price 2.00 vs MA 1.80 -> above).
    v2 = np.full(40, 2.0); v2[30] = v2[31] = 1.0
    traj = trend_state(pd.Series(v2, index=idx))["states"]
    chk("two consecutive dips DO flip to DOWNTREND", (traj == "DOWNTREND").any())
    chk("flip happens exactly at the 2nd month below", traj.iloc[31] == "DOWNTREND")
    chk("not flipped yet at the 1st month below", traj.iloc[30] == "UPTREND")
    chk("episode closes again once price recovers", traj.iloc[-1] == "UPTREND")

    # 6. too-short series -> UNKNOWN, never a confident state
    chk("short series -> UNKNOWN", trend_state(pd.Series(2.0, index=idx[:5]))["state"] == "UNKNOWN")

    # 7. causality: state at time t must not change when FUTURE points are appended
    real, _ = monthly_with_current(f"{W}/data/rubber_monthly.csv")
    full = trend_state(real)["states"]
    for cut in (120, 180, 220):
        part = trend_state(real.iloc[:cut])["states"]
        chk(f"no look-ahead at cut={cut}", (part.dropna() == full.loc[part.dropna().index]).all())

    # 8. provisional month from the daily feed lands on the right month and is a MEAN
    s2, prov = monthly_with_current(f"{W}/data/rubber_monthly.csv", f"{W}/data/rubber_weekly.csv")
    d = pd.read_csv(f"{W}/data/rubber_weekly.csv"); d["date"] = pd.to_datetime(d["date"])
    aug = d[(d["src"] != "wb_seed") & d["rss3_usdkg"].notna()]
    aug = aug[aug["date"].dt.to_period("M").astype(str) == "2026-08"]
    chk("provisional month detected", prov == "2026-08")
    chk("provisional value == mean of that month's real prints",
        abs(float(s2.loc["2026-08-15"]) - float(aug["rss3_usdkg"].mean())) < 1e-9)
    chk("provisional does not touch WB history",
        (s2.loc[:"2026-07-15"] == real.loc[:"2026-07-15"]).all())

    # 9. the WB series must not contain a wb_seed round-trip (monthly file is the source)
    chk("monthly file has no duplicate months", not real.index.duplicated().any())

    print(f"\n  selfcheck: {ok} PASS, {fail} FAIL")
    return fail == 0


if __name__ == "__main__":
    if "--selfcheck" in sys.argv:
        sys.exit(0 if selfcheck() else 1)

    s, prov = monthly_with_current(f"{W}/data/rubber_monthly.csv", f"{W}/data/rubber_weekly.csv")
    r = trend_state(s)
    print("=" * 74)
    print("TRẠNG THÁI TREND_BREAK HÔM NAY (tham chiếu, chưa wire)")
    print("=" * 74)
    print(f"  chuỗi        : {len(s)} tháng, {s.index[0]:%Y-%m} .. {s.index[-1]:%Y-%m}")
    print(f"  tháng tạm    : {prov or 'không'} (trung bình các phiên thật trong tháng)")
    print(f"  giá mới nhất : {r['price']:.3f} USD/kg")
    print(f"  MA10 tháng   : {r['ma']:.3f} USD/kg  (= MA200 ngày tương đương)")
    print(f"  khoảng cách  : {r['dist_pct']:+.1f}% so với đường")
    print(f"  TRẠNG THÁI   : {r['state']}  (từ {r['since']:%Y-%m})")
    print(f"  tháng dưới đường trong {CONFIRM} kỳ gần nhất: {r['months_below']}/{CONFIRM}")

    # last 14 months of context
    ma = s.rolling(MA_WIN).mean()
    print("\n  14 tháng gần nhất:")
    for dt in s.index[-14:]:
        st = r["states"].loc[dt]
        flag = "DƯỚI" if s.loc[dt] < ma.loc[dt] else "trên"
        pv = " (tạm)" if prov and dt.strftime("%Y-%m") == prov else ""
        print(f"    {dt:%Y-%m}  giá {s.loc[dt]:.3f}  MA10 {ma.loc[dt]:.3f}  {flag}  -> {st}{pv}")
