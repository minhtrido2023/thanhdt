"""backfill13 v2 (vòng 2 arch-review, job Taylor_20261110_103537) — thay backfill13/ (SUPERSEDED: lớp lỗi
stale-CUM/ hệ số của raw_basis cũ, 83/11.717 dòng). Backfill 13 phiên thưa 2026-06..09 vào BẢN SAO 2 pkl
(KHÔNG ghi đè data/*.pkl) bằng lagged_cache_patch.raw_basis MỚI (ticker_1m ưu tiên + detector registry
ticker_price_stale_on_exdate.md) và merge_window fail-safe. Nguồn: data/bq_*.csv (pull 2026-11-10, md5 trong MD5.txt).
Ra: earnings_px_bf13v2.pkl, lagged_pos_ov_bf13v2.pkl, MD5.txt, recon.txt (đối soát từng dòng mới với BQ Price).
--apply (CHỈ SAU arch-review + user duyệt): backup .pre_bf13v2 rồi os.replace vào data/; từ chối nếu canonical đổi md5.
Interpreter: $DNA_PYEXE."""
import sys, os, pickle, hashlib, shutil
import pandas as pd, numpy as np
WC = "/home/trido/thanhdt/WorkingClaude"; O = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("LAGCACHE_CODE", "/home/trido/thanhdt/wt-lagcache-1110/WorkingClaude"))
from lagged_cache_patch import raw_basis, merge_window, with_refs
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
PX, OV = f"{WC}/data/earnings_px.pkl", f"{WC}/data/lagged_pos_ov.pkl"
if "--apply" in sys.argv:
    m = {l.split()[0]: l.split()[1] for l in open(f"{O}/MD5.txt")}
    assert md5(PX) == m["canonical_earnings_px"] and md5(OV) == m["canonical_lagged_pos_ov"], "canonical đã đổi từ lúc build — build lại"
    for src, dst in [(f"{O}/earnings_px_bf13v2.pkl", PX), (f"{O}/lagged_pos_ov_bf13v2.pkl", OV)]:
        assert md5(src) == m[os.path.basename(src).replace(".pkl", "")], f"{src} đổi md5 từ lúc build"
        shutil.copy2(dst, dst + ".pre_bf13v2"); shutil.copy2(src, dst + ".tmp"); os.replace(dst + ".tmp", dst); print("applied", dst)
    sys.exit(0)

px = pickle.load(open(PX, "rb")); px["time"] = pd.to_datetime(px["time"])
ov = pickle.load(open(OV, "rb")); ov["time"] = pd.to_datetime(ov["time"])
bq = pd.read_csv(f"{O}/data/bq_ticker_20260525_now.csv", parse_dates=["time"])
t1m = pd.read_csv(f"{O}/data/bq_ticker_1m_20260525_now.csv", parse_dates=["time"])
ca = pd.read_csv(f"{O}/data/bq_corporate_action_20260518_now.csv", parse_dates=["exright_date"])
cnt = px.groupby("time").ticker.nunique()
gap = sorted(d for d in cnt.index if d >= pd.Timestamp("2026-06-01") and cnt[d] < 50 and d.weekday() < 5)
gap = [d for d in gap if d in set(bq.time.unique())]
print("gap:", [str(d.date()) for d in gap]); assert len(gap) == 13
S = pd.Timestamp("2026-06-01")
a = raw_basis(bq, S, t1m=t1m, ca=ca)
ag = a[a.time.isin(gap)]
R = ["ticker", "time", "src", "ref_adj", "ref_prev"]
newpx = with_refs(ag, "Close_raw", "Close")[R].assign(Close=ag.Close_raw)
newov = with_refs(ag, "Open_raw", "Open")[R].assign(Open=ag.Open_raw, Volume_3M_P50=ag.Volume_3M_P50)
# Fail-safe mặc định (tol 2%) chạy TRƯỚC để lấy danh sách dòng cũ sẽ bị giữ, rồi ghép thật với tol=inf CHỈ
# trên 13 phiên thưa: dòng cũ ở các phiên này là ảnh chụp lúc BQ chưa chốt phiên (fetch thưa = chính lỗi
# đang vá) — bằng chứng in ở recon.txt (dòng cũ nằm TRONG biên [Low,High] của phiên = giá giữa phiên;
# các phiên KHÔNG thưa cùng kỳ: số dòng pkl lệch BQ Price >2% in kèm để so).
_, hpx, cpx = merge_window(px, newpx, S, "Close")
_, hov, cov = merge_window(ov, newov, S, "Open")
pxB, _, _ = merge_window(px, newpx, S, "Close", tol=np.inf)
ovB, _, _ = merge_window(ov, newov, S, "Open", tol=np.inf)
for df in (pxB, ovB): df["time"] = df["time"].astype("datetime64[ns]")
pickle.dump(pxB, open(f"{O}/earnings_px_bf13v2.pkl", "wb")); pickle.dump(ovB, open(f"{O}/lagged_pos_ov_bf13v2.pkl", "wb"))

