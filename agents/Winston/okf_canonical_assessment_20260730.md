# Đánh giá OKF-hoá `kb/canonical.md` — BƯỚC 1 (chỉ đánh giá, CHƯA thực thi)

> Job `Winston_20260730_141312` · Winston (data-ops) · 2026-07-30
> Kết luận ngắn: **KHÔNG nên OKF-split `canonical.md`** (kết quả kiểu cron_registry, không phải
> data_registry). Lý do KHÔNG phải "ít mục quá" mà là: **tầng chi tiết đã tồn tại sẵn**
> (`kb/KNOWLEDGE.md` §1-9) và tầng đó **đang trôi số so với canonical.md** — thêm 1 tầng thứ 3 sẽ
> nhân bản đúng lỗi đang có. Đề xuất thay thế: **trim tại chỗ ~2KB + sửa 3 chỗ stale/drift đo được**.

---

## 0. Số đo thật (không ước lượng)

| Thành phần `context_pack.md` | Byte | % pack |
|---|---:|---:|
| `current_ops.md` | 24 808 | 63% |
| **`canonical.md`** | **7 323** | **19%** |
| `projects/INDEX.md` | 4 415 | 11% |
| RECENT + header + footer | ~2 595 | 7% |
| **Tổng `context_pack.md`** | **39 141** | ngưỡng mới 45 000 → còn dư **5 859 B** |

Trần trên của mọi phương án ở file này = 7,3KB (19% pack). Cắt được 30% canonical = tiết kiệm
2,2KB = **5,6% pack**. Đây là bối cảnh cần nhớ khi cân nhắc chi phí cấu trúc.

## 1. Phát hiện quyết định — tầng chi tiết ĐÃ CÓ, và ĐANG TRÔI

`canonical.md` **không phải** file gốc như `data_registry.md`/`cron_registry.md` (2 file đó là
nguồn duy nhất của nội dung chúng chứa). Nó là **bản digest của `kb/KNOWLEDGE.md`** (40 078 B,
§1-9, KHÔNG được inject — đọc theo yêu cầu). Ánh xạ 1-1 đo được:

| Mục canonical.md | Bản chi tiết đã tồn tại |
|---|---|
| V2.4 | `KNOWLEDGE.md` §1 + `data/results_registry.md` |
| Đã thử BỊ LOẠI | `KNOWLEDGE.md` §1 (đầy đủ hơn: 10 mục có lý do, canonical chỉ 9 mục 1 dòng) |
| MOM_N/MOM_S | `kb/projects/momentum-deals.md` + `agents/Taylor/plan_close_mom_20260712.md` |
| DT5G | `KNOWLEDGE.md` §2 + `kb/data_registry/market-state/` |
| 8L Rating | `KNOWLEDGE.md` §7 |
| Hạ tầng giao dịch | `KNOWLEDGE.md` §4 + `kb/ops_runbook.md` (bảng giờ) + `current_ops.md` (routing) |
| Kiến trúc fleet | `KNOWLEDGE.md` §3 + `MIKE.md` |
| Quy chuẩn làm việc | `KNOWLEDGE.md` §1 (multiple-testing) + `coding_guidelines.md` |
| Cổ phiếu / banned | `KNOWLEDGE.md` §6 + `kb/context_safety_core.md` |
| Backup/DR | `KNOWLEDGE.md` §4 |

**Duplication này ĐÃ trôi thật (3 bằng chứng, không suy đoán):**
1. `KNOWLEDGE.md:19` vẫn khẳng định *"pin gốc vẫn là số tham chiếu chính thức"* = **CAGR 28.05% /
   Sharpe 1.87 / DD −18.8%** — trong khi `canonical.md` (và `results_registry.md`) đã re-pin
   **27.60% / 1.84 / −17.5%** từ 2026-07-29. Hai tầng nói 2 số khác nhau cho cùng 1 pin "chính thức".
2. `KNOWLEDGE.md` §9 bảng cron ghi `19:30 send_plan_report` + `15:00 eod_trading_report`, trong khi
   `ops_runbook.md` (nguồn sống) ghi **21:00** và **19:10**.
3. `KNOWLEDGE.md` §2 vẫn mô tả sự cố DT5G 07-10 ở trạng thái *"publish BQ ĐANG CHỜ"* (đã đóng từ lâu).

⇒ Tạo `kb/canonical/<topic>.md` = **tầng thứ 3** cho cùng nội dung. Với 1 file digest (không phải
registry), tách không loại bỏ bản sao nào — nó **thêm** một bản sao nữa phải đồng bộ. Đây chính là
lớp rủi ro mà brief lo (SIGNAL_V11 base-leak): rủi ro ở đây không đến từ "quên tra", mà từ
"tra đúng chỗ nhưng chỗ đó cũ".

