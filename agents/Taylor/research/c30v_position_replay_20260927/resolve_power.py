"""Vòng 3 — đo NHỮNG GÌ quant-skeptic đòi, bằng phép đo của TÔI, không lấy lại số của nó.

Ba câu, cả ba đều là "phép kiểm này phân giải được tới đâu", chứ không phải "kết luận là gì":
  (1) IS/OOS: chênh replay−flat có ổn định giữa 2014-19 và 2020+ không (báo cáo vòng 2 chỉ có
      số toàn kỳ, và §18 coding_guidelines bắt walk-forward).
  (2) Độ phân giải THẬT: bootstrap theo NGÀY trên chuỗi đóng góp, cho từng nhãn sự kiện. Gross
      Σ|contrib| mà attribute.py in ra phạt quá tay lớp nhiễu trung bình-0; CI mới là số đúng.
  (3) Chân TRỌNG SỐ (custom_basket.py:544 mcapw = pxw × OShares): bao nhiêu phiên rổ mà giá re-base
      mà số CP KHÔNG bước cùng phiên. Replay nhập wmap nguyên xi nên KHÔNG test được chân này —
      đo để ghi đúng giới hạn, không phải để kết luận.
"""
import numpy as np, pandas as pd

H = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/c30v_position_replay_20260927"
at = pd.read_parquet(f"{H}/attribution.parquet")
at["date"] = pd.to_datetime(at["date"])
START, END = pd.Timestamp("2014-08-05"), pd.Timestamp("2026-06-19")
at = at[(at["date"] >= START) & (at["date"] <= END)]
YRS = (END - START).days / 365.25

lvl = pd.read_parquet(f"{H}/levels_base.parquet")
lvl.index = pd.to_datetime(lvl.index)
lvl = lvl.loc[START:END]


def cagr(s):
    s = s.dropna()
    return ((s.iloc[-1] / s.iloc[0]) ** (365.25 / (s.index[-1] - s.index[0]).days) - 1) * 100


print(f"cửa sổ {START.date()} → {END.date()} = {YRS:.4f}y · {len(lvl)} phiên · {len(at):,} name×session\n")

print("=== (1) IS / OOS — walk-forward §18 ===")
CUT = pd.Timestamp("2020-01-01")
rows = []
for tag, sl in (("FULL", lvl), ("IS 2014-08→2019-12", lvl.loc[:CUT]), ("OOS 2020-01→2026-06", lvl.loc[CUT:])):
    c = {k: cagr(sl[k]) for k in lvl.columns}
    rows.append({"kỳ": tag, "n phiên": len(sl), "FLAT": c["ENGINE_FLAT"], "LEGACY": c["ENGINE_LEGACY"],
                 "REPLAY_B": c["REPLAY_B"],
                 "Δ B−FLAT": c["REPLAY_B"] - c["ENGINE_FLAT"],
                 "phantom LEGACY−FLAT": c["ENGINE_LEGACY"] - c["ENGINE_FLAT"]})
print(pd.DataFrame(rows).to_string(index=False, float_format=lambda v: f"{v:8.3f}"))

# đóng góp pp/năm theo nhãn, tách kỳ — RIGHTS là lớp không mô phỏng được nên phải tách ra
def ppyr(df, yrs):
    return df.groupby("label")["contrib_rep_minus_flat"].sum() / yrs * 100

print("\n  đóng góp pp/năm theo nhãn (ròng):")
a_is, a_oos = at[at["date"] < CUT], at[at["date"] >= CUT]
y_is = (CUT - START).days / 365.25
y_oos = (END - CUT).days / 365.25
cmp_ = pd.DataFrame({"IS": ppyr(a_is, y_is), "OOS": ppyr(a_oos, y_oos), "FULL": ppyr(at, YRS)})
print(cmp_.to_string(float_format=lambda v: f"{v:+8.3f}"))

print("\n=== (2) độ phân giải THẬT — bootstrap theo NGÀY (4000 lần, khối = 1 phiên) ===")
print("  (gross Σ|contrib| phạt quá tay lớp nhiễu trung bình-0; CI là con số đúng để trích)")
FREE = ["FREESHARE", "DIV+FREESHARE"]
buckets = {
    "lớp ĐANG AUDIT (FREESHARE + DIV+FREESHARE)": at["label"].isin(FREE),
    "DIV (cổ tức tiền)": at["label"] == "DIV",
    "NONE (không sự kiện)": at["label"] == "NONE",
    "MỌI thứ trừ RIGHTS": ~at["label"].str.contains("RIGHTS"),
    "RIGHTS (không mô phỏng được)": at["label"].str.contains("RIGHTS"),
}
rng = np.random.default_rng(20260927)
days = lvl.index
out = []
for nm, msk in buckets.items():
    ser = at[msk].groupby("date")["contrib_rep_minus_flat"].sum().reindex(days, fill_value=0.0).values
    net = ser.sum() / YRS * 100
    gross = np.abs(at[msk]["contrib_rep_minus_flat"]).sum() / YRS * 100
    idx = rng.integers(0, len(ser), size=(4000, len(ser)))
    bs = ser[idx].sum(axis=1) / YRS * 100
    lo, hi = np.percentile(bs, [2.5, 97.5])
    out.append({"lớp": nm, "n": int(msk.sum()), "ròng pp/năm": net, "SE boot": bs.std(),
                "CI95 lo": lo, "CI95 hi": hi, "GROSS pp/năm": gross})
