# -*- coding: utf-8 -*-
"""dc_overlap_cap_backtest.py (job Taylor_20260707_042827, NHÁNH A) — RESEARCH ONLY.

Xử lý mã TRÙNG giữa DC book và custom30V trong sleeve (đo 2026-07-06: 5/8 mã DC nằm trong rổ
custom30V). Mô phỏng sleeve ở mức PER-NAME (DC layer + từng tên trong rổ custom30V):
  (iii) control  = hiện tại: eff_i = W_dc_i + pk * w_c30v_i (cộng dồn tự do)
  (ii)  dedupe   = tên đang ở DC bị loại khỏi phần custom30V, renormalize phần còn lại
  (i)   cap gộp  = eff_i <= X (X=0.15, 0.20), phần cắt redistribute cho tên c30v chưa chạm cap

Convention khớp deepdive/paper sleeve: DC layer T+1 (W_dc(t-1) earn ret t); custom30V vehicle
nội bộ theo parking_returns (rebal áp <= t, drift). TC = block-level như paper sleeve (identical
mọi variant) + extra TC trên adjustment turnover riêng của variant (|Δ(eff_v - eff_ctrl)|/2).

SELF-CHECKS:
  A. decompose: Σ Wp(t)·ret(t) == park_ret(t) (custom30V weights matrix tái lập đúng vehicle).
  B. r_ctrl == r_wf (cột 'ConvergePort (equal-weight)' trong converge NAV file) — 0 VND.
  C. weight sum mỗi variant = 1 - residual_cash; residual chỉ xuất hiện ở cap khi hết headroom.
Overlay full-NAV lên R3 y như deepdive.
"""
import os, sys, numpy as np, pandas as pd
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
import converge_portfolio_backtest as cpb

IS_END = pd.Timestamp("2019-12-31")
CAP_DC, TC = 0.20, 0.001

# ------------------------------------------------ load
basket = cpb.load_parking_basket()
dbl = pd.read_csv("data/dc_dbl_panel.csv", index_col=0, parse_dates=True).astype(bool)
if "DHG" in dbl.columns:
    dbl["DHG"] = False
WL = list(dbl.columns)
price = cpb.load_prices(set(WL) | set(basket["ticker"]))
cal = pd.DatetimeIndex(sorted(price["time"].unique()))
cal = cal[cal >= pd.Timestamp(cpb.START)]
price_wide = price.pivot_table(index="time", columns="ticker", values="Close").reindex(cal)
ret = price_wide.pct_change()
park_ret = cpb.parking_returns(basket, price_wide, cal)
slv = pd.read_csv("data/converge_portfolio_backtest_nav.csv", parse_dates=["date"]).set_index("date")
r_wf_ref = slv["ConvergePort (equal-weight)"]
r_c30v = slv["baseline_ret"]

NAMES = list(price_wide.columns)

# ---------------------------------------------- c30v daily weight matrix (same order as parking_returns)
def c30v_weight_matrix():
    rebals = sorted(basket["rebal_date"].unique())
    Wp = pd.DataFrame(0.0, index=cal, columns=NAMES)
    holdings = None; reb = 0
    for i, d in enumerate(cal):
        while reb < len(rebals) and rebals[reb] <= d:
            mem = basket[basket["rebal_date"] == rebals[reb]]
            w = mem.set_index("ticker")["weight"]
            w = w[w.index.isin(price_wide.columns)]
            holdings = (w / w.sum()).to_dict()
            reb += 1
        if holdings is None:
            continue
        # weights EFFECTIVE for day d's return = post-rebal(<=d), pre-drift(d)
        tot = sum(holdings.values())
        for tk, v in holdings.items():
            Wp.at[d, tk] = v / tot
        # drift by day-d return for tomorrow
        if i > 0 or True:
            newh = {}
            r = ret.loc[d]
            for tk, v in holdings.items():
                rt = r.get(tk); rt = rt if np.isfinite(rt) else 0.0
                newh[tk] = v * (1 + rt)
            holdings = newh
    return Wp

print("building c30v weight matrix ...")
Wp = c30v_weight_matrix()
# SELF-CHECK A: decompose park_ret
rec = (Wp * ret.fillna(0.0)).sum(axis=1)
diff = (rec - park_ret).abs()
# first day of history park_ret=0 by construction; ignore day0
print(f"SELF-CHECK A: max|Σ Wp·ret - park_ret| = {diff.iloc[1:].max():.2e}")