## 2. Bảng đánh giá TỪNG MỤC (11 mục, có lý do + số đo)

Cột "Phải biết NGAY?" = Mike/Taylor có thể **ra quyết định sai** nếu không thấy dòng này mà không
biết là mình cần tra.

| # | Mục | Byte | Phải biết NGAY? | Verdict | Lý do (đo được) |
|---|---|---:|---|---|---|
| 1 | Header + Mục tiêu | 420 | — | **GỘP** (−~120B) | "Mục tiêu" lặp nguyên dòng 3 header + mục V2.4. Không mất fact nào. |
| 2 | V2.4 chiến lược trung tâm | 1 713 | **CÓ** | **GIỮ INLINE** (nén câu chữ ~200B, KHÔNG tách) | Số headline + 2 caveat (MIXED-universe, anchor DD ~−30% chứ không −17,5%) đúng là loại fact Taylor trích dẫn hàng ngày; trích sai vintage = lỗi đã xảy ra thật (07-22/07-29). Tách = mời gọi trích số cũ. |
| 3 | Đã thử BỊ LOẠI | 364 | **CÓ** (negative knowledge) | **GIỮ INLINE** + trỏ `KNOWLEDGE.md §1` | 9 mục / 364B = đã cực nén (~40B/mục). Tách tiết kiệm ~250B nhưng bỏ mất trigger "nhận ra ngay" — mà đây đúng là chức năng duy nhất của mục này (Taylor định đề xuất lại → phải thấy, không phải nhớ đi tra). Chi phí/lợi ích âm. |
| 4 | MOM_N/MOM_S đã đóng | 426 | Một phần | **TRIM còn 1 dòng** (−~300B) | `projects/INDEX.md:16` — **đã nằm trong CÙNG context_pack** — đã ghi "2026-07-12 đóng kênh MOM_N/MOM_S → kb/projects/momentum-deals.md". 3 dòng giải thích "vì sao" là trùng lặp trong cùng 1 pack. ⚠️ KHÔNG xoá hẳn: `KNOWLEDGE.md` **không hề có** MOM (curated 07-11, đóng 07-12) — canonical + projects/ là nơi duy nhất. |
| 5 | DT5G | 344 | **CÓ (bẫy sự cố thật)** | **GIỮ INLINE VERBATIM**, bỏ 1 dòng stale (−~70B) | 2 dòng đầu = bẫy `vnindex_5state` base vs `dt5g_live` — bất khả xâm phạm. Dòng "State hiện tại 2026-07-01: NEUTRAL(3)" đã **cũ 29 ngày** và trạng thái live là việc của `current_ops.md`/`golive_state_today` → xoá (giữ fact tĩnh, bỏ fact động). |
| 6 | 8L Rating & Composite | 357 | **CÓ** | **GIỮ INLINE** | "Rating = binary gate ≤3, KHÔNG phải return-tilt" + golden floor là rule Taylor áp mỗi lần chạm selector; gate LAG rating≤3 vừa được user chốt cứng 07-27. Đã nén tối đa. |
| 7 | Hạ tầng giao dịch | 959 | Phần lớn KHÔNG | **TRIM MẠNH còn ~2 dòng** (−~700B) ⇐ **thắng lớn nhất** | Đã xác minh trùng lặp thật, không đoán: chuỗi giờ 21:00/08:45/09:05/13:00/19:10 nằm nguyên trong bảng `ops_runbook.md:28-40` (chính canonical đã tự ghi "giờ chuẩn tắc ở kb/ops_runbook.md"); routing 2 topic Discord nằm ở `current_ops.md:211,225-227` (**cùng pack**); BOT_STOP nằm ở `context_safety_core.md` + `current_ops.md:256`; bq_cache/OTP/PHS nằm ở `KNOWLEDGE.md` §4. GIỮ: `BOT_STOP` (1 dòng) + `bot_execute.py` deterministic ≠ LLM. |
| 8 | Kiến trúc fleet | 655 | Một phần | **TRIM ~3 dòng** (−~300B) | GIỮ: quant-skeptic REFUTED/INCONCLUSIVE = KHÔNG wire (gate production, Taylor cần thấy); execution bằng Python chứ không LLM headless. BỎ: lịch sử daemon + cơ chế dispatch — Mike đã import `MIKE.md`, Taylor đã có mục "Dispatch ngang hàng" trong CLAUDE.md riêng. |
| 9 | Quy chuẩn làm việc (5 mục) | 1 517 | **CÓ (headline)** | **GIỮ ngưỡng VERBATIM, trim narrative** (−~400B) | Mục 5 chiếm ~1,1KB. **DSR<0.95 = RED FLAG, PBO≥0.5, per-year LOO, N trials** — giữ nguyên từng chữ. Trim: câu chuyện Wave1/H8a (đã có `KNOWLEDGE.md` §8 bảng incident) + chi tiết annex V2.4 (DSR≈1.0/PBO≈0.20 → giữ 1 cụm ngắn + trỏ `results_registry.md`). |
| 10 | Cổ phiếu — quy tắc nhanh | 467 | **CÓ (BANNED)** | **GIỮ INLINE VERBATIM**, trim dòng sector-sweep (−~150B) | ⚠️ Đã kiểm: **Mike và Taylor KHÔNG import `context_safety_core.md`** (chỉ Winston/Spyros/DollarBill/Mafee import). Với 2 audience thật của file này, `canonical.md` là **nguồn inline DUY NHẤT** của danh sách BANNED → tuyệt đối không tách. Dòng "sector sweeps #1–9 = lens/tilt" là kết luận R&D đã đóng → trỏ `KNOWLEDGE.md` §7. |
| 11 | Backup / DR | 101 | KHÔNG | **BỎ** (−101B) hoặc giữ nguyên | Trùng `KNOWLEDGE.md` §4 + memory. 1 dòng/101B — bỏ hay giữ đều không đáng tranh luận; nghiêng về BỎ cho nhất quán nguyên tắc (fact vận hành không thuộc "hiến pháp chiến lược"). |