L = []
p = lambda *x: (print(*x), L.append(" ".join(str(i) for i in x)))
untouched = lambda o, n: o[~o.time.isin(gap)].reset_index(drop=True).equals(n[~n.time.isin(gap)].sort_values(["ticker", "time"]).reset_index(drop=True))
p("rows px", len(px), "->", len(pxB), "| ov", len(ov), "->", len(ovB), "| non-gap rows unchanged: px", untouched(px, pxB), "ov", untouched(ov, ovB))
c = pxB.groupby("time").ticker.nunique(); c = c["2026-06-01":]; p("min tickers/day weekdays since 06-01:", int(c[c.index.weekday < 5].min()))
p("src (dòng gap):", ag.src.value_counts().to_dict())
p("fail-safe mặc định (tol 2%) — px: held", len(hpx), "corrected", len(cpx), "| ov: held", len(hov), "corrected", len(cov),
  "⇒ bản dựng ghi đè các dòng held trên phiên thưa (tol=inf), bằng chứng dưới")
hl = pd.read_csv(f"{O}/data/bq_ticker_hilo_20260525_now.csv", parse_dates=["time"])
e = hpx.merge(hl, on=["ticker", "time"]).merge(bq[["ticker", "time", "Price", "Close"]], on=["ticker", "time"])
e["r"] = e.Price / e.Close; e["lo_raw"] = e.Low * e.r; e["hi_raw"] = e.High * e.r
e["old_in_day_range"] = (e.old >= e.lo_raw * 0.999) & (e.old <= e.hi_raw * 1.001)
p("dòng held: dòng cũ nằm trong biên [Low,High]×r của phiên (= giá giữa phiên):", int(e.old_in_day_range.sum()), "/", len(e))
nong = px[(px.time >= S) & (px.time <= "2026-10-27") & ~px.time.isin(gap)].merge(bq[["ticker", "time", "Price"]], on=["ticker", "time"])
nd = (nong.Close / nong.Price - 1).abs()
p("đối chứng phiên KHÔNG thưa 01/06–27/10: pkl vs BQ Price —", len(nong), "dòng; lệch >2%:", int((nd > 0.02).sum()), "; >0,1%:", int((nd > 0.001).sum()))
og = px[px.time.isin(gap)].merge(bq[["ticker", "time", "Price"]], on=["ticker", "time"])
gd = (og.Close / og.Price - 1).abs()
p("phiên thưa: dòng cũ pkl vs BQ Price —", len(og), "dòng; lệch >2%:", int((gd > 0.02).sum()), "; >0,1%:", int((gd > 0.001).sum()))
# rủi ro tồn dư: phiên liền trước GDKHQ bị ghi giá đã điều chỉnh (r≈1 trong khi r_prev>1,02) ngoài phủ ticker_1m
pre = a.merge(ca.assign(time=ca.exright_date - pd.Timedelta(0)).rename(columns={"time": "ex"})[["ticker", "ex"]], on="ticker")
pre = pre[(pre.r_prev > 1.02) & ((pre.r - 1).abs() < 0.005) & (pre.src == "price")]
nxt = a.groupby("ticker").time.shift(-1); a2 = a.assign(t_next=nxt)
pre = a2.merge(ca.rename(columns={"exright_date": "t_next"}), on=["ticker", "t_next"])
pre = pre[(pre.r_prev > 1.02) & ((pre.r - 1).abs() < 0.005) & (pre.src == "price")]
p("rủi ro tồn dư (KHÔNG tự sửa — mơ hồ với GDKHQ lệch 1 phiên): phiên liền trước GDKHQ có r≈1 trong khi r_prev>1,02, src=price:",
  len(pre), "dòng toàn cửa sổ;", int(pre.time.isin(gap).sum()), "trên 13 phiên thưa")
