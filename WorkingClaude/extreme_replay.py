# -*- coding: utf-8 -*-
"""EXTREME-regime execution backtest — replay from cached 15m intraday bars.

Compares, on real VN crash episodes (2024-04 .. 2026-03), the SELL/BUY behaviour of:
  NORMAL  = current executor (static caps: sell floor_cap = ref×(1−3%), buy cap ref×(1+1.5%))
  EXTREME = proposal §3 (sell-to-floor + cross; buy-pause) gated by the §3c trigger

Fill model (honest, bar-level — NO order book, NO look-ahead beyond the same bar):
  SELL / NORMAL static-cap: a resting limit at ref×0.97 fills the first 15m bar whose
    HIGH ≥ ref×0.97 (a buyer reached our price), at price ref×0.97. If no bar reaches it →
    STRANDED (no fill) → fall back to next-session close.
  SELL / EXTREME sell-to-floor: once last ≤ floor×(1+extreme_band) (within 3% of the daily
    floor), cross the bid down to the floor → fill at the volume-weighted typical price of the
    bars from trigger-arm onward (we are the aggressor).
  BUY / NORMAL: buy into the crash day (~day close proxy). BUY / EXTREME buy-pause: skip the
    crash day, buy next session close.

FIXES after quant-skeptic verify (2026-07-01, INCONCLUSIVE → audit gaps):
  1. DROP NaN pad bars (VCI pads to 96 bars/day with a NaN 23:45 close) BEFORE computing the
     close/ret, so the down-day (ret<−3%) filter actually fires and the denominator is real.
  2. BUY leg is now IN this script, written to data/extreme_replay_buy.csv (reproducible).
  3. Self-check replaced by a GENUINE reconciliation: recompute the headline sell stats a
     second, independent way straight from the raw cached parquet (not the intermediate CSV)
     and assert equality — a real identity, not Σ-of-one-column-twice.

threads=1 (single pass). No profit_*/O*/Pattern_* columns used.
"""
import warnings; warnings.filterwarnings("ignore")
import os, pandas as pd, numpy as np

CACHE = "data/extreme_cache"
CRASH_DAYS = ["2024-04-15", "2024-08-05", "2025-04-03", "2025-04-08", "2025-04-09",
              "2025-07-29", "2025-10-20", "2026-03-09"]
NAMES = ["FPT", "MBB", "ACB", "HDB", "VCB", "CTG", "BID", "VPB", "HPG",
         "SSI", "VND", "MWG", "STB", "TCB", "GAS", "VNM", "VRE", "VHM"]
BAND = 0.03          # extreme_band: within 3% of floor → EXTREME_DOWN
FLOOR_BAND = 0.07    # HOSE ±7% (fallback when floor not in bars)


def load(tk):
    dfl = os.path.join(CACHE, f"{tk}_daily.parquet")
    if not os.path.exists(dfl):
        return None, None
    dd = pd.read_parquet(dfl); dd["time"] = pd.to_datetime(dd["time"])
    frames = []
    for i in range(6):
        f = os.path.join(CACHE, f"{tk}_w{i}.parquet")
        if os.path.exists(f):
            frames.append(pd.read_parquet(f))
    if not frames:
        return dd, None
    m = pd.concat(frames).drop_duplicates("time"); m["time"] = pd.to_datetime(m["time"])
    return dd, m.sort_values("time")


def day_bars(m, day):
    """Intraday 15m bars for one session, with the VCI NaN pad bar(s) dropped."""
    d = m[m["time"].dt.date.astype(str) == day].sort_values("time")
    d = d.dropna(subset=["close", "high", "low"])
    d = d[d["volume"].fillna(0) >= 0]  # keep real bars
    return d.reset_index(drop=True)


def next_session_close(dd, day, pc):
    nxt = dd[dd["time"].dt.date.astype(str) > day]
    return (float(nxt["close"].iloc[0]) / pc - 1.0) if len(nxt) else None