**Đếm điều kiện tách của brief (≥3-4 mục đủ điều kiện tách sang `kb/canonical/`):**
đủ điều kiện = **0 mục**. Mục có nội dung "chỉ cần khi chạm" (4, 7, 8, 9-narrative, 10-sector, 11)
đều đã có **đích đến sẵn** (`ops_runbook.md`, `current_ops.md`, `KNOWLEDGE.md`, `projects/`) —
tách sang `kb/canonical/` sẽ tạo đích **thứ hai** cho cùng nội dung.

## 3. So sánh 2 phương án (chi phí thật)

| | A. OKF-split `kb/canonical/` | B. Trim tại chỗ + trỏ nguồn ĐÃ CÓ ✅ đề xuất |
|---|---|---|
| Byte cắt khỏi pack | ~2,0KB | ~2,0KB (tương đương) |
| Byte MỚI tạo ra | +2–3KB (index.md + CHANGELOG.md + frontmatter + pointer) | ~0 |
| Số bản sao của cùng 1 fact | **3** (canonical + KNOWLEDGE + canonical/) | 2 (như hiện tại, có giảm ở phần trùng) |
| Rủi ro tra trúng bản cũ | **Tăng** (đã có bằng chứng trôi ở §1) | Không đổi |
| Khớp brief | Có hình thức OKF | Đúng discipline 2 lần trim `current_ops.md` |

Ước tính sau phương án B: `canonical.md` **7 323 → ~5 300B**, `context_pack.md` **39 141 → ~37 100B**
(dư 7,9KB dưới ngưỡng 45KB). *(Ước tính; sẽ đo thật bằng `wc -c` + `publish_context.sh` nếu được duyệt.)*

## 4. Ba lỗi fact/stale phát hiện được trong lúc audit (độc lập với quyết định tách hay không)

1. `canonical.md:41` — "State hiện tại 2026-07-01: NEUTRAL(3)" — fact động nằm trong file "hiến
   pháp" tĩnh, đã cũ 29 ngày.
2. `KNOWLEDGE.md:19` — vẫn ghi 28.05% là "số tham chiếu chính thức" (mâu thuẫn re-pin 27.60% 07-29).
3. `KNOWLEDGE.md` §9 — bảng cron sai giờ (19:30/15:00 vs thật 21:00/19:10); §2 mô tả sự cố 07-10 như
   đang mở.

Đề xuất xử lý #2/#3: KHÔNG sửa số ở `KNOWLEDGE.md` bằng cách chép lại (sẽ trôi tiếp) — thay bằng
**trỏ 1 dòng** tới `data/results_registry.md` / `kb/ops_runbook.md` là nguồn sống. *(Ngoài phạm vi
job này — cần Mike duyệt riêng vì `KNOWLEDGE.md` do Mike biên tập.)*

## 5. Việc đang chờ Mike quyết

