#!/usr/bin/env python3
"""THIRD, INDEPENDENT reconstruction of the custom30V park basket — POSITION REPLAY.

Model = the user's own (2026-09-27 17:11 ICT): hold SHARE COUNTS, mark to market at the RAW price
actually traded that session, and apply every corporate action as an EXPLICIT event on its
ex-date. Nothing here reads an adjusted price series for the mark, so it cannot inherit either of
the two chains inside `custom_basket.py` (legacy `Close_adj x OShares`, or flat `Close_adj`).

Legs (PREREG.md):
  REPLAY_A  buy-and-hold share counts between rebalances, 0,1%/side fees. The user's model.
  REPLAY_B  same event arithmetic, re-weighted DAILY to the engine's own target weights, no fees
            -> differs from the engine's FLAT leg in EXACTLY ONE variable (the return chain).
            This is the leg the 0,30pp match threshold is judged on.
  ENGINE_*  the engine's own two legs, recomputed here from the dumped panel and asserted against
            the levels `build_pit()` returned, so a disagreement in the harness itself cannot be
            mistaken for a finding.

ROUND 2 (2026-09-27, after quant-skeptic REFUTED round 1 — all three were real):
  * WEIGHT ALIGNMENT. Round 1 set the share vector at the CLOSE of session d from `wmap[d]` and
    held it into d+1, so `w_d` earned the d->d+1 return while the engine earns it on
    (d-1)->d. `wmap[d]` is already built from PREV-day `mcapw`, so round 1 ran a whole extra
    session of staleness: measured -0,395pp on the replay chain and -0,422pp on the flat chain,
    i.e. bigger than the entire 0,30pp threshold. REPLAY_B therefore differed from ENGINE_FLAT in
    TWO variables, not one. Now every leg trades at the PREVIOUS close with `w_d`, which is the
    engine's own convention.
  * SAME-DAY SHARE EVENTS ARE ADDITIVE, NOT MULTIPLICATIVE. Round 1 did `fac *= (1+q)` per event.
    Two tranches going ex the same day are each quoted against the ORIGINAL count, so the true
    factor is `1 + sum(q)`. Verified against the panel's own independently-sourced `OShares`
    column: HPG 2015-05-08 actual 1,499959 vs multiplicative 1,560000 (+4,00% phantom shares);
    HDB 2020-10-01 1,299997 vs 1,322500; MBB 2018-07-06 1,190000 vs 1,197000; SSB 2022-06-16
    1,193456 vs 1,201874. `custom_basket._match_step_date` SUMS `exercise_ratio` for the same-day
    case for exactly this reason. Round 1's bias was +0,123pp/yr upward.
  * PRE-PANEL EVENTS. `searchsorted` returns 0 for any ex-date before the first session, so round
    1 stamped 1.837 of 7.277 vintage rows onto session one and inflated every reported event count
    (rights 366 -> 195 in-window). Harmless to the NAV only because session one holds nothing.
    Now dropped explicitly and counted separately.
  * CAGR WINDOW. The level series starts 2013-12-23 but the first rebal is 2014-08-05, so round 1
    divided by 12,49y of which 0,616y was uninvested. All legs are now measured from the first
    rebal, which is also the window PREREG names (2014-08 -> 2026-06).

Mutation knobs (selfcheck only — every one of them MUST move the number):
  --mult-share-step reinstate round 1's multiplicative same-day factor (M1b)
  --no-share-step   drop the share step entirely                        (M1)
  --mark-close      mark to market on adjusted Close                    (M2)
  --no-fee          drop rebalance fees                                 (M3)
  --no-px-repair    keep the stale ex-date raw Price as-is              (M4)
  --lag-weights     reinstate round 1's 1-session weight lag            (M5)
"""
import argparse
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
TC = 0.001          # 0,1%/side, CLAUDE.md § Backtest shared cost convention
BASE_LEVEL = 1000.0
# ISS issue methods that change an EXISTING holder's share count for free.
FREE_SHARE_ISS = {"Trả Cổ tức bằng Cổ phiếu", "Cổ phiếu thưởng"}
# Price-adjusting but NOT free: the holder must pay to subscribe, and the vendor table has no
# issue price, so a replay cannot value it. Counted, never silently dropped (PREREG §4).
RIGHTS_ISS = "Quyền mua CP cho Cổ đông hiện hữu"


