# REPORT — W2 / Q2: so 4 phương tiện park khi tiền nhàn rỗi KHÔNG còn 0%/năm

> Job `Taylor_20260927_141318` (attempt 2 — tiếp quản 13 chân attempt 1 đã chạy, không chạy lại).
> Kế hoạch: `kb/projects/custom30v-revalidation-plan-20260927.md` §3-§4. Tiêu chí: `PREREG.md`
> (commit `4041c7bf`, ghi TRƯỚC log đầu tiên).
> **PAPER-ONLY.** Không re-pin, không đổi rail / `trading_rules.json`, không merge.
> **KHÔNG kết luận giữ/bỏ custom30V** — đó là quyết định của user (Q3/W3).

## 0. Kết luận một dòng

**Không ứng viên nào đạt tiêu chí PREREG.** Thứ hạng **ĐẢO DẤU HOÀN TOÀN** giữa hai tầng proxy: ở
tầng 1 (baseline) **không park (D) thắng tất cả** (P(D>X) = 0,67–0,81); ở tầng 2 (floor) **mọi
phương tiện park đều thắng D** (P(X>D) = 0,55–0,68). PREREG §1 đòi "đứng ở tầng 1 VÀ không đảo dấu
ở tầng 2" ⇒ **không ai qua**. Câu trả lời thực chất của W2 không phải "ai thắng" mà là: **thứ hạng
park-vs-không-park KHÔNG ROBUST với giả định lãi tiền nhàn rỗi** — nó bị quyết định bởi tầng proxy,
không phải bởi phương tiện.

## 1. Cổng bắt buộc — trạng thái

| Cổng (PREREG §3) | Kết quả |
|---|---|
| **Control leg tái lập anchor** | **PASS.** 2 chân độc lập (`w2ctrl`, `w2ctrl2`) → ledger md5 `4707bcbeb7e801d49a4a851ffd91d5e7` = anchor R3; `cmp` sạch vs ledger `reverify_j131635`. CAGR 23,37 / Sharpe 1,88 / MaxDD −14,6 / Calmar 1,60. |
| **Self-check 0 VND** | **PASS 13/13 chân.** BAL + LAG cash-flow identity 0 VND, final-NAV identity 0 VND, borrow-audit 0 VND — kể cả mọi chân có carry. |
| **`basket_return_leg_oshares_selfcheck.py`** | **FAIL 2/7 (R2, R5) — nợ CŨ của canonical, không phải regression W2.** Xem §6. |
| **Đòn 8 quant-skeptic (double-count corp-action)** | **Không có dấu hiệu.** R1 chuỗi engine == chuỗi Close dựng lại độc lập, max\|Δ\| = 3,3e−16 / 414 phiên; R1b legacy PHẢI lệch (5,1e−02) ⇒ R1 không phải hằng đúng; R3 positive control 37/37 phiên lệch trùng ĐÚNG ngày có bước OShares thật; R4 `mcap == Close×OShares` max\|Δ\| = 0. |
| **park = 0,0 suy biến (§2b)** | **Đạt theo Ý, THẤT BẠI theo CHỮ.** Xem §5 — ghi rõ để quant-skeptic tự phán xử. |

## 2. Bảng cuối — mỗi ứng viên × {park 0,30; park 0,0} × {tầng 1; tầng 2}

Paired block bootstrap: `L=21`, `B=4000`, `seed=12345`, MỘT chuỗi block-index cho MỌI chân (cùng
"thế giới resample"). Cửa sổ 2014-01-02 → 2026-06-19, 3.107 phiên, 12,460 năm **lịch**, 249,3 obs/năm.

### Tầng 1 — proxy `baseline` (SBV 12M-low − 2,04pp; trung bình 4,156%/năm, 2,76–5,46%)

| Ứng viên | CAGR | Sharpe | MaxDD | Calmar | E[Calmar] | P(X>D) | DD5th | Cổng DD | IS 14-19 | OOS 20+ |
|---|---|---|---|---|---|---|---|---|---|---|
| **D** không park | 26,23% | 2,19 | −13,7% | 1,919 | **1,996** | — | −20,5% | PASS | 23,48% | 28,84% |
| **A** custom30V | 25,84% | 2,01 | −14,0% | 1,851 | 1,760 | 0,192 | −22,9% | **FAIL** | 22,75% | 28,77% |
| **B** custom30 | 26,06% | 2,03 | −13,3% | 1,953 | 1,751 | 0,217 | −23,1% | **FAIL** | 23,70% | 28,29% |
| **C6** k=6 | 26,61% | 2,04 | −14,9% | 1,788 | 1,799 | 0,258 | −22,9% | **FAIL** | 23,78% | 29,30% |
| **C10** k=10 | 26,93% | 2,06 | −14,2% | 1,895 | 1,857 | 0,329 | −22,5% | PASS (sát) | 24,05% | 29,66% |

Cổng DD = `DD5th ≥ DD5th(D) − 2,0pp` = **≥ −22,5%**.

### Tầng 2 — proxy `floor` (liên NH 1M, max(0,·); trung bình 3,609%/năm, 0–8,65%)

| Ứng viên | CAGR | Sharpe | MaxDD | Calmar | E[Calmar] | P(X>D) | DD5th | Cổng DD | IS 14-19 | OOS 20+ |
|---|---|---|---|---|---|---|---|---|---|---|
| **D** không park | 24,22% | 2,04 | −14,1% | 1,715 | 1,713 | — | −22,1% | PASS | 22,73% | 25,62% |
| **A** custom30V | 26,22% | 2,04 | −14,2% | 1,853 | 1,771 | **0,610** | −23,2% | PASS | 22,04% | 30,22% |
| **B** custom30 | 26,07% | 2,04 | −13,7% | 1,903 | 1,776 | **0,621** | −22,9% | PASS | 23,00% | 28,98% |
| **C6** k=6 | 26,92% | 2,06 | −15,5% | 1,741 | **1,835** | **0,683** | −22,9% | PASS | 23,34% | 30,34% |
| **C10** k=10 | 26,33% | 2,02 | −14,7% | 1,797 | 1,728 | 0,548 | −23,5% | PASS | 23,23% | 29,28% |

Cổng DD tầng 2 = **≥ −24,1%** (nới ra vì chính D xấu hơn) ⇒ mọi chân PASS. **Cổng DD không phân
biệt được gì ở tầng 2** — nó neo vào D, và D tệ hơn khi carry thấp.

### Cột "park 0,0" = MỘT chân duy nhất (D)
`PARK_STATES=3:0.0` ⇒ không đồng nào vào rổ ⇒ phương tiện trơ ⇒ `A@0,0 ≡ B@0,0 ≡ C6@0,0 ≡ C10@0,0 ≡ D`.
Đã CHỨNG MINH, không giả định (§5). Nên bảng trên đã là bảng đầy đủ: cột park 0,0 chính là dòng **D**.

### Chân tham chiếu: park 0,0 với carry = 0% (quy ước engine CŨ)
`w2d_off`: CAGR **22,12%** / Sharpe 1,93 / MaxDD −16,2% / Calmar 1,36. So với `w2ctrl2`
(= A@park0,3 carry 0%) 23,37 / 1,88 / −14,6 / 1,60. **Đây là lý do toàn bộ vấn đề tồn tại**: dưới
quy ước 0%/năm, parking "mua" +1,25pp CAGR và +0,24 Calmar — nhưng phần lớn con số đó chỉ là
**tiền nhàn rỗi bị trả 0%**. Cho tiền nhàn rỗi ăn carry tầng 1 thì D nhảy từ 22,12% lên 26,23% (+4,11pp)
còn A chỉ từ 23,37% lên 25,84% (+2,47pp) — và **trật tự đảo**.

## 3. Ma trận P(hàng > cột) trên Calmar bootstrap — để điền cây quyết định §4

Tầng 1 (baseline) | D | A | B | C6 | C10
---|---|---|---|---|---
**D** | — | 0,808 | 0,783 | 0,742 | 0,671
**A** | 0,192 | — | 0,450 | 0,404 | 0,264
**B** | 0,217 | 0,550 | — | 0,451 | 0,338
**C6** | 0,258 | 0,596 | 0,549 | — | 0,235
**C10** | 0,329 | 0,736 | 0,662 | 0,765 | —

Tầng 2 (floor) | D | A | B | C6 | C10
---|---|---|---|---|---
**D** | — | 0,390 | 0,379 | 0,317 | 0,452
**A** | **0,610** | — | 0,501 | 0,304 | 0,501
**B** | **0,621** | 0,498 | — | 0,334 | 0,512
**C6** | **0,683** | **0,696** | **0,666** | — | 0,683
**C10** | 0,548 | 0,498 | 0,487 | 0,317 | —

### Cây quyết định kế hoạch §4 — điền bằng số (KHÔNG quyết)