- **[Q1]** Chốt: dừng ở kết luận "không OKF-split" (kết quả hợp lệ, giống cron_registry), hay vẫn
  muốn tách cho đồng bộ hình thức?
- **[Q2]** Có duyệt phương án B (trim tại chỗ ~2KB, giữ VERBATIM mọi ngưỡng/cảnh báo, verify
  diff-based như 2 lần trước)? Winston làm được ngay, chưa commit đến khi Mike đọc diff.
- **[Q3]** 3 lỗi stale ở §4 — sửa trong cùng lượt hay tách job riêng (`KNOWLEDGE.md` là file Mike
  biên tập)?

**CHƯA thay đổi file production nào trong job này** (read-only + 1 file báo cáo này).

---

# BƯỚC 2 — THỰC THI (job `Winston_20260730_142006`, Mike duyệt Q1/Q2/Q3)

> Q1: không OKF-split ✔ · Q2: phương án B (trim tại chỗ) ✔ · Q3: sửa 3 lỗi stale `KNOWLEDGE.md` ✔
> **CHƯA commit** — chờ Mike đọc diff (+ arch-review nếu muốn).

## A. Số đo THẬT (`wc -c`, sau `publish_context.sh` → v1538)

| File | Trước | Sau | Δ | Ước tính ở bước 1 | Lệch |
|---|---:|---:|---:|---:|---:|
| `kb/canonical.md` | 7 323 | **5 969** | **−1 354 (−18,5%)** | ~5 300 | +669 |
| `kb/context_pack.md` | 39 097¹ | **37 743** | **−1 354 (−3,5%)** | ~37 100 | +643 |
| `kb/KNOWLEDGE.md` | 40 078 | 41 489 | +1 411 | — | (không inject → 0 chi phí pack) |

¹ Bước 1 đo 39 141; pack đã trôi −44B giữa 2 lần đo (file khác cập nhật), không phải sai số của job này.

**Vì sao hụt ~670B so với ước tính:** ước tính bước 1 tính phần XOÁ mà chưa trừ phần THÊM — mỗi mục
trim đều phải giữ lại 1 dòng con trỏ tới nguồn thật (`ops_runbook.md` / `current_ops.md` /
`KNOWLEDGE.md` §3-4-7 / `momentum-deals.md`). Bỏ nốt các con trỏ này sẽ đạt đúng ~5 300B nhưng phá
chính nguyên tắc của phương án B (trỏ tới file ĐÃ CÓ, không để fact mồ côi). **Không ép cho khớp số.**
Dư dưới ngưỡng 45 000: **7 257B**.

## B. Diff `canonical.md` — 15 dòng thêm / 33 dòng xoá

| Mục | Hành động | Δ thực |
|---|---|---:|
| Header + Mục tiêu | gộp 6 dòng → 4; bump "Cập nhật" 07-01 → 07-30 | ~−95 |
| MOM_N/MOM_S | bỏ heading `###` + 2 dòng "vì sao" → 3 dòng, trỏ `momentum-deals.md` | ~−140 |
| DT5G | xoá fact ĐỘNG `State hiện tại 2026-07-01: NEUTRAL(3)` (cũ 29 ngày) → trỏ `current_ops.md`/`golive_state_today`. **3 dòng bẫy base-vs-live giữ nguyên byte** | ~0 |
| Hạ tầng giao dịch | xoá 7 dòng (run_bot wrapper, bq_cache, Gmail-OTP, PHS, chuỗi giờ, 2 topic-id) → 2 dòng con trỏ. GIỮ: `BOT_STOP`, `bot_execute.py` deterministic | ~−630 |
| Kiến trúc fleet | xoá 4 dòng daemon/dispatch → 1 dòng trỏ `MIKE.md` + §3. GIỮ: quant-skeptic gate, Execution | ~−325 |
| Quy chuẩn §5 | bỏ narrative Wave1/H8a + tên script + "R&D Q3 program H2" + "(parking/lever/basket sweep)". **Mọi ngưỡng giữ nguyên byte** | ~−300 |
| Cổ phiếu | dòng sector-sweep #1–9 → con trỏ §7. **Dòng BANNED KHÔNG chạm** | ~−90 |
| Backup / DR | BỎ hẳn (trùng §4 + memory) | −110 |

## C. Verify verbatim 6 mục GIỮ INLINE — **PASS 6/6** (so byte với `git show HEAD:kb/canonical.md`)

