# Lỗi giờ lần 3 (2026-08-21, 23:02 ICT) — "13:00 ICT còn ~15 phút" lúc 23:02. Kiến trúc sửa TRIỆT ĐỂ

> Tác giả: Mike (Fable, plan-only). Trạng thái: CHỜ user duyệt → dispatch Wags/Taylor (Opus) implement.
> Thread gốc: Trading strategy 1521735922066919515, tin lúc 16:02:43Z = 23:02 ICT, session `c31c975c`.

## 0. Kết luận 1 đoạn

Hai lớp hôm qua (stamp header + chuẩn hoá UTC→ICT trong thân tin) chặn đúng 2 loại lỗi đầu (LLM
viết giờ hiện tại sai; script viết UTC). Lỗi lần 3 là loại KHÁC: **LLM SUY LUẬN sai về thời gian**
(nhãn ICT đúng, số bịa) — transport không thể bắt vì không có token UTC nào để sửa. Bằng chứng transcript
cho thấy LLM lúc đó **không có bất kỳ mốc giờ đáng tin nào** và **mọi thứ xung quanh đều là UTC không
nhãn**. Vì vậy câu trả lời cho "chỉ bơm ngữ cảnh có đủ không?" là **KHÔNG đủ nếu đứng một mình** —
nhưng nó cũng **chưa hề được chạy thật** (bug). Kiến trúc đúng = làm cho **toàn bộ thứ LLM quan sát
được chỉ còn MỘT múi giờ (ICT)** + **tính sẵn fact phái sinh (phiên mở/đóng, phiên kế tiếp) bằng code**
để LLM không phải suy luận + **đo** xem còn sai không thay vì chờ user chụp màn hình.

## 1. Bằng chứng (đọc từ `~/.claude/projects/.../c31c975c-….jsonl` + code ccdb + env host)

| # | Phát hiện | Bằng chứng |
|---|---|---|
| E1 | Lớp "bơm `[now: HH:MM ICT]`" (ccdb `prompt_builder.py`, commit 56e3b29) **KHÔNG chạy cho tin text-only** | `build_prompt_and_images()`: `if not message.attachments: return prompt, []` đứng TRƯỚC dòng chèn `now_line`. 13/14 prompt từ lúc restart 19:25 ICT không có `[now:`; đúng 1 prompt có (tin kèm ảnh). Cả 2 prompt dẫn tới lỗi (22:51, 22:59 ICT) đều không có. |
| E2 | Đường wake một-lần (`scheduler.py` `task["prompt"]`) cũng không chèn | `scheduler.py:179` gửi prompt thô |
| E3 | Host + ccdb chạy **TZ=UTC** | `/etc/timezone = Etc/UTC`; service `ccdb-mike` không set TZ; `date` trong Bash tool của mọi phiên Claude = UTC. Crontab đã `TZ=Asia/Ho_Chi_Minh` (§16) ⇒ cùng một script cho giờ KHÁC NHAU tuỳ ai gọi (cron = ICT, Claude = UTC). |
| E4 | Lịch sử Discord bơm vào prompt ghi giờ **UTC không nhãn** | `thread_context._format_line`: `created.strftime("%m-%d %H:%M")` trên `created_at` UTC → `[08-21 15:59] John Dinh: …` — ~20-40 token UTC/prompt, đứng NGAY TRƯỚC câu hỏi. |
| E5 | Tool output LLM đọc có timestamp naive lẫn lộn | cùng lượt: `"ts": "2026-08-21T04:47:31"` (UTC-naive) và `ts=2026-08-21T22:00:05` (ICT-naive). 70 file `.py` trong repo dùng `datetime.now().isoformat()/strftime` naive. |
| E6 | Verification hôm qua của Mike **thiếu ca text-only** | E2E chỉ test `/api/notify` + tin kèm ảnh. Không có selfcheck nào grep transcript xem `[now:` có mặt ở từng đường prompt. |

Cơ chế lỗi tái dựng: user 22:59 ICT viết "sáng mua MBB có thể bán ra sau đó" (ý: sáng mai). LLM không có
`now`, xung quanh chỉ có `[08-21 15:59]` (UTC, không nhãn) + `ts=…22:00:05` (không nhãn) → nó "neo" vào một
giờ chiều tuỳ ý và viết "phiên chiều 13:00 còn ~15 phút". Transport thấy `13:00 ICT` là hợp lệ → cho qua.

