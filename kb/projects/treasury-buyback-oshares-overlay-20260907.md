# Treasury-buyback OShares PIT overlay — điều tra + quyết định (2026-09-07/08)

## Câu hỏi gốc
User hỏi vì sao Oshares suy từ `corporate_action` (AIS/ISS) không khớp `ticker_financial.OShares`
cho VRE. Điều tra bằng bảng mới `tav2_bq.treasury_news` (tạo 2026-09-04).

## Phát hiện chuỗi (3 vòng dispatch + 2 vòng quant-skeptic, tất cả CONFIRMED)
1. **VRE**: gap 56.500.000 cp (2,49%) = đợt mua cổ phiếu quỹ VRE+VHM hoàn tất 2019-12-19
   (`treasury_news` action_type=buy_done). `corporate_action` không có event code cho buyback
   (chỉ ISS/AIS cho TĂNG CP) nên model AIS không bao giờ trừ được lô này.
2. **Hệ thống, không riêng VRE**: `ticker_financial.OShares` cho ~150-176/1.290 mã (11-14%) bị
   vendor backfill/restate — giá trị quý lịch sử bị ghi đè bằng số "mới nhất biết", có case đổi
   TRƯỚC CẢ ngày công ty công bố ý định (không chỉ trước ngày hoàn tất).
3. Overlay `agents/Taylor/research/treasury_oshares_overlay_20260907/match_overlay.py` (v1→v2→v3,
   commit 8a891a5d→3c856e2a→1d28f339) neo ngày hiệu lực thật theo `treasury_news.public_date`.
   Kết quả cuối: **162 mã HIGH/MEDIUM, 14 SUSPECT, 29 unexplained** trên 232 candidate. Cả 2 vòng
   quant-skeptic verify đều CONFIRMED (v1 medium, v2 cao) sau khi vá bug đếm (161/13/28→162/14/29
   sai do file thiếu newline cuối) + sensitivity sweep ngưỡng SUSPECT_RATIO_PCT=15% (giữ nguyên,
   xác nhận qua tra tay 8+5 mã biên, không có natural break thống kê nhưng phân loại tay khớp).
   24-27 mã "thiếu" xác nhận là gap dữ liệu vendor thật (OShares NULL/0 lịch sử), không phải lỗi
   join. Data registry: `kb/data_registry/price-volume/treasury_news_buyback.md` (status PARTIAL).

## QUYẾT ĐỊNH CUỐI (2026-09-08, user chốt): KHÔNG WIRE VÀO PRODUCTION
Giữ overlay làm **công cụ tra cứu ad-hoc** (dùng khi cần đối soát 1 case cụ thể, như VRE lần này),
KHÔNG đưa vào `oshares_live.py`/`corp_action_lib.py`/`corp_action_daily.py`.

**Lý do (Mike phân tích, user đồng ý):**
- OShares chỉ nuôi ĐÚNG 1/3 thành phần composite v3 (`rating_8l.py`: `ps = Price×OShares/Rev_ttm`
  → sales_yield). Trụ chính "1/PE dominant factor" (IC +0,125) KHÔNG phụ thuộc OShares.
- Vấn đề chỉ nằm ở CỬA SỔ LỊCH SỬ bị gắn sai ngày hiệu lực (vài tuần/mã) — OShares hiện tại đã
  đúng, sống. Live trading không hưởng lợi gì; chỉ backtest đi qua đúng cửa sổ đó mới khác.
- Production đã có lớp fallback đối soát riêng (`oshares_pit.oshares_reconciled` + cờ
  `OSHARES_RECONCILE`) — wire thêm `treasury_news` (76% event thiếu `shares_delta`, 100%
  `ref_price` NULL, 24-27 mã gap) là thêm 1 trục "silent gap" mới vào hệ thống vốn đã nhiều tầng
  gate (MODEL_REBASE, AIS_UNCERTIFIED).
- Chưa ai đo được tác động thật lên xếp hạng/backtest — 3 vòng review chỉ dừng ở "cơ chế đúng,
  tái lập được", chưa tới "có tạo khác biệt nào đáng kể".

**Điều kiện mở lại**: chỉ đầu tư wire nếu tương lai có 1 case cho thấy sai lệch này thực sự đổi
quyết định đầu tư/backtest — lúc đó đo tác động cụ thể (so ranking có/không overlay) rồi mới quyết,
không wire "phòng khi cần" khi chưa đo được lợi ích.

## Artifact
- Research: `agents/Taylor/research/treasury_oshares_overlay_20260907/` (report.md §1-9,
  match_overlay.py, threshold_sensitivity.py, overlay_results.csv, oshares_timeseries.csv)
- Commits: `8a891a5d` (v1) → `3c856e2a` (v2, fix count bug) → `1d28f339` (v3, boundary tickers)
- Bus findings: `treasury-buyback-oshares-pit-overlay` / `-v2` / `-v3` (Taylor) +
  `verification` CONFIRMED ×2 (quant-skeptic, job `quant-skeptic_20260907_162132`/`_172518`)