def cap_names(w, cap):
    """Water-fill each weight down to `cap`, redistributing to the uncapped ones.

    Same fixed point as custom_basket._cap_names; reimplemented here so the replay shares no code
    with the thing it audits (a shared helper would make an identical bug invisible in both).
    Verified equivalent to 7,5e-16 over 3.000 random vectors (quant-skeptic, 2026-09-27).
    """
    w = np.asarray(w, dtype=float).copy()
    if w.sum() <= 0:
        return w
    w = w / w.sum()
    for _ in range(100):
        over = w > cap + 1e-12
        if not over.any():
            break
        excess = float((w[over] - cap).sum())
        w[over] = cap
        free = ~over
        if not free.any() or w[free].sum() <= 0:
            break
        w[free] += excess * w[free] / w[free].sum()
    return w


def load():
    bx = pd.read_parquet(f"{HERE}/panel_bx.parquet")
    bx["time"] = pd.to_datetime(bx["time"])
    mem = pd.read_parquet(f"{HERE}/members_df.parquet")
    mem["rebal_date"] = pd.to_datetime(mem["rebal_date"])
    ev = pd.read_parquet(f"{HERE}/ca_vintage.parquet")
    for c in ("exright_date", "effective_date"):
        ev[c] = pd.to_datetime(ev[c], errors="coerce")
    ev["exercise_ratio"] = pd.to_numeric(ev["exercise_ratio"], errors="coerce")
    ev["value_per_share"] = pd.to_numeric(ev["value_per_share"], errors="coerce")
    ev["issue_method_name_vi"] = ev["issue_method_name_vi"].fillna("")
    return bx, mem, ev


def ex_date_mask(ev, px):
    """Boolean panel: does `ticker` have a PRICE-ADJUSTING corp-action going ex on this session?

    Used to bound the `Price`-staleness repair to cells where the registry says the defect lives
    (`price-volume/ticker_price_stale_on_exdate.md` is about the ex-date row specifically). Round 1
    let the ratio heuristic fire anywhere and it overwrote genuine raw quotes on non-event days
    (CVT 2016-07-01: repaired return swung 1.608bp away from every other chain).
    """
    m = pd.DataFrame(False, index=px.index, columns=px.columns)
    ds = pd.DatetimeIndex(px.index)
    for r in ev.itertuples():
        if not r.price_adjusting or r.ticker not in m.columns or pd.isna(r.exright_date):
            continue
        # bound BOTH sides. Round 2 wrote `ds[i] < px.index[0]`, which can never be true because
        # `ds[i]` is by construction >= ds[0] — so every pre-panel event still stamped session 1
        # (161 cells). The test has to be on the EVENT's date, not on the snapped session's.
        i = ds.searchsorted(r.exright_date)
        if i >= len(ds) or r.exright_date < ds[0]:
            continue
        m.iat[i, m.columns.get_loc(r.ticker)] = True
    return m


