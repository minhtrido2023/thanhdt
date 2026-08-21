# PLAN — Timestamp & format Discord: ép đúng BẰNG CẤU TRÚC, không bằng dặn dò LLM

> Mike, 2026-08-21 18:15 ICT. Trạng thái: **PLAN, chưa sửa gì**. User yêu cầu: "format và thông tin thời
> gian có vấn đề — lỗi cố hữu LLM, đã dặn nhưng vẫn lặp. Thiết kế kiến trúc để không còn lặp. Chỉ lên plan."

## 0. Bằng chứng lỗi lặp (cùng ngày, SAU khi đã có skill `discord-timestamp` 08-20)

| Lúc (ICT thật) | Thread | LLM viết | Lỗi | Nguyên nhân đo được |
|---|---|---|---|---|
| 17:26 21/08 | Corp action research | `03:25 sáng ngày 21/08/2026` | sai 14h | transcript `bd1924de…`: **không có tool call `date` nào** trong 40 record trước đó → LLM nhẩm từ UTC 10:25 rồi **trừ** 7h thay vì cộng |
| 09:47 21/08 | topic này | `09:xx sáng ngày 21/08/2026` | `xx` literal | LLM biết phải có dòng đó nhưng lười gọi `date`, điền placeholder |
| 08-20 | nhiều | `_(10:12 ICT)_` cuối message | UTC dán nhãn ICT | đã ghi trong skill |
| 08-20 | — | ETA wakeup "~10:12 ICT" | UTC dán nhãn ICT | đã ghi trong skill |

Kết luận: quy tắc đã đủ rõ, đã có ví dụ sai, vẫn vi phạm **2 lần trong 1 ngày**. Đây không phải lỗi
"chưa dặn kỹ" — đó là lớp lỗi **không sửa được bằng văn xuôi** vì nó xảy ra đúng lúc LLM bỏ qua 1 tool
call và tự suy luận. Cùng loại với §22 / enforcement policy trong `coding_guidelines.md`: *"đẩy bài học
cũ ra công cụ thay vì văn xuôi"*.

## 1. Nguyên tắc thiết kế (1 câu)

**Thứ gì tất định tại thời điểm gửi thì TẦNG VẬN CHUYỂN làm, LLM không được làm — và nếu LLM lỡ làm
thì tầng vận chuyển ghi đè.** Timestamp là tất định 100% lúc `send()`; chuẩn hoá markdown cho Discord
cũng tất định. Cả hai chuyển khỏi prompt vào code, ở **đúng 2 choke point** mà 100% tin nhắn Discord của
fleet đi qua.

## 2. Hai choke point (đã verify bằng grep, 2026-08-21)

| # | Đường đi | Nơi sửa (ccdb, repo `/workspace/claude-code-discord-bridge`) | Phủ |
|---|---|---|---|
| A | Reply tương tác của mọi session (Mike ở mọi topic) | `claude_discord/cogs/event_processor.py` — nhánh RESULT `chunk_message(response_text)` → `_send_thread_message` (~L623) | 100% reply LLM |
| B | Mọi script fleet: `bin/notify_thread.sh` (**57 caller**) + `_bg_wrapper` của dispatch + cron | `claude_discord/ext/api_server.py::notify` (`/api/notify`, L478) `fmt=="text"` → `target.send(message)` | 100% post từ script |

Không có đường thứ 3: grep `discord.com/api|CCDB_API_URL` trong `mike/bin` + root chỉ ra notify_thread
(+ 1 selfcheck, 1 cleanup script không post text). Fleet KHÔNG cần sửa 57 caller — chỉ sửa ccdb.
Trong fleet chỉ **1** script tự viết timestamp kiểu này (`dividend_adjusted_return.py`) — LLM là
nguồn chính của lỗi, đúng như giả thuyết.

## 3. Thiết kế — module `claude_discord/discord_ui/outbound_format.py` (hàm thuần, ~80 dòng)

