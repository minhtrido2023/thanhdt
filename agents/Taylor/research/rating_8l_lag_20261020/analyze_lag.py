"""Rating 8L lag study — Phần 1 (trễ vận hành) + Phần 3 (giả định trễ trong backtest).
Read-only: chỉ đọc raw/*.csv (đã kéo từ BQ, xem REPORT.md §Tái lập). Output: out_*.csv + in số ra stdout.
N = cặp (ticker, quarter) — mỗi cặp là 1 sự kiện công bố độc lập."""
import re, sys
import numpy as np, pandas as pd

R = "raw/"
BANKS = None
Q = lambda s: s.quantile([.5, .75, .9]).round(1).tolist() + [s.max()]


def qend(q):
    y, n = int(q[:4]), int(q[-1])
    return pd.Timestamp(y, n * 3, 1) + pd.offsets.MonthEnd(0)


def dist(s, label):
    s = s.dropna()
    if len(s) == 0:
        return {"seg": label, "N": 0}
    p = s.quantile([.5, .75, .9])
    return {"seg": label, "N": len(s), "median": p[.5], "p75": p[.75], "p90": p[.9], "max": s.max(), "min": s.min()}


tf = pd.read_csv(R + "tf_current.csv", parse_dates=["time", "Release_Date", "qend"])
fa = pd.read_csv(R + "fa_current.csv", parse_dates=["time"])
route = fa.sort_values("time").groupby("ticker")["route"].last()
tf["route"] = tf["ticker"].map(route)
tf["bank"] = tf["route"].eq("BANK")
tf["qn"] = tf["quarter"].str[-1].astype(int)
tf["rd_lag"] = (tf["Release_Date"] - tf["qend"]).dt.days        # quý-kết-thúc -> Release_Date
tf["t_lag"] = (tf["time"] - tf["qend"]).dt.days
tf["univ"] = tf["in_univ_qend"].fillna(False).astype(bool)
tf["rd_null"] = tf["Release_Date"].isna()

# ---------------- A. Release_Date semantics -------------------------------------------------
print("== A1. Release_Date NULL / time==Release_Date, universe_pit, 2025Q1..2026Q3")
W = tf[(tf.quarter >= "2025Q1") & tf.univ]
a1 = W.groupby("quarter").agg(N=("ticker", "size"), n_null=("rd_null", "sum"),
                              eq=("time", lambda s: (s == W.loc[s.index, "Release_Date"]).sum()),
                              rd_before_qend=("rd_lag", lambda s: (s < 0).sum()))
print(a1.to_string())

# A2. Independent source: stock_news titles "BCTC ... quý k/yyyy" -> earliest public_date per (ticker, quarter)
n = pd.read_csv(R + "stock_news_bctc.csv")
roman = {"i": 1, "ii": 2, "iii": 3, "iv": 4}
pat = re.compile(r"(?:báo cáo tài chính|bctc)[^:]*?quý\s*(iv|iii|ii|i|[1-4])\s*(?:/|năm|-)\s*(20\d\d)", re.I)
def parse(t):
    m = pat.search(str(t))
    if not m:
        return None
    k = m.group(1).lower(); k = roman.get(k, None) or int(k)
    return f"{m.group(2)}Q{k}"
n["quarter"] = n["title"].map(parse)
low = n["title"].str.lower()
n = n[n.quarter.notna() & ~low.str.contains("giải trình|đính chính|điều chỉnh|soát xét|kiểm toán|gia hạn|chậm")]
n["public_date"] = pd.to_datetime(n["public_date"])
nf = n.groupby(["ticker", "quarter"], as_index=False)["public_date"].min()
m = nf.merge(tf[["ticker", "quarter", "Release_Date", "time", "qend", "univ", "bank"]], on=["ticker", "quarter"])
m["d_rd_minus_news"] = (m["Release_Date"] - m["public_date"]).dt.days
m["d_time_minus_news"] = (m["time"] - m["public_date"]).dt.days
m.to_csv("out_news_vs_release_date.csv", index=False)
mm = m[m.Release_Date.notna()]
print(f"\n== A2. stock_news vs Release_Date: N cặp (ticker,quý) khớp = {len(mm)} "
      f"(quý {mm.quarter.min()}..{mm.quarter.max()}; univ={mm.univ.sum()})")
vc = mm["d_rd_minus_news"].clip(-5, 5).value_counts().sort_index()
print("RD - news (ngày, cắt ±5):", vc.to_dict())
print("share |diff|<=1:", round((mm.d_rd_minus_news.abs() <= 1).mean(), 3),
      " RD>news+1:", round((mm.d_rd_minus_news > 1).mean(), 3), " RD<news-1:", round((mm.d_rd_minus_news < -1).mean(), 3))
