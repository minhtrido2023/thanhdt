"""Fama-MacBeth cross-sectional: IC cua value co doi theo DT5G state / theo do phan tan dinh gia?

PHUONG PHAP (chon (a) Fama-MacBeth, KHONG dung OLS gop dong):
  moi NGAY QUAN SAT chay 1 hoi quy cross-sectional rieng  fwd ~ a + b*value  =>  1 he so b/ngay.
  Chuoi {b_t} theo THANG la don vi thong ke; N hieu dung = SO THANG, khong phai so dong panel.
  Ngay quan sat = phien cuoi thang => fwd20 (20 phien ~ 1 thang) gan nhu KHONG chong lan
  => dung t-stat thuong cho fwd20; fwd60 chong lan 3 thang => Newey-West lag 2.
"""
import numpy as np, pandas as pd, os
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
MIN_N = 20                      # so ma toi thieu/ngay de hoi quy cross-sectional co nghia
STATE_NAME = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}


def nw_se(x, lags):
    """Newey-West SE cua trung binh chuoi x."""
    x = np.asarray(x, float); n = len(x); mu = x.mean(); e = x - mu
    g0 = (e @ e) / n
    s = g0
    for L in range(1, lags + 1):
        g = (e[L:] @ e[:-L]) / n
        s += 2 * (1 - L / (lags + 1)) * g
    return np.sqrt(max(s, 0) / n)


def summarize(x, lags=0, label=""):
    x = np.asarray(pd.Series(x).dropna(), float)
    n = len(x)
    if n < 3:
        return dict(label=label, N=n, mean=np.nan, t=np.nan, p=np.nan, lo90=np.nan, hi90=np.nan)
    mu = x.mean()
    se = nw_se(x, lags) if lags else x.std(ddof=1) / np.sqrt(n)
    t = mu / se if se > 0 else np.nan
    q = stats.t.ppf(0.95, n - 1)
    return dict(label=label, N=n, mean=mu, t=t, p=2 * (1 - stats.t.cdf(abs(t), n - 1)),
                lo90=mu - q * se, hi90=mu + q * se)


def per_date(p, vcol, ycol):
    """1 dong/ngay: he so FM (pp tren toan dai value 0->1) + rank-IC Spearman."""
    rows = []
    for d, g in p.groupby("d", sort=True):
        g = g[[vcol, ycol, "state"]].dropna()
        if len(g) < MIN_N:
            continue
        x = g[vcol].to_numpy(); y = g[ycol].to_numpy()
        b = np.polyfit(x, y, 1)[0]
        ic = stats.spearmanr(x, y).statistic
        rows.append(dict(d=d, state=int(g.state.iloc[0]), n=len(g), beta=b * 100, ic=ic))
    return pd.DataFrame(rows)


def report(fm, lags, tag):
    print(f"\n{'='*88}\n{tag}   (N = SO THANG doc lap, khong phai so dong panel)\n{'='*88}")
    groups = [("TAT CA", fm.index == fm.index),
              ("CRISIS+BEAR", fm.state.isin([1, 2])),
              ("NEUTRAL", fm.state == 3),
              ("BULL+EXBULL", fm.state.isin([4, 5]))]
    for st in sorted(fm.state.unique()):
        groups.append((f"  .{STATE_NAME[st]}", fm.state == st))
    print(f"{'nhom':<14}{'N thang':>8}{'IC tb':>9}{'t':>7}{'p':>8}{'CI90 IC':>20}"
          f"{'beta(pp)':>10}{'t':>7}{'CI90 beta':>20}")
    out = {}
    for name, m in groups:
        sub = fm[m]
        a = summarize(sub.ic, lags); b = summarize(sub.beta, lags)
        out[name.strip()] = (a, b)
        print(f"{name:<14}{a['N']:>8}{a['mean']:>9.3f}{a['t']:>7.2f}{a['p']:>8.3f}"
              f"{f'[{a['lo90']:+.3f};{a['hi90']:+.3f}]':>20}"
              f"{b['mean']:>10.2f}{b['t']:>7.2f}{f'[{b['lo90']:+.1f};{b['hi90']:+.1f}]':>20}")
    # so sanh cap nhom (Welch tren chuoi he so theo thang)
    print("  -- hieu giua nhom (Welch t tren chuoi IC theo thang) --")
    for a, b in (("CRISIS+BEAR", "NEUTRAL"), ("CRISIS+BEAR", "BULL+EXBULL"), ("NEUTRAL", "BULL+EXBULL")):
        xa = fm[fm.state.isin([1, 2] if a == "CRISIS+BEAR" else [3] if a == "NEUTRAL" else [4, 5])].ic.dropna()
        xb = fm[fm.state.isin([1, 2] if b == "CRISIS+BEAR" else [3] if b == "NEUTRAL" else [4, 5])].ic.dropna()
        t, pv = stats.ttest_ind(xa, xb, equal_var=False)
        print(f"     {a:<12} - {b:<12}: d(IC)={xa.mean()-xb.mean():+.3f}  t={t:+.2f}  p={pv:.3f}")
    return out


