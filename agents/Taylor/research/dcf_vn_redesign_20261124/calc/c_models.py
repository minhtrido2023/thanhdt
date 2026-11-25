# -*- coding: utf-8 -*-
"""c_models.py — tính V/B và V/P cho 19 biến thể chính + 8 độ nhạy (khai ở PRELOCK §1). Mù giá trừ E/F.
In: ../out/panel_m.parquet (+ engine_A.parquet, panel_m_lag1.parquet). Out: ../out/vp.parquet (cột lv_<variant> = log V/P)."""
import os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
ERP = 5.5; H = 10

def rim_vb(roe_start, roe_n, r, gT, ret, kappa=0.4, stage1=True, flat=False):
    # kappa: số vô hướng hoặc mảng (độ bền ROE vượt trội theo từng mã)
    """V/B theo thu nhập thặng dư 10 năm + terminal. Mọi đầu vào là mảng numpy (thập phân)."""
    roe_lr = roe_n if flat else r + kappa * (roe_n - r)
    B = np.ones_like(roe_n); pv = np.zeros_like(roe_n)
    for t in range(1, H + 1):
        if flat:
            roe_t = roe_n
        elif stage1:
            roe_t = np.where(t <= 3, roe_start + (roe_n - roe_start) * t / 3.0, roe_n + (roe_lr - roe_n) * (t - 3) / 7.0)
        else:
            roe_t = roe_n + (roe_lr - roe_n) * t / 10.0
        g_raw = np.clip(roe_t * ret, 0, 0.15)
        g_t = gT + (g_raw - gT) * (H - t) / (H - 1.0)
        g_t = np.minimum(g_t, np.maximum(roe_t, 0.0))          # không giả định phát hành vốn ngoài
        pv += (roe_t - r) * B / (1 + r) ** t
        B = B * (1 + g_t)
    g_term = np.minimum(gT, np.maximum(roe_lr, 0.0))
    tv = (roe_lr - r) * B / (r - g_term) / (1 + r) ** H
    return np.maximum(1 + pv + tv, 0.2)

def run(pan, tag=""):
    out = {}
    roe = pan.roe.clip(-0.3, 0.5).values
    ret = (1 - pan.payout.fillna(0.3)).clip(0.1, 1.0).values
    rs = {"fix": np.full(len(pan), 0.1225), "adp": (pan.dep.values + ERP) / 100, "slow": (pan.dep_slow.fillna(pan.dep).values + ERP) / 100}
    def n_roe(W, shrink=True):
        tc = pan[f"roe_tc{W}"].clip(-0.1, 0.4).values
        if not shrink:
            return tc
        n = pan[f"n_tc{W}"].values; w = n / (n + 8.0)
        sec = pan[f"sec_roe{W}"].clip(-0.1, 0.4).values
        return w * tc + (1 - w) * sec
    for rk, r in rs.items():
        gT = np.minimum(0.055, r - 0.04)
        vb = {"B": rim_vb(roe, roe, r, gT, ret, flat=True),
              "C": rim_vb(roe, n_roe(5, False), r, gT, ret, flat=True),
              "D0": rim_vb(roe, n_roe(5, False), r, gT, ret, 0.4, stage1=False),
              "D": rim_vb(roe, n_roe(5), r, gT, ret, 0.4, stage1=True)}
        for k, v in vb.items():
            out[f"lv_{k}_{rk}"] = np.log(v * pan.bp.values)
            out[f"vb_{k}_{rk}"] = v
        e = np.log(pan.pb_med5.values * pan.bp.values)
        out[f"lv_E_{rk}"] = e                                   # E không phụ thuộc r (khai 3 lần cho đủ lưới)
        out[f"lv_F_{rk}"] = 0.5 * (out[f"lv_D_{rk}"] + e)
    # --- 8 độ nhạy trên D (r fix trừ khi ghi khác) ---
    r = rs["fix"]; gT = np.minimum(0.055, r - 0.04)
    sens = {"Dk0": rim_vb(roe, n_roe(5), r, gT, ret, 0.0), "Dk7": rim_vb(roe, n_roe(5), r, gT, ret, 0.7),
            "Dw3": rim_vb(roe, n_roe(3), r, gT, ret, 0.4), "Dw7": rim_vb(roe, n_roe(7), r, gT, ret, 0.4),
            "Dnos1": rim_vb(roe, n_roe(5), r, gT, ret, 0.4, stage1=False)}
    r135 = np.full(len(pan), 0.135); sens["Dr135"] = rim_vb(roe, n_roe(5), r135, np.minimum(0.055, r135 - 0.04), ret, 0.4)
    illiq = (pan.tv.fillna(0).values < pan.tv_med_uni.fillna(np.inf).values)
    rl = r + 0.01 * illiq; sens["Dliq"] = rim_vb(roe, n_roe(5), rl, np.minimum(0.055, rl - 0.04), ret, 0.4)
    # --- SAU PRELOCK (thăm dò, khai ở REPORT §Lệch prelock): H = độ bền theo mã + trộn TTM cho mã không chu kỳ ---
    cyc = pan.route.isin(["CYCLICAL", "REALESTATE", "SECURITIES"]).values
    rn = n_roe(5); rn_h = np.where(cyc, rn, 0.5 * rn + 0.5 * np.clip(roe, -0.1, 0.4))
    rmin = pan.roe_min5.clip(-0.1, 0.4).values
    with np.errstate(divide="ignore", invalid="ignore"):
        dur = np.where(rn_h > r + 0.005, np.clip((rmin - r) / (rn_h - r), 0.0, 0.9), 0.4)
    dur = np.where(pan.n_tc5.values >= 12, dur, np.minimum(dur, 0.4))       # lịch sử < 3 năm: không cho độ bền cao
    sens2 = {"H": rim_vb(roe, rn_h, r, gT, ret, dur), "Hd": rim_vb(roe, rn, r, gT, ret, dur)}
    for k, v in {**sens, **sens2}.items():
        out[f"lv_{k}_fix"] = np.log(v * pan.bp.values); out[f"vb_{k}_fix"] = v
    return pd.DataFrame(out, index=pan.index)

