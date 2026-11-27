---
kind: project
owner: Taylor
status: closed-nogo
updated: 2026-11-15
title: "Kế hoạch nghiên cứu \"AI giải thích momentum + phản biện chéo 2 model\" — đề xuất 2026-11-15 (Taylor, job `Taylor_20261115_144310`; CHỈ KẾ HOẠCH, chưa code, chưa chạy)"
---
# Kế hoạch nghiên cứu "AI giải thích momentum + phản biện chéo 2 model" — đề xuất 2026-11-15 (Taylor, job `Taylor_20261115_144310`; CHỈ KẾ HOẠCH, chưa code, chưa chạy)

Nguồn yêu cầu: user John Dinh (Discord 15/11) gửi quy trình 6 bước (chọn mã momentum mạnh → hỏi AI điều gì đang lái → AI đọc tin/công ty/ngành → đưa AI thứ hai tìm thiếu sót → hai model thách thức nhau → nhiều góc nhìn, ít lỗ hổng). Mọi số dưới đây là **đo** (có lệnh/file) hoặc gắn **giả định**.

## 0. Trùng với NO-GO đã đóng? — Trùng một nửa, nên THU HẸP
- **Đã đóng**: momentum làm **tín hiệu mua** cơ học (MOM_N/MOM_S đóng 07/2026, `momentum-deals.md`; MOMENTUM/MEGA generic vẫn sống trong BAL) và **dự báo hướng bằng đọc tape** (Livermore NO-GO 14/11: 0/48 trial, DSR 0,005, PBO 0,74 — `livermore-divergence-nogo-20261114.md`). Bài học Livermore: với N vài chục, cổng forecast chỉ phát hiện edge ≥ ~25pp ⇒ **không thể chứng minh edge dự báo nhỏ bằng pilot ngắn**.
- **Chưa làm**: *quy nguyên nhân* (causal attribution) có cấu trúc + *phản biện chéo hai họ model*. Đây là phần mới và là phần duy nhất đáng thử.
- ⇒ Thu hẹp: đánh giá quy trình trước hết như **CÔNG CỤ HIỂU THỊ TRƯỜNG** (chất lượng nguồn, tỉ lệ thiếu sót được phát hiện, tỉ lệ bất đồng có bằng chứng), dự báo chỉ là mục tiêu **phụ**, đo trung thực với MDE nói rõ. KHÔNG đề xuất lại momentum làm tín hiệu mua; KHÔNG override SIGNAL_V11.

## A. "Momentum mạnh" = SỰ KIỆN PIT, là CÒ cho điều tra nguyên nhân (không phải tín hiệu mua)
Định nghĩa đề xuất (cột có sẵn trong `tav2_bq.ticker`, vũ trụ `tav2_mike.universe_pit`, KHÔNG `ticker_prune` §9b):
`mom20 = Close/Close_T−20 − 1 ≥ +20%` ∧ `idio20 = mom20 − VNINDEX mom20 ≥ +15pp` ∧ `Volume_1M/Volume_3M_P50 ≥ 1,5` ∧ `Close ≥ HI_3M_T1` (đỉnh 3 tháng mới) ∧ `Price×Volume_1M ≥ 3 tỷ/ngày` ∧ cooldown 90 ngày/mã (⇒ **N = sự kiện độc lập**, không phải số dòng).
- **Đo thật** (bq, 15/11, 40,9 MB quét; lệnh ở Phụ lục): **330 sự kiện / 20,5 tháng (2024-10 → 2026-06-15), 330 mã-sự kiện** — trung bình ~16/tháng nhưng **rất cụm**: 2025-07/08 = 50/49, 2025-09 = 4, 2026-04 = 2. ⇒ Tần suất theo chế độ thị trường; placebo phải hoán vị **khối tháng** (luật 12/11), không hoán vị trong năm.
- Ngưỡng trên là **điểm xuất phát** (giả định hợp lý); P0 hiệu chỉnh để ra 3–8 sự kiện/tuần bình thường, trần 10/tuần (hàng đợi theo thanh khoản).
- Quan hệ với funnel 8L (chất lượng → rẻ → tin, `discretionary-8l-candidate-funnel-plan-20261006.md`): **hai chiều ngược nhau nhưng không mâu thuẫn vì khác VAI**. Funnel = nguồn *ứng viên mua* cho sleeve; momentum-explain = *hiểu thị trường đang định giá gì*, phục vụ (i) mã đang GIỮ/trong sổ DD bật mạnh (giữ/tỉa — user quyết), (ii) mục "Điều thị trường chưa tính" của skill DD, (iii) phát hiện sớm luận điểm ngành mà Bobby đọc mù. Chọn **SONG SONG**, không gộp vào funnel; chỉ chung một thứ: ưu tiên skeptic cho giao `momentum ∩ (rating_8l ≤ 3 ∪ đang giữ ∪ dd_price_zones.json)`. Mã có cờ DD ⇒ vẫn giải thích nhưng dán nhãn "LOẠI khỏi mọi candidate" (luật 02/11).

