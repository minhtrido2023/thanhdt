---
kind: registry
status: CANONICAL
source: livermore (native agent, định nghĩa ~/.claude/agents/livermore.md) — đọc kỹ thuật VNINDEX độc lập, DISPLAY-ONLY
group: market-state
writer: Mike (orchestrator) ghi mỗi lần đọc; Livermore chỉ TRẢ KẾT QUẢ
role: Sổ append-only các lần đọc kỹ thuật tại điểm chuyển trạng thái; mỗi dòng có FORECAST khoá trước, chấm sau +20 phiên.
last_update: 2026-10-22 (tạo; user duyệt, tên do user đặt)
---
# Livermore reads (append-only)
**Quy tắc:** đọc MÙ (không DT5G, không dữ liệu sau as-of) · FORECAST: H20_DIR, H20_P_UP, LEVEL HOLD/BREAK, INVALIDATION · chỉ HIỂN THỊ (không sizing/gate) · Mike chấm sau +20 phiên.
**Kích hoạt:** DT gate candidate >=5/10 hoặc >=15/25 phiên, hoặc VNINDEX chạm biên vùng lớn. Loại `livermore` nạp sau khi khởi động lại phiên; trước đó dùng general-purpose + đọc file định nghĩa.
**Cổng giải thể:** sau >=12 lần đọc sống đã chấm, nếu không hơn đồng xu (hit, Brier) VÀ "luôn UP" VÀ DT5G-implied ⇒ bỏ vai.
**Thử mù lịch sử 22/10/2026:** 10/16 hit, Brier 0,231, không hơn "luôn UP" 11/16 ⇒ chưa chứng minh gì: `agents/Mike/research/livermore_blind_20261022/REPORT.md`.

## Entries
(chưa có lần đọc sống)