if len(pre): p(pre[["ticker", "time", "Price", "Close", "r_prev", "r", "t_next"]].to_string(index=False))
for nm, t in (("px held", hpx), ("px corrected", cpx), ("ov held", hov), ("ov corrected", cov)):
    if len(t): p(nm + ":\n" + t.to_string(index=False))
# đối soát từng dòng gap mới với BQ Price (giá thô ticker) — lệch >0,1% phải là exfix có bằng chứng
j = pxB[pxB.time.isin(gap)].merge(bq[["ticker", "time", "Price", "Close"]], on=["ticker", "time"], how="left").merge(
    ag[["ticker", "time", "src"]], on=["ticker", "time"], how="left")
j["dev"] = (j.Close_x / j.Price - 1).abs()
dv = j[j.dev > 0.001]
p("đối soát gap px vs BQ Price:", len(j), "dòng; lệch >0,1%:", len(dv), "; theo src:", dv.src.value_counts(dropna=False).to_dict())
if len(dv): p(dv[["ticker", "time", "Close_x", "Price", "Close_y", "src"]].rename(columns={"Close_x": "pkl_raw", "Close_y": "bq_adj"}).to_string(index=False))
# so với bf13 cũ (SUPERSEDED)
OLD = os.path.join(os.path.dirname(O), "backfill13", "earnings_px_bf13.SUPERSEDED.pkl")
if os.path.exists(OLD):
    old = pickle.load(open(OLD, "rb")); old["time"] = pd.to_datetime(old["time"])
    k = old[old.time.isin(gap)].merge(pxB[pxB.time.isin(gap)], on=["ticker", "time"], how="outer", suffixes=("_old", "_new"))
    dd = k[(k.Close_old / k.Close_new - 1).abs() > 0.001]
    p("bf13 cũ vs v2 trên 13 phiên: dòng", len(k), "khác >0,1%:", len(dd), "chỉ-cũ", int(k.Close_new.isna().sum()), "chỉ-mới", int(k.Close_old.isna().sum()))
# lớp lỗi reviewer đo (01/08–27/10): raw_basis mới so với BQ Price, và với ticker_1m nơi chồng lấn
w = a[(a.time >= "2026-08-01") & (a.time <= "2026-10-27")]
x = w[(w.Close_raw / w.Price - 1).abs() > 0.001]
p("01/08–27/10: raw_basis mới khác BQ Price >0,1%:", len(x), "dòng /", x.ticker.nunique(), "mã; src:", x.src.value_counts().to_dict())
if len(x): p(x[["ticker", "time", "Close_raw", "Price", "Close", "r_prev", "r", "r_next", "src"]].to_string(index=False))
open(f"{O}/recon.txt", "w").write("\n".join(L) + "\n")
open(f"{O}/MD5.txt", "w").write("\n".join(f"{k} {v}" for k, v in {
    "canonical_earnings_px": md5(PX), "canonical_lagged_pos_ov": md5(OV),
    "earnings_px_bf13v2": md5(f"{O}/earnings_px_bf13v2.pkl"), "lagged_pos_ov_bf13v2": md5(f"{O}/lagged_pos_ov_bf13v2.pkl"),
    **{f"src_{os.path.basename(f)}": md5(f"{O}/data/{f}") for f in sorted(os.listdir(f"{O}/data"))}}.items()) + "\n")
print(open(f"{O}/MD5.txt").read())