## B. Pipeline 2 model: "điều tra" + "phản biện chéo"
| Vai | Ai | Model/effort (dispatch-routing) | Tính chất |
|---|---|---|---|
| M1 điều tra | agent `claude` (có WebSearch/WebFetch/BQ đọc) hoặc Taylor + WebSearch qua agent con; **Bobby mù ngành** chỉ khi nhãn NGÀNH | Sonnet medium (~$0,79/job, spend report 15/11) | tạo giả thuyết + bằng chứng có NGÀY |
| M2 phản biện KHÁC HỌ | `bin/second_opinion.sh` (opencode + deepseek free; ~0 đồng) | — | **ADVISORY ONLY** (header script; chưa hiệu chuẩn trên domain) |
| M2' phản biện cùng họ, đã hiệu chuẩn | `fundamental-skeptic` (Agent) | Opus high (~$3,62/job) | **GATE** nội dung: REFUTED ⇒ báo cáo không phát hành |
| Cổng số liệu | `bin/verify_finding.sh` (quant-skeptic) | Opus high | GATE cho mọi kết luận thống kê ở C |
- **Khung prompt M1** (đầu ra JSON cố định, 1 file/sự kiện, append-only): `{ticker, T, stats{mom20,idio20,volr,newhi,liq_bn,rating_8l,dd_flag,held}, driver_class ∈ {EARNINGS, CORP_ACTION, SECTOR_MACRO, FLOW_INDEX, NARRATIVE_ONLY, UNKNOWN}, evidence[{claim, source, date ≤ T}], what_market_prices_in, invalidation, view_20s/60s ∈ {CONT, REV, NO_VIEW}, confidence}`. Bắt buộc có lựa chọn **UNKNOWN/NARRATIVE_ONLY**; bằng chứng không có ngày ≤ T thì bị loại khỏi `evidence`.
- **M2 chạy MÙ trước** (nhận stats + tin thô, KHÔNG thấy kết luận M1 — cùng nguyên tắc Bobby mù), ghi `blind_driver`; **sau đó** mới nhận JSON M1 và trả `missed[]`, `disagree[]`, `verifiable(bool)` cho từng mục. Đo được κ(M1,M2 mù) = độ độc lập thật.
- **Vòng thách thức: tối đa 2** (M1 → M2 → M1 trả lời). Dừng khi vòng không thêm mục có nguồn mới; vòng 3 bị cắt (circuit-breaker dispatch-routing). Ghi `flip_rate` (M1 đổi driver sau phản biện) — flip cao đồng loạt = sycophancy, không phải "học được".
- **Chi phí/ngày (giả định từ TB/job spend report 15/11)**: 5 sự kiện × (M1 Sonnet $0,79 + deepseek 0) ≈ **$4**; thêm skeptic Opus high chỉ cho tập ưu tiên (~2/ngày) ≈ **+$7** ⇒ ~$11/ngày, trần đề xuất **$15/ngày, $300/pilot**. Chạy sau `pt_8l_daily` 19:20 (cron §11 — chỉ đề xuất, chưa cài).

