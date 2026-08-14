# 2026-08-13 — DNS ra ngoài chết trong cửa sổ hẹp 09:14-09:21 ICT, chặn cả đặt lệnh TV1 lẫn gửi email duyệt P0

**Bối cảnh phát hiện.** Retro `retro-2026-08-13.md` — 2 sự cố riêng biệt (khác agent, khác giao
thức) nhưng cùng cửa sổ giờ và cùng chữ ký lỗi, gộp 1 file vì cùng root cause hạ tầng.

## Triệu chứng

**#1 — TV1 không đặt được lúc mở phiên (09:21 ICT, cả 2 account).** Job dispatch ad-hoc
`Mafee_codex_20260813_022100` gọi `openapi.dnse.com.vn` để lấy quote trước khi đặt lệnh mua TV1
(SpaceX 1.800cp + ZaloPay 1.200cp, đã duyệt bởi John Dinh) — lỗi `failed DNS resolution in
execution environment`, quote fields trả về `None`. Bot fail-safe **từ chối đặt lệnh không giá**
(đúng thiết kế §5 idempotent side-effects — không đoán, không đặt lệnh mù).

**#2 — Email xin duyệt P0 (hybrid fill-timing, paper-only) không gửi được.** Job
`DollarBill_codex_20260813_021400` gọi SMTP để gửi — lỗi `SMTP DNS resolution failed (Temporary
failure in name resolution)`. DollarBill xử lý đúng: ghi rõ `NOT_SENT`, không suy diễn đã gửi,
chỉ retry khi DNS/SMTP sẵn sàng.

**Cùng cửa sổ giờ:** 02:14-02:21 UTC (09:14-09:21 ICT) — lệch nhau ~7 phút, khác agent
(`Mafee_codex_*` vs `DollarBill_codex_*`), khác giao thức đích (DNSE OpenAPI vs SMTP) nhưng cùng
1 loại lỗi (DNS resolution failure trong môi trường thực thi headless).

## Root cause

**Chưa xác định dứt điểm** — giả thuyết mạnh nhất (2 sự cố trùng khung giờ + trùng loại lỗi):
hạ tầng mạng/DNS dùng chung cho các job dispatch loại `_codex_` (headless, không phải luồng
`claude -p` chuẩn) bị flaky trong đúng cửa sổ 7 phút đó. Chưa có bằng chứng trực tiếp (log DNS
server, log network namespace) để xác nhận — chỉ có suy luận từ tương quan thời gian.

## Hậu quả thật (đã đối soát bằng artifact, KHÔNG phải bot đứng im cả ngày)

Bot **tự phục hồi một phần** sau sự cố — chu kỳ đặt lệnh chính retry lại sau 09:21 và khớp được:
- SpaceX TV1: **1.100/1.800cp (61%)**
- ZaloPay TV1: **600/1.200cp (50%)**

Xác nhận qua snapshot `positions` cuối ngày (20:30 ICT) — nguồn đối soát broker, không phải đếm
số request `place_order`. (Draft retro đầu tiên kết luận sai "0cp cả ngày" do grep nhầm đường dẫn
`mike/data/...` thay vì đúng `WorkingClaude/data/...` — Wags bắt lại lúc verify độc lập.)

Email P0: không có bằng chứng retry thành công riêng cho lần gửi này trong ngày — nhưng đây là
paper-only, không chặn vận hành thật.

## Còn hở — chưa làm

1. **Chưa xác nhận nguyên nhân hạ tầng gốc** (network namespace của job `_codex_` headless có gì
   khác các job dispatch thường không, tại sao chỉ 7 phút đó).
2. **Chưa có cơ chế retry/backoff riêng cho lớp job này** ở mức network — khác hẳn cơ chế
   usage-limit fallback đã có trong `dispatch.sh` (đó là tầng quota API, đây là tầng DNS/network).
3. **Chưa biết có tái diễn không** — mới 1 lần quan sát, cần theo dõi thêm trước khi đầu tư xây
   cơ chế phòng ngừa riêng (đúng nguyên tắc "quan sát tự nhiên trước khi tự động phục hồi").

## Bài học

Cả 2 lỗi đều **xử lý đúng theo thiết kế** (fail-safe, không đoán, ghi rõ trạng thái thật) — đây
không phải lỗi logic bot, mà là lỗi hạ tầng tạm thời được xử lý tốt. Giá trị của việc ghi lại: có
2 điểm dữ liệu cùng chữ ký lỗi trong cùng cửa sổ giờ — nếu tái diễn lần 3, đó là bằng chứng đủ
mạnh để đầu tư retry/backoff riêng cho lớp job `_codex_`.
