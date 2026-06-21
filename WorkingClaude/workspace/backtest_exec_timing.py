# -*- coding: utf-8 -*-
"""Backtest EXECUTION TIMING cho trading_bot — co dang chon thoi diem tot hon "mu" khong?

Cau hoi: cung mot parent order (mua/ban 1B VND, ticker T, ngay D), lich dat lenh
nao cho gia khop binh quan tot hon? So 4 chien luoc bang simulator child-order
tren bar 1-phut (fill model giong executor.py: slice 200M / 8 phut / participation 10%).

  S0 BASELINE   — bot hien tai: cross spread moi slice, deu tu 09:15 (mu).
  S1 OR_PACING  — OR30 VN30F (09:00-09:30): mua ngay OR+ -> front-load cross;
                  ngay OR- -> sang passive, chieu mới cross; |OR|<0.2% nhu S0. Ban nguoc lai.
  S2 DIP_CROSS  — moi slice: gia vua chay nguoc huong minh 15' -> cross ngay,
                  vua chay cung huong -> dat passive (mean-reversion 15-30').
  S3 COMBO      — S1 pacing + S2 quy tac cross/passive trong cua so cho phep.

Fill model (bar 1m, khong co quote — spread uoc 1 tick, ap dung NHU NHAU moi strategy):
  - cross  : khop tai open(bar ke tiep) + 0.5 tick (tra spread), toi da 10%/bar volume.
  - passive: limit = open(bar ke tiep) − 0.5 tick; khop khi low(bar) < limit trong
             <=8 phut, gia = limit, toi da 10%/bar volume; het han -> huy, quyet dinh lai.
  - 14:25: phan con lai force cross (proxy quet ATC) — moi strategy nhu nhau.
Metric: implementation shortfall (bps) vs arrival = open 09:15 (mua: fill/arr−1;
ban: 1−fill/arr; cong them penalty phan khong khop: danh dau tai gia close cuoi).
T-stat: trung binh chenh lech vs S0 theo NGAY (cluster by day).
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np
import pandas as pd

WD = r"/home/trido/thanhdt/WorkingClaude"
IN_DIR = os.path.join(WD, "data", "intraday_1m")
VN30F = os.path.join(WD, "data", "vn30f1m_1min.csv")
OUT_CSV = os.path.join(WD, "data", "exec_timing_results.csv")

ORDER_VALUE = 1_000_000_000   # 1B VND moi parent (book 50B, vi the 2%)
CHILD_VALUE = 200_000_000     # max_child_value (config bot)
SLICE_MIN = 8                 # slice_interval_min
PART = 0.10                   # max_participation per bar
OR_TH = 0.002                 # nguong |OR| 0.2% (research ORB)
DIP_WIN = 15                  # cua so mean-reversion (phut)
FORCE_HM = "14:25"            # force cross phan con lai (proxy ATC sweep)


def tick_size(price_vnd):
    if price_vnd < 10_000: return 10
    if price_vnd < 50_000: return 50
    return 100


# ----------------------------------------------------------------- OR signal
def load_or_signal():
    f = pd.read_csv(VN30F)
    f["time"] = pd.to_datetime(f["time"])
    f["date"] = f["time"].dt.date
    f["hm"] = f["time"].dt.strftime("%H:%M")
    sig = {}
    for d, g in f.groupby("date"):
        op = g[g["hm"] <= "09:30"]
        if len(op) < 10:
            continue
        orr = op["close"].iloc[-1] / g["close"].iloc[0] - 1
        sig[str(d)] = orr
    return sig


# ----------------------------------------------------------------- simulator
class Sim:
    """Mo phong 1 parent order tren chuoi bar 1 ngay (gia VND, volume shares).

    bars = dict numpy arrays {hm, open, high, low, close, volume} — toc do.
    """

    def __init__(self, bars, side):
        self.b = bars
        self.side = side         # +1 mua, -1 ban
        self.n = len(bars["open"])

    def run(self, schedule):
        """schedule(i, hm, sim) -> None|('cross',qty_vnd)|('passive',qty_vnd).
        Goi tai cac thoi diem quyet dinh (moi SLICE_MIN phut khi khong co child song).
        Tra ve (vwap_fill, filled_vnd, forced_vnd)."""
        fills = []               # (price, shares)
        remaining = ORDER_VALUE  # theo VND tai ref — quy doi shares theo gia hien hanh
        child = None             # dict(limit, qty_sh, filled_sh, expire_i, type)
        last_decision = -10**9
        b = self.b
        hms, op, hi, lo, vol = b["hm"], b["open"], b["high"], b["low"], b["volume"]
        i = 0
        while i < self.n - 1 and remaining > 0:
            hm = hms[i]
            if hm >= FORCE_HM:
                break
            # 1) child dang song: thu khop bang bar hien tai
            if child is not None:
                qty = 0
                cap = int(PART * vol[i])
                want = child["qty_sh"] - child["filled_sh"]
                touched = (lo[i] <= child["limit"]) if self.side > 0 \
                    else (hi[i] >= child["limit"])
                if touched:
                    qty = min(want, cap)
                if qty > 0:
                    px = child["limit"]
                    fills.append((px, qty))
                    child["filled_sh"] += qty
                    remaining -= qty * px
                if child["filled_sh"] >= child["qty_sh"] or i >= child["expire_i"]:
                    child = None
            # 2) khong co child -> den ky quyet dinh?
            if child is None and remaining > 0 and i - last_decision >= SLICE_MIN:
                act = schedule(i, hm, self)
                last_decision = i
                if act is not None:
                    typ, val = act
                    val = min(val, remaining)
                    t = tick_size(op[i + 1])
                    if typ == "cross":
                        limit = op[i + 1] + self.side * 0.5 * t
                    else:
                        limit = op[i + 1] - self.side * 0.5 * t
                    qty_sh = max(0, int(val / limit))
                    if qty_sh > 0:
                        child = {"limit": limit, "qty_sh": qty_sh, "filled_sh": 0,
                                 "expire_i": i + SLICE_MIN, "type": typ}
            i += 1
        # force cross phan con lai tai FORCE_HM (proxy ATC) — cap participation van ap
        forced = 0.0
        if remaining > 0:
            for j in range(self.n):
                if hms[j] < FORCE_HM or remaining <= 0:
                    continue
                t = tick_size(op[j])
                px = op[j] + self.side * 0.5 * t
                qty = min(int(remaining / px), int(PART * vol[j]))
                if qty > 0:
                    fills.append((px, qty))
                    remaining -= qty * px
                    forced += qty * px
        if not fills:
            return None
        sh = sum(q for _, q in fills)
        vwap = sum(p * q for p, q in fills) / sh
        filled_vnd = ORDER_VALUE - max(0.0, remaining)
        return vwap, filled_vnd, forced, max(0.0, remaining)


# ----------------------------------------------------------------- schedules
def make_s0():
    return lambda i, hm, sim: ("cross", CHILD_VALUE)

def r15(sim, i):
    """Return 15' gan nhat cua chinh co phieu."""
    j = max(0, i - DIP_WIN)
    a, b = sim.b["close"][j], sim.b["close"][i]
    return b / a - 1 if a > 0 else 0.0