```
format_outbound(text, *, stamp: bool, now: datetime|None=None) -> str
```
Gọi từ A và B, thứ tự cố định:

1. **Strip mọi dấu giờ do LLM tự viết** (regex, fail-safe rộng):
   - dòng đầu khớp `^\d{1,2}:\d{2}\s+(sáng|chiều|tối)\s+ngày\s+\d{2}/\d{2}/\d{4}` **kể cả biến thể
     lỗi** `\d{1,2}:(\d{2}|xx|XX)` → xoá;
   - dòng cuối khớp `^_\(\d{1,2}:\d{2}\s*ICT\)_$` → xoá (mẫu 08-20 đã bị reject).
   Ghi 1 dòng log `outbound_format: stripped_llm_stamp=<chuỗi> true=<HH:MM>` → đây chính là **đồng hồ
   đo tỉ lệ LLM viết sai**, miễn phí.
2. **Chuẩn hoá markdown Discord** (chỉ luật tất định, không "làm đẹp"):
   - dòng `---` / `***` / `___` (hr) → xoá (Discord in nguyên văn — thấy rõ trong ảnh user);
   - `####`+ → `**…**` (Discord chỉ hỗ trợ `#`/`##`/`###`);
   - ≥3 dòng trống liên tiếp → 2.
   Bảng GFM đã có `_wrap_tables_in_fences` trong `chunker.py` — giữ nguyên, không đụng.
3. **Đóng dấu thật** nếu `stamp=True`: prepend `HH:MM sáng|chiều|tối ngày DD/MM/YYYY` tính từ
   `datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))` (§16 coding_guidelines — không tin TZ hệ thống),
   đúng format skill đã chốt 08-20 (sáng 00–11, chiều 12–17, tối 18–23). Chỉ chunk đầu tiên có dấu.
4. Không stamp khi message là **subtext** (`-# …` heartbeat/progress) hoặc rỗng — luật cơ học, không
   cần caller khai gì.

### Chính sách `stamp` theo đường đi
- A (RESULT cuối lượt): `stamp=True`. Tin **TEXT giữa lượt** (narration "Thấy vấn đề rồi…", L776):
  `stamp=False` nhưng vẫn chuẩn hoá markdown — tránh 6 dấu giờ cho 1 lượt. *(Điểm cần user chốt, §7a.)*
- B (`/api/notify` text): `stamp=True` mặc định; field JSON `"stamp": false` để opt-out;
  `notify_thread.sh` thêm cờ `--no-stamp` truyền xuống (dùng cho ping tiến độ ngắn nếu muốn).
  Embed (`fmt=embed`): set `embed.timestamp` (Discord tự hiển thị theo giờ người xem) thay vì chèn chữ.

### Lớp "belt" bổ trợ (giảm xác suất LLM nhẩm sai giờ ở chỗ KHÔNG mechanize được — ETA)
- ccdb prepend vào prompt mỗi lượt 1 dòng context ẩn: `[now: 17:26 chiều 21/08/2026 ICT]` (đã có chỗ
  ccdb bơm context hệ thống). LLM có giờ đúng mà không cần tool call → ETA đúng gốc.
- Khi LLM gọi `ScheduleWakeup(delay)`, **ccdb** tự post `-# ⏰ tự quay lại ~HH:MM ICT` (tính từ delay,
  tất định) và prompt nói: "KHÔNG tự nêu giờ ETA — bridge đã in". Đóng nốt lỗi ETA 08-20.
- Export `TZ=Asia/Ho_Chi_Minh` cho tiến trình claude mà ccdb spawn (hiện máy đã ở +07 nhưng không
  nên dựa vào host — §16).

