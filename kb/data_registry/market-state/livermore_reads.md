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
**Kích hoạt:** DT gate candidate >=5/10 hoặc >=15/25 phiên, hoặc VNINDEX chạm biên vùng lớn. **Khoảng cách tối thiểu 20 phiên giữa mọi lần đọc (chân 20 phiên không chồng); NGOẠI LỆ user duyệt 22/10: `DT_ENTER_*` (candidate vào CRISIS/EX-BULL ≥15/25) VƯỢT khoảng cách** để không bị câm vì một lần đọc giá đi trước. Entry `LIVE-BASELINE`/`MANUAL` không tính vào khoảng cách. Cron: T2-T6 19:05 ICT `bin/livermore_trigger_check.py`. Loại `livermore` nạp sau khi khởi động lại phiên; trước đó dùng general-purpose + đọc file định nghĩa.
**Cổng giải thể:** sau >=12 lần đọc sống đã chấm, giữ vai CHỈ KHI Livermore hơn CẢ BA baseline — đồng xu, "luôn UP", DT5G-implied (mỗi baseline: hit VÀ Brier, nghiêm ngặt); thua dù chỉ MỘT baseline ⇒ đề xuất giải thể (người quyết định).
**Thử mù lịch sử 22/10/2026:** 10/16 hit, Brier 0,231, không hơn "luôn UP" 11/16 ⇒ chưa chứng minh gì: `agents/Mike/research/livermore_blind_20261022/REPORT.md`.

## Entries
(chưa có lần đọc sống)

### LVR-2026-10-21
- as_of: 2026-10-21
- created: 2026-10-22T14:03:00+07:00
- trigger: LIVE-BASELINE
- close_asof: 1738.67
- due: 2026-11-18 (calendar=CONFIRMED)
- report: (đọc tay phiên Mike, không có file báo cáo riêng)
- dt5g_at_asof: 3
- note: LIVE-BASELINE, KHÔNG phải kích hoạt thật (DT gate candidate CRISIS 11/25 < ngưỡng 15/25). Định dạng chuyển 2026-10-22 để scorer chấm được; nội dung dự báo giữ nguyên, due tính lại đúng 20 phiên (bản gốc ghi "≈19/11"). dt5g_at_asof đọc 2026-10-22 từ vnindex_5state_dt5g_live (state công bố tại 21/10).
- note: Phân loại: 20 phiên markdown đang thử đáy (mơ hồ) · 60 phiên markdown (rõ) · 250 phiên range tam giác 1580–1933 (mơ hồ). Phiên 21/10 +2,76% vol 948M (1,46× TB20): "thrust thật nhưng CHƯA xác nhận"; cần đóng >1768.
- forecast:
    - H20_DIR: UP
    - H20_P_UP: 0.56
    - LEVEL: 1677 HOLD
    - INVALIDATION: đóng <1690 trong 5 phiên với vol ≥700M, hoặc bất kỳ phiên đóng <1677.
- result: RESULT|2026-10-21|UP|0.56|HOLD
- outcome:
