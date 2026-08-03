# Pilot đánh giá `srcwalk` — tra cứu code Python bằng AST thay vì grep+Read

> **Status: ĐÓNG SỚM 2026-08-03 — user chỉ đạo mở toàn fleet, KHÔNG chờ hết cửa sổ 3 tuần.**
> Pilot chạy 2026-08-01 → 2026-08-03 (2 ngày), `srcwalk_pilot_log.jsonl` **0 dòng** (Taylor chưa
> dùng thật lần nào). Theo ngưỡng gốc bên dưới, "<3 lần dùng thật" đáng lẽ = tín hiệu BỎ; user
> quyết định ngược lại và đó là quyền của user — ghi lại đây cho minh bạch, không phải để phản đối.

## Quyết định 2026-08-03 (thay thế phần "Phạm vi pilot" bên dưới)
- **Cài dạng skill**: `~/.claude/skills/srcwalk/` (SKILL.md + GUIDE.md từ repo upstream, version
  khớp binary). Binary `~/.local/bin/srcwalk` **v1.3.0** (tarball musl tĩnh, thay bản npm của pilot).
- **Phạm vi**: TOÀN FLEET (8 agent), làm công cụ đọc code mặc định thay Read/grep.
- **Docs đã sửa**: `WorkingClaude/CLAUDE.md` § Code navigation (nguồn chi tiết duy nhất),
  `kb/coding_guidelines.md` §18b, `agents/*/CLAUDE.md` (8 file).
- **Bỏ cơ chế log JSONL** — không còn đo pilot nữa.

## ⚠️ 3 lỗi của pilot ĐÃ VERIFY LẠI TRÊN v1.3.0 (2026-08-03) — VẪN CÒN, không được coi là đã fix
Mike chạy lại đúng các test của pilot trên binary mới:
1. **`trace callers --depth ≥2` / khối "impact"**: `srcwalk trace callers filter_lag_rating_orders
   --scope . --depth 2` → **496 cạnh hop-2**, gần như toàn rác (mọi `main()`, mọi `run(...)`, kể cả
   `subprocess.run(...)` bị khớp là caller của `run`). Ngay ở `--depth 1`, khối "impact" đã có false
   positive `setup_gmail_oauth.py:81`. Hop-1 (4 call site trực tiếp) thì ĐÚNG.
   → Chỉ dùng `--depth 1`, chỉ đọc danh sách call-site trực tiếp, verify blast-radius bằng `grep`.
2. **`review` bỏ sót hàm mới thêm**: trên `d64717f`, hunk `trading_bot/plan.py:509-598` (nơi
   `filter_lag_rating_orders` được THÊM ở 532-604) bị gắn nhãn `file-level`; "changed symbols" chỉ
   liệt kê `main` + `lag_filter_low_rating`. Hunk nằm TRONG hàm có sẵn thì gắn context đúng.
   → `git diff` là nguồn chuẩn tắc cho change set.
3. **Bash vẫn không được hỗ trợ**: `srcwalk bin/dispatch.sh` (1244 dòng) chỉ in comment header dạng
   raw preview, không có outline symbol; `srcwalk discover <fn> --scope bin` chỉ trả về định nghĩa
   Python, không thấy hàm bash nào. `mike/bin/` = **63 `.sh` vs 46 `.py`** → phần lớn khối lượng đọc
   file hạ tầng của fleet KHÔNG hưởng lợi từ công cụ này.

**Việc nên làm sau này**: khi lên version srcwalk mới, chạy lại đúng 3 test trên TRƯỚC khi nới lỏng
bất kỳ cấm đoán nào — đừng tin changelog.

---
> _Phần dưới là nội dung pilot gốc (2026-08-01), giữ nguyên làm hồ sơ._

## Bối cảnh
User yêu cầu tham khảo `github.com/sting8k/srcwalk` (công cụ CLI dùng tree-sitter để tra symbol
theo AST, thay cho text-match thuần của grep) và đánh giá xem cách đọc file hiện tại của fleet
(grep + Read, skill `token-saver`, OKF cho markdown) có nên cải thiện theo hướng này không.

**Đã tự cài + test tay thật (không tin README/benchmark suông) trước khi quyết định pilot:**
- `discover cap_lag_orders` — kết quả tốt hơn grep: tự cho biết mỗi lần xuất hiện nằm TRONG hàm
  nào (điều grep không có), giá ~338 token vs vài chục token của grep thuần cho câu hỏi tương
  đương — đắt hơn nhưng ngữ cảnh giàu hơn thật.
- `trace callers filter_lag_rating_orders` — **bắt được 1 lỗi thật**: phần "2nd hop impact" khớp
  nhầm theo TÊN HÀM CHUNG CHUNG (`main`, `run`) xuyên file hoàn toàn không liên quan (báo
  `dcf_fv_sens_cache.py` "bị ảnh hưởng" bởi thay đổi ở `bot_execute.py` — verify bằng grep xác
  nhận SAI, 2 file không gọi nhau). Claim "N hàm bị ảnh hưởng qua 2 hop" bị thổi phồng.
