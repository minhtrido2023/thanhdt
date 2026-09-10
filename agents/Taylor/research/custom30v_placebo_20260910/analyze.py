# -*- coding: utf-8 -*-
"""VONG 5 custom30V PLACEBO — cong so phan ra (PREREG §1) + cac bang bat buoc (PREREG §5).
job Taylor_20260909_165335, PAPER-ONLY. Chi doc CSV do run_leg.sh / basket_probe.py sinh ra."""
import hashlib, os, sys, bisect
import numpy as np, pandas as pd
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dsr_pbo_annex import load_nav, daily_logret, moments, dsr, expected_max_sr, cscv_pbo  # noqa

OUT = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/custom30v_placebo_20260910"
_D = ("/home/trido/thanhdt/WorkingClaude/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge"
      "_etfliqcustompitg_wtnamecap_advprice_univpit")
LEGS = ["ctrl", "L1b", "P1d", "P2d", "P1r1", "P1r2", "P2r1", "P2r2"]
CTRL = "ctrl"
TREAT = ["L1b", "P1d", "P2d", "P1r1", "P1r2", "P2r1", "P2r2"]
N_TRIALS = 4          # PREREG §4: P1d, P2d, P1r, P2r (2 seed cua moi chan random = MOT uoc luong)
BLOCK = 63            # 1 quy = 1 chu ky rebal
PIN_MD5 = "7d053e6201c9d107685ff4d1dd9d2d2a"
PIN = dict(cagr=28.8627, final_B=1178.0099, calmar=1.6229, maxdd=-17.785)
path = lambda t: f"{_D}_exp_c30vpb{t.lower()}.csv"
pd.set_option("display.width", 260)

nav, raw = {}, {}
for t in LEGS:
    p = path(t)
    if not os.path.exists(p): print("MISSING", p); continue
    nav[t] = load_nav(p); raw[t] = pd.read_csv(p, low_memory=False)
HAVE = [t for t in LEGS if t in nav]

print("=== TIEN QUYET (PREREG §6): CONTROL vs PIN R3 ===")
md5 = hashlib.md5(open(path(CTRL), "rb").read()).hexdigest()
print(f"  ctrl md5 = {md5}  pin = {PIN_MD5}  -> "
      f"{'MATCH' if md5 == PIN_MD5 else '*** MISMATCH — DUNG, khong doc so treatment ***'}")

def metrics(s):
    r = daily_logret(s); yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1; dd = (s / s.cummax() - 1).min()
    return dict(cagr=cagr * 100, maxdd=dd * 100, calmar=cagr / abs(dd),
                sharpe=r.mean() / r.std(ddof=1) * np.sqrt(252), final_B=s.iloc[-1] / 1e9)
sub = lambda s, a, b: s[(s.index >= a) & (s.index <= b)]

rows = []
for t in HAVE:
    s = nav[t]; rows.append(dict(leg=t, **metrics(s),
        cagr_IS=metrics(sub(s, "2014-01-01", "2019-12-31"))["cagr"],
        cagr_OOS=metrics(sub(s, "2020-01-01", "2026-06-19"))["cagr"]))
T = pd.DataFrame(rows).set_index("leg"); c = T.loc[CTRL]
for k in ["cagr", "cagr_IS", "cagr_OOS", "calmar", "sharpe", "maxdd"]: T["d_" + k] = T[k] - c[k]
print(f"\n  ctrl CAGR {c['cagr']:.4f} (pin {PIN['cagr']}) | NAV {c['final_B']:.4f}B (pin {PIN['final_B']}) "
      f"| Calmar {c['calmar']:.4f} (pin {PIN['calmar']}) | MaxDD {c['maxdd']:.3f} (pin {PIN['maxdd']})")
print("\n=== A/B metrics ===");  print(T.round(4).to_string()); T.to_csv(f"{OUT}/ab_metrics.csv")

# ---------- CONG SO PHAN RA (PREREG §1) ----------
print("\n" + "=" * 100)
print("=== CONG SO PHAN RA — luat doc chot truoc o PREREG §1 ===")
TOT = T.loc["L1b", "d_cagr"]
def avg(ts): return float(np.mean([T.loc[t, "d_cagr"] for t in ts if t in T.index]))
P1 = {"det": T.loc["P1d", "d_cagr"] if "P1d" in T.index else np.nan, "rnd": avg(["P1r1", "P1r2"])}
P2 = {"det": T.loc["P2d", "d_cagr"] if "P2d" in T.index else np.nan, "rnd": avg(["P2r1", "P2r2"])}
dec = []
for lab, dp1, dp2 in [("CHINH (mode=top, bao toan thu hang)", P1["det"], P2["det"]),
                      ("PHU  (mode=random, TB 2 seed)",       P1["rnd"], P2["rnd"])]:
    inter = TOT - dp1 - dp2
    dec.append(dict(bo=lab, TONG=TOT, dP1_phaloang=dp1, dP2_tenmoi=dp2, tuongtac=inter,
                    pct_P1=100 * dp1 / TOT, pct_P2=100 * dp2 / TOT, pct_inter=100 * inter / TOT))