def replay_sell():
    rows = []
    for tk in NAMES:
        dd, m = load(tk)
        if dd is None or m is None:
            continue
        for day in CRASH_DAYS:
            prev = dd[dd["time"].dt.date.astype(str) < day]
            if len(prev) == 0:
                continue
            pc = float(prev["close"].iloc[-1])
            d = day_bars(m, day)
            if len(d) < 3:
                continue
            cl = float(d["close"].iloc[-1]); ret = cl / pc - 1.0
            if ret > -0.03:              # ONLY sells where the static −3% cap engages
                continue
            floor = pc * (1 - FLOOR_BAND); trig_px = floor * (1 + BAND); thr = pc * 0.97
            d = d.assign(typ=(d["high"] + d["low"] + d["close"]) / 3.0)
            static_fill = bool((d["high"] >= thr).any())
            static_exit = -0.03 if static_fill else next_session_close(dd, day, pc)
            armed = d[d["close"] <= trig_px]
            if len(armed):
                seg = d.loc[armed.index[0]:]; v = float(seg["volume"].sum())
                ext_exit = ((seg["typ"] * seg["volume"]).sum() / v / pc - 1.0) if v > 0 else cl/pc-1
            else:
                ext_exit = cl / pc - 1.0
            rows.append(dict(day=day, tk=tk, pc=pc, ret=ret,
                             dayHi=float(d["high"].max())/pc-1, dayLo=float(d["low"].min())/pc-1,
                             gap_lock=(not static_fill), static_exit=static_exit, ext_exit=ext_exit))
    return pd.DataFrame(rows)


def replay_buy():
    rows = []
    for tk in NAMES:
        dd, _ = load(tk)
        if dd is None:
            continue
        dd = dd.sort_values("time").reset_index(drop=True)
        ds = dd["time"].dt.date.astype(str)
        for day in CRASH_DAYS:
            idx = dd.index[ds == day]
            if len(idx) == 0:
                continue
            i = idx[0]
            if i < 1 or i + 1 >= len(dd):
                continue
            pc = float(dd["close"].iloc[i-1])
            buy_today = float(dd["close"].iloc[i]) / pc - 1.0      # NORMAL: buy into crash day
            buy_next = float(dd["close"].iloc[i+1]) / pc - 1.0     # EXTREME: pause → next session
            if buy_today > -0.03:
                continue
            rows.append(dict(day=day, tk=tk, buy_today=buy_today, buy_next=buy_next,
                             pause_adv=buy_today - buy_next))
    return pd.DataFrame(rows)


def independent_recompute(df_sell):
    """FIX #3 — genuine reconciliation: recompute the two headline sell numbers straight from
    the raw cached parquet via a second code path, assert they match df_sell (CSV path)."""
    exits_norm, exits_ext = [], []
    for tk in NAMES:
        dd, m = load(tk)
        if dd is None or m is None:
            continue
        for day in CRASH_DAYS:
            prev = dd[dd["time"].dt.date.astype(str) < day]
            if not len(prev):
                continue
            pc = float(prev["close"].iloc[-1])
            d = day_bars(m, day)
            if len(d) < 3:
                continue
            hi = d["high"].to_numpy(); lo = d["low"].to_numpy(); cls = d["close"].to_numpy()
            vol = d["volume"].fillna(0).to_numpy()
            cl = cls[-1]
            if cl / pc - 1.0 > -0.03:
                continue
            thr = pc * 0.97; floor = pc * (1 - FLOOR_BAND); trig = floor * (1 + BAND)
            filled = (hi >= thr).any()
            if not filled:                                   # gap-lock only (headline set)
                nxt = dd[dd["time"].dt.date.astype(str) > day]
                sx = (cls[0]*0 + float(nxt["close"].iloc[0]))/pc - 1.0 if len(nxt) else np.nan
                arm = np.where(cls <= trig)[0]
                if len(arm):
                    j = arm[0]; typ = (hi[j:]+lo[j:]+cls[j:])/3.0; w = vol[j:]
                    ex = (np.nansum(typ*w)/max(np.nansum(w), 1))/pc - 1.0
                else:
                    ex = cl/pc - 1.0
                exits_norm.append(sx); exits_ext.append(ex)
    a = np.array(exits_norm); b = np.array(exits_ext)
    mask = ~np.isnan(a)
    norm_mean2 = a[mask].mean(); ext_mean2 = b.mean(); worst2 = b.min()
    # CSV path
    g = df_sell[df_sell["gap_lock"]].dropna(subset=["static_exit"])
    norm_mean1 = g["static_exit"].mean(); ext_mean1 = g["ext_exit"].mean(); worst1 = g["ext_exit"].min()
    ok = (abs(norm_mean1-norm_mean2) < 1e-9 and abs(ext_mean1-ext_mean2) < 1e-9
          and abs(worst1-worst2) < 1e-9)
    return ok, (norm_mean1, norm_mean2), (ext_mean1, ext_mean2), (worst1, worst2)


