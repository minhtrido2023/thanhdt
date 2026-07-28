# LAG 07-24 (IVS/TMG/TRC) — user chốt phương án C, chỉ mua TRC

> Archived 2026-07-28 từ kb/current_ops.md — quyết định bound tới 1 phiên giao dịch
> (07-24) đã qua từ lâu, mọi sub-item đều đã ĐÃ XONG/ĐÃ TRẢ LỜI/ĐÃ XÁC MINH.

## LAG 07-24 (IVS/TMG/TRC) — user chốt phương án C, chỉ mua TRC (2026-07-21)
Chuỗi điều tra hôm nay (job `Taylor_20260721_130404` + `_133858`) phát hiện: (a) đường live
LAG **thiếu trần %ADV** mà chính backtest R3 pinned đang giả định (≤20%ADV/phiên, ≤5 phiên,
huỷ nếu <30% filled) — lỗ hổng thật, chưa fix; (b) **TMG** `Volume_3M_P50=0` (ngoài
`ticker_prune`, ~20tr VND/ngày) → đóng góp ĐÚNG 0 vào backtest, mua live = ngoài mô hình; (c)
**IVS** (ICB 8777, CTCK) surprise +136,7% phồng cơ học do nền 2025Q4 lỗ, ROE_Trailing chỉ
1,89%, ADV 39% lệnh fleet, ngoài `ticker_prune`; PEAD nhóm CTCK edge trung bình cao hơn sản
xuất NHƯNG không dự báo được (IC=+0,051 p=0,35 vs manuf +0,136 p<1e-4) và chỉ là hiện tượng
kỷ nguyên 2020-24 bull/retail-boom (IS 2014-19 âm), 12m gần nhất đã âm. **User CHỐT: phương án
C — chỉ mua TRC ngày 07-24, bỏ IVS và TMG.** DollarBill lập plan riêng tối 07-23 — PHẢI áp
đúng quyết định này (không tự ý mua lại IVS/TMG theo tier gốc). Việc còn treo (chưa làm, cần
duyệt riêng): wire trần %ADV cho lệnh LAG trong `plan.py` mirror `cap_capit_orders`.

**✅ ĐÃ XONG 2026-07-22 (job `Taylor_20260721_162243`) — gate LAG %ADV LIVE + baseline được
đính chính.** (a) `trading_bot.plan.cap_lag_orders` đã COMMIT và wire VÔ ĐIỀU KIỆN trong
`bot_execute.py` (không feature-flag) ⇒ **ACTIVE từ phiên kế tiếp**, áp cho MỌI account
(SpaceX/ZaloPay/paper `main`). Cơ chế: trần 20%ADV/phiên chia đều theo số account live,
TRIM (phần dư tự mua tiếp phiên sau qua diff target-vs-thật), fail-CLOSED khi không đo được
ADV. Đo trên rổ 07-24: TRC trần 279tr/phiên (1 account) hoặc 140tr (2 account) — plan TRC
bình thường KHÔNG bị chạm; TMG sẽ bị CHẶN HẲN (ADV=0) nếu ai đó đưa lại vào plan.
(b) Baseline: engine backtest có lỗi cho phép mua TRỌN size mã `Volume_3M_P50<=0` (12,8%
vốn quay vòng LAG, nhóm này LỖ) — đã sửa (default OFF, canonical không đổi). A/B
contemporaneous **27,22% → 31,33% CAGR (+4,11pp)**, LOO 13/13 dương, quant-skeptic
CONFIRMED/high. ⚠️ **Số chính thức VẪN là 27,84%**; con số trung thực để kỳ vọng là **khoảng
[~27,2% ; 31,3%]**. Re-pin chuẩn còn chờ `data/bq_cache` trở lại `verified:true` (phụ thuộc
`ticker_prune` corruption còn treo). Anchor drawdown mới nên dùng ~−30% (bootstrap 5th-pct),
không phải −19%.

