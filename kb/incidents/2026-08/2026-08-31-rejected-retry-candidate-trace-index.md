# 2026-08-31 — Bộ dò "ỨNG VIÊN RETRY" của check 5b đọc trace_id ở SAI vị trí ⇒ khẳng định "event MẤT THẬT" cho đúng ca word-split

**Phát hiện:** `ops_health_check.sh --account ZaloPay` (05:45Z) báo 1 bản ghi cách ly trong 24h
(agent `Taylor`, 13 tham số) kèm câu *"KHÔNG tìm thấy ứng viên retry nào trên bus trong 15 phút
sau đó — khả năng cao event MẤT THẬT, phải dựng lại nội dung từ argv rồi ghi lại."* Dispatch tới
Winston qua `ops_autofix` (job `Winston_20260831_054504`).

## Sự thật 1: KHÔNG mất event, và ứng viên retry NẰM NGAY TRONG cửa sổ 15 phút

Bản ghi bị chặn: `finding` của Taylor, topic `vn-jul2026-margin-forced-selloff-case-20260831`,
trace `Taylor_20260831_042737`, ts `2026-08-31T04:34:58Z`. Taylor tự ghi lại thành công **+42
giây** — event `2ceafcdb-ee4d-4d73-b304-54046ae5e9cf` (`04:35:40Z`), **cùng topic, cùng
trace_id**, đủ nội dung (8 key top-level, `external_check`/`breadth_and_volume_signature`
nguyên vẹn). Ca thứ **9/9** liên tiếp tự lành ≤54s. Đã đánh dấu sidecar (index 10).

Nguyên nhân bị chặn lần này ĐÚNG là word-split thật (payload bọc nháy ĐƠN nhưng bên trong có
`'`) — khác 2 ca gần nhất (08-28 thừa `}`, 08-30 thiếu `}`). Call site là lệnh Bash ad-hoc của
agent ⇒ không có script để vá.

## Lỗi THẬT: `_tr = _a[4]` chỉ đúng khi argc == 5

`append_event.sh` nhận `<agent> <type> <topic> <payload> [trace_id]` — **trace_id là tham số
CUỐI**. Khi payload bị word-split (argc > 5 — dạng cách ly PHỔ BIẾN NHẤT), payload chiếm các
index 3…n-2 và trace_id trôi về `argv[-1]`; `argv[4]` chỉ còn là một mảnh payload (ở ca này là
chữ `"vi"`). Bộ dò lọc `trace_id == argv[4]` ⇒ **không bao giờ khớp**, rơi vào nhánh "MẤT THẬT".

Hệ quả: cơ chế ỨNG VIÊN RETRY (thêm 08-24, commit `9ce6a60c`) hoạt động đúng cho ca argc==5
nhưng **mù đúng ca nó sinh ra để phục vụ**, rồi dispatch chép nguyên văn chẩn đoán sai vào dòng
đầu prompt ops-autofix — lần thứ 4 của hình thái "checker/guard khẳng định nguyên nhân chưa hề
kiểm chứng" (§29 coding_guidelines; 5b 08-21, check#9 08-25, guard JSON 08-28).

## Đã vá — commit trong job này

`bin/ops_health_check.sh` khối 5b:
- `_tr = str(_a[-1]) if len(_a) >= 5 else ""` (tham số CUỐI, không phải `_a[4]`).
- Thêm bằng chứng thứ hai `_tp = str(_a[2])` (topic — KHÔNG bị ảnh hưởng bởi split trong
  payload). Khớp **1 trong 2** là đủ; **không có bằng chứng nào thì KHÔNG nhận bừa** event đầu
  tiên trong cửa sổ (hành vi cũ khi `_tr` rỗng).

`bin/ops_health_check_rejected_selfcheck.py`: fixture `rec()` trước đây đặt trace ở `argv[4]`
với argc=6 — chính nó MÃ HOÁ cái bug, nên sửa sang `argv[-1]`; thêm `case_wordsplit_trace_o_cuoi`
dựng lại đúng argv 13 phần tử của ca thật + 2 ca đối chứng (khác cả trace lẫn topic ⇒ không nhận;
mất trace nhưng trùng topic ⇒ vẫn nhận).

**Verify:** selfcheck 30/30 PASS dưới 4 TZ (`Asia/Ho_Chi_Minh`, `UTC`, `America/New_York`,
`env -u TZ`). Mutation: khôi phục `bin/ops_health_check.sh` bản HEAD ⇒ **4 assertion FAIL** đúng
các ca ứng viên retry. Chạy lại checker thật: check 5b chuyển sang ✅ *"24h qua không có ca CHƯA
XỬ LÝ (2 ca mới đã được đánh dấu xử lý)"*, tổng 3 → 2 điểm chú ý.
