#!/usr/bin/env python3
"""W1 muc 4 — do lai break-even carry cua Job U THEO THANG (tang 1 / tang 2 cua
`idle_rate_proxy.py`) thay cho 8.55% PHANG, tren dung khuon paired bootstrap da dung de
ha park 0.80 -> 0.30 (L=21, B=4000, seed=12345 — `park_fraction_grid_20260927/paired_v2.py`).

Chi doi MOT bien so voi `idle_pool_redeploy_20260927/carry_paired.py`: lai suat tien nhan roi
tu HANG SO -> VECTO theo ngay (point-in-time qua `r_idle`). Moi thu khac giu nguyen: 12 leg
pin, credit carry len max(bal_cash_ref+lag_cash_ref, 0) theo so ngay duong lich (cash am =
no margin, engine da tinh 10%/nam), cung metric, cung seed.

PAPER-ONLY. Khong wire, khong sinh lai CSV, khong doi config.
"""
import glob, json, sys
import numpy as np, pandas as pd

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from idle_rate_proxy import r_idle_series, HAIRCUT_PP, SPOT_RATE_PCT  # noqa: E402

DATA = "/home/trido/thanhdt/WorkingClaude/data"
TAGS = ["000", "030", "080"]
XS = {t: int(t) / 100 for t in TAGS}
L, B, SEED = 21, 4000, 12345


def load(tag):
    hits = sorted(glob.glob(f"{DATA}/*_parkgrid_{tag}_univpit.csv"))
    assert len(hits) == 1, (tag, hits)
    df = pd.read_csv(hits[0], low_memory=False).dropna(subset=["combined_nav"])
    t = pd.to_datetime(df["ymd"], errors="coerce")
    df = df[t.notna()].copy(); t = t[t.notna()]
    g = df.groupby(t.dt.normalize()).last()
    return (g["combined_nav"].astype(float),
            g[["bal_cash_ref", "lag_cash_ref"]].fillna(0).sum(axis=1).astype(float))


NAV, CASH = {}, {}
for t in TAGS:
    NAV[t], CASH[t] = load(t)
idx = NAV["000"].index
for t in TAGS:
    assert NAV[t].index.equals(idx), t
YRS = (idx[-1] - idx[0]).days / 365.25
N = len(idx) - 1
ANN = N / YRS
DTS = np.array([(idx[i + 1] - idx[i]).days for i in range(N)], dtype=float)

# --- vecto lai suat point-in-time, danh gia tai ngay DAU moi doan (khong nhin truoc).
# Ngay TRUOC khi mot tang co du lieu (floor: lien NH bat dau 2014-01 => dung duoc tu
# 2014-02-01) duoc credit 0%, KHONG forward-fill nguoc va KHONG cat bo duong NAV pin.
# Lua chon nay BAO THU (giam carry) va giu so sanh voi baseline 0% nguyen ven.
RATES = {}
GAP = {}
for tier in ("baseline", "floor"):
    v = np.zeros(N); miss = 0
    for k, d in enumerate(idx[:-1]):
        try:
            v[k] = r_idle_series([d], tier=tier)[0] / 100.0
        except ValueError:
            miss += 1
    RATES[tier] = v; GAP[tier] = miss
    print(f"  tier {tier}: {miss} ngay dau chuoi khong co moc PIT -> credit 0% ({miss/N*100:.2f}% so ngay)")
RATES["flat_8.543"] = np.full(N, SPOT_RATE_PCT / 100.0)
RATES["zero"] = np.zeros(N)

print(f"3 leg aligned, {len(idx)} days {idx[0].date()}->{idx[-1].date()}, {YRS:.3f} yrs, obs/yr={ANN:.1f}")
print(f"HAIRCUT_PP={HAIRCUT_PP}")
for k, v in RATES.items():
    if k == "zero":
        continue
    # trung binh gia quyen theo so ngay lich
    wavg = float((v * DTS).sum() / DTS.sum()) * 100
    print(f"  tier {k:12s}: mean(day-weighted) {wavg:6.3f}%/yr  min {v.min()*100:6.3f}  max {v.max()*100:6.3f}")


def carry_ret(tag, rate_vec, scale=1.0):
    nav, cash = NAV[tag], CASH[tag]
    return (np.maximum(cash.values[:-1], 0.0) / nav.values[:-1]) * rate_vec * scale * DTS / 365.0


def logret(tag, rate_vec, scale=1.0):
    return np.diff(np.log(NAV[tag].values)) + np.log1p(carry_ret(tag, rate_vec, scale))


def metrics(r):
    nav = np.exp(np.cumsum(r, axis=0)); peak = np.maximum.accumulate(nav, axis=0)
    yrs = r.shape[0] / ANN
    cagr = nav[-1] ** (1 / yrs) - 1
    dd = (nav / peak - 1).min(axis=0)
    return cagr, r.mean(axis=0) / r.std(axis=0) * np.sqrt(ANN), dd, cagr / np.abs(dd)


