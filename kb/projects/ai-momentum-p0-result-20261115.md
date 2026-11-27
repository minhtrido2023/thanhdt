---
kind: project
owner: Taylor
status: closed
updated: 2026-11-15
title: "AI momentum — kết quả P0 (2026-11-15, Taylor, job `Taylor_20261115_150627`)"
---
# AI momentum — kết quả P0 (2026-11-15, Taylor, job `Taylor_20261115_150627`)

Bổ sung cho `ai-momentum-research-plan-20261115.md` (không ghi đè). Artifact:
`agents/Taylor/research/ai_momentum_20261115/` — PREREG v1 commit `5d3284d0b` (md5 PREREG `4ed34b38`,
md5 prompt/schema trong `PREREG.md5`), commit TRƯỚC dry-run. Retro/dry-run KHÔNG tính vào N chính.

## 1. Sự kiện PIT (universe_pit ∧ rating_8l ≤ 4)
- **Có rating PIT thật**: `tav2_bq.fa_ratings_8l` (CANONICAL as-of, 2014-06-30→2026-11-13, 54.841 dòng,
  không trùng ticker+time) — join as-of (dòng `time ≤ T` mới nhất). Không dùng `data/rating_8l.csv`
  (snapshot hôm nay). Caveat: bảng được republish định kỳ ⇒ as-of hồi tố có thể lệch nhẹ; live sẽ
  ghi rating đọc được tại T.
- Định nghĩa ngưỡng giữ nguyên kế hoạch; cooldown sửa thành **greedy từ sự kiện đã phát** (> 90 ngày
  ∧ khác quý) — SQL phụ lục cũ đo khoảng cách tới *ngày đủ điều kiện trước*, không phải sự kiện trước.
- **Đo** (`build_events.py`, 2024-10 → 2026-11-13): không lọc rating N=391 (270 mã); **R4 N=341
  (247 mã), TB 13,1/tháng, trung vị 8**, rất cụm (2025-07/08 = 40/48; 2026-04/05 = 2/3).
  **6 tháng gần nhất (05→10/2026): 6,3/tháng.** Rating lọc mất ~13% sự kiện.
- Mô tả outcome R4 (chỉ để tính power, KHÔNG phải kết quả): ex20 TB +2,75% trung vị −0,17%,
  P(ex20>0)=0,485; ex60 TB +2,45% trung vị −3,63%, P(ex60>0)=0,426 — đuôi phải dày.

## 2. Power / MDE (G-fcst là cổng chính) — `power_sim.py`, phân phối ex THẬT, p hoán vị khối tháng, α=0,05/3
| N_scored | ex20 Δ5pp | Δ8pp | Δ12pp | ex60 Δ8pp | Δ12pp | Δ20pp | nhị phân MDE |
|---|---|---|---|---|---|---|---|
| 40 | 0,04 | 0,05 | 0,14 | 0,01 | 0,07 | 0,18 | +23,5pp |
| 80 | 0,18 | 0,41 | 0,61 | 0,22 | 0,50 | 0,78 | +16,6pp |
| 150 | 0,41 | **0,87** | 0,98 | 0,43 | **0,85** | 1,00 | +12,1pp |
| 250 | 0,69 | 0,95 | 1,00 | 0,73 | 0,98 | 1,00 | +9,4pp |
ICC tháng 0,007/0,003 (yếu sau khi trừ trung vị route). **Thẳng: cần N≈150 để bắt chênh ≥8pp ex20 /
≥12pp ex60 — hiệu ứng lớn. Ở nhịp 6,3/tháng ⇒ ~24 tháng + 3 tháng chờ ex60** (~11 tháng nếu nhịp
TB 13/tháng). Edge LLM thực tế nhiều khả năng nhỏ hơn (giả định) ⇒ kết cục dễ nhất là "không kết luận".
Khung phán quyết định sẵn (PREREG §4.1): L1 N=80, L2 N=150 (Haybittle–Peto p<0,001, có luật dừng vô
ích), FINAL N=250 hoặc 24 tháng.

**Tăng N hợp lệ** (đo trên `qual_days_loose.csv`, R4):
| Biến thể | N 26 tháng | TB/tháng | 6 tháng gần | mã >1 sự kiện | Rủi ro |
|---|---|---|---|---|---|
| Chuẩn, cooldown 90 | 342 | 13,2 | 6,3 | 80 | — |
| cooldown 45 | 360 | 13,8 | 6,5 | 89 | gần như không thêm N — cooldown KHÔNG phải nút thắt |
| liq ≥ 1 tỷ | 397 | 15,3 | 7,7 | 98 | mã kém thanh khoản, khó thực thi, tin thưa hơn |
| mom15/idio10/volr1,2/liq1 | 560 | 21,5 | 12,3 | 168 | gấp ~2× tốc độ; sự kiện "yếu" hơn, nhiều mã lặp ⇒ phụ thuộc trong-mã tăng, cần cụm theo mã + tháng |
Khuyến nghị: nếu muốn rút thời gian, chỉ nới ngưỡng (mom15/…) **trước khi khoá PREREG v2**, không hạ cooldown.

