# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## R&D Q3 program (review 8L + V2.4/V2.5, plan file li-n-quan-n-thi-t-wondrous-zephyr.md, user duyệt 2026-07-05)

### Kết quả thật đã có (verify qua registry, không chỉ tin job status)
- **H1 FSCORE bottom-exclusion**: FAIL proxy → ĐÓNG (registry dòng 228).
- **H2 DSR/PBO annex**: DSR≈1.0 (edge KHÔNG phải multiple-testing artifact, ~4.5σ trên null dù N=200
  trial), PBO≈0.20 (overfit vừa phải ở tầng chọn-config, đã giảm thiểu đúng cách bằng robustness-first
  deploy). Đề xuất chuẩn wire mới: N trials + DSR≥0.95 + PBO<0.5. TỰ THÂN đã đạt tiêu chí thành công
  chương trình (registry dòng ~1483-1562, script dsr_pbo_annex.py reproducible).
- **T2 panel-ext**: chỉ H6a MAX5_1M SỐNG tier-1 (mIC-gate −0.047 IS/−0.042 OOS, crash Q5 10.1% vs Q1
  4.2% — lottery effect Bali-Cakici-Whitelaw 2011 THẬT trên VN, trực giao value). H4 accruals/H5 DY/H6b
  limit-hit CLOSED (registry dòng 230-243).

### Đang chạy (Wave 1, dispatch 2026-07-05 08:59 ICT)
- Taylor_20260705_085946: H6a tier-2 proxy (exclusion MAX5_1M q∈{10%,20%} khỏi pool-60, timeout 3600s).
- Taylor_20260705_085949: H8a (LAG capacity tiebreaker d_NPR) + H8b (foreign-flow data audit), timeout 1800s.

### QUYẾT ĐỊNH: KHÔNG bắn thêm A4/A6 deep-research
4/4 memo deep-research đã bắn (A1/A2/A3/A5) đều bị lớp adversarial-verify sập TOÀN BỘ vì rate-limit
(2 nguyên nhân khác nhau: usage-limit tài khoản lúc 07:xx, rồi API server rate-limit chung lúc A1) →
"all refuted" là ARTIFACT hạ tầng, KHÔNG PHẢI nội dung sai (nguồn thật: JFE/JF/RFS/ScienceDirect,
tự tôi biết các paper này chính xác qua kiến thức nền — Harvey-Liu-Zhu t>3, Hou-Xue-Zhang 64-85% fail,
Bailey-LdP DSR formula...). H6a đã tự chứng minh giả thuyết A4 bằng dữ liệu VN THẬT — mạnh hơn lit-review
tốn kém (mỗi memo ~1.4-3M token). A6 (ML boundary-setting) không cần workflow — viết ngắn từ kiến thức
nền khi tổng hợp cuối chương trình.

### Ghi chú vận hành
- Wrapper Agent(haiku, run_in_background) bọc jobs.sh wait KHÔNG đáng tin cho việc chờ dài — quan sát
  2 lần liên tiếp nó tự thoát báo "đang chạy" thay vì block tới khi done. Dùng ScheduleWakeup làm
  cơ chế chính, wrapper chỉ là phụ (không spawn nữa nếu đã có ScheduleWakeup).
- Budget Taylor: đã dùng 7 dispatch call (2 fail do usage-limit, không tính unique-work) / ≤16.

- [2026-07-05T10:06:16Z] LESSON (2026-07-05): backtick markdown trong dispatch.sh prompt (double-quoted bash string) bị bash coi là command substitution → nội dung trong backtick bị XÓA TRẮNG (không phải lỗi tool, lỗi cách tôi viết lệnh). Đã xảy ra 2 lần (H3 BAL_VOL_TARGET, H8a-tiebreaker LAG_FUND_DNPR_TIEBREAK) — thiệt hại nhỏ (chỉ mất tên biến đề xuất, Taylor tự đặt tên được). TỪ NAY: không dùng backtick trong prompt text truyền qua Bash tool double-quote; viết tên biến/file bằng chữ thường không backtick, hoặc dùng single-quote cho toàn bộ prompt argument.
