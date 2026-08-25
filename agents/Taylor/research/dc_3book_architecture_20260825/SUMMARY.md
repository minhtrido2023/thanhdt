# SUMMARY — DC (Alpha Lens) 3-book architecture, giai đoạn 2

Job `Taylor_20260825_151108` (dispatch Mike). Câu hỏi gốc: có nên thêm DC làm book thứ 3
(1/3-1/3-1/3), và nếu không — có cấu trúc nào sáng tạo hơn V2.4 hiện tại không?

## Verdict tổng hợp

**KHÔNG thêm DC làm book thứ 3 tĩnh (1/3-1/3-1/3 mọi state).** Backtest thật (Phần A) bác bỏ trực
tiếp: CAGR FULL 27,05% vs baseline 29,33% (−2,28pp), MaxDD −19,9% vs −18,3% (xấu hơn), Calmar 1,36
vs 1,60. Pha loãng vốn vào 1 book có MaxDD tự thân cao hơn (ConvergePort chuẩn gốc −40,6%/−46,1%)
không được bù đắp đủ bằng phần CAGR tăng thêm.

**NHƯNG DC có alpha thật, không phải BAL diluted hay beta ngành thuần** (Phần B): naive Bank5
basket (không gate) BULL gross ≈ baseline parking (46,3% vs 45,3%), trong khi DC vượt xa cả hai
(64-69%). Double-confirm gate đóng góp alpha thật ~18-27pp trong BULL.

**Hướng đúng = state-conditional, không phải book cố định** (Phần C, C1 vs C2):
- C1 (chỉ swap LAG→DC trong BULL, giữ nguyên state khác): **+4,19pp/năm combined gross BULL** —
  cải thiện thật, khiêm tốn, đồng thuận cả 3 nguồn bằng chứng độc lập (Phần A gross table, Phần B
  factor-check, C1 phép cộng). **Đây là ứng viên backtest thật ưu tiên #1.**
- C2 (thay LAG hoàn toàn mọi state): **BÁC BỎ rõ ràng** — DC thua LAG ở NEUTRAL (−10,8pp) và
  EXBULL (−21,7pp), ÂM ở BEAR (−7,58%/năm). Không nên đề xuất lại hướng này.

**Kiến trúc sáng tạo nhất tìm được (C3.1)**: nghĩ về vấn đề như **ma trận factor×regime** thay vì
book cố định — không factor nào (BAL momentum / LAG PEAD / DC quality-value) thắng ở ≥4/5 state.
BAL dẫn NEUTRAL+BULL, LAG dẫn BEAR+EXBULL, DC dẫn CRISIS. Đây là bằng chứng CHỐNG LẠI cả "gộp về
1 book duy nhất" (C3.3, bác bỏ) LẪN "book thứ 3 cố định 1/3" (Phần A, bác bỏ) — hướng đúng là
**trọng số 3-factor thay đổi CHỦ ĐỘNG theo DT5G state**, tổng quát hơn cơ chế w_lag_tgt 1-tham-số
hiện tại của V2.4.

**Capacity không phải rào cản cho câu hỏi gốc** (C4): 4 mã Securities SSI/VND/VCI/HCM đều an toàn
(1,8-5,5% ADV cho vị thế full-cap ở 1/3 NAV). Nhưng phát hiện phụ quan trọng: **DHG và MSH** (2/16
tên DC universe) có capacity risk nghiêm trọng (890% và 205% ADV) — cần cap riêng nếu bất kỳ biến
thể DC nào được wire ở quy mô vốn thật.

## Recommendation — xếp hạng hướng đi tiếp theo

1. **Backtest thật C1 (state-conditional BULL-only swap)** — ưu tiên cao nhất. Cần: tích hợp vào
   allocator (w_LAG→w_DC chỉ khi state=BULL, giữ nguyên state khác), đo turnover cost thật của
   việc chuyển đổi qua lại (chưa tính trong phép cộng linear ở Phần C), walk-forward IS/OOS,
   DSR/PBO, quant-skeptic pass trước khi đề xuất wire — đúng pipeline `quant-research` skill.
