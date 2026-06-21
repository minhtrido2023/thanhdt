---
name: lag_pickle_stringdtype_fix_2026
description: Fix khi pickle (ba_v11_*/earnings_*/lagged_*) không load được trên Linux env — pandas 2.3.3 vs StringDtype mới; dựng lại từ BQ
metadata: 
  node_type: memory
  type: reference
  originSessionId: b9f5df15-d12b-4ad2-9ce0-4383e857f93b
---

[REDACTED]. Trên Linux env này (pandas 2.3.3), các pickle signal/cache ghi bằng pandas string-dtype mới (`StringDtype(storage='python', na_value=nan)`, kiểu mặc định pandas 3.0) **KHÔNG load được** → `NotImplementedError` ở `NDArrayBacked.__setstate__`. Bị: `ba_v11_*_sig.pkl`, `ba_patches_signal_cache.pkl`, `earnings_px.pkl`, `lagged_pos_ov.pkl`, `earnings_surprise_data.pkl`. (intraday_full.pkl lỗi KHÁC: numpy `_core.numeric` — nhưng vô hại, mọi nơi load nó bọc try/except → rơi về T+1-Open.) Monkeypatch `__setstate__` KHÔNG được (Cython non-writable).

**FIX = dựng lại từ BQ** (`rebuild_lag_caches.py`), KHÔNG sửa pandas. Momentum signal KHÔNG cần pickle (regen tươi qua `bq(SIGNAL_V11.format(...))`). 3 cache LAG chỉ là data thô BQ: earnings_px=(ticker,time,Close), lagged_pos_ov=(ticker,time,Open,Volume_3M_P50), earnings_surprise_data=(ticker,quarter,time,Release_Date,NP_P0..P7,NP_R,Revenue_YoY_P0). `refresh_lagged_caches.py` không tự sửa được vì nó load-rồi-append (vấp pickle cũ) → phải FULL pull bỏ qua load. Universe LAG = mã có earnings (distinct ticker trong earnings_surprise_data, ~1258). **QUAN TRỌNG: ghi `ticker` astype(object)** (không để StringDtype) để pickle load lại được. Đã chạy: 3 file reload sạch, coverage events 100%.

**Harness full-history 2014→now = `pt_v23_audit_2014.py`** (KHÔNG phải pt_v22_dt5g.py — đó là live-forward START_DATE=[REDACTED]11 ~vài ngày). pt_v23 chỉ load earnings_surprise_data.pkl (giá LAG pull thẳng BQ); `pt_dates.detect_end_date()` load lagged_pos_ov.pkl để cap END_DATE. Baseline chạy OK [REDACTED]: V2.3A FULL CAGR 21.44%/Sh1.55/DD−25.0%/Cal0.86, self-check 0 VND. [[dcf_valuation_ic_test_2026]]
