# Pilot đánh giá `srcwalk` — tra cứu code Python bằng AST thay vì grep+Read

> Status: PILOT ĐANG CHẠY (bắt đầu 2026-08-01). Không phải dự án đã đóng — file này track tới khi
> có quyết định giữ/bỏ, lúc đó chuyển ghi chú đóng vào `kb/projects/INDEX.md` như thường lệ.

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