DEC = pd.DataFrame(dec); print(DEC.round(3).to_string(index=False)); DEC.to_csv(f"{OUT}/decomp.csv", index=False)
for r in dec:
    if abs(r["tuongtac"]) > 0.5 * abs(TOT):
        v = "TUONG TAC LON (>50% TONG) -> phan ra cong tinh KHONG mo ta duoc he nay"
    elif r["dP1_phaloang"] >= 0.60 * TOT and r["dP2_tenmoi"] <= 0.40 * TOT: v = "(X) PHA LOANG NGANH chiem uu the"
    elif r["dP2_tenmoi"] >= 0.60 * TOT and r["dP1_phaloang"] <= 0.40 * TOT: v = "(Y) THEM TEN RE chiem uu the"
    else: v = "HON HOP — khong gan nhan, bao ty le"
    print(f"  {r['bo']:38s} -> {v}")

# ---------- kiem chung co che: n_fin/ky ----------
print("\n=== §5.1 KIEM CHUNG CO CHE (n_fin moi ky, quy uoc route cua _placebo_reorder) ===")
fc = {}
for t in LEGS + ["probe_ctrl", "probe_L1b"]:
    p = f"{OUT}/fincount_{t}.csv"
    if os.path.exists(p): fc[t] = pd.read_csv(p, parse_dates=["rebal_date"]).set_index("rebal_date")
if "ctrl" in fc and "probe_ctrl" in fc:
    for a, b in [("ctrl", "probe_ctrl"), ("L1b", "probe_L1b")]:
        if a in fc and b in fc:
            same = fc[a]["n_fin"].equals(fc[b]["n_fin"])
            print(f"  dump NAV-day-du '{a}' vs dump build_pit '{b}': "
                  f"{'TRUNG TUNG DONG' if same else '*** LECH ***'}")
tab = []
for t in LEGS:
    if t not in fc: continue
    d = fc[t]
    tab.append(dict(leg=t, n_rebal=len(d), n_fin_mean=d.n_fin.mean(), n_fin_min=int(d.n_fin.min()),
                    n_fin_max=int(d.n_fin.max()), n_bank_mean=d.n_bank.mean(),
                    n_fin_pool_mean=d.n_fin_pool.mean(), n_pool_mean=d.n_pool.mean()))
FC = pd.DataFrame(tab).set_index("leg"); print(FC.round(3).to_string()); FC.to_csv(f"{OUT}/fincount_summary.csv")
print("\n  khop muc tieu (P1* phai = L1b tung ky; P2* phai = ctrl tung ky):")
for t, tgt in [("P1d", "L1b"), ("P1r1", "L1b"), ("P1r2", "L1b"),
               ("P2d", "ctrl"), ("P2r1", "ctrl"), ("P2r2", "ctrl")]:
    if t not in fc or tgt not in fc: continue
    a, b = fc[t]["n_fin"], fc[tgt]["n_fin"]
    j = a.to_frame("got").join(b.to_frame("want"), how="inner")
    bad = j[j.got != j.want]
    print(f"   {t:5s} vs {tgt:5s}: khop {len(j)-len(bad)}/{len(j)} ky"
          + ("" if bad.empty else "  LECH: " + ", ".join(f"{d.date()}({r.got}!={r.want})"
                                                         for d, r in bad.iterrows())))

# ---------- %ten + %trong so tai chinh ----------
print("\n=== §5.2 %TEN va %TRONG SO tai chinh (trong so = build_pit, selfcheck trong probe log) ===")
vp = pd.read_csv("/home/trido/thanhdt/WorkingClaude/data/value_panel_2014.csv",
                 parse_dates=["time"], usecols=["ticker", "time", "route"])
vp["q"] = vp["time"].dt.to_period("Q").dt.start_time
rt = vp.dropna(subset=["route"]).sort_values("time").groupby(["ticker", "q"])["route"].last()
rh = {tk: (list(g.index.get_level_values(1)), list(g.values)) for tk, g in rt.groupby(level=0)}
def route_asof(tk, q):
    e = rh.get(tk)
    if not e: return "UNKNOWN"
    i = bisect.bisect_right(e[0], pd.Timestamp(q)) - 1
    return e[1][i] if i >= 0 else e[1][0]
