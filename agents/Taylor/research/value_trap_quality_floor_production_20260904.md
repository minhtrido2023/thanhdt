# Value-trap quality-floor → production: có chỗ nào thiếu sàn chất lượng, và có đáng thêm không?
> Taylor, 2026-09-04 · job Taylor_20260903_174422 · tiếp mảnh (b) của `mania_quality_tilt_20260904.md` §3.1

## Tóm tắt 1 phút

1. **Mike đúng một nửa.** custom30V/BAL KHÔNG "trần trụi" — chúng có gate `fa_ratings_8l.rating<=3`
   trước khi rank yieldcombo. Nhưng gate đó **KHÔNG PHẢI** golden floor (`ROE_Min3Y≥0 ∧ CF_OA_3Y>0`)
   — nó là một scorecard bù trừ (ROIC/ROE/leverage/FSCORE) mà tác giả `rating_8l.py` **cố ý** không
   đặt hard-gate trên ROE_Min (dòng 398, quyết định của user 2026-06-02). Đây là khoảng trống THẬT,
   xác nhận bằng code, không phải suy diễn từ tài liệu.
2. **Nhưng đo thực nghiệm cho thấy khoảng trống đó KHÔNG có giá trị để lấp.** Thêm golden floor
   ngay TRÊN gate rating<=3 hiện tại (giữ nguyên top-60 pool / top-30 / yieldcombo — đúng funnel
   production, không đổi bề rộng rổ) cho kết quả **FULL −0,44pp, OOS −2,08pp, DSR excess = 0,361
   << 0,95 (RED FLAG)** — không phân biệt được với nhiễu. Cơ chế: 45% quan sát trong rổ ey-decile
   KHÔNG-gate nào cũng thất bại golden floor và kéo trung bình xuống −0,64%/quý (so +3,80% phần
   đạt floor) — nhưng NHỮNG TÊN CỤ THỂ đó (TLH/HSG/MHC/TVB/PLP/HHG…) đã mang rating 4-5 phần lớn
   thời gian trong `fa_ratings_8l`, tức là **gate rating<=3 hiện tại đã loại chúng ra rồi** trước
   khi golden floor có cơ hội làm gì thêm.
3. **Kết luận: KHÔNG đề xuất wire.** Đây LÀ một đề xuất (đã đo, đã null) — không phải quyết định
   của tôi, cần quant-skeptic verify trước khi trình user nếu ai đó muốn theo đuổi tiếp (xem §5).

---

## Việc 0 — Quét production: chỗ nào dùng ey/PE để chọn/xếp hạng, có sàn chất lượng chưa?

### (a) `rating_8l.py` — golden floor CÓ tồn tại nhưng chỉ áp một phần, không áp lên rating (1-5)

- **Golden floor `ROE_Min3Y≥0 ∧ CF_OA_3Y>0` CÓ trong code**, dòng 914:
  `_book_ok = ~(scr["ROE_Min3Y"] < 0) & (scr["CF_OA_3Y"] > 0) & ...` — nhưng nó chỉ áp cho
  `golden_cell` (pb_z≤−1 dislocation) để floor zone lên `1_BUY-NOW` (dòng 900-920). Đây LÀ đúng
  cái CLAUDE.md mô tả — nhưng phạm vi hẹp hơn CLAUDE.md ngụ ý: chỉ áp cho phần dislocation
  (pb_z≤−1), KHÔNG áp cho toàn bộ `value_score`/`zone` composite.
- **TRAP-zone gate rộng hơn (dòng 892-894, 941)** chỉ kiểm `ROE_Min3Y<0` — KHÔNG kiểm `CF_OA_3Y`:
  `if r["ROE_Min3Y"] < 0 and r["value_pct"] >= P_ACC: return "4_TRAP"`. Một tên ROE_Min3Y≥0 nhưng
  CF_OA_3Y≤0 (đốt tiền mặt, book lãi giấy) mà KHÔNG phải golden_cell (pb_z>−1) thì KHÔNG bị TRAP,
  KHÔNG bị floor — đi thẳng vào `value_score`/`zone` composite bình thường.