mn = m[m.Release_Date.isna()]
print(f"   NULL-RD rows có tin: N={len(mn)}; time - news:", dist(mn.d_time_minus_news, "x"))
print("   theo năm news:", mm.groupby(mm.public_date.dt.year)["d_rd_minus_news"].agg(
    lambda s: f"N={len(s)} exact={(s == 0).mean():.2f} le1={(s.abs() <= 1).mean():.2f}").to_dict())

# ---------------- B. Phân phối quý-kết-thúc -> Release_Date (công bố) ----------------------
print("\n== B. qend -> Release_Date (ngày), universe_pit, Release_Date not null")
rows = []
for (q, b), g in W[W.Release_Date.notna()].groupby(["quarter", "bank"]):
    rows.append({**dist(g.rd_lag, "rd_lag"), "quarter": q, "bank": b})
B = pd.DataFrame(rows)[["quarter", "bank", "N", "median", "p75", "p90", "max", "min"]]
print(B.to_string(index=False))
B.to_csv("out_qend_to_release_by_quarter.csv", index=False)

# ---------------- C. Đoạn (a): Release_Date -> có trong ticker_financial ---------------------
# C1. Q2/2026: so ticker_financial_breadth.csv (đếm THẬT ~19:00 ICT mỗi ngày làm việc) với đường cumulative
#     Release_Date<=d (từ bảng hiện tại). Nếu Release_Date là ngày ingest -> 2 đường trùng.
br = pd.read_csv(R + "ticker_financial_breadth.csv", parse_dates=["date"])
cur = tf[tf.quarter == "2026Q2"]
out = []
for _, r in br[br.quarter == "2026Q2"].iterrows():
    cum_rd = int((cur.Release_Date <= r.date).sum())
    cum_t = int((cur.time <= r.date).sum())
    out.append({"date": r.date.date(), "observed": r.n_tickers, "cum_RD_le_d": cum_rd, "cum_time_le_d": cum_t,
                "gap_RD": cum_rd - r.n_tickers})
C1 = pd.DataFrame(out)
C1.to_csv("out_breadth_vs_cum_release_2026Q2.csv", index=False)
print("\n== C1. Q2/2026 breadth thực đo vs cum(Release_Date<=d)\n", C1.to_string(index=False))

# C2. Pin 2026-07-29 22:30 ICT (giữa mùa Q2): mã có RD<=07-28 trong bảng HIỆN TẠI nhưng VẮNG trong pin
p7 = pd.read_csv(R + "tf_pin_202607.csv", parse_dates=["time", "rd"])
k7 = set(zip(p7.ticker, p7.quarter))
c = cur.copy(); c["in_pin0729"] = [(t, q) in k7 for t, q in zip(c.ticker, c.quarter)]
for cut in ["2026-07-20", "2026-07-25", "2026-07-28", "2026-07-29"]:
    s = c[c.Release_Date <= cut]
    print(f"   RD<={cut}: N={len(s)}, vắng trong pin 07-29 = {(~s.in_pin0729).sum()}")
late = c[(c.Release_Date <= "2026-07-28") & ~c.in_pin0729][["ticker", "quarter", "Release_Date", "time", "univ"]]
late.to_csv("out_q2_2026_rd_before_pin_but_absent.csv", index=False)
# RD bị đổi giữa pin và hiện tại?
pj = p7.merge(cur[["ticker", "quarter", "Release_Date", "time"]], on=["ticker", "quarter"], how="inner")
print(f"   pin07-29 vs hiện tại, Q2/2026 cặp chung N={len(pj)}: RD đổi = {(pj.rd != pj.Release_Date).sum()}, "
      f"time đổi = {(pj.time_x != pj.time_y).sum()}")

# C3. Q3/2026 time-travel hourly (first seen) -> đoạn (a) & (b) độ phân giải 1h
try:
    tt = pd.read_csv(R + "tt_ticker_financial_2026Q3.csv")
    tr = pd.read_csv(R + "tt_fa_ratings_8l_202610.csv")
    fs_tf = tt.groupby(["ticker", "quarter"]).agg(first_seen_tf=("snap_ict", "min"), rd=("rd", "first"), time=("time", "first")).reset_index()
    fs_fa = tr.groupby(["ticker", "time"]).agg(first_seen_fa=("snap_ict", "min")).reset_index()
    x = fs_tf.merge(fs_fa, left_on=["ticker", "rd"], right_on=["ticker", "time"], how="left", suffixes=("", "_fa"))
    x["a_hours"] = (pd.to_datetime(x.first_seen_tf) - pd.to_datetime(x.rd)).dt.total_seconds() / 3600
    x["b_hours"] = (pd.to_datetime(x.first_seen_fa) - pd.to_datetime(x.first_seen_tf)).dt.total_seconds() / 3600
    x["window_start"] = tt.snap_ict.min()
    x.to_csv("out_q3_2026_timetravel_first_seen.csv", index=False)
    print(f"\n== C3. Q3/2026 time-travel (cửa sổ từ {tt.snap_ict.min()} tới {tt.snap_ict.max()}), N={len(x)}")
    print(x[["ticker", "rd", "first_seen_tf", "first_seen_fa", "a_hours", "b_hours"]].to_string(index=False))