FIN = {"BANK", "INSURANCE", "SECURITIES"}
mrows = []
for t in HAVE:
    M = raw[t]; M = M[M.record_type == "CUSTOM_MEMBERS"].copy(); M["ymd"] = pd.to_datetime(M["ymd"])
    mm = {d: list(g.ticker) for d, g in M.groupby("ymd")}; ds = sorted(mm)
    fin = [np.mean([route_asof(x, pd.Timestamp(d).to_period("Q").start_time) in FIN for x in mm[d]]) for d in ds]
    bank = [np.mean([route_asof(x, pd.Timestamp(d).to_period("Q").start_time) == "BANK" for x in mm[d]]) for d in ds]
    tv = [len(set(mm[b]) - set(mm[a])) / len(mm[b]) for a, b in zip(ds, ds[1:])]
    row = dict(leg=t, n_rebal=len(ds), fin_name_share=100 * np.mean(fin),
               bank_name_share=100 * np.mean(bank), turnover_pct_q=100 * np.mean(tv))
    dw = f"{OUT}/dailyw_{t}.csv"
    if os.path.exists(dw):
        W = pd.read_csv(dw, parse_dates=["time"]).set_index("time")
        row.update(fin_w=100 * W.fin_w.mean(), fin_w_OOS=100 * W.fin_w[W.index >= "2020-01-01"].mean(),
                   fin_w_max=100 * W.fin_w.max(), bank_w=100 * W.bank_w.mean())
    mrows.append(row)
MM = pd.DataFrame(mrows).set_index("leg")
for k in [x for x in ["fin_name_share", "bank_name_share", "fin_w", "bank_w", "turnover_pct_q"] if x in MM]:
    MM["d_" + k] = MM[k] - MM.loc[CTRL, k]
print(MM.round(2).to_string()); MM.to_csv(f"{OUT}/members_decomp.csv")

# ---------- ADV / suc park ----------
print("\n=== §5.3 ADV RO + SUC PARK 20%/ngay (doc thang tu log engine moi chan) ===")
import re
adv = []
for t in LEGS:
    p = f"{OUT}/run_{t}.log"
    if not os.path.exists(p): continue
    m = re.search(r"median ADV ([\d.]+)B/day -> ~([\d.]+)B/day parkable", open(p, encoding="utf-8", errors="replace").read())
    if m: adv.append(dict(leg=t, adv_median_B=float(m.group(1)), park20_B=float(m.group(2))))
AD = pd.DataFrame(adv).set_index("leg")
if not AD.empty:
    AD["pct_vs_ctrl"] = 100 * AD.adv_median_B / AD.loc[CTRL, "adv_median_B"] - 100
    print(AD.round(2).to_string()); AD.to_csv(f"{OUT}/adv.csv")

# ---------- exposure ----------
print("\n=== §5.4a EXPOSURE tren phien NEUTRAL (state=3) — nguong |d_w_equity|>2pp ===")
dec2 = []
for t in HAVE:
    D = raw[t]; D = D[D.record_type.astype(str).str.lower().str.startswith("daily")]
    D = D[D["nav_bal_ref"].notna()].copy(); D["ymd"] = pd.to_datetime(D["ymd"])
    D = D.drop_duplicates("ymd").set_index("ymd").sort_index(); n3 = D["state"] == 3
    ws = (D["bal_stocks_ref"] / D["nav_bal_ref"])[n3]; wp = (D["bal_etf_ref"] / D["nav_bal_ref"])[n3]
    dec2.append(dict(leg=t, n_neutral=int(n3.sum()), w_stock=ws.mean() * 100,
                     w_park=wp.mean() * 100, w_equity=(ws + wp).mean() * 100))
E = pd.DataFrame(dec2).set_index("leg")
for k in ["w_stock", "w_park", "w_equity"]: E["d_" + k] = E[k] - E.loc[CTRL, k]
print(E.round(3).to_string()); E.to_csv(f"{OUT}/exposure_decomp.csv")

# ---------- per-year / per-window ----------
yr = {}
for t in HAVE:
    s = nav[t]; o = {}
    for y, g in s.groupby(s.index.year):
        pv = s[s.index < g.index[0]]; o[y] = (g.iloc[-1] / (pv.iloc[-1] if len(pv) else g.iloc[0]) - 1) * 100
    yr[t] = pd.Series(o)
