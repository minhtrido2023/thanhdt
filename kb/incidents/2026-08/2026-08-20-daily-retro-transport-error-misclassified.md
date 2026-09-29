# 2026-08-20 — retro 2026-08-19 mất vì lỗi TRUYỀN TẢI API, bị log gán nhầm thành "Mike trả lạc đề"

**Triệu chứng.** ops_health_check 08:20 ICT (run account=ZaloPay) flag: thiếu
`kb/incidents/retro/retro-2026-08-19.md`, nghi "cron 00:30 crash — đúng lớp lỗi 08-01
(quoting bug làm script chết trước khi kịp notify)".

**Chẩn đoán — KHÔNG cùng root cause với 08-01.** `daily_retro.sh` không hề chết âm thầm: nó
chạy trọn vẹn, abort có kiểm soát, notify Telegram, và mở question
`Mike/daily-retro-draft-failed-2026-08-19`. Bằng chứng thật ở 2 log draft:

```
mike/logs/daily_retro_draft_20260819_173001_a1.log  (00:30:01 → 00:30:17)
mike/logs/daily_retro_draft_20260819_173017_a2.log  (00:30:17 → 00:30:35)
API Error: Unable to connect to API: Self-signed certificate detected.
Check your proxy or corporate SSL certificates
```

Cả 2 lần thử chết sau 16-18 giây vì tầng MẠNG (proxy/ISP chèn cert vào TLS tới API), không
phải vì prompt/quoting/usage-limit. Chuỗi chỉ xuất hiện đúng trong cửa sổ đó
(`grep -rl "Self-signed certificate" mike/logs/` → 4 file, tất cả thuộc 2 job này) ⇒ blip
nhất thời, không phải hỏng cấu hình.

**Hai lỗi thiết kế thật sự (chứ không phải "mạng lỗi thì chịu"):**

1. **Retry không có backoff.** Vòng `for _attempt in 1 2` gọi lại NGAY (18 giây sau) ⇒ rơi
   đúng vào cùng khoảng blip ⇒ lần thử thứ 2 vô dụng. Backoff hợp lý với usage-limit thì vô
   nghĩa (đã dừng hẳn), nhưng với lỗi truyền tải thì đó là toàn bộ giá trị của việc retry.
2. **Chỉ có HAI lớp phân loại: usage-limit và "mọi thứ còn lại".** "Mọi thứ còn lại" bị gán
   cứng nhãn *"nghi Mike trả nhầm task cũ"* trong log, notify Telegram và payload bus
   question. Hệ quả đo được: sáng hôm sau checker + job ops-autofix
   (`Winston_20260820_012008`) bị dẫn thẳng sang giả thuyết "quoting bug 08-01" — sai lớp,
   sai file, sai cả thời đại. Cùng họ với §28 coding_guidelines (checker suy sai từ một kênh
   không đủ phân giải).

**Fix (commit dưới, `mike/bin/daily_retro.sh`):** thêm lớp phân loại THỨ BA —
`API_TRANSPORT_ERROR_RE` (`Unable to connect to API|Self-signed certificate|Connection
error|fetch failed|ECONNREFUSED|ECONNRESET|ETIMEDOUT|getaddrinfo|EAI_AGAIN`):
- khớp ⇒ log đúng lớp lỗi + `sleep $API_RETRY_BACKOFF_SEC` (mặc định 180s, override bằng
  `DAILY_RETRO_API_BACKOFF_SEC`) trước lần thử cuối;
- nhánh ABORT tính `$_fail_cause` và bơm vào CẢ log, notify Telegram lẫn payload bus
  question — người/agent đọc lần sau thấy ngay "lỗi mạng" thay vì phải tự đoán.

**CỐ Ý không gộp vào `usage_limit_phrases.sh`.** File đó là hợp đồng dùng chung với
`dispatch.sh`: khớp ⇒ auto-resume. Lỗi mạng không được kích auto-resume của dispatch.sh —
gộp vào là đổi hành vi của mọi agent trong fleet, không chỉ retro.

**Verify.** `mike/bin/daily_retro_failcause_selfcheck.sh` — 8/8 PASS trên 4 biến thể TZ
(`Asia/Ho_Chi_Minh`/`UTC`/`America/New_York`/`env -u TZ`), gồm nguyên văn dòng log sự cố và
3 ca usage-limit thật để chứng minh HAI lớp loại trừ nhau (lẫn nhau ⇒ mất auto-resume hoặc
chờ backoff vô ích). ShellCheck gate: chỉ còn SC1091 info (pre-existing). Retro 2026-08-19
đã được chạy bù thủ công cùng phiên.

**Bài học.** Một checker/pipeline có N lớp lỗi thật mà chỉ phân loại được 2 thì lớp thứ 3
không biến mất — nó bị GÁN NHÃN SAI, và cái nhãn sai đó tự truyền xuống mọi người đọc sau
(log → Telegram → bus → job autofix hôm sau). Thêm nhánh `else` mang tên cụ thể rẻ hơn
nhiều so với một buổi sáng đi tìm bug quoting không tồn tại.

---

## Phụ lục — sự cố THỨ HAI trong chính lần chạy bù (tự gây, 2026-08-20 08:28 ICT)

Lần chạy bù đầu tiên (08:21) **hỏng vì chính tôi sửa `daily_retro.sh` TRONG LÚC nó đang chạy.**
Bash không nạp trọn script vào bộ nhớ — nó đọc tiếp theo **byte offset**. Chèn ~30 dòng ở đầu
file làm mọi offset phía sau dịch đi ⇒ tiến trình đang chạy đọc tiếp vào giữa câu lệnh:

```
mike/bin/daily_retro.sh: line 222: API_TRANSPORT_ERROR_RE: unbound variable
mike/bin/daily_retro.sh: line 230: syntax error near unexpected token `done'
```

Hệ quả gây hiểu nhầm nặng hơn cả lỗi: draft Mike vừa viết ra bị gán nhãn *"SAI ĐỊNH DẠNG —
thiếu header, nghi lạc đề"* và bị `mv` sang `state/retro_rejected_2026-08-19_a1.md`. **Draft đó
hoàn toàn hợp lệ** — chạy lại đúng regex của gate trên chính file bị loại:

```
$ grep -qE "^#{1,2} RETRO — 2026-08-19" state/retro_rejected_2026-08-19_a1.md && echo PASS
PASS        # 16.998 bytes, header đúng
```

Xác nhận cuối: lần chạy sạch 08:35 (không sửa file trong lúc chạy) qua gate ngay lần thử đầu —
`Draft OK (14940 bytes)`. Tức gate KHÔNG có bug; nhãn "lạc đề" là thiệt hại phụ của việc sửa
script đang chạy.

**Luật rút ra:** không bao giờ `Edit`/`sed -i`/ghi đè một file `.sh` đang có tiến trình chạy.
Nếu buộc phải vá gấp: `cp` sang tên mới rồi sửa bản copy, hoặc đợi tiến trình kết thúc. Đây
cũng là một dạng "nhãn sai tự truyền đi" y hệt bug chính ở trên — lần này nạn nhân là chẩn
đoán của chính người đang sửa.
