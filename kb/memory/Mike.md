# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## R&D Q3 program — GẦN KẾT THÚC (plan file li-n-quan-n-thi-t-wondrous-zephyr.md)

### Toàn bộ kết quả Wave 0+1 (verify qua registry, không tin job status mù)
- H1 FSCORE-exclusion: FAIL proxy (registry L228).
- H2 DSR/PBO annex: PASS — DSR≈1.0 (edge KHÔNG phải multi-testing artifact), PBO≈0.20 (overfit vừa
  phải, đã kiểm soát đúng). Đề xuất chuẩn wire mới N-trials+DSR≥0.95+PBO<0.5 (registry L1483-1562).
  **Đây là thành công chính của chương trình, tự đạt tiêu chí thành công.**
- T2 panel-ext: chỉ H6a MAX5_1M sống tier-1 (registry L230-243); H4/H5/H6b CLOSED tier-1.
- H6a tier-2 (exclusion + soft-penalty): FAIL cả 2 vehicle — signal thật nhưng value-rank đã hấp thụ
  sẵn trong universe cô đặc (registry L245) — CÙNG CƠ CHẾ THẤT BẠI như H1.
- H7 EVEB D&A_HEAVY: FAIL bar cao (registry L247).
- H3 vol-managed BAL: FAIL toàn bộ harness — Cederburg 2020 OOS-failure tái hiện đúng trên VN, DT5G
  đã lo phần de-risk regime-tail nên overlay vol chỉ rỉ máu return giai đoạn vol-thường (registry L249).
- H8 audit: H8a LAG-capacity BINDS ~luôn (92.2% entry >12 tên đang giữ) → đề xuất d_NPR tiebreaker
  (KHÁC hard-filter đã bác); H8b foreign-flow ABSENT → CLOSED (registry L1572-1599).
- **H8a-tiebreaker: ĐANG CHẠY LẠI** (Taylor_20260705_110959) — lần đầu (Taylor_20260705_100258) báo
  done/exit0 nhưng KHÔNG có kết quả thật (chỉ để lại code wire dở `LAG_FUND_DNPR` env, OFF-default,
  logic đúng ý đồ verify bằng grep) — do dispatch song song 2 job cùng sửa pt_v23_audit_2014.py
  (H3 + H8a-tiebreaker cùng lúc) gây interrupt. **LESSON: KHÔNG dispatch 2 job Taylor cùng lúc nếu
  cả 2 sửa CÙNG 1 file production/harness — serialize hoặc tách file.** File hiện tại syntax OK,
  không bị corrupt, các env gate (VOLMANAGE_BAL, LAG_FUND_DNPR) đều OFF-default đúng.

### QUYẾT ĐỊNH: STOP sau khi H8a-tiebreaker xong (dù pass/fail)
4 giả thuyết liên tiếp fail từ tầng proxy/harness (H1, H6a, H7, H3) = đúng ngưỡng PAUSE của plan.
H8a-tiebreaker đã dispatch trước khi đếm đủ ngưỡng nên để chạy nốt, nhưng KHÔNG mở thêm giả thuyết
mới nào sau đó. Khi H8a-tiebreaker xong → chuyển thẳng sang Wave 3: viết synthesis "V2.4 đang ở
local optimum" (nếu H8a cũng fail) hoặc "+1 wire-able candidate" (nếu pass), trình user, KHÔNG bắn
thêm A4/A6 deep-research (đã quyết định trước), KHÔNG dispatch thêm hypothesis mới.

### Budget Taylor đã dùng: ~11 dispatch call thật (bao gồm 2 fail do usage-limit ban đầu + 1 job
chết do concurrency) / ngân sách ≤16.

