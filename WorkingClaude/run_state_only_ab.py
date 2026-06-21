# -*- coding: utf-8 -*-
"""Pure state-machine on VNINDEX NAV backtest: TQ34b vs Tinh_Te.
Allocation by state: CRISIS(0%) BEAR(20%) NEUTRAL(70%) BULL(100%) EX-BULL(130%).
T+1 execution, ramp 3 sessions (snap if |Δw|<3%), TC=0.1%, deposit=0%, borrow=10%/yr.
"""
import sys, io, os, subprocess, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import pandas as pd, numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
BQ_BIN = r"bq"

def bq(sql):
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); qp = f.name
    cmd = f'"{BQ_BIN}" query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv --max_rows=20000 < "{qp}"'
    r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    os.unlink(qp)
    return pd.read_csv(io.StringIO(r.stdout))

# Allocation
ALLOC = {1: 0.0, 2: 0.20, 3: 0.70, 4: 1.00, 5: 1.30}
TC = 0.001       # 0.1% per traded portion
DEPO_ANNUAL = 0.0
BORR_ANNUAL = 0.10
RAMP_DAYS = 3
SNAP_TOL = 0.03  # if |Δw|<3% snap immediately
SPY = 252.0

# Load VNI from clean cache (Downloads CSV converted earlier)
vni = pd.read_pickle(os.path.join(WORKDIR, "data/_cache_vnindex_2000_now.pkl"))
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
vni = vni[vni["time"] >= "2014-01-01"].copy().reset_index(drop=True)

# Load 2 state series
state_tq = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_4b_full_history.csv"))
state_tq["time"] = pd.to_datetime(state_tq["time"])

state_tt = bq("""SELECT s.time, s.state FROM `lithe-record-440915-m9.tav2_bq.vnindex_5state_archive_tinh_te_20260525_220329` AS s
WHERE s.time >= '2014-01-01' ORDER BY s.time""")
state_tt["time"] = pd.to_datetime(state_tt["time"])

def simulate(vni_df, state_df, name):
    df = vni_df.merge(state_df[["time","state"]], on="time", how="left")
    df["state"] = df["state"].ffill().fillna(3).astype(int)
    df["target_w"] = df["state"].map(ALLOC)
    n = len(df)
    nav = np.full(n, 1.0)
    w = np.full(n, 0.0)
    ret = df["Close"].pct_change().fillna(0).values
    target = df["target_w"].values
    # T+1 execution: target_w at t known at end of t-1
    for i in range(1, n):
        # Effective target = signal from i-1 (we trade at t to reach target_w[i-1])
        sig_target = target[i-1]
        prev_w = w[i-1]
        dw_total = sig_target - prev_w
        # Snap if small, else ramp
        if abs(dw_total) < SNAP_TOL:
            new_w = sig_target
        else:
            # Move 1/RAMP_DAYS of remaining gap per day
            step = dw_total / RAMP_DAYS
            new_w = prev_w + step
            # If we're within snap_tol after step, snap to target
            if abs(sig_target - new_w) < SNAP_TOL:
                new_w = sig_target
        traded = abs(new_w - prev_w)
        # Apply daily return
        r_day = ret[i]
        # Borrow on margin >100%, deposit on idle <100%
        cash_w = max(0, 1.0 - new_w)
        margin_w = max(0, new_w - 1.0)
        gross_ret = new_w * r_day + cash_w * (DEPO_ANNUAL/SPY) - margin_w * (BORR_ANNUAL/SPY)
        cost = traded * TC
        nav[i] = nav[i-1] * (1 + gross_ret - cost)
        w[i] = new_w
    df["nav"] = nav; df["w"] = w
    df["bh"] = df["Close"] / df["Close"].iloc[0]
    return df

def metrics(s, sd, ed, label):
    sub = s[(s.index>=sd) & (s.index<=ed)].dropna()
    if len(sub)<30: return None
    r = sub.pct_change().dropna()
    yrs = (sub.index[-1]-sub.index[0]).days/365.25
    spy = len(r)/yrs if yrs>0 else 252
    cagr = (sub.iloc[-1]/sub.iloc[0])**(1/yrs)-1 if yrs>0 else 0
    sh = r.mean()/r.std()*np.sqrt(spy) if r.std()>0 else 0
    dd = ((sub-sub.cummax())/sub.cummax()).min()
    cal = cagr/abs(dd) if dd<0 else 0
    return label, cagr*100, sh, dd*100, cal, sub.iloc[-1]/sub.iloc[0]

print("="*90)
print(f"  PURE STATE-MACHINE BACKTEST ON VNINDEX  (2014-2026, alloc 0/20/70/100/130%)")
print("="*90)
print(f"  States: TQ34b ({state_tq[state_tq.time>='2014-01-01'].time.max().date()})  vs  Tinh_Te ({state_tt.time.max().date()})")

df_tq = simulate(vni, state_tq, "TQ34b")
df_tt = simulate(vni, state_tt, "Tinh_Te")

# Align common dates
common = sorted(set(df_tq.time).intersection(set(df_tt.time)))
nav_tq = df_tq.set_index("time")["nav"].reindex(common)
nav_tt = df_tt.set_index("time")["nav"].reindex(common)
bh    = df_tq.set_index("time")["bh"].reindex(common)

print(f"\n[FULL period {common[0].date()} -> {common[-1].date()}]")
print(f"  {'System':<15}{'CAGR':>9}{'Sharpe':>9}{'MaxDD':>9}{'Calmar':>8}{'Wealth':>9}")
for s, label in [(nav_tq,"TQ34b"),(nav_tt,"Tinh_Te"),(bh,"B&H VNI")]:
    m = metrics(s, s.index[0], s.index[-1], label)
    print(f"  {m[0]:<14}{m[1]:>+8.2f}%{m[2]:>+9.2f}{m[3]:>+8.2f}%{m[4]:>+8.2f}{m[5]:>+9.2f}")

print(f"\nPeriod slices:")
print(f"{'Period':<12}{'TQ34b':>12}{'Tinh_Te':>12}{'Δ':>10}{'VNI B&H':>12}")
for p,sd,ed in [("FULL","2014-01-01","2026-05-26"),("IS_14_19","2014-01-01","2019-12-31"),
                ("OOS_20_23","2020-01-01","2023-12-31"),("OOS_24_26","2024-01-01","2026-05-26"),
                ("YTD_2026","2026-01-01","2026-05-26"),("Mid_18_23","2018-01-01","2023-12-31"),
                ("Q1_2026","2026-01-01","2026-03-31")]:
    sd_dt = pd.Timestamp(sd); ed_dt = pd.Timestamp(ed)
    mt = metrics(nav_tq, sd_dt, ed_dt, "TQ"); mn = metrics(nav_tt, sd_dt, ed_dt, "TT"); mv = metrics(bh, sd_dt, ed_dt, "B&H")
    if mt and mn:
        print(f"{p:<12}{mt[1]:>+10.2f}%{mn[1]:>+10.2f}%{mt[1]-mn[1]:>+8.2f}pp{mv[1]:>+11.2f}%")

# Save
out = pd.DataFrame({"TQ34b": nav_tq, "Tinh_Te": nav_tt, "VNI_BH": bh})
out.index.name = "time"
out.to_csv(os.path.join(WORKDIR, "data/state_only_ab.csv"))
print(f"\nSaved: data/state_only_ab.csv  shape={out.shape}")
print("DONE.")
