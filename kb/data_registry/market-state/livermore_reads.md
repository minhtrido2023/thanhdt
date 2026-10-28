---
kind: registry
status: CANONICAL
source: livermore (native agent, định nghĩa ~/.claude/agents/livermore.md) — đọc kỹ thuật VNINDEX độc lập, DISPLAY-ONLY
group: market-state
writer: Mike (orchestrator) ghi mỗi lần đọc; Livermore chỉ TRẢ KẾT QUẢ
role: Sổ append-only các lần đọc kỹ thuật tại điểm chuyển trạng thái; mỗi dòng có FORECAST khoá trước, chấm sau +20 phiên.
last_update: 2026-10-25 (thêm luật REPORT_BLOCK, nhánh feat/livermore-report-block-20261025 — chưa merge)
---
# Livermore reads (append-only)
**Quy tắc:** đọc MÙ (không DT5G, không dữ liệu sau as-of) · FORECAST: H20_DIR, H20_P_UP, LEVEL HOLD/BREAK, INVALIDATION · chỉ HIỂN THỊ (không sizing/gate) · Mike chấm sau +20 phiên.
**Kích hoạt:** DT gate candidate >=5/10 hoặc >=15/25 phiên, hoặc VNINDEX chạm biên vùng lớn. **Khoảng cách tối thiểu 20 phiên giữa mọi lần đọc (chân 20 phiên không chồng); NGOẠI LỆ user duyệt 22/10: `DT_ENTER_*` (candidate vào CRISIS/EX-BULL ≥15/25) VƯỢT khoảng cách** để không bị câm vì một lần đọc giá đi trước. Entry `LIVE-BASELINE`/`MANUAL` không tính vào khoảng cách. Cron: T2-T6 19:05 ICT `bin/livermore_trigger_check.py`. Loại `livermore` nạp sau khi khởi động lại phiên; trước đó dùng general-purpose + đọc file định nghĩa.
**REPORT_BLOCK (user duyệt 25/10/2026, `bin/livermore_report_block.py`):** mỗi weekly/monthly Livermore viết khối Kỹ thuật (số do script tính, kiểm số lạ cơ học, fail-closed; `report_delivery_gate.py::_check_livermore_block` chặn khối gắn tên Livermore không nguyên văn). Khoảng cách của REPORT_BLOCK đo từ lần đọc có forecast gần nhất **thuộc MỌI loại, kể cả `LIVE-BASELINE`/`MANUAL`** (chặt hơn cò trigger — chân 20 phiên không chồng): <20 phiên ⇒ chỉ nhắc lại nguyên văn; ≥20 ⇒ `livermore_run.sh --triggers REPORT_BLOCK_WEEKLY|REPORT_BLOCK_MONTHLY` ghi entry như thường. Entry `REPORT_BLOCK_*` **TÍNH** vào khoảng cách của `livermore_trigger_check.py` ⇒ chặn đọc trigger 20 phiên (trừ `DT_ENTER_*`), nên mẫu cổng giải thể sẽ chủ yếu là đọc THEO LỊCH chứ không phải tại điểm chuyển. Không lập forecast lùi ngày: báo cáo soạn trễ >5 phiên, hoặc sổ đã có entry sau as-of trong vòng 20 phiên ⇒ khối ghi "không có dự báo được lập cho kỳ này".
**Cổng giải thể:** sau >=12 lần đọc sống đã chấm, giữ vai CHỈ KHI Livermore hơn CẢ BA baseline — đồng xu, "luôn UP", DT5G-implied (mỗi baseline: hit VÀ Brier, nghiêm ngặt); thua dù chỉ MỘT baseline ⇒ đề xuất giải thể (người quyết định).
**Chốt user 25/10/2026 (`decided_by: user`):** (1) Livermore đảm nhận khối "Kỹ thuật" trong báo cáo weekly/monthly (`bin/livermore_report_block.py`, merge `ae1bbc9ba`); (2) các lần đọc THEO LỊCH (REPORT_BLOCK) CÓ tính vào cổng giải thể — chấp nhận kích hoạt thật ít đi; (3) `LVR-2026-10-21` (đọc tay) coi là đọc MÙ, không cần giải thích riêng cho nhà đầu tư.
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
