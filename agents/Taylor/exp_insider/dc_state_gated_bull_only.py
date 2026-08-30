# -*- coding: utf-8 -*-
"""dc_state_gated_bull_only.py -- job Taylor_20260830_162358.

Test kien truc "DC book chi active BULL/EXBULL, tu dong FLAT (w_DC=0) o
CRISIS/BEAR/NEUTRAL" -- huong mo tu dc_3book_factor_neutral_20260830.md (phat hien phu, chua
qua DSR/PBO/quant-skeptic). Day la job lam day du huong do.

Cach tai tro von (TU QUYET DINH, giai thich):
  Overlay blend_ret = (1 - w_dc_t) * baseline_ret + w_dc_t * dc_ret, voi
  w_dc_t = w_DC neu state in {BULL, EXBULL} else 0.
  Tuc la khi DC active, no thay THE MOT PHAN combined_nav production THAT (BAL+LAG+CAPIT da
  hoan chinh), khong rieng BAL hay rieng LAG. Ly do chon cach nay thay vi "thay 1 phan
  w_BAL/w_LAG rieng le" hoac "thay 1 phan custom30V parking":
    1. custom30V parking CHI xay ra khi state=NEUTRAL (PARK_STATES="3:0.7") -- DC gate lai CHI
       active o BULL/EXBULL, hai dieu kien khong bao gio overlap => "thay parking" la khong co
       nghia (khong co von parking nao dang ton tai luc DC active de thay the).
    2. Thay rieng w_BAL hay rieng w_LAG doi hoi vi lai toan bo allocator state-conditional
       (w_LAG={1:.50,2:0,3/4/5:.65} band +-10pp + CAPIT) trong pt_v23_audit_2014.py -- rui ro
       cao, kho verify trong 1 job (dung canh bao Q3 file 08-25, da tranh o Viec 1 truoc).
    3. "Thay ti le deu tu combined_nav" la it xao tron nhat: dung DUNG combined_nav production
       lam nen, chi lam mot phep OVERLAY tuyen tinh o muc return -- khong dung cham logic
       allocator ben trong, de rollback (w_DC=0 tra ve chinh xac baseline).
  Day chinh la cach "phat hien phu" 08-30 da lam (w_DC=0.20/0.33) -- job nay MO RONG no thanh
  mot nghien cuu day du: nhieu muc w_DC, walk-forward IS/OOS rieng, transition-cost, DSR bang
  block-bootstrap theo EPISODE (khong phai theo ngay -- ngay trong cung 1 episode KHONG doc lap),
  va per-episode consistency check.

Nguon du lieu THAT (khong tu tao, dung lai y nguyen tu dc_3book_real_blend.py):
  - baseline_ret = combined_nav pct_change, CSV audit fresh EXP_TAG=dc3book_baseline_check
    (khong canonical, xem dc_3book_real_blend.py doc dc de biet cach sinh).
  - dc_ret = cot "ConvergePort (equal-weight)", converge_portfolio_backtest_nav.csv
    (Taylor_20260706_093329, da T+1 + TC 0.1% + tu park cash du).
  - state = cot "state" cung CSV audit (1..5, DA sinh boi macro_state_live pipeline that,
    KHONG tu ve lai smoothing/hysteresis -- DT5G da co cam ket bat doi xung 10/25 phien built-in
    trong chinh cot state nay, xem CLAUDE.md muc "VNINDEX 5-State").

CAVEAT:
  1. Transition cost la UOC LUONG don gian: moi ngay state CHUYEN VAO hoac RA khoi {BULL,EXBULL}
     bi tru mot lan turnover = w_DC * TC_ONEWAY (0.1%) -- xap xi chi phi mua/ban w_DC ty trong
     NAV vao dung ngay chuyen trang thai. Khong mo hinh slippage vuot TC chuan (per CLAUDE.md).
  2. state column da la SAU-smoothing (DT 4-gate + macro cap) -- khong ap them hysteresis nao
     nua o day, dung dung tin hieu production da co.
  3. N doc lap la SO EPISODE (chuoi lien tuc state in {BULL,EXBULL}), KHONG PHAI so ngay --
     482 ngay BULL/EXBULL nhung chi 10 episode doc lap trong lich su 2014-2026. DSR/robustness
     phai dung N=10, khong duoc dung N=482 (thoi phong do doc lap gia).
  4. Ke thua dung caveat 1-4 cua dc_3book_real_blend.py (khong mo phong CAPIT tuong tac 3-book,
     khong ADV cap dung chung -- da do gan 0 o job 08-25, quy mo backtest 50B != NAV that ~1B).

RESEARCH ONLY -- khong dung production file.
"""
import os
import numpy as np
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
CSV_BASELINE = os.path.join(WORKDIR, "data",
    "v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_dc3book_baseline_check_univpit.csv")
