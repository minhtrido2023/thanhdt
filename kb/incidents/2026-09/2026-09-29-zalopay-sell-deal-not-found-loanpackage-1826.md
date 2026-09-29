# 2026-09-29 — `zalopay-sell-deal-not-found-loanpackage-1826`: 2.628 `PLACE_FAIL` HTTP 400 `deal not found` — lệnh BÁN gửi gói default account (1258) trong khi 6 mã chỉ có deal ở gói 1826

**Trạng thái:** CHẨN ĐOÁN XONG, **CHƯA VÁ** — root cause nằm trong `DNSEBroker.place_order`
(logic đặt lệnh = ranh giới CỨNG của Winston). Đã escalate bus question
`sell-loanpackage-deal-not-found-zalopay-20260929`.

## Triệu chứng
`data/execution_logs/exec_ZaloPay_2026-09-29_journal.csv`: **2.628 `PLACE_FAIL`**, 100% cùng một
note `HTTP 400: deal not found`, liên tục **09:15:08 → 13:30:26** (09h:702 · 10h:1038 · 11h:522 ·
13h:372, ~10 lượt/phút, chưa dứt lúc chẩn đoán). Cùng journal: 12 `PLACE` + 12 `FILL` + 9 `DONE`
thành công.

Chỉ **6 mã** fail: `HPG MSB SHB TPB VIX VRE` (đều `PARKMERGE-SELL-*`, sell 100cp/lượt).
9 mã bán trót: `BID CTG HDB LPB MBB TCB VCB VHM VPB`.

**KHÔNG có orphan/dup**: cột `child_oid` của mọi bản ghi fail đều RỖNG, và
`dnse_raw_2026-09-29.jsonl` (đã lọc `accountNo=0001743768` theo §12) chỉ có **12** bản ghi
`place_order` = đúng 12 lệnh thành công. Ngoại lệ bị ném trước khi `_log_raw` chạy ⇒ broker chưa
tạo lệnh nào.

## Root cause (đo, không đoán)
Phân hoạch HOÀN HẢO theo gói vay của deal đang mở (snapshot `positions` 13:31:07):

| Mã | `loanPackageId` của deal mở | Kết quả |
|---|---|---|
| CTG HDB LPB TCB VHM VPB BID MBB VCB | có deal **1258** | **PLACE OK 9/9** |
| HPG MSB SHB TPB VIX VRE | **CHỈ có 1826** | **400 deal not found 6/6** |

`trading_bot/brokers.py::place_order` — nhánh `else` (lệnh BÁN) đặt `lp = None`, nhưng dòng ngay
sau đó `lp_sent = lp if lp is not None else self._account_default_lp()` ⇒ **mọi lệnh bán vẫn mang
`loanPackageId` = gói default account**. Đo thật: cả 12 `place_order` hôm nay đều
`lp_sent=1258, lp=None`. DNSE tìm deal khớp gói 1258 ⇒ 6 mã kia không có deal nào ở 1258 ⇒ 400.

**Vì sao 6 mã đó ở gói 1826:** chúng được MUA ngày 2026-08-11 và nhánh BUY resolve gói **theo MÃ**:
`dnse_raw_2026-08-11.jsonl` ghi `['HPG',500,'buy',22200] lp=1826` (tương tự MSB/SHB/TPB/VIX/VRE).
⇒ **bất đối xứng**: BUY resolve gói per-symbol, SELL gửi gói default account. Deal sinh ra ở gói A
không bán được bằng gói B.

Đây là **tái diễn cùng LỚP** với `2026-08-10-funding-gate-multipackage-shared-pot-false-block.md`
§"SỰ CỐ THỨ HAI" (376 fail cùng note). Lần đó vá bằng cách cho lệnh BÁN `lp=None`; nhưng
cq-20260913 #1 đổi sang "truyền TƯỜNG MINH gói default account" ⇒ lệnh bán lại mang gói. Với
ZaloPay gói credentials = 1258 = đúng gói của mọi deal tháng 7 nên **latent** suốt 08-11→09-28;
2026-09-29 là ngày ĐẦU TIÊN park-trim chạm nhóm mã chỉ-có-deal-1826.

## Ảnh hưởng
- Plan ZaloPay 2026-09-29 (`approved_by=user`, 15 lệnh): **6/15 lệnh bán bị chặn cứng**, ~**9,77
  triệu VND** không huy động được (100cp × giá cuối: HPG 20.300 · SHB 11.450 · VIX 12.600 ·
  MSB 14.200 · VRE 24.500 · TPB 14.600). 9/15 khớp đủ.
- **Retry không có điểm dừng**: 400 là lỗi KHÔNG tạm thời, nhưng executor thử lại 2.628 lượt trong
  4h15. Tốn quota API và nhấn chìm log.

## KHÔNG sửa gì trong lần chạy này
Cả hai điểm cần vá đều nằm trong `trading_bot/brokers.py` / vòng retry của executor = ranh giới
CẤM của Winston (quy trình ops-autofix việc 3). Đã escalate + notify, không tự chạm.

## Đề xuất cho người sở hữu execution (Mafee/Taylor/user quyết)
1. Lệnh BÁN: resolve `loanPackageId` từ **deal đang mở của chính mã đó** (`positions[].loanPackageId`)
   thay vì gói default account; nhiều deal khác gói ⇒ chọn theo thứ tự bán mong muốn, hoặc gửi
   `None` thật (bỏ field) nếu DNSE tự khớp deal.
2. Thêm điều kiện DỪNG cho `PLACE_FAIL` mang lỗi cấu trúc (400 `deal not found`): fail-safe bỏ lệnh
   + báo người sau N lượt, không retry vô hạn cả phiên.
3. Có test phủ **CẢ HAI chiều lệnh** — đúng bài học đã ghi 2026-08-10 ("giả định phạm vi không được
   viết ra thành test"), lần này thêm ca "deal ở gói khác gói default account".
