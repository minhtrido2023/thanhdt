---
kind: local-csv
status: RESEARCH-ONLY
source: mike/agents/Taylor/research/dt5g_ext_2008_20260904/dt5g_ext_2008_full.csv
group: market-state
aka: DT5G extended-to-2008 (research series)
writer: mike/agents/Taylor/research/dt5g_ext_2008_20260904/run_extended.py (Taylor, ad-hoc, NOT scheduled)
columns: time, state, state_dt4, cap, easing
---

# DT5G extended-to-2008 research series

**Status: RESEARCH-ONLY — KHÔNG dùng cho production, KHÔNG dùng để re-tune tham số.**

## Là gì
`get_macro_state(start='2008-01-01', end=<hôm nay>)` chạy với **tham số production nguyên vẹn**
(DT_10_25_25, macro thresholds, breadth_th=0.50/breadth_min_univ=100, BREADTH_SOURCE="pit") —
KHÔNG re-tune. Mục đích: tăng N_eff cho nghiên cứu conditional-theo-regime (2014+ chỉ có
8-10 đợt BULL / 9 đợt CRISIS). Job gốc: `Taylor_20260904_114556`.

## Gate đã PASS (bắt buộc trước khi tin bất kỳ số nào ở đây)
So 2014-01-02→2026-09-03 (3.158 phiên chồng lấn) với `tav2_bq.vnindex_5state_dt5g_live`:
**0 phiên lệch `state`.** Byte-identical. (`gate_check.py` trong cùng thư mục.)

## ⚠️ BẪY BẮT BUỘC ĐỌC — dùng phải nhớ TRƯỚC KHI dùng chuỗi 2008-2013
1. **`BQ_LOCAL_CACHE=data/bq_cache` (export sẵn trong `wc_env.sh`, kế thừa MỌI phiên đã source
   nó) âm thầm route `get_macro_state`/`simulate_holistic_nav.bq()` qua DuckDB cache** — cache
   này KHÔNG có bảng `universe_pit` (chỉ có `universe_pit_q`) và **cắt cụt lịch sử về 2013**
   (chạy `start='2008-01-01'` dưới cache trả về rows bắt đầu 2013-01-02, sai hoàn toàn, không
   báo lỗi rõ ràng ngoài 1 dòng cảnh báo breadth-guard-inactive). **Phải `env -u BQ_LOCAL_CACHE`**
   khi chạy bất kỳ nghiên cứu nào cần lịch sử pre-2014 qua `get_macro_state`/`simulate_holistic_nav.bq`.
2. **Macro overlay (Pillar A+B, phần MỚI của DT5G) chỉ thực sự "làm việc" ở 2 cửa sổ trong
   2008-2013**: 2008-07→2009-06 (cap=CRISIS 94,8% ngày, GFC — US panic + domestic) và
   2011-03→2011-11 (cap=CRISIS 100% ngày, lạm phát cao SBV refi→15%) — CẢ HAI khớp lịch sử thật.
   Các đợt CRISIS/BEAR khác (2009-12→2010-01, 2012-04→2012-10, 2013-03→2013-08) có `cap=9`
   (không có macro cap nào bắn) — nhãn CRISIS ở đó đến 100% từ **BASE `state_dt4`**
   (`tav2_bq.vnindex_5state_tam_quan_v34b_clean`, thuật toán v3.4b), KHÔNG phải từ phần mở rộng
   nghiên cứu này.
3. **Base v3.4b PHÁT HIỆN 1 false-positive CRISIS rõ ràng, đã verify bằng giá thật**: đợt
   CRISIS 2013-03-27→2013-08-22 (103 phiên) có giá VNINDEX **trung bình CAO HƠN MA200 12,4%**
   suốt cả đợt (Close dao động 462-528, MA200 417-453 — đi lên đều, không hề có drawdown thật).
   Đối chiếu: MỌI đợt CRISIS khác trong 2008-2013 đều có Close trung bình NGANG hoặc DƯỚI MA200
   (khoảng −36%..+2%) — đợt 2013 này là outlier rõ rệt (+12,4%), không giống bất kỳ đợt nào khác.
   ⇒ chất lượng bảng BASE pre-2014 **chưa được kiểm chứng độc lập**; ít nhất 1 lỗi cụ thể tồn tại.
4. **SBV_REFI_EVENTS (`sbv_macro_overlay.py`) tự ghi rõ**: "Pre-2014 entries are CONTEXTUAL —
   IC/backtest use 2011+ window only" + "some pre-2011 dates have ±1-2 month uncertainty".
   23/34 mốc SBV dùng cho Pillar A của giai đoạn 2008-2013 thuộc nhóm CONTEXTUAL này — bản thân
   tác giả overlay đã không khuyến nghị dùng backtest định lượng trước 2011.
5. **Universe `tav2_mike.universe_pit` (breadth guard) năm 2008 = 204 mã distinct/năm** (đo lại
   thật 2026-09-04, khác số 243 Mike nêu — do cách đếm distinct-per-year vs point-in-time-per-day
   khác nhau, không phải mâu thuẫn) — trên ngưỡng `breadth_min_univ=100` nên breadth guard
   KỸ THUẬT chạy được, nhưng CLAUDE.md đã cảnh báo thanh khoản tập trung ở ~50 mã đầu → % above
   MA200 trên đuôi kém thanh khoản 2008 đáng tin tới đâu là câu hỏi mở, KHÔNG kiểm chứng thêm
   trong lượt này.

## Kết luận sử dụng
- **Episode 2008-07→2009-06 và 2011-03→2011-11: dùng được** cho nghiên cứu conditional — macro
  cap tự bắn, khớp lịch sử thật (GFC, lạm phát 2011), không phụ thuộc chất lượng base pre-2014.
- **Mọi episode CRISIS/BEAR khác trong 2008-2013 (2009-12→01-2010, 2010-08→09, 2012-04→10,
  2013-03→08): KHÔNG nên dùng làm ground-truth regime label** cho tới khi ai đó kiểm chứng độc
  lập chất lượng base v3.4b trong giai đoạn này — đã có ít nhất 1 lỗi cụ thể xác nhận.
- Toàn bộ CSV vẫn giữ để tham khảo / tái kiểm; **không promote lên bất kỳ bảng BQ nào**.
