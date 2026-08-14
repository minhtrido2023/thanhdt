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

## Root cause — TẤT ĐỊNH, đã xác nhận + tái lập được (đính chính 2026-08-14, job `Taylor_20260814_003518`)

**KHÔNG phải hạ tầng DNS flaky.** Là hành vi TẤT ĐỊNH của sandbox `codex -s workspace-write` mà
`dispatch.sh` cố ý bật: **sandbox này tắt mạng theo mặc định** (`--unshare-net`,
`"network":"restricted"` trong permission-profile — xác nhận trực tiếp từ argv thật trong log,
`ps -ef` bên trong job `Mafee_codex_20260813_022100`).

Taylor tái lập ngay hôm sau bằng A/B một biến:

| Chân | Kết quả |
|---|---|
| Host, không sandbox | `103.151.242.24` ✅ |
| codex `workspace-write` (đúng argv `dispatch.sh` dùng) | `GETENT_FAILED rc=2` — **0ms** ❌ |
| + `-c sandbox_workspace_write.network_access=true` | `103.151.242.24` — 117ms ✅ |

**0ms là chữ ký DENY (chặn ngay lập tức ở tầng sandbox), không phải TIMEOUT** (timeout thật sẽ mất
hàng giây chờ hết hạn kết nối). "Cửa sổ hẹp 7 phút" trong bản đầu của file này là ẢO ẢNH quan sát:
`logs/` chỉ có 5 log job `codex` trong ngày, tất cả nằm trong 09:09–09:21, 3 job đầu chết TRƯỚC
KHI chạm mạng (lỗi khác) ⇒ "cửa sổ 7 phút" thực ra là TOÀN BỘ dân số job codex có chạm mạng hôm
đó — 2/2 hỏng, không phải 2/nhiều-hơn trong 1 khung giờ ngẫu nhiên.

## Hậu quả thật — KHÔNG có lệnh nào được đặt, KHÔNG có rủi ro tiền

Đọc trực tiếp log job `Mafee_codex_20260813_022100`: Mafee tự probe quote TV1, nhận đủ `last/ref/
bid/ask = None`, và **từ chối gửi lệnh mù** đúng thiết kế §5 (idempotent side-effects) — dòng kết
luận cuối log: *"Không đặt lệnh nào."* DNS-block ở đây **vô tình đóng vai trò bảo vệ** (chặn được
placement khi không xác nhận được giá), không gây thiệt hại.

**Nhưng lệnh vẫn khớp được sau đó** — chu kỳ đặt lệnh CHÍNH (không qua sandbox codex, chạy bình
thường qua đường production) retry lại sau 09:21 và khớp:
- SpaceX TV1: **1.100/1.800cp (61%)**
- ZaloPay TV1: **600/1.200cp (50%)**

Xác nhận qua snapshot `positions` cuối ngày (20:30 ICT) — nguồn đối soát broker, không phải đếm
số request `place_order`. (Draft retro đầu tiên kết luận sai "0cp cả ngày" do grep nhầm đường dẫn
`mike/data/...` thay vì đúng `WorkingClaude/data/...` — Wags bắt lại lúc verify độc lập.)

Email P0: không có bằng chứng retry thành công riêng cho lần gửi này trong ngày — nhưng đây là
paper-only, không chặn vận hành thật.

## Nghi vấn CHƯA GIẢI QUYẾT — job Mafee/DollarBill chạy qua codex, ngược với allow_agents

`kb/cli_providers.json`'s `codex.allow_agents = ["Taylor","Winston","Wendy","Spyros","Wags"]` —
**KHÔNG gồm Mafee/DollarBill**. `bin/cli_provider.sh`'s `validate` (tồn tại từ commit `be1bd7d5`,
2026-08-03, không đổi từ đó) đáng lẽ phải chặn (`exit 1`) bất kỳ dispatch nào cho 2 agent này qua
provider `codex`. Nhưng 2 job `Mafee_codex_20260813_022100` / `DollarBill_codex_20260813_021400`
đã CHẠY THẬT (đầy đủ session codex, CLAUDE.md được nạp đúng cơ chế `render_profile_prompt.sh`,
sandbox trỏ đúng `agents/Mafee` thật) — job_id có dạng `<id>_codex_<timestamp>`, KHÁC định dạng
chuẩn `${id}_${ts}` mà `dispatch.sh` hiện tại sinh ra. Quét cả `bus/jobs/` (hot + archive): **0**
job record nào có "codex" trong tên, dù có log `dispatch_<job_id>.log` — nghĩa là quy trình tạo
job record chuẩn của `dispatch.sh` (hàm `JSET`) KHÔNG chạy cho 2 job này.

**Chưa xác định:** đây là dispatch qua 1 phiên bản/nhánh khác của `dispatch.sh` (worktree, chưa
merge), một cách gọi thủ công mô phỏng lại cơ chế profile-prompt, hay lỗ hổng thật trong luồng
production hôm đó (đã tự đóng từ khi nào, hay còn tồn tại)? **Cần Mike/user xác nhận trực tiếp**
(nhớ lại đã tự tay dispatch bằng cách nào hôm 08-13, hoặc kiểm tra thêm reflog/lịch sử worktree)
— không suy đoán thêm chỉ bằng đọc code hiện tại, vì code hiện tại (đã verify 2026-08-14) chặn
đúng theo thiết kế cho input `id="Mafee"`/`id="DollarBill"` tường minh.

## Còn hở — chưa làm

1. **Xác nhận nguồn gốc 2 job `_codex_`** — xem mục trên, KHẨN vì liên quan tới cổng an toàn cho
   agent chạm tiền thật (Mafee) và kênh gửi ra ngoài (DollarBill email).
2. **KHÔNG xây retry/backoff** — đã bác bỏ theo phân tích 2026-08-14: lỗi tất định thì retry đập
   vào cùng 1 deny mãi mãi, chỉ tốn cửa sổ giao dịch. Đây là quyết định CẤU HÌNH (bật
   `network_access=true` cho lớp job cần mạng, hoặc không chạy job chạm tiền thật qua sandbox
   codex nữa), không phải quyết định kỹ thuật đơn thuần — cần user/Mike duyệt (§22).

## Bài học

**Đính chính quan trọng nhất:** đừng gọi lỗi tất định (sandbox network policy) là "hạ tầng flaky"
chỉ vì quan sát ban đầu trông giống flaky (2 lần trong 1 khung giờ hẹp). Bản thân file này (bản
gốc) là ví dụ sống của Pattern-B (§28 coding_guidelines.md) — tin biểu diễn (2 điểm dữ liệu trùng
giờ ⇒ "chắc là hạ tầng chập chờn") thay vì xác nhận artifact (argv sandbox thật + A/B tái lập).
Ngoài ra: Mafee vẫn xử lý đúng theo thiết kế bất kể lỗi hạ tầng gì (fail-safe, không đặt lệnh mù)
— đây là bằng chứng độc lập cho việc gate an toàn cấp-lệnh hoạt động đúng, tách biệt hoàn toàn
với câu hỏi CHƯA GIẢI QUYẾT ở trên về việc job đó có lẽ ra không nên chạy qua codex từ đầu.
