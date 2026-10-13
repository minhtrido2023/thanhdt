# CAPIT margin — TẠM GIỮ: không duyệt ngày margin nào (mở 2026-10-13)
> User duyệt 2026-10-13 15:21 ICT (`decided_by: user`), topic Discord 1540662920889761883. Status: ĐANG GIỮ.

## Luật
Plan có lệnh CAPIT đòn bẩy (`loan_package_id` khác null) ⇒ Mike **KHÔNG chạy `bin/approve_plan_simple.sh`
như thường**. Từ 2026-08-22 script đó TỰ tạo margin approval ("duyệt plan = duyệt margin",
`approve_plan_simple.sh:173-194`). Trong thời gian giữ: hỏi user RIÊNG về margin, nói rõ đang giữ, chỉ
duyệt khi user trả lời riêng câu đó. **Chưa có khoá cơ học** — đề xuất (chờ user): file giữ mà
`approve_plan_simple.sh` kiểm trước khi tự gọi `approve_margin_day.py`.

## Vì sao
Chi phí vốn tăng ngầm mà bộ lọc "khủng hoảng cơ cấu" của lever không thấy: `pit_deposit_threshold` 9%
đọc Big-4 12M online = 6,8% (`golive_recommend_v23.py`, cố ý Big-4-only theo quyết định 2026-10-01).
Số đo 13/10/2026:
- CCTG VPBank Super Thịnh Vượng tới 9,2% (ảnh app user 13/10 15:09 ICT; mệnh giá 100 triệu, 2 nguồn báo
  khớp số; 29/07 là 9,0%). MB 7,1% (6-9 tháng, bậc thường), ACB 7,2% (3 tháng) —
  `data/cctg_rate_vn_tier2_events.csv`.
- Trái phiếu vốn cấp 2 chào bán công chúng: VietinBank 6 năm +2,25 (12/2025: 8 năm +1,25, bán 55,5%);
  BIDV 09/2026 +2,25/+2,3 (bán 80,3%); BIDV 05/2026 +1,8/+1,9 (bán 36,9%).
- Tín dụng YTD 10,89% > huy động 9,78% (28/09, Cục Thống kê) — chênh +1,11pp (22/08: −0,4pp, phạm vi
  có thể khác).
- Lever hiện KHÔNG active (dd52 −10,7% > cổng −20%, `data/golive_v23_status.json` 12/10) ⇒ giữ không
  tốn gì.

## Đọc độc lập của Bobby (13/10, BLIND — không được cho biết nhận định của user/Mike)
CHƯA phải một episode. Nền = tích luỹ cơ cấu kiểu Loại 1, sớm-giữa, mức nhẹ, ambiguous ~55/45 (kỳ 30/09:
60/40). Tầng ngắn đã yên (qua đêm <3%, OMO lưu hành giảm gần nửa, tỷ giá yên, core CPI 4,45% giảm); tầng
dài vẫn đang định giá lại (biên trái phiếu cấp 2, liên NH 6-9 tháng 8,5-9%, lãi cho vay bình quân 9,12%).
Nợ xấu Q2 tăng tập trung ở Sacombank (77,7% mức tăng) — Bobby tự đính chính câu "NPL tăng tốc kiểu
2011→2012". Chi tiết + điều kiện đổi phân loại: `kb/data_registry/market-state/vn_macro_regime_history.md`
mục "REGIME READ #2". ⇒ Không có phân loại Loại 2 ⇒ theo mandate margin (2026-08-25) không có căn cứ gỡ.

## Gỡ khi
User xác nhận gỡ (tường minh). Mike KHÔNG tự gỡ.

## Liên quan
- Ngưỡng Macro Watch (6)(7) thêm cùng ngày: `kb/projects/vn-realestate-structural-risk-20260826.md`.
- Bảng ngưỡng lãi suất × PE đo 12-13/10 là MÔ TẢ (số đợt độc lập 2-5 mỗi vùng, ~40 ô chưa hiệu chỉnh đa
  kiểm định), KHÔNG phải cổng: lãi CCTG-tương-đương <7,5% không ảnh hưởng PE; 7,5-8% trần PE ~17; ≥8%
  trần ~14; ≥9% PE trung vị ~9,7 (chỉ 2011-13). Script tạm ở /tmp, CHƯA lưu repo, chưa qua quant-skeptic.
