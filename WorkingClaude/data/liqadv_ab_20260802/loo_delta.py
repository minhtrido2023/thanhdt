"""Per-year leave-one-out tren DELTA giua 2 chan A/B — job Taylor_20260802_163657.

Bai hoc MOM/Wave1 (KNOWLEDGE §8): mot edge ma 1-2 nam ganh het = reshuffle-luck, khong phai
signal ben. Kiem: bo LAN LUOT tung nam khoi CA HAI chan, tinh lai CAGR, xem delta co con
DUONG o moi phep khong.

CAGR sau khi bo 1 nam = chain-link cac he so tang truong NAM CON LAI roi annualize theo tong
so nam con lai (khong the dung ngay dau/cuoi vi chuoi bi thung o giua).

Dung: loo_delta.py <csv_ctrl> <csv_treat> [nhan]
"""
import sys
import pandas as pd


def yearly_factors(path):
    df = pd.read_csv(path, low_memory=False)
    d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
    d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce")
    d = d.dropna(subset=["ymd"]).sort_values("ymd")
    nav = d.groupby("ymd")["combined_nav"].last().astype(float)
    out = {}
    for y in range(int(nav.index[0].year), int(nav.index[-1].year) + 1):
        ny = nav[nav.index.year == y]
        if len(ny) < 5:
            continue
        # so nam thuc te cua doan (nam cut 2026 khong duoc tinh tron 1.0)
        span = (ny.index[-1] - ny.index[0]).days / 365.25
        out[y] = (float(ny.iloc[-1] / ny.iloc[0]), span)
    return out


def cagr_excluding(fac, drop):
    growth, yrs = 1.0, 0.0
    for y, (g, span) in fac.items():
        if y == drop:
            continue
        growth *= g
        yrs += span
    return (growth ** (1 / yrs) - 1) * 100


ctrl, treat = yearly_factors(sys.argv[1]), yearly_factors(sys.argv[2])
label = sys.argv[3] if len(sys.argv) > 3 else "delta"
assert set(ctrl) == set(treat), f"nam lech nhau: {set(ctrl) ^ set(treat)}"

full_c, full_t = cagr_excluding(ctrl, None), cagr_excluding(treat, None)
print(f"  {label}: FULL(chain) ctrl {full_c:.2f}%  treat {full_t:.2f}%  delta {full_t-full_c:+.2f}pp")
print("  --- leave-one-year-out ---")
deltas = []
for y in sorted(ctrl):
    c, t = cagr_excluding(ctrl, y), cagr_excluding(treat, y)
    deltas.append(t - c)
    print(f"    bo {y}: ctrl {c:6.2f}%  treat {t:6.2f}%  delta {t-c:+.2f}pp")
pos = sum(1 for d in deltas if d > 0)
print(f"  ==> delta DUONG {pos}/{len(deltas)} phep; bien do [{min(deltas):+.2f} ; {max(deltas):+.2f}] pp")
