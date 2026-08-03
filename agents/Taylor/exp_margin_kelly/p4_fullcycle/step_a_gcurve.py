#!/usr/bin/env python
"""BUOC A (§3 ke hoach margin_kelly_full_cycle_plan_20260803.md)

Duong cong g(f) = toc do tang truong hinh hoc qua chuoi N=17 su kien washout (2014+),
+ bootstrap CI (iid VA theo khoi) + chan adversarial.

GATE G-A (§5, dang ky TRUOC, khong duoc sua):
    f*_geo > 1,0  VA  P_boot(g(1,3) > g(1,0)) >= 0,90  o CA iid LAN khoi, tai lai suat 12,5%.
    Rot -> NO-GO chung cuoc, dung, khong chay B/C/D.

RESEARCH-ONLY. Khong cham production. Khong dung cot profit_*.
"""
import numpy as np
import pandas as pd
from pathlib import Path

HERE = Path(__file__).resolve().parent
# HEADLINE = chan `universe_pit` (§4 guard #5). `../events_outcome.csv` la chan `ticker_prune`
# (TB x +10,45%) — chay lam SENSITIVITY, khong lam so chinh. Xem build_pit_paths.py.
import sys
LEG = sys.argv[1] if len(sys.argv) > 1 else "pit"
SRC = HERE / "events_outcome_pit.csv" if LEG == "pit" else HERE.parent / "events_outcome.csv"
OUT = HERE

PHI = 0.00075 * 2          # phi giao dich 2 chieu (§1.1)
SEED = 20260803
B = 10_000                 # so lan bootstrap (§1.3)
BLOCK_DAYS = 183           # "<6 thang la 1 khoi" (§1.3b)

# ---------------------------------------------------------------- du lieu
def load_events():
    df = pd.read_csv(SRC)
    df["event"] = pd.to_datetime(df["event"])
    df = df[df["r"].notna() & (df["event"] >= "2014-01-01")].copy()
    df = df.sort_values("event").reset_index(drop=True)
    assert len(df) == 17, f"ky vong N=17 su kien 2014+ co ket cuc day du, thay {len(df)}"
    return df


def block_ids(dates, gap_days=BLOCK_DAYS):
    """Su kien cach nhau < gap_days gop chung 1 khoi (chuoi lien ket)."""
    ids, cur = [0], 0
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days >= gap_days:
            cur += 1
        ids.append(cur)
    return np.array(ids)


