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

### 2026-10-21 (as-of) — LIVE-BASELINE (không phải kích hoạt thật; DT gate candidate CRISIS 11/25 < ngưỡng 15/25) — ghi 2026-10-22 14:03 ICT
Phân loại: 20 phiên markdown đang thử đáy (mơ hồ) · 60 phiên markdown (rõ) · 250 phiên range tam giác 1580–1933 (mơ hồ). Phiên 21/10 +2,76% vol 948M (1,46× TB20): "thrust thật nhưng CHƯA xác nhận"; cần đóng >1768.
FORECAST: H20_DIR=UP · H20_P_UP=0.56 · LEVEL=1677 HOLD · INVALIDATION=đóng <1690 trong 5 phiên với vol ≥700M, hoặc bất kỳ phiên đóng <1677.
Đáo hạn chấm: 20 phiên giao dịch sau 2026-10-21 (≈ 19/11/2026). Đối chiếu close 21/10 = 1738,67. Outcome: (chưa).
RESULT|LIVE-BASELINE-20261021|UP|0.56|HOLD