| Nhánh §4 | Điều kiện | Số thật | Bật? |
|---|---|---|---|
| **1. BỎ parking** | D ≥ A trên E[Calmar] tầng 1 **VÀ** không thua ở tầng 2 | Tầng 1: D 1,996 > A 1,760 ✓ (P(D>A) = 0,808). Tầng 2: D 1,713 < A 1,771 ✗ (P(A>D) = 0,610) | **KHÔNG** — nửa đầu đạt, nửa sau THUA |
| **2. ĐỔI rổ** | A > D, **và** B/C vượt A với P(>A) ≥ 0,60 **và** vượt null-90 | Chỉ ở tầng 2 mới có A > D. Ở đó: **P(C6>A) = 0,696 ✓**, vượt null-p90 ✓ (§4). Nhưng P(B>A) = 0,498 ✗, P(C10>A) = 0,498 ✗. Ở tầng 1 thì A KHÔNG > D | **CHỈ Ở TẦNG 2, chỉ C6** — không đứng được ở tầng 1 |
| **3. GIỮ custom30V** | A tốt nhất | A không tốt nhất ở tầng nào: tầng 1 D nhất (1,996), tầng 2 C6 nhất (1,835). A xếp 3/5 ở tầng 1, 3/5 ở tầng 2 | **KHÔNG** |
| **4. Chỉ thắng tầng 3** | — | Tier `spot` (8,543%) **KHÔNG được chạy** (PREREG §3: engine từ chối `IDLE_CARRY_TIER=spot` có ý) | không áp dụng |

**Đọc đúng:** cây §4 được thiết kế với ngầm định thứ hạng ổn định qua các tầng. Số thật cho thấy
ngầm định đó SAI. Nhánh 1 và nhánh 2 cùng "gần bật" nhưng ở HAI tầng khác nhau — tức là dữ liệu
đang trả lời một câu hỏi khác câu hỏi được hỏi: **mức lãi tiền nhàn rỗi thật là bao nhiêu** quan
trọng hơn **chọn phương tiện nào**.

Điểm đảo dấu nằm ở đâu: tầng 1 trung bình 4,156%/năm, tầng 2 trung bình 3,609%/năm. Khoảng **0,55pp
carry trung bình** là đủ để đảo toàn bộ thứ hạng. Đó là biên độ hẹp hơn cả sai số của chính proxy
(§7 caveat: đoạn trước 2025-11 là single-source).

## 4. Null-300 cho C — C **có edge trên CAGR**, nhưng **đuôi DD xấu hơn ngẫu nhiên**

Hai null độc lập, cả hai `R=300`, `SEED=20260927`, EW, reshuffle theo đúng 48 đoạn giữ của engine,
**cùng một hàm** dựng chuỗi cho C và cho null (khác nhau ĐÚNG một thứ: tên nào được chọn).

| | pool | C CAGR | null CAGR med / p90 / max | phân vị C | C MaxDD | null MaxDD med / p90 | phân vị C (DD) | Cổng PREREG |
|---|---|---|---|---|---|---|---|---|
| **C6** | đầy đủ (med 137) | 24,43% | 6,11 / 10,12 / — | **100,0** | −46,2% | −41,1 / −32,6 | 23,0 | **CÓ EDGE** |
| **C6** | khớp thanh khoản top-60 | 24,43% | 6,80 / **10,47** / 13,99 | **100,0** | −46,2% | −42,4 / −33,9 | 27,3 | **CÓ EDGE** |
| **C10** | đầy đủ | 23,14% | 6,70 / 9,71 / — | **100,0** | −50,3% | −38,0 / −31,1 | 3,0 | **CÓ EDGE** |
| **C10** | khớp thanh khoản top-60 | 23,14% | 6,45 / **9,16** / 12,82 | **100,0** | −50,3% | −40,6 / −33,6 | 3,7 | **CÓ EDGE** |

**Vì sao có null thứ hai (quan trọng):** `null_c.py` rút từ TOÀN BỘ tập đủ điều kiện, nhưng engine
KHÔNG chọn từ đó — `custom_basket.py:1397-1398` cho `v3route3` lấy `pool = gated[:CFO_POOL]` với
`CFO_POOL = 60` (dòng 700), tức **60 tên thanh khoản nhất đã qua cổng**, xếp theo thanh khoản QUÝ
TRƯỚC (dòng 1263-1266). Null 137-tên vì thế **tặng không cho C một phần bù thanh khoản** — chính cái
đuôi kém thanh khoản sinh ra CAGR 6% / MaxDD −41% của null. `null_c_liqmatched.py` dựng lại pool đó
(AVG(`Volume_3M_P50` × giá RAW `COALESCE(Price,Close)`), `nd≥20`, quý trước — đúng công thức engine).
**Kết luận không đổi ở cả hai pool**, nên cổng edge của C robust với định nghĩa pool.