def boot(R):
    rng = np.random.default_rng(SEED); nblk = int(np.ceil(N / L)); off = np.arange(L)
    k = R.shape[1]
    C = np.empty((B, k)); D = np.empty((B, k)); K = np.empty((B, k))
    for b in range(B):
        st = rng.integers(0, N, nblk)
        ix = ((st[:, None] + off[None, :]) % N).ravel()[:N]
        c, s, d, kk = metrics(R[ix]); C[b], D[b], K[b] = c, d, kk
    return C, D, K


def cagr_flat(tag, rate_vec, scale=1.0):
    r = logret(tag, rate_vec, scale)
    return np.exp(r.sum()) ** (1 / YRS) - 1


out = {"haircut_pp": HAIRCUT_PP, "N": int(N), "yrs": round(YRS, 4), "tiers": {}}
for tier, vec in RATES.items():
    R = np.column_stack([logret(t, vec) for t in TAGS])
    ACT = metrics(R); C, D, K = boot(R)
    D5 = np.percentile(D, 5, axis=0); EK = K.mean(axis=0); EC = C.mean(axis=0)
    i30, i80, i00 = TAGS.index("030"), TAGS.index("080"), TAGS.index("000")
    p_30_80 = float((K[:, i30] > K[:, i80]).mean())
    p_30_80_cagr = float((C[:, i30] > C[:, i80]).mean())
    p_00_30 = float((K[:, i00] > K[:, i30]).mean())
    floor = D5[i00] - 0.02
    print(f"\n=== tier {tier} ===  (DD gate floor = DD5th@park0 - 2.0pp = {floor*100:.2f}%)")
    print(f"{'park':>5} {'CAGRact':>8} {'E[CAGR]':>8} {'E[Calmar]':>10} {'DD5th':>8} {'gate':>6}")
    for j, t in enumerate(TAGS):
        print(f"{XS[t]:5.2f} {ACT[0][j]*100:7.2f}% {EC[j]*100:7.2f}% {EK[j]:10.3f} "
              f"{D5[j]*100:7.2f}% {'OK' if D5[j] >= floor else 'FAIL':>6}")
    print(f"  P(Calmar 0.30 > 0.80) = {p_30_80:.4f}   P(CAGR 0.30 > 0.80) = {p_30_80_cagr:.4f}"
          f"   P(Calmar 0.00 > 0.30) = {p_00_30:.4f}")
    # scale lambda de tang nay dat break-even CAGR(0.30)==CAGR(0.80)
    lam = None
    if tier != "zero":
        xs = np.arange(0.0, 6.0001, 0.005)
        d = np.array([cagr_flat("030", vec, s) - cagr_flat("080", vec, s) for s in xs])
        sign = np.where(np.diff(np.sign(d)) != 0)[0]
        lam = float(xs[sign[0] + 1]) if len(sign) else None
        wavg = float((vec * DTS).sum() / DTS.sum()) * 100
        if lam:
            print(f"  break-even: phai NHAN CA DUONG CONG nay x{lam:.3f} "
                  f"(<=> mean {wavg*lam:.3f}%/yr) de CAGR(0.30)==CAGR(0.80); hien x1 => "
                  f"{(cagr_flat('030',vec)-cagr_flat('080',vec))*100:+.3f}pp")
        else:
            print(f"  break-even: KHONG dat duoc trong x[0,6] (mean {wavg:.3f}%/yr); "
                  f"x1 => {(cagr_flat('030',vec)-cagr_flat('080',vec))*100:+.3f}pp")
    out["tiers"][tier] = {
        "mean_day_weighted_pct": round(float((vec * DTS).sum() / DTS.sum()) * 100, 4),
        "park": [XS[t] for t in TAGS],
        "cagr_act_pct": [round(float(v) * 100, 3) for v in ACT[0]],
        "E_cagr_pct": [round(float(v) * 100, 3) for v in EC],
        "E_calmar": [round(float(v), 4) for v in EK],
        "dd5_pct": [round(float(v) * 100, 2) for v in D5],
        "dd_gate_floor_pct": round(float(floor) * 100, 2),
        "gate_pass": [XS[t] for j, t in enumerate(TAGS) if D5[j] >= floor],
        "P_calmar_030_gt_080": p_30_80,
        "P_cagr_030_gt_080": p_30_80_cagr,
        "P_calmar_000_gt_030": p_00_30,
        "breakeven_scale_lambda": lam,
    }

json.dump(out, open("carry_paired_tiered_results.json", "w"), indent=1)
print("\nwrote carry_paired_tiered_results.json")
