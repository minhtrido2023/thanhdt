---
kind: incident
date: 2026-08-01
topic: daily-retro-quoting-bug-silent-2day-outage
title: >-
  2026-08-01: daily_retro.sh crashed silently 2 đêm liên tiếp (07-31, 08-01) — bug quoting
  do chính commit migrate OKF gây ra
status: fixed
category: dispatch-orchestration
origin: >-
  bước sửa file (edit kb/incidents migration, commit e2c2fb3d9 2026-07-30) thiếu escape
  double-quote lồng bên trong chuỗi double-quoted bash — không có bash-level test sau khi sửa
recorder: >-
  Mike, phát hiện khi user yêu cầu review toàn diện quy trình vận hành (2026-08-01), không phải
  qua alert/notify nào — script crash TRƯỚC bất kỳ notify.sh nào có thể chạy tới
---

# 2026-08-01: daily_retro.sh crashed silently 2 đêm liên tiếp (07-31, 08-01)

**Phát hiện:** trong lúc audit tổng quát theo yêu cầu user ("rà soát quy trình vận hành có vấn
đề gì, OKF file reorg có hiệu quả không, token usage có cải thiện không"), kiểm tra
`logs/daily_retro.log` thấy 2 dòng lỗi liên tiếp thay vì log hoàn tất bình thường:
```
[2026-07-31T00:30:01+0700] === daily_retro START (reviewing 2026-07-30, ...) ===
bin/daily_retro.sh: line 114: label: No such file or directory
bin/daily_retro.sh: line 169: draft_prompt: unbound variable
[2026-08-01T00:30:01+0700] === daily_retro START (reviewing 2026-07-31, ...) ===
bin/daily_retro.sh: line 114: label: No such file or directory
bin/daily_retro.sh: line 169: draft_prompt: unbound variable
```
Cả 2 đêm cron chạy đúng giờ nhưng script crash ngay ở bước gán biến `draft_prompt` — KHÔNG có
draft, KHÔNG dispatch Wags verify, KHÔNG finalize, và quan trọng nhất: **KHÔNG notify** (crash
xảy ra trước dòng `notify.sh`/`append_event.sh` nào trong luồng chính có thể chạy tới) — đây
đúng là kiểu lỗi "im lặng hoàn toàn" mà toàn bộ cơ chế RETRO được dựng lên để bắt, nhưng chính nó
lại là nạn nhân.

**Root cause:** commit `e2c2fb3d9` (2026-07-30, phần việc migrate sổ sự cố sang cấu trúc OKF)
thêm 1 câu hướng dẫn vào `draft_prompt` (biến chuỗi double-quoted nhiều dòng) nhắc agent dùng
`incident_lookup.py`:
```
'python3 bin/incident_lookup.py "<label>" "<chi tiết>"' — KHÔNG đoán từ trí nhớ
```
Cặp `"<label>"`/`"<chi tiết>"` là double-quote **không escape** nằm LỒNG bên trong chuỗi
double-quoted bao ngoài (`draft_prompt="..."`) — bash coi `"` đầu tiên gặp là điểm ĐÓNG chuỗi
ngoài. Phần còn lại (`<label>" "<chi tiết>"` ...) bị bash phân tích lại như token shell bình
thường: `<label>` bị hiểu là redirect input từ file tên `label` (lỗi "line 114: label: No such
file or directory"), và vì chuỗi bị cắt ngang giữa chừng, gán `draft_prompt=` không bao giờ hoàn
tất → tới dòng 169 dùng `"$draft_prompt"` dưới `set -u` → "unbound variable" → bash thoát ngay
lập tức (non-interactive + nounset = fatal). `bash -n` (syntax check) KHÔNG bắt được lỗi này vì
đây là lỗi ngữ nghĩa (quoting logic), không phải lỗi cú pháp.

**Tái hiện lỗi (xác nhận đúng cơ chế trước khi sửa):**
```
$ bash -c 'set -uo pipefail; draft_prompt=\
"a '"'"'python3 x "<label>"'"'"' b"
echo $draft_prompt'
bash: line 2: label: No such file or directory
bash: line 3: draft_prompt: unbound variable
```
khớp CHÍNH XÁC 2 dòng lỗi thật trong log.

**Fix:** escape 2 cặp dấu ngoặc kép lồng bên trong (`\"<label>\"` `\"<chi tiết>\"`),
`bin/daily_retro.sh:114`. Verify: (1) `bash -n` pass; (2) test cô lập tái hiện với bản sửa cho
kết quả đúng; (3) trích đúng khối gán `draft_prompt=` (dòng 76-152) từ file THẬT, chạy độc lập —
`RC=0`, `draft_prompt` dài 5709 ký tự đúng như kỳ vọng, không còn lỗi nào.

**Tác động:** RETRO của 2 ngày 2026-07-30 và 2026-07-31 KHÔNG được review tự động — không rõ có
sự cố/pattern nào trong 2 ngày đó bị bỏ sót hay không (chưa quyết backfill, theo đúng tiền lệ RETRO
07-24→07-27 vẫn đang để "chưa quyết" — không tự ý backfill mà không hỏi, ghi vào phần treo).

**Bài học — GIỐNG pattern đã biết, khác lớp:** đây là lần thứ N script/prompt bash bị hỏng vì sửa
text tự do bên trong 1 chuỗi quoted phức tạp mà không test lại bằng cách CHẠY THẬT đoạn code sau
khi sửa (chỉ dựa vào "đọc lại thấy hợp lý" + `bash -n`). Vòng lặp fix `wags_autofix.sh` CÙNG NGÀY
hôm trước (2026-07-30, P1/P2/P3 work) đã tự bắt+tự sửa đúng 1 lỗi quoting tương tự TRƯỚC khi
commit — nhưng bài học đó không được tổng quát hoá thành 1 quy tắc kiểm tra bắt buộc
("sau khi sửa bất kỳ chuỗi bash nhiều dòng chứa dấu ngoặc kép, chạy thử đoạn gán biến độc lập
trước khi commit") — nên lặp lại ở file khác 1 ngày sau, và lần này KHÔNG có review nào bắt được
trước khi lên production (khác với `send_plan_report.sh`/`wags_autofix.sh` đã qua arch-reviewer).
**Đề xuất prevention cụ thể**: bất kỳ commit sửa `draft_prompt=`/tương tự (chuỗi lệnh dài truyền
cho `dispatch.sh`) trong các file cron-driven (`daily_retro.sh`, `kb_nightly.sh`, `ops_autofix.sh`,
`wags_autofix.sh`, `send_plan_report.sh`) nên chạy `bash -c 'source <(sed -n "START,ENDp" file); echo OK'`
(hoặc tương đương) như 1 bước self-check tối thiểu trước khi commit — không thay được review độc
lập, nhưng bắt được CHÍNH XÁC lớp lỗi này, rẻ hơn arch-reviewer nhiều.

**Cập nhật cùng ngày:** áp dụng đúng cách tự-kiểm này khi sửa `kb_nightly.sh` (thêm opus%-alert)
phát hiện thêm **2 lỗi CÙNG LỚP đã sống 2 TUẦN** làm cả review Friday/Saturday chết hẳn — nghiêm
trọng hơn bug này nhiều. Xem [[2026-08-01-kb-nightly-friday-dispatch-silently-broken-2-weeks]].

---

**Follow-up 2026-08-01 15:2x ICT (Winston, job `Winston_20260801_081056`) — BUG THỨ HAI nằm ngay
sau bug quoting, đã sửa trước khi nó kịp nổ.** `ops_health_check` 15:10 vẫn flag "thiếu
retro-2026-07-31" (đúng: RC đã fix lúc 10:49 nhưng chưa ai backfill). Khi verify xem đêm nay
00:30 có chạy trót lọt không, phát hiện `_draft_valid()` — content-shape gate thêm ngày 07-30 —
yêu cầu `^## RETRO — <ngày>` (2 dấu #), trong khi **prompt bước 1 mục 4 ra lệnh viết `# RETRO —`
(1 dấu #)** và mọi entry đã finalize trong `kb/incidents/retro/` cũng dùng 1 dấu #. Tức gate sẽ
loại đúng cái draft ĐÚNG ĐỊNH DẠNG → reject cả 2 attempt → abort.

Lý do latent: gate được thêm lúc **07-30 00:48 ICT** (`01a7f991`) — tức SAU lần chạy thành công
cuối cùng (07-30 00:36), và 2 đêm sau đó (07-31, 08-01) script chết ở bug quoting *trước* khi tới
dòng gate. **Gate chưa từng chạy thật một lần nào**; đêm nay là lần đầu — và nó sẽ fail (lần này
có notify, nhưng vẫn không có retro). `state/retro_rejected_*` rỗng = bằng chứng gate chưa từng
loại gì.

Fix (`68757b7e`): gate nhận `^#{1,2} RETRO — <ngày>`. Giữ nguyên tính chất chống-lạc-đề (vẫn bắt
buộc đúng header + đúng ngày). Verify 6/6 trên gate trích nguyên văn: 1-dấu-# ACCEPT, 2-dấu-#
ACCEPT, lạc đề / sai ngày / rỗng / 3-dấu-# đều REJECT; `bash -n` OK; ShellCheck pre-commit gate
Passed. Cũng verify độc lập bug quoting đã hết: chạy thật khối gán `draft_prompt` (dòng 76–152)
dưới `set -u` → RC=0, 5709 ký tự.

**Bài học cộng thêm (khác với bài học quoting ở trên):** một *gate phòng thủ* mới thêm mà chưa
từng chạy production một lần nào thì bản thân nó là code chưa được test — và ở đây nó bị che bởi
đúng cái bug mà nó đứng sau. Khi thêm gate cơ khí kiểu "output phải khớp định dạng X", phải
kiểm chứng X **đối chiếu với prompt sinh ra output đó và với artifact thật đang có trên đĩa**,
đừng viết định dạng từ trí nhớ. Prevention: sau khi một cron pipeline được sửa RC, verify luôn
các bước *phía sau* điểm crash cũ — chúng chưa hề chạy.

**Vẫn treo (cần USER/Mike quyết, KHÔNG tự làm):** backfill RETRO 2026-07-30 + 2026-07-31 (và tiền
lệ 07-24→07-27 vẫn "chưa quyết").
