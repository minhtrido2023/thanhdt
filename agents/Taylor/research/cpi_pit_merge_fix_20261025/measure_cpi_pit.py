"""Đo tác động merge_cpi pit=True (cq-2026-10-25 cpi_vn.py:269) lên CAPIT PIT CPI gate + input macro_confidence_regime.
Chạy: python3 measure_cpi_pit.py <worktree WorkingClaude dir>. So pit=False (hành vi cũ) vs pit=True trên MỌI phiên VNINDEX 2011-01..cuối CSV.
Mô phỏng ĐÚNG nhánh live golive_recommend_v23.py: end=LATEST+2M, max(interp, last NSO) khi LATEST > tháng NSO thật cuối; cổng CPI>=6.0.
dd52 = Close/rolling252 max -1 (cùng công thức L921) nhưng tính trên data/VNINDEX.csv (lịch sử đầy đủ) thay vì cửa sổ 420 ngày BQ — xấp xỉ."""
import sys, io, contextlib
W = sys.argv[1]; sys.path.insert(0, W)
import pandas as pd, cpi_vn
vni = pd.read_csv("/home/trido/thanhdt/WorkingClaude/data/VNINDEX.csv", usecols=["time", "Close"], parse_dates=["time"]).sort_values("time")
vni["dd52"] = (vni.Close / vni.Close.rolling(252, min_periods=60).max() - 1) * 100
vni = vni[vni.time >= "2011-01-01"].reset_index(drop=True)
# phiên live gần nhất (CSV dừng 2026-05): thêm 2026-10-23 để đo đúng nhánh live (dd52 NaN = không arm)
vni = pd.concat([vni, pd.DataFrame({"time": [pd.Timestamp("2026-10-23")], "Close": [float("nan")], "dd52": [float("nan")]})], ignore_index=True)
END = str((vni.time.max() + pd.DateOffset(months=2)).date())
with contextlib.redirect_stdout(io.StringIO()):
    old = cpi_vn.merge_cpi(vni[["time"]], end=END, pit=False)[["time", "cpi_yoy", "cpi_yoy_chg3"]]
    new = cpi_vn.merge_cpi(vni[["time"]], end=END, pit=True)[["time", "cpi_yoy", "cpi_yoy_chg3"]]
d = vni.merge(old, on="time").merge(new, on="time", suffixes=("_old", "_new"))
last_real_t, last_real_v = sorted(cpi_vn.NSO_CPI_YOY_REAL.items())[-1]
past = d.time > pd.to_datetime(last_real_t)
for c in ("old", "new"):
    d.loc[past, f"cpi_yoy_{c}"] = d.loc[past, f"cpi_yoy_{c}"].clip(lower=last_real_v)
    d[f"block_{c}"] = d[f"cpi_yoy_{c}"] >= 6.0
d["diff"] = d.cpi_yoy_new - d.cpi_yoy_old
gate = d.dd52 <= -20.0
flip = d.block_old != d.block_new
print(f"sessions={len(d)} {d.time.min().date()}..{d.time.max().date()}  last_real_NSO={last_real_t}={last_real_v}")
print(f"cpi_yoy changed sessions={int((d['diff'].abs()>1e-9).sum())}  |diff| mean={d['diff'].abs().mean():.3f}pp max={d['diff'].abs().max():.3f}pp")
print(f"chg3 sign-agree={(( d.cpi_yoy_chg3_old>0)==(d.cpi_yoy_chg3_new>0)).mean():.3f}")
print(f"gate(CPI>=6) flips ALL sessions={int(flip.sum())}  (old block->new allow={int((d.block_old&~d.block_new).sum())}, allow->block={int((~d.block_old&d.block_new).sum())})")
print(f"sessions with dd52<=-20 (lever arm-able)={int(gate.sum())}; flips among them={int((flip&gate).sum())}")
f = d[flip & gate]
if len(f):
    f = f.assign(m=f.time.dt.to_period("M")).groupby("m").agg(n=("time", "size"), dd52=("dd52", "min"), old=("cpi_yoy_old", "first"), new=("cpi_yoy_new", "first"))
    print(f.round(2).to_string())
t = d.iloc[-1]
print(f"LIVE-proxy last session {t.time.date()}: old={t.cpi_yoy_old:.2f} new={t.cpi_yoy_new:.2f} block_old={t.block_old} block_new={t.block_new} dd52={t.dd52:.1f}")
# months where flip happens (any dd52), for the record
fm = d[flip].assign(m=d[flip].time.dt.to_period("M")).groupby("m").size()
print("flip months (all dd52):", ", ".join(f"{k}({v})" for k, v in fm.items()))
