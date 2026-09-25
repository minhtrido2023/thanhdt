# -*- coding: utf-8 -*-
"""
orb_core.py -- module dung chung cho validation config DANG DEPLOY cua orb_pt.py.

Muc dich: tai dung CHINH XAC logic orb_pt.py (khong phai vn30f_orb_strategy.py /
vn30f_orb_final.py, hai script do dung config KHAC tren 4 truc). Moi tham so o day
la BAN SAO tu orb_pt.py; doi mot con so o day ma khong doi orb_pt.py = so bao cao
khong con noi ve cai dang chay.

Config DANG DEPLOY (orb_pt.py, doc 2026-09-25):
  OR      : bar dau phien -> bar cuoi <= 09:30 (entry = close bar cuoi <= 09:30)
  signal  : sign(or_ret), bo phien sig==0
  exit    : close cua bar cuoi cung trong (09:30, 14:30]  (= bar 14:29 hoac 14:30)
  stop    : KHONG
  loc     : KHONG loc |OR| -- trade TAT CA phien co signal
  size    : co dinh (1 don vi)
  chi phi : slip 1 tick (0.1d) moi chieu theo huong xau + fee 0.6bps round-trip
  complete: len(op)>=10 va len(seg)>0 va bar cuoi cua phien >= 14:25

Nguon du lieu 1m:
  - lich su : WC/data/vn30f1m_1min.csv            2023-09-11 .. 2026-06-09
  - live    : research/orb_reeval_20260925/vn30f1m_live_snapshot_20260925.csv
                                                  2026-01-23 .. 2026-09-25
  Doi soat 21.272 bar trung nhau: 1 bar lech (high/low 0.3d, close 0.1d) => coi la
  cung tape. Ghep: uu tien file lich su cho ngay co trong ca hai (arbitrary nhung
  deterministic), live snapshot mo rong phan sau 2026-06-09.
"""
import numpy as np, pandas as pd, os

WC = "/home/trido/thanhdt/WorkingClaude"
RES = os.path.join(WC, "mike/agents/Taylor/research")

# --- tham so config DANG DEPLOY (ban sao tu orb_pt.py) ---
TICK       = 0.1
SLIP_TICKS = 1
FEE        = 0.00006
EXIT_HM    = "14:30"
STOP       = None
MIN_OR     = 0.0          # KHONG loc
LIVE_START = "2026-06-09" # STARTDATE cua orb_pt.py = ngay dau so paper


def load_bars():
    """Ghep 2 nguon 1m thanh 1 tape, tra DataFrame co cot time/open/high/low/close/date/hm."""
    h = pd.read_csv(os.path.join(WC, "data/vn30f1m_1min.csv"))
    l = pd.read_csv(os.path.join(RES, "orb_reeval_20260925/vn30f1m_live_snapshot_20260925.csv"))
    h["src"] = "hist"; l["src"] = "live"
    for d in (h, l):
        d["time"] = pd.to_datetime(d["time"])
        d["date"] = d["time"].dt.date
    hdays = set(h["date"].unique())
    # ngay 2026-06-09 trong file lich su bi CAT (bar cuoi 10:01) -> khong dung ban hist cho ngay do
    trunc = {pd.Timestamp("2026-06-09").date()}
    keep_h = h[~h["date"].isin(trunc)]
    keep_l = l[~l["date"].isin(hdays - trunc)]
    df = pd.concat([keep_h, keep_l], ignore_index=True).sort_values("time").reset_index(drop=True)
    df["hm"] = df["time"].dt.strftime("%H:%M")
    return df


def build_days(df):
    """Tach tape thanh per-day record theo dung dieu kien 'complete' cua orb_pt.py."""
    out = []
    for d, g in df.groupby("date"):
        g = g.sort_values("time")
        op  = g[g["hm"] <= "09:30"]
        seg = g[(g["hm"] > "09:30") & (g["hm"] <= EXIT_HM)]
        complete = len(op) >= 10 and len(seg) > 0 and g["hm"].iloc[-1] >= "14:25"
        if not complete:
            continue
        entry = float(op["close"].iloc[-1])
        or_ret = entry / float(g["close"].iloc[0]) - 1
        sig = int(np.sign(or_ret))
        if sig == 0:
            continue
        out.append({"date": str(d), "or_ret": or_ret, "sig": sig, "entry": entry,
                    "post": g[g["hm"] > "09:30"][["hm", "high", "low", "close"]].reset_index(drop=True)})
    return out


def sim(days, exit_hm=EXIT_HM, stop=STOP, min_or=MIN_OR,
        slip_ticks=SLIP_TICKS, fee=FEE):
    """Mo phong. Mac dinh = CHINH config dang deploy."""
    recs = []
    for dd in days:
        if abs(dd["or_ret"]) < min_or:
            continue
        sig, entry = dd["sig"], dd["entry"]
        seg = dd["post"][dd["post"]["hm"] <= exit_hm]
        if len(seg) == 0:
            continue
        exitpx = float(seg["close"].iloc[-1]); stopped = False
        if stop is not None:
            if sig > 0:
                hit = seg[seg["low"] <= entry * (1 - stop)]
                if len(hit): exitpx = entry * (1 - stop); stopped = True
            else:
                hit = seg[seg["high"] >= entry * (1 + stop)]
                if len(hit): exitpx = entry * (1 + stop); stopped = True
        ef = entry + sig * slip_ticks * TICK
        xf = exitpx - sig * slip_ticks * TICK
        net = sig * (xf / ef - 1) - fee
        recs.append({"date": dd["date"], "or_ret": dd["or_ret"], "sig": sig,
                     "entry": entry, "exit": exitpx, "net": net, "stopped": stopped})
    r = pd.DataFrame(recs)
    if len(r):
        r["date_dt"] = pd.to_datetime(r["date"])
    return r


def stats(r, ann=252):
    """Thong ke co ban. Sharpe annualise bang sqrt(252) (1 trade/phien)."""
    if r is None or len(r) == 0:
        return None
    x = r["net"].values
    n = len(x); mu = x.mean(); sd = x.std(ddof=1)
    sh = mu / sd * np.sqrt(ann) if sd > 0 else 0.0
    nav = np.cumprod(1 + x)
    mdd = float((nav / np.maximum.accumulate(nav) - 1).min())
    t = mu / (sd / np.sqrt(n)) if sd > 0 else 0.0
    return dict(n=n, wr=float((x > 0).mean()), mean_bps=mu * 1e4, sd_bps=sd * 1e4,
                sharpe=float(sh), cum=float(nav[-1] - 1), mdd=mdd, t=float(t),
                sr_per_obs=float(mu / sd) if sd > 0 else 0.0,
                skew=float(pd.Series(x).skew()), kurt=float(pd.Series(x).kurt() + 3.0),
                stopped_pct=float(r["stopped"].mean()) if "stopped" in r else 0.0)


def fmt(s, label=""):
    if s is None:
        return f"  {label:<26} (khong co trade)"
    return (f"  {label:<26} n={s['n']:>4}  WR={s['wr']*100:>5.1f}%  mean={s['mean_bps']:>+7.2f}bps"
            f"  Sharpe={s['sharpe']:>+6.2f}  cum={s['cum']*100:>+7.2f}%  MaxDD={s['mdd']*100:>+6.2f}%"
            f"  t={s['t']:>+5.2f}")