def make_s2():
    def f(i, hm, sim):
        if r15(sim, i) * sim.side <= 0:      # gia vua di NGUOC huong minh -> cross
            return ("cross", CHILD_VALUE)
        return ("passive", CHILD_VALUE)      # gia vua chay cung huong -> cho hoi
    return f

def make_s1(or_ret):
    def f(i, hm, sim):
        fav = or_ret * sim.side              # OR cung huong lenh = drift bat loi (gia chay mat)
        if abs(or_ret) < OR_TH:
            return ("cross", CHILD_VALUE)
        if fav > 0:                          # drift bat loi -> front-load gap doi
            if hm < "09:30":
                return None                  # chua co tin hieu OR truoc 09:30
            return ("cross", 2 * CHILD_VALUE)
        # drift thuan loi -> sang passive, 13:00+ cross don
        if hm < "13:00":
            return ("passive", CHILD_VALUE)
        return ("cross", CHILD_VALUE)
    return f

def make_s3(or_ret):
    s2 = make_s2()
    def f(i, hm, sim):
        fav = or_ret * sim.side
        if abs(or_ret) < OR_TH:
            return s2(i, hm, sim)
        if fav > 0:
            if hm < "09:30":
                return None
            typ, _ = s2(i, hm, sim)
            return (typ, 2 * CHILD_VALUE)
        if hm < "13:00":
            return ("passive", CHILD_VALUE)
        return s2(i, hm, sim)
    return f


