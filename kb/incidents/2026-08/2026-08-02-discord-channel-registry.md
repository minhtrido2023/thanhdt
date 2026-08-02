---
kind: incident
date: 2026-08-02
topic: discord-channel-registry
title: >-
  2026-08-02: lần thứ 5 "message các topic Discord lẫn lộn" — bỏ vá từng lớp, chuyển sang
  registry duy nhất + pre-commit gate chặn ID trần
status: fixed
category: dispatch-orchestration
origin: >-
  user báo (KHÔNG phải lần đầu) rằng message của các topic Discord khác nhau bị gửi lẫn lộn,
  không kiểm soát được, và yêu cầu một phương án KỸ THUẬT giải quyết triệt để thay vì vá thêm
  một lớp nữa
recorder: Wags (job Wags_20260802_160902), dispatch từ Mike
---

# 2026-08-02 — Định tuyến topic Discord: thay 4 lớp vá bằng 1 registry + 1 gate cơ học

## Vì sao 4 lần vá trước không triệt để

| Lần | Sự cố | Bản vá | Vì sao vẫn tái phát |
|---|---|---|---|
| 2026-07-01 | DollarBill thread-leak | `_agent_thread_override` (map tĩnh agent→topic) | Ngầm giả định 1 agent = 1 topic |
| 2026-07-06 | Taylor phục vụ 2 topic, notify rơi nhầm | Ghim `discord_thread_id` lên job record | Đúng nguyên lý, nhưng chỉ phủ notification CỦA `dispatch.sh` |
| 2026-07-22 | override thành dead-code (env xếp trên) | Đảo thứ tự ưu tiên + export `DISCORD_THREAD_ID` xuống tiến trình con (`b3e9fe8`+`1d9dcc6`+`f0eb2b2`, sau đó `734cbac`) | "Gap WIDENED sau b3e9fe8" — job record và env của agent lệch nhau **do kiến tạo** |
| 2026-07-22b | job record ≠ env agent | Sửa ở consumer (`session_start.sh` dùng `INTERACTIVE_TID`) | Vẫn còn 31 file tự quyết định topic riêng |

**Mẫu chung của cả 4 lần**: mỗi lần đều sửa đúng chỗ hỏng, nhưng đều dựa vào **con người nhớ
dùng đúng biến/hàm có sẵn**. Không lần nào loại bỏ được điều kiện khiến lỗi mới sinh ra được.

## Root cause thật (3 điểm, đo bằng số liệu)

**R1 — logic phân giải bị NHÂN BẢN.** `dispatch.sh` có resolver 3 tầng; `notify_thread.sh` có
resolver 2 tầng RIÊNG; 31 file trong `bin/` (69 call site) mỗi file tự hardcode. Mỗi lần vá chỉ
sửa **một bản sao**.

**R2 — ID trần KHÔNG kiểm chứng được.** 45 chỗ viết ID Discord trần trong code, dưới **8 tên
biến khác nhau cho CÙNG 1 channel** (`DISCORD_STALE_CHANNEL`, `DISCORD_TRADING_DAILY`,
`TRADING_DAILY_THREAD`, `DISCORD_TRADING_THREAD`, `TRADING_DAILY`, `THREAD_ID`, `_tid`, literal
trần) — tất cả = Trading Daily. Nguy hiểm nhất: `eod_trading_report.sh` khai **cả**
`TRADING_THREAD` (= Trading **Report**) **và** `TRADING_DAILY_THREAD` (= Trading **Daily**)
trong cùng một file; `preflight_check.sh` dùng `DISCORD_TRADING_THREAD` (= Trading **Daily**) —
hai tên chỉ khác nhau đúng tiền tố `DISCORD_` mà trỏ hai channel khác nhau. Nhìn một chuỗi 19
chữ số thì không ai biết tác giả định gửi đâu ⇒ copy-paste sai là **im lặng vĩnh viễn**: không
test nào bắt, không review nào thấy.

**R3 — fallback im lặng CHÍNH LÀ cơ chế rò rỉ.** Tầng cuối của cả hai resolver là
`agents/Mike/state/ccdb_thread_id` = "topic Mike vào gần nhất", bị `hooks/session_start.sh` ghi
đè mỗi lần Mike start/resume ở bất kỳ topic nào. Khi các tầng trên rỗng, tin nhắn **không
fail** — nó rơi vào topic user tình cờ đang đọc. Fail-open sai hướng.

