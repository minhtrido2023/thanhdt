"""Luồng E4 (job Taylor_20261112_151839) — dựng blocklist (ticker, NGÀY KHỚP, book) cho từng luật live-only W2b.
Quy ước: luật hiệu lực từ ngày E (theo brief) ⇒ chặn lệnh KHỚP ngày d ≥ E; vị từ đánh giá trên dữ liệu đóng cửa phiên
TRƯỚC d (= ngày lập plan, point-in-time). Dữ liệu: cache BQ đóng băng sandbox (ADV3T = Volume_3M_P50 × COALESCE(Price,Close),
đúng due_diligence.adv_vnd), universe_pit_q chụp 12/11 (universe_pit_q_20261028_1111.csv), dd_price_zones chụp 12/11.
  blk_adv.csv   : ADV3T < 2 tỷ, d ≥ 2026-08-10, book * (BAL+LAG; engine tự miễn CAPIT*/ETF*)
  blk_flag.csv  : cờ = NGOAI_UNIVERSE (không in_universe / không có dòng) ∪ quality_flag≠QUALITY_OK ∪ ADV3T ≤ 0,1 tỷ (book *)
                  ∪ SURPRISE_PHONG_CO_HOC NP_P4 ≤ 0 (book LAG), d ≥ 2026-11-03. KHÔNG mô hình LENH_QUA_LON_VS_ADV (phụ thuộc size).
  blk_ddzone.csv: LAG mua chỉ khi có DD dd_date ≤ ngày plan và Price ≤ tâm; còn lại chặn; d ≥ 2026-11-09, book LAG."""
import json, os
import pandas as pd
R = os.path.dirname(os.path.abspath(__file__))
X = pd.read_parquet(f"{R}/sb/data/bq_cache_asof20261111/ticker/2026.parquet", columns=["time", "ticker", "Price", "Close", "Volume_3M_P50", "NP_P4"])
X["time"] = pd.to_datetime(X["time"]); X = X[X.time >= "2026-07-01"]
X["px"] = X["Price"].where(X["Price"] > 0, X["Close"]); X["adv"] = X["Volume_3M_P50"] * X["px"]
days = sorted(X.time.unique()); nxt = {days[i]: days[i + 1] for i in range(len(days) - 1)}
X = X[X.time.isin(nxt)].copy(); X["fill"] = X.time.map(nxt)


def out(df, name, book="*"):
    o = df[["ticker", "fill"]].rename(columns={"fill": "date"}).copy(); o["book"] = book; o["date"] = o["date"].dt.strftime("%Y-%m-%d")
    return o


adv = X[(X.fill >= "2026-08-10") & ~(X.adv >= 2e9)]
out(adv, "adv").to_csv(f"{R}/blk_adv.csv", index=False)
U = pd.read_csv(f"{R}/universe_pit_q_20261028_1111.csv"); U["time"] = pd.to_datetime(U["time"])
F = X[X.fill >= "2026-11-03"].merge(U, on=["time", "ticker"], how="left")
inu = F["in_universe"].astype(str).str.lower().eq("true")
flag = F[(~inu) | (F["quality_flag"] != "QUALITY_OK") | ~(F["adv"] > 1e8)]
surp = F[~(F["NP_P4"] > 0)]
pd.concat([out(flag, "flag"), out(surp, "flag", "LAG")]).drop_duplicates().to_csv(f"{R}/blk_flag.csv", index=False)
Z = pd.DataFrame(json.load(open(f"{R}/dd_price_zones_frozen_20261112.json"))["entries"]); Z["dd_date"] = pd.to_datetime(Z["dd_date"])
D = X[X.fill >= "2026-11-09"].copy()
def ok(r):
    z = Z[(Z.ticker == r.ticker) & (Z.dd_date <= r.time)]
    if not len(z): return False
    c = z.sort_values(["dd_date"] + (["rev"] if "rev" in z else [])).iloc[-1]["center"]
    return bool(c and c > 0 and r.px <= c)
D["ok"] = D.apply(ok, axis=1)
out(D[~D.ok], "ddzone", "LAG").to_csv(f"{R}/blk_ddzone.csv", index=False)
for f in ("blk_adv", "blk_flag", "blk_ddzone"):
    b = pd.read_csv(f"{R}/{f}.csv"); print(f, len(b), "dong,", b.ticker.nunique(), "ma,", b.date.min(), "->", b.date.max())
print("pit_q khop dong:", int(F["in_universe"].notna().sum()), "/", len(F))