print(pd.DataFrame(out).to_string(index=False, float_format=lambda v: f"{v:+8.3f}"))

print("\n=== (3) chân TRỌNG SỐ — replay KHÔNG test được (nhập wmap nguyên xi) ===")
bx = pd.read_parquet(f"{H}/panel_bx.parquet")
bx["time"] = pd.to_datetime(bx["time"])
mem = pd.read_parquet(f"{H}/members_df.parquet")
mem["rebal_date"] = pd.to_datetime(mem["rebal_date"])

# "trong rổ tại phiên d" = thuộc kỳ rebal có hiệu lực gần nhất <= d (đúng semantics wmap của replay)
rebs = sorted(mem["rebal_date"].unique())
bx = bx[(bx["time"] >= START) & (bx["time"] <= END)].sort_values(["ticker", "time"]).copy()
bx["reb"] = pd.Series(np.searchsorted(rebs, bx["time"].values, side="right") - 1, index=bx.index)
valid = bx["reb"] >= 0
mm = {i: set(mem.loc[mem["rebal_date"] == r, "ticker"]) for i, r in enumerate(rebs)}
bx["in_basket"] = False
bx.loc[valid, "in_basket"] = [t in mm[i] for t, i in zip(bx.loc[valid, "ticker"], bx.loc[valid, "reb"])]

g = bx.groupby("ticker", sort=False)
bx["ratio"] = bx["Close"] / bx["pxw"]   # pxw = giá THÔ (weight price); Close = đã điều chỉnh
bx["d_ratio"] = g["ratio"].pct_change()
bx["d_osh"] = g["OShares"].pct_change()

reb_ = bx[(bx["d_ratio"].abs() > 0.005) & bx["in_basket"]]     # giá re-base thật, TRONG rổ
same = reb_[reb_["d_osh"].abs() > 0.005]                       # số CP bước CÙNG phiên
print(f"  {len(reb_)} phiên (ticker×session) TRONG RỔ mà hệ số điều chỉnh giá bước >0,5%")
print(f"  {len(same)} ({len(same)/max(len(reb_),1):.0%}) có OShares bước CÙNG phiên "
      f"⇒ {len(reb_)-len(same)} phiên giá và số CP LỆCH NGÀY")

# khoảng cách ngày tới bước OShares gần nhất, cho những phiên lệch
osh_steps = {t: d["time"].values for t, d in bx[bx["d_osh"].abs() > 0.005].groupby("ticker")}
gaps = []
for t, d in zip(reb_["ticker"], reb_["time"]):
    st = osh_steps.get(t)
    if st is None or len(st) == 0:
        gaps.append(np.nan); continue
    gaps.append(np.abs((st - np.datetime64(d)).astype("timedelta64[D]").astype(float)).min())
gaps = pd.Series(gaps)
print(f"  khoảng cách (ngày dương lịch) tới bước OShares gần nhất: median {gaps.median():.0f}, "
      f"p90 {gaps.quantile(0.9):.0f}, max {gaps.max():.0f}; {int((gaps > 5).sum())} phiên lệch >5 ngày, "
      f"{int(gaps.isna().sum())} mã không có bước nào")
print("  ⇒ mcapw = pxw × OShares ghép giá ĐÃ re-base với số CP CHƯA bước. Chân TRỌNG SỐ được chuẩn")
print("    hoá theo tiết diện + cap 0,10 nên KHÔNG in ra phantom return như chân return đã sửa, và")
print("    custom_basket.py:112-120 khai đây là staleness CHẤP NHẬN CÓ CHỦ Ý. Nhưng replay dùng lại")
print("    ĐÚNG wmap đó (replay.py:390) ⇒ audit này chứng nhận chân RETURN, KHÔNG chứng nhận chân")
print("    TRỌNG SỐ. Đây là giới hạn phạm vi, KHÔNG phải phát hiện lỗi.")