**R4 (khác họ, đừng lẫn)** — `2026-08-02-notify-api-silent-message-loss.md`: `/api/notify` âm
thầm **đánh rơi** ~10 message/3 ngày (embed >4096 ký tự + UnicodeDecodeError ở bridge dùng
chung). Triệu chứng "Mike không follow topic" có thể một phần là **mất** tin nhắn chứ không
phải **gửi nhầm**. `notify_discord.sh` đã fix truncate; lỗi UTF-8 ở bridge **vẫn chưa sửa**.

## Phương án đã thực hiện

1. **`kb/discord_channels.json`** — registry DUY NHẤT tên-ý-nghĩa → ID thật (7 channel). Là nơi
   DUY NHẤT trong repo được phép chứa ID trần.
2. **Một điểm phân giải duy nhất**: `bin/notify_thread.sh` nhận **TÊN** ở đối số 2
   (`notify_thread.sh "<msg>" trading_daily`). ID trần 17–20 chữ số vẫn passthrough vì
   `dispatch.sh` phải truyền lại đúng ID đã ghim trên job record. Tên sai ⇒ **exit 1 + ghi
   `logs/notify_thread_errors.log`**, KHÔNG rơi về topic mặc định.
   Phụ trợ: `bin/discord_channel.sh <tên>` (CLI) và `bin/discord_channels.py` (`resolve()`).
3. **`dispatch.sh`**: `_agent_thread_override` tra registry thay vì `echo` ID; `--thread` nhận
   cả tên lẫn ID và **phân giải ngay tại điểm ghim** ⇒ job record + `DISCORD_THREAD_ID` của
   tiến trình con luôn giữ ID THẬT, mọi tầng sau chỉ đọc lại, không phân giải lần nữa.
4. **Migrate 31 file / 45 chỗ** về registry — 0 ID trần còn lại trong `bin/` và `hooks/`.
   Đổi tên 2 biến gây nhầm: `TRADING_THREAD`→`TRADING_REPORT_THREAD` (eod), 
   `DISCORD_TRADING_THREAD`→`TRADING_DAILY_THREAD` (preflight).
5. **`bin/discord_id_gate.sh` + hook `discord-id-gate` trong `.pre-commit-config.yaml`** —
   CHẶN CỨNG commit nếu snowflake 18–19 chữ số xuất hiện trong `bin/*.sh|*.py`, `hooks/*.sh`
   ngoài registry. **Đây là điểm mấu chốt**: biến "nhớ dùng tên" từ quy ước thành điều kiện
   CƠ HỌC để commit được — thứ mà cả 4 lần vá trước đều thiếu.
   Regex `(?<![0-9.])1[0-9]{17,18}(?![0-9.])` đã đo trên toàn repo trước khi chốt: **0
   false-positive** trong `bin/`+`hooks/` (lookaround loại phần thập phân của float dài trong
   CSV nghiên cứu của Taylor). Phạm vi cố ý hẹp (chỉ code thực thi) theo đúng triết lý curated
   của `bin/shellcheck_gate.sh` — tài liệu `kb/*.md` được phép trích ID để giải thích.
6. **Nhánh fallback toàn cục vẫn giữ nhưng nay GHI LOG mỗi lần dùng** — tính đến 2026-08-02
   không còn call site nào trong `bin/` đi vào nhánh này; giữ lại để phiên tương tác của Mike
   không mất thông báo, nhưng một call site mới quên truyền topic sẽ hiện trong
   `logs/notify_thread_errors.log` thay vì biểu hiện thành "message lẫn topic" không truy được.

## Verify

- `bin/discord_id_gate.sh bin/*.sh bin/*.py hooks/*.sh` → **0** ID trần (trước migrate: 45).
- Gate CHẶN đúng khi cố ý thêm lại ID trần vào một file đã migrate (exit 1); CHO QUA file sạch.
- `bash -n` + `python3 -m py_compile` sạch trên toàn bộ 32 file đã sửa;
  `bin/shellcheck_gate.sh` không có hard-block (**gate này đã bắt 1 regression do chính bản
  migrate gây ra**: backtick lọt vào prompt string của `daily_retro.sh` — SC2006, đúng lớp lỗi
  nó sinh ra để chặn; đã sửa).
