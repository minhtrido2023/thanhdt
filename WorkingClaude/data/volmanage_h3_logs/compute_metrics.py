"""Wave1/H3 metrics — FULL + IS(2014-2019)/OOS(2020+) from combined_nav column.
Formulas identical to pt_v23_audit_2014.py metric_formulas (registry-audited):
  CAGR=(end/0)^(365.25/cal_days)-1 ; Sharpe=mean/std*sqrt(252) ;
  Sortino=mean/sqrt(mean(neg^2))*sqrt(252) ; MaxDD=min(NAV/cummax-1) ; Calmar=CAGR/|MaxDD|.
All on DAILY combined_nav. IS/OOS sliced by date on the same series.
"""
import sys, pandas as pd, numpy as np

def block(nav):  # nav = pd.Series indexed by date
    nav = nav.dropna()
    ret = nav.pct_change().dropna()
    cal = (nav.index[-1] - nav.index[0]).days
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (365.25 / cal) - 1
    sharpe = ret.mean() / ret.std() * np.sqrt(252)
    neg = ret[ret < 0]
    sortino = ret.mean() / np.sqrt((neg ** 2).mean()) * np.sqrt(252)
    dd = (nav / nav.cummax() - 1).min()
    calmar = cagr / abs(dd)
    return dict(cagr=cagr * 100, sharpe=sharpe, sortino=sortino, maxdd=dd * 100,
                calmar=calmar, endB=nav.iloc[-1] / 1e9, n=len(nav))

def run(path, label):
    df = pd.read_csv(path)
    df["ymd"] = pd.to_datetime(df["ymd"], errors="coerce")   # metadata rows at tail -> NaT
    df["combined_nav"] = pd.to_numeric(df["combined_nav"], errors="coerce")
    df = df.dropna(subset=["ymd", "combined_nav"])
    s = df.set_index("ymd")["combined_nav"].sort_index()
    full = block(s)
    is_ = block(s[s.index <= "2019-12-31"])
    oos = block(s[s.index >= "2020-01-01"])
    print(f"\n=== {label}  ({path.split('/')[-1]}) ===")
    for tag, m in [("FULL", full), ("IS 14-19", is_), ("OOS 20+", oos)]:
        print(f"  {tag:9s} CAGR {m['cagr']:6.2f}%  Sh {m['sharpe']:.2f}  Sort {m['sortino']:.2f}  "
              f"MaxDD {m['maxdd']:6.1f}%  Cal {m['calmar']:.2f}  end {m['endB']:.3f}B  n={m['n']}")
    return dict(label=label, full=full, is_=is_, oos=oos)

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        label, path = arg.split("=", 1)
        run(path, label)
