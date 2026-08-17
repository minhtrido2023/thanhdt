# 2026-08-17 — `ops_health_check` check #5 dispatch job Wags cho câu hỏi mới 4 phút 31 giây tuổi

**Phát hiện:** job `Wags_20260817_020616` (wags_autofix `coord-2026-08-17`, model Opus), dispatch
bởi một lượt chạy `ops_health_check.sh --account SpaceX` với nội dung "⚠️ Có 1 câu hỏi (question)
trong 48h qua CHƯA thấy answer tương ứng: ['Taylor/hybrid-fill-live-deadline-20260817']".

## Timeline thật (giờ UTC, dựng từ `bus/inbox/*.jsonl` + `bus/jobs/*.json`)

| Giờ | Sự kiện |
| --- | --- |
| 02:00:06 | Mike dispatch `Taylor_20260817_020006` — hỏi về "deadline 17/08" của hybrid fill-timing |
| 02:01:45 | Taylor đăng `question` `hybrid-fill-live-deadline-20260817` (chính là kết quả của dispatch trên: "KHÔNG có deadline thật vào 17/08, text cũ đã superseded") |
| 02:06:15 | Một lượt `ops_health_check` chạy TAY thấy câu hỏi đó "chưa có answer" → dispatch job Wags |
| 02:06:56 | **Mike đăng `answer` đóng đúng topic đó** |

Câu hỏi bị đánh cờ "bị bỏ rơi" sau **4 phút 31 giây**, và được trả lời **41 giây sau khi** job
Wags bị dispatch. Toàn bộ job là false alarm — không có gì để sửa ở phía điều phối.

## Root cause

Check #5 phân loại question theo BẢN CHẤT (tự-sinh bởi wags_autofix → WARN-ONLY; đã có ack
`triaged-needs-human:` → WARN-ONLY; còn lại → routable) nhưng **chưa bao giờ xét TUỔI** ở nhánh
routable. Điều kiện dispatch thực tế là "tại thời điểm quét chưa thấy answer" — một BIỂU DIỄN tức
thời — chứ không phải "đã có đủ thời gian trả lời mà vẫn im", là sự thật bền cần kiểm. Đúng họ
Pattern-B §28 `kb/coding_guidelines.md`.

Vì sao đến hôm nay mới cắn: cron chỉ chạy 2 lần/ngày (01:20 + 05:45 UTC) nên xác suất trùng vào
khoảnh khắc fleet đang trao đổi rất thấp. Hôm 08-17 `ops_health_check` được chạy TAY **5 lần trong
6 phút** (02:01:48, 02:06:15, 02:06:33, 02:07:17, 02:07:34) chồng lên đúng lúc Taylor đang trả lời
dispatch của Mike ⇒ cửa sổ đua mở ra.

Không phải lỗi Taylor (dùng `question` cho phần cần user quyết là đúng quy ước) cũng không phải
lỗi Mike (đã trả lời trong 5 phút). Lỗi nằm ở checker.

## Fix (commit `<xem git log>`, 2 file)

- `bin/ops_health_check.sh`: thêm `QUESTION_GRACE_MIN = 60`. Câu hỏi mới hơn ân hạn vào
  `pending_q_fresh` — **vẫn in ra báo cáo** kèm marker `[WARN-ONLY]` (không im lặng, không xoá
  khỏi tầm mắt), chỉ không rơi vào `COORD_WARN` nên không kéo dispatch. Nhánh `✅ không có câu hỏi
  nào đang chờ` phải kiểm thêm `not pending_q_fresh` — nếu không, "hoãn dispatch" biến thành "báo
  sạch", đúng thứ mọi comment khác trong check #5 đang chống.
- Ân hạn đặt SAU 2 nhánh phân loại bản chất: tuổi không được ghi đè phân loại.
- Vì sao 60 phút không mất ca nào: cron cách nhau 4h25/19h35, câu hỏi thật sự bị bỏ rơi vẫn được
  bắt ở lượt kế tiếp, thừa sức trong cutoff 48h.

## Verify

- `bash -n` OK; `bin/ops_health_check_selfcheck.py` toàn bộ PASS (2 ca mới: 8b, 8c — 5 assertion).
- **RED control 2 chiều** (bắt buộc, xem bài học round-5 08-12): `QUESTION_GRACE_MIN=0` → 2
  assertion ca 8b ĐỎ; `QUESTION_GRACE_MIN=999999` → 2 assertion ca 8c ĐỎ. Chỉ pin một chiều thì
  đặt ân hạn = ∞ vẫn xanh trong khi kênh escalate chết im.
- Dry-run trên bus THẬT (`OPS_HEALTH_DRY_RUN=1 ... --account SpaceX`): `✅ Không có câu hỏi nào
  đang chờ xử lý trong 48h qua` — không regression.

## Không đụng

`bin/bus_question_audit.py` (sibling port cùng thuật toán MATCH) cố ý giữ nguyên: nó là báo cáo
đọc-only, liệt kê câu hỏi mới là ĐÚNG. Ân hạn là ràng buộc của kênh DISPATCH, không phải của
matcher — thêm vào đó sẽ làm audit giấu bớt câu hỏi thật.