## C. Đo GIÁ TRỊ THẬT — thiết kế preregister
**Câu hỏi**: `driver_class`/`view` của pipeline có dự báo excess return 20/60 phiên (so trung vị route cùng ngày, universe_pit) **tốt hơn baseline** không? Baseline B0 = tiếp diễn cơ học (CONT cho mọi sự kiện); B1 = M1 **không** phản biện (đo riêng giá trị của bước 4–5).
- **N**: sự kiện độc lập (cooldown 90 ngày, ≤1/mã/quý), cụm theo tháng ⇒ kiểm định bằng **hoán vị khối tháng** + BH-FDR trên ≤3 phép thử khai trước. Tốc độ đo được ~16/tháng ⇒ **N≈40 sau ~2,5–3 tháng** paper-forward (nhanh hơn nếu thị trường sôi động).
- **MDE thẳng thắn (giả định)**: N=40 nhị phân, hit-rate baseline ~50% ⇒ chỉ phát hiện lệch ≥ ~±22pp ở α=0,05 một phía. ⇒ dự báo gần như **không chứng minh được** trong pilot; vì vậy tiêu chí GO chính là **chất lượng quy trình**, dự báo là theo dõi.
- **RỦI RO LEAKAGE của LLM trên dữ liệu quá khứ (nêu rõ)**: mọi model đã "đọc" kết quả 2022–2025 trong training; hồi tố sẽ cho giải thích và dự báo *nhìn lại*. Xử lý: (1) **bằng chứng GO/NO-GO duy nhất = paper-forward** (mù theo cấu trúc); (2) hồi tố CHỈ để gỡ lỗi prompt/format, giới hạn sự kiện **≥ 2026-07** (sau mốc tri thức Fable 5.1 06/2026; Sonnet/Opus 5.5 chưa xác minh — giả định), **cấm WebSearch** trong hồi tố (trang web chứa hậu nghiệm), chỉ dùng `tav2_bq.stock_news` với `public_date ≤ T` (bẫy PIT: `ingested_at` không phải ngày biết tin, 98,8% backfill 09-13; gãy phủ 2021→2022 — `kb/data_registry/price-volume/stock_news.md`) + BQ ≤ T; (3) **canary rò rỉ**: hỏi model đường giá sau T, tái hiện được ⇒ loại sự kiện; (4) placebo: xáo `driver_class` theo khối tháng.
- **Bẫy nhận thức, đo bằng số**: narrative fallacy (M1 luôn tìm ra "lý do") ⇒ theo dõi tỉ lệ UNKNOWN/NARRATIVE_ONLY, <10% là đáng ngờ; confirmation bias ⇒ M2 mù trước; đồng thuận do cùng training ⇒ κ(M1, deepseek mù) và κ(M1, skeptic); sycophancy ⇒ flip_rate theo vòng.
- **GO/NO-GO khai trước** (PREREG.md, md5 commit trước lần chạy đầu, như `discretionary_dd_pick_v2` và Livermore): **G-proc** (chính): ≥80% sự kiện có ≥1 bằng chứng ngày ≤ T kiểm được; M2 phát hiện ≥1 mục thiếu *kiểm chứng được* ở ≥30% sự kiện; bất đồng có bằng chứng 20–60% (0% = không độc lập, >80% = nhiễu); user chấm hữu ích trung vị ≥3/5. **G-fcst** (phụ, báo nhưng không gate): excess 60s của nhóm `EARNINGS/CORP_ACTION` − `NARRATIVE_ONLY` với CI; hit-rate view≠NO_VIEW vs B0, B1. Trượt G-proc ⇒ NO-GO, không kéo dài.

