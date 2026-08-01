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

**Follow-up: review vai trò FSCORE trong 8L — GIỮ NGUYÊN cả 2 tầng (2026-08-01, job
`Taylor_20260801_082823`, báo cáo `mike/agents/Taylor/research/fscore_role_review_20260801.md`,
artifact `data/fscore_review_20260801/`, Mike verify độc lập self-check + git-diff production
sạch).** User nghi ngờ FSCORE quá mạnh sau finding trên, đề xuất bỏ/nới nhánh FSCORE ở cổng VÀO
của CAPIT hoặc giảm trọng số trục FSCORE trong `core_score()` cho công ty tài sản nhẹ. Kết quả
NGƯỢC nghi ngờ ở cả 2 câu:
- **Cổng VÀO CAPIT** (`capit_basket()`, `FSCORE>=6`): mọi cách nới (bỏ hẳn, hạ ngưỡng, xác nhận
  2 quý theo đúng đề xuất của user, route qua 8L sector-aware) đều làm rổ CAPIT TỆ ĐI theo
  dose-response đơn điệu (−6,94pp đến +0,73pp tuỳ mức nới), 3/5 biến thể nới mạnh nhất giữ dấu
  14/14 LOO. Engine A/B: bỏ hẳn FSCORE thua trên MỌI trục kể cả MaxDD (−17,5%→−18,3%) — rổ rộng
  hơn không có nghĩa an toàn hơn, FSCORE đang loại đúng nhóm mã dễ sập. Đề xuất "2 quý liên tiếp"
  của user đã test đúng như phát biểu và vẫn thua (−3,06pp).
- **Trục FSCORE trong `core_score()` chung** (chỉ COMPOUNDER+CYCLICAL dùng, không có route
  RETAIL, POWER không dùng trục này — sửa lại brief ban đầu): trực giác "chỉ hợp tài sản nặng"
  đúng CHIỀU nhưng nhỏ, không có ý nghĩa thống kê (heavy−light IC chênh t=1,52 theo
  `FAsset_Eq_P0`, biến mất theo `FAssetTurn_P0` t=0,39). Nhóm tài sản NHẸ vẫn IC dương vững
  (+0,034, t=4,70, IS/OOS đều dương) — không mất sức dự báo.
- **Case DGC (capex Nghi Sơn) — giả thuyết "cùng gốc lỗi" với NCT/SAB BỊ BÁC**, ngược chiều dự
  đoán ở cả 3 lát cắt: nhóm capex nặng KHÔNG bị hạ FSCORE cơ học (61,0% vs 65,9% nhóm capex nhẹ),
  và sức dự báo của FSCORE MẠNH NHẤT chính ở nhóm capex nặng. Không bác luận điểm đầu tư riêng về
  DGC — chỉ bác việc khái quát hoá thành lỗi hệ thống.
- **Hoà giải với finding quality-exit ở trên**: không mâu thuẫn — cổng VÀO là so sánh CẮT NGANG
  giữa các mã (có tín hiệu thật, IC +0,179 trong pool CAPIT), cổng RA là so sánh CHUỖI THỜI GIAN
  trong 1 mã giữa kỳ hold (là nhiễu). Một chỉ số có thể vừa là tín hiệu cắt ngang vừa là nhiễu
  chuỗi thời gian cùng lúc.
- Không cần quant-skeptic (kết luận không đổi gì, không có thay đổi production). Lead còn mở,
  CHƯA làm: registry IC-panel-8L từng ghi FSCORE marginal là "ứng viên enhancer selection, chưa
  test trong custom30V" — đo lần này ủng hộ (+0,037 marginal) nhưng vẫn chưa test thật.
