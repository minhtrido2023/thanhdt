# CAPIT margin — TẠM GIỮ: không duyệt ngày margin nào (mở 2026-10-13)
> User duyệt 2026-10-13 15:21 ICT (`decided_by: user`), topic Discord 1540662920889761883. Status: ĐANG GIỮ —
> từ 19:30 ICT cùng ngày giữ bằng CÔNG TẮC TỔNG (mục "Cơ chế đang chạy").

## Cơ chế đang chạy — công tắc tổng TẮT (user duyệt phương án D, 2026-10-13 19:30 ICT, `decided_by: user`)
- `data/trading_rules.json` → `capit_margin_lever.enabled = false` (WC `b33c1952`; chỉ 3 khoá đổi: cờ, dòng
  status, changelog; f / gate / gói vay giữ nguyên).
- Tác dụng ở HAI tầng: (1) SIZING — `golive_recommend_v23.py:1057` `_lever_active` đòi `enabled` ⇒ không plan
  nào sizing ×1,3 (đã chạy hàm `capit_lever_policy()` thật: enabled=False, err=None; mọi điều kiện khác đạt
  vẫn không active); (2) THỰC THI — `apply_capit_lever` mở lại file chính sách lúc đặt lệnh ⇒ không cấp cờ
  vay, gỡ cờ có sẵn (`capit_lever_selfcheck.py` C19/C20).
- Selfcheck sau đổi (trên main): `capit_lever_selfcheck` tất cả PASS (C20 đảo kỳ vọng theo trạng thái thật,
  WC `3dc35467`), park_rail_consistency OK (park 0,0 không đổi), strategy_fit_dashboard 93/0,
  nav_loss_brake_monitor 228/0, macro_killswitch_a 38, compute_park_trim 122/0.
- **Bật lại**: CHỈ khi user chỉ đạo tường minh. Thao tác: đổi `enabled` về true + đảo lại kỳ vọng C20 trong
  CÙNG commit + ghi changelog. **Trước khi bật lại phải xử lý lỗ hổng ở mục ⚠️ bên dưới** (thiếu bản duyệt
  margin không làm giảm khối lượng ×1,3) hoặc user chấp nhận nó bằng văn bản.
- Nhánh khoá bằng file giữ `feat/capit-margin-hold-lock-20261013` @ `0d0702856`: KHÔNG merge. Với công tắc
  tổng tắt thì không còn plan đòn bẩy nào để nó chặn ⇒ thừa; giữ nhánh làm tư liệu.
- Luật bằng chữ ở mục "Luật" dưới đây nay là lớp dự phòng (chỉ còn nghĩa nếu ai đó bật lại công tắc).

## Luật
Plan có lệnh CAPIT đòn bẩy (`loan_package_id` khác null) ⇒ Mike **KHÔNG chạy `bin/approve_plan_simple.sh`
như thường**. Từ 2026-08-22 script đó TỰ tạo margin approval ("duyệt plan = duyệt margin",
`approve_plan_simple.sh:173-194`). Trong thời gian giữ: hỏi user RIÊNG về margin, nói rõ đang giữ, chỉ
duyệt khi user trả lời riêng câu đó. **Khoá cơ học: user DUYỆT làm 2026-10-13 18:37 ICT** — nhánh mike
`feat/capit-margin-hold-lock-20261013` (Taylor, CHƯA merge tới khi arch-review APPROVED): file giữ mà
`approve_plan_simple.sh` + `approve_margin_day.py` kiểm, hỏng/không đọc được ⇒ coi như ĐANG GIỮ. Cho tới
khi nhánh đó merge VÀ file giữ được bật, luật bằng chữ ở trên vẫn là chốt duy nhất.

## ⚠️ KHÔNG duyệt margin CHƯA ĐỦ — plan đã sizing đòn bẩy vẫn nguy hiểm (phát hiện 2026-10-13 19:10 ICT)
Taylor đọc code + đo trên fixture (job `Taylor_20261013_114453`), Mike đọc lại xác nhận:
- Thiếu bản duyệt margin ⇒ `trading_bot/plan.py:1263-1271` chỉ GỠ cờ vay (`lever_f`, `loan_package_id`),
  **KHÔNG giảm khối lượng** (khối lượng đã sizing ×1,3 từ tầng plan — `plan.py:1336-1339`).
- Sau đó một trong hai: (a) tổng MUA vượt sức mua ⇒ `plan_funding_gate.py:392` BLOCK ⇒ `bot_execute.py`
  bỏ qua CẢ account (kể cả lệnh không đòn bẩy, kể cả lệnh BÁN); (b) đủ sức mua ⇒ mua ĐỦ khối lượng ×1,3
  bằng gói mặc định của account (chưa xác minh với DNSE gói đó có phải gói không vay).
- Hành vi này có từ TRƯỚC (mọi ngày thiếu bản duyệt margin đều vậy). Hôm nay chưa phơi nhiễm: lever không
  active (dd52 −10,7% > −20%), chưa plan nào sizing ×1,3.
⇒ **Trong thời gian giữ, nếu plan sizing đòn bẩy xuất hiện: KHÔNG duyệt plan đó. Báo user, lập lại plan
không đòn bẩy.** Chặn gốc đúng chỗ là tầng SIZING: `golive_recommend_v23.py:1057` chỉ sizing ×1,3 khi
`capit_margin_lever.enabled` = true (`data/trading_rules.json`) ⇒ tắt công tắc tổng là hết đường sinh plan
đòn bẩy. Đổi `trading_rules.json` là ranh giới cứng — CHỜ USER quyết (trình 13/10 19:1x).
Nhánh `feat/capit-margin-hold-lock-20261013` @ `0d0702856` (file giữ + 3 script, selfcheck 127/127) CHƯA
review, CHƯA merge — treo tới khi user chọn hướng.

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

## Chuyển từ `kb/current_ops.md` 2026-10-13 19:4x (nguyên văn 2 dòng bị thay)
## CAPIT margin TẠM GIỮ từ 2026-10-13 (user duyệt): plan có lệnh CAPIT đòn bẩy ⇒ **KHÔNG chạy `approve_plan_simple.sh` như thường** (nó tự duyệt margin), hỏi user RIÊNG; chỉ user gỡ: `kb/projects/capit-margin-hold-20261013.md`
- **CAPIT margin lever** (`capit_margin_lever.enabled=True`) — LIVE từ **2026-08-24**. Ngày có CAPIT margin phải chạy `approve_margin_day.py` TRƯỚC bot.
