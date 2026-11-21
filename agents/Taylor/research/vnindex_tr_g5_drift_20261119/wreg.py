"""Ước sai số trọng số Δw_i = w_synth_i − w_VNIndex_i bằng hồi quy lệch ngày d_t lên lợi suất vượt
(r_i − r_VNI). d_t = Σ Δw_i·r_i ≈ Σ Δw_i·(r_i − r_VNI) (vì ΣΔw = 0). Chỉ đọc."""
import pandas as pd, numpy as np
D = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/vnindex_tr_g5_drift_20261119"
u = pd.read_pickle(f"{D}/u_frame_latest.pkl"); a = pd.read_pickle(f"{D}/day_frame_latest.pkl")
for lo, hi in (("2026-05-06", "2026-11-18"), ("2026-08-15", "2026-11-11")):
    uu = u[(u.time >= lo) & (u.time <= hi)]
    off = a.off[lo:hi]; d = (a.k2_synth_pr - a.off)[lo:hi]
    R = uu.pivot(index="time", columns="ticker", values="pr").reindex(off.index)
    W = uu.pivot(index="time", columns="ticker", values="w").reindex(off.index)
    names = ["VIC", "VHM", "VCB", "BID", "CTG", "TCB", "VPB", "GAS", "MBB", "HPG", "VPL", "FPT", "LPB", "MCH", "VRE", "GEE"]
    names = [n for n in names if n in R]
    X = R[names].sub(off, axis=0).fillna(0)
    beta, *_ = np.linalg.lstsq(X.values, d.values, rcond=None)
    res = d.values - X.values @ beta
    r2 = 1 - res.var() / d.var()
    print(f"\n{lo}..{hi} n={len(d)} R2={r2:.2f}  (Δw ước lượng, điểm %; w_synth TB)")
    out = pd.DataFrame({"dw_pp": beta * 100, "w_synth_pp": W[names].mean().values * 100}, index=names)
    # t-stat (OLS)
    s2 = res @ res / (len(d) - len(names)); cov = s2 * np.linalg.inv(X.T.values @ X.values)
    out["t"] = beta / np.sqrt(np.diag(cov))
    print(out.round(2).to_string())
    # Đóng góp vào G5 của từng mã qua Δw: Σ_t Δw_i (r_i - off)
    print("đóng góp tích luỹ pp:", (X.mul(beta).sum() * 100).round(3).sort_values().to_string())