## 3. Dry-run 10 sự kiện (≥ 2026-07, seed 20261115, chỉ stock_news PIT + BQ ≤ T, cấm web)
| Đo | Kết quả | Ngưỡng P0 |
|---|---|---|
| Sự kiện có ≥1 bằng chứng ngày ≤ T kiểm được (khớp đúng phần tử gói) | **10/10**; 29/29 mục bằng chứng ngày ≤ T, 29/29 tham chiếu khớp gói | ≥8/10 ✅ |
| …trong đó bằng chứng nằm trong ~4 tuần trước T (xúc tác thật) | **5/10** (HII, ASP, MSR, HID, VOS); 5 còn lại chỉ có BCTC cũ 2–3 tháng | mô tả |
| Gói có ≥1 tin stock_news trong 120 ngày | 6/10 (4/10 không có tin nào) | mô tả |
| UNKNOWN / NARRATIVE_ONLY | **4/10 UNKNOWN**, 0 NARRATIVE_ONLY; EARNINGS 5, CORP_ACTION 1 | ≥10% ✅ (không narrative fallacy) |
| view_20s | CONT 4, REV 1, NO_VIEW 5; view_60s NO_VIEW 10/10; confidence 0,15–0,50 | — |
| Canary rò rỉ (Sonnet, không gói) | **0/10** — 10/10 UNKNOWN, tự nhận cutoff ~06/2026 | ≤2/10 ✅ |
| Tuân thủ schema | Lệch tên khoá 10/10 (`ref/note` thay `claim/source`); 1/10 thêm trường `caveats` | sửa prompt P1 |
| **M2 deepseek (`second_opinion.sh`)** | **FAIL 3/3** — opencode `UnknownError: Unexpected server error` sau 7–10 s, kể cả prompt 1 dòng ⇒ lỗi phía provider, không do input. Fail-open đúng thiết kế | ⚠️ |
| flip_rate, κ(M1, M2 mù) | **chưa đo được** (M2 không chạy) | — |
Không chấm ex20/ex60 của 10 sự kiện (theo PREREG: hồi tố không phải bằng chứng; N=10 vô nghĩa).
Nhận xét chất lượng: M1 thận trọng (không bịa xúc tác, tự gắn UNKNOWN khi BCTC đã cũ) nhưng view_60s
toàn NO_VIEW ⇒ T2/T1 ở 60s có thể thiếu nhóm; T1 dùng 20s là đúng. Gói thiếu dữ liệu ngành ⇒
SECTOR_MACRO không bao giờ được chọn — P1 cần thêm return route/ngành 20 phiên vào gói.

## 4. Chi phí token THỰC TẾ dry-run (đo từ `subagent_tokens` của Agent tool)
- M1: 10 agent Sonnet = **763.960 token** (75.841–76.934/agent); canary 1 agent = **68.127**. Tổng
  subagent **832.087 token**. deepseek: 0 (không chạy). BQ: ~58 MB quét/lần truy vấn sự kiện (dry-run).
- ~68k/agent là context cố định (canary không tool, không gói vẫn 68k) ⇒ phần việc thật chỉ ~8k/sự
  kiện. **P1 phải chạy M1 bằng phiên trần (không nạp CLAUDE.md/KB fleet)** — giảm ~85–90% token
  (ước lượng). Quy ra $ chưa đo (không có bảng giá/caching thực trong phiên); token phiên Taylor
  điều phối chưa đo.

## 5. Khuyến nghị
**QUA P1 có điều kiện** — G-proc P0 đạt (bằng chứng 10/10, canary 0/10, UNKNOWN 40%), nhưng 3 việc
phải xong trước khi bật paper-forward:
1. M2 deepseek phải chạy lại thành công ≥1 lần (provider opencode đang lỗi server) và cần chế độ
   prompt tuỳ biến/không-post-bus cho `second_opinion.sh` (wrapper hiện ép khung "3 điểm đáng ngờ" +
   post bus mỗi lần ⇒ 2 event/sự kiện, nhiễu bus) — việc của Wags/arch-review, không phải Taylor sửa.
2. Sửa schema M1 (tên khoá) + thêm return ngành vào gói; M1 chạy phiên trần để cắt token.
3. User biết trước: với G-fcst là cổng chính, phán quyết có ý nghĩa cần **~2 năm** ở nhịp gần đây;
   nhiều khả năng kết cục là "không kết luận". Nếu không chấp nhận thời gian đó ⇒ hoặc nới ngưỡng sự
   kiện (×2 tốc độ, PREREG v2 trước khi chạy) hoặc DỪNG ở P0.
quant-skeptic chưa gọi (Mike gọi sau).