def dispersion(p):
    """Do phan tan dinh gia cross-sectional/ngay — tinh tren earn_yield THO (percentile luon deu)."""
    rows = []
    for d, g in p.groupby("d", sort=True):
        ey = g.earn_yield.dropna()
        if len(ey) < MIN_N:
            continue
        q1, q3 = ey.quantile([.25, .75])
        rows.append(dict(d=d, state=int(g.state.iloc[0]), iqr=q3 - q1, sd=ey.std(),
                         med=ey.median(), cv=ey.std() / ey.median() if ey.median() > 0 else np.nan))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    p = pd.read_csv(os.path.join(HERE, "panel.csv.gz"), parse_dates=["d"])
    print(f"panel {len(p)} dong / {p.d.nunique()} thang / {p.ticker.nunique()} ma; "
          f"MIN_N/ngay = {MIN_N}")

    res = {}
    for vcol in ("ey_pct", "vs_proxy"):
        for ycol, lags in (("fwd20", 0), ("fwd60", 2)):
            fm = per_date(p, vcol, ycol)
            res[(vcol, ycol)] = fm
            report(fm, lags, f"CAU HOI 1 — value={vcol}, horizon={ycol}"
                             f"{' (NW lag2, cua so chong lan)' if lags else ' (khong chong lan)'}")

    # ---------------- CAU HOI 2 ----------------
    dp = dispersion(p)
    rad = pd.read_csv(os.path.join(HERE, "..", "exp_value_radar", "radar.csv"), parse_dates=["time"])
    dp = dp.merge(rad[["time", "radar3_roll"]], left_on="d", right_on="time", how="left")
    print(f"\n{'='*88}\nCAU HOI 2a — do phan tan dinh gia (IQR cua 1/PE) theo state / vs Value Radar\n{'='*88}")
    print(dp.groupby("state").agg(N=("iqr", "size"), iqr_tb=("iqr", "mean"), iqr_med=("iqr", "median"),
                                  cv_med=("cv", "median"), ey_med=("med", "median")).round(4).to_string())
    ok = dp.dropna(subset=["radar3_roll"])
    print(f"  Spearman(IQR, radar3_roll) = {stats.spearmanr(ok.iqr, ok.radar3_roll).statistic:+.3f} "
          f"(p={stats.spearmanr(ok.iqr, ok.radar3_roll).pvalue:.3f}, N={len(ok)} thang)")
    print(f"  Spearman(IQR, median 1/PE) = {stats.spearmanr(dp.iqr, dp.med).statistic:+.3f}")
    print(f"  Spearman(state, IQR)       = {stats.spearmanr(dp.state, dp.iqr).statistic:+.3f} "
          f"(p={stats.spearmanr(dp.state, dp.iqr).pvalue:.3f})")

    dp["terc"] = pd.qcut(dp.iqr, 3, labels=["HEP", "GIUA", "RONG"])
    print(f"\n{'='*88}\nCAU HOI 2b — IC cua value theo tercile do phan tan\n{'='*88}")
    for (vcol, ycol), fm in res.items():
        lags = 2 if ycol == "fwd60" else 0
        f2 = fm.merge(dp[["d", "terc", "iqr"]], on="d", how="inner")
        print(f"\n-- value={vcol}, {ycol} --")
        print(f"{'tercile':<10}{'N thang':>8}{'IC tb':>9}{'t':>7}{'p':>8}{'CI90':>20}{'beta(pp)':>10}")
        for tc in ["HEP", "GIUA", "RONG"]:
            sub = f2[f2.terc == tc]
            a = summarize(sub.ic, lags); b = summarize(sub.beta, lags)
            print(f"{tc:<10}{a['N']:>8}{a['mean']:>9.3f}{a['t']:>7.2f}{a['p']:>8.3f}"
                  f"{f'[{a['lo90']:+.3f};{a['hi90']:+.3f}]':>20}{b['mean']:>10.2f}")
        xr = f2[f2.terc == "RONG"].ic.dropna(); xh = f2[f2.terc == "HEP"].ic.dropna()
        t, pv = stats.ttest_ind(xr, xh, equal_var=False)
        print(f"   RONG - HEP: d(IC)={xr.mean()-xh.mean():+.3f}  t={t:+.2f}  p={pv:.3f}")
        print(f"   Spearman(IQR lien tuc, IC) = {stats.spearmanr(f2.iqr, f2.ic).statistic:+.3f} "
              f"(p={stats.spearmanr(f2.iqr, f2.ic).pvalue:.3f})")

    # tuong tac 2 chieu (chi bao cao mo ta — N moi o rat mong)
    fm = res[("ey_pct", "fwd20")].merge(dp[["d", "terc"]], on="d")
    fm["grp"] = np.where(fm.state.isin([1, 2]), "CRISIS+BEAR",
                np.where(fm.state == 3, "NEUTRAL", "BULL+EXBULL"))
    print(f"\n-- mo ta: IC tb theo (state x tercile phan tan), value=ey_pct/fwd20 --")
    print(fm.pivot_table(index="grp", columns="terc", values="ic", aggfunc=["mean", "size"],
                         observed=False).round(3).to_string())

    for (vcol, ycol), fm2 in res.items():
        fm2.to_csv(os.path.join(HERE, f"fm_{vcol}_{ycol}.csv"), index=False)
    dp.to_csv(os.path.join(HERE, "dispersion.csv"), index=False)