- `review` trên commit `d64717f` thật (P1/P0 domain-constraint) — nhận diện đúng file/hunk/class
  bao quanh nhưng BỎ SÓT gắn tên hàm mới (`filter_lag_rating_orders`) vào bằng chứng diff.
- **Không hỗ trợ Bash** — gap lớn vì `mike/bin/` (hạ tầng fleet tự quản) có 53 file `.sh` vs 37
  file `.py`; bash nhiều hơn Python ngay trong chính thư mục cốt lõi.
- Markdown chỉ có "document navigation" cơ bản — không thay được việc phân tích ngữ nghĩa mà OKF
  (data_registry/cron_registry/canonical.md/INCIDENTS.md, 2026-07-30) đã chứng minh cần hiểu NỘI
  DUNG chứ không chỉ cấu trúc.

**Kết luận ban đầu**: không áp dụng toàn hệ thống — phạm vi lệch (bash/markdown chiếm phần lớn
khối lượng đọc-file thực tế của fleet) và có lỗi thật ở đúng tính năng cốt lõi nhất (call-graph).
Chỉ 2 lệnh `discover`/`show` cho thấy giá trị rõ trên Python.

## Phạm vi pilot
- **Agent**: chỉ Taylor (chủ sở hữu phần lớn code Python: `trading_bot/`, script nghiên cứu).
- **Lệnh cho phép**: CHỈ `srcwalk discover` và `srcwalk show`. **CẤM** `trace`/`review` (lỗi đã
  biết) cho tới khi có xác nhận độc lập khác.
- **Phạm vi file**: Python trong `trading_bot/` + script nghiên cứu. KHÔNG áp dụng cho bash
  (không hỗ trợ) hay markdown (giá trị thấp hơn quy trình OKF thủ công đang dùng).
- Cài đặt: `~/.local/bin/srcwalk` (npm, đã verify có trên PATH cho dispatch qua `bash -lc` +
  crontab thật — `PATH=.../home/trido/.local/bin/...` đã có sẵn trong crontab).

## Cơ chế đo — log THẬT, không dựa tự báo cáo cảm tính
Taylor ghi 1 dòng JSONL mỗi lần dùng thật vào `mike/agents/Taylor/srcwalk_pilot_log.jsonl`
(lệnh mẫu trong `agents/Taylor/CLAUDE.md` §PILOT). Mỗi dòng: timestamp, lệnh, mô tả việc, có
hữu ích hơn grep+Read không (true/false), 1 câu lý do.

## Thời hạn & ngưỡng quyết định
- **Cửa sổ**: 3 tuần (tới ~2026-08-22) HOẶC đủ **≥8 lần dùng thật**, cái nào tới trước.
- Nếu **<3 lần dùng thật** sau 3 tuần → tự nó là tín hiệu: KHÔNG đủ giá trị để agent chủ động
  chọn dùng thay vì phản xạ cũ (grep) → **BỎ**, không cần đo thêm gì.
- Nếu **≥8 lần** → Mike đọc log + tự spot-check lại 2-3 dòng bất kỳ (chạy lại lệnh, xác nhận kết
  quả đúng như Taylor ghi — đúng kỷ luật "verify artifact, không tin self-report" cả ngày
  2026-07-30 đã áp dụng), rồi quyết:
  - **GIỮ** (mở rộng phạm vi lệnh/agent khác) nếu: ≥70% lần dùng thật được đánh dấu hữu ích THẬT
    (verify được, không chỉ Taylor tự nói), VÀ 0 lần phát hiện thêm lỗi accuracy kiểu như
    `trace`/`review` đã có.
  - **GIỮ NGUYÊN PHẠM VI HẸP** (không mở rộng, không bỏ) nếu hữu ích nhưng hiếm dùng hoặc giá trị
    biên nhỏ — không đáng công sức mở rộng nhưng cũng không hại gì để Taylor tiếp tục dùng.
  - **BỎ HẲN** (gỡ `srcwalk`, xoá mục PILOT khỏi CLAUDE.md) nếu phát hiện thêm lỗi accuracy MỚI
    trong lúc dùng thật, hoặc log cho thấy phần lớn lần dùng không thực sự tiết kiệm gì so với
    grep+Read (Taylor tự nhận trong `note`).
- Không qua arch-review/quant-skeptic — đây là công cụ hỗ trợ R&D, không chạm production/tiền
  thật, quyết định ở mức Mike + log thật là đủ cân xứng rủi ro.

## Việc Mike cần tự nhắc
Đặt lịch xem lại vào ~2026-08-22 (hoặc sớm hơn nếu thấy `srcwalk_pilot_log.jsonl` đã có ≥8 dòng).
Nếu quên, `kb_nightly.sh` Friday editorial review sẽ không tự nhắc việc này (chưa wire) — ghi vào
`kb/memory/Mike.md` làm lưới an toàn.