Y = pd.DataFrame(yr)
for t in HAVE:
    if t != CTRL: Y["d_" + t] = Y[t] - Y[CTRL]
print("\n=== §5.4b loi suat theo nam + delta vs ctrl ==="); print(Y.round(2).to_string()); Y.to_csv(f"{OUT}/peryear.csv")

W = pd.read_csv("../bal_2025_diagnosis_20260909/p1_bull_windows.csv", parse_dates=["start", "end"])
starts = list(W["start"]) + [pd.Timestamp("2100-01-01")]
lr = lambda t: pd.Series(daily_logret(nav[t]), index=nav[t].index[1:])
rc_s = lr(CTRL); rc = daily_logret(nav[CTRL])
pw = []
for t in TREAT:
    if t not in nav: continue
    d = (lr(t) - rc_s).dropna()
    rec = {"leg": t, "total_dlogret_pp": d.sum() * 100, "pre_first_window_pp": d[d.index < starts[0]].sum() * 100}
    for i in range(len(W)):
        rec[f"W{i+1}_{W['start'].iloc[i].date()}"] = d[(d.index >= starts[i]) & (d.index < starts[i+1])].sum() * 100
    pw.append(rec)
PW = pd.DataFrame(pw).set_index("leg")
print("\n=== delta theo CUA SO regime ==="); print(PW.round(3).T.to_string()); PW.to_csv(f"{OUT}/perwindow.csv")
conc = lambda v, tot: np.nan if abs(tot) < 1e-12 else float(np.max(np.abs(v)) / abs(tot))
print("\n=== tap trung LOYO nam / cua so (chu y neu > 0.50) ===")
for t in TREAT:
    if t not in nav: continue
    ca = conc(Y["d_" + t].values, Y["d_" + t].sum())
    cb = conc(PW.loc[t].drop("total_dlogret_pp").values, PW.loc[t, "total_dlogret_pp"])
    print(f"  {t:5s} nam={ca:7.2f}  cuaso={cb:7.2f}   {'ok' if (ca <= .5 and cb <= .5) else 'TAP TRUNG'}")

# ---------- DSR / PBO / bootstrap ----------
sr_c = rc.mean() / rc.std(ddof=1)
uniq = [t for t in ["P1d", "P2d", "P1r1", "P2r1"] if t in nav]     # 4 trial phan biet (PREREG §4)
srs = [daily_logret(nav[t]).mean() / daily_logret(nav[t]).std(ddof=1) for t in uniq]
var_sr = np.var(srs, ddof=1) if len(srs) > 1 else 0.0
sr0 = expected_max_sr(var_sr, N_TRIALS) if var_sr > 0 else 0.0
print(f"\n=== DSR (null = SR ctrl {sr_c:.5f}/obs; SR0(N={N_TRIALS})={sr0:.5f}) ===")
for t in TREAT:
    if t not in nav: continue
    rb = daily_logret(nav[t]); sh, g3, g4 = moments(rb)
    print(f"  {t:5s} DSR_vs_SRctrl={dsr(sh, sr_c, g3, g4, len(rb))[0]:.6f}  "
          f"DSR_vs_SR0={dsr(sh, sr0, g3, g4, len(rb))[0]:.6f}")
M = np.column_stack([daily_logret(nav[t]) for t in HAVE])
print(f"\n=== PBO (CSCV S=16, {M.shape[1]} config toan ho) = {cscv_pbo(M, S=16)[0]:.4f} ===")

def cbb(r, L=BLOCK, Bn=4000, seed=12345):
    rng = np.random.default_rng(seed); n = len(r); nb = int(np.ceil(n / L)); o = np.empty(Bn)
    for b in range(Bn):
        st = rng.integers(0, n, nb)
        o[b] = r[np.concatenate([(np.arange(s, s + L) % n) for s in st])[:n]].sum()
    return o
yrs = (nav[CTRL].index[-1] - nav[CTRL].index[0]).days / 365.25
print(f"\n=== block bootstrap L={BLOCK} B=4000 tren chuoi delta log-return ===")
for t in TREAT:
    if t not in nav: continue
    d = (lr(t) - rc_s).dropna().values; bs = cbb(d) / yrs * 100
    lo, hi = np.percentile(bs, 2.5), np.percentile(bs, 97.5)
    print("  %-5s point=%+.3f pp/yr  CI95=[%+.3f, %+.3f]  P(d>0)=%.3f  %s"
          % (t, d.sum() / yrs * 100, lo, hi, (bs > 0).mean(),
             "loai tru 0" if (lo > 0 or hi < 0) else "om 0"))
print("\nDONE")