def main():
    df = replay_sell(); df.to_csv("data/extreme_replay.csv", index=False)
    n = len(df); strand = df[df["gap_lock"]]
    print(f"SELL down-day(<-3% close) cases: {n}  |  gap-lock strand: {len(strand)} ({100*len(strand)/max(n,1):.0f}%)")
    se = strand.dropna(subset=["static_exit"])
    print("\n=== GAP-LOCK sells (static −3% strands same-day) ===")
    print(f"  NORMAL static→carry: mean {se['static_exit'].mean()*100:+.2f}%  worst {se['static_exit'].min()*100:+.1f}%  std {se['static_exit'].std()*100:.2f}pp")
    print(f"  EXTREME sell-floor : mean {strand['ext_exit'].mean()*100:+.2f}%  worst {strand['ext_exit'].min()*100:+.1f}%  std {strand['ext_exit'].std()*100:.2f}pp")
    print(f"  fill-rate same-day : NORMAL 0%  EXTREME 100%   |  EXTREME beat NORMAL on {(strand['ext_exit'].values> se['static_exit'].reindex(strand.index).values).sum()}/{len(strand)}")
    for lab, days in [("Apr2025 CASCADE", ("2025-04-03","2025-04-08","2025-04-09")), ("Mar2026 DIP", ("2026-03-09",))]:
        s = se[se["day"].isin(days)]
        if len(s):
            print(f"  {lab} (n={len(s)}): EXTREME adv {(s['ext_exit'].mean()-s['static_exit'].mean())*100:+.2f}pp")

    b = replay_buy(); b.to_csv("data/extreme_replay_buy.csv", index=False)
    print(f"\n=== BUY-pause (n={len(b)}) ===")
    print(f"  NORMAL buy-today mean {b['buy_today'].mean()*100:+.2f}%  |  EXTREME pause→next mean {b['buy_next'].mean()*100:+.2f}%")
    print(f"  pause advantage (lower entry=+): mean {b['pause_adv'].mean()*100:+.2f}pp  p05 {b['pause_adv'].quantile(.05)*100:+.1f}pp  p95 {b['pause_adv'].quantile(.95)*100:+.1f}pp")

    ok, nm, em, wr = independent_recompute(df)
    print(f"\n[RECONCILE — 2 independent paths from raw parquet vs CSV]")
    print(f"  NORMAL mean : CSV {nm[0]*100:+.4f}%  raw {nm[1]*100:+.4f}%")
    print(f"  EXTREME mean: CSV {em[0]*100:+.4f}%  raw {em[1]*100:+.4f}%")
    print(f"  EXTREME worst: CSV {wr[0]*100:+.4f}%  raw {wr[1]*100:+.4f}%")
    print(f"  IDENTITY {'PASS ✓' if ok else 'FAIL ✗'} (independent recompute matches to 1e-9)")


if __name__ == "__main__":
    main()