pan = pd.read_parquet(os.path.join(OUT, "panel_m.parquet"))
res = pd.concat([pan, run(pan)], axis=1)
# độ nhạy thứ 8: lag +1 quý (panel riêng) -> nối theo (ticker, ym)
p1 = os.path.join(OUT, "panel_m_lag1.parquet")
if os.path.exists(p1):
    l1 = pd.read_parquet(p1); r1 = run(l1)
    l1 = pd.concat([l1[["ticker", "ym"]], r1[["lv_D_fix"]].rename(columns={"lv_D_fix": "lv_Dlag1_fix"})], axis=1)
    res = res.merge(l1, on=["ticker", "ym"], how="left")
# đối chứng A: FV engine tại cuối quý, giữ V cố định trong quý (V/P trượt theo Close)
pa = os.path.join(OUT, "engine_A.parquet")
if os.path.exists(pa):
    A = pd.read_parquet(pa); A = A[A.ok & (A.FV > 0)].copy()
    A["ym"] = pd.to_datetime(A["asof"]).dt.to_period("M").astype(str); A["lvA0"] = np.log(A.FV / A.P0)
    res = res.merge(A[["ticker", "ym", "lvA0"]], on=["ticker", "ym"], how="left")
    res = res.sort_values(["ticker", "ym"])
    res["_lva"] = res.lvA0 + np.log(res.Close)                   # log V theo đơn vị Close tại cuối quý
    res["_lva"] = res.groupby("ticker")._lva.ffill(limit=2)
    res["lv_A_fix"] = res._lva - np.log(res.Close); res = res.drop(columns=["_lva", "lvA0"])
# --- SAU PRELOCK: G = DCF × premium riêng của mã (trung vị 60 tháng TRƯỚC đó của log P/V, tối thiểu 24 tháng), λ ∈ {1; 0,5}
res = res.sort_values(["ticker", "ym"]).reset_index(drop=True)
for base in ("D0", "H"):
    med = res.groupby("ticker")[f"lv_{base}_fix"].transform(lambda x: x.shift(1).rolling(60, min_periods=24).median())
    res[f"lv_G1{base}_fix"] = res[f"lv_{base}_fix"] - med
    res[f"lv_G05{base}_fix"] = res[f"lv_{base}_fix"] - 0.5 * med
res.to_parquet(os.path.join(OUT, "vp.parquet"))
u = res[res.in_universe & (res.ym >= "2014-01")]
cols = [c for c in res.columns if c.startswith("lv_")]
print(u[cols].describe(percentiles=[.25, .5, .75]).T[["count", "25%", "50%", "75%"]].round(3).to_string())