## D. Đầu ra cho user — không tự mua
- **Báo cáo ngắn ≤12 dòng/sự kiện**: mã · stats (mom20/idio20/volr/đỉnh mới/liq) · 8L rating + cờ DD + đang giữ? · driver_class + confidence · 3 bằng chứng có ngày · M2 thấy thiếu gì · bất đồng còn lại · điểm vô hiệu hoá · dòng cố định "**KHÔNG phải khuyến nghị mua; sleeve chỉ qua DD + user duyệt**".
- **Topic Discord (đề xuất, chưa ghi)**: pilot P0–P1 vào thread nghiên cứu Taylor `1521735922066919515` (user đã chỉ định Taylor cho topic này); nếu GO ⇒ 1 dòng tổng hợp trong topic việc-cần-quyết 08:00 (`daily_decision_topic.py`, cùng chỗ funnel 8L), không vào Trading Daily. Phương án thay thế: topic mới "Momentum Lab" (user hay thích mở topic cho việc mới).
- **Tích hợp sleeve**: (a) mã đang giữ/sổ DD bật momentum ⇒ báo cáo gắn với `dd_price_zones.json` (giá vs tâm, luật 0,85×tâm) — user quyết giữ/tỉa; (b) mã mới: momentum ∩ rating≤3 ∩ không cờ ⇒ chỉ **đề xuất đưa vào hàng đợi DD** theo skill `due-diligence` (luật 5 09/11: mua cần DD + giá ≤ tâm — mã bật mạnh thường KHÔNG ≤ tâm, user biết trước); (c) tuyệt đối không ghi `state_*.json`, không chạm plan.

## E. Phân pha
| Pha | Mục tiêu | Việc cụ thể | Chi phí (giả định) | Điều kiện qua pha | Agent · model/effort | User duyệt |
|---|---|---|---|---|---|---|
| **P0** (1 tuần) | Định nghĩa + khung + dry-run RẺ | SQL sự kiện PIT (Phụ lục) → `agents/Taylor/research/ai_momentum_20261115/{PREREG.md, events.csv}`; prompt M1/M2 + schema JSON; **dry-run 10 sự kiện ≥2026-07** chỉ stock_news PIT, không WebSearch, canary rò rỉ; quant-skeptic đọc PREREG | ~$30: Taylor Opus medium 1 dispatch + 10×Sonnet + 1 skeptic | ≥8/10 có bằng chứng ngày ≤T; canary rò ≤2/10; UNKNOWN rate báo được; PREREG md5 commit | Taylor Opus medium (thiết kế); quant-skeptic Opus high (PREREG) | ngưỡng A, topic, trần $/ngày, 3–4 câu F |
| **P1** (≥10 tuần paper-forward, tới N≥40) | Chạy mù theo cấu trúc | Script `ai_momentum_daily.py` (PIT, append-only JSONL, md5), cron 19:35 T2–T6 (§11, đề xuất); M1 Sonnet (WebSearch cho phép — live là PIT by construction), M2 deepseek mù rồi phản biện, skeptic cho tập ưu tiên; đăng topic; scorer 20/60s tự chạy | ~$11/ngày, trần $15; ~$300 cả pha | N≥40 sự kiện; G-proc đạt sơ bộ; chi phí trong trần; user chấm ≥3/5 | Sonnet medium (M1), Opus high (skeptic), arch-review 1 lần cho script/cron | cài cron; đọc + chấm báo cáo |
| **P2** (khi sự kiện cuối đủ 60 phiên, ~02–03/2027) | Phán quyết | Chấm G-proc + G-fcst theo PREREG, hoán vị khối tháng, BH; `verify_finding.sh`; REPORT + results_registry (no_ledger: paper) | ~$20 | quant-skeptic CONFIRMED | Taylor Opus high; quant-skeptic | GO/NO-GO; nếu GO: wire dòng 08:00 + mục "Điều thị trường đang định giá" trong skill DD |
| **P3** (tuỳ chọn, sau GO) | Mở rộng | Vũ trụ = vị thế đang giữ cả 2 TK (exit intelligence), thêm họ model thứ 3 nếu có | theo P1 | — | — | riêng |
Rủi ro chung: chi phí lan (giữ trần cứng + hàng đợi); M2 free tier gián đoạn (fail-open: báo cáo ghi "M2 không chạy", không chặn); narrative hoá thành khuyến nghị ngầm (dòng cố định + không có trường "mua"); đụng phủ sóng tin VN mỏng (nhiều sự kiện UNKNOWN là kết quả hợp lệ, không phải lỗi).