def build_prices(bx, ev, args, log):
    """Raw-price and adjusted-Close panels, with the ex-date staleness of `Price` repaired.

    Registry `price-volume/ticker_price_stale_on_exdate.md`: on ~2% of events the ex-date row's
    `Price` is the T-1 CUM price copied verbatim. For a share-count replay that is not a rounding
    nit — the share count has already stepped up while the price has not stepped down, which
    manufactures exactly the phantom return this audit exists to find. Detected on the invariant
    that `ratio = Close/Price` is piecewise constant and steps to its post-event level ON the
    ex-date, so a row whose ratio matches neither the previous session's level nor the next's is
    stale; repaired as `Price := Close / ratio_next`, and ONLY on a real price-adjusting ex-date.

    CAVEAT, stated because it bounds what this leg can prove (quant-skeptic 2026-09-27): the
    repaired value is `Close_t * P_t+1 / Close_t+1`, i.e. it injects adjusted-chain information
    into the "raw" leg. On a cell that is ALSO a share-step ex-date the repaired replay return
    collapses algebraically to `Close_t/Close_t-1` — the replay would be FORCED to agree with the
    chain it audits. So the overlap with share steps is measured and reported, not assumed away.
    """
    px = bx.pivot_table(index="time", columns="ticker", values="pxw").sort_index()
    cl = bx.pivot_table(index="time", columns="ticker", values="Close").sort_index()
    cl = cl.reindex(index=px.index, columns=px.columns)
    if args.no_px_repair:
        log("[px-repair] SKIPPED (mutation M4)")
        return px, cl, None
    ratio = cl / px
    rnext, rprev = ratio.shift(-1), ratio.shift(1)
    lo, hi = np.minimum(rprev, rnext), np.maximum(rprev, rnext)
    stale = ((ratio > lo * 1.005) & (ratio < hi * 0.995)
             & ratio.notna() & rnext.notna() & rprev.notna() & ex_date_mask(ev, px))
    n = int(stale.values.sum())
    px = px.where(~stale, cl / rnext)
    log(f"[px-repair] {n} ô ex-date có `Price` kẹt hệ CUM đã sửa thành Close/ratio_next")
    return px, cl, stale


def build_events(ev, px, args, log):
    """(share_factor, cash_per_share) panels aligned to the price grid, plus a rights inventory.

    Several tranches can go ex on one day and each `exercise_ratio` is quoted against the ORIGINAL
    share count, so the same-day factor is `1 + sum(q)` — ADDITIVE. Round 1 compounded them and was
    measurably wrong against the panel's own `OShares` (see the module header). `custom_basket`
    makes the same choice in `_match_step_date`'s same-day branch.
    """
    dates, cols = px.index, px.columns
    # DIV TIMING SENSITIVITY. PREREG §4 credits the cash at the ex-date and declares the bias; it
    # never measured it. `--div-lag K` moves ONLY the cash leg K sessions later (the share step
    # stays on the ex-date) so the timing is isolated from the share count at payment.
    LAGK = int(args.div_lag)
    qsum = pd.DataFrame(0.0, index=dates, columns=cols)
    qmul = pd.DataFrame(1.0, index=dates, columns=cols)
    cash = pd.DataFrame(0.0, index=dates, columns=cols)
    ds = pd.DatetimeIndex(dates)

    def dpay(d):
        i = min(list(dates).index(d) + LAGK, len(dates) - 1)
        return dates[i]

    def snap(d):
        """Ex-date -> first session on/after it, or (None, reason). An event before the first
        session must be DROPPED, not stamped on session one (round 1 bug)."""
        if pd.isna(d):
            return None, "no_exdate"
        t = pd.Timestamp(d)
        if t < ds[0]:
            return None, "pre_panel"
        i = ds.searchsorted(t)
        if i >= len(ds):
            return None, "post_panel"
        return ds[i], None

    n_free, n_div, rights = 0, 0, []
    # THREE different reasons an event is dropped, counted separately: round 2 logged all of them
    # as "trước phiên đầu", which was 9,6% wrong and the same reporting-inflation class as round 1.
    drop = {"pre_panel": 0, "post_panel": 0, "no_exdate": 0}
    for r in ev.itertuples():
        if r.ticker not in cols:
            continue
        if r.event_code == "DIV":
            if pd.isna(r.value_per_share) or r.value_per_share <= 0:
                continue
            d, why = snap(r.exright_date)
            if d is None:
                drop[why] += 1
                continue
            cash.at[dpay(d), r.ticker] += float(r.value_per_share)
            n_div += 1
        elif r.event_code == "ISS":
            m = r.issue_method_name_vi.strip()
            if m != RIGHTS_ISS and m not in FREE_SHARE_ISS:
                continue                      # ESOP / placement: existing holders get nothing
            d, why = snap(r.exright_date)
            if d is None:
                drop[why] += 1
                continue
            if m == RIGHTS_ISS:
                rights.append((r.ticker, r.exright_date, float(r.exercise_ratio or 0.0)))
            else:
                q = float(r.exercise_ratio or 0.0)
                if q > 0:
                    qsum.at[d, r.ticker] += q
                    qmul.at[d, r.ticker] *= (1.0 + q)
                    n_free += 1
        # AIS = additional LISTING of shares already issued -> no effect on an existing holder.
    fac = qmul if args.mult_share_step else (1.0 + qsum)
    if args.no_share_step:
        fac = pd.DataFrame(1.0, index=dates, columns=cols)
        log("[events] share step DROPPED (mutation M1)")
    elif args.mult_share_step:
        log("[events] same-day factor MULTIPLICATIVE (mutation M1b = lỗi vòng 1)")
    log(f"[events] TRONG cửa sổ: {n_free} sự kiện CP thưởng/cổ tức CP áp vào N; {n_div} cổ tức tiền "
        f"vào cash; {len(rights)} QUYỀN MUA KHÔNG mô phỏng được. Bỏ: "
        f"{drop['pre_panel']} trước phiên đầu / {drop['post_panel']} sau phiên cuối / "
        f"{drop['no_exdate']} không có ex-date (phần lớn là AIS).")
    return fac, cash, rights