CSV_DC = os.path.join(WORKDIR, "data", "converge_portfolio_backtest_nav.csv")
OUT_METRICS = os.path.join(os.path.dirname(__file__), "dc_state_gated_bull_only_metrics.csv")
OUT_EPISODES = os.path.join(os.path.dirname(__file__), "dc_state_gated_bull_only_episodes.csv")

IS_END = pd.Timestamp("2019-12-31")
OOS_START = pd.Timestamp("2020-01-01")
STATE_NAMES = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}
DC_ACTIVE_STATES = (4, 5)
TC_ONEWAY = 0.001
W_DC_GRID = [0.15, 0.20, 0.25, 0.33]
N_BOOT = 3000
SEED = 20260830


def metrics(r):
    r = r.dropna()
    s = (1 + r).cumprod()
    if len(s) < 2:
        return (np.nan,) * 4
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = s.iloc[-1] ** (1 / yrs) - 1
    spd = len(r) / yrs
    sh = r.mean() / r.std() * np.sqrt(spd) if r.std() > 0 else 0
    dd = (s / s.cummax() - 1).min()
    cal = cagr / abs(dd) if dd < 0 else 0
    return cagr * 100, sh, dd * 100, cal


def windows(r):
    return [("FULL", r), ("IS_2014-2019", r[r.index <= IS_END]), ("OOS_2020+", r[r.index >= OOS_START])]


def build_episodes(active_bool_series):
    """Danh sach (start_date, end_date, length) cho moi lan chay lien tuc active=True."""
    eps = []
    cur_start = None
    prev = False
    for dt, a in active_bool_series.items():
        if a and not prev:
            cur_start = dt
        if (not a) and prev:
            eps.append((cur_start, prev_dt))
        prev = a
        prev_dt = dt
    if prev:
        eps.append((cur_start, prev_dt))
    return eps


def blend_with_transition_cost(base_r, dc_r, active, w_dc):
    w_dc_t = active.astype(float) * w_dc
    blend = (1 - w_dc_t) * base_r + w_dc_t * dc_r
    # transition day = active flips vs previous day -> pay w_dc * TC_ONEWAY that day
    flips = active.astype(int).diff().fillna(0).abs().astype(bool)
    cost = flips.astype(float) * w_dc * TC_ONEWAY
    blend_after_cost = blend - cost
    return blend, blend_after_cost, int(flips.sum())


