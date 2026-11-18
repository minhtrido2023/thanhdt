"""POST-HOC (KHÔNG tiền-đăng-ký; thêm sau khi thấy kết quả, chỉ để diễn giải): tín hiệu dự báo CHIỀU hay chỉ BIẾN ĐỘNG?
(a) lift chiều xuống: P(minex<=-X | sig) chuẩn hoá năm×tercile ADV; (b) lift run-up chuẩn hoá năm×thập phân vị ATR14%(t) (causal)."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
OUT = os.path.dirname(os.path.abspath(__file__))
P = pd.read_parquet(f"{OUT}/panel.parquet"); P = P[P.E & ~P.chase & P.OOS].copy()
C = P.Close; 
# ATR% causal xấp xỉ: lấy từ cột ret rolling std 20 (causal) để tránh dựng lại OHLC
P["vol20"] = P.groupby("ticker").ret.transform(lambda s: s.rolling(20, min_periods=10).std())
P["vdec"] = P.groupby("year").vol20.transform(lambda s: pd.qcut(s.rank(method="first"), 10, labels=False))
q = pd.read_parquet(f"{OUT}/panel.parquet", columns=["ADV20_real", "OOS", "E"]); q = q[q.E & ~q.OOS].ADV20_real.quantile([1/3, 2/3]).to_numpy()
P["terc"] = np.digitize(P.ADV20_real, q)
rows = []
for X in XS:
    c = f"y{int(X*100)}"; P["dn"] = P.minex <= -X
    bu = P.groupby(["year", "terc"])[c].transform("mean"); bd = P.groupby(["year", "terc"]).dn.transform("mean")
    bv = P.groupby(["year", "vdec"])[c].transform("mean")
    for sg in SIGS:
        m = P[sg]
        rows.append({"sig": sg, "name": NAMES[sg], "X": X, "n": int(m.sum()),
                     "L_up": P.loc[m, c].sum() / bu[m].sum(), "L_down": P.loc[m, "dn"].sum() / bd[m].sum(),
                     "L_up_volmatched": P.loc[m, c].sum() / bv[m].sum(),
                     "mean_maxex": P.loc[m, "maxex"].mean(), "mean_minex": P.loc[m, "minex"].mean(),
                     "mean_trade_ex_gross": P.loc[m, "trade_ex"].mean(), "median_trade_ex_gross": P.loc[m, "trade_ex"].median()})
R = pd.DataFrame(rows); R.to_csv(f"{OUT}/posthoc_vol.csv", index=False)
pd.set_option("display.width", 220); print(R[R.X == 0.2].round(3).to_string())
print("all OOS rows: mean trade_ex", round(P.trade_ex.mean(), 4), "median", round(P.trade_ex.median(), 4))
