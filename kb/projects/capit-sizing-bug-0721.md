# CAPIT sizing bug 07-21 — ĐÃ ĐÓNG (2026-07-31)

> Tách ra khỏi `kb/current_ops.md` 2026-08-01 (token-cost review) — mục này đã ĐÓNG từ 07-31,
> giữ nguyên full rationale vì có quyết định discretionary quan trọng (không bù tiền thiếu) mà
> user tự đưa ra 4 căn cứ cụ thể, có giá trị tham chiếu tương lai cho case tương tự.

**Đã đóng 2026-07-31, job `Taylor_20260731_154624`+`_155814`, commit `53cb117`/`d3aa3f05`.**
Phát hiện: plan SpaceX 07-21 nhân `capit_size` HAI LẦN (đọc nhầm cột `weight_pct` đa nghĩa) →
deploy 254,4tr thay vì đúng 348,4tr theo booknav, thiếu 87,1tr (ghi chú cũ sai lầm quy hết cho
"rounding lots", thực ra rounding chỉ giải thích 6,8tr). ZaloPay không bị lỗi (đọc đúng cột).

**Đã fix gốc**: `golive_recommend_v23.py` publish sẵn `capit_slot_targets` (VND/slot từng
account) để tầng plan copy thẳng không tự lắp công thức; CSV thêm cột `weight_base` làm rõ mẫu số
từng book; `send_plan_report.sh` đối chiếu Σ lệnh CAPIT vs mục tiêu ở bước duyệt 21:00 (WARN-only,
ngưỡng 10% — **gate này vẫn LIVE**, mỗi lần duyệt plan có CAPIT order). Self-check 24/24 PASS,
Mike verify độc lập cả 2 commit.

**User CHỐT: KHÔNG bù phần 87,1tr thiếu cho SpaceX** (phương án C) — 4 căn cứ: (1) rổ hiện
−1,15% từ 07-21 nên thiếu tiền vô tình tránh lỗ, không phải thiệt hại cần bù; (2) điều kiện kích
hoạt CAPIT hôm nay đang tắt (`capit_size=0`), bù = quyết định discretionary mới không nằm trong
rule nào; (3) đúng 2/5 mã (NCT, SAB) đã rớt sàn chất lượng của chính rổ CAPIT và cũng là 2 mã
giảm sâu nhất; (4) LAG book chung sổ đã oversubscribe, không có ngân sách thật.

**Việc R&D mở, chưa làm** (không sửa nóng giữa episode đang mở): CAPIT hiện không có cơ chế
quality-exit khi 1 mã rớt sàn chất lượng sau khi mua (chỉ hold cố định 60 phiên) — NCT/SAB là ca
thật đầu tiên để khảo sát, cần backtest riêng trước khi cân nhắc thêm cơ chế này.