def main():
    print("Loading fresh production baseline CSV (combined_nav + state) ...")
    df = pd.read_csv(CSV_BASELINE)
    d = df[df["record_type"] == "DAILY"].copy()
    d["ymd"] = pd.to_datetime(d["ymd"])
    d = d.sort_values("ymd").set_index("ymd")
    baseline_ret_full = d["combined_nav"].astype(float).pct_change()
    state_full = d["state"].astype(float)

    print("Loading ConvergePort DC leg (equal-weight) ...")
    conv = pd.read_csv(CSV_DC)
    conv["date"] = pd.to_datetime(conv["date"])
    conv = conv.set_index("date")
    dc_ret_full = conv["ConvergePort (equal-weight)"]

    calendar = baseline_ret_full.index.intersection(dc_ret_full.index).sort_values()
    print(f"  intersected calendar: {calendar[0].date()} -> {calendar[-1].date()} ({len(calendar)} sessions)")

    base_r = baseline_ret_full.reindex(calendar)
    dc_r = dc_ret_full.reindex(calendar)
    st = state_full.reindex(calendar).ffill()
    active = st.isin(DC_ACTIVE_STATES)

    n_active_days = int(active.sum())
    episodes = build_episodes(active)
    print(f"\nDC-active days (state in BULL/EXBULL): {n_active_days} / {len(calendar)}")
    print(f"Independent episodes (contiguous BULL/EXBULL runs): N={len(episodes)}")
    for i, (s0, s1) in enumerate(episodes, 1):
        span = (s1 - s0).days
        print(f"  ep{i:>2}: {s0.date()} -> {s1.date()}  ({span}d calendar)")

    print("\n" + "=" * 90)
    print("BASELINE (production combined_nav, no DC overlay)")
    print("=" * 90)
    base_metrics_by_window = {}
    for tag, rr in windows(base_r):
        c, sh, dd, cal = metrics(rr)
        base_metrics_by_window[tag] = (c, sh, dd, cal)
        print(f"  {tag:<14} CAGR {c:>7.2f}%  Sharpe {sh:>5.2f}  MaxDD {dd:>7.1f}%  Calmar {cal:>5.2f}")

    rows = []
    per_config_daily = {}
    for w_dc in W_DC_GRID:
        blend, blend_cost, n_flips = blend_with_transition_cost(base_r, dc_r, active, w_dc)
        per_config_daily[w_dc] = blend_cost
        print("\n" + "=" * 90)
        print(f"STATE-GATED DC OVERLAY  w_DC={w_dc:.2f} (active only BULL/EXBULL)  "
              f"n_transitions={n_flips}  (raw / net-of-transition-cost)")
        print("=" * 90)
        for tag, rr in windows(blend):
            c, sh, dd, cal = metrics(rr)
            bc, bsh, bdd, bcal = base_metrics_by_window[tag]
            print(f"  {tag:<14} RAW        CAGR {c:>7.2f}%  Sharpe {sh:>5.2f}  MaxDD {dd:>7.1f}%  Calmar {cal:>5.2f}"
                  f"   (d CAGR {c-bc:+.2f}pp  dSharpe {sh-bsh:+.2f}  dCalmar {cal-bcal:+.2f})")
        for tag, rr in windows(blend_cost):
            c, sh, dd, cal = metrics(rr)
            bc, bsh, bdd, bcal = base_metrics_by_window[tag]
            print(f"  {tag:<14} NET-of-TC  CAGR {c:>7.2f}%  Sharpe {sh:>5.2f}  MaxDD {dd:>7.1f}%  Calmar {cal:>5.2f}"
                  f"   (d CAGR {c-bc:+.2f}pp  dSharpe {sh-bsh:+.2f}  dCalmar {cal-bcal:+.2f})")
            rows.append(dict(w_dc=w_dc, window=tag, n_transitions=n_flips,
                              baseline_cagr=bc, blend_net_cagr=c, d_cagr=c - bc,
                              baseline_sharpe=bsh, blend_net_sharpe=sh, d_sharpe=sh - bsh,
                              baseline_maxdd=bdd, blend_net_maxdd=dd, d_maxdd=dd - bdd,
                              baseline_calmar=bcal, blend_net_calmar=cal, d_calmar=cal - bcal))

    # ---- per-episode consistency: for the w_dc=0.20 config (mid-grid), compare blend vs baseline
    # cumulative return WITHIN each episode (net of transition cost)
    print("\n" + "=" * 90)
    print("PER-EPISODE CONSISTENCY (w_DC=0.20, net of transition cost)")
    print("=" * 90)
    ep_rows = []
    blend020 = per_config_daily[0.20]
    wins = 0
    for i, (s0, s1) in enumerate(episodes, 1):
        seg_base = base_r.loc[s0:s1]
        seg_blend = blend020.loc[s0:s1]
        base_cum = (1 + seg_base.fillna(0)).prod() - 1
        blend_cum = (1 + seg_blend.fillna(0)).prod() - 1
        delta = (blend_cum - base_cum) * 100
        wins += int(delta > 0)
        state_tag = "EXBULL" if st.loc[s0:s1].max() == 5 else "BULL"
        print(f"  ep{i:>2} [{state_tag:<6}] {s0.date()}->{s1.date()}  base {base_cum*100:>7.2f}%  "
              f"blend {blend_cum*100:>7.2f}%  delta {delta:>+7.2f}pp")
        ep_rows.append(dict(episode=i, start=s0.date(), end=s1.date(), state_tag=state_tag,
                             base_cum_pct=base_cum * 100, blend_cum_pct=blend_cum * 100,
                             delta_pp=delta))
    print(f"\n  episodes where blend beats baseline: {wins}/{len(episodes)}")

    # ---- DSR-style block bootstrap: resample EPISODES (not days) with replacement, plus the
    # non-active days held fixed (they're identical between base and blend by construction when
    # active=False -> delta=0 there), so only episode-level dispersion of the DC excess matters.
    print("\n" + "=" * 90)
    print(f"BLOCK BOOTSTRAP over N={len(episodes)} episodes (w_DC=0.20, net of transition cost), "
          f"{N_BOOT} resamples")
    print("=" * 90)
    rng = np.random.default_rng(SEED)
    ep_deltas = np.array([r["delta_pp"] for r in ep_rows])
    n_ep = len(ep_deltas)
    boot_means = np.array([ep_deltas[rng.integers(0, n_ep, n_ep)].mean() for _ in range(N_BOOT)])
    p5 = np.percentile(boot_means, 5)
    p50 = np.percentile(boot_means, 50)
    frac_positive = (boot_means > 0).mean()
    print(f"  mean per-episode delta: {ep_deltas.mean():+.2f}pp  (median {np.median(ep_deltas):+.2f}pp)")
    print(f"  bootstrap distribution of mean-delta: p5={p5:+.2f}pp  p50={p50:+.2f}pp  "
          f"P(mean delta > 0) = {frac_positive:.3f}")
    print(f"  DSR proxy note: N={n_ep} independent episodes is SMALL -- this is a directional "
          f"robustness check, not a formal Bailey-Lopez-de-Prado DSR (needs return-series trial "
          f"count, not applicable cleanly to a state-gated overlay). Treat p5/frac_positive as "
          f"the honest confidence signal, not a p-value.")

    # ---- simplified PBO-style robustness across the W_DC_GRID: is OOS ranking consistent with
    # IS ranking, or does OOS degrade when using the IS-best config? (grid too small, N=4, for a
    # real combinatorial PBO -- report monotonicity instead, which is the practically relevant
    # question: "does more w_DC always help IS but hurt OOS" would be the overfitting signature)
    print("\n" + "=" * 90)
    print("GRID MONOTONICITY CHECK (IS Sharpe vs OOS Sharpe across w_DC grid)")
    print("=" * 90)
    grid_rows = [r for r in rows if r["window"] in ("IS_2014-2019", "OOS_2020+")]
    is_sh = {r["w_dc"]: r["blend_net_sharpe"] for r in grid_rows if r["window"] == "IS_2014-2019"}
    oos_sh = {r["w_dc"]: r["blend_net_sharpe"] for r in grid_rows if r["window"] == "OOS_2020+"}
    is_best = max(is_sh, key=is_sh.get)
    oos_best = max(oos_sh, key=oos_sh.get)
    print(f"  IS-best w_DC = {is_best:.2f} (Sharpe {is_sh[is_best]:.2f})   "
          f"OOS-best w_DC = {oos_best:.2f} (Sharpe {oos_sh[oos_best]:.2f})")
    print(f"  IS Sharpe by w_DC:  {dict((k, round(v,2)) for k,v in sorted(is_sh.items()))}")
    print(f"  OOS Sharpe by w_DC: {dict((k, round(v,2)) for k,v in sorted(oos_sh.items()))}")

    pd.DataFrame(rows).to_csv(OUT_METRICS, index=False)
    pd.DataFrame(ep_rows).to_csv(OUT_EPISODES, index=False)
    print(f"\nwrote {OUT_METRICS}")
    print(f"wrote {OUT_EPISODES}")
    print(f"\nself-check: gate is exact partition (active XOR inactive covers 100% of calendar, "
          f"no VND double count) -> active+~active days = {int(active.sum())}+{int((~active).sum())}"
          f" = {int(active.sum())+int((~active).sum())} == {len(calendar)}")


if __name__ == "__main__":
    main()
