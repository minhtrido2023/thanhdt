"""Chan doan 2011-file: (1) cua so vs troi du lieu; (2) do bias BO CHO CO TUC o chan co phieu.
Paper-only, khong sua file goc."""
import sys, os, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0,"/home/trido/thanhdt/WorkingClaude")
import numpy as np, pandas as pd
import backtest_recovery_alloc_2011 as M
d = M.load()

VARIANTS = {
 "BASELINE":            dict(),
 "recovery deep":       dict(recovery={1:0.70,2:0.70}, thr=-0.3),
 "DEPTH lev-free0.95":  dict(depth=(-0.3,-0.5,0.95)),
 "DEPTH margin1.5":     dict(depth=(-0.3,-0.7,1.5)),
 "+DEPgate m1.5":       dict(depth=(-0.3,-0.7,1.5), dep_gate=(0.06,0.12)),
 "+DEPgate lev-free.95":dict(depth=(-0.3,-0.5,0.95), dep_gate=(0.06,0.12)),
}
def table(dd, tag, dy=None):
    print(f"\n--- {tag} (n={len(dd)}, {dd.index[0].date()}..{dd.index[-1].date()}) ---")
    print(f"{'variant':22}{'CAGR':>7}{'Sh':>6}{'MaxDD':>8}{'11-13':>7}{'20-26':>7}")
    for nm,kw in VARIANTS.items():
        out = M.run(dd, **kw)
        if dy is not None:                      # cong lai co tuc rong thue cho chan co phieu
            r_add = out["w"].values * dy.reindex(out.index).values
            nav = np.cumprod((1+out["nav"].pct_change().fillna(0).values)*(1+r_add))
            out = out.copy(); out["nav"] = nav/nav[0]*1.0
        c,sh,mdd,cal = M.metrics(out)
        print(f"{nm:22}{c*100:>6.1f}%{sh:>6.2f}{mdd*100:>7.1f}%{M.seg(out,2011,2013)*100:>6.1f}%{M.seg(out,2020,2026)*100:>6.1f}%")

table(d[d.index<="2026-06-19"], "END=2026-06-19 (cua so gan nhu ban pin)")
table(d, "END=2026-09-25 (hom nay)")

# --- chuoi DY thi truong (liq-weighted) theo nam, rong thue 5%, quy ve NGAY ---
dyy = pd.read_csv(f"{os.path.dirname(os.path.abspath(__file__))}/market_dy_by_year.csv")
m = dict(zip(dyy.y.astype(int), dyy.dy_liqw/100.0))
dy_d = pd.Series([ (m.get(t.year, np.nan))*0.95/252.0 for t in d.index], index=d.index).ffill().bfill()
print(f"\n[DY thi truong liq-weighted, rong thue 5%] trung binh {dy_d.mean()*252*100:.2f}%/nam; "
      f"2011-13 {dy_d[dy_d.index.year<=2013].mean()*252*100:.2f}%/nam")
table(d, "END=2026-09-25 + CONG CO TUC vao chan co phieu", dy=dy_d)
