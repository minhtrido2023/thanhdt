# 2026-08-13 — Quyết định trần giá TV1 đã được THỰC THI qua code + injector, nhưng chưa từng đóng câu hỏi bus gốc bằng event `answer`

**Bối cảnh phát hiện.** Retro `retro-2026-08-13.md`, sự cố #4 — 1 trong 6+ biến thể của Pattern-B
(xem `kb/coding_guidelines.md` §28) quan sát được trong 4 ngày liên tiếp 08-10→08-13.

## Triệu chứng

Câu hỏi bus `DollarBill/zalopay-tv1-ceiling-vs-t1-band` mở 08-11, tái khẳng định 08-12 — **chưa
từng có event `answer` đóng nó**. Checker/người đọc bus thấy câu hỏi vẫn "mở", suy diễn quyết
định chưa được đưa ra.

**Thực tế:** quyết định kỹ thuật đã được **thực thi thật** qua kênh khác — code change + injector
chạy tay (ghi lại trong working memory `[2026-08-13T00:06:58Z]`). Plan `2026-08-14` xác nhận cả 2
account đã chuyển từ ceiling tĩnh sang cơ chế **trần động §24** (`hard_no_chase_ceiling_vnd =
20.661`, tính theo `entry_anchor × (1+tau)` chứ không phải số tĩnh cũ). Với ceiling mới, cả 2
account đã mua được một phần TV1 hôm 08-13 (SpaceX 1.100cp, ZaloPay 600cp) — ceiling không còn là
rào cản chính.

## Root cause

Không phải bug checker (đã loại trừ 2 giả thuyết false-positive quen thuộc: answer chéo-agent
không match, resolver hậu-tố/thứ-tự timestamp sai — không tái diễn). Bản chất: **quyết định đi
qua kênh HÀNH ĐỘNG (code + chạy tay), không đi qua kênh BUS** — đúng chữ ký Pattern-B ("hệ thống
tin biểu diễn của sự thật — ở đây là sự vắng mặt của event `answer` trên 1 kênh — thay vì xác
nhận sự thật bằng artifact khác").

## Fix

**Đóng bus question bằng 1 event `answer` trích artifact thật** (giá trị `hard_no_chase_ceiling_vnd`
trong plan + số khớp lệnh thật) — theo đúng skill `close-the-loop`. Xem event `answer` trên bus
ngày 2026-08-14 cho nội dung đầy đủ.

**Phòng ngừa chung** (không riêng ca này) — đã ghi thành `kb/coding_guidelines.md` §28 (duyệt bởi
user 2026-08-14): mọi checker so sánh 2 nguồn phải chuẩn hoá GIÁ TRỊ trước khi so, không suy diễn
từ sự vắng mặt của 1 kênh. Không lặp lại quy tắc ở đây — đọc trực tiếp §28.

## Bài học

Kênh HÀNH ĐỘNG (code diff, log injector chạy tay) và kênh BÁO CÁO (bus event `answer`) là 2 việc
tách biệt, dễ quên bước 2 khi đã làm xong bước 1 dưới áp lực vận hành. Kỷ luật: mọi khi resolve
một câu hỏi bus — dù bằng cách nào — luôn có bước cuối là post lại `answer`/`decision`, không coi
"đã làm xong việc" là tương đương "đã đóng câu hỏi".
