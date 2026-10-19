# DT gate — luật đếm candidate khi nền xoay BEAR↔CRISIS (job Taylor_20261019_160133, 2026-10-19)
Read-only. Không sửa code/tham số. Script: `fetch.py` (bq CLI, dữ liệu tới 2026-10-19), `replay.py`, `hist.py`.
Artifact: `base_v34b.csv`, `vnindex.csv`, `dt5g_live.csv`, `badzone_episodes.csv`, `variants_vnindex_proxy.csv`.

## 1. Bộ đếm đúng code
- Selfcheck: `_dt_4gate(base v34b_clean)` vs `vnindex_5state_dt5g_live.state_raw`: **0 diff / 3.190 phiên** (vs cột `state` sau macro cap: 50 diff — đúng thiết kế).
- Chuỗi: 29/09→06/10 base BEAR, streak 1..6 (need 10) · 07/10 base CRISIS → `pr` reset về 1 (code: `if s==ps: pr+=1 else: pr=1`), need 25 · 19/10 = CRISIS 9/25. Committed NEUTRAL suốt. VNINDEX 1.780,68 (28/09) → 1.689,84 (19/10) = **−5,10%**.
- Không off-by-one, không reset sai so với code.

## 2. Đúng thiết kế hay lỗ hổng
- Đúng code-design: streak = số phiên LIÊN TỤC cùng MỘT nhãn; 25 để vào CRISIS là cố ý ("chậm hoảng loạn").
- Hệ quả phụ CÓ THẬT, không được ghi trong thiết kế: nền XẤU THÊM (BEAR→CRISIS) làm phòng thủ CHẬM hơn. Nếu nền giữ BEAR, gate đã commit BEAR (20%) ngày **12/10**; vì leo lên CRISIS nên sớm nhất commit CRISIS (0%) là ~**10/11** (ước lượng: 16 phiên nữa nếu CRISIS không đứt, chưa trừ nghỉ lễ).
- Lịch sử 2014→nay: 36 đợt "nền xấu, committed chưa phòng thủ"; 16 đợt ≥15 phiên; **9 đợt ≥15 phiên có xoay** (gồm đợt hiện tại). 8 đợt đã kết thúc: fwd20 từ phiên 15 = +3,3%…+10,6% (8/8 dương), fwd60 = +3,5%…+24,9%, đáy tệ nhất trong 60 phiên sau −4,4%; 7/8 gate về NEUTRAL/BULL, 1/8 (2018-10) commit BEAR. Đúng tiêu chí xem lại (≥15 phiên + VNI ≤−5%): **N=2** (12/2014: fwd20 +5,9%, fwd60 +3,5%; 07/2018: +7,2%, +12,2%).
- Ngược lại 7 đợt nền xấu KHÔNG xoay (thuần CRISIS 24 phiên) mới là đợt nguy hiểm: 4/2018 fwd60 −15,8%, 9/2023 đáy −9,6%.

## 3. Phương án (proxy: VNINDEX × trọng số state, T+1, TC 0,1%, pin0%, không ramp, DT4 không macro cap; 2014-06→2026-10)
| Phương án | CAGR full | DD full | CAGR IS 14-19 | CAGR OOS 20+ | DD OOS | phiên khác A |
|---|---|---|---|---|---|---|
| A giữ nguyên | 9,56% | −25,4% | 8,33% | 10,59% | −18,8% | 0 |
| C đếm nhóm xấu ≥10 → BEAR | 7,28% | −24,1% | 7,16% | 7,39% | −22,2% | 289 |
| B N=10 cap 50% | 8,96% | −23,2% | 8,46% | 9,38% | −20,6% | 205 |
| B N=15 cap 50% | 9,24% | −24,4% | 8,18% | 10,13% | −20,0% | 120 |
| B N=10 cap 20% | 8,20% | −23,2% | 7,83% | 8,51% | −21,7% | 205 |
| B N=15 cap 20% | 8,74% | −24,9% | 7,42% | 9,83% | −20,8% | 120 |
- B và C đều TỐN CAGR cả IS lẫn OOS và làm DD OOS XẤU đi (cắt gần đáy, lỡ nhịp hồi). B/C = **re-tune theo lịch sử** → trái CLAUDE.md.
- D (tay cắt 70%→20-50%): tương đương B áp 1 lần; ở 2 tiền lệ đúng tiêu chí, cắt 35pp tại phiên 15 lỡ ~+2,1/+2,5pp NAV trong 20 phiên (0,35×fwd20; ước lượng suy từ N=2).

## 4. Khuyến nghị: A (giữ nguyên) — chắc chắn TRUNG BÌNH
- Ngưỡng "xem lại" đã làm đúng việc: kích hoạt kiểm tra; kiểm tra cho thấy luật đếm đúng code và không có bằng chứng lịch sử ủng hộ đổi.
- Cơ chế phòng thủ vẫn còn: CRISIS liên tục tới 25 → tự commit 0% (~10/11, ước lượng); macro gate cap vẫn chạy.
- KHÔNG biết: (1) N=2/8 quá nhỏ, tiền lệ có thể không lặp; (2) base v3.4b bất biến chỉ từ 2026-07-30 — lịch sử trước đó là backfill do mô hình đã tune trên chính lịch sử đó (in-sample); (3) proxy VNINDEX ≠ NAV V2.4 (LAG/BAL/custom30V phản ứng khác); (4) đợt hiện tại khác tiền lệ ở chỗ đã có 9 phiên CRISIS liền cuối đợt — giống dạng "thuần CRISIS" nguy hiểm hơn.
- Nếu user muốn hành động: chọn D, ghi rõ là phán đoán tay, không phải luật; đừng đổi code gate.
