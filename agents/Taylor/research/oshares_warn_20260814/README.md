# Việc 1 (WARN biên độ) — ĐÃ NHƯỜNG cho job `Taylor_20260814_003610`. Patch giữ làm dự phòng.

Job `Taylor_20260814_003518` (tôi) và job `Taylor_20260814_003610` được Mike dispatch **cách nhau
55 giây** cho **cùng một việc**, trên **cùng file** `mike/bin/corp_action_daily.py` (cron sống
07:30 ICT), **không cách ly worktree**.

## Đã xảy ra thật, không phải rủi ro lý thuyết

- 07:36:11 job B (`_003610`, dedicated Việc 1, user chọn phương án C) bắt đầu.
- 07:41:33 file có **cả hai** cơ chế WARN cùng lúc: `latest_quarter_row`/`magnitude_watch`/
  `_fmt_magnitude` (của B) **và** `_quarterly_at`/`sanity_flag`/`sanity_warns` (của tôi).
- Công cụ `Edit` ghi **cả file** từ bản đã đọc trước đó ⇒ sửa của bên này âm thầm đè bên kia.
  Phần của B biến mất khỏi disk lúc ~07:42. Job B sau đó hết turn budget (attempt 1, exit 1) và
  phải làm lại từ đầu ở attempt 2.

Đây đúng ca đã ghi trong `kb/coding_guidelines.md` (Mafee + Taylor sửa cùng `plan_funding_gate.py`
trong 1 phút, 2026-08-07). Lần đó mất việc chưa xảy ra; lần này **đã mất một attempt**.

## Tôi đã làm gì

Lưu diff của mình thành `taylor_003518_warn.patch` (101 dòng thêm) rồi **revert sạch**
(`git apply -R`) — verify sau khi revert: `git status` sạch, file == HEAD, **không corrupt**.
Việc 1 thuộc về job B.

## ⚠️ ĐỌC TRƯỚC KHI ÁP LẠI PATCH NÀY — **ĐỪNG ÁP**, trừ khi file sạch trơn cơ chế WARN

**Cập nhật 07:52, đo lại file thật:** va chạm đã kết thúc bằng **HỘI TỤ, không phải trùng lặp**.
Job B đọc file lúc ~07:41 khi bản của tôi còn nằm đó, và **đã tiếp nhận** nó: file hiện có
`_quarterly_at()` / `sanity_flag()` / `sanity_warns()` / `check_retro(..., back=)` /
`import oshares_pit as _pit` **của tôi**, cộng thêm `sanity_warns_from_crosscheck()` và
`_fmt_magnitude()` **của job B**. Bộ tên cũ của B (`latest_quarter_row`/`magnitude_watch`) đã
biến mất — chỉ còn **một** cơ chế WARN mạch lạc, do **job B sở hữu**.

⇒ Áp patch này lên file hiện tại = thêm bản THỨ HAI của đúng những hàm đã có ⇒ **hai vị ngữ cho
cùng một câu hỏi**, đúng khiếm khuyết R8/R10 mà chính file này vừa phải vá hai vòng (`refused()`
được nâng lên module-level chỉ vì lý do đó).

Patch chỉ còn giá trị **dự phòng**: job B đang ở **attempt 2/2** (không còn attempt 3). Nếu nó
fail hẳn *và* file không còn cơ chế WARN nào, đây là điểm khởi động — **sau khi đọc lại file
thật**, không áp mù. Lưu ý patch này **không có selfcheck** (tôi dừng ở bước phát hiện va chạm);
job B mới là bên có nhiệm vụ 142+ ca hồi quy.

## Nội dung patch (nếu cần dựng lại)

Ngưỡng dùng chung, không chép số: `import oshares_pit as _pit` rồi gọi `_pit._sane()` /
`_pit.SANITY_FACTOR` **tại lúc gọi** (không `from ... import SANITY_FACTOR` — bản `from` đóng băng
giá trị lúc import ⇒ `OSHARES_SANITY_FACTOR=<x>` và mọi monkeypatch của selfcheck sẽ im lặng vô
hiệu ở file này). WARN gắn field `sanity_warn` vào bản ghi và **giữ nguyên `value`**; phủ cả 3
điểm gọi `oshares_at` (publish / `check_retro` / `crosscheck`) bằng cách truyền `back=` đã tính
sẵn vào `check_retro` thay vì gọi `oshares_at` lần thứ hai.

Selfcheck thì **chưa viết** — tôi dừng ở bước phát hiện va chạm.
