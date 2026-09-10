# Structural-break protocol — khi HỆ SINH THÁI thị trường đổi, không phải khi backtest đổi

> Mở 2026-09-10 (AMH review, hướng #6 — user duyệt cả 7 hướng). Chủ: Mike.
> Bối cảnh: `kb/projects/amh-adaptivity-review-20260910.md` § gap G7.

## Vấn đề nó giải

DT5G và 8L cố ý **frozen theo LỊCH SỬ** — CLAUDE.md cấm re-tune theo lịch sử, và đó là luật đúng
(re-tune 8L đã NO-GO 16/16; DT5G tham số đang ở vùng bình ổn). Nhưng "đừng re-tune vì backtest nói
thế" **không đồng nghĩa** với "đừng bao giờ kiểm tra lại". AMH (Lo): lợi nhuận của một luật phụ
thuộc vào HỆ SINH THÁI người chơi. Khi hệ sinh thái đổi bằng một sự kiện CẤU TRÚC — không phải một
pha chu kỳ — thì mẫu lịch sử mà luật được hiệu chuẩn trên đó không còn mô tả cùng một thị trường.

Khoảng trống hiện tại: **không có gì kích hoạt việc kiểm tra lại theo SỰ KIỆN.** Nếu VN nâng hạng
FTSE/MSCI, hoặc hệ thống KRX đổi cơ chế khớp, hoặc chu kỳ thanh toán rút ngắn, thì hôm nay không có
cơ chế nào bắt ai đó phải hỏi "DT5G/8L còn đo đúng thứ nó tưởng mình đang đo không?".

## Nguyên tắc (đọc trước khi dùng bảng bên dưới)

1. **Trigger là SỰ KIỆN, không phải số liệu backtest xấu đi.** Backtest xấu đi là tín hiệu chu kỳ,
   xử bằng edge-health/gate. Chỉ sự kiện trong bảng mới mở protocol này.
2. **Protocol KHÔNG cho phép đổi tham số.** Nó chỉ bắt buộc **RE-VALIDATE** và bắt buộc **ghi lại
   kết luận**. Muốn đổi tham số vẫn phải đi đường cũ: prereg → backtest → quant-skeptic → user duyệt.
3. **Re-validate trước, kết luận sau.** Mặc định của mọi lần chạy protocol là "không đổi gì" — phải
   có bằng chứng mới lật được, không phải ngược lại.
4. **Fail-safe = giữ nguyên.** Nếu không kết luận được (dữ liệu sau sự kiện quá mỏng — thường là
   thế, vì sự kiện vừa xảy ra), thì GIỮ NGUYÊN và đặt lại mốc kiểm tra, KHÔNG đổi theo linh cảm.
   Dữ liệu sau một sự kiện cấu trúc luôn mỏng đúng lúc ta muốn dùng nó nhất — đó là bản chất, không
   phải lỗi thu thập.

## Danh mục sự kiện theo dõi

Registry máy đọc được: `kb/structural_break_watch.json` (trạng thái + nguồn phát hiện từng mục).

| Sự kiện | Vì sao đổi hệ sinh thái | Tầng phải re-validate |
|---|---|---|
| Nâng hạng thị trường (FTSE Secondary Emerging → Advanced; MSCI EM) | Vốn tổ chức/thụ động vào; giảm tỷ trọng lệnh cá nhân; breadth và tương quan đổi cấu trúc | DT5G (breadth guard PIT, ngưỡng state), custom30V (pool thanh khoản), CAPIT (%ADV) |
| Hệ thống KRX / đổi cơ chế khớp lệnh, biên độ, lô | Vi cấu trúc đổi ⇒ mọi thứ tính từ giá/khối lượng trong phiên đổi theo | fill model (trần %ADV/phiên), chase-cap, fill_timing HYBRID |
| Rút ngắn chu kỳ thanh toán (T+2 → T+1/T+0) | Sức mua, vòng quay vốn, và toàn bộ giả định "tiền về" đổi | `compute_active_nav`, plan funding gate, §25 field tiền, sizing |
| Luật margin / room margin toàn thị trường đổi | Đòn bẩy hệ thống là biến trạng thái ẩn của mọi episode hoảng loạn | `capit_margin_lever`, sleeve discretionary, mandate margin Loại-2 |
| Bỏ/nới giới hạn sở hữu nước ngoài (room ngoại) | Đổi tập tên đầu tư được và định giá tương đối của chính các tên đó | universe_pit, 8L (comp định giá), BAL/LAG pool |
| Sản phẩm mới quy mô lớn (phái sinh mở rộng, ETF quy mô, bán khống) | Thêm loài mới vào hệ sinh thái — chính là định nghĩa AMH của đổi chế độ | biodiversity gate, DT5G, edge-health toàn bộ |

## Checklist khi một sự kiện kích hoạt

1. **Ghi ngày hiệu lực THẬT** vào registry (ngày luật có hiệu lực/ngày vận hành, không phải ngày báo chí đưa tin).
2. **Đánh dấu mẫu** — mọi backtest chạy sau đó phải báo cáo tách "trước sự kiện / sau sự kiện", kể cả
   khi phần sau quá ngắn để kết luận. Ngắn thì nói là ngắn, đừng gộp im lặng.
3. **Re-validate đúng tầng ở cột 3**, không quét cả hệ (§23 coding_guidelines: theo phạm vi).
4. **Bobby (macro-strategist) đọc BLIND** — phân loại sự kiện trước khi ai đó xem forward return,
   đúng kỷ luật đã chốt 2026-08-24 để tránh đồng thuận sớm.
5. **Ghi kết luận vào registry + KB dù kết luận là "không đổi gì"** — im lặng không phân biệt được
   với chưa làm.

## Nhịp kiểm tra

Gộp vào **review quý của Bobby** đã có sẵn (`kb/current_ops.md` § Macro watch, next ~2026-11-26) —
KHÔNG tạo cron mới. Mỗi lần review quý, Bobby quét lại registry: mục nào chuyển từ `watching` sang
`triggered`, mục nào cần thêm. Lý do không cron riêng: trigger là sự kiện không định kỳ, một cron
theo lịch chỉ tạo thêm báo động rỗng — cái cần là một người đọc tin thị trường mỗi quý, việc đó
Bobby đang làm rồi.
