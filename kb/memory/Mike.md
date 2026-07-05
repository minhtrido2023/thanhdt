# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## R&D Q3 program — ĐÃ KẾT THÚC (2026-07-05, plan file li-n-quan-n-thi-t-wondrous-zephyr.md)

### Kết quả cuối cùng (7 hypothesis + 1 audit, đã verify qua registry)
| # | Hypothesis | Verdict | Ghi chú |
|---|---|---|---|
| H1 | FSCORE bottom-exclusion | FAIL tier-2 | Value-rank đã hấp thụ sẵn edge trong universe cô đặc |
| H2 | DSR/PBO robustness annex | **PASS** | DSR≈1.0, PBO≈0.20 — edge KHÔNG phải multi-testing artifact. Đề xuất chuẩn wire mới N-trials+DSR≥0.95+PBO<0.5 |
| H4/H5/H6b | accruals/DY/limit-hit | CLOSED tier-1 | Không đạt ngưỡng marginal IC |
| H6a | MAX5_1M lottery-exclusion | FAIL tier-2 | Signal THẬT (+0.59pp cohort) nhưng redundant với value-rank — CÙNG cơ chế H1 |
| H7 | EVEB D&A_HEAVY route swap | FAIL tier-2 (bar cao) | Chỉ chạm ~4 tên/quý, quá mỏng |
| H3 | Vol-managed BAL exposure | FAIL harness | Cederburg 2020 OOS-failure tái hiện đúng trên VN — DT5G đã lo de-risk regime-tail |
| H8a (audit) | LAG capacity audit | Finding thật | Bind ~luôn (92.2%), đề xuất d_NPR tiebreaker (KHÁC hard-filter đã bác) |
| H8b | Foreign-flow data audit | CLOSED | Không có data trong tav2_bq |
| H8a-tiebreaker | A/B test đề xuất trên | **INCONCLUSIVE — infra fail 2 lần** | Code đã wire đúng (LAG_FUND_DNPR, OFF-default), nhưng backtest full-NAV không chạy xong trong turn-budget headless (2 lần, kể cả sau khi tránh concurrency). Backlog: cần phiên có timeout dài hơn/chạy tay. |

### QUYẾT ĐỊNH: CHƯƠNG TRÌNH DỪNG TẠI ĐÂY (đã báo cáo user 2026-07-05)
4 giả thuyết liên tiếp fail từ tier-2/harness (H1,H6a,H7,H3) = đúng ngưỡng PAUSE. Tiêu chí thành công
ĐÃ ĐẠT qua H2 (annex + chuẩn wire mới, độc lập không cần thêm gì). KHÔNG mở thêm giả thuyết mới,
KHÔNG bắn thêm A4/A6 deep-research. Backlog duy nhất: H8a-tiebreaker cần chạy lại (không phải research
work, chỉ là thực thi backtest đã sẵn code) khi có phiên rảnh/timeout dài hơn.

### Bài học vận hành rút ra (đã áp dụng, ghi lại cho lần sau)
1. KHÔNG bắn >1 deep-research workflow cùng lúc với dispatch Taylor headless (ăn chung usage-limit).
2. KHÔNG dùng backtick trong prompt text qua Bash tool double-quote (bash command-substitution nuốt mất).
3. KHÔNG dispatch 2 job Taylor cùng lúc nếu cả 2 sửa CÙNG 1 file production/harness.
4. Full-NAV backtest 2 lần chạy (baseline+treatment) contemporaneous có thể vượt turn-budget 1 phiên
   headless — cân nhắc tách baseline (cache lại) và treatment thành 2 dispatch riêng nếu cần.
5. Wrapper Agent(haiku, background) chờ job dài KHÔNG đáng tin — dùng ScheduleWakeup làm chính.

- [2026-07-05T14:42:42Z] H8a-tiebreaker ĐÃ ĐÓNG: LOO xác nhận CONFIRMED-LUMPY-DO-NOT-WIRE (drop 2021+2023 → treatment LOSES −1.53pp CAGR/−0.08 Calmar; drop 2024 → edge phồng +2.86pp = dấu hiệu overfit theo năm kinh điển). Env LAG_FUND_DNPR giữ OFF-default vĩnh viễn. Đang chạy verify_finding.sh (task bmm7t91zr) để quant-skeptic phản biện độc lập đóng vòng cuối. R&D Q3 program: mọi hạng mục đã xong (H2 chính thức hoá commit c27d967, H8a-tiebreaker đóng). Không còn việc mở.
