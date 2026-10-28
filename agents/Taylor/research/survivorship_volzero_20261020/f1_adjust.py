"""PREREG_F1 §1: lô kẹt cuối kỳ hạch toán hậu kỳ (a) giá 0, (b) chiết khấu H; số lô ép bán theo book. + Δ so V1D."""
import re, sys, pandas as pd
PIN = {"p30_pin0": "raw/pin_4707bcbe.csv", "p30_pin1M": "raw/pin_bcd0469f.csv", "p0_pin0": "raw/pin_537e349b.csv", "p0_pin1M": "raw/pin_a6ba34d8.csv"}
def cg(x):
    return (x.iloc[-1] / x.iloc[0]) ** (365.25 / (x.index[-1] - x.index[0]).days) - 1
def daily(csv):
    df = pd.read_csv(csv, low_memory=False)
    d = df[df.record_type == "DAILY"].copy(); d["ymd"] = pd.to_datetime(d.ymd); return d.set_index("ymd")
base = {leg: cg(daily(p).combined_nav.astype(float)) for leg, p in PIN.items()}
rows = []
for var in sys.argv[1:]:
    H = float(re.search(r"H(\d+)", var).group(1)) / 100
    for leg in PIN:
        log = open(f"logs/vz_{var}_{leg}.log").read()
        csv = re.findall(r"/home/trido/thanhdt/WorkingClaude/data/v23_golive\S*\.csv", log)[-1]
        d = daily(csv); s = d.combined_nav.astype(float)
        r = dict(var=var, leg=leg, cagr=cg(s) * 100)
        loss = {}
        for bk in ("BAL", "LAG"):
            m = re.findall(rf"\[F1\] v23audit_{bk}: forced_lots=(\d+) by=(\{{.*?\}}) stuck_end n=(\d+) value_vnd=([\d.]+) book_nav_last=([\d.]+)", log)[-1]
            r[f"forced_{bk}"] = int(m[0]); r[f"forced_by_{bk}"] = m[1]; r[f"stuck_n_{bk}"] = int(m[2]); r[f"stuck_bn_ref_{bk}"] = float(m[3]) / 1e9
            loss[bk] = float(d[f"cap_{bk.lower()}"].iloc[-1]) * float(m[3]) / float(m[4])
        for lab, w in (("a0", 1.0), ("bH", H)):
            s2 = s.copy(); s2.iloc[-1] -= w * (loss["BAL"] + loss["LAG"])
            r[f"cagr_adj_{lab}"] = cg(s2) * 100; r[f"d_cagr_adj_{lab}_vs_pin"] = (cg(s2) - base[leg]) * 100
            r[f"d_oos_adj_{lab}_note"] = (cg(s2["2019-12-31":]) - cg(s["2019-12-31":])) * 100
        rows.append(r)
out = pd.DataFrame(rows); pd.set_option("display.width", 250)
print(out.round(3).to_string(index=False)); out.to_csv(f"out_f1_adjust_{'_'.join(sys.argv[1:])}.csv", index=False)
