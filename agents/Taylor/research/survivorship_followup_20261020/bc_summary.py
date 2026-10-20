"""Tổng hợp B/C theo PREREG_BC: kiểm tái lập vs replay gốc, rồi bảng dải 4 chân + nhãn."""
import pandas as pd, numpy as np, json
f = pd.read_csv("out_followup_results.csv")
o = pd.read_csv("../survivorship_replay_20261020/out_replay_results.csv")
o = o[(o.scen == "Z") & (o.xmode == "liq") & (o.set == "M")]
b = f[(f.w == "orig") & (f.set == "M") & (f.cap == 0.20) & (f.exitval == "ptin")]
m = b.merge(o, on=["leg", "var", "cfg"], suffixes=("", "_o"))
err = {c: float((m[c] - m[c + "_o"]).abs().max()) for c in ["d_cagr_pp", "d_sharpe", "d_maxdd_pp"]}
ntr = int((m.n_trades != m.n_trades_o).sum())
print("REPRO rows", len(m), "of", len(o), "maxerr", err, "n_trades mismatch", ntr)
if len(m) != len(o) or max(err.values()) > 1e-12 or ntr:
    raise SystemExit("TÁI LẬP TRƯỢT — dừng")
FL = 0.46
def lab(lo, hi):
    if hi <= -FL: return "vượt sàn chiều THIỆT"
    if lo >= FL: return "vượt sàn chiều LỢI"
    if lo > -FL and hi < FL: return "dưới sàn"
    return "dải cắt sàn"
rows = []
for k, g in f.groupby(["w", "set", "cap", "scope", "exitval", "var", "cfg"]):
    lo, hi = g.d_cagr_pp.min(), g.d_cagr_pp.max()
    rows.append(dict(zip(["w", "set", "cap", "scope", "exitval", "var", "cfg"], k), lo=lo, hi=hi, label=lab(lo, hi),
                     n_trades=f"{g.n_trades.min()}-{g.n_trades.max()}", stuck=f"{g.n_stuck.min()}-{g.n_stuck.max()}",
                     dmaxdd=f"{g.d_maxdd_pp.min():+.2f}..{g.d_maxdd_pp.max():+.2f}"))
t = pd.DataFrame(rows); t.to_csv("out_followup_table.csv", index=False)
def show(w, sel):
    q = t[(t.w == w) & (t.cfg == "MIX")]
    for (s, c, sc, ev) in sel:
        r = q[(q.set == s) & (q.cap == c) & ((q.scope == sc) | (c == 0.20)) & (q.exitval == ev)]
        r = r.drop_duplicates(["var"])
        print(f"  {s:10s} cap{int(c*100):>2d}% {sc:5s} exit={ev:4s} | " + " | ".join(
            f"{v}: {x.lo:+.2f}..{x.hi:+.2f} [{x.label}] st{x.stuck}" for v in ["UB", "MID", "LIVE", "UB_ALLOC", "MID_ALLOC", "LIVE_ALLOC"]
            for x in r[r['var'] == v].itertuples()))
SEL = [("M", .20, "phase", "ptin"), ("M-TGG-GAB", .20, "phase", "ptin"), ("M", .10, "phase", "ptin"), ("M", .05, "phase", "ptin"),
       ("M-TGG-GAB", .10, "phase", "ptin"), ("M-TGG-GAB", .05, "phase", "ptin"), ("M", .05, "all", "ptin"), ("M-TGG-GAB", .05, "all", "ptin"),
       ("M-GAB", .20, "phase", "ptin"), ("M", .20, "phase", "nm"), ("M", .05, "phase", "nm"), ("M-GAB", .05, "phase", "nm")]
for w in ["fixA", "orig"]:
    print(f"== w={w} MIX (dải 4 chân, pp) ==")
    show(w, SEL)