def engine_weights(bx, mem, px):
    """The engine's own daily target weight vector, recomputed from the dumped panel.

    Mirrors custom_basket.build_pit()'s weight leg for weight_scheme='namecap': base =
    mcapw(prev day) * qmult over the active rebal's members, restricted to names with a non-NaN
    mcap on BOTH days, then water-filled to name_cap. The key is the session whose (d-1)->d return
    these weights earn — which is the engine's convention and, since round 2, the replay's too.
    """
    mcap = bx.pivot_table(index="time", columns="ticker", values="mcap").sort_index()
    mcapw = bx.pivot_table(index="time", columns="ticker", values="mcapw").reindex(
        index=mcap.index, columns=mcap.columns)
    members = {d: list(zip(g["ticker"], g["qmult"])) for d, g in mem.groupby("rebal_date")}
    reb = sorted(members)
    out, dates = {}, list(mcap.index)
    for i, d in enumerate(dates):
        if i == 0:
            continue
        prev = dates[i - 1]
        j = np.searchsorted(reb, d, side="right") - 1
        if j < 0:
            continue
        mm = members[reb[j]]
        tks = [t for t, _ in mm if t in mcap.columns]
        qm = np.array([q for t, q in mm if t in mcap.columns], dtype=float)
        today = mcap.loc[d, tks].values.astype(float)
        yest = mcap.loc[prev, tks].values.astype(float)
        yestw = mcapw.loc[prev, tks].values.astype(float)
        valid = ~np.isnan(today) & ~np.isnan(yest)
        if valid.sum() == 0:
            continue
        base = np.where(np.isnan(yestw[valid]), yest[valid], yestw[valid]) * qm[valid]
        if base.sum() <= 0:
            continue
        out[d] = (list(np.array(tks)[valid]), cap_names(base, 0.10), reb[j])
    return out, mcap


def engine_legs(bx, wmap, mcap):
    """Recompute the engine's FLAT and LEGACY daily returns from the dumped panel (harness check)."""
    cl = bx.pivot_table(index="time", columns="ticker", values="Close").reindex(
        index=mcap.index, columns=mcap.columns)
    dates = list(mcap.index)
    rf = pd.Series(0.0, index=mcap.index)
    rl = pd.Series(0.0, index=mcap.index)
    for i, d in enumerate(dates):
        if d not in wmap:
            continue
        prev = dates[i - 1]
        tks, w, _ = wmap[d]
        rf.loc[d] = float(np.nansum(w * (cl.loc[d, tks].values / cl.loc[prev, tks].values - 1.0)))
        rl.loc[d] = float(np.nansum(w * (mcap.loc[d, tks].values / mcap.loc[prev, tks].values - 1.0)))
    return rf, rl