## 4. Tháo prose (SUBTRACTIVE — bắt buộc, không làm là vẫn lỗi)
Khi code đã ép, **gỡ** quy tắc "dòng đầu phải là timestamp" khỏi `MIKE.md` §Kỷ luật tương tác,
`~/.claude/skills/discord-timestamp/SKILL.md`, prompt agent (Wags/Taylor/DollarBill). Thay bằng
**1 dòng**: *"KHÔNG tự viết giờ hiện tại/timestamp vào message — bridge tự đóng dấu ICT. Cần nêu giờ
(ETA/lịch) thì đọc từ dòng `[now: …]` của lượt, không nhẩm."* Lý do phải gỡ: để lại quy tắc cũ ⇒ LLM
vẫn cố viết ⇒ formatter phải strip mỗi lần (vẫn đúng, nhưng tốn token + log nhiễu), và quy tắc ngược
chiều nhau trong prompt là nguồn lỗi mới. Bớt ~40 dòng prompt auto-load.

## 5. Kiểm chứng & đo (không "tin là đúng")
- **pytest ccdb** cho `format_outbound`: 10 ca — strip đúng 4 biến thể (kể cả `xx`), không strip giờ
  nằm giữa câu, hr bị xoá, `####`→bold, subtext không stamp, chunk 2 không stamp, embed có
  `timestamp`, `now` giả ở 3 khung sáng/chiều/tối, TZ=UTC giả lập vẫn ra +07 (chạy dưới `env -u TZ`
  + `TZ=UTC` theo skill `verify-before-done`).
- **Selfcheck fleet** `bin/discord_outbound_format_selfcheck.py`: import module ccdb trực tiếp (cùng
  venv) và so format string với SKILL.md — drift giữa doc và code ⇒ đỏ. Vào `selfcheck_baseline.json`.
- **Metric**: `daily_retro.sh` đếm `stripped_llm_stamp` trong journal ccdb (mục 2e mới) — kỳ vọng
  **giảm về ~0** sau khi gỡ prose (§4); không giảm ⇒ prompt nào đó vẫn bảo LLM viết giờ → tìm và gỡ.
- **Kiểm tra đầu-cuối 1 lần sau restart**: post 1 tin qua `notify_thread.sh` + 1 reply Mike, đối
  chiếu dấu với giờ Discord hiển thị (chính cách user phát hiện lỗi).

## 6. Trình tự triển khai (≈ 1 buổi, 1 restart ccdb ngoài giờ giao dịch)
1. ccdb: module + 2 call site + tests (commit, **không** restart ngay).
2. Fleet: `notify_thread.sh --no-stamp` (passthrough field), selfcheck, `daily_retro` 2e, gỡ prose
   §4, cập nhật skill → commit.
3. Restart `ccdb-mike` sau 15:05 ICT (hoặc sớm hơn nếu 0 session/job như lần 08-21 12:39).
4. Kiểm tra đầu-cuối §5, post kết quả, ghi `kb/current_ops.md` 1 dòng + incident note ngắn
   (`kb/incidents/2026-08/2026-08-21-discord-stamp-by-construction.md`).

## 7. Điểm cần user chốt trước khi làm
a. **TEXT giữa lượt** (narration) có đóng dấu không? Đề xuất **KHÔNG** (chỉ reply cuối + mọi post
   từ script) — tránh 5-6 dấu giờ/lượt.
b. **Kiểu dấu**: giữ dòng thường `17:26 chiều ngày 21/08/2026` (anh chốt 08-20) hay chuyển sang
   subtext xám nhỏ `-# 17:26 chiều ngày 21/08/2026`? Đề xuất **giữ dòng thường** (không đổi thứ anh đã
   chọn); subtext là 1 ký tự đổi nếu sau này muốn nhẹ mắt.
c. Telegram (`notify.sh`) có áp cùng formatter không? Đề xuất **chưa** — ngoài phạm vi lỗi đang thấy.

## 8. Ngoài phạm vi (nói rõ để không hiểu lầm "đã xử lý")
Độ dài/cấu trúc nội dung (wall-of-text, bao nhiêu heading) **không** tất định → không ép bằng code;
vẫn là chuyện prompt + review. Plan này chỉ đóng lớp lỗi **tất định nhưng bị giao nhầm cho LLM**:
giờ, múi giờ, ký hiệu markdown Discord không render.