# ---------------------------------------------------------------- co hoc R_i(f)
def event_returns(f, r, mae, days, c, maint, penalty, call_rule="s12", accrue=True):
    """Loi nhuan tren VON TU CO cua sleeve tai don bay gop f, co overlay margin-call
    xap xi bang MAE per-event (§3.1).

    call_rule:
      's12'    -> dung dinh nghia chuan tac §1.2: E/A = (f*(1+mae) - L) / (f*(1+mae))
      'lit31'  -> dung nguyen van bieu thuc §3.1: (1 + f*mae - (f-1)) / (f*(1+mae))
                  (chat hon; bao cao lam sensitivity vi §3.1 va §1.2 khong khop nhau)
    """
    carry = c * days / 365.0
    # No tai thoi diem MAE: gia dinh bao thu = da cong don ca ky (accrue=True)
    L = (f - 1.0) * (1.0 + carry) if accrue else (f - 1.0)

    A_mae = f * (1.0 + mae)                      # tai san tai day MAE
    if call_rule == "s12":
        E_mae = A_mae - L
    else:                                        # 'lit31' — nguyen van §3.1
        E_mae = 1.0 + f * mae - (f - 1.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(A_mae > 0, E_mae / A_mae, -np.inf)
    called = ratio < maint

    # Ket cuc binh thuong (§1.1)
    R_ok = f * (r - PHI) - (f - 1.0) * carry
    # Ket cuc thanh ly cuong che: ban tai day MAE voi penalty slippage, tra no
    R_call = A_mae * (1.0 - penalty) - L - 1.0
    R = np.where(called, R_call, R_ok)
    R = np.maximum(R, -0.999999)                 # von tu co khong am duoi -100%
    return R, called


def g_of(f, r, mae, days, **kw):
    R, called = event_returns(f, r, mae, days, **kw)
    return float(np.mean(np.log1p(R))), int(called.sum()), R


# ---------------------------------------------------------------- bootstrap
def boot_indices(rng, n, blocks=None):
    if blocks is None:
        return rng.integers(0, n, size=n)
    uniq = np.unique(blocks)
    members = [np.where(blocks == b)[0] for b in uniq]
    out = []
    while len(out) < n:
        out.extend(members[rng.integers(0, len(members))])
    return np.array(out[:n])


def boot_pair(r, mae, days, blocks, f_hi, f_lo, **kw):
    """P(g(f_hi) > g(f_lo)) + CI cua g tai 2 muc f, tren cung draw."""
    rng = np.random.default_rng(SEED)
    n = len(r)
    R_hi, _ = event_returns(f_hi, r, mae, days, **kw)
    R_lo, _ = event_returns(f_lo, r, mae, days, **kw)
    l_hi, l_lo = np.log1p(R_hi), np.log1p(R_lo)
    g_hi = np.empty(B); g_lo = np.empty(B)
    for b in range(B):
        idx = boot_indices(rng, n, blocks)
        g_hi[b] = l_hi[idx].mean()
        g_lo[b] = l_lo[idx].mean()
    return g_hi, g_lo, float(np.mean(g_hi > g_lo))


def boot_fstar(r, mae, days, blocks, grid, **kw):
    """Phan phoi f*_geo (argmax) qua bootstrap."""
    rng = np.random.default_rng(SEED + 1)
    n = len(r)
    L = np.vstack([np.log1p(event_returns(f, r, mae, days, **kw)[0]) for f in grid])
    fs = np.empty(B)
    for b in range(B):
        idx = boot_indices(rng, n, blocks)
        fs[b] = grid[int(np.argmax(L[:, idx].mean(axis=1)))]
    return fs


# ---------------------------------------------------------------- chay
def main():
    df = load_events()
    r = df["r"].to_numpy(float)
    mae = df["mae"].to_numpy(float)
    days = df["cal_days"].to_numpy(float)
    blocks = block_ids(list(df["event"]))

    lines = []
    P = lines.append
    P("=" * 78)
    P("BUOC A — duong cong tang truong hinh hoc g(f), N=17 su kien washout 2014+")
    P("Ke hoach: margin_kelly_full_cycle_plan_20260803.md §3 | GATE G-A §5")
    P("=" * 78)
    P(f"N = {len(df)} su kien | TB r = {r.mean():+.4%} | ty le duong = {(r>0).mean():.1%}")
    P(f"MAE xau nhat = {mae.min():+.4%} | cal_days TB = {days.mean():.1f}")
    P("")
    P("Khoi bootstrap (su kien cach nhau <183 ngay = 1 khoi):")
    for b in np.unique(blocks):
        ev = df.loc[blocks == b, "event"].dt.strftime("%Y-%m-%d").tolist()
        P(f"  khoi {b}: {', '.join(ev)}")
    P(f"  -> {len(np.unique(blocks))} khoi doc lap tren {len(df)} su kien")
    P("")

    grid = np.round(np.arange(1.00, 2.5001, 0.05), 2)

    scenarios = [
        ("BASE      (c=12,5% maint=30% pen=1%)", dict(c=0.125, maint=0.30, penalty=0.01), r),
        ("ADV lai   (c=14,0% maint=30% pen=1%)", dict(c=0.140, maint=0.30, penalty=0.01), r),
        ("ADV maint (c=12,5% maint=35% pen=2%)", dict(c=0.125, maint=0.35, penalty=0.02), r),
        ("ADV full  (c=14,0% maint=35% pen=2%)", dict(c=0.140, maint=0.35, penalty=0.02), r),
        ("ADV edge  (c=12,5% maint=30% pen=1%, r-6,6pp)",
         dict(c=0.125, maint=0.30, penalty=0.01), r - 0.066),
    ]

    rows = []
    for name, kw, rr in scenarios:
        gs, calls = [], []
        for f in grid:
            g, nc, _ = g_of(f, rr, mae, days, **kw)
            gs.append(g); calls.append(nc)
        gs = np.array(gs); calls = np.array(calls)
        g1 = gs[0]
        fstar = float(grid[int(np.argmax(gs))])
        ge = gs >= g1 - 1e-12
        fbreak = float(grid[np.max(np.where(ge)[0])]) if ge.any() else 1.0
        rows.append(dict(scenario=name, f_star=fstar, g_max=gs.max(), g_1=g1,
                         f_break=fbreak, calls_at_13=calls[grid == 1.30][0],
                         calls_at_15=calls[grid == 1.50][0],
                         g_13=gs[grid == 1.30][0], g_15=gs[grid == 1.50][0]))
        pd.DataFrame({"f": grid, "g": gs, "n_called": calls}).to_csv(
            OUT / f"gcurve_{LEG}_{name.split()[0]}_{name.split()[1]}.csv", index=False)

    P("-" * 78)
    P("BANG 1 — f*_geo va g(f) theo kich ban (call_rule = §1.2 chuan tac, accrue=True)")
    P("-" * 78)
    P(f"{'kich ban':<46}{'f*_geo':>8}{'g(1,0)':>10}{'g(f*)':>10}{'f_break':>9}")
    for d in rows:
        P(f"{d['scenario']:<46}{d['f_star']:>8.2f}{d['g_1']:>10.5f}"
          f"{d['g_max']:>10.5f}{d['f_break']:>9.2f}")
    P("")
    P(f"{'kich ban':<46}{'g(1,3)':>10}{'g(1,5)':>10}{'call@1,3':>10}{'call@1,5':>10}")
    for d in rows:
        P(f"{d['scenario']:<46}{d['g_13']:>10.5f}{d['g_15']:>10.5f}"
          f"{d['calls_at_13']:>10d}{d['calls_at_15']:>10d}")
    P("")

    # ---- sensitivity: bieu thuc call nguyen van §3.1 (chat hon) + khong cong don lai
    P("-" * 78)
    P("BANG 1b — sensitivity dinh nghia margin-call (BASE c=12,5%)")
    P("-" * 78)
    for rule, acc, tag in [("s12", True, "§1.2 + cong don lai (headline)"),
                           ("s12", False, "§1.2 + KHONG cong don lai"),
                           ("lit31", True, "§3.1 nguyen van (chat hon)")]:
        gs = np.array([g_of(f, r, mae, days, c=0.125, maint=0.30, penalty=0.01,
                            call_rule=rule, accrue=acc)[0] for f in grid])
        nc13 = g_of(1.30, r, mae, days, c=0.125, maint=0.30, penalty=0.01,
                    call_rule=rule, accrue=acc)[1]
        P(f"  {tag:<36} f*_geo={grid[int(np.argmax(gs))]:.2f}  "
          f"g(1,0)={gs[0]:+.5f}  g(1,3)={gs[grid==1.30][0]:+.5f}  call@1,3={nc13}")
    P("")

    # ---- GATE G-A: bootstrap tai lai suat 12,5% (base), CA iid LAN khoi
    P("=" * 78)
    P("GATE G-A — bootstrap B=10.000, lai suat 12,5% (§5, dang ky truoc)")
    P("=" * 78)
    kwb = dict(c=0.125, maint=0.30, penalty=0.01)
    ga_pass = {}
    for unit, blk in [("iid", None), ("khoi", blocks)]:
        g_hi, g_lo, p = boot_pair(r, mae, days, blk, 1.30, 1.00, **kwb)
        fs = boot_fstar(r, mae, days, blk, grid, **kwb)
        d_ci = np.percentile(g_hi - g_lo, [5, 50, 95])
        P(f"[{unit}] P(g(1,3) > g(1,0)) = {p:.4f}   (nguong G-A: >= 0,90)")
        P(f"       CI90 cua g(1,3)-g(1,0) = [{d_ci[0]:+.5f}, {d_ci[2]:+.5f}], trung vi {d_ci[1]:+.5f}")
        P(f"       f*_geo bootstrap: trung vi {np.median(fs):.2f}, "
          f"pct5 {np.percentile(fs,5):.2f}, pct95 {np.percentile(fs,95):.2f}, "
          f"P(f*<=1,0) = {np.mean(fs<=1.0):.3f}")
        ga_pass[unit] = p
    P("")

    base = rows[0]
    cond1 = base["f_star"] > 1.0
    cond2 = min(ga_pass.values()) >= 0.90
    P(f"  dieu kien 1: f*_geo > 1,0            -> f*_geo = {base['f_star']:.2f}  "
      f"{'PASS' if cond1 else 'FAIL'}")
    P(f"  dieu kien 2: P_boot >= 0,90 ca 2 don vi -> iid {ga_pass['iid']:.4f} / "
      f"khoi {ga_pass['khoi']:.4f}  {'PASS' if cond2 else 'FAIL'}")
    P("")
    verdict = "PASS" if (cond1 and cond2) else "FAIL"
    P(f"  >>> GATE G-A: {verdict}")
    if verdict == "FAIL":
        P("  >>> Theo §5: NO-GO CHUNG CUOC. DUNG, khong chay buoc B/C/D.")
    else:
        P("  >>> Di tiep BUOC B (§1.2, §2).")

    # ---- meta-gate FRAGILE (§5): 12,5% vs 14%
    P("")
    P("-" * 78)
    P("META-GATE trung thuc (§5): ket luan co doi dau giua cac lua chon khong?")
    P("-" * 78)
    for name, kw, rr in scenarios:
        gs = np.array([g_of(f, rr, mae, days, **kw)[0] for f in grid])
        say = "NEN VAY (f*>1)" if grid[int(np.argmax(gs))] > 1.0 else "KHONG NEN VAY (f*=1)"
        P(f"  {name:<46} -> {say}")
    _, _, p14 = boot_pair(r, mae, days, blocks, 1.30, 1.00,
                          c=0.140, maint=0.30, penalty=0.01)
    P(f"  P_boot(khoi) tai lai 14%/nam = {p14:.4f}")

    txt = "\n".join(lines)
    print(txt)
    (OUT / f"step_a_gcurve_{LEG}.log").write_text(txt + "\n", encoding="utf-8")
    pd.DataFrame(rows).to_csv(OUT / f"step_a_summary_{LEG}.csv", index=False)


if __name__ == "__main__":
    main()
