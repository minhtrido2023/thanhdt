# Cổng "chờ duyệt" cho file kb/ — điều tra + draft (job Wags_20260730_143925)

Sự cố nguồn: `bin/consolidate.sh` (cron :07 mỗi giờ + tự chạy sau MỌI dispatch) làm
`git add kb/` + `git commit -- kb/` BLANKET ⇒ file `kb/` một agent cố ý để chưa commit
chờ Mike đọc diff bị cuốn vào commit "consolidate KB vNNNN" trong vài chục giây.
Lần xảy ra thật: job `Winston_20260730_142006` → commit `8215e3b8` (mang theo
`kb/KNOWLEDGE.md` + `kb/canonical.md`). Nội dung hoá ra đúng, nhưng cổng review bị bỏ qua.

## 1. Điều tra — có luồng nào ĐANG dựa vào blanket sweep không? CÓ

Không grep suông; đếm thực tế path `kb/` xuất hiện trong 400 commit "consolidate" gần nhất:

| path | số commit /400 | ai ghi | ai commit nếu bỏ blanket |
|---|---|---|---|
| events_buffer.md, version.txt, context_pack.md, fleet_status.md, recent_delta.jsonl | 294–399 | chính consolidate.sh / publish_context.sh | tự nó (allowlist OK) |
| **kb/memory/&lt;id&gt;.md** | **214** | `bin/remember.sh` (Stop hook, mỗi lượt, MỌI agent) | **KHÔNG AI** |
| kb/data_registry/* | 18 | agent (Write tool) | KHÔNG AI |
| current_ops.md | 13 | Mike/agent | KHÔNG AI |
| INCIDENTS.md | 7 | daily_retro/agent | KHÔNG AI |
| data_registry.md, cron_registry.md, canonical.md, projects/*, context_planning_mini.md, ops_runbook.md, KNOWLEDGE.md | 1–4 mỗi loại | agent/Mike | KHÔNG AI |

⇒ **Allowlist thuần bị loại**: `remember.sh` ghi working memory rồi không commit — đó là luồng
write-and-wait **thật, cơ khí hoá, chạy mỗi lượt của mọi agent**; cộng thêm ~7 nhóm file tri thức
do agent ghi bằng Write tool cũng không có script committer nào. Allowlist sẽ để chúng bẩn
working tree cả ngày cho tới khi `fleet_backup.sh` (00:00 ICT, `git add -A`) cuốn hết bằng
message "fleet backup" — đổi một sweep vô duyệt lấy một sweep vô duyệt khác, tệ hơn.

## 2. Phát hiện thêm (quan trọng hơn cả git): harm "live ngay trong context_pack" KHÔNG do git

`bin/publish_context.sh` `cat` **THẲNG file working-tree** `current_ops.md`, `canonical.md`,
`projects/INDEX.md` vào `context_pack.md` — file mọi dispatch nạp đầu phiên.
⇒ Một bản sửa dở đã LIVE cho cả fleet ở lần consolidate kế tiếp **kể cả khi không có commit nào**.
Chặn `git add` chỉ chặn việc GHI NHẬN; muốn chặn PHÁT TÁN phải sửa cả publish. Cổng chỉ kín khi
làm cả hai — đây là lý do draft chạm 2 file chứ không phải 1.

## 3. Hướng đã chọn: HOLD-LIST (opt-in), cả ở git lẫn ở publish

- `state/kb_pending_review.txt` (state/ đã gitignore) — mỗi dòng: `<kb/path> <ISO-ts> <agent> <note>`.
- `bin/kb_hold.sh add|release|list|held` — API cho agent, không sửa file txt bằng tay.
- `consolidate.sh`: dựng pathspec `kb/` + `:(exclude)<path>` cho **cả `add` lẫn `commit`**
  (commit không pathspec sẽ cuốn cả index — path bị hold mà đã lỡ staged từ trước vẫn thoát).
- `publish_context.sh`: path bị hold → xuất **bản ĐÃ COMMIT gần nhất** (`git show HEAD:<path>`)
  + 1 dòng ⚠️ "ĐANG CHỜ DUYỆT" hiện trong context_pack của mọi dispatch (áp lực tự nhiên để đóng).
- **TTL** mặc định 6h (`KB_HOLD_TTL_HOURS`): quá hạn → `notify.sh` + bus event `question` cho Mike,
  debounce 3h/path (khuôn `state/cursorwarn` sẵn có). **KHÔNG tự nhả** — tự nhả = commit đúng thứ
  đang cần duyệt, phá chính cổng này. Không giữ vô thời hạn *im lặng*: nó kêu, người quyết định.
- Fail-safe: dòng hold rác / path ngoài `kb/` / có `..` → bỏ qua + log `HOLD-BADPATH` ⇒ quay về
  hành vi CŨ (vẫn commit), không bao giờ im lặng ngừng commit.

## 4. Test — `python3 bin/kb_hold_selfcheck.py.draft` → **31/31 PASS**

Sandbox riêng (git riêng, bus riêng, `/tmp`), chạy chính các file draft, KHÔNG chạm repo thật.
- **A** case hôm nay: file hold không bị commit, git vẫn giữ bản đã duyệt, bản sửa dở còn nguyên
  trên đĩa, context_pack **không** chứa nội dung chưa duyệt, file kb/ khác vẫn publish bình thường.
- **B** không có hold → `kb/memory/<id>.md` vẫn được commit (luồng remember.sh không vỡ).
- **C** file hold đã lỡ `git add` từ trước → vẫn không bị commit.
- **D** TTL: có notify + bus event, **không** tự nhả, **không** tự xoá khỏi hold-list, debounce chạy đúng.
- **E** hold-list có rác → chạy bình thường, log HOLD-BADPATH, kb/ vẫn commit (fail-safe).
- **F** sau `release` → commit + publish lại bình thường.
- **G** **đối chứng LIVE vs DRAFT** cùng sandbox/cùng event/không hold: **tập file commit giống hệt
  và nội dung context_pack giống hệt** ⇒ bằng chứng không hồi quy so với bản đang chạy thật.

## 5. Lỗ còn lại — cần Mike quyết (CHƯA làm, ngoài scope job này)

Hold **chỉ** được `consolidate.sh` tôn trọng. Hai sweeper blanket khác vẫn còn:
- `fleet_backup.sh` 00:00 ICT — `git add -A` (toàn repo).
- `kb_nightly.sh` 02:00 ICT — `git add kb/`.

Hệ quả cụ thể: nếu hold kéo qua 00:00, `fleet_backup` commit file đó ⇒ `git show HEAD:<path>` từ
đó trả về **nội dung chưa duyệt** ⇒ cổng publish cũng bị mở luôn. TTL 6h được chọn để kêu TRƯỚC
khi cửa sổ này đóng, nhưng đó là giảm nhẹ, không phải bịt.
Đề xuất bịt: đưa đúng pathspec `:(exclude)` vào cả 2 script (mỗi chỗ ~3 dòng, dùng lại khối parse
của consolidate). Đánh đổi: file đang hold **không được backup** tối đa tới TTL. Cần Mike duyệt vì
nó đổi ngữ nghĩa backup (durability), không phải thuần điều phối.

Rủi ro vận hành còn lại (đã có giảm nhẹ, nêu để minh bạch): quên `release` sau khi duyệt ⇒ fleet
đọc bản cũ. Giảm nhẹ = dòng ⚠️ hiện trong context_pack mọi dispatch + TTL alarm 6h.

## 6. Trạng thái file

| file | trạng thái |
|---|---|
| `bin/consolidate.sh.draft` | draft, 644, chưa live |
| `bin/publish_context.sh.draft` | draft, 644, chưa live |
| `bin/kb_hold.sh.draft` | draft, 664, chưa live |
| `bin/kb_hold_selfcheck.py.draft` | test, chạy bằng `python3 <file>` |

`bin/consolidate.sh` / `bin/publish_context.sh` **LIVE vẫn nguyên vẹn** (`git diff HEAD` rỗng).
Chờ Mike đọc + arch-review trước khi áp (đúng discipline `fleet_housekeeping.sh` hôm nay).

Ghi chú nhỏ: dispatch dẫn "coding_guidelines.md §10" cho quy ước `.sh.draft` — §10 thực tế nói về
archive các biến thể khi 1 file thành canonical; trong `kb/coding_guidelines.md` hiện KHÔNG có mục
nào định nghĩa quy ước draft. Vẫn làm đúng theo chỉ đạo (draft, không executable); nếu quy ước này
là chính thức thì nên viết hẳn thành 1 mục để lần sau không phải suy đoán.