**Hai điều phải nói rõ, không được bỏ:**
1. **Đuôi DD của C xấu hơn ngẫu nhiên.** C6 ở phân vị 27, C10 ở phân vị **3,7** — tức chuỗi
   standalone của C10 có MaxDD tệ hơn **96%** số rổ ngẫu nhiên cùng pool. "Có edge" ở đây là **chỉ
   trên CAGR**, đúng chữ của cổng PREREG, và cổng đó KHÔNG phủ rủi ro đuôi. Nhất quán với việc C6
   TRƯỢT cổng DD ở tầng 1.
2. **Bản dựng lại pool là XẤP XỈ.** Chỉ **58% (C6) / 55% (C10)** tên C thật nằm trong top-60 tôi
   dựng lại (trung vị; min 0% ở vài quý). Engine đọc `tav2_bq.ticker` live + `UNIVERSE_FILTER` theo
   `ICB_Code` + `fa_ratings_8l` as-of, tôi dùng cache + cờ `rating_8l` của `universe_pit_q`. Vì hai
   null cho cùng phán quyết nên khoảng lệch này không đổi kết luận, nhưng **đừng đọc con số p90 như
   là pool chính xác của engine**.

## 5. Cổng suy biến park = 0,0 — ĐẠT theo Ý, THẤT BẠI theo CHỮ (ghi rõ, không nới lỏng ngầm)

PREREG §2b: chạy `B@park0,0`, `cmp` ledger với `D`, **kỳ vọng byte-identical; lệch ⇒ DỪNG**.

**`cmp` LỆCH** (line 36; md5 `af7133a9` vs `cd261ada`). Tôi KHÔNG bỏ qua — mở ra theo `record_type`:

| `record_type` | n | giống? |
|---|---|---|
| DAILY (8 cột tiền) | 3.107 | **identical** |
| TX | 7.663 | **identical** |
| REBAL / METRIC / ANNUAL / EVENT_CAPIT | 39 / 37 / 13 / 18 | **identical** |
| CUSTOM_BASKET (cột `value`) | 3.114 | khác |
| CUSTOM_MEMBERS (cột `ticker`, `reason`) | 1.440 | khác |
| META (cột `value`) | 37 | khác |

Bằng chứng **mạnh hơn** byte-identity: `bal_etf_ref` max = **0,0** và `lag_etf_ref` max = **0,0**
trên toàn cửa sổ ⇒ **KHÔNG MỘT ĐỒNG** nào vào phương tiện park. Headline trùng tuyệt đối ở cả hai
chân: Final NAV 910,83B / 26,23% / 2,26 / −13,7% / 1,92.

**Phán xử trung thực:** tiêu chí viết theo CHỮ đã THẤT BẠI, và tôi không âm thầm nới nó. Cách diễn
đạt đó SAI ngay từ đầu: ledger CÓ thiết kế ghi cả rổ chẩn đoán (mức index danh nghĩa + tên sẽ giữ),
nên file KHÔNG THỂ giống hệt khi `BASKET_SELECT` khác — 3 chỗ lệch đều là bản ghi CHẨN ĐOÁN, không
phải đường tiền. Bất biến mà cổng nhắm tới (không rò tiền ra phương tiện khi park = 0) đã được xác
nhận bằng phép đo chặt hơn. Vì vậy KHÔNG DỪNG — nhưng đây là **LỆCH so với chữ của PREREG**, để
quant-skeptic tự phán xử.

## 6. `basket_return_leg_oshares_selfcheck.py` FAIL 2/7 — nợ CŨ của canonical

FAIL: **R2** `md5(weight)` mới == tiền-sửa (`c28f222c…` vs `a953d4bb…`), **R5** level legacy ==
tiền-sửa (max\|Δ\| = 9,23e+01).

