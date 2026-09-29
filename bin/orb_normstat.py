# -*- coding: utf-8 -*-
"""
normstat.py -- Phi / Phi^-1 tu chuan, KHONG can scipy.

Ly do ton tai: he nay co 2 interpreter (system python3 3.10 khong co scipy;
$DNA_PYEXE = wc_venv co scipy 1.17). Script canh bao som (Viec C) se chay duoi
cron/python3, nen moi phep tinh phan phoi phai chay duoc o CA HAI. Sai so da do
nguoc lai scipy: xem normstat_selfcheck() ben duoi (max |diff| < 5e-9 tren ca CDF
lan PPF trong vung dung).
"""
import math

def ncdf(x):
    return 0.5 * math.erfc(-x / math.sqrt(2.0))

# Acklam's rational approximation, refined 1 buoc Halley => ~1e-15
_A = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
      1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
_B = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
      6.680131188771972e+01, -1.328068155288572e+01]
_Cc = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
       -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
_D = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
      3.754408661907416e+00]

def nppf(p):
    if not (0.0 < p < 1.0):
        raise ValueError(f"nppf: p phai trong (0,1), nhan {p}")
    pl, ph = 0.02425, 1 - 0.02425
    if p < pl:
        q = math.sqrt(-2 * math.log(p))
        x = (((((_Cc[0]*q+_Cc[1])*q+_Cc[2])*q+_Cc[3])*q+_Cc[4])*q+_Cc[5]) / \
            ((((_D[0]*q+_D[1])*q+_D[2])*q+_D[3])*q+1)
    elif p <= ph:
        q = p - 0.5; r = q*q
        x = (((((_A[0]*r+_A[1])*r+_A[2])*r+_A[3])*r+_A[4])*r+_A[5])*q / \
            (((((_B[0]*r+_B[1])*r+_B[2])*r+_B[3])*r+_B[4])*r+1)
    else:
        q = math.sqrt(-2 * math.log(1 - p))
        x = -(((((_Cc[0]*q+_Cc[1])*q+_Cc[2])*q+_Cc[3])*q+_Cc[4])*q+_Cc[5]) / \
             ((((_D[0]*q+_D[1])*q+_D[2])*q+_D[3])*q+1)
    e = ncdf(x) - p
    u = e * math.sqrt(2*math.pi) * math.exp(x*x/2)
    return x - u / (1 + x*u/2)

def normstat_selfcheck(verbose=True):
    """Doi chieu voi scipy neu co; neu khong co scipy thi kiem tinh nhat quan noi tai."""
    pts = [-4,-3,-2,-1,-0.5,0,0.5,1,2,3,4]
    ps  = [1e-6,1e-4,0.001,0.01,0.025,0.1,0.25,0.5,0.75,0.9,0.975,0.99,0.999,1-1e-6]
    try:
        from scipy.stats import norm
        dc = max(abs(ncdf(x) - norm.cdf(x)) for x in pts)
        dp = max(abs(nppf(p) - norm.ppf(p)) for p in ps)
        ok = dc < 5e-9 and dp < 5e-9
        if verbose: print(f"  normstat vs scipy: max|dCDF|={dc:.2e} max|dPPF|={dp:.2e} -> {'PASS' if ok else 'FAIL'}")
        return ok
    except ImportError:
        dr = max(abs(ncdf(nppf(p)) - p) for p in ps)
        ok = dr < 1e-12
        if verbose: print(f"  normstat (khong co scipy) round-trip CDF(PPF(p))-p: max={dr:.2e} -> {'PASS' if ok else 'FAIL'}")
        return ok

if __name__ == "__main__":
    import sys
    sys.exit(0 if normstat_selfcheck() else 1)