def replay(px, cl, fac, cash, wmap, args, log, daily_reweight, fees):
    """NAV path of a real share portfolio. `daily_reweight` False = REPLAY_A, True = REPLAY_B.

    Timing (round-2 fix): the share vector that earns session d's return is bought at session
    d-1's close using `wmap[d]` — the same weights, on the same return, as the engine. Round 1
    bought at d's close and earned d+1's return, a full extra session of staleness.
    """
    mark = cl if args.mark_close else px
    dates = list(px.index)
    N = pd.Series(0.0, index=px.columns)
    cashbal = BASE_LEVEL          # initial capital sits in CASH, not a phantom position
    nav = BASE_LEVEL
    navs, cur_reb, n_carry, turn, div_total, fee_total = {}, None, 0, 0.0, 0.0, 0.0
    last_px = pd.Series(np.nan, index=px.columns)
    for i, d in enumerate(dates):
        if d not in wmap:
            navs[d] = nav
            continue
        prev = dates[i - 1]
        tks, w, rebd = wmap[d]
        pp = mark.loc[prev].copy()
        p = mark.loc[d].copy()
        # a name can lose its quote mid-period (halt/delist); a real holder still owns it, so the
        # last observed price is carried. Counted, never silently zeroed.
        for vec in (pp, p):
            miss = vec.isna() & (N != 0)
            if miss.any():
                n_carry += int(miss.sum())
                vec[miss] = last_px[miss]
        last_px = last_px.where(p.isna(), p)

        # (1) trade at the PREVIOUS close, with this session's weights
        if daily_reweight or rebd != cur_reb:
            tgt = pd.Series(0.0, index=px.columns)
            tgt[tks] = w
            newN = (tgt * nav / pp.where(pp > 0)).fillna(0.0)
            traded = float(((newN - N).abs() * pp).fillna(0.0).sum())
            turn += traded
            fee = traded * TC if fees else 0.0
            fee_total += fee
            N = newN
            cashbal = nav - float((N * pp).fillna(0.0).sum()) - fee
            nav -= fee
            cur_reb = rebd
        # (2) corporate actions going ex THIS session. The cash dividend is paid on the PRE-step
        # count (a bonus issue does not retro-earn the dividend), hence this order.
        held = N != 0
        if held.any():
            got = float((N[held] * cash.loc[d][held]).sum())
            cashbal += got
            div_total += got
            N[held] = N[held] * fac.loc[d][held]
        # (3) mark to market
        nav = float((N * p).fillna(0.0).sum()) + cashbal
        navs[d] = nav
    s = pd.Series(navs).sort_index()
    log(f"[replay {'B' if daily_reweight else 'A'}] {n_carry} ô giá thiếu carry-forward; "
        f"turnover {turn/BASE_LEVEL:.1f}x vốn gốc; cổ tức tiền nhận {div_total/BASE_LEVEL:.2f}x; "
        f"phí {fee_total/BASE_LEVEL:.3f}x")
    return s