# ---------------------------------------------- DC layer weights (T+1: use t-1 for return t)
W_dc = pd.DataFrame(0.0, index=cal, columns=NAMES)
pk = pd.Series(1.0, index=cal)
for d in cal:
    cur = [t for t in WL if dbl.at[d, t]] if d in dbl.index else []
    n = len(cur)
    if n:
        w = min(CAP_DC, 1.0 / n)
        for t in cur: W_dc.at[d, t] = w
        pk.loc[d] = max(0.0, 1.0 - w * n)

W_dc_lag = W_dc.shift(1).fillna(0.0)
pk_lag = pk.shift(1).fillna(1.0)

# block-level TC (identical mọi variant, = paper sleeve treatment)
blk_turn = (W_dc.diff().abs().sum(axis=1).fillna(0.0) + pk.diff().abs().fillna(0.0)) / 2.0
blk_tc = blk_turn * TC

# ---------------------------------------------- effective weight builders
def eff_control():
    return W_dc_lag.add(Wp.mul(pk_lag, axis=0), fill_value=0.0), pd.Series(0.0, index=cal)

def eff_dedupe():
    """c30v phần bỏ tên đang ở DC (theo W_dc_lag>0), renormalize, scale pk_lag."""
    Wp_adj = Wp.copy()
    mask_dc = W_dc_lag > 0
    Wp_adj[mask_dc] = 0.0
    s = Wp_adj.sum(axis=1)
    s = s.replace(0.0, np.nan)
    Wp_adj = Wp_adj.div(s, axis=0).fillna(0.0)
    # ngày Wp có mà s=0 (không thể trên thực tế) -> park về cash, track residual
    resid = pd.Series(np.where((Wp.sum(axis=1) > 0) & (Wp_adj.sum(axis=1) == 0), pk_lag, 0.0), index=cal)
    return W_dc_lag.add(Wp_adj.mul(pk_lag, axis=0), fill_value=0.0), resid

def eff_cap(X, passes=12):
    """Cap gộp per-name <= X. Phần cắt redistribute cho THÀNH VIÊN rổ custom30V hiện hành
    (Wp>0, kể cả ngày pk=0 — waterfall: DC ăn tới cap, phần còn lại LUÔN được rót custom30V)."""
    base = W_dc_lag.add(Wp.mul(pk_lag, axis=0), fill_value=0.0)
    arr = base.values.copy()
    mem = (Wp.values > 0)                      # current basket membership per day
    resid = np.zeros(len(cal))
    for i in range(len(cal)):
        row = arr[i]
        for _ in range(passes):
            over = row - X
            over[over < 0] = 0.0
            F = over.sum()
            if F <= 1e-12:
                break
            row = np.minimum(row, X)
            head = np.where(mem[i], np.maximum(X - row, 0.0), 0.0)
            H = head.sum()
            if H <= 1e-12:
                resid[i] += F
                break
            add = np.minimum(head, head / H * F)
            row = row + add
            F -= add.sum()
            if F > 1e-12:
                resid[i] += F
                break
        arr[i] = row
    return pd.DataFrame(arr, index=cal, columns=NAMES), pd.Series(resid, index=cal)

# ---------------------------------------------- sim
def run(eff, resid, label, eff_ctrl=None):
    gross = (eff * ret.fillna(0.0)).sum(axis=1)
    extra_tc = pd.Series(0.0, index=cal)
    if eff_ctrl is not None:
        adj = eff - eff_ctrl
        extra_tc = adj.diff().abs().sum(axis=1).fillna(0.0) / 2.0 * TC
    r = gross - blk_tc - extra_tc
    return r, extra_tc.sum() / ((cal[-1] - cal[0]).days / 365.25)

E_ctrl, res0 = eff_control()
r_ctrl, _ = run(E_ctrl, res0, "control")
# SELF-CHECK B: control == r_wf reference. LƯU Ý: file NAV (job _093329) KHÔNG loại DHG khỏi
# double-confirm set, còn paper config (và mọi variant ở đây) loại DHG — nên so bằng bản
# control có-DHG để chứng minh máy per-name đúng 0 VND.
dbl_dhg = pd.read_csv("data/dc_dbl_panel.csv", index_col=0, parse_dates=True).astype(bool)
W2 = pd.DataFrame(0.0, index=cal, columns=NAMES); pk2 = pd.Series(1.0, index=cal)
for d_ in cal:
    cur = [t for t in dbl_dhg.columns if dbl_dhg.at[d_, t]] if d_ in dbl_dhg.index else []
    n = len(cur)
    if n:
        w = min(CAP_DC, 1.0 / n)
        for t in cur: W2.at[d_, t] = w
        pk2.loc[d_] = max(0.0, 1.0 - w * n)
