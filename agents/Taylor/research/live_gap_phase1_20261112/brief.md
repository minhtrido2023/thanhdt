# GĐ1 — Thác nước gap backtest-vs-live trên cửa sổ 01/07→12/11/2026 (user DUYỆT plan 12/11/2026 17:40 ICT)
Plan gốc: kb/projects/bal-lag-live-gap-research-plan-20261112.md (§0, §2). Bạn làm GĐ1; GĐ0 (hurdle, book-sổ, fill-vs-open) chạy song song ở job khác, scope khác — đừng làm lại.
Skill bắt buộc đọc trước: .claude/skills/quant-research/SKILL.md (WC repo); tra mike/kb/data_registry/ trước khi chọn nguồn; universe_pit không dùng ticker_prune; profit_*/_center_* CẤM làm feature.

Khung: dựng WATERFALL pp NAV, mỗi bậc đổi ĐÚNG MỘT trục (luật §8c: pin_ledger.py compare từ chối ≥2 trục):
 W0 pt_v23_audit_2014.py cấu hình pin park 0 (PARK_STATES=3:0.0, BASKET_WT=namecap, BASKET_SELECT=yieldcombo, ETF_LIQ=custompitg), AUDIT_START=2026-07-01, AUDIT_END=2026-11-12, NAV_TOTAL_B=50
 W1 NAV_TOTAL_B=1 (vốn thật) · W2 + luật live-only (sàn ADV 2 tỷ, loại mã cờ/excluded_tickers, LAG DD-zone gate, CAPIT off) · W3 + lệnh tay thật (DRI/TV1/SCL bán, VGS/NNC/FPT mua) · W4 + fill thật (dnse_raw_*) thay close T+1 · W5 + tiền thật (egg ~79% NAV).
Mỗi bậc: NAV, lợi suất kỳ, chênh bậc trước (pp), kèm hurdle +2,70% và VN-Index −6,08% (01/07→11/11) cho tham chiếu. Làm cho từng account SpaceX và ZaloPay (ZaloPay tách DGC qua nav_sleeve_history_ZaloPay.csv). Dữ liệu live: nav_unit_ledger_<acct>.csv, nav_period_returns.py (đừng tự tính TWR).

TIỀN ĐỀ KỸ THUẬT — làm TRONG nhánh/worktree nghiên cứu cô lập, TUYỆT ĐỐI KHÔNG merge vào main, KHÔNG đổi cron/production:
 a) Engine không tất định theo AUDIT_END: sort_values không ổn định (regime_size_overlay.py ~dòng 47; bằng chứng: 48/153 tháng lệch giữa AUDIT_END 09-30 và 10-30). Vá bằng sort ổn định (kind="mergesort" + khoá phụ), chứng minh bằng chạy 2 AUDIT_END khác nhau → tháng chung phải giống bit-for-bit. Đây là đổi engine ⇒ CHỈ trong nhánh, báo rõ số pin cũ có đổi không.
 b) LAG cache sau 06-19 trộn cơ sở giá (fix chưa merge: kb/projects/lag-cache-adjusted-20261110.md, nhánh feat/lag-cache-adjusted-20261110). Dùng code nhánh đó để dựng cache điều chỉnh vào PT_WORKDIR RIÊNG (không ghi đè data/ production); nếu không dùng được thì loại LAG mã bị ảnh hưởng và NÊU RÕ phạm vi nhiễu. Merge production là quyết định user riêng — KHÔNG làm.
 c) Dữ liệu giá: ưu tiên snapshot tav2_pin.*_pin_YYYYMM / bq_cache_asof thay cache sống đã restate; ghi vintage dùng.
 d) Control leg: chạy lại đúng lệnh pin 23,37% (AUDIT_END=2026-06-19, bq_cache_asof20260729_postrestate) → phải tái hiện md5 ledger 4707bcbe (hoặc khai chênh) trước khi tin W0.
Ràng buộc: threads=1 (BQ_CACHE_THREADS=1), self-check 0 VND, N độc lập nêu rõ (live = 4 tháng, BAL live=1 deal: nói thẳng đây là MỘT mẫu), khai trials. Mỗi ledger mới ghi tên NON-canonical (_exp_gap_W<k>) — cấm ghi đè file pin (§8). Bậc nào không dựng được thì ghi "chưa đo", đừng ước lượng.
Cổng dừng theo plan: nếu gap chủ yếu ở W0 ⇒ nói rõ "thị trường/kỳ vọng"; W1–W2 lớn ⇒ "hệ live đã trôi khỏi hệ pin → cần re-pin V2.4-live"; W3 lớn ⇒ "kỷ luật/người". Chỉ báo kết luận cái đo được.
Kết thúc: ghi bus finding "live-gap-phase1-20261112" kèm REPORT.md (waterfall bảng+biểu đồ), md5 ledger, lệnh tái lập; cập nhật kb/memory/Taylor.md. Chưa wire gì; quant-skeptic sẽ phản biện sau.