except FileNotFoundError:
    print("\n== C3. time-travel chưa xong")

# ---------------- D. Đoạn (b): có trong TF -> có rating trong fa_ratings_8l ------------------
# D1. Độ phủ: cặp TF (univ, RD not null) có dòng fa_ratings_8l với time==Release_Date?
fk = set(zip(fa.ticker, fa.time))
W2 = W.copy()
W2["eff"] = W2["Release_Date"].fillna(W2["time"])                     # eff_date_of (offset 0)
W2["has_rating_row"] = [(t, e) in fk for t, e in zip(W2.ticker, W2.eff)]
d1 = W2.groupby("quarter")["has_rating_row"].agg(["size", "sum"])
print("\n== D1. cặp TF (universe) có dòng fa_ratings_8l tại eff_date:\n", d1.to_string())
W2[~W2.has_rating_row][["ticker", "quarter", "Release_Date", "time", "route"]].to_csv("out_tf_without_rating_row.csv", index=False)

# D2. Pin đồng thời 07-29 (TF 22:30, fa 22:36 ICT) và 10-01: cặp có trong TF-pin mà fa-pin chưa có dòng
for p in ["202607", "202608", "202610"]:
    tp = pd.read_csv(R + f"tf_pin_{p}.csv", parse_dates=["time", "rd"])
    fp = pd.read_csv(R + f"fa_pin_{p}.csv", parse_dates=["time"])
    tp["eff"] = tp.rd.fillna(tp.time)
    k = set(zip(fp.ticker, fp.time))
    rec = tp[tp.eff >= tp.eff.max() - pd.Timedelta(days=60)]
    miss = rec[[(t, e) not in k for t, e in zip(rec.ticker, rec.eff)]]
    print(f"   pin {p}: cặp TF eff trong 60 ngày cuối N={len(rec)}, chưa có dòng rating = {len(miss)}"
          f" (eff max {rec.eff.max().date()}); mẫu: {miss.sort_values('eff').tail(5)[['ticker','quarter','eff']].values.tolist()}")

# D3. Lịch chạy refresh thật (log) -> độ trễ (b) theo lịch: từ ingest ~16:36 ICT ngày D tới lần refresh OK kế tiếp
import subprocess
log = open("/home/trido/thanhdt/WorkingClaude/mike/logs/fa_ratings_8l_refresh.log", encoding="utf-8", errors="ignore").read()
oks = re.findall(r"OK: refreshed — lastModified (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)", log)
runs = pd.to_datetime(pd.Series(oks)).sort_values().reset_index(drop=True)
runs.to_csv("out_fa_ratings_8l_refresh_runs.csv", index=False, header=["lastModified_ict"])
print(f"\n== D3. refresh OK trong log: {len(runs)} lần, {runs.min()} → {runs.max()}")

def next_run(ts):
    i = runs.searchsorted(ts)
    return runs.iloc[i] if i < len(runs) else pd.NaT

# Giả định ingest 16:36 ICT ngày D (cron_registry). D = ngày xuất hiện ≈ Release_Date (xem A/C).
rows = []
for q in ["2026Q2"]:
    g = tf[(tf.quarter == q) & tf.univ & tf.Release_Date.notna()]
    for _, r in g.iterrows():
        ing = r.Release_Date + pd.Timedelta(hours=16, minutes=36)
        nr = next_run(ing)
        rows.append({"ticker": r.ticker, "quarter": q, "rd": r.Release_Date.date(), "next_refresh": nr,
                     "b_hours_sched": (nr - ing).total_seconds() / 3600 if pd.notna(nr) else np.nan, "bank": r.bank})
D3 = pd.DataFrame(rows)
D3.to_csv("out_b_segment_by_schedule_2026Q2.csv", index=False)
print("   (b) theo lịch thực chạy, Q2/2026, giờ:", dist(D3.b_hours_sched, "b"))
D3["rd_m"] = pd.to_datetime(D3.rd)
D3["in_window"] = ((D3.rd_m.dt.month == 7) & (D3.rd_m.dt.day >= 10)) | ((D3.rd_m.dt.month == 8) & (D3.rd_m.dt.day <= 10))
print("   trong cửa sổ:", dist(D3[D3.in_window].b_hours_sched, "in"), "\n   ngoài cửa sổ:", dist(D3[~D3.in_window].b_hours_sched, "out"))
print("   ngoài cửa sổ N mã:", (~D3.in_window).sum(), "/", len(D3))