## 2. Phân loại lỗi & lớp nào chặn được

| Loại | Ví dụ | Chặn bằng | Trạng thái |
|---|---|---|---|
| A. LLM viết GIỜ HIỆN TẠI sai | `03:25 sáng` lúc 17:26 | stamp header by-construction (56e3b29) | ✅ sống |
| B. Script viết UTC vào thân tin | `12:14 UTC (~435s)` | `_normalize_times` + `utc_text_gate.sh` (4e6f2cb/34037199) | ✅ sống |
| C. LLM SUY LUẬN thời gian sai, nhãn đúng | `13:00 ICT còn ~15 phút` lúc 23:02 | **không có lớp nào** hôm nay | ❌ đây |

Loại C không bắt được ở transport (không thể biết "13:00" là sai nếu không hiểu ý). Chỉ có 3 cách: (i) bỏ
nguồn gây nhầm (UTC) khỏi tầm nhìn LLM, (ii) đưa sẵn fact phái sinh để LLM không phải tính, (iii) đo để biết
còn sai hay không. Không có (iv) "dặn kỹ hơn" — đã thử 3 lần.

## 3. Kiến trúc đề xuất — 4 biện pháp CỤ THỂ (không phải prose), xếp theo độ "by construction"

### S1 — MỘT múi giờ cho mọi thứ LLM quan sát được: `TZ=Asia/Ho_Chi_Minh` ở tầng môi trường
- `systemctl --user edit ccdb-mike.service` → `Environment=TZ=Asia/Ho_Chi_Minh`. Mọi `claude` subprocess,
  mọi Bash tool call, mọi script chạy từ phiên Claude thừa hưởng ⇒ `date`, `ls -l`, log, naive
  `datetime.now()` đều ICT — **khớp crontab** (đã ICT từ §16). Hết tình trạng "cùng script, 2 giờ".
- Đây là fix gốc của E3/E5: LLM không còn thấy token UTC nào từ shell. Không cần dặn.
- **Điều kiện trước khi bật (audit bắt buộc, giao Taylor/data-ops):** rà 70 file naive `datetime.now()`
  → phân loại: (a) ghi timestamp **máy đọc** rồi so với dữ liệu UTC-aware hoặc gắn `Z` → phải đổi sang
  `datetime.now(timezone.utc)` tường minh (để không đổi nghĩa khi TZ đổi); (b) ghi cho người / so với
  lịch ICT → giữ nguyên (giờ mới đúng). Job-id `Taylor_20260821_011002` (dispatch.sh `date +%Y%m%d_%H%M%S`)
  sẽ thành ICT — vô hại, ghi chú vào `jobs.sh`. Đo thật trước/sau bằng `env -u TZ` vs `TZ=ICT` chạy selfcheck.
- Rollback: xoá 1 dòng Environment, restart.

### S2 — Dòng `[now: …]` là FACT PHÁI SINH, bơm ở MỌI đường prompt, và có selfcheck chứng minh
- Nội dung (code tính, LLM chỉ đọc):
  `[now: 23:02 ICT · Thứ Sáu 21/08/2026 · HOSE: ĐÃ ĐÓNG CỬA — phiên kế tiếp Thứ Hai 24/08 09:00 ICT]`
  Trạng thái từ `trading_bot/vn_market.session_phase()` + `next_trading_day()` (đã có, holiday-aware) —
  không viết lịch mới. Lỗi trong ảnh là lỗi "phiên nào / còn bao lâu" — đưa thẳng đáp án, bỏ bước suy luận.
- 3 điểm chèn, tất cả tất định:
  1. ccdb `prompt_builder.build_prompt_and_images` — **sửa bug early-return** (E1): chèn trước `if not
     message.attachments`. Test: `test_prompt_builder` thêm ca text-only assert `[now:` có mặt.
  2. ccdb `scheduler._run_task` (E2) — prepend cùng dòng vào `task["prompt"]`.
  3. Fleet hook `mike/hooks/user_prompt_submit.sh` (8 agent dùng chung) — echo dòng `[now: …]` mỗi lượt.
     Phủ cả **headless dispatch** (Taylor/DollarBill/Mafee/Wags) mà ccdb không chạm tới. Một script
     `bin/now_line.py` dùng chung cho cả 3 (ccdb import qua subprocess hoặc copy thuần 20 dòng + test khớp).
