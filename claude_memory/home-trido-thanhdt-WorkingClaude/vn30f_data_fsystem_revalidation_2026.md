---
name: vn30f_data_fsystem_revalidation_2026
description: "VN30F futures data now in BQ + F-system re-validated on real front-month prices (basis harmless to long-heavy overlay, short-only dead, DT5G mixed on futures)"
metadata: 
  node_type: memory
  type: project
  originSessionId: da955fb4-3cf3-4f12-a372-44b0e169e1a4
---

**[REDACTED]08.** User hỏi F-system (overlay phái sinh VN30F, không phải production chính) — đào sâu backtest + cải thiện. Production chính vẫn là DT5G + book cổ phiếu V4/V5; F-system là overlay OPTIONAL 20% vốn, state→long/short VN30F (CRISIS−100/BEAR−20/NEU+70/BULL+100/EXBULL+130 = map F_HAdapted live).

**Dữ liệu VN30F:** KHÔNG có trong BigQuery ban đầu (chỉ `VN30` spot index + `E1VFVN30` ETF). **vnstock (source VCI) CÓ**: `VN30F1M` + `VN30F2M` full history 2017-08-10→now (~2188 phiên, OHLCV). Đã nạp vào **`tav2_bq.vn30f_daily`** (f1m OHLCV + f2m_close + spot_vn30 + basis + basis_pct). Files: vn30f1m_raw.csv, vn30f2m_raw.csv, vn30f_bq_upload.csv.

**Basis (VN30F1M − spot):** cấu trúc DISCOUNT, mean −0.21%/median −0.13%/std 0.78%, 63% ngày discount, p5 −1.51%. NỚI RỘNG đúng năm gấu (2020 −0.63%, 2022 −0.48%/79% ngày disc) — carry âm cho SHORT, dương cho LONG. NHƯNG **long-carry net ≈ 0%/năm** qua trọn chu kỳ (VN30F1M cum +172.6% ≈ spot +172.8%): convergence bù discount. Chuỗi VN30F1M là GHÉP THÔ (raw-stitched, roll đã nằm trong return) → backtest dùng return VN30F1M trực tiếp, BỎ roll cost nhân tạo 1.2%/yr (đã double-count).

**Re-validation trên futures thật vs spot proxy (f_system_improve_test.py):**
1. Basis KHÔNG phá hệ thống (overlay nặng long, long-carry≈0); vài cửa sổ futures còn tốt hơn spot (LIVE/CoDien 2018+ +20.7% vs spot +16.2%). Backtest cũ không ảo tổng thể.
2. SHORT-only CHẾT hẳn, trên futures còn tệ hơn (DT5G short OOS spot +1.7%→fut +0.4%). Short VN30F = bảo hiểm rỉ máu, KHÔNG phải alpha. Dứt khoát.
3. DT5G vs Cổ Điển = 50-50 trên futures (KHÔNG còn thắng rõ như trên spot): DT5G thắng OOS 2021+ (+4.4pp, Sh+0.21, DD−22.8 vs−25.3, cắt 57% trades 116→50) nhưng THUA 2018+ (DD−36.4 vs−25.3, Sh.75 vs.96).
4. PHÁT HIỆN MỚI spot che giấu: đòn bẩy futures khuếch đại deep-DD của DT5G lên −36% (spot chỉ −32%), từ giữ long-100%+ vào cú rớt nhanh 2018/2020 khi DT5G chậm lật. → **van vol-target/cắt-nhanh BẮT BUỘC trước khi đưa DT5G lên overlay futures**; chưa có van thì CoDien≈DT5G trên futures.

**Gate-speed + vol-target van (f_system_van_gatespeed_test.py, futures, map F_HAdapted):**
- Q1 quan sát user "futures intraday → smooth nhẹ/bỏ 10-25-25" = **SAI/BÁC BỎ**. Smooth NẶNG hơn TỐT hơn: thang raw(497tr,Sh.64/DD−30) → 5_15_15(Sh.56/DD−41) → 7_20_20(Sh.51/DD−47=TỆ NHẤT) → 10_25_25(Sh.72) → 15_25_30(62tr,OOS Sh.89/Cal.90=tốt nhất no-van) → dt5g_live(Sh.74-82). Khung trung gian nhẹ = valley-of-death (whipsaw + vẫn dính long-đòn-bẩy vào cú rớt). Smoothing lọc NHIỄU TÍN HIỆU không phải bù trễ thực thi; execution speed≠signal responsiveness. → GIỮ smooth nặng cho futures.
- Q2 Vol-target van = ĐÚNG công cụ chữa deep-DD (gate-speed KHÔNG chữa được). Van B full (pos×clip(tgt/rv,0,1.5), tgt=median vol 17.5%): **DT5G+VanB Sharpe .74→.86 (2018+), deep-DD −36→−23%, CAGR gần giữ; OOS Sh.87/DD−19.4**. Van A de-risk-only cắt DD sâu hơn (−19.5) nhưng −3pp CAGR. ⚠️van rescale daily → trades 42→~900 (cần BANDING giảm churn).
- **CHỐT: DT5G live (giữ 10-25-25+macro) + Vol-target Van B = nâng cấp sạch** (nhất quán 2 cửa sổ, deep-DD chữa xong, đồng bộ production). Alt risk-adj cao nhất = DT 15-25-30 + Van B.

**Banding (f_system_van_banding_test.py):** DEADBAND là cơ chế thắng (bucket/weekly kém hơn; weekly DD−25% do lệch nhịp vol spike). Deadband .10 VƯỢT cả van no-band: Sharpe .86→.90 (cả 2 cửa sổ), DD −22.6→−20.6%, trades 889→292 (3×) — vùng no-trade lọc vol-noise mean-revert = ít lệnh HƠN và mượt HƠN (cải tiến free). Deadband .25 = 17-26 lệnh/năm, chỉ mất ~.04 Sharpe.
**CẤU HÌNH CHỐT CUỐI: DT5G live (10-25-25+macro) + Vol-target Van B + deadband 0.10** → 2018+ Sh.90/DD−20.6 · OOS Sh.90/DD−19.1/Cal.78 · ~35 lệnh/năm. vs baseline live no-van (Sh.74/DD−36): Sharpe .74→.90, deep-DD −36→−21%, CAGR giữ ~14%. Alt: DT15-25-30+deadband.10 = OOS Sh.99/Cal1.02 (cao nhất) nhưng DD 2018+ −30%, biến động cửa-sổ lớn hơn. Công thức van: pos=base(state)×applied; desired=clip(median_vol/rv_20d_annual,0,1.5) causal T-1; applied chỉ đổi khi |desired−applied|≥0.10.

NEXT (chưa làm): wire DT5G+VanB+deadband.10 vào f_system_daily.py live (xuất khuyến nghị vị thế VN30F). Liên quan [[dt5g_walkforward_event_audit]] (DT5G=fail-safe gate, edge OOS-tập-trung), [[8l_vn30_basket_backtest_2026]] (cổng DT5G nâng mọi rổ).
