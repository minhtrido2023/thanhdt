"""
Bước 2.2 — tập kiểm chứng ĐỘC LẬP, KHÔNG chứa 16 mã BANNED.
Tiêu chí khách quan (đo được từ dữ liệu, không phải danh sách người chọn):
  EVENT-A: BVPS chuyển ÂM LẦN ĐẦU (BVPS>0 quý trước -> BVPS<=0 quý này), xảy ra 2020Q1 trở đi.
  (đây là hỏng-bảng-cân-đối khách quan, không cần biết nguyên nhân/tin tức).
"""
import pandas as pd, numpy as np, json

# Verified against actual code constant, lag_forensic_filter.py:90-91 (grep'd directly, not
# transcribed from CLAUDE.md's slash-grouped KB summary which reads as 15 -- code has 16, incl BAF).
BANNED_16 = {"PC1", "VVS", "KSF", "NKG", "HSG", "HVN", "VJC", "NVL", "GEG", "SBA",
             "DMC", "IMP", "TRA", "TOS", "VTP", "BAF"}
assert len(BANNED_16) == 16

df = pd.read_csv("universe_financials_v3_intcov.csv", parse_dates=["time", "Release_Date"])
df = df.sort_values(["ticker", "time"]).reset_index(drop=True)
df = df[~df["ticker"].isin(BANNED_16)].copy()

df["prev_bvps"] = df.groupby("ticker")["BVPS"].shift(1)
df["event_a"] = (df["prev_bvps"] > 0) & (df["BVPS"] <= 0)

events = df[df["event_a"] & (df["time"] >= "2020-01-01")].copy()
# first occurrence per ticker only (avoid counting the same distress episode multiple quarters)
events = events.sort_values(["ticker", "time"]).groupby("ticker").first().reset_index()
events = events[["ticker", "time", "quarter", "Release_Date", "BVPS", "prev_bvps", "Debt_Eq_P0", "EBITDA_P0"]]
events.to_csv("independent_event_set_bvps_turn_negative.csv", index=False)
print(f"n independent danger events (2020+, ex-BANNED-15, BVPS turn negative): {len(events)}")
print(events.to_string(index=False))
