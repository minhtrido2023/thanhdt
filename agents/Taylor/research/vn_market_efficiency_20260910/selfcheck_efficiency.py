"""Positive/negative controls for the VR + Hurst estimators (they must be able to FAIL)."""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from efficiency import variance_ratio, hurst_dfa

rng = np.random.default_rng(7)
T = 250
ok = True

def chk(label, cond, detail):
    global ok
    print(f"{'PASS' if cond else 'FAIL'}  {label}: {detail}")
    ok &= bool(cond)

# 1) white noise -> VR ~ 1, |z| small on average
vr2 = []; z2 = []
for _ in range(400):
    r = rng.normal(0, .015, T)
    v, z = variance_ratio(r, 2); vr2.append(v); z2.append(z)
chk("iid VR(2)~1", abs(np.mean(vr2) - 1) < 0.02, f"mean VR2={np.mean(vr2):.4f}")
chk("iid z2 ~ N(0,1)", 0.75 < np.std(z2) < 1.25, f"sd(z2)={np.std(z2):.3f}, |mean|={abs(np.mean(z2)):.3f}")
rej = np.mean(np.abs(z2) > 1.96)
chk("iid size ~5%", rej < 0.12, f"reject rate={rej:.3f}")

# 2) AR(1) phi=+0.2 (momentum/underreaction) -> VR(2) ~ 1+phi > 1, z positive
vr = []; zz = []
for _ in range(400):
    e = rng.normal(0, .015, T + 50); r = np.zeros(T + 50)
    for t in range(1, T + 50): r[t] = 0.2 * r[t-1] + e[t]
    v, z = variance_ratio(r[50:], 2); vr.append(v); zz.append(z)
chk("AR(1)+0.2 VR(2)>1", np.mean(vr) > 1.10, f"mean VR2={np.mean(vr):.4f} (theory ~1.20)")
chk("AR(1)+0.2 power", np.mean(np.array(zz) > 1.96) > 0.30, f"power={np.mean(np.array(zz) > 1.96):.3f}")

# 3) AR(1) phi=-0.2 (mean reversion) -> VR(2) < 1
vr = []
for _ in range(200):
    e = rng.normal(0, .015, T + 50); r = np.zeros(T + 50)
    for t in range(1, T + 50): r[t] = -0.2 * r[t-1] + e[t]
    vr.append(variance_ratio(r[50:], 2)[0])
chk("AR(1)-0.2 VR(2)<1", np.mean(vr) < 0.92, f"mean VR2={np.mean(vr):.4f} (theory ~0.80)")

# 4) Hurst: white noise -> ~0.5 ; cumulative-sum (H=1 trend) -> clearly >0.5
h_wn = np.mean([hurst_dfa(rng.normal(0, 1, 500)) for _ in range(60)])
chk("Hurst iid ~0.5", abs(h_wn - 0.5) < 0.06, f"mean H={h_wn:.4f}")
h_tr = np.mean([hurst_dfa(np.cumsum(rng.normal(0, 1, 500))) for _ in range(60)])
chk("Hurst trending >0.5", h_tr > 0.85, f"mean H={h_tr:.4f}")

print("\nSELFCHECK", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