## F. Câu hỏi user quyết (kèm khuyến nghị)
1. **Mục tiêu chính** là công cụ hiểu thị trường (G-proc) hay tìm edge dự báo (G-fcst)? → Khuyến nghị **G-proc là cổng**, G-fcst chỉ theo dõi; muốn chứng minh dự báo cần N≥150 (~1 năm), nên nói trước.
2. **Vũ trụ**: toàn `universe_pit` ∩ liq≥3 tỷ (~16 sự kiện/tháng, nhiều mã lạ) hay chỉ `rating≤3 ∪ đang giữ ∪ sổ DD`? → Khuyến nghị toàn vũ trụ cho M1+deepseek (rẻ), skeptic Opus chỉ cho tập ưu tiên.
3. **M2 là ai**: deepseek khác họ (độc lập thật, chưa hiệu chuẩn, advisory) vs fundamental-skeptic (cùng họ, đã hiệu chuẩn, gate)? → Khuyến nghị **cả hai** trong P1 và đo κ giữa chúng; chốt ở P2.
4. **Topic**: thread nghiên cứu Taylor hiện có hay topic mới "Momentum Lab"? → Khuyến nghị topic mới, Mike tạo khi user gật.

## Phụ lục — lệnh đo tần suất sự kiện (bq, 2026-11-15, dry-run 40.880.089 bytes)
```sql
WITH p AS (SELECT t.ticker,t.time,t.Close,t.Price,t.Volume_1M,t.Volume_3M_P50,t.HI_3M_T1,t.VNINDEX,
  LAG(t.Close,20) OVER (PARTITION BY t.ticker ORDER BY t.time) c20, LAG(t.VNINDEX,20) OVER (PARTITION BY t.ticker ORDER BY t.time) v20
  FROM tav2_bq.ticker t JOIN tav2_mike.universe_pit u ON u.ticker=t.ticker AND u.time=t.time AND u.in_universe
  WHERE t.time>="2024-10-01" AND t.time<"2026-06-16" AND t.ticker!="VNINDEX"),
e AS (SELECT ticker,time,Close/c20-1 mom20,(Close/c20-1)-(VNINDEX/v20-1) idio20,Volume_1M/NULLIF(Volume_3M_P50,0) volr,Close>=HI_3M_T1 newhi,Price*Volume_1M/1e9 liq_bn FROM p WHERE c20 IS NOT NULL),
f AS (SELECT *,LAG(time) OVER (PARTITION BY ticker ORDER BY time) prev FROM e WHERE mom20>=0.20 AND idio20>=0.15 AND volr>=1.5 AND newhi AND liq_bn>=3),
g AS (SELECT * FROM f WHERE prev IS NULL OR DATE_DIFF(time,prev,DAY)>90)
SELECT FORMAT_DATE("%Y-%m",time) ym,COUNT(*) n_events,COUNT(DISTINCT ticker) n_tk FROM g GROUP BY ym ORDER BY ym
```
Kết quả theo tháng: 2024-10 5 · 11 14 · 12 23 · 2025-01 7 · 02 38 · 03 13 · 04 8 · 05 13 · 06 15 · 07 50 · 08 49 · 09 4 · 10 7 · 11 10 · 12 7 · 2026-01 22 · 02 17 · 03 19 · 04 2 · 05 3 · 06 4 (tổng 330).
