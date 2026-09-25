# -*- coding: utf-8 -*-
"""
calibrate_cusum.py -- chon nguong h cho CUSUM mot phia bang MO PHONG ARL,
khong lay tu bang tra cuu chuan hoa (bang chuan gia dinh Gauss; phan phoi that
cua ORB co kurtosis 5.73 nen ARL that lech khoi bang).

Nen mo phong = 670 phien PRE-LIVE (khong dung du lieu live -> dry-run o Viec C
moi la kiem tra doc lap).
"""
import sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np
import orb_core as C

rng = np.random.default_rng(7)
days = C.build_days(C.load_bars()); R = C.sim(days)
pre = R[R["date"] < C.LIVE_START]["net"].values
MU0, SD = float(pre.mean()), float(pre.std(ddof=1))
print(f"Nen: n={len(pre)} phien pre-live | mu0 = {MU0*1e4:+.3f}bps | sd = {SD*1e4:.2f}bps"
      f" | SNR/phien = {MU0/SD:.4f} | kurtosis = {float(__import__('pandas').Series(pre).kurt()+3):.2f}")

K = (MU0 + 0.0) / 2.0                       # reference value: giua H0 (mu0) va H1 (mu=0)
print(f"Reference k = {K*1e4:.3f}bps (giua mu0 va 0). CUSUM: S_i = max(0, S_(i-1) - (x_i - k)/sd)")

def run_len(mu_shift, h, B=40000, maxn=4000, boot=True):
    """ARL: so phien trung binh den khi S vuot h. mu_shift = mean muc tieu."""
    out = np.zeros(B); S = np.zeros(B); done = np.zeros(B, bool); n = np.full(B, maxn, float)
    resid = pre - MU0
    for i in range(1, maxn+1):
        if boot:
            x = mu_shift + resid[rng.integers(0, len(resid), size=B)]
        else:
            x = rng.normal(mu_shift, SD, size=B)
        S = np.maximum(0.0, S - (x - K)/SD)
        hit = (~done) & (S > h)
        n[hit] = i; done |= hit
        if done.all(): break
    return float(n.mean()), float(done.mean())

print("\n  ARL mo phong (bootstrap tu residual THAT, giu duoi day beo):")
print(f"  {'h':>5}{'ARL0 (mu=mu0)':>16}{'ARL1 (mu=0)':>14}{'ARL2 (mu=-mu0)':>16}{'FPR/250 phien':>15}")
print("  " + "-"*66)
rows = []
for h in [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0]:
    a0,_ = run_len(MU0, h); a1,_ = run_len(0.0, h); a2,_ = run_len(-MU0, h)
    fpr = 1 - np.exp(-250.0/a0) if a0 > 0 else 1.0
    rows.append(dict(h=h, arl0=a0, arl1=a1, arl2=a2, fpr250=fpr))
    print(f"  {h:>5.1f}{a0:>16.0f}{a1:>14.0f}{a2:>16.0f}{fpr*100:>14.1f}%")

print("\n  Doc: ARL0 = bao nhieu phien trung binh moi bao dong GIA khi chien luoc van dung ky vong.")
print("       ARL1 = bao nhieu phien de phat hien khi edge ve 0 (mu=0).")
print("       ARL2 = khi edge dao dau (mu=-mu0).")
json.dump({"mu0": MU0, "sd": SD, "k": K, "arl": rows},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cusum_arl.json"), "w"),
          indent=1, default=float)

# --- SPRT: bao nhieu phien den quyet dinh? ---
a, b = 0.05, 0.20
A_up = np.log((1-b)/a); B_lo = np.log(b/(1-a))
print(f"\n  SPRT (H0: mu=mu0, H1: mu=0, alpha={a}, beta={b}): bien tren {A_up:+.3f} / bien duoi {B_lo:+.3f}")
print(f"  LLR moi phien = ((mu1-mu0)/sd^2)*(x - (mu0+mu1)/2) ; E[LLR|H1] = {(MU0/SD**2)*(MU0/2)*1:.5f}"
      f"  => can ~{A_up/((MU0/SD**2)*(MU0/2)):.0f} phien de ket luan 'edge chet' neu edge THUC SU = 0")
print(f"  E[LLR|H0] = {-(MU0/SD**2)*(MU0/2):.5f} => can ~{abs(B_lo/((MU0/SD**2)*(MU0/2))):.0f} phien"
      f" de ket luan 'edge con song' neu edge dung bang mu0")
print("\n  => Do la RAO CAN VAT LY cua bai toan, khong phai khuyet diem cua phuong phap:")
print(f"     SNR/phien = {MU0/SD:.4f}. Bat ky test nao phan biet mu0 voi 0 o alpha=5%/power=80%")
print(f"     can ~{((1.645+0.8416)/(MU0/SD))**2:.0f} phien. Hien co 75.")