def cagr(s, start=None):
    """CAGR measured from `start` (default: the series' own first date).

    The pre-registered window is 2014-08 -> 2026-06 and the first rebal is 2014-08-05, so the
    caller passes that date: the 0,616y before it is uninvested and would dilute every Delta.
    """
    if start is not None:
        s = s.loc[s.index >= start]
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    return (float(s.iloc[-1]) / float(s.iloc[0])) ** (1 / yrs) - 1, yrs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-share-step", action="store_true")
    ap.add_argument("--mult-share-step", action="store_true")
    ap.add_argument("--mark-close", action="store_true")
    ap.add_argument("--no-fee", action="store_true")
    ap.add_argument("--no-px-repair", action="store_true")
    ap.add_argument("--lag-weights", action="store_true")
    ap.add_argument("--div-lag", default="0", help="trả cổ tức tiền CHẬM K phiên (chỉ chân tiền)")
    ap.add_argument("--fixed-start", default="", help="ghim ngày bắt đầu đo CAGR (so cùng cửa sổ)")
    ap.add_argument("--out-prefix", default="")
    args = ap.parse_args()
    lines = []

    def log(m):
        print(m, flush=True)
        lines.append(m)

    bx, mem, ev = load()
    px, cl, stale = build_prices(bx, ev, args, log)
    fac, cash, rights = build_events(ev, px, args, log)
    wmap, mcap = engine_weights(bx, mem, px)
    if args.lag_weights:
        # mutation M5: reinstate round 1's off-by-one — give session d the weights keyed to d-1.
        ks = sorted(wmap)
        wmap = {ks[i]: wmap[ks[i - 1]] for i in range(1, len(ks))}
        log("[weights] LAG 1 phiên bật lại (mutation M5 = lỗi vòng 1)")
    rf, rl = engine_legs(bx, wmap, mcap)
    lvl_f = BASE_LEVEL * (1 + rf).cumprod()
    lvl_l = BASE_LEVEL * (1 + rl).cumprod()

    if not args.lag_weights:
        for tag, lv in (("flat", lvl_f), ("legacy", lvl_l)):
            ref = pd.read_parquet(f"{HERE}/level_{tag}.parquet")["level"]
            err = float((lv.reindex(ref.index) / ref - 1).abs().max())
            log(f"[harness] chân {tag} tái lập từ panel vs level build_pit trả về: max |Δ| = {err:.3e}")
            assert err < 1e-9, f"harness lệch chân {tag} — không được đọc số replay khi harness sai"

    # IDENTITY CHECK the harness cannot give: with every event removed, no fee and daily
    # reweighting, the replay MUST equal an independently written raw-price weighted chain. This
    # tests the NAV machinery itself (share arithmetic, cash residual, carry-forward) rather than
    # the event model, and it is not true by construction.
    class _Flat(argparse.Namespace):
        pass
    z = _Flat(**{**vars(args), "no_share_step": True, "mult_share_step": False})
    zero = pd.DataFrame(0.0, index=px.index, columns=px.columns)
    one = pd.DataFrame(1.0, index=px.index, columns=px.columns)
    b0 = replay(px, cl, one, zero, wmap, z, lambda *_: None, True, False)
    # the reference chain must use the SAME mark panel the replay used, otherwise mutation M2
    # (mark on Close) fails an identity that was never about M2 — a false alarm, not a finding.
    mk = cl if args.mark_close else px
    dates = list(px.index)
    r0 = pd.Series(0.0, index=px.index)
    for i, d in enumerate(dates):
        if d not in wmap:
            continue
        tks, w, _ = wmap[d]
        a = mk.loc[d, tks].values.astype(float)
        b = mk.loc[dates[i - 1], tks].values.astype(float)
        r0.loc[d] = float(np.nansum(w * (a / b - 1.0)))
    ident = float((b0 / (BASE_LEVEL * (1 + r0).cumprod()) - 1).abs().max())
    log(f"[identity] REPLAY_B không sự kiện/không phí vs chuỗi giá (cùng panel mark) viết độc lập: max |Δ| = {ident:.3e}")
    assert ident < 1e-9, "NAV machinery của replay không khớp chuỗi giá viết độc lập"

    a = replay(px, cl, fac, cash, wmap, args, log, daily_reweight=False, fees=not args.no_fee)
    b = replay(px, cl, fac, cash, wmap, args, log, daily_reweight=True, fees=False)

    # A mutation must never move the measurement window (round 2's M5 shifted it by one session
    # because re-keying wmap drops its first key — 0,017pp of the reported effect was the window).
    # `--fixed-start` lets the selfcheck pin the BASE window for every mutation leg.
    if args.fixed_start:
        start = pd.Timestamp(args.fixed_start)
    else:
        start = max(min(wmap) if wmap else px.index[0],
                    pd.Timestamp(sorted(mem["rebal_date"].unique())[0]))
    log("")
    log(f"[window] đo từ rebal ĐẦU TIÊN {start.date()} -> {px.index[-1].date()} "
        f"(cửa sổ PREREG; bỏ {(start - px.index[0]).days/365.25:.3f}y chưa đầu tư ở đầu chuỗi)")
    res = {}
    for tag, s in (("ENGINE_FLAT", lvl_f), ("ENGINE_LEGACY", lvl_l), ("REPLAY_A", a), ("REPLAY_B", b)):
        c, yrs = cagr(s, start)
        res[tag] = c
        log(f"{tag:14s} level {float(s.loc[s.index>=start].iloc[0]):8.1f} -> {float(s.iloc[-1]):10.1f}"
            f"   CAGR {c*100:7.3f}%   ({yrs:.2f}y)")
    log("")
    log(f"Δ CAGR  REPLAY_B − ENGINE_FLAT   = {(res['REPLAY_B']-res['ENGINE_FLAT'])*100:+.3f} pp "
        f"(THÔ — chưa trừ phần quyền mua; ngưỡng PREREG 0,300pp áp cho số ĐÃ TRỪ, xem attribute.py)")
    log(f"Δ CAGR  REPLAY_A − ENGINE_FLAT   = {(res['REPLAY_A']-res['ENGINE_FLAT'])*100:+.3f} pp")
    log(f"Δ CAGR  REPLAY_B − ENGINE_LEGACY = {(res['REPLAY_B']-res['ENGINE_LEGACY'])*100:+.3f} pp")

    rb, ra = b.pct_change().dropna(), a.pct_change().dropna()
    for tag, r in (("REPLAY_B", rb), ("REPLAY_A", ra)):
        for eng, re_ in (("FLAT", rf), ("LEGACY", rl)):
            j = pd.concat([r, re_.reindex(r.index)], axis=1).dropna()
            j = j.loc[j.index >= start]
            log(f"  {tag:9s} vs {eng:7s}: corr {float(j.iloc[:,0].corr(j.iloc[:,1])):.6f}   "
                f"tracking error {float((j.iloc[:,0]-j.iloc[:,1]).std()*np.sqrt(252))*100:6.3f}%/yr")

    log("")
    log(f"[rights] {len(rights)} sự kiện quyền mua TRONG cửa sổ "
        f"({len(set(t for t, _, _ in rights))} mã) — KHÔNG mô phỏng được (thiếu giá phát hành)")
    if stale is not None:
        ov = inb = 0
        for d, (tks, w, _) in wmap.items():
            row, frow = stale.loc[d], fac.loc[d]
            for t in tks:
                if bool(row.get(t, False)):
                    inb += 1
                    ov += int(abs(float(frow.get(t, 1.0)) - 1.0) > 1e-12)
        log(f"[px-repair] ô sửa GIAO với một bước số CP trong rổ: {ov} — nếu >0 thì đúng những ô đó "
            f"replay bị CƯỠNG BỨC khớp chuỗi Close (xem docstring build_prices)")
        # quant-skeptic 2026-09-27: phép co-về-Close KHÔNG chỉ xảy ra trên bước số CP. Trên ô sửa mà
        # sự kiện là cổ tức TIỀN, r_replay co về r_flat·(1−D/P) — cũng là cưỡng bức, mà `ov` ở trên
        # không thấy (5/8 ô sửa toàn panel là DIV-only). Điều kiện ĐỦ và duy nhất cần: ô sửa không
        # nằm trong rổ phiên đó ⇒ nó không vào chỉ số dưới BẤT KỲ loại sự kiện nào.
        log(f"[px-repair] ô sửa NẰM TRONG RỔ phiên đó: {inb} — 0 ⇒ đường cưỡng bức không bao giờ "
            f"được đi, với mọi loại sự kiện (mạnh hơn phép đếm GIAO-bước-số-CP ở trên)")

    pref = args.out_prefix or "base"
    pd.DataFrame({"ENGINE_FLAT": lvl_f, "ENGINE_LEGACY": lvl_l, "REPLAY_A": a, "REPLAY_B": b}
                 ).to_parquet(f"{HERE}/levels_{pref}.parquet")
    rsfx = "" if pref == "base" else f"_{pref}"
    pd.DataFrame(rights, columns=["ticker", "exright_date", "ratio"]).to_csv(
        f"{HERE}/rights_not_modelled{rsfx}.csv", index=False)
    with open(f"{HERE}/replay_{pref}.log", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"\n[out] levels_{pref}.parquet + replay_{pref}.log")


if __name__ == "__main__":
    main()
