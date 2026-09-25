# -*- coding: utf-8 -*-
"""make_baseline.py -- dong bang 'KY VONG' cho monitor. Nguon = CHI 670 phien PRE-LIVE
cua config dang deploy (Viec A). KHONG dung phien live nao: neu khong thi monitor se
so live voi chinh live va khong bao gio bao duoc gi."""
import sys, io, json, os, hashlib, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd, orb_core as C

rng = np.random.default_rng(20260925)
R = C.sim(C.build_days(C.load_bars()))
pre = R[R["date"] < C.LIVE_START]
x = pre["net"].values
MU0, SD = float(x.mean()), float(x.std(ddof=1))

# envelope: phan phoi cum VA sd cua k phien LIEN TIEP trong pre-live.
# sd dung ENVELOPE BOOTSTRAP chu khong phai chi2: phan phoi loi nhuan co kurtosis 5.76,
# chi2 gia dinh chuan nen p-value cua no SAI o n nho (dry-run dau tien: 8/56 lan bao gia).
env, envsd = {}, {}
for k in [10,20,25,30,40,50,60,75,100,125,150]:
    if len(x) - k + 1 < 50: continue
    st = rng.integers(0, len(x)-k+1, size=40000)
    W = x[st[:,None] + np.arange(k)]
    cums = np.prod(1 + W, axis=1) - 1
    sds  = W.std(axis=1, ddof=1)
    env[str(k)]   = {f"p{p}": float(np.percentile(cums, p)) for p in (1,5,10,25,50,75,95)}
    envsd[str(k)] = {f"p{p}": float(np.percentile(sds, p)) for p in (0.5,1,5,50,95,99,99.5)}

def git_head(path):
    try:
        return subprocess.run(["git","-C",path,"rev-parse","--short","HEAD"],
                              capture_output=True, text=True, timeout=10).stdout.strip() or None
    except Exception:
        return None

b = {
 "_doc": "KY VONG dong bang cho orb_drift_monitor.py. CHI SU DUNG DE GIAM SAT. Khong duoc dung lam co so doi tham so chien luoc.",
 "generated": "2026-09-25", "job": "Taylor_20260925_103217",
 "config_monitored": {"src": "orb_pt.py", "exit_hm": C.EXIT_HM, "stop": None, "min_or": C.MIN_OR,
                      "slip_ticks": C.SLIP_TICKS, "fee_rt": C.FEE, "sizing": "fixed"},
 "baseline_window": {"source": "backtest PRE-LIVE cua dung config dang deploy",
                     "first": pre["date"].iloc[0], "last": pre["date"].iloc[-1], "n": int(len(x))},
 "moments": {"mu_bps": MU0*1e4, "sd_bps": SD*1e4, "snr_per_session": MU0/SD,
             "win_rate": float((x>0).mean()), "skew": float(pd.Series(x).skew()),
             "kurtosis": float(pd.Series(x).kurt()+3),
             "long_frac": float((pre["sig"]>0).mean()),
             "mean_abs_or_ret": float(pre["or_ret"].abs().mean()),
             "sd_abs_or_ret": float(pre["or_ret"].abs().std(ddof=1))},
 "cum_envelope_by_k_sessions": env,
 "sd_envelope_by_k_sessions": envsd,
 "cusum": {
   "_doc": "h chon bang MO PHONG ARL tren residual THAT (kurtosis 5.76), khong tu bang Gauss. Xem cusum_arl_extended.json.",
   "A_warn":  {"target": "mu -> 0 (edge chet)",      "k_bps": MU0*1e4/2, "h": 18.0,
               "arl0_sessions": 809,  "arl1_sessions": 215, "fpr_per_250_sessions": 0.266},
   "B_alert": {"target": "mu -> -mu0 (edge dao dau)", "k_bps": 0.0,       "h": 22.0,
               "arl0_sessions": 3580, "arl1_sessions": 184, "fpr_per_250_sessions": 0.067}},
 "sprt": {"h0": "mu = mu0", "h1": "mu = 0", "alpha": 0.05, "beta": 0.20,
          "bound_accept_h1": float(np.log(0.8/0.05)), "bound_accept_h0": float(np.log(0.2/0.95)),
          "expected_sessions_to_h1_if_true": 551, "expected_sessions_to_h0_if_true": 310},
 "power_reality_check": {
   "sessions_for_alpha05_power80_vs_zero": int(round(((1.6449+0.8416)/(MU0/SD))**2)),
   "note": "SNR 0.1003/phien. KHONG co phuong phap nao phat hien 'edge tu mu0 ve 0' trong vai chuc phien. Day la tran vat ly, khong phai lua chon thiet ke."},
 "provenance": {"tape_hist": "WC/data/vn30f1m_1min.csv", "tape_live": "research/orb_reeval_20260925/vn30f1m_live_snapshot_20260925.csv",
                "wc_head": git_head("/home/trido/thanhdt/WorkingClaude"), "mike_head": git_head("/home/trido/thanhdt/WorkingClaude/mike"),
                "orb_pt_sha256": hashlib.sha256(open("/home/trido/thanhdt/WorkingClaude/orb_pt.py","rb").read()).hexdigest()[:16]},
}
json.dump(b, open("orb_drift_baseline.json","w"), indent=1)
print(f"baseline ghi xong: mu0={MU0*1e4:+.3f}bps sd={SD*1e4:.2f}bps n={len(x)}"
      f" | envelope cho k={sorted(env, key=int)}")
print(f"  can {b['power_reality_check']['sessions_for_alpha05_power80_vs_zero']} phien de phan biet mu0 voi 0 (alpha 5%, power 80%)")