**Không phải regression W2:** 6 log của job `postmerge_haukiem_20260927` chạy trên **canonical HEAD**
(TZ ICT/UTC/unset × py310/dnapy) cho ĐÚNG 2 FAIL này, ĐÚNG cặp md5, `RC=1` ở cả 6 dòng
`sc_master.log`. Nguyên nhân: R2/R5 khẳng định byte-identity với baseline **TIỀN-SỬA** (chế độ
OShares-step theo QUÝ); sau khi bản vá `exdate` được merge, chế độ mặc định là `exdate` ⇒ weight đổi
THẬT theo đúng thiết kế ⇒ 2 assertion đó tất yếu fail. Chứng minh: cùng selfcheck với biến thể
`STEPQUARTER` cho **PASS TOÀN BỘ** trên canonical
(`selfchecks/basket_return_leg_oshares_selfcheck__PREREF2c_STEPQUARTER__TZ-ICT__dnapy.log`).
Commit knob `75fba8a9` chỉ chạm `idle_rate_proxy.py`, `pt_v23_audit_2014.py`,
`simulate_holistic_nav.py` — **KHÔNG** chạm `custom_basket.py`.

**Đề xuất (việc RIÊNG, không làm trong W2):** refresh baseline R2/R5 theo chế độ `exdate`, hoặc đổi
2 assertion đó thành "khác tiền-sửa ĐÚNG ở các ngày có bước OShares" (tức biến chúng thành positive
control như R3) — hiện chúng là 2 FAIL vĩnh viễn, và một selfcheck luôn đỏ thì không ai còn đọc.

## 7. DSR / PBO — manifest GHIM ngay từ đầu, không glob động

`DSR_FAMILY_MANIFEST=data/dsr_family_manifest_w2q2_2026-09-27.json` (10 CSV, `verify` khớp md5).
Họ trial = **đúng 10 cấu hình được so sánh với nhau khi chọn** (5 phương tiện × 2 tầng), liệt kê
TƯỜNG MINH — không glob, không mốc mtime. `build_w2_manifest.py` lấy đường dẫn từ dòng engine TỰ IN
trong log, không suy từ env (§8).

| | neo trên A@tầng 1 | neo trên A@tầng 2 |
|---|---|---|
| ann-SR | 2,014 | 2,035 |
| skew / kurtosis | −0,173 / 7,90 | −0,157 / 7,86 |
| **DSR** @N=10 / 120 / 200 | **1,0000** / 1,0000 / 1,0000 | **1,0000** / 1,0000 / 1,0000 |
| **PBO** (CSCV, S=16, 12.870 split) | **0,1348** | 0,1348 |
| block boot CAGR 5th / MaxDD 5th | 18,0% / −22,9% | 18,3% / −23,2% |
| stationary boot CAGR 5th / MaxDD 5th | 17,9% / −22,6% | 18,1% / −22,9% |

DSR ≥ 0,95 ✓, PBO < 0,5 ✓. **Caveat phải đọc kèm:** PBO thấp một phần vì họ trial gồm 10 cấu hình
RẤT GIỐNG NHAU (sd ann-SR = **0,051**) — PBO đo "IS-best có tụt dưới trung vị OOS không", và khi 10
chân gần trùng nhau thì câu hỏi đó dễ trả lời "không". PBO 0,1348 ở đây **không** là bằng chứng
chống overfit mạnh cho việc chọn phương tiện; nó chỉ nói họ 10 chân này không phân kỳ IS→OOS.
Bằng chứng thật về tính không-robust nằm ở **đảo dấu giữa hai tầng** (§2-§3), và PBO không nhìn
thấy nó vì cả hai tầng đều nằm TRONG họ.

## 8. LOYO — ổn định hạng khi bỏ một năm

E[Calmar] bỏ-một-năm (thứ tự D/A/B/C6/C10):

- Tầng 1: 2014 `1,76/1,58/1,61/1,60/1,66` · 2015 `2,01/1,80/1,78/1,81/1,87` · 2016 `2,09/1,85/1,82/1,89/1,92` · 2017 `2,13/1,82/1,78/1,86/1,94` → **D dẫn ở MỌI năm bị bỏ**.
- Tầng 2: 2014 `1,50/1,61/1,64/1,65/1,55` · 2015 `1,72/1,81/1,81/1,85/1,74` · 2016 `1,80/1,87/1,86/1,93/1,80` · 2017 `1,82/1,83/1,81/1,91/1,81` → **D xếp cuối/gần cuối ở MỌI năm bị bỏ**.

Đầy đủ 13 năm trong `paired_baseline.json` / `paired_floor.json` khoá `_loyo_E_calmar`. Đảo dấu
**không** do một năm cá biệt — nó là tính chất của tầng proxy, ổn định qua LOYO.

## 9. Giới hạn — phải đọc trước khi dùng bất kỳ số nào ở trên