- **Rating cốt lõi (1-5) — dòng 398, comment tường minh của tác giả**: *"No ROE_Min/ROIC_Min hard
  gate (user): a single weak quarter in 3Y must not cap a name whose annual result is fine."*
  Đây là quyết định CÓ CHỦ Ý, không phải sơ suất — nhưng hệ quả là `rating<=3` **≠** golden floor.
- **Kết luận (a): golden floor tồn tại trong `rating_8l.py` nhưng KHÔNG PHẢI là cơ chế gate mà
  custom30V/BAL production đọc (xem b/c) — nó chỉ chạy trong discretionary screener
  (`rating_8l_screener.csv`), là công cụ tay cho margin discretionary funnel, KHÔNG PHẢI đường
  live tự động.**

### (b) custom30V (`tav2_bq.custom30v_8l`) — gate = `rating<=3` ONLY, không có golden floor

- Builder: `custom_basket.py::build_pit()`. Gate cứng: `custom_basket.py:945`
  `if gate_rating is not None and not (pd.notna(rt) and rt <= gate_rating): continue` — chỉ đọc
  `rating_asof()` (fa_ratings_8l.rating), KHÔNG đọc `ROE_Min3Y`/`CF_OA_3Y` ở bước này.
- Sau gate: `custom_basket.py:951` `pool = gated[:CFO_POOL]` (top-60 liquid trong pool đã gate) →
  `custom_basket.py:995-1000` `score = rank_pct(1/PE) + rank_pct(1/PCF)` (yieldcombo, fillna 0.5
  trung tính) → top-30. **Không có bước lọc ROE/CFO nào giữa gate và rank.**
- Xác nhận độc lập từ comment người viết trước (`probe_route_eveb_h7.py:20`): *"pool = top-60 by
  turnover, gate as-of rating<=3 (the set V2.4 acts within); pick top-30 by yieldcombo."*
- **custom30V ĐÃ chạy trong cron production 19:00 hàng ngày** (`kb/cron_registry.md:83`,
  `golive_recommend_v23`) — đây KHÔNG phải đường research-only.

### (c) BAL book — cùng builder, cùng khoảng trống