- **Dispatch THẬT `--bg`** (`Wags_20260802_162119`) với `DISCORD_CHANNELS_REGISTRY` trỏ registry
  GIẢ: job record ghim `discord_thread_id=9999999999999999911` = đúng ID giả của `architecture`
  ⇒ chuỗi `_agent_thread_override` → `discord_channel.sh` → registry → job record chạy thật,
  không tin nhắn nào tới topic thật.
- Nhánh fallback: ghi đúng dòng WARN vào `logs/notify_thread_errors.log`. **Tác dụng phụ của
  chính phép thử này**: một dòng `TEST-fallback` đã được gửi vào `1522519012066721923` (topic
  Mike vào gần nhất, KHÔNG nằm trong registry) — chính là hành vi rò rỉ đang mô tả, quan sát
  được trực tiếp. Xoá tay nếu thấy phiền.

### Verify vòng 2 (attempt 2 của job, sau khi attempt 1 hết lượt giữa chừng)

- **Đối chiếu ĐÍCH ĐẾN từng file (kiểm tra quan trọng nhất)**: script so tập ID trần bị XOÁ với
  tập ID mà tên mới PHÂN GIẢI RA, trên cả 32 file → **30/32 khớp tuyệt đối**. 2 file lệch
  (`notify_thread.sh`, `hooks/session_start.sh`) đã soi tay: chỉ là chữ trong **comment**
  (ID trần → tên gọi), không đổi định tuyến. ⇒ migrate KHÔNG đổi đích của bất kỳ file nào.
- **E2E trên dây thật**: dựng HTTP server bắt gói ở cổng phụ, chạy bản sao `notify_thread.sh`
  trỏ vào đó. `channel_id` LÊN DÂY đúng ID thật cho `trading_daily` / `architecture` /
  `trading_report` / ID trần passthrough; tên **gõ sai ⇒ exit 1 và KHÔNG có gói nào lên dây**
  (fail-loud, không rơi topic khác). Không tin nhắn nào tới Discord thật.
- Gate: chạy sạch toàn `bin/`+`hooks/` (exit 0); CHẶN ID trần cố ý (exit 1); KHÔNG bắt nhầm
  float dài 20+ chữ số (exit 0).
- `--thread` của `dispatch.sh`: tên → ID thật; **tên sai ⇒ topic RỖNG** (fail-safe: job chạy
  không có topic, không bao giờ gửi nhầm topic khác). `_agent_thread_override` trả đúng ID cũ
  cho `DollarBill`/`Wags`. Quét toàn repo: **0** ID trần còn trong bất kỳ `.sh`/`.py` nào;
  crontab sạch; chỉ `notify_thread.sh`+`notify_discord.sh` chạm API Discord (không đường vòng).

**2 lỗi THẬT phát hiện thêm ở vòng 2 (đã sửa):**
1. `discord_id_gate.sh:28` — dòng comment mở đầu bằng `# shellcheck` khiến shellcheck đọc nhầm
   thành directive hỏng (SC1072/SC1073) và **BỎ LINT cả file gate**. Trớ trêu: chính công cụ
   gác cổng lại là file không được lint. Đã đổi thành `# bin/shellcheck_gate.sh`.
2. `weekly_ops_audit.sh` — biến `ARCH_THREAD` **chết từ TRƯỚC** refactor (prompt tự ghi topic,
   không đọc biến). Đúng lớp lỗi của sự cố 2026-07-22 "override thành dead-code": sửa biến,
   tưởng đã đổi đích, thực tế không. Đã xoá kèm comment cảnh báo.

## Bài học

Ba lần trước đều sửa **cơ chế**; lần này sửa **điều kiện tồn tại của lỗi**. Một quy ước
("nhớ dùng biến có sẵn") mà không có gate cơ học thì tuổi thọ chỉ bằng trí nhớ của người sửa
tiếp theo — đúng bài học đã ghi ở `2026-07-20` ("chỉ nhắc trong prose không đủ, cần cơ chế")
nhưng lần đó mới áp cho **một** agent (`_agent_thread_override` cho Wags), chưa áp cho **lớp
lỗi**.
