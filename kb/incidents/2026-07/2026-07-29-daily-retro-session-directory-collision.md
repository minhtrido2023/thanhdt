---
kind: incident
date: 2026-07-29
topic: daily-retro-session-directory-collision
title: >-
  2026-07-29: daily_retro root-cause fix — session-directory collision (Pattern A closed)
status: open-items
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-29: daily_retro root-cause fix — session-directory collision (Pattern A closed)

**Bối cảnh:** Pattern A ("Mike trả lời nhầm task cũ" ở Bước 1 draft) đã bị RETRO 07-18/07-19 gọi
tên 2 lần, mitigated bằng retry (commit `9fd7913`, 07-28) nhưng chưa có gate cơ khí thật —
đúng "Prevention #1" còn treo trong RETRO 07-28. Trong lúc user hỏi Mike đánh giá 2 đề xuất
tiết kiệm token (không liên quan), job `Mike_20260729_173001` (dispatch Bước 1 thật, ~17:30 ICT)
tái diễn Pattern A ngay trước mắt: rc=0 nhưng draft KHÔNG được tạo, log cho thấy Mike trả lời về
"theo dõi job Taylor" — nội dung này khớp CHÍNH XÁC với hội thoại sống của phiên Mike Discord
đang chạy cùng lúc.

**Root cause tìm ra (không phải model flakiness như giả định trước đây):** `hooks/session_start.sh`
gọi `bin/recap_prev.py`, tự nhận "most recent OTHER transcript trong cwd của agent" là phiên
trước của CHÍNH agent đó — đúng cho mọi agent khác (cwd của họ chỉ chứa các headless dispatch
tuần tự, không ai khác ghi vào). **Sai riêng cho Mike**: cwd `agents/Mike` được CẢ live companion
session (Discord) LẪN mọi headless dispatch (`dispatch.sh Mike ...`, vd daily_retro.sh,
kb_nightly.sh) dùng chung — `dispatch.sh` tự `cd "$AGENT_DIR"` trước khi gọi `claude -p`. Khi 1
headless dispatch khởi động trong lúc live companion đang hoạt động (transcript mới ghi gần
nhất), `recap_prev.py` chọn NHẦM transcript SỐNG làm "phiên trước", nhét 6 lượt cuối của hội
thoại KHÔNG LIÊN QUAN vào context của task headless — mô hình tự nhiên có thể "làm nốt" mạch cũ
(theo dõi job Taylor) thay vì viết draft mới. Đây chính là cơ chế đứng sau CẢ 4 lần Pattern A đã
ghi nhận (07-17, 07-19, 07-26, 07-27) và lần thứ 5 hôm nay.

**Fix (2 lớp, cả 2 đã verify syntax + logic bằng tay, dry-run 3 case Mike-headless/Mike-live/
Taylor):**
1. **Root cause** — `hooks/session_start.sh`: chỉ gọi `recap_prev.py` khi (agent ≠ Mike) HOẶC
   (Mike VÀ `INTERACTIVE_TID` non-empty — tín hiệu "đây là live companion", đã có sẵn trong hook
   từ trước để phân biệt dispatch headless vs phiên sống, tái dùng chứ không thêm cơ chế mới).
   Headless Mike dispatch giờ luôn khởi động sạch, không còn khả năng thừa hưởng hội thoại sống.
2. **Defense-in-depth** — `bin/daily_retro.sh` Bước 1: thêm `_draft_valid()` — draft phải
   non-empty VÀ chứa đúng header `## RETRO — <ngày>` mà prompt yêu cầu, thay vì chỉ kiểm tra
   non-empty. Draft sai định dạng bị đổi tên thành `retro_draft_<ngày>_rejected_a<n>.md` (giữ để
   chẩn đoán, không xoá) rồi retry; sau 2 lần vẫn sai → escalate `question` như cũ, kèm trích dẫn
   file rejected. Đây là gate cơ khí RETRO 07-18/07-19/07-28 đã đề xuất, nay mới cài thật.

**Đóng "Prevention #1" của RETRO 07-28.** Chưa self-check bằng 1 lần chạy `daily_retro.sh` thật
(sẽ tự verify ở lần chạy 00:30 ICT kế tiếp, hoặc có thể trigger tay để xác nhận sớm hơn nếu cần).
Chưa qua quant-skeptic/Wags review độc lập — nên làm trước khi coi đây là "đóng hoàn toàn", vì
đây là thay đổi vào cơ chế lõi (`session_start.sh`) ảnh hưởng MỌI headless dispatch tới Mike,
không chỉ riêng daily_retro.
