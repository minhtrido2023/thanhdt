"""Phần 3: phân loại mã-quý (universe_pit tại cuối quý, 2014Q3+) theo độ tin của eff_date=Release_Date.
N = cặp (ticker, quarter). Read-only trên raw/*.csv + out_news_vs_release_date.csv."""
import pandas as pd, numpy as np
tf = pd.read_csv("raw/tf_current.csv", parse_dates=["time", "Release_Date", "qend"])
fa = pd.read_csv("raw/fa_current.csv", parse_dates=["time"])
tf["univ"] = tf.in_univ_qend.eq(True)
tf["bank"] = tf.ticker.map(fa.sort_values("time").groupby("ticker").route.last()).eq("BANK")
tf = tf.sort_values(["ticker", "qend"])
tf["prev_rd"] = tf.groupby("ticker").Release_Date.shift()
tf["prev_q"] = tf.groupby("ticker").quarter.shift()
tf["eff"] = tf.Release_Date.fillna(tf.time)
tf["rd_lag"] = (tf.Release_Date - tf.qend).dt.days
tf["c_before_qend"] = tf.rd_lag < 0
tf["c_carry"] = tf.Release_Date.notna() & tf.prev_rd.notna() & (tf.Release_Date <= tf.prev_rd)
tf["c_definite_peek"] = tf.c_before_qend | tf.c_carry
tf["c_early_le7"] = tf.rd_lag.between(0, 7)          # công bố <=7 ngày sau quý: đáng ngờ (không chắc sai)
news = pd.read_csv("out_news_vs_release_date.csv")[["ticker", "quarter", "public_date", "d_rd_minus_news"]]
tf = tf.merge(news, on=["ticker", "quarter"], how="left")
tf["has_news"] = tf.public_date.notna() & tf.Release_Date.notna()
tf["c_news_peek6"] = tf.has_news & (tf.d_rd_minus_news <= -6)
tf["c_news_cons6"] = tf.has_news & (tf.d_rd_minus_news >= 6)
H = tf[tf.univ & (tf.quarter >= "2014Q3") & (tf.quarter <= "2026Q2")].copy()
H["qn"] = "Q" + H.quarter.str[-1]
H["grp"] = np.where(H.bank, "bank", "nonbank")
H["era"] = np.where(H.quarter >= "2025Q1", "2025Q1-26Q2", np.where(H.quarter >= "2020Q1", "2020-24", "2014-19"))
agg = lambda g: pd.Series({"N": len(g), "rd_null": g.Release_Date.isna().sum(),
    "definite_peek": g.c_definite_peek.sum(), "definite_peek_pct": round(100 * g.c_definite_peek.mean(), 2),
    "early_le7": g.c_early_le7.sum(),
    "N_news": g.has_news.sum(), "news_peek6": g.c_news_peek6.sum(), "news_cons6": g.c_news_cons6.sum(),
    "news_peek6_pct": round(100 * g.c_news_peek6.sum() / max(g.has_news.sum(), 1), 1),
    "news_cons6_pct": round(100 * g.c_news_cons6.sum() / max(g.has_news.sum(), 1), 1)})
T1 = H.groupby(["era", "grp"]).apply(agg); T2 = H.groupby(["qn", "grp"]).apply(agg)
print(T1.to_string()); print(T2.to_string())
pd.concat([T1.assign(cut="era"), T2.assign(cut="quarter")]).to_csv("out_phase3_peek_classes.csv")
dp = H[H.c_definite_peek][["ticker", "quarter", "prev_q", "prev_rd", "Release_Date", "time", "rd_lag", "bank"]]
dp.to_csv("out_phase3_definite_peek_cases.csv", index=False)
print("definite peek theo quý (univ):", dp.quarter.value_counts().sort_index().to_dict())
# Hệ quả trên fa_ratings_8l: dòng carry-over có eff trùng eff của quý trước -> ROW_NUMBER(q_time DESC) GHI ĐÈ rating quý trước
fk = fa.set_index(["ticker", "time"]).rating
dp2 = dp[dp.Release_Date.notna()]
print("definite-peek univ có RD trùng đúng RD quý trước (ghi đè dòng quý trước trong fa_ratings_8l):",
      int((dp2.Release_Date == dp2.prev_rd).sum()), "/", len(dp2))
# độ dài nhìn trộm: từ eff(RD) tới 'time' (time thường = ngày dữ liệu thật vào) cho các ca carry
dp2 = dp2.assign(peek_days=(dp2.time - dp2.Release_Date).dt.days)
print("peek_days (time - RD) definite:", dp2.peek_days.describe()[["count", "50%", "75%", "max"]].to_dict())