# ---------------- E. Phần 3 — giả định trễ trong backtest so với Release_Date thật ----------
print("\n== E. Phần 3")
H = tf[tf.univ & (tf.quarter >= "2014Q3")].copy()
# E1. eff_date_of: RD hoặc time (offset 0). Peek (i) chỉ có thể xảy ra khi eff < ngày công bố thật.
#     Với RD not null: eff = RD. Proxy ngày công bố thật = RD (A2 xác nhận). NULL: eff = time (placeholder).
print("E1. tỉ lệ NULL Release_Date (eff = time placeholder) theo nhóm:")
H["era"] = np.where(H.quarter >= "2020Q1", "2020+", "2014-19")
print(H.groupby(["era", "bank"])["rd_null"].agg(["size", "mean"]).round(3).to_string())
# E2. bank_aq_avail_date (FiinPro +45 / Q4 +90) vs Release_Date thật của chính ngân hàng
Bk = H[H.bank & H.Release_Date.notna()].copy()
Bk["fiin_avail"] = Bk.qend + pd.to_timedelta(np.where(Bk.qn == 4, 90, 45), unit="D")
Bk["gap"] = (Bk.fiin_avail - Bk.Release_Date).dt.days     # >0 = quá thận trọng; <0 = nhìn trộm
Bk["peek"] = Bk.gap < 0
Bk["conservative_gt14"] = Bk.gap > 14
e2 = Bk.groupby("qn").agg(N=("gap", "size"), peek=("peek", "mean"), cons14=("conservative_gt14", "mean"),
                          gap_med=("gap", "median"), gap_p10=("gap", lambda s: s.quantile(.1)), gap_p90=("gap", lambda s: s.quantile(.9)))
print("E2. NGÂN HÀNG: FiinPro +45/+90 vs Release_Date (gap = avail - RD, ngày):\n", e2.round(3).to_string())
print("   theo era:", Bk.groupby("era").agg(N=("gap", "size"), peek=("peek", "mean"), cons14=("conservative_gt14", "mean"), gap_med=("gap", "median")).round(3).to_dict("index"))
Bk[Bk.peek][["ticker", "quarter", "Release_Date", "fiin_avail", "gap"]].to_csv("out_bank_fiin_peek_cases.csv", index=False)
# E2b. Hệ quả thực: rating ngân hàng dòng eff=RD dùng quý FiinPro nào? (bank_aq_asof: quý mới nhất có avail<=eff)
#      -> khi RD < avail(q) thì dòng rating quý q dùng NPL quý q-1 (stale) — thận trọng, KHÔNG peek.
Bk["uses_same_q_fiin"] = Bk.fiin_avail <= Bk.Release_Date
print("   tỉ lệ dòng rating ngân hàng dùng NPL CÙNG quý (avail<=RD):",
      Bk.groupby("qn")["uses_same_q_fiin"].mean().round(3).to_dict())
# E3. Hằng số +45 fallback (custom_basket QFLOOR/DY_TIEBREAK, tắt mặc định) vs dòng NULL: không có RD thật để so;
#     so time placeholder với tin stock_news nếu có (A2 phần NULL).
# E4. Ngoại lai: Release_Date < qend (không thể là ngày công bố thật của quý đó)
bad = tf[(tf.rd_lag < 0)][["ticker", "quarter", "time", "Release_Date", "rd_lag", "univ"]]
bad.to_csv("out_release_date_before_quarter_end.csv", index=False)
print(f"E4. Release_Date < cuối quý: N={len(bad)} (univ {bad.univ.sum()}); quý>=2025Q1: {(bad.quarter>='2025Q1').sum()}")
print(bad[bad.quarter >= "2025Q1"].to_string(index=False))

# ---------------- F. Ngoại lai trễ công bố > p90 (2025Q1..2026Q2) ---------------------------
F = W[W.Release_Date.notna()].copy()
p90 = F.groupby(["quarter", "bank"])["rd_lag"].transform(lambda s: s.quantile(.9))
F = F[F.rd_lag > p90][["ticker", "quarter", "bank", "route", "rd_lag", "Release_Date"]].sort_values(["quarter", "rd_lag"])
F.to_csv("out_outliers_gt_p90.csv", index=False)
rep = F.groupby("ticker").size().sort_values(ascending=False)
print(f"\n== F. ngoại lai > p90: N={len(F)}; mã lặp lại >=3 quý: {rep[rep>=3].to_dict()}")