- **Selfcheck đường đi** (để không lặp E6): `bin/now_injection_selfcheck.sh` — với mỗi đường (text-only,
  có attachment, mention thread lạ, ScheduleWakeup, headless dispatch) grep transcript jsonl mới nhất của
  đường đó tìm `<system-reminder>\n[now:`; thiếu đường nào → FAIL nêu tên đường. Chạy 1 lần sau deploy +
  gắn `daily_retro.sh`.

### S3 — Lịch sử Discord bơm vào prompt ghi ICT có nhãn
- `thread_context._format_line`: `created.astimezone(ICT).strftime("%d/%m %H:%M")` + hậu tố ` ICT` →
  `[21/08 22:59 ICT] John Dinh: …`. 1 dòng + 1 test. Gỡ E4 (nguồn UTC nằm sát câu hỏi nhất).

### S4 — ĐO thay vì chờ user: `bin/time_claim_audit.py` (detector, KHÔNG chặn)
- Hằng ngày quét tin Mike/agent đã gửi (ccdb messages DB hoặc `/api/threads/*/messages`), tìm mệnh đề giờ
  tương đối: `còn ~N phút/giờ`, `sau N phút`, `lúc HH:MM (ICT)? … (nữa|còn)`, `phiên (sáng|chiều) … mở lúc`.
  So với giờ gửi thật (`created_at` → ICT) và `session_phase(created_at)`: mâu thuẫn (vd "còn 15 phút tới
  13:00" khi gửi lúc 23:02; "phiên chiều mở lúc" khi đã đóng cửa) → ghi 1 dòng finding vào Architecture
  topic + đếm vào `daily_retro`. Mục tiêu: **0 mismatch/tuần** là tiêu chí "đã sửa xong"; >0 = S1-S3 chưa
  đủ, còn nguồn UTC nào đó → truy tiếp có bằng chứng.
- Cố ý KHÔNG chặn/sửa tự động: heuristic, có false-positive ("13:00 mai còn ~14 giờ" là đúng); chặn sai còn
  tệ hơn. Detector = cách duy nhất biết lớp C đã hết mà không phụ thuộc screenshot của user.

### Không làm
- Không thêm đoạn prose "nhớ dùng ICT" vào MIKE.md/skill — đã 3 lần, đo được là vô hiệu.
- Không vá riêng lẻ từng script in `date` — S1 giải quyết cả lớp.
- Không yêu cầu LLM thôi nói giờ — user cần giờ.

## 4. Vì sao bộ này "không làm đi làm lại"
- A/B/C phủ kín 3 cách giờ có thể sai: viết giờ hiện tại (A), script sinh UTC (B), LLM suy luận (C).
- C được xử bằng cách **bỏ input gây nhầm** (S1, S3) + **bỏ bước suy luận** (S2) — không dựa vào "LLM nhớ".
- S4 là vòng phản hồi: nếu vẫn sai, ta biết trong 24h kèm bằng chứng, không phải chờ user.
- Mỗi lớp có test/selfcheck riêng (E6 không lặp): unit test prompt_builder text-only, test thread_context ICT,
  `now_injection_selfcheck.sh` 5 đường, `env -u TZ` vs `TZ=ICT` cho S1.

## 5. Thực thi (theo bright-line "Fable = plan only")
| Bước | Ai | Model | Ghi chú |
|---|---|---|---|
| S2.1 + S2.2 + S3 (ccdb) + S2.3 (hook) + selfcheck | Wags | opus/high | cùng 1 dispatch; restart ccdb sau 15:05 hoặc giờ user chọn; arch-reviewer audit sau |
| S1 audit 70 file + bật TZ service | Taylor (data-ops) | opus/high | deliverable: bảng phân loại (a)/(b) + PR sửa (a) + lệnh bật + rollback |
| S4 detector + cron | Wags | opus/medium | chạy 7 ngày, báo Architecture topic |

Thứ tự: S2+S3 trước (rẻ, gỡ ngay lỗi đang thấy) → S1 sau audit → S4 chạy song song từ ngày 1 để đo baseline.

## 6. Cái giá / rủi ro
- S1: đổi nghĩa timestamp naive trong file máy-đọc nếu audit sót → vì vậy audit là gate, có rollback 1 dòng.
- S2: thêm ~25 token/lượt cho mọi agent (8 agent × N lượt) — chấp nhận được so với lỗi tiền/giờ giao dịch.
- S4: false-positive ban đầu → chỉ log, tinh chỉnh pattern theo ca thật trong 1 tuần.