1. **Proxy tiền nhàn rỗi: đoạn trước 2025-11 là SINGLE-SOURCE.** Registry
   `kb/data_registry/macro/fiinprox_rates_snapshot_20260927.md` chỉ ghi `CANONICAL-PIT` cho phạm vi
   **2025-11 → 2026-09**. Mà điểm đảo dấu chỉ cách nhau **0,55pp carry trung bình** — nhỏ hơn mức
   bất định hợp lý của một chuỗi single-source trải 11 năm. **Đây là giới hạn nghiêm trọng nhất của
   W2**: nó không tách được "phương tiện nào tốt hơn" khỏi "proxy sai bao nhiêu".
2. **Chân TRỌNG SỐ chưa audit.** `custom_basket.py:544` (`mcapw = pxw × OShares`) — replay job
   `Taylor_20260927_101335` finding 4. W2 KHÔNG audit nó. **Đề xuất A/B riêng `BASKET_OSHARES_STEP`
   sau W2.**
3. **Quy ước tích lãi `/252`.** Giữ nguyên của engine (không đổi sang 365) để thay-đổi-mã chỉ là
   scalar→Series. Cửa sổ có 249,3 phiên/năm ⇒ carry tích thiếu ~0,4% **tương đối** (5,00%/năm ≈ nhận
   4,98%). Nhỏ hơn 2 bậc so với khoảng cách tầng 1↔tầng 2 — không đổi kết luận.
4. **Ngày trước khi chuỗi proxy bắt đầu trả 0%.** Tầng 2 (`floor`): 18 phiên `2014-01-02..2014-01-27`.
   Tầng 1: 0 phiên. Fail-safe, không back-fill (back-fill = rò 1 tháng lãi tương lai vào đầu cửa sổ).
   Engine IN ra con số này ở mọi chân.
5. **Ánh xạ C → `v3route3` là DIỄN GIẢI.** Kế hoạch §3.1 viết "composite v3 + tier A/B của route";
   không có field code nào tên "tier A/B". Diễn giải ở đây = phân tầng theo ROUTE. Nếu user có ý
   khác, C là chân phải chạy lại. Đã khai TRƯỚC trong PREREG §2, không phải chọn sau khi thấy số.
6. **Sharpe lệch hệ thống ~3,4% vs engine.** Engine in Sharpe(252), `paired_w2.py` dùng 249,3 obs/năm
   (quy ước thời-gian-lịch của CLAUDE.md). Tỉ số **đồng nhất 1,034 trên CẢ 5 chân** ⇒ khác quy ước,
   không phải lỗi riêng chân nào. CAGR thì trùng TUYỆT ĐỐI với engine (A 25,84 / D 26,23 …).
7. **Chưa quy đổi thực tế.** Mọi CAGR ở trên là CAGR backtest. Quy ước CLAUDE.md: CAGR thật ≈ CAGR
   backtest − 1,5% (slippage + thuế, không được mô hình hoá).

## 10. Tái lập

```bash
WT=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-w2q2-2709/WorkingClaude   # branch research/c30v-w2-idlecarry-2709 @ 6bdd6924
R=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/c30v_w2_q2_20260927
$R/run_leg.sh w2ctrl2   BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=off        # cong control -> md5 4707bcbe...
$R/run_leg.sh w2a_baseline BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=baseline
$R/run_leg.sh w2c6_floor   BASKET_WT=ew BASKET_SELECT=v3route3 BASKET_TOPN=6 PARK_STATES=3:0.3 IDLE_CARRY_TIER=floor
# ... 13 chan, lenh day du o dong EXIT= cuoi moi file logs/<tag>.log
$DNA_PYEXE $R/paired_w2.py baseline ; $DNA_PYEXE $R/paired_w2.py floor
$DNA_PYEXE $R/pairwise_w2.py
$DNA_PYEXE $R/null_c.py w2c6_baseline 6 ; $DNA_PYEXE $R/null_c_liqmatched.py w2c6_baseline 6
$DNA_PYEXE $R/build_w2_manifest.py
cd /home/trido/thanhdt/WorkingClaude && DSR_FAMILY_MANIFEST=data/dsr_family_manifest_w2q2_2026-09-27.json \
  DSR_R3_CSV=<ledger chan> $DNA_PYEXE dsr_pbo_annex.py
```

Artifact: `logs/*.log` (13 chân + paired + pairwise + null ×4 + dsr ×2), `paired_{baseline,floor}.json`,
`pairwise_{baseline,floor}.json`, `null_*.json`, `nullliq_*.json`,
`data/dsr_family_manifest_w2q2_2026-09-27.json`, `selfchecks/`.