2. **Khám phá C3.1 (state-adaptive factor rotation, ma trận đầy đủ)** — hướng dài hạn/tổng quát
   hơn, tiềm năng lớn hơn C1 nhưng RỦI RO CAO HƠN NHIỀU (thay đổi kiến trúc allocator sâu hơn, ma
   trận hiện tại chỉ là point-estimate 1 lần chạy, N mỏng ở CRISIS/EXBULL, chưa qua bootstrap/OOS
   stability check). Đề xuất: làm bước validate ma trận (bootstrap CI + OOS stability) TRƯỚC khi
   thiết kế allocator mới, tách thành 1 job riêng.
3. **Cap capacity riêng cho DHG/MSH** trong bất kỳ biến thể DC nào đi tiếp — sửa nhỏ, rẻ, nên làm
   cùng lúc với bước 1 bất kể hướng nào được chọn.
4. **KHÔNG theo đuổi**: C2 (thay LAG hoàn toàn), C3.3 (gộp về 1 book), 3-book tĩnh 1/3-1/3-1/3 —
   cả ba đều bị data bác bỏ trực tiếp trong job này.
5. **Hướng dài hạn, không ưu tiên ngay**: C3.2 (earnings-revision signal mới cho LAG trong BULL) —
   ý tưởng hợp lý về lý thuyết nhưng cần nguồn dữ liệu mới ngoài phạm vi BQ hiện tại, chi phí biên
   cao hơn hẳn C1.

## Giới hạn chung của toàn bộ job (đọc trước khi hành động)

- Tất cả kết quả là **point estimate từ 1 lần chạy**, chưa qua DSR/PBO/bootstrap CI — theo đúng
  §18 coding_guidelines, **KHÔNG được coi là đủ để wire production**. Bước tiếp theo bắt buộc qua
  `quant-research` skill đầy đủ + quant-skeptic CONFIRMED trước khi đề xuất đổi bất kỳ điều gì
  trong `pt_v23_audit_2014.py`/`trading_rules.json` thật.
- Phần A dùng band ±10pp CHỈ kích hoạt 4 lần/11,9 năm — bản chất gần như buy-and-hold tĩnh, KHÔNG
  phải mô phỏng đầy đủ độ phức tạp của allocator V2.4 thật (w_lag_tgt theo state, CAPIT arm,
  postbull mult...). Kết luận "3-book tĩnh thua baseline" đáng tin cho chính CÂU HỎI ĐÓ (1/3 tĩnh),
  KHÔNG suy rộng ra mọi cách tích hợp DC có thể có.
- r_DC dùng 2 quy ước khác nhau giữa Phần A/C (state-gated park) và Phần B (always-park,
  ConvergePort gốc) — có ghi rõ trong từng file, không lẫn lộn, nhưng người đọc cần chú ý khi trích
  dẫn số "gross DC BULL" ở đâu đó khác (43,64% state-gated vs 64,12% always-park).
- N mỏng ở CRISIS (443)/EXBULL (60) so với NEUTRAL/BULL (1799-1941/422) — kết luận cho 2 state này
  kém chắc chắn hơn, đặc biệt EXBULL (60 phiên, dễ bị chi phối bởi 1-2 giai đoạn cụ thể).
- Backtest chỉ dùng dữ liệu đã có sẵn local (BQ cache, CSV production) — không query BQ live mới,
  đúng ràng buộc "không tạo nguồn dữ liệu mới" ngầm định của 1 job R&D nhanh.

## File trong thư mục này

- `exp_dc3book_20260825.py` — Phần A backtest script (+ output `exp_dc3book_nav_3book_dc33.csv`,
  `exp_dc3book_metrics_3book_dc33.csv`)
- `exp_dc3book_factorcheck_20260825.py` — Phần B factor-check script (+ output
  `exp_dc3book_factorcheck_naive_bank5.csv`)
- `A_backtest_3book.md`, `B_factor_neutral_check.md`, `C_creative_alternatives.md` — chi tiết từng
  phần, đọc kèm caveat trong mỗi file trước khi trích dẫn số.