**✅ ĐÃ XONG 2026-07-22 (job `Taylor_20260721_172103`) — lọc thanh khoản LAG ở TẦNG TÍN HIỆU
(user quyết 2026-07-21), commit `4b7aaa1`.** `golive_recommend_v23.py` gọi `lag_filter_illiquid()`
(module mới `lag_liquidity_filter.py`) NGAY TRƯỚC bước chọn/xếp hạng ứng viên LAG ⇒ mã ADV≤0/
thiếu/cũ >30 ngày không còn thành mục tiêu, vốn tự chảy sang event LAG kế tiếp thay vì nằm im.
Phạm vi = **CHỈ book LAG** (đo thật: BAL đã có `liq>=1e9` cứng; CAPIT pool 0/26.277 dòng ADV≤0
+ `capit_adv_caps` fail-closed; PARK custom30V min ADV 13,1 tỷ). Self-check 13/13 offline +
19/19 live (TMG loại, TRC giữ); quant-skeptic **CONFIRMED/high** (`logs/verify_20260721_175346.log`,
sau 2 vòng REFUTED — cả 2 chỉ refute phần DIỄN GIẢI, code không đổi).

⚠️ **CON SỐ CAGR KỲ VỌNG: GIỮ NGUYÊN KHOẢNG [~27,2%; ~31,3%], KHÔNG chốt về 31,33%.** Lý do (quan
trọng, đừng bỏ qua): quant-skeptic đo được TREAT vào lệnh **+30,1%** nhưng vị thế HOÀN TẤT lại
**−16,3%**, tỷ lệ ABANDONED_REFUND **59,2% → 73,8%**. "Vốn chảy sang event kế tiếp" và "book không
fill nổi mã LAG ở quy mô 25B" để lại **cùng dấu vết CSV** — chưa tách được. Nếu vế sau đúng thì
+4,11pp là hiện vật mô hình fill, không phải edge. Bộ lọc vẫn đúng logic (không mua được thì đừng
đặt mục tiêu) nhưng **đừng dùng +4,11pp làm cơ sở kỳ vọng**. Số chính thức VẪN **27,84%**.

**✅ ĐÃ TRẢ LỜI 2026-07-22 (job `Taylor_20260722_030015`) — trần vị thế LAG.** Số đúng theo logic
production = **12**, nhưng KHÔNG phải tham số rủi ro độc lập — là nghịch đảo số học của tier
weight (LAG_HI 10%/LAG_LO 8% NAV book LAG ⇒ 1/0,09≈11,1⇒12 = "book đầy"). Cơ chế enforce THẬT là
TIỀN (`target_value = NAV_book × tier_weight`), không phải bộ đếm — trần đếm-tên và trần tiền là
dual của nhau. Con số "16-17" đo trước đó là ảo giác từ cổng rò (chỉ đếm vị thế ĐÃ hoàn tất, bỏ
sót lệnh đang khớp dở); đếm đúng theo size thật (≥4% book) ra **max 13 / p95 11** — khớp hằng số
12. **Kết luận: LIVE KHÔNG CẦN thêm trần cứng nào** — trần kinh tế đã bị ép bởi tiền, thêm
`MAX_POS_LAG=12` sẽ là code chết (không bao giờ bind trước ràng buộc tiền), chỉ tạo ảo giác an
toàn. Backtest đã vá cổng rò (`count_inflight_slots`, commit `f974459`, default OFF = byte-
identical, không cần quant-skeptic vì không đổi hành vi live).

**✅ ĐÃ XÁC MINH 2026-07-22 (job `Taylor_20260722_034554`) — `weight_base` KHÔNG có rủi ro thật,
ĐÓNG, không sửa gì.** Trace đủ 3 kênh tiêu thụ `weight_pct` LAG: hiển thị/telegram (đúng, có ghi
chú base), archive-BQ (trung tính, không nhân NAV), DollarBill (đúng — MD tự ghi rõ base 2 chỗ).
Bằng chứng thật: plan `SpaceX_2026-07-22.json` tính đúng LAG book ~463M = active_nav × w_lag_target,
không phải NAV tổng. Không có code nào khác đọc thẳng CSV rồi nhân NAV — thêm field sẽ chỉ gây
rối không cần thiết.