- BAL's basket component gọi cùng `custom_basket.build_pit(gate_rating=..., weight_scheme=BASKET_WT,
  top_n=BASKET_TOPN, ...)` (`lag_dnpr_harness.py:663,686,707`, `pt_v23_lagcap_research.py:915,938,959`)
  — cùng gate `rating<=3`, cùng yieldcombo, cùng khoảng trống như (b). SIGNAL_V11 core (MEGA/
  MOMENTUM/DEEP_VALUE_RECOVERY/RE_BACKLOG_BUY tiers) không được audit chi tiết từng tier trong job
  này (time-boxed) — phần basket-component (rổ giá trị) là phần dùng ey/PE trực tiếp và đã xác nhận.
- `filter.json` KHÔNG chứa SIGNAL_V11/yieldcombo — nó là bộ filter cũ (`_BKMA200`, `_BullDvg`…),
  không phải đường V2.4 production hiện tại. Nghi ngờ ban đầu của dispatch về `filter.json` sai
  vị trí — code thật nằm ở `custom_basket.py`/`lag_dnpr_harness.py`.

### (d) CAPIT + margin discretionary funnel

- **CAPIT "golden" bottom-fish** (`lag_dnpr_harness.py:951`): `ROE_Min5Y>=0.12 AND ROIC5Y>=0.10
  AND FSCORE>=6` — **CHẶT HƠN** golden floor, nhưng rank theo **pb_z** (P/B), không phải ey/PE →
  ngoài phạm vi câu hỏi value-trap-qua-PE của dispatch này.
- **Margin discretionary "candidate 70%"** = `rating_8l.py` dòng 889 `P_BUY=0.70` (zone
  `1_BUY-NOW` khi `value_pct>=0.70`) — cùng cơ chế đã nói ở (a): golden floor chỉ áp cho
  `golden_cell` dislocation, TRAP-zone rộng chỉ kiểm ROE_Min3Y. Đây là công cụ TAY (screener CSV),
  không phải lệnh tự động.

### Kết luận Việc 0

**Có khoảng trống thật ở (b)+(c) — custom30V/BAL dùng gate `rating<=3` (KHÔNG phải golden floor)
trước khi rank yieldcombo, và đây LÀ đường live tự động (cron 19:00).** → chuyển sang Việc 1.

---

## Việc 1 — Đo tác động của việc thêm golden floor vào ĐÚNG chỗ đó

### Thiết kế (N_TRIALS=1 — một giả thuyết duy nhất, không phải family search)

Tái tạo funnel production **đúng thứ tự, đúng logic**, nhưng standalone (không đụng
`custom_basket.py` — module đang chạy cron live, tránh rủi ro; script đọc-chỉ, artifact riêng):

```
BASELINE   : fa_ratings_8l.rating<=3 (as-of)  → top-60 liquid pool → yieldcombo top-30 → EW
GOLDEN-FLR : (rating<=3) AND (ROE_Min3Y>=0 AND CF_OA_TTM>0)  → top-60 pool → yieldcombo top-30 → EW
```

- Nguồn: `tav2_bq.fa_ratings_8l` (PIT rating, xác nhận CANONICAL —
  `kb/data_registry/rating-8l/fa_ratings_8l.md`), `tav2_bq.ticker` (PE/PCF/liquidity/ROE_Min3Y/
  CF_OA_P0-3, cùng cadence — đã verify PIT-correct theo CLAUDE.md/`valuation_pe_pb_pcf_ps.md`;
  KHÔNG nhân `Price/Close` — bẫy đã biết, đã bị bác bỏ 2026-08-02).
- **Đơn giản hoá đã khai báo** (khác `pt_v23_audit_2014.py` đầy đủ): equal-weight (không
  namecap-cap-10%, nhưng EW-30-tên ≈ 3,3%/tên đã dưới cap nên khác biệt nhỏ), rebal `qstart`
  (production live dùng `q2m5` — lệch vài ngày, không phải lệch logic chọn), KHÔNG TC/margin/CAPIT/
  allocator (gross NAV thuần — mục đích cô lập hiệu ứng CHỌN MÃ, không tái lập số R3 pin). ROE_Min3Y/
  CF_OA đọc cùng cadence PE (KHÔNG staggered theo Release_Date như `BASKET_QFLOOR` sẵn có trong
  `custom_basket.py`).
- Self-check 0 VND: weight-sum error tại mỗi rebalance **max 3,55e-15** (cả 2 biến thể) — pass.
- Artifact: `valuetrap_20260904/pull_data.py`, `pull_step34.py`, `build_and_compare.py`,
  `analyze.py`, `capacity_check.py`; data `nav_baseline.csv`/`nav_gfloor.csv`/
  `capacity_by_quarter.csv`.

### Kết quả

| | FULL 2014-01→2026-09 | IS 2014-07→2019-12 | OOS 2020-01→2026-09 |
|---|---:|---:|---:|
| BASELINE (rating≤3, không golden floor) | CAGR 13,24% / Sharpe 0,71 / DD −50,7% / Calmar 0,26 | CAGR 6,10% / Sharpe 0,45 | CAGR 20,63% / Sharpe 0,89 |
| GOLDEN-FLOOR (rating≤3 ∧ ROE_Min3Y≥0 ∧ CFO_TTM>0) | CAGR 12,80% / Sharpe 0,70 / DD −54,2% / Calmar 0,24 | CAGR 7,40% / Sharpe 0,56 | CAGR 18,55% / Sharpe 0,82 |
| **Delta (GF − Baseline)** | **−0,44pp** | **+1,30pp** | **−2,08pp** |

(CAGR tuyệt đối THẤP HƠN R3 pin 28,86% vì đây là NAV custom30V-thuần equal-weight, KHÔNG cộng
BAL/LAG/CAPIT/margin/allocator — đúng như đã khai báo, chỉ dùng để so BASELINE vs GOLDEN-FLOOR nội
bộ, không so trực tiếp với R3.)

**Per-year delta (gfloor − baseline CAGR, pp), 11 năm đầy đủ 2015-2025:**
2015 +0,71 · 2016 +3,33 · 2017 +3,33 · 2018 −0,48 · 2019 +0,97 · **2020 −9,80** · 2021 +0,72 ·
2022 −2,76 · 2023 −3,93 · 2024 −0,43 · 2025 +0,05.
→ 6/11 năm dương nhưng **mean −0,75pp, std 3,54pp** (biên độ nhiễu lớn hơn hẳn effect size) — năm
2020 (V-shape hồi phục sau COVID) một mình kéo mean xuống âm: tên tạm thời fail golden floor
(CFO âm ngắn hạn do phong toả) vẫn hồi giá cực nhanh mà BASELINE (gate lỏng hơn) bắt được, GOLDEN-
FLOOR bỏ lỡ.

**Leave-one-year-out (xoá từng năm, nối lại, đo total-return-delta còn lại):** dao động cực mạnh
từ **−34,04pp** (ex-2016) đến **+3,94pp** (ex-2020) — dấu hiệu rõ ràng rằng con số full-period
(−0,44pp) **không ổn định**, bị chi phối bởi một vài năm cụ thể chứ không phải một edge bền.

**DSR** (Deflated/Probabilistic Sharpe Ratio trên chuỗi excess-return hàng ngày GF−Baseline,
N_TRIALS=1 vì đây là MỘT giả thuyết đơn, không phải family-search nên không cần haircut đa kiểm
định): ann. excess SR = **−0,101**, skew −0,07, kurtosis(raw) 4,77, n=3.159 ngày →
**DSR = 0,361 << 0,95 → RED FLAG.** Không thể phân biệt excess return này với nhiễu; điểm trung
tâm còn hơi ÂM.

**Capacity** (`capacity_by_quarter.csv`): golden floor thu hẹp universe đạt-cả-2-điều-kiện từ
median 542 tên (chỉ rating≤3) xuống **median 397 tên** (−26,7%) — nhưng vẫn **gấp 13 lần** nhu
cầu top-30, chỉ 3/51 quý (giai đoạn đầu 2014-2015, dữ liệu mỏng) có <30 tên đạt cả 2 điều kiện.
**Capacity KHÔNG phải nút thắt** — kết quả null không phải vì floor cắt quá sâu.

### Vì sao null: cơ chế (đã verify, không suy diễn)

Từ mảnh trước (`mania_quality_tilt_20260904.md`), ey-decile **KHÔNG gate gì cả** value-trap thật:
45% quan sát "chọn theo ey" thất bại golden floor, và phần thất bại kéo trung bình xuống **−0,64%/
quý** so với **+3,80%/quý** phần đạt floor (script `/tmp/worst_offenders.py`, dữ liệu
`qualitytilt/universe_pe.csv`+`golden_floor_snap.csv`). 12 tên tệ nhất theo tổng đóng góp âm:
**TLH, HSG, MHC, TVB, PLP, HHG, TDG, NDT, BOT, DNM, LDP, CMC** (fail-rate 33-100% mỗi lần được
chọn). Nhưng khi tra `fa_ratings_8l` cho 6 tên đầu (dữ liệu gần đây nhất, 2025-04→2026-07):
**TLH/HSG/MHC/TVB/PLP/HHG đều mang rating 4-5 phần lớn thời gian** (TLH chỉ rớt về 3 ở
2026-07-30; HSG dao động 3-5; PLP/HHG giữ 4 SUỐT 6 kỳ gần nhất). **HSG cũng nằm trong danh sách
BANNED vĩnh viễn của CLAUDE.md** — một xác nhận độc lập ngoài dự tính.

⇒ **Gate `rating<=3` hiện tại, dù không phải golden floor theo định nghĩa, đã loại phần lớn đúng
những tên mà golden floor sẽ loại** — thông qua con đường khác (scorecard ROIC/ROE/leverage/FSCORE
bù trừ thay vì hard-gate ROE_Min/CFO). Đây là lý do value-trap-KHÔNG-gate (mảnh trước, +2,58% vs
+11,47%) và value-trap-CÓ-gate-rating (job này, 13,24% vs 12,80%, thực chất bằng nhau trong biên
nhiễu) là **HAI câu trả lời khác nhau cho hai câu hỏi khác nhau** — không mâu thuẫn.

### Kết luận Việc 1

**KHÔNG có bằng chứng để đề xuất wire golden floor thêm vào custom30V/BAL.** DSR fail nặng, full-
period delta âm nhẹ, IS/OOS đảo dấu, LOO không ổn định, và cơ chế giải thích được: gate hiện tại
đã làm gần hết việc golden floor định làm, qua một con đường khác. **Đây LÀ một đề xuất đã đo và
NULL — nếu ai muốn đẩy tiếp (vd thử golden floor với ngưỡng khác, hoặc route khác), phải qua
quant-skeptic trước khi trình user, đúng yêu cầu dispatch. Bản thân tôi KHÔNG kết luận "nên wire".**

Đối chiếu tiền lệ: `plan_quality_sleeve_20260712.md` trial **QF8-NEU** (2026-07-12) đã test một
biến thể GẦN giống (fundamentals floor THAY THẾ rating gate, cho rổ 8 tên tập trung) → NO-GO, nhưng
confound với giảm bề rộng (30→8 tên, mất diversification premium). Job này tách biệt sạch hơn: GIỮ
NGUYÊN bề rộng (top-30/pool-60), chỉ thêm floor — kết luận NO-GO ở đây độc lập với vấn đề
concentration của QF8-NEU, củng cố thêm chứ không lặp lại nó.

---

## Trả lời trực tiếp 3 câu hỏi dispatch

1. **Production có chỗ nào thiếu sàn chất lượng không?** CÓ, xác nhận bằng code:
   `custom_basket.py:945` (gate) — chỉ đọc `fa_ratings_8l.rating<=3`, không đọc `ROE_Min3Y`/
   `CF_OA_3Y`; các call site `lag_dnpr_harness.py:663,686,707` và
   `pt_v23_lagcap_research.py:915,938,959` dùng cùng builder nên cùng khoảng trống. `rating_8l.py:
   892-894,941` (TRAP zone) cũng chỉ kiểm ROE_Min3Y, không kiểm CFO. `rating_8l.py:398` — tác giả
   xác nhận rõ đây là chủ đích, không phải bug.
2. **Nếu có thì thêm vào đáng giá bao nhiêu?** **KHÔNG đáng** — FULL −0,44pp (nhiễu, LOO dao động
   −34..+4pp), OOS −2,08pp, DSR 0,361 << 0,95. Capacity đủ dư nên không phải lý do null.
3. **Nếu không (n/a ở đây, nhưng câu trả lời gần nhất — floor hiện tại có bền không?)**: gate
   `rating<=3` — dù không phải golden floor theo tên gọi — **đo được là loại đúng phần lớn tên
   value-trap thật** (worst-offenders TLH/HSG/MHC/TVB/PLP/HHG hầu hết rating 4-5). Không cần thêm
   golden floor riêng vì cơ chế bù trừ hiện tại đã phủ được phần lớn cùng rủi ro qua route khác.

## Giới hạn

- Standalone script, không phải `pt_v23_audit_2014.py` đầy đủ — số CAGR tuyệt đối KHÔNG so được
  với R3 pin trực tiếp; chỉ delta nội bộ (baseline vs golden-floor, cùng phương pháp) là có ý nghĩa.
- ROE_Min3Y/CF_OA đọc cùng cadence PE, không staggered theo Release_Date — có thể sớm hơn vài
  ngày-tuần so với `BASKET_QFLOOR`'s PIT nghiêm ngặt hơn; tác động dự kiến nhỏ (cả hai đều PIT,
  chỉ khác độ trễ công bố).
- Không audit chi tiết SIGNAL_V11 4 tier (MEGA/MOMENTUM/DEEP_VALUE_RECOVERY/RE_BACKLOG_BUY) — chỉ
  phần basket-component (custom_basket.build_pit) đã xác nhận đầy đủ.
- LOO ở đây là "xoá nguyên năm, nối chuỗi lại" — biến động lớn một phần vì bản thân effect size
  full-period đã gần 0 (bất kỳ nhiễu năm nào cũng đủ đổi dấu số nhỏ).
