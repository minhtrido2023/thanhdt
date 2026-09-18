# 2026-09-18 — Bộ dò "ỨNG VIÊN RETRY" của check 5b chỉ vào HEARTBEAT của watcher, che mất bản retry thật

**Phát hiện:** `ops_health_check.sh --account ZaloPay` (01:20Z) báo 1 bản ghi cách ly trong 24h
(agent `Wags`, 17 tham số), kèm ứng viên retry `Wags/…17:40:04Z → 17:40:21Z event 755b7de9
topic Wags_20260917_173519`. Dispatch tới Winston qua `ops_autofix` (job `Winston_20260918_012009`).

## Sự thật: KHÔNG mất event — nhưng ứng viên checker chỉ ra là SAI event

Bản ghi bị chặn: `finding` của Wags, topic `retro-2026-09-17-independent-verify-CONFIRMED`,
trace `Wags_20260917_173519`, ts `2026-09-17T17:40:04Z`. Nguyên nhân chặn là **word-split THẬT**
(argc=17): payload bọc nháy ĐƠN mà bên trong có `'` (`…su co ban nhap da liet 'ke'`) ⇒ bash cắt
argv[3] giữa chừng, các mảnh còn lại trôi thành argv[4..15]. Call site là lệnh Bash ad-hoc của
agent ⇒ không có script committed để vá.

Wags tự ghi lại **+24 giây**: event `10d9cf98-6e79-4d0c-8f0f-4161aacaed2d` (`17:40:28Z`), CÙNG
topic, CÙNG trace_id, nội dung khớp nguyên vẹn (verdict CONFIRMED, scope, 5 khoá `checks`,
`minor_note`). Ca **14/14** liên tiếp tự lành ≤60s. Đã đánh dấu sidecar (index 15).

Nhưng event mà checker in ra là `755b7de9` (`17:40:21Z`) — **heartbeat của watcher**
(`event_type=heartbeat`, `payload.source=watcher`, `topic = trace_id`), không phải bản retry.

## Lỗi THẬT: `break` ở ứng viên ĐẦU TIÊN, và heartbeat luôn khớp trace_id

Watcher phát heartbeat mỗi ~5 phút cho mọi job đang chạy, với `topic = trace_id`. Vì vậy trong
cửa sổ 15 phút sau một bản ghi bị chặn, heartbeat **luôn** khớp điều kiện `trace_id == _tr`, và
thường đến TRƯỚC bản retry thật vài giây. Vòng quét cũ `break` ngay ở event khớp đầu tiên ⇒
heartbeat che mất finding thật.

Hai hệ quả, mức độ khác nhau:
- Nhẹ (ca này): có retry thật nhưng checker trỏ nhầm ⇒ autofix phải tra lại từ đầu, đúng thứ
  công việc mà khối ứng-viên-retry sinh ra để tiết kiệm.
- Nặng (chưa xảy ra nhưng cùng code): event MẤT THẬT mà job vẫn còn chạy ⇒ heartbeat một mình
  đủ để checker khẳng định "nhiều khả năng agent đã TỰ ghi lại" — báo yên tâm giả.

Hình thái thứ **5** của cùng một lớp lỗi "checker tra cứu/so sánh bằng bằng chứng YẾU rồi khẳng
định kết luận mạnh" (§28/§29 coding_guidelines): 5b 08-21 (quy chụp word-split), check#9 08-25
(hardcode quoting bug), guard JSON 08-28 (đoán nguyên nhân), 5b 08-31 (đọc trace_id ở argv[4]),
và lần này.

## Fix — commit `<HASH>`

`bin/ops_health_check.sh` khối 5b: bỏ `break`-ở-ứng-viên-đầu-tiên, đổi thành **chấm điểm rồi lấy
tốt nhất**; loại thẳng `event_type == "heartbeat"`; topic khớp = 2 điểm (bằng chứng mạnh hơn
trace_id vì trace_id dùng chung cho cả job), cùng `event_type` với argv[1] = +1 điểm.

`bin/ops_health_check_rejected_selfcheck.py`: +2 assertion dựng lại đúng hình dạng 09-17
(heartbeat đứng trước retry thật ⇒ phải chỉ ra retry thật; CHỈ có heartbeat ⇒ KHÔNG được coi là
ứng viên). Mutation test trên `git show HEAD:bin/ops_health_check.sh`: cả 2 assertion mới FAIL
trên bản cũ (giết đúng bug), toàn bộ selfcheck PASS trên bản mới ở 4 TZ + `env -u TZ`.