# ----------------------------------------------------------------- main loop
def main():
    or_sig = load_or_signal()
    rows = []
    tickers = [f[:-4] for f in sorted(os.listdir(IN_DIR)) if f.endswith(".csv")]
    for tk in tickers:
        df = pd.read_csv(os.path.join(IN_DIR, f"{tk}.csv"))
        df["time"] = pd.to_datetime(df["time"])
        for c in ["open", "high", "low", "close"]:
            df[c] = df[c] * 1000.0           # nghin -> VND
        df["date"] = df["time"].dt.date.astype(str)
        df["hm"] = df["time"].dt.strftime("%H:%M")
        df = df[(df["hm"] >= "09:15") & (df["hm"] <= "14:30")]
        for d, g in df.groupby("date"):
            if d not in or_sig or len(g) < 200:
                continue
            g = g.sort_values("time").reset_index(drop=True)
            day_val = (g["close"] * g["volume"]).sum()
            if day_val < 5 * ORDER_VALUE:    # ngay qua mong -> order 1B khong realistic
                continue
            bars = {c: g[c].to_numpy() for c in ["open", "high", "low", "close", "volume"]}
            bars["hm"] = g["hm"].to_numpy()
            arr = bars["open"][0]
            orr = or_sig[d]
            for side, sname in [(1, "buy"), (-1, "sell")]:
                strats = {"S0": make_s0(), "S1": make_s1(orr),
                          "S2": make_s2(), "S3": make_s3(orr)}
                res = {}
                ok = True
                for k, sch in strats.items():
                    out = Sim(bars, side).run(sch)
                    if out is None:
                        ok = False
                        break
                    vwap, filled, forced, unfilled = out
                    # shortfall (bps): mua duong = dat hon arrival; phan khong khop
                    # mark tai close cuoi ngay (chi phi co hoi cung dau voi side)
                    lastpx = bars["close"][-1]
                    eff = (vwap * filled + lastpx * unfilled) / ORDER_VALUE \
                        if ORDER_VALUE else vwap
                    isf = side * (eff / arr - 1) * 1e4
                    res[k] = (isf, filled / ORDER_VALUE, forced / ORDER_VALUE)
                if not ok:
                    continue
                row = {"ticker": tk, "date": d, "side": sname, "or_ret": orr,
                       "day_value_b": day_val / 1e9}
                for k, (isf, fr, fo) in res.items():
                    row[f"{k}_isf"] = isf
                    row[f"{k}_fill"] = fr
                    row[f"{k}_forced"] = fo
                rows.append(row)
        print(f"[{tk}] xong, cum rows={len(rows)}")
    R = pd.DataFrame(rows)
    R.to_csv(OUT_CSV, index=False)
    print(f"\nSaved {len(R):,} obs -> {OUT_CSV}")
    report(R)


def report(R):
    R["year"] = R["date"].str[:4]
    R["or_bucket"] = np.where(R["or_ret"].abs() < OR_TH, "FLAT",
                       np.where(R["or_ret"] > 0, "OR+", "OR-"))

    def daily_diff_t(R, col):
        d = (R[col] - R["S0_isf"]).groupby(R["date"]).mean()
        return d.mean(), d.std(ddof=1) / np.sqrt(len(d)) if len(d) > 2 else np.nan, len(d)

    print("\n===== TONG QUAN (shortfall bps vs arrival 09:15 — THAP HON = TOT) =====")
    print(f"{'strategy':10s} {'mean isf':>9s} {'fill%':>6s} {'forced%':>8s}")
    for k in ["S0", "S1", "S2", "S3"]:
        print(f"{k:10s} {R[f'{k}_isf'].mean():9.1f} {100*R[f'{k}_fill'].mean():6.1f} "
              f"{100*R[f'{k}_forced'].mean():8.1f}")

    print("\n===== DELTA vs S0 (am = tiet kiem), t-stat cluster theo ngay =====")
    for k in ["S1", "S2", "S3"]:
        m, se, n = daily_diff_t(R, f"{k}_isf")
        t = m / se if se and se > 0 else np.nan
        print(f"{k}: {m:+7.2f} bps  (t={t:+.2f}, n_days={n})")

    for dim in ["side", "or_bucket", "year"]:
        print(f"\n===== DELTA vs S0 theo {dim} =====")
        for v, grp in R.groupby(dim):
            line = f"{str(v):6s}"
            for k in ["S1", "S2", "S3"]:
                d = (grp[f"{k}_isf"] - grp["S0_isf"]).groupby(grp["date"]).mean()
                t = d.mean() / (d.std(ddof=1) / np.sqrt(len(d))) if len(d) > 5 else np.nan
                line += f" | {k} {d.mean():+7.2f} (t{t:+.1f})"
            print(line + f"  n={len(grp):,}")

    # thanh khoan: chia 2 nhom theo median day_value
    med = R.groupby("ticker")["day_value_b"].median()
    liq = set(med[med >= med.median()].index)
    R["liq"] = np.where(R["ticker"].isin(liq), "LIQUID", "SMALL")
    print("\n===== DELTA vs S0 theo thanh khoan =====")
    for v, grp in R.groupby("liq"):
        line = f"{v:6s}"
        for k in ["S1", "S2", "S3"]:
            d = (grp[f"{k}_isf"] - grp["S0_isf"]).groupby(grp["date"]).mean()
            t = d.mean() / (d.std(ddof=1) / np.sqrt(len(d))) if len(d) > 5 else np.nan
            line += f" | {k} {d.mean():+7.2f} (t{t:+.1f})"
        print(line + f"  n={len(grp):,}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        report(pd.read_csv(OUT_CSV, dtype={"date": str}))
    else:
        main()
