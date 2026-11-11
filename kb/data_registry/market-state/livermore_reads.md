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

### LVR-STK-2026-11-05-FPT  (đọc SỐNG theo MÃ — vai mới: giữ cửa quyết bán FPT, user 05/11/2026)
- as_of: 2026-11-05 · close_asof: 52900 · created: 2026-11-05T22:40:00+07:00 · trigger: USER-ASSIGNED (không bị khoảng cách 20 phiên của VNINDEX)
- due: H20 2026-12-03 (lịch giao dịch) · cửa sổ chạm 25 phiên đến 2026-12-10
- classification: 20 MARKDOWN (mơ hồ, có dấu dừng sớm) / 60 MARKDOWN (rõ) / 250 MARKDOWN (rõ); đỉnh 97.480 (19/01), đáy 49.550 (03/11)
- forecast:
    - H20_DIR: DOWN
    - H20_P_UP: 0.45
    - LEVEL: 58700 HOLD (không đóng cửa > 58.700 trong 20 phiên)
    - INVALIDATION: đóng > 56.000 với vol ≥1,5× v20 và giữ 2 phiên
    - P_TOUCH_PLUS10: 0.27 (high ≥ 58.190 trong 25 phiên)
    - P_TOUCH_MINUS10: 0.30 (low ≤ 47.610 trong 25 phiên)
    - SELL_VIEW_AT_PLUS10: SELL mặc định (cung 56,0–58,7k); HOLD chỉ khi test lại 49,55–51k giữ <0,7× v20 VÀ đóng >58.700 vol ≥1,5× v20
- note: agent nhận ra mã FPT; không có thông tin sau as-of (cutoff 06/2026 < cửa sổ dữ liệu). Không đọc DT5G. Nghi giá điều chỉnh ~18/09.
- outcome:

### LVR-STK-2026-11-05-NNC
- as_of: 2026-11-05 · close_asof: 47300 · created: 2026-11-05T22:40:00+07:00 · trigger: USER-ASSIGNED
- due: H20 2026-12-03 · cửa sổ chạm 25 phiên đến 2026-12-10
- classification: 250 markdown muộn → chuyển tích luỹ (mơ hồ) / 60 tích luỹ→markup sớm (khá rõ) / 20 range tích luỹ lại 43.850–49.950 (mơ hồ, hơi tích cực). Tape mỏng: độ tin THẤP-TB.
- forecast:
    - H20_DIR: UP
    - H20_P_UP: 0.55
    - LEVEL: 43850 HOLD (không đóng cửa < 43.850 trong 20 phiên)
    - INVALIDATION: đóng < 43.850 với vol ≥ v20; hoặc bị từ chối lần 2 ở 49,5–50k vol tăng, đóng đáy ngày
    - P_TOUCH_PLUS10: 0.30 (high ≥ 52.030 trong 25 phiên)
    - P_TOUCH_MINUS10: 0.25 (low ≤ 42.570 trong 25 phiên)
    - SELL_VIEW_AT_PLUS10: SELL mặc định (52.030 giữa kệ cung 50–54,6k); HOLD chỉ khi đóng >52.700 vol ≥2× v20 thân nến trên 1/3 và pullback giữ 50.000 vol cạn
- outcome:

### LVR-BATTERY-2026-11-05 (thử ẩn danh 100 chuỗi cổ phiếu, PREREG md5 trong thư mục)
- artifact: agents/Mike/research/livermore_stock_battery_20261105/ (PREREG.md, cases/, SEALED_truth.json, livermore_results.csv, score.py, scored.txt)
- kết quả: 55/100 hit (UP 21/40, DOWN 34/60), Brier 0,2507; base rate tăng 47%; B1 luôn UP 47, B2 mom20 50, B3 mom60 48. P(≥55|đồng xu)=0,184; P(≥55|base)=0,067.
- PREREG: KHÔNG ĐẠT (Brier 0,2507 ≥ 0,25 — trượt 0,0007; hit hơn mọi baseline 5 điểm nhưng không khác đồng xu có ý nghĩa). Không RECOGNIZED nào. ACTION_IF_UP10 trùng hướng H20 (không thêm thông tin).

### LVR-STK-2026-11-11-VGS
- as_of: 2026-11-11 · close_asof: 20300 · created: 2026-11-11T23:00:00+07:00 · trigger: USER-ASKED (hỏi có mua được ở phiên 12/11 không) · nhãn: CỔ PHIẾU ĐƠN LẺ, không trộn hit-rate VNINDEX
- due: H20 2026-12-10
- classification: 250 markdown dài, có thể đang tạo đáy (hơi lẫn) / 60 tích luỹ→markup (rõ) / 20 đi ngang 18.300–19.800, 11/11 đóng trên đỉnh vùng lần đầu (hơi lẫn). 11/11 KL 949k = 1,84× TB10 (không phải 2,3×); chưa follow-through; 10/29 từng chạm 20.500 rồi bị bán ngược.
- ENTRY_VERDICT: BUY_ON_PULLBACK 19.400–19.900 (KL lùi <~500k); giá tối đa 20.000, KHÔNG đuổi mở cửa >20.000. Nhánh WAIT_CONFIRM: đóng ≥20.600 KL ≥600k ⇒ tối đa ~21.000. Huỷ: đóng <18.900 trong 5 phiên hoặc <18.300.
- forecast:
    - H20_DIR: UP
    - H20_P_UP: 0.57
    - LEVEL: 18300 HOLD
    - INVALIDATION: đóng <18.300; hoặc 5 phiên tới đóng <18.900 kèm KL bán >500k
- outcome:

### LVR-STK-2026-11-11-NNC
- as_of: 2026-11-11 · close_asof: 47050 · created: 2026-11-11T23:00:00+07:00 · trigger: USER-ASKED · nhãn: CỔ PHIẾU ĐƠN LẺ
- due: H20 2026-12-10
- classification: 250 downtrend đã dừng, có thể tạo nền (mơ hồ) / 60 markup (rõ) / 20 đi ngang 46.500–47.500, mơ hồ nghiêng re-accumulation (02/11 hấp thụ KL 3,7×, đáy nâng; nhưng yếu hơn VNINDEX và KL không cạn).
- ENTRY_VERDICT: BUY_ON_PULLBACK 45.000–46.000 (KL lùi <~35k), tối đa 46.000 — ở 47.050 R:R ≈1:1 (−6,8% tới 43.850 vs +6,2% tới 49.950). WAIT_CONFIRM: đóng ≥47.600 KL ≥60k + phiên sau không đóng <47.200 ⇒ tối đa 48.300. Huỷ: đóng <44.300 KL>60k hoặc <43.850.
- forecast:
    - H20_DIR: UP
    - H20_P_UP: 0.53
    - LEVEL: 43850 HOLD
    - INVALIDATION: đóng <43.850; hoặc <44.300 KL>60k
- note: giá trước ~24/08 có thể đã điều chỉnh ngược; sự kiện quyền 11–14/09 chưa kiểm.
- outcome:
