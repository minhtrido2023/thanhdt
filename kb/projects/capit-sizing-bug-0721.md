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

**R&D quality-exit — ĐÃ KHẢO SÁT (2026-08-01, job `Taylor_20260801_073610`, báo cáo
`mike/agents/Taylor/research/capit_quality_exit_20260801.md`, artifact `data/capit_qexit_20260801/`).**
Kết luận: **GIỮ NGUYÊN production, không thêm cơ chế thoát sớm.** Lưới 24 chiến lược (bán ngay /
bán sau K phiên / trim 50%, theo 4 metric rớt-sàn khác nhau) đều ≤ baseline ở tầng vị thế (N=85 vị
thế / 14 sự kiện / 11 quyết định thật), và 4/4 leg engine đầy đủ đều ≤ control ở tầng danh mục
(CAGR/Sharpe/Calmar), MaxDD giống hệt −17,5% ở cả 5 leg — không mua được bảo hiểm rủi ro nào. Root
cause: "rớt sàn chất lượng" trong cửa sổ hold 60 phiên gần như 100% do FSCORE (nhiễu kế toán quý,
0/85 vị thế thật sự vi phạm golden floor ROE_Min5Y/ROIC5Y dài hạn) — bán ở đó = hiện thực hoá đáy
(giữ tới hết +13,7% vs bán tại ngày cờ +2,7%, bỏ lại ~11pp). **Đối chiếu case NCT/SAB**: cả hai chỉ
rớt vì FSCORE, KHÔNG rớt theo ROE/ROIC/8L rating — 8L (cổng chất lượng chuẩn của hệ) vẫn xác nhận cả
hai đạt, nên căn cứ (3) ở trên ("2/5 mã rớt sàn chất lượng") cần đọc lại: đúng về mặt cờ FSCORE,
nhưng KHÔNG phải suy giảm chất lượng dài hạn — không đổi kết luận không-bù, chỉ làm rõ cơ chế.
Mẫu nhỏ (sign test p=0,549 không có ý nghĩa tần suất; bootstrap+LOO có ý nghĩa về độ lớn, nhưng
tầng danh mục kém sạch hơn — năm 2025 gánh gần hết hiệu ứng âm). Code: knob `CAPIT_QEXIT`
env-gated default OFF trong `pt_v23_audit_2014.py`/`simulate_holistic_nav.py`, production
byte-identical, KHÔNG wire.

**quant-skeptic verify: CONFIRMED, confidence high** (2026-08-01, verdict trên bus trace_id
`Taylor_20260801_073610`). Recompute độc lập khớp 24/24 ô lưới + case NCT/SAB (FSCORE 6→3/6→5,
ROE/ROIC bất động, 8L rating ≤3 suốt) trực tiếp từ parquet cache — không dùng lại số Taylor báo
cáo. Xác nhận `capit_basket()` entry-gate SQL byte-identical với Python re-implementation của
metric `floor` (không lệch ngưỡng thật-vs-thử). Không look-ahead (floor/8L point-in-time,
full-exit route qua T+1 Open giống cơ chế TIME/STOP có sẵn; trim same-day mark bias LỢI cho
treatment, không thể tạo ra underperformance báo cáo). Killer objection duy nhất: con số −0,35pp
CAGR tầng danh mục không bền theo năm (2025 gánh gần hết) — nhưng khuyến nghị "không đổi gì"
không phụ thuộc số đó, đã đứng vững một mình trên kết quả tầng vị thế (28/28 cấu hình ≤ baseline,
MaxDD giống hệt mọi leg). **Chấp nhận là tri thức chốt của fleet.**