| Mục | Cách kiểm | Kết quả |
|---|---|---|
| V2.4 (headline + MIXED-universe + anchor DD) | so **nguyên section** | PASS — 1 713B ↔ 1 713B, 0 hunk diff |
| Đã thử BỊ LOẠI | so **nguyên block** | PASS — 363B, khớp tuyệt đối |
| DT5G trap | so từng dòng (`Production:` / `KHÔNG đọc vnindex_5state` / `Gate phòng thủ`) | PASS 3/3 |
| 8L Rating & Composite | so **nguyên section** | PASS — 357B ↔ 357B |
| DSR/PBO | so 5 chuỗi ngưỡng: `DSR < 0.95 → RED FLAG` · `PBO≥0.5 = ưu tiên config robust-trung vị thay vì IS-best` · `per-year leave-one-out` · `N trials (số config…)` · `DSR≈1.0, PBO≈0.20` | PASS 5/5 |
| **BANNED tickers** | parse list → so **từng mã** | PASS — **13/13 mã trùng khớp, đúng thứ tự**: PC1, VVS, KSF, NKG, HSG, HVN, VJC, NVL, GEG, SBA, DMC/IMP/TRA, TOS, VTP |

Hậu kiểm sau publish: `canonical.md` nhúng **nguyên khối** trong `context_pack.md` ✔; 5 chuỗi
sống-còn (BANNED / DSR gate / DT5G trap / pin R3 / BOT_STOP) đều có mặt trong pack ✔.

## D. Sửa stale `KNOWLEDGE.md` (Q3) — 3 mục Mike giao + 1 phát sinh, tất cả đối chiếu nguồn

| # | Chỗ | Trước | Sau | Nguồn đối chiếu |
|---|---|---|---|---|
| a | §1 pin R3 | 28.05% / 1.87 / −18.8% / 1.50 là "số tham chiếu chính thức" | **27.60% / 1.84 / −17.5% / 1.58** (pin 07-29, `universe_pit`) + **giữ đủ dấu vết 3 vintage cũ** (27.16 / 27.84 / 28.05 kèm lý do không so trực tiếp) | `data/results_registry.md` §"2026-07-29 — ⭐ RE-PIN R3 SAU RESTATE DT5G" |
| b | §9 bảng cron | 17:30 freshness · 19:30 plan · 15:00 EOD | **19:00 · 21:00 · 19:10**, kèm ngày đổi + ghi rõ nguồn sống là `ops_runbook.md`/`crontab -l` | `kb/ops_runbook.md:26,28,40` **+ `crontab -l` thật** (không chỉ tin doc) |
| c | §2 sự cố DT5G 07-10 | "ĐÃ FIX local, publish BQ ĐANG CHỜ" + "câu hỏi mở, chờ user/Mike" | **ĐÃ ĐÓNG 2026-07-13** (đường B zero-touch: backfill tay tối CN 07-12 + cron 18:30 T2 07-13 recompute & publish; lúc stale `get_gated_state()` fail-closed DT4-only, DT4==DT5G==NEUTRAL). Root-cause giữ nguyên làm bài học | `kb/INCIDENTS.md:322-347` (mục 2026-07-13) |
| **d** | §2 dòng cuối *(phát sinh — báo Mike)* | "**Đề xuất chưa áp dụng** (chờ Mike duyệt): thêm post-chain assertion" | **ĐÃ WIRE** — `daily_refresh_v34b_linux.sh` step **[8b]** `assert_chain_outputs.sh "$CHAIN_START_EPOCH"`, die TRƯỚC publish BQ | đọc thẳng code `daily_refresh_v34b_linux.sh:93-115` |

⚠️ **2 chỗ vượt nhẹ chỉ đạo, báo minh bạch để Mike bác nếu muốn:**
1. Mục **(d)** không nằm trong 3 lỗi Mike liệt kê — nhưng cùng section §2 và cùng loại "trạng thái
   treo đã đóng"; xác minh bằng CODE chứ không suy đoán. Để nguyên sẽ mâu thuẫn với header vừa sửa.
2. §4 (`KNOWLEDGE.md:163`, dòng "Workflow ngày trading đầy đủ") **cũng** chép 17:30/19:30/15:00 —
   sửa luôn cho khớp §9, nếu không file tự mâu thuẫn với chính nó ngay sau khi sửa (b).

## E. Còn treo cho Mike

- **Chưa `git commit`** (đúng yêu cầu). 3 file đổi: `kb/canonical.md`, `kb/KNOWLEDGE.md`, `kb/context_pack.md` (auto-publish v1538).
- Memory entry `project-dt5g-ewleg-bugfix-pending-monday-publish.md` vẫn ghi "pending Monday publish"
  → nay đã đóng (07-13). **Winston không sửa memory của Mike** — Mike tự cập nhật/xoá.
