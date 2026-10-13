# FTSE nâng hạng — sự kiện cấu trúc ĐÃ KÍCH HOẠT (hiệu lực 2026-09-21)
> Mở 2026-10-13. Protocol: `kb/projects/amh-structural-break-protocol-20260910.md`. Registry máy đọc:
> `kb/structural_break_watch.json` (`ftse_msci_upgrade`, status `triggered`). Status: ĐANG RE-VALIDATE.

## Sự kiện
- FTSE Russell chuyển Việt Nam từ cận biên (Frontier) lên mới nổi thứ cấp (Secondary Emerging), hiệu lực
  **2026-09-21**; cổ phiếu vào rổ theo nhiều đợt tới khoảng 09/2027 (Bobby 13/10).
- **User chốt 2026-10-13 18:37 ICT (`decided_by: user`): "Ftse đã nâng hạng ngày 21/09"** ⇒ tính là sự
  kiện đã kích hoạt. Bobby chưa có nguồn đăng SAU 21/09 xác nhận đã thực thi (mọi nguồn ≤18/09, thì
  tương lai) — nguồn sau ngày đó vẫn cần bổ sung.
- MSCI: 06/2026 CHƯA đưa Việt Nam vào danh sách theo dõi ⇒ vế MSCI chưa kích hoạt.
- Nhãn gốc trong registry ("FTSE Advanced Emerging") không khớp sự kiện thật (Secondary Emerging); protocol
  viết "Secondary Emerging → Advanced". Lý do của protocol (vốn thụ động/tổ chức vào làm đổi hệ sinh thái)
  áp dụng cho sự kiện này nên vẫn mở protocol.

## Checklist protocol
1. ✅ Ngày hiệu lực thật đã ghi registry: 2026-09-21.
2. ✅ Đánh dấu mẫu: **mọi backtest chạy từ nay báo TÁCH "trước 2026-09-21 / từ 2026-09-21"**, kể cả khi
   phần sau quá ngắn (tới 13/10 mới ~16 phiên) — ngắn thì nói là ngắn, không gộp im lặng.
3. ⏳ Re-validate đúng tầng (KHÔNG quét cả hệ): DT5G (breadth guard PIT, ngưỡng state) · custom30V (pool
   thanh khoản) · CAPIT (%ADV). Giao Taylor 13/10 — kết quả ghi mục "Kết luận" bên dưới.
4. ⏳ Bobby đọc BLIND sự kiện (không forward return) — 13/10.
5. ⏳ Ghi kết luận vào registry + file này, kể cả khi kết luận là "không đổi gì".

## Nguyên tắc (nhắc lại từ protocol)
Protocol KHÔNG cho phép đổi tham số; chỉ bắt buộc re-validate + ghi kết luận. Không kết luận được vì dữ
liệu sau sự kiện mỏng ⇒ GIỮ NGUYÊN và đặt lại mốc kiểm. Muốn đổi tham số: prereg → backtest →
quant-skeptic → user duyệt.

## Kết luận
(chưa có — đang chạy)

## Chuyển từ `kb/current_ops.md` 2026-10-13 (nguyên văn)
**Review quý — next ~2026-11-26: dispatch Bobby refresh bảng lead indicators + quét
`kb/structural_break_watch.json`** (6 sự kiện cấu trúc: nâng hạng, KRX, T+, luật margin, room
ngoại, sản phẩm mới). Protocol: `kb/projects/amh-structural-break-protocol-20260910.md` —
sự kiện kích hoạt ⇒ BẮT BUỘC re-validate đúng tầng, mặc định vẫn là KHÔNG đổi tham số.
