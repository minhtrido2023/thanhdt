"""Post-shock base formation — event study (job Taylor_20260823_025658).

Thực thi ĐÚNG prereg `research/postshock_base_formation_prereg_20260823.md` (commit 1a3bf8b0).
threads=1, seed cố định. KHÔNG dùng cột profit_* (forward-looking).
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "1"

from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import db_dtypes  # noqa: F401 — parquet từ BQ mang extension type 'dbdate'

HERE = Path(__file__).resolve().parent
RES = HERE.parent
SEED = 20260823
RNG = np.random.default_rng(SEED)
warnings.filterwarnings("ignore", category=RuntimeWarning)

# ---- Tham số CHỐT TRƯỚC (prereg §3) --------------------------------------
LOOKBACK_HI = 60      # cửa sổ đỉnh rolling
SHOCK_DD = -0.25      # ngưỡng giảm từ đỉnh
MAX_SPEED = 20        # số phiên tối đa từ đỉnh tới ngày shock
CONFIRM_N = 5         # số phiên không phá đáy để xác nhận đáy
K_BASE = 20           # cửa sổ nền
BOTTOM_SEARCH = 60    # hạn tìm đáy sau t_s
VOL_RATIO = 0.5       # nền/shock
TURN_RATIO = 0.5
HORIZONS = (60, 120, 250)
COOLDOWN = 250        # chặn sự kiện mới cùng mã
BOOT_L = 20           # block bootstrap (phiên giao dịch)
BOOT_N = 10_000
TAIL_DD = -0.30
RATING_PREV_DAYS = 120


# ---------------------------------------------------------------- events --
def build_events(panel: pd.DataFrame) -> pd.DataFrame:
    """Quét toàn panel, trả 1 dòng/sự kiện độc lập."""
    rows = []
    for tkr, g in panel.groupby("ticker", sort=True):
        g = g.sort_values("time").reset_index(drop=True)
        if len(g) < LOOKBACK_HI + K_BASE + 10:
            continue
        close = g["Close"].to_numpy(float)
        vol = g["Volume"].to_numpy(float)
        inu = g["in_universe"].to_numpy(bool)
        turn = close * vol                     # prereg §2: tự tính, không đọc Trading_Value
        n = len(close)

        # đỉnh rolling 60 phiên (bao gồm phiên hiện tại)
        s = pd.Series(close)
        hi60 = s.rolling(LOOKBACK_HI, min_periods=LOOKBACK_HI).max().to_numpy()
        # argmax gần nhất trong cửa sổ
        peak_idx = np.full(n, -1)
        for i in range(LOOKBACK_HI - 1, n):
            w = close[i - LOOKBACK_HI + 1:i + 1]
            peak_idx[i] = i - LOOKBACK_HI + 1 + int(np.max(np.flatnonzero(w == w.max())))

        i = LOOKBACK_HI - 1
        while i < n:
            if not inu[i] or not np.isfinite(hi60[i]) or hi60[i] <= 0:
                i += 1
                continue
            dd = close[i] / hi60[i] - 1.0
            if dd > SHOCK_DD or (i - peak_idx[i]) > MAX_SPEED:
                i += 1
                continue

            t_s, t_peak = i, int(peak_idx[i])

            # --- đáy cục bộ xác nhận PIT ---
            t_b = None
            run_min = np.inf
            for j in range(t_s, min(t_s + BOTTOM_SEARCH, n - CONFIRM_N)):
                if close[j] <= run_min:
                    run_min = close[j]
                    if close[j + 1:j + 1 + CONFIRM_N].min() > close[j]:
                        t_b = j
                        break
            ev = dict(ticker=tkr, t_peak=g["time"].iat[t_peak], t_s=g["time"].iat[t_s],
                      dd_shock=dd, speed=t_s - t_peak, idx_s=t_s)

            if t_b is None or t_b + K_BASE >= n:
                ev.update(t_b=pd.NaT, t_conf=pd.NaT, base_formed=False, base_reason="no_bottom",
                          vol_ratio=np.nan, turn_ratio=np.nan, higher_low=False)
            else:
                sh = slice(t_peak, t_b + 1)                  # nhánh rơi [t_peak, t_b]
                bs = slice(t_b + 1, t_b + 1 + K_BASE)        # nền [t_b+1, t_b+K]
                r_sh = np.diff(np.log(close[sh])) if (t_b - t_peak) >= 2 else np.array([np.nan])
                r_bs = np.diff(np.log(close[bs]))
                v_sh, v_bs = np.nanstd(r_sh, ddof=1), np.nanstd(r_bs, ddof=1)
                to_sh, to_bs = np.nanmean(turn[sh]), np.nanmean(turn[bs])
                vr = v_bs / v_sh if v_sh > 0 else np.nan
                tr = to_bs / to_sh if to_sh > 0 else np.nan
                hl = bool(close[bs].min() >= close[t_b])
                ok = bool(np.isfinite(vr) and vr < VOL_RATIO and
                          np.isfinite(tr) and tr < TURN_RATIO and hl)
                reasons = []
                if not (np.isfinite(vr) and vr < VOL_RATIO): reasons.append("vol")
                if not (np.isfinite(tr) and tr < TURN_RATIO): reasons.append("turn")
                if not hl: reasons.append("hl")
                ev.update(t_b=g["time"].iat[t_b], t_conf=g["time"].iat[t_b + K_BASE],
                          base_formed=ok, base_reason="ok" if ok else "+".join(reasons),
                          vol_ratio=vr, turn_ratio=tr, higher_low=hl,
                          idx_b=t_b, idx_conf=t_b + K_BASE)

            # --- entry + forward, cho cả 2 biến thể ---
            for tag, sig_idx in (("a", t_s), ("b", ev.get("idx_conf"))):
                if sig_idx is None or (isinstance(sig_idx, float) and not np.isfinite(sig_idx)):
                    continue
                e = int(sig_idx) + 1                     # T+1 execution
                if e >= n:
                    continue
                ev[f"entry_{tag}"] = g["time"].iat[e]
                ev[f"entry_px_{tag}"] = close[e]
                ev[f"idx_entry_{tag}"] = e
                for H in HORIZONS:
                    if e + H < n:
                        ev[f"fwd{H}_{tag}"] = close[e + H] / close[e] - 1.0
                        ev[f"dd{H}_{tag}"] = close[e:e + H + 1].min() / close[e] - 1.0
                    else:
                        ev[f"fwd{H}_{tag}"] = np.nan
                        ev[f"dd{H}_{tag}"] = np.nan
                # chuỗi cụt (delist/đình chỉ) — prereg §6.4
                ev[f"truncated_{tag}"] = bool(e + max(HORIZONS) >= n)
                ev[f"n_fwd_{tag}"] = int(n - 1 - e)

            rows.append(ev)
            i = t_s + COOLDOWN          # prereg §3.4: chặn sự kiện mới cùng mã
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- rating --
def attach_rating(ev: pd.DataFrame, rt: pd.DataFrame) -> pd.DataFrame:
    rt = rt.dropna(subset=["rating"]).sort_values(["time", "ticker"]).reset_index(drop=True)
    now = pd.merge_asof(ev.sort_values("t_s"), rt[["ticker", "time", "rating"]],
                        left_on="t_s", right_on="time", by="ticker",
                        direction="backward")[["rating"]].rename(columns={"rating": "rating_now"})
    ev = ev.sort_values("t_s").reset_index(drop=True)
    ev["rating_now"] = now["rating_now"].to_numpy()
    ev["t_prev"] = ev["t_s"] - pd.Timedelta(days=RATING_PREV_DAYS)
    prv = pd.merge_asof(ev.sort_values("t_prev"), rt[["ticker", "time", "rating"]],
                        left_on="t_prev", right_on="time", by="ticker",
                        direction="backward")[["ticker", "t_s", "rating"]]
    ev = ev.merge(prv.rename(columns={"rating": "rating_prev"}), on=["ticker", "t_s"], how="left")

    rn = pd.to_numeric(ev["rating_now"], errors="coerce").astype(float)
    rp = pd.to_numeric(ev["rating_prev"], errors="coerce").astype(float)
    ev["rating_now"], ev["rating_prev"] = rn, rp
    d = rn - rp
    ev["rating_delta"] = d
    na = rn.isna().to_numpy() | rp.isna().to_numpy()
    bad = ((d >= 2).fillna(False) | (rn == 5).fillna(False)).to_numpy()
    ev["rating_group"] = np.where(na, "RATING_NA", np.where(bad, "RATING_BAD", "RATING_OK"))
    return ev


# ------------------------------------------------------------- benchmark --
def attach_vni(ev: pd.DataFrame, vni: pd.DataFrame) -> pd.DataFrame:
    v = vni.sort_values("time").reset_index(drop=True)
    vt = v["time"].to_numpy()
    vc = v["vni"].to_numpy(float)
    pos = {t: i for i, t in enumerate(vt)}
    for tag in ("a", "b"):
        col = f"entry_{tag}"
        if col not in ev:
            continue
        for H in HORIZONS:
            out = np.full(len(ev), np.nan)
            for k, t in enumerate(ev[col].to_numpy()):
                i = pos.get(t)
                if i is None or i + H >= len(vc):
                    continue
                out[k] = vc[i + H] / vc[i] - 1.0
            ev[f"vni{H}_{tag}"] = out
            ev[f"exc{H}_{tag}"] = ev[f"fwd{H}_{tag}"] - out
    return ev


# ------------------------------------------------------------- bootstrap --
def block_ids(dates: pd.Series, sessions: pd.DatetimeIndex, L: int = BOOT_L) -> np.ndarray:
    """Gán mỗi sự kiện vào 1 khối L phiên giao dịch liên tiếp (cluster theo thời gian)."""
    idx = sessions.searchsorted(pd.DatetimeIndex(dates))
    return (idx // L).astype(int)


def boot_stat(values: np.ndarray, blocks: np.ndarray, fn=np.median, n=BOOT_N, rng=None):
    """Cluster block bootstrap. Trả (theta_obs, lo, hi, p_one_sided_gt0, n_eff)."""
    rng = rng or np.random.default_rng(SEED)
    m = np.isfinite(values)
    values, blocks = values[m], blocks[m]
    if len(values) < 3:
        return np.nan, np.nan, np.nan, np.nan, len(values)
    theta = float(fn(values))
    ub = np.unique(blocks)
    by = {b: values[blocks == b] for b in ub}
    draws = np.empty(n)
    for i in range(n):
        pick = rng.choice(ub, size=len(ub), replace=True)
        cat = np.concatenate([by[b] for b in pick])
        draws[i] = fn(cat)
    lo, hi = np.percentile(draws, [2.5, 97.5])
    p = float(np.mean((draws - draws.mean()) >= theta))     # dịch về H0: theta=0
    return theta, float(lo), float(hi), p, len(values)


def bh_fdr(pvals, q=0.10):
    p = np.asarray(pvals, float)
    ok = np.isfinite(p)
    out = np.zeros(len(p), bool)
    idx = np.flatnonzero(ok)
    order = idx[np.argsort(p[idx])]
    m = len(order)
    thr = np.nan
    for rank, j in enumerate(order, start=1):
        if p[j] <= q * rank / m:
            thr = p[j]
    if np.isfinite(thr):
        out[idx] = p[idx] <= thr
    return out, thr


# ------------------------------------------------------------------ main --
def main():
    panel = pd.read_parquet(HERE / "panel.parquet")
    panel["time"] = pd.to_datetime(panel["time"]).astype("datetime64[ns]")
    vni = pd.read_parquet(HERE / "vnindex.parquet")
    vni["time"] = pd.to_datetime(vni["time"]).astype("datetime64[ns]")
    rt = pd.read_parquet(HERE / "ratings8l.parquet")
    rt["time"] = pd.to_datetime(rt["time"]).astype("datetime64[ns]")

    sessions = pd.DatetimeIndex(sorted(vni["time"].unique()))

    ev = build_events(panel)
    for c in ("t_peak", "t_s", "t_b", "t_conf"):
        ev[c] = pd.to_datetime(ev[c]).astype("datetime64[ns]")
    ev = ev[ev["t_s"] >= "2008-01-01"].reset_index(drop=True)
    print(f"[events] tổng shock độc lập: {len(ev)}")

    ev = attach_rating(ev, rt)
    ev = attach_vni(ev, vni)

    # --- assert cơ học chống look-ahead (prereg §5.3.1) ---
    bf = ev[ev["base_formed"]]
    assert (bf["entry_b"] > bf["t_b"]).all(), "entry_b phải sau t_b"
    off = (pd.DatetimeIndex(bf["entry_b"]).map(lambda d: sessions.searchsorted(d))
           - pd.DatetimeIndex(bf["t_b"]).map(lambda d: sessions.searchsorted(d)))
    assert (np.asarray(off) >= CONFIRM_N).all(), "entry_b phải >= t_b+5 phiên (đáy đã xác nhận)"
    assert (np.asarray(off) == K_BASE + 1).all(), "entry_b phải đúng t_b+K+1 phiên"
    assert (ev["entry_a"] > ev["t_s"]).all(), "entry_a phải sau t_s (T+1)"
    print("[assert] look-ahead checks PASS")

    ev["period"] = np.where(ev["t_s"] < "2020-01-01", "IS", "OOS")
    ev["blk"] = block_ids(ev["t_s"], sessions)
    ev["ym"] = ev["t_s"].dt.to_period("M").astype(str)
    ev.to_csv(RES / "postshock_events_20260823.csv", index=False)

    # ---------------- họ 12 test CHÍNH (prereg §5.1) ----------------
    base = ev[ev["base_formed"]].copy()
    tests = []
    for grp in ("RATING_OK", "RATING_BAD"):
        sub = base[base["rating_group"] == grp]
        for H in HORIZONS:
            for kind in ("exc", "paired"):
                if kind == "exc":
                    vals = sub[f"exc{H}_b"].to_numpy(float)
                    label = f"(b) excess vs VNINDEX, H={H}"
                else:
                    vals = (sub[f"fwd{H}_b"] - sub[f"fwd{H}_a"]).to_numpy(float)
                    label = f"(b)-(a) paired, H={H}"
                th, lo, hi, p, ne = boot_stat(vals, sub["blk"].to_numpy(),
                                              rng=np.random.default_rng(SEED + H))
                tests.append(dict(group=grp, horizon=H, kind=kind, label=label,
                                  median=th, ci_lo=lo, ci_hi=hi, p_one_sided=p, n=ne))
    T = pd.DataFrame(tests)
    T["bh_pass"], thr = bh_fdr(T["p_one_sided"].to_numpy())
    T["bh_threshold"] = thr

    # ---------------- cổng rủi ro đuôi (prereg §5.2) ----------------
    tail_rows = []
    for grp in ("RATING_OK", "RATING_BAD", "RATING_NA"):
        sub = base[base["rating_group"] == grp]
        m = sub[f"dd250_a"].notna() & sub[f"dd250_b"].notna()
        s = sub[m]
        if len(s) < 3:
            tail_rows.append(dict(group=grp, n=len(s), p_tail_a=np.nan, p_tail_b=np.nan,
                                  delta=np.nan, ci_lo=np.nan, ci_hi=np.nan, p_one_sided=np.nan))
            continue
        d = (s["dd250_b"] <= TAIL_DD).astype(float) - (s["dd250_a"] <= TAIL_DD).astype(float)
        th, lo, hi, p_gt, ne = boot_stat(d.to_numpy(), s["blk"].to_numpy(), fn=np.mean,
                                         rng=np.random.default_rng(SEED + 999))
        # H1: delta < 0  => p một đuôi phía dưới
        p_lt = np.nan
        if np.isfinite(th):
            rng = np.random.default_rng(SEED + 999)
            ub = np.unique(s["blk"].to_numpy())
            by = {b: d.to_numpy()[s["blk"].to_numpy() == b] for b in ub}
            dr = np.array([np.mean(np.concatenate([by[b] for b in rng.choice(ub, len(ub), True)]))
                           for _ in range(BOOT_N)])
            p_lt = float(np.mean((dr - dr.mean()) <= th))
        tail_rows.append(dict(group=grp, n=len(s),
                              p_tail_a=float((s["dd250_a"] <= TAIL_DD).mean()),
                              p_tail_b=float((s["dd250_b"] <= TAIL_DD).mean()),
                              delta=th, ci_lo=lo, ci_hi=hi, p_one_sided=p_lt))
    TAIL = pd.DataFrame(tail_rows)

    # ---------------- mô tả + test PHỤ ----------------
    desc = []
    for grp in ("RATING_OK", "RATING_BAD", "RATING_NA"):
        for formed, sub0 in (("BASE_FORMED", base), ("NO_BASE", ev[~ev["base_formed"]])):
            sub = sub0[sub0["rating_group"] == grp]
            for tag in ("a", "b"):
                for H in HORIZONS:
                    c = f"fwd{H}_{tag}"
                    if c not in sub:
                        continue
                    v = sub[c].to_numpy(float)
                    ex = sub.get(f"exc{H}_{tag}", pd.Series(np.nan, index=sub.index)).to_numpy(float)
                    desc.append(dict(group=grp, subset=formed, entry=tag, horizon=H,
                                     n=int(np.isfinite(v).sum()),
                                     med_fwd=float(np.nanmedian(v)) if np.isfinite(v).any() else np.nan,
                                     med_exc=float(np.nanmedian(ex)) if np.isfinite(ex).any() else np.nan,
                                     mean_fwd=float(np.nanmean(v)) if np.isfinite(v).any() else np.nan,
                                     p_tail=float(np.nanmean(
                                         sub[f"dd250_{tag}"].to_numpy(float) <= TAIL_DD))
                                     if f"dd250_{tag}" in sub else np.nan))
    D = pd.DataFrame(desc)

    # IS/OOS cho thống kê chính (RATING_OK, H=120, paired + excess)
    wf = []
    for grp in ("RATING_OK", "RATING_BAD"):
        for per in ("IS", "OOS"):
            sub = base[(base["rating_group"] == grp) & (base["period"] == per)]
            for H in HORIZONS:
                for kind, vals in (("exc", sub[f"exc{H}_b"].to_numpy(float)),
                                   ("paired", (sub[f"fwd{H}_b"] - sub[f"fwd{H}_a"]).to_numpy(float))):
                    v = vals[np.isfinite(vals)]
                    wf.append(dict(group=grp, period=per, horizon=H, kind=kind,
                                   n=len(v), median=float(np.median(v)) if len(v) else np.nan))
    WF = pd.DataFrame(wf)

    T.to_csv(RES / "postshock_stats_20260823.csv", index=False)
    D.to_csv(RES / "postshock_desc_20260823.csv", index=False)
    TAIL.to_csv(RES / "postshock_tailrisk_20260823.csv", index=False)
    WF.to_csv(RES / "postshock_walkforward_20260823.csv", index=False)

    # ---------------- in ra ----------------
    pd.set_option("display.width", 200, "display.max_columns", 50, "display.float_format",
                  lambda x: f"{x:,.4f}")
    print("\n=== PHÂN BỐ SỰ KIỆN ===")
    print(pd.crosstab(ev["rating_group"], ev["base_formed"], margins=True))
    print("\ntheo period:")
    print(pd.crosstab([ev["rating_group"], ev["period"]], ev["base_formed"]))
    print(f"\nsố cụm lịch (tháng có sự kiện): all={ev['ym'].nunique()}, "
          f"base_formed={base['ym'].nunique()}, "
          f"OK={base[base.rating_group=='RATING_OK']['ym'].nunique()}, "
          f"BAD={base[base.rating_group=='RATING_BAD']['ym'].nunique()}")
    print("\nlý do KHÔNG tạo nền:")
    print(ev[~ev["base_formed"]]["base_reason"].value_counts())

    print("\n=== 12 TEST CHÍNH (BH FDR 10%) ===")
    print(T.to_string(index=False))
    print(f"\nBH threshold p* = {thr}")
    print("\n=== CỔNG RỦI RO ĐUÔI P(maxDD250 <= -30%) ===")
    print(TAIL.to_string(index=False))
    print("\n=== MÔ TẢ ===")
    print(D[D.n > 0].to_string(index=False))
    print("\n=== WALK-FORWARD IS/OOS ===")
    print(WF[WF.n > 0].to_string(index=False))


if __name__ == "__main__":
    main()