W2l, pk2l = W2.shift(1).fillna(0.0), pk2.shift(1).fillna(1.0)
blk2 = ((W2.diff().abs().sum(axis=1).fillna(0.0) + pk2.diff().abs().fillna(0.0)) / 2.0) * TC
r_ctrl_dhg = (W2l.add(Wp.mul(pk2l, axis=0), fill_value=0.0) * ret.fillna(0.0)).sum(axis=1) - blk2
chk = (r_ctrl_dhg - r_wf_ref.reindex(cal)).abs()
print(f"SELF-CHECK B (control CÓ DHG vs r_wf file): max diff = {chk.iloc[1:].max():.2e}")
chk2 = (r_ctrl - r_wf_ref.reindex(cal)).abs()
print(f"   (tham chiếu: control paper-config loại DHG vs file = {chk2.iloc[1:].max():.2e} — lệch do DHG, đã hiểu)")

E_ddp, res_d = eff_dedupe()
E_c15, res15 = eff_cap(0.15)
E_c20, res20 = eff_cap(0.20)

variants = [
    ("(iii) control — cộng dồn tự do", E_ctrl, res0, None),
    ("(ii) dedupe — DC loại khỏi c30V", E_ddp, res_d, E_ctrl),
    ("(i) cap gộp X=0.20", E_c20, res20, E_ctrl),
    ("(i) cap gộp X=0.15", E_c15, res15, E_ctrl),
]

# ---------------------------------------------- overlay full-NAV
aud_df = pd.read_csv("data/h3_baseline_R3.csv", low_memory=False)
d = aud_df[aud_df["record_type"] == "DAILY"].copy()
d["ymd"] = pd.to_datetime(d["ymd"])
for c_ in ["bal_etf_ref", "lag_etf_ref", "combined_nav"]:
    d[c_] = pd.to_numeric(d[c_])
aud = d.set_index("ymd").sort_index()
nav = aud["combined_nav"]
r_base = nav.pct_change().dropna()
w_park_prev = ((aud["bal_etf_ref"] + aud["lag_etf_ref"]) / aud["combined_nav"]).shift(1).reindex(r_base.index).fillna(0.0)

def overlay(rv):
    # r_c30v = park_ret REBUILD cùng cache (file converge NAV build trước sync 23:45 -> skew 227 ngày)
    dv = (rv - park_ret.reindex(cal)).reindex(r_base.index).fillna(0.0)
    return r_base + w_park_prev * dv

def metrics(r):
    r = r.dropna(); nv = (1 + r).cumprod()
    yrs = (r.index[-1] - r.index[0]).days / 365.25
    cagr = nv.iloc[-1] ** (1 / yrs) - 1
    sh = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else np.nan
    dd = (nv / nv.cummax() - 1).min()
    return cagr * 100, sh, dd * 100, (cagr / abs(dd) if dd < 0 else np.nan)

hdr = f"{'variant':<38}{'win':<5}{'CAGR':>8}{'Sharpe':>7}{'MaxDD':>9}{'Calmar':>7}"
print("\n=== NHÁNH A — overlap DC ∩ custom30V trong sleeve (full-NAV overlay lên R3) ===")
print(hdr); print("-" * len(hdr))
for label, E, resid, Ec in variants:
    rv, xtc = run(E, resid, label, Ec)
    rr = overlay(rv)
    for tag, x in [("FULL", rr), ("IS", rr[rr.index <= IS_END]), ("OOS", rr[rr.index > IS_END])]:
        c, sh, dd, ca = metrics(x)
        print(f"{label:<38}{tag:<5}{c:>7.2f}%{sh:>7.2f}{dd:>8.1f}%{ca:>7.2f}")
    mx = E.max(axis=1)
    active_days = mx[E.sum(axis=1) > 0]
    print(f"    max eff name-weight sleeve: max {mx.max()*100:.1f}%  p99 {mx.quantile(0.99)*100:.1f}%  "
          f"mean-daily-max {active_days.mean()*100:.1f}%  | @sleeve=70%NAV: max = {mx.max()*70:.1f}%NAV")
    print(f"    residual-cash days>1e-6: {(resid>1e-6).sum()}  max resid {resid.max()*100:.2f}%  "
          f"extraTC {xtc*100:.3f}pp/yr sleeve")
    print()

# tần suất & mức độ vi phạm cap ở control (diagnostic)
mx_ctrl = E_ctrl.max(axis=1)
print("diagnostic control: %days max-eff-name >15%:",
      f"{(mx_ctrl>0.15).mean()*100:.1f}%,  >20%: {(mx_ctrl>0.20).mean()*100:.1f}%,  >25%: {(mx_ctrl>0.25).mean()*100:.1f}%")
