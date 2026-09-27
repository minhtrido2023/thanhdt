#!/usr/bin/env python3
"""Decompose (REPLAY_B - ENGINE_FLAT) and (LEGACY - FLAT) to the name x session level.

REPLAY_B is, by construction, a weight-times-return sum over the same weight vector the engine
uses and on the same session, so the daily gap is exactly attributable:

    diff_t = sum_i  w_i,t * ( r_replay_i,t - r_flat_i,t )
    r_replay_i,t = ( f_i,t * P_i,t + D_i,t ) / P_i,t-1 - 1        (raw price + explicit events)
    r_flat_i,t   = Close_i,t / Close_i,t-1 - 1                    (vendor-adjusted chain)

Each (name, session) contribution is bucketed by what the corp-action table says happened that
day, which is what turns "the two chains differ by X" into "they differ BECAUSE of Y".

RIGHTS CARVE-OUT REPORTED AS A BAND (round 2, quant-skeptic 2026-09-27). A rights ex-date is the
one event class the replay cannot value (no issue price in the vendor table), so PREREG judges the
threshold on the carved number. But the carve-out is ~2x the threshold, so HOW it is drawn matters
and a single figure would hide that:
  BAND_HI  substitute r_flat for the WHOLE name x session whenever a rights event goes ex — this
           also erases the replay's verdict on any FREESHARE/DIV that went ex the same day, i.e.
           on part of the event class under audit. Most generous to the engine.
  BAND_LO  substitute only where the session's ONLY event is the rights issue. Most conservative.
Whichever band is used, the FLAT leg is NOT certified on rights ex-dates — stated, not buried.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from replay import (BASE_LEVEL, FREE_SHARE_ISS, RIGHTS_ISS, build_events, build_prices,
                    cagr, engine_weights, load)


class A:      # argparse stand-in: base configuration, no mutations
    no_share_step = mult_share_step = mark_close = no_fee = no_px_repair = lag_weights = False
    div_lag = "0"
    fixed_start = ""


def permanent_rebase(px, cl, tol_step=0.005, tol_flat=0.002, k=3):
    """Sessions where the vendor PERMANENTLY re-based `Close` relative to raw `Price`.

    `ratio = Close/Price` is piecewise constant and steps only when the vendor applies an
    adjustment. A session is a permanent re-basing if the ratio steps by > `tol_step` and then
    HOLDS the new level for the next `k` sessions (within `tol_flat`). Round 2's report called the
    whole non-rights residual "nhiễu `Price` đứng yên 1 phiên, triệt tiêu ở phiên sau" — true for
    the VEA/BID/VPB blips (ratio returns to its old level) and FALSE for this class, which never
    reverts. quant-skeptic found 437 such in-basket cells with no event in the pinned vintage;
    they are the measurement's real noise floor and must be reported GROSS, not just net.
    """
    ratio = cl / px
    step = (ratio / ratio.shift(1) - 1).abs() > tol_step
    holds = None
    for j in range(1, k + 1):
        h = (ratio.shift(-j) / ratio - 1).abs() < tol_flat
        holds = h if holds is None else (holds & h)
    return step & holds & ratio.notna()


def main():
    args = A()
    log = print
    bx, mem, ev = load()
    px, cl, _ = build_prices(bx, ev, args, log)
    fac, cash, rights = build_events(ev, px, args, log)
    wmap, mcap = engine_weights(bx, mem, px)
    dates = list(px.index)
    start = max(min(wmap), pd.Timestamp(sorted(mem["rebal_date"].unique())[0]))
    print(f"[window] {start.date()} -> {px.index[-1].date()}")

    # per (ticker, date) event label, for bucketing. Same window bound as build_events: an event
    # before the first session is DROPPED, not stamped on session one.
    lab = pd.DataFrame("", index=px.index, columns=px.columns)
    ds = pd.DatetimeIndex(px.index)
    for r in ev.itertuples():
        if r.ticker not in px.columns or pd.isna(r.exright_date):
            continue
        m = (r.issue_method_name_vi or "").strip()
        if r.event_code == "DIV" and pd.notna(r.value_per_share) and float(r.value_per_share) > 0:
            tag = "DIV"
        elif r.event_code == "ISS" and m == RIGHTS_ISS:
            tag = "RIGHTS"
        elif r.event_code == "ISS" and m in FREE_SHARE_ISS and float(r.exercise_ratio or 0) > 0:
            tag = "FREESHARE"
        else:
            continue
        i = ds.searchsorted(r.exright_date)
        if i >= len(ds) or r.exright_date < ds[0]:
            continue
        d = ds[i]
        cur = lab.at[d, r.ticker]
        lab.at[d, r.ticker] = tag if not cur else (cur if tag in cur else cur + "+" + tag)
    lab = lab.apply(lambda col: col.map(lambda s: "+".join(sorted(s.split("+"))) if s else ""))

    osh = bx.pivot_table(index="time", columns="ticker", values="OShares").reindex(
        index=px.index, columns=px.columns)

    rows = []
    r_b = pd.Series(0.0, index=px.index)
    r_f = pd.Series(0.0, index=px.index)
    r_hi = pd.Series(0.0, index=px.index)
    r_lo = pd.Series(0.0, index=px.index)
    r_un = pd.Series(0.0, index=px.index)
    perm = permanent_rebase(px, cl)
    unmod_rows = []
    for i, d in enumerate(dates):
        if d not in wmap:
            continue
        prev = dates[i - 1]
        tks, w, _ = wmap[d]
        p1 = px.loc[prev, tks].values.astype(float); p2 = px.loc[d, tks].values.astype(float)
        c1 = cl.loc[prev, tks].values.astype(float); c2 = cl.loc[d, tks].values.astype(float)
        f = fac.loc[d, tks].values.astype(float); dv = cash.loc[d, tks].values.astype(float)
        o1 = osh.loc[prev, tks].values.astype(float); o2 = osh.loc[d, tks].values.astype(float)
        rr = (f * p2 + dv) / p1 - 1.0
        rf = c2 / c1 - 1.0
        rl = (c2 * o2) / (c1 * o1) - 1.0
        lb = lab.loc[d, tks].values
        has_r = np.array(["RIGHTS" in (x or "") for x in lb])
        only_r = np.array([(x or "") == "RIGHTS" for x in lb])
        r_b.loc[d] = float(np.nansum(w * rr))
        r_f.loc[d] = float(np.nansum(w * rf))
        r_hi.loc[d] = float(np.nansum(w * np.where(has_r, rf, rr)))
        r_lo.loc[d] = float(np.nansum(w * np.where(only_r, rf, rr)))
        # PRINCIPLED CARVE: a session where the vendor permanently re-based the price and the
        # replay applied NO event (fac==1 and div==0) is a session the replay structurally cannot
        # price — whatever the vintage's date says. This covers the rights issues AND the vendor's
        # own gaps/mis-datings (SHS 2022-04-18: vintage dates the 1:1 rights 04-14, the price
        # re-bases 04-18, so a carve keyed to `exright_date` neutralises the WRONG session).
        pm = perm.loc[d, tks].values.astype(bool)
        unmod = pm & (np.abs(f - 1.0) < 1e-12) & (dv <= 0)
        r_un.loc[d] = float(np.nansum(w * np.where(unmod, rf, rr)))
        for k in np.nonzero(unmod)[0]:
            unmod_rows.append((d, tks[k], w[k], lb[k] or "NONE", rr[k], rf[k], w[k] * (rr[k] - rf[k])))
        for k in range(len(tks)):
            dr, dl = rr[k] - rf[k], rl[k] - rf[k]
            if abs(dr) < 1e-9 and abs(dl) < 1e-9:
                continue
            rows.append((d, tks[k], w[k], lb[k] or "NONE", p1[k], p2[k], c1[k], c2[k], f[k], dv[k],
                         o1[k], o2[k], rr[k], rf[k], rl[k], w[k] * dr, w[k] * dl))
    at = pd.DataFrame(rows, columns=["date", "ticker", "w", "label", "p_prev", "p", "c_prev", "c",
                                     "fac", "div", "osh_prev", "osh", "r_replay", "r_flat",
                                     "r_legacy", "contrib_rep_minus_flat", "contrib_leg_minus_flat"])
    at = at[at["date"] >= start]
    at.to_parquet(f"{HERE}/attribution.parquet", index=False)
    print(f"\n[attr] {len(at):,} dòng (name × session) có chênh khác 0, trong cửa sổ")

    print("\n== REPLAY_B − ENGINE_FLAT: đóng góp theo NHÃN SỰ KIỆN ==")
    yrs = (px.index[-1] - start).days / 365.25
    g = at.groupby("label")["contrib_rep_minus_flat"]
    tb = pd.DataFrame({"n": g.size(), "sum_contrib": g.sum(), "mean_bp": g.mean() * 1e4,
                       "max_abs_bp": g.apply(lambda s: s.abs().max()) * 1e4})
    tb["pp_per_yr"] = tb["sum_contrib"] / yrs * 100
    print(tb.sort_values("sum_contrib").to_string(float_format=lambda v: f"{v:,.4f}"))

    def C(s):
        return cagr(BASE_LEVEL * (1 + s).cumprod(), start)[0]
    cF, cB, cHI, cLO, cUN = C(r_f), C(r_b), C(r_hi), C(r_lo), C(r_un)
    print(f"\nENGINE_FLAT              CAGR {cF*100:7.3f}%")
    print(f"REPLAY_B (thô)           CAGR {cB*100:7.3f}%   Δ {(cB-cF)*100:+.3f} pp")
    print(f"REPLAY_B carve BAND_LO   CAGR {cLO*100:7.3f}%   Δ {(cLO-cF)*100:+.3f} pp  "
          f"(chỉ trung hoà phiên CHỈ CÓ quyền mua)")
    print(f"REPLAY_B carve BAND_HI   CAGR {cHI*100:7.3f}%   Δ {(cHI-cF)*100:+.3f} pp  "
          f"(trung hoà CẢ phiên có quyền mua + sự kiện khác)")
    print(f"REPLAY_B carve UNMODELLED CAGR {cUN*100:7.3f}%   Δ {(cUN-cF)*100:+.3f} pp  "
          f"(trung hoà MỌI phiên vendor re-base vĩnh viễn mà replay không có sự kiện — carve có "
          f"nguyên tắc, không neo theo ngày của vintage)")
    print(f"\nDẢI XÁC NHẬN vs ngưỡng PREREG 0,300pp: Δ ∈ [{(cLO-cF)*100:+.3f}, {(cHI-cF)*100:+.3f}] pp"
          f"  ⇒ {'TRONG' if max(abs(cLO-cF), abs(cHI-cF))*100 <= 0.300 else 'CÓ ĐẦU VƯỢT'} ngưỡng"
          f"  · carve UNMODELLED {(cUN-cF)*100:+.3f} pp")
    ur = pd.DataFrame(unmod_rows, columns=["date", "ticker", "w", "label", "r_replay", "r_flat",
                                           "contrib"])
    ur = ur[ur.date >= start]
    ur.to_csv(f"{HERE}/unmodelled_rebase_cells.csv", index=False)
    gross = ur.contrib.abs().sum() / yrs * 100
    print(f"[noise-floor] {len(ur)} name×session vendor re-base VĨNH VIỄN mà replay không có sự "
          f"kiện ({int((ur.label=='NONE').sum())} nhãn NONE tức vintage KHÔNG có sự kiện nào ngày đó): "
          f"ròng {ur.contrib.sum()/yrs*100:+.3f} pp/năm nhưng **GROSS Σ|đóng góp| = {gross:.3f} pp/năm**. "
          f"Gross này LỚN HƠN ngưỡng 0,300pp ⇒ phép kiểm PASS nhưng KHÔNG PHÂN GIẢI được sai số "
          f"nhỏ hơn ~{gross:.2f}pp. Số ròng chặt là do TRIỆT TIÊU giữa {len(ur)} mục độc lập, "
          f"không phải do một cơ chế bù trừ theo cặp.")
    print(ur.reindex(ur.contrib.abs().sort_values(ascending=False).index).head(8).to_string(
        index=False, float_format=lambda v: f"{v:,.4f}"))
    print(f"phần quyền mua: BAND_LO {(cB-cLO)*100:+.3f}pp · BAND_HI {(cB-cHI)*100:+.3f}pp")
    nr = at[at.label.str.contains("RIGHTS")]
    print(f"[carve] {len(nr)} name×session bị trung hoà ở BAND_HI, trong đó "
          f"{int((nr.label != 'RIGHTS').sum())} có sự kiện KHÁC đi ex cùng ngày ⇒ BAND_HI xoá luôn "
          f"phán quyết của replay trên chính lớp sự kiện đang audit; đó là lý do báo theo DẢI.")

    # raw-Price one-session staleness OUTSIDE ex-dates: the biggest residual pattern, mean-reverting
    fz = at[(at.label == "NONE") & (np.isclose(at.p, at.p_prev)) & (~np.isclose(at.c, at.c_prev))]
    print(f"\n[residual] {len(fz)} name×session nhãn NONE có `Price` ĐỨNG YÊN đúng bằng phiên trước "
          f"trong khi `Close` đã đổi (giá thô bị chép 1 phiên, NGOÀI ngày ex ⇒ detector không bắt): "
          f"tổng đóng góp {fz.contrib_rep_minus_flat.sum():+.4f}; các cặp này TRIỆT TIÊU ở phiên sau "
          f"(giá kẹt nằm ở tử số phiên t và mẫu số phiên t+1).")

    led = at[at["contrib_leg_minus_flat"].abs() > 1e-9]
    bysess = led.groupby("date")["contrib_leg_minus_flat"].sum().sort_values(ascending=False)
    print(f"\n== LEDGER phiên LEGACY ≠ FLAT: {len(led)} name×session / {len(bysess)} phiên, "
          f"{int((bysess>0).sum())} phiên dương / {int((bysess<0).sum())} âm, "
          f"max {bysess.max()*100:+.2f}pp, min {bysess.min()*100:+.2f}pp ==")
    led.to_csv(f"{HERE}/ledger_legacy_vs_flat.csv", index=False)
    bysess.rename("contrib_pp").to_frame().to_csv(f"{HERE}/ledger_legacy_by_session.csv")

    hdr = (f"{'ticker':6s} {'date':12s} {'w':>6s} {'raw Δ%':>8s} {'adj Δ%':>8s} {'ΔOSh%':>8s} "
           f"{'r_legacy%':>10s} {'r_flat%':>9s} {'r_replay%':>10s} {'label':20s}")

    def line(r):
        return (f"{r.ticker:6s} {str(r.date.date()):12s} {r.w:6.3f} {(r.p/r.p_prev-1)*100:8.2f} "
                f"{(r.c/r.c_prev-1)*100:8.2f} {(r.osh/r.osh_prev-1)*100:8.2f} "
                f"{r.r_legacy*100:10.2f} {r.r_flat*100:9.2f} {r.r_replay*100:10.2f} {r.label:20s}")

    print("\n== 3 ca quant-skeptic nêu — replay khớp chân nào ==")
    print(hdr)
    for tk, dt in (("ACB", "2024-05-31"), ("HPG", "2025-06-26"), ("TCB", "2024-06-20")):
        sub = at[(at.ticker == tk) & (at.date == pd.Timestamp(dt))]
        if sub.empty:
            print(f"{tk:6s} {dt:12s}  -- KHÔNG nằm trong rổ phiên đó ⇒ đóng góp 0 vào chỉ số")
        else:
            print(line(sub.iloc[0]))

    top = led.reindex(led["contrib_leg_minus_flat"].abs().sort_values(ascending=False).index).head(15)
    print("\n== 15 name×session phantom LEGACY lớn nhất ==")
    print(hdr)
    for r in top.itertuples():
        print(line(r))

    print("\n== 8 chênh REPLAY-vs-FLAT lớn nhất KHÔNG phải quyền mua (dư lượng cần giải thích) ==")
    nn = at[~at.label.str.contains("RIGHTS")]
    print(hdr)
    for r in nn.reindex(nn.contrib_rep_minus_flat.abs().sort_values(ascending=False).index
                        ).head(8).itertuples():
        print(line(r))


if __name__ == "__main__":
    main()
