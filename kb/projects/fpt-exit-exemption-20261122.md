# FPT — MIỄN stop/TIME/TARGET cố định (user 22/11/2026 19:27 ICT, `decided_by: user`)

Nguyên văn: "(a) miễn stop. Discretionary sleeve không cần quy tắc thoát cố định. (B) Tôi tự quyết. (C) Cho phép bạn kiểm tra" (topic Discord "DD nâng cấp 22.11", trả lời thẻ FPT A1 v2).

## Đã làm (tôi, ngay sau quyết định)
- `data/discretionary_exit_rules.json` (repo ngoài, file ngoài git): gỡ 2 entry FPT (SpaceX + ZaloPay) ⇒ `auto_exit_inject` không còn đề xuất TARGET/STOP/TIME cho FPT. Bản gốc: `data/discretionary_exit_rules.json.bak_20261122_fpt_exempt` (khôi phục = chép lại 2 entry). Dry-run injector plan 23/11 cả 2 account: "không có candidate tới mốc exit"; selfcheck `auto_exit_disc` 99/0, `auto_exit_inject` 148/0.
- Plan nháp 23/11 (SpaceX 800cp / ZaloPay 500cp): chuyển lệnh `SELL-FPT-AUTOEXIT-DISC-STOP` từ `orders` sang `cancelled_orders` (chưa duyệt; bản gốc `plan_*_2026-11-23.json.bak_20261122_fpt`).
- Thoát FPT từ nay = user quyết thủ công. KHÔNG đổi: cổng giá −5% ∧ idio −4% + hồ sơ DD 7 ngày (`intraday_price_watch`, user quyết bán, mặc định giữ); LAG/BAL/CAPIT không liên quan FPT sleeve.
- NNC, VGS: GIỮ rule hiện hành (VGS user chọn phương án A 11/11, từng có sự cố wire nhầm phương án B) — chỉ đổi khi user xác nhận câu "quy tắc thoát cố định" áp cho cả sleeve hay chỉ FPT.

## Thẻ A1 + quét tin (user cho phép, 22/11)
Thẻ: `agents/Taylor/research/dd_upgrade_20261122/A1_fpt_thesis_audit/THESIS_CARD.md` (v2, skeptic REFUTED v1 → áp 9 đính chính). Quét legal-vn 01–22/11 (nguồn báo chí; chưa mở CBTT gốc HOSE/HNX/UBCK):
- FTEL: KHÔNG thấy tin thu hồi tài sản/điều tra/khởi tố/CBTT bất thường trong 01–22/11. Có chuyển giao vốn nhà nước FTEL: BCA nhận quyền đại diện (23/10), SCIC chuyển 370,7tr cp FOX (50,17%) cho BCA 31/10–28/11 (thủ tục cuối, không phải thu hồi). FPT FTEL 45,66%; FTEL trả cổ tức 2.000đ + thưởng 15% (GDKHQ 9/12).
- FOX chưa đủ điều kiện công ty đại chúng (CBTT 11/5/2026); chưa có quyết định hủy; UBCK sớm nhất ~05/2027 mới xét (suy luận, chưa đối chiếu Luật 56/2024).
- KQKD 10T/2026 (fpt.com 18/11): DT 44.959 tỷ +12,5%; LNTT 9.954 tỷ +16,8%; ký mới nước ngoài luỹ kế 40.130 tỷ **+20,8%** (≥ mốc +15% ⇒ chưa kích hoạt điều kiện hạ); Nhật +17,7% VND (+23,9% JPY) (≥ +15%); **riêng tháng 10 ký mới nước ngoài chỉ +~3%** (chậm lại: Vietcap/ACBS/VCBS: ký mới Q3 +~4% so +45% Q2; hợp đồng lớn hoãn dồn sang AI; JPY yếu; lo ngại AI vs outsourcing).
- Lý do báo chí cho đà giảm 12–20/11: khối ngoại bán ròng (đầu Q4 → 17/11 ~3.100 tỷ; 18/11 ~226 tỷ; 19/11 ~270 tỷ; room ngoại ~39% → ~25%), 27 quỹ bán ròng 16,7tr cp tháng 10, ký mới chậm, lo AI, JPY. KHÔNG bài nào gắn đà giảm với FTEL/điều tra/BCA.
- Lưu ý: phạm vi hợp nhất đổi (FTEL ghi nhận theo vốn chủ sở hữu từ 01/01/2026) ⇒ LNTT năm nay/cùng kỳ không cùng cơ sở.
Cập nhật cho thẻ A1: tiền đề "không có tin pháp lý mới" nhìn chung được tin công khai ủng hộ (chưa thấy bằng chứng ngược), nhưng nguồn là báo chí, chưa phải CBTT gốc.
