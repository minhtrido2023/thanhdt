#!/usr/bin/env python3
"""Assemble the park-fraction grid table from the 12 leg logs + bootstrap logs + haircut log,
then plot Calmar / MaxDD vs x. No number is retyped by hand: everything is parsed from an artifact."""
import re, glob, os, csv
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
WC = "/home/trido/thanhdt/WorkingClaude"
TAGS = ["000","010","020","030","040","050","060","070","075","080","090","100"]
X = {t: int(t)/100 for t in TAGS}

def leg(t):
    log = open(f"{HERE}/parkgrid_{t}.log").read()
    m = re.search(r"Final NAV ([\d.]+)B\s+CAGR ([\d.]+)%\s+Sharpe\(252\) ([\d.]+)\s+MaxDD (-[\d.]+)%\s+Calmar ([\d.]+)", log)
    nav, cagr, sr, dd, cal = (float(g) for g in m.groups())
    zero = log.count("identity max err = 0 VND")
    pol = re.search(r"parking policy \(cash_etf_states\) \{3: ([\d.]+)\}", log).group(1)
    b = open(f"{HERE}/bootstrap_parkgrid_{t}.log").read()
    c5 = float(re.search(r"CAGR\s+[-\d.]+%\s+[-\d.]+%\s+([\d.]+)%", b).group(1))
    d5 = float(re.search(r"MaxDD\s+[-\d.]+%\s+[-\d.]+%\s+(-[\d.]+)%", b).group(1))
    s5 = float(re.search(r"Sharpe\s+[\d.]+\s+[\d.]+\s+([\d.]+)", b).group(1))
    return dict(x=X[t], pol=float(pol), nav=nav, cagr=cagr, sharpe=sr, maxdd=dd, calmar=cal,
                zero=zero, cagr5=c5, dd5=d5, sr5=s5)

# IS/OOS + haircut parsed from their own artifacts
hc = {}
blk = open(f"{HERE}/haircut_all.log").read().split("csv=")[1:]
for b in blk:
    t = re.search(r"parkgrid_(\d+)_univpit", b).group(1)
    hc[t] = (float(re.search(r"park share NAV mean full period = ([\d.]+)", b).group(1)),
             float(re.search(r"drag on CAGR = ([\d.]+) pp/yr", b).group(1)),
             float(re.search(r"-> ([\d.]+)%", b).group(1)))
iso = {}
for line in open(f"{HERE}/isoos.txt"):
    t, rest = line.split("|", 1)
    iso[t.strip()] = (float(re.search(r"IS ([\d.]+)%", rest).group(1)),
                      float(re.search(r"OOS ([\d.]+)%", rest).group(1)))

rows = []
for t in TAGS:
    r = leg(t); r["tag"] = t
    r["park_share"], r["drag_pp"], r["cagr_net"] = hc[t]
    r["is"], r["oos"] = iso[t]
    assert abs(r["pol"] - r["x"]) < 1e-9, f"{t}: parking policy {r['pol']} != x {r['x']}"
    assert r["zero"] == 2, f"{t}: selfcheck lines {r['zero']}"
    rows.append(r)

dd0 = [r for r in rows if r["x"] == 0][0]["dd5"]
FLOOR = dd0 - 2.0
with open(f"{HERE}/grid_summary.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) + ["dd5_ok"])
    w.writeheader()
    for r in rows:
        w.writerow({**r, "dd5_ok": int(r["dd5"] >= FLOOR)})

print(f"bootstrap 5th-pct MaxDD at park=0 = {dd0}%  =>  PREREG constraint floor = {FLOOR}%")
print(f"{'x':>5} {'CAGR':>7} {'Sharpe':>7} {'MaxDD':>7} {'Calmar':>7} {'NAV_B':>8} {'IS':>6} {'OOS':>6} "
      f"{'C5th':>6} {'DD5th':>7} {'SR5th':>6} {'park%NAV':>9} {'drag':>6} {'CAGRnet':>8} {'ok':>3}")
for r in rows:
    print(f"{r['x']:5.2f} {r['cagr']:7.2f} {r['sharpe']:7.2f} {r['maxdd']:7.1f} {r['calmar']:7.3f} "
          f"{r['nav']:8.2f} {r['is']:6.2f} {r['oos']:6.2f} {r['cagr5']:6.1f} {r['dd5']:7.1f} {r['sr5']:6.2f} "
          f"{r['park_share']*100:9.2f} {r['drag_pp']:6.3f} {r['cagr_net']:8.3f} {'OK' if r['dd5']>=FLOOR else 'FAIL':>3}")

print("\nMarginal 'CAGR bought per 1pp of extra MaxDD' between adjacent grid levels:")
for a, b in zip(rows, rows[1:]):
    dc, dd = b["cagr"] - a["cagr"], abs(b["maxdd"]) - abs(a["maxdd"])
    if dd <= 0 and dc > 0: v = "FREE (CAGR up AND DD better/equal)"
    elif dd <= 0 and dc <= 0: v = "dominated (CAGR down, DD not better)" if dc < 0 else "flat"
    elif dc <= 0: v = "STRICTLY WORSE (CAGR down, DD worse)"
    else: v = f"{dc/dd:.2f} pp CAGR per 1pp DD"
    print(f"  {a['x']:.2f} -> {b['x']:.2f}:  dCAGR {dc:+.2f}pp  d|MaxDD| {dd:+.2f}pp   {v}")

cand = [r for r in rows if r["dd5"] >= FLOOR]
best = max(cand, key=lambda r: r["calmar"])
band = [r["x"] for r in rows if abs(r["calmar"] - best["calmar"]) <= 0.03]
print(f"\ncandidates passing the DD constraint: {[r['x'] for r in cand]}")
print(f"Calmar-max candidate: x={best['x']:.2f} (Calmar {best['calmar']:.3f})")
print(f"levels indistinguishable from it at the declared 0.03-Calmar resolution: {band}")

fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
xs = [r["x"] for r in rows]
ax[0].plot(xs, [r["calmar"] for r in rows], "o-", color="#1f6feb", label="Calmar (actual)")
ax[0].axvline(best["x"], color="#d1242f", ls="--", lw=1, label=f"Calmar max @ {best['x']:.0%}")
ax[0].axvline(0.8, color="#8250df", ls=":", lw=1.4, label="LIVE 80%")
ax[0].set_xlabel("park fraction of idle cash (NEUTRAL)"); ax[0].set_ylabel("Calmar")
ax[0].set_title("Calmar vs park fraction — interior peak at 30%"); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3)
ax[1].plot(xs, [r["maxdd"] for r in rows], "o-", color="#1f6feb", label="MaxDD actual")
ax[1].plot(xs, [r["dd5"] for r in rows], "s--", color="#bc4c00", label="MaxDD bootstrap 5th-pct")
ax[1].axhline(FLOOR, color="#d1242f", ls="--", lw=1, label=f"PREREG constraint floor {FLOOR:.1f}%")
ax[1].set_xlabel("park fraction of idle cash (NEUTRAL)"); ax[1].set_ylabel("MaxDD %")
ax[1].set_title("Drawdown vs park fraction"); ax[1].legend(fontsize=8); ax[1].grid(alpha=.3)
fig.tight_layout(); fig.savefig(f"{HERE}/park_grid_curves.png", dpi=130)
print(f"\nwrote grid_summary.csv + park_grid_curves.png")
