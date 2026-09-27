# REPORT — W2 / Q2: so 4 phương tiện park khi tiền nhàn rỗi KHÔNG còn 0%/năm

> Job `Taylor_20260927_141318` (attempt 2 — tiếp quản 13 chân attempt 1 đã chạy, không chạy lại).
> Kế hoạch: `kb/projects/custom30v-revalidation-plan-20260927.md` §3-§4. Tiêu chí: `PREREG.md`
> (commit `4041c7bf`, ghi TRƯỚC log đầu tiên).
> **PAPER-ONLY.** Không re-pin, không đổi rail / `trading_rules.json`, không merge.
> **KHÔNG kết luận giữ/bỏ custom30V** — đó là quyết định của user (Q3/W3).

## 0. Kết luận một dòng

> ⚠️ **ĐỌC §11 TRƯỚC KHI DÙNG BẤT KỲ SỐ NÀO Ở §2/§3.** quant-skeptic đã **REFUTED** (2026-09-27
> 15:48Z) phần DIỄN GIẢI của W2, và W2b (job `Taylor_20260927_155645`) đã xác nhận bằng 3 phép đo
> độc lập. Cụ thể: câu *"bị quyết định bởi tầng proxy"* dưới đây **ĐÃ RÚT LẠI** — đảo dấu là
> **nhiễu đường giao dịch của engine**, và khoảng cách giữa các phương tiện ở §2/§3 nằm DƯỚI sàn
> nhiễu đó nên **không đọc được**. Kết luận "không ai đạt tiêu chí PREREG" vẫn đúng, nhưng vì lý do
> khác (không đo được). Xem §11 (rút lại) · §12 (overlay) · §13 (sàn nhiễu) · §14 (cơ chế) ·
> §17 (kết luận sau W2b).


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

---

# W2b — SỬA W2 theo verdict REFUTED của quant-skeptic

> Job `Taylor_20260927_155645`. Verdict gốc: bus `quant-skeptic/verification` topic
> `w2-c30v-q2-final`, 2026-09-27 15:48Z, **REFUTED / confidence high**. PAPER-ONLY, `EXP_TAG`
> non-canonical, không re-pin, không đổi rail, không merge. 13 chân W2 giữ nguyên, không chạy lại.
> **Skeptic bác DIỄN GIẢI, không bác số** — `independent_recompute` của nó khớp cả 12 ledger, và
> tôi không tranh chấp điểm đó.

## 11. RÚT LẠI — đoạn nào của finding `w2-c30v-q2-final` không còn đứng được

Rút lại **nguyên văn** 3 tuyên bố sau. Tất cả đều là DIỄN GIẢI, không phải phép đo:

| # | Tuyên bố cũ (ở đâu) | Trạng thái | Vì sao |
|---|---|---|---|
| **R1** | "**Khoảng 0,55pp carry trung bình là đủ để đảo toàn bộ thứ hạng**" (§3, cuối) | **RÚT LẠI** | 0,55pp carry KHÔNG đảo thứ hạng. Overlay §3(3) (bảng dưới) cho thấy khi chỉ có carry thay đổi mà đường giao dịch KHÔNG đổi, đổi tầng dịch MỌI phương tiện gần như đồng đều (−0,37pp CAGR cho D, −0,31pp cho A) và **không có đảo dấu**. Cái đảo dấu đến từ chỗ khác. |
| **R2** | "thứ hạng **bị quyết định bởi tầng proxy**, không phải bởi phương tiện" (§0) | **RÚT LẠI một nửa** | Nửa phủ định ĐÚNG và còn mạnh hơn: thứ hạng KHÔNG do phương tiện quyết định. Nửa khẳng định SAI: nó cũng không do tầng proxy quyết định — nó do **đường giao dịch rời rạc** của chính engine. Tầng proxy chỉ là thứ tình cờ làm xáo đường đi ở lần đo này. |
| **R3** | "giới hạn nghiêm trọng nhất của W2 là proxy single-source trước 2025-11" (§9.1) → và hàm ý W3 "làm chắc proxy trước" | **RÚT LẠI thứ tự ưu tiên** | Proxy single-source vẫn là một giới hạn thật, nhưng **không phải cái chặn**. Làm proxy chính xác tuyệt đối cũng không giúp gì: sàn nhiễu đường đi của engine (§13) lớn hơn toàn bộ khoảng cách giữa các phương tiện. Siết proxy trước = nhắm sai nguyên nhân. |

**KHÔNG rút lại** (vẫn đứng, skeptic cũng xác nhận): mọi con số ledger và mọi cổng §1; §4 (C có edge
trên CAGR, đuôi DD xấu hơn ngẫu nhiên, 2 pool cho cùng phán quyết); §5 (park 0,0 không rò tiền);
§6 (R2/R5 là nợ cũ, không phải regression W2); §9 các mục 2-7; và kết luận **"không ứng viên nào đạt
tiêu chí PREREG"** — kết luận đó vẫn đúng, chỉ là **vì lý do khác** (không đo được, thay vì đo được
rồi thấy không robust).

Một lệch **so với chữ PREREG** phải khai ở đây: PREREG §3(3) hứa overlay như "phép đối chiếu bậc 1
trong REPORT"; attempt 2 đã bỏ sót nó. Skeptic bắt đúng
(`reproducibility_selfcheck: "Undisclosed deviation: PREREG §3(3) overlay cross-check missing"`).
Mục §12 dưới đây trả món nợ đó.

## 12. Overlay PREREG §3(3) — carry ÁP LÊN đường carry-0%, đường giao dịch KHÔNG đổi

Đây là phép đo tách được **hiệu ứng carry trực tiếp** khỏi **hiệu ứng đổi đường giao dịch**, vì nó
áp carry bằng số học lên chuỗi NAV của chân carry-0% thật, không cho nó chạy lại engine.

- Đường nền: `w2d_off` (= D, park 0,0, carry 0%) và `w2ctrl2` (= A, park 0,3, carry 0% — **chính là
  chân control ledger md5 `4707bcbe`**). Cả hai là chân THẬT đã pin, không dựng lại.
- Công thức mỗi phiên: `nav_ov(d) = nav_ov(d−1)·(1+r_eng(d)) + max(idle_cash(d−1),0)·rate(d)/252·(nav_ov/nav_eng)(d−1)`
  với `idle_cash = bal_cash_ref + lag_cash_ref` từ **DAILY rows** (đúng đại lượng `simulate()` trả
  lãi: chỉ `cash>0`, tiền đã park nằm ở `bal_etf_ref`/`lag_etf_ref`), `rate` = `idle_rate_proxy.r_idle`
  PIT theo tầng, `/252` đúng quy ước engine, 0 trước khi chuỗi bắt đầu (tầng 2: 18 phiên).
- Tiền nhàn rỗi trung bình: **D 57,6% NAV · A 46,4% NAV** — đây là đòn mà overlay tác động qua, và
  là lý do D được lợi nhiều hơn A.
- Script `w2b_overlay.py`, output `w2b_overlay.json`, paired bootstrap DÙNG CHUNG `paired_w2.py`
  (L=21, B=4000, seed=12345) trên cả 6 đường ⇒ cùng một "thế giới resample" như W2.

| Đường | CAGR | Sharpe | MaxDD | Calmar | **E[Calmar]** | DD5th | ΔCAGR vs carry-0% |
|---|---|---|---|---|---|---|---|
| D carry 0% (`w2d_off`) | 22,12% | 1,87 | −16,2% | 1,363 | 1,488 | −23,9% | — |
| A carry 0% (`w2ctrl2`) | 23,37% | 1,81 | −14,6% | 1,596 | 1,474 | −25,2% | — |
| **D + overlay tầng 1** | 25,08% | 2,10 | −15,5% | 1,621 | **1,779** | −22,5% | **+2,96pp** |
| **A + overlay tầng 1** | 25,77% | 1,98 | −13,9% | 1,850 | 1,705 | −23,8% | **+2,40pp** |
| **D + overlay tầng 2** | 24,71% | 2,07 | −15,5% | 1,592 | **1,744** | −22,6% | **+2,59pp** |
| **A + overlay tầng 2** | 25,46% | 1,96 | −14,0% | 1,821 | 1,677 | −24,0% | **+2,09pp** |

`P(A > D)` trên Calmar bootstrap: carry 0% **0,515** · overlay tầng 1 **0,422** · overlay tầng 2
**0,430**.

**Ba điều đọc ra, và một chỗ tôi khác skeptic:**

1. **KHÔNG CÓ ĐẢO DẤU giữa hai tầng.** Trên tiêu chí CHÍNH của PREREG (E[Calmar]) overlay cho
   **D > A ở CẢ hai tầng** (1,779 vs 1,705 và 1,744 vs 1,677), `P(A>D)` = 0,422 / 0,430 — cùng
   phía, cùng độ lớn. Trên CAGR thì **A > D ở cả hai tầng** (25,77 vs 25,08; 25,46 vs 24,71).
   Hai tiêu chí trả lời khác nhau, nhưng **mỗi tiêu chí trả lời NHẤT QUÁN qua hai tầng.** Đó là
   điều bảng engine-rerun §2 không có.
2. **Đổi tầng dịch mọi thứ cùng chiều, cỡ ~0,3pp.** D −0,37pp CAGR, A −0,31pp; E[Calmar] D −0,035,
   A −0,028. So với engine-rerun: D **−2,01pp** CAGR (26,23→24,22) và A **+0,38pp** (25,84→26,22).
   Tức hiệu ứng trực tiếp của tầng nhỏ hơn cái W2 đo được **5,4 lần** ở chân D, và **ngược dấu** ở
   chân A. Phần chênh lệch ấy không phải carry — nó là đường đi.
3. **Skeptic nói "mọi phương tiện dịch ĐỒNG ĐỀU ~0,3pp/book"; chính xác hơn là KHÔNG hoàn toàn đồng
   đều** — D được +2,96pp còn A +2,40pp khi bật carry tầng 1, lệch **0,56pp**, đúng bằng tỉ lệ tiền
   nhàn rỗi (57,6% vs 46,4%). Đây là một hiệu ứng THẬT và nó đi **đúng chiều có lợi cho D**: cho tiền
   nhàn rỗi ăn lãi thì không-park được lợi nhiều hơn park, hiển nhiên. Nhưng 0,56pp vẫn nhỏ hơn sàn
   nhiễu 1,57pp (§13) ⇒ **vẫn không đọc được**. Điều chỉnh này không cứu kết luận cũ, nó chỉ làm
   phép mô tả đúng hơn.

**Giới hạn của chính overlay (PREREG §3 đã khai TRƯỚC, không phải biện hộ sau):** overlay KHÔNG
truyền carry vào sizing, nên nó **hạ thấp chân D một cách có hệ thống** (ở D tiền nhàn rỗi là 57,6%
NAV; carry của nó làm NAV to hơn ⇒ lệnh sau to hơn — overlay không có cơ chế đó). Vì vậy overlay là
**phép đối chiếu bậc 1**, không phải nguồn số kết luận. Nó đủ để trả lời đúng một câu — "carry tự nó
có đảo thứ hạng không?" — và câu trả lời là **KHÔNG**.

## 13. SÀN NHIỄU ĐƯỜNG ĐI — 8 chân engine, carry FLAT, không proxy

Câu hỏi: nếu giữ nguyên MỌI thứ và chỉ nhích mức lãi tiền nhàn rỗi, engine trả lời khác bao nhiêu?
8 chân thật: {D = park 0,0 · A = custom30V park 0,3} × `IDLE_CARRY_FLAT` ∈ {3,0 · 3,5 · 4,0 · 4,5}%/năm.

**Vì sao FLAT, không phải proxy:** hằng số không có cấu trúc theo tháng, nên mọi chuyển động của
metric qua 4 mức **không thể** là tính chất của chuỗi lãi — nó chỉ có thể là engine đi đường giao
dịch khác vì mức tiền đổi. Bằng cấu tạo, chân flat cũng không thể có look-ahead.

Cùng lệnh pin, cùng `BQ_LOCAL_CACHE`/`BASKET_CA_SNAPSHOT`, cùng paired bootstrap (L=21, B=4000,
seed=12345, MỘT chuỗi block-index cho cả 8 chân). Script `w2b_noise.py` → `w2b_noise.json`.

| chân | CAGR | Sharpe | MaxDD | Calmar | E[Calmar] | DD5th |
|---|---|---|---|---|---|---|
| D @3,0% | 24,38% | 2,05 | −14,4% | 1,690 | 1,735 | −22,1% |
| D @3,5% | 24,29% | 2,04 | −14,1% | 1,722 | 1,723 | −22,1% |
| D @4,0% | 25,86% | 2,14 | −13,9% | 1,855 | **1,901** | −21,3% |
| D @4,5% | 25,79% | 2,17 | −13,7% | 1,880 | **1,947** | −20,7% |
| A @3,0% | 25,68% | 2,00 | −14,1% | 1,826 | 1,716 | −23,4% |
| A @3,5% | 26,14% | 2,03 | −14,0% | 1,863 | 1,763 | −23,2% |
| A @4,0% | 26,02% | 2,02 | −14,0% | 1,856 | 1,754 | −23,1% |
| A @4,5% | 26,04% | 2,02 | −14,0% | 1,866 | 1,756 | −23,1% |

### 13.1 Sàn nhiễu, hai thước đo

`step_0,5pp` = bước LỚN NHẤT giữa hai mức lãi KỀ NHAU (0,5pp). Đây là thước **so sánh trực tiếp
được**, vì khoảng cách tầng 1 ↔ tầng 2 mà kết luận W2 dựa vào là **0,55pp** lãi trung bình.

| phương tiện | metric | 4 giá trị | range (1,5pp) | **step (0,5pp)** | đơn điệu theo lãi? |
|---|---|---|---|---|---|
| **D** | CAGR | 24,38 / 24,29 / 25,86 / 25,79 | 1,574pp | **1,574pp** | **KHÔNG** |
| **D** | E[Calmar] | 1,735 / 1,723 / 1,901 / 1,947 | 0,225 | **0,178** | **KHÔNG** |
| **D** | MaxDD | −14,43 / −14,11 / −13,94 / −13,72 | 0,71pp | 0,32pp | có |
| **A** | CAGR | 25,68 / 26,14 / 26,02 / 26,04 | 0,459pp | **0,459pp** | **KHÔNG** |
| **A** | E[Calmar] | 1,716 / 1,763 / 1,754 / 1,756 | 0,047 | **0,047** | **KHÔNG** |
| **A** | MaxDD | −14,06 / −14,03 / −14,01 / −13,96 | 0,10pp | 0,05pp | có |

**Nhích lãi tiền nhàn rỗi 0,5pp — từ 3,5% lên 4,0% — làm CAGR của chân D nhảy 1,57pp và E[Calmar]
nhảy 0,178.** Không đơn điệu (3,0→3,5 còn GIẢM 0,09pp rồi 3,5→4,0 tăng 1,57pp). Đó không phải hàm
phản ứng của một tham số, đó là nhiễu.

### 13.2 Khoảng cách phương tiện nằm TRONG sàn nhiễu — bảng phán quyết

| mức lãi flat | ΔCAGR (A−D) | ΔE[Calmar] (A−D) | ΔMaxDD | `P(A>D)` Calmar |
|---|---|---|---|---|
| 3,0% | **+1,31pp** | −0,018 | +0,37pp | 0,501 |
| 3,5% | **+1,86pp** | **+0,041** | +0,08pp | 0,588 |
| 4,0% | +0,16pp | **−0,147** | −0,07pp | 0,287 |
| 4,5% | +0,25pp | **−0,191** | −0,24pp | 0,258 |

Cùng một cặp phương tiện, cùng một cửa sổ, chỉ đổi một hằng số vô hại: `ΔE[Calmar]` **đổi dấu**
(−0,018 → +0,041 → −0,147 → −0,191) và `P(A>D)` chạy từ **0,258 đến 0,588**. So sánh trực tiếp với
W2: `P(A>D)` = 0,192 (tầng 1) → 0,610 (tầng 2). **Toàn bộ "đảo dấu" của W2 nằm gọn trong dải mà một
hằng số lãi vô nghĩa cũng tạo ra được.** Skeptic đúng: đó là nhiễu đường đi, không phải tính chất
phương tiện.

### 13.3 Kích cỡ hiệu ứng TỐI THIỂU đọc được (MDE) trên engine này

`sd` = độ lệch chuẩn qua 4 mức lãi (n=4, `w2b_mde.json`). MDE ở n=4/phương tiện ≈ `2,8·sd·√(2/4)`:

| phương tiện | metric | sd | **MDE @n=4** | số chân/phương tiện để phân giải hiệu ứng = nửa dải nhiễu |
|---|---|---|---|---|
| **D** (park 0,0) | CAGR | 0,863pp | **1,71pp** | ~19 |
| **D** | E[Calmar] | 0,115 | **0,227** | ~16 |
| **A** (park 0,3) | CAGR | 0,199pp | **0,39pp** | ~12 |
| **A** | E[Calmar] | 0,021 | **0,042** | ~13 |

**Sàn nhiễu là tính chất của CHÂN, không của engine nói chung** — và đây là phát hiện khó chịu nhất:
chân D (57,6% NAV là tiền mặt) nhiễu **hơn 4 lần** chân A (46,4%). Càng nhiều tiền nhàn rỗi, càng
nhiều "nhiên liệu" cho engine chọn đường khác. Nghĩa là **trục park-vs-không-park chính là trục
engine này đo TỆ NHẤT** — đúng cái trục W2 được hỏi. Khoảng cách E[Calmar] giữa các phương tiện mà
W2 báo (0,05–0,25) nhỏ hơn MDE của chân D (0,227) ⇒ **không một so sánh nào trong §2/§3 của W2 đọc
được.**

## 14. VÌ SAO nhiễu tiền mặt lại đổi TẬP LỆNH — truy vết tới rail của engine

Skeptic đề nghị bắt đầu ở phiên phân kỳ đầu 2018-05-09 (D) / 2015-12-03 (A). Đo lại thì **hai mốc
đó không phải phân kỳ đầu**: phân kỳ TX đầu tiên là **2014-02-06 cho CẢ HAI phương tiện**, và phân
kỳ tiền mặt là **2014-01-02** — ngay phiên đầu cửa sổ, đúng như phải thế (lãi vào cash từ phiên 1).
Tôi báo mốc đo được, không chép lại mốc trong prompt.

### 14.1 Hai loại phân kỳ, phải tách ra mới hiểu được

| | phân kỳ đầu | bản chất |
|---|---|---|
| **liên tục** (cùng tên, cùng hành động, khác SỐ LƯỢNG) | **2014-02-06** — `LAG\|DNC\|buy` 2.601.115,09 vs 2.590.993,78 cp (−0,39%); `LAG\|VBC\|buy` −0,39% | vô hại, đúng như mong đợi: tiền nhiều hơn 0,4% ⇒ mua nhiều hơn 0,4% |
| **rời rạc** (tập TÊN khác nhau) | **2014-08-11** — `LAG\|VIP\|buy ENTRY_FILL` 81,58M **CÓ ở tầng 1, KHÔNG có ở tầng 2**; 16 TX vs 15 TX | đây mới là chỗ sinh ra swing 13–28pp |

**`shares` là số THỰC, không phải số lô** (`2601115,088400856` — kiểm chứng trong `w2b_trace2.py`,
`shares_are_fractional: True`). **Không có lượng hoá theo lô nào trong engine này.** Vậy không phải
"round/lô" gây chuyện — sizing liên tục hoàn hảo theo tiền. Chuyện xảy ra khi một chênh lệch LIÊN TỤC
cán qua một **ngưỡng RỜI RẠC**.

### 14.2 Ba rail rời rạc, đọc thẳng từ `simulate_holistic_nav.py`

| rail | vị trí | cơ chế | cash có vào không? |
|---|---|---|---|
| **R-a min-ticket 100.000 VND** | `simulate_holistic_nav.py:1240` `if buy_value >= 100_000` với `buy_value = min(remaining_value, daily_max, _bp)` và `_bp = cash + …` (1226-1229) | ngưỡng CỨNG. Chênh lệch tiền đủ đẩy một chân lên trên và chân kia xuống dưới 100k | **trực tiếp** (`cash` là một trong 3 hạng của `min`) |
| **R-b hoàn tất/bỏ lệnh** | `:1263` `done = fill_pct >= 0.95 or days_filling >= max_fill_days(5)`; `:1264` `elif filled_shares > 0 and fill_pct >= min_fill_pct(0.30)` → nếu không thì **`ABANDONED_REFUND`** (`:1297,1317`) | HAI ngưỡng cứng (0,95 và 0,30) trên một TỈ SỐ mà mẫu số là `target_value = cur_nav / max_positions` (`:1145`) và tử số bị chặn bởi tiền + trần ADV | **trực tiếp** (qua cả `cash` và `cur_nav`) |
| **R-c đếm slot** | `:1082` `if is_first_fill and not _slot_exempt and _n_slots >= max_positions`; `:1264` cổng nạp `len(positions)+len(pending) < max_positions*3` | occupancy là SỐ NGUYÊN. Một khi R-a/R-b nhét tên khác vào một slot, **mọi tín hiệu SAU đó** được nạp/bị chặn khác đi | gián tiếp — đây là bộ **KHUẾCH ĐẠI**, không phải nguồn |

Trần ADV (`daily_max = liq × 0,20`) là liên tục, **không** phải rail.

### 14.3 Rail nào thật sự cắn — đếm trên ledger (`w2b_trace3.json`)

D tầng 1 vs tầng 2 (chỉ khác đúng chuỗi lãi):

| đại lượng | giá trị |
|---|---|
| TX rows | 7.663 vs 7.534 |
| TX chỉ có ở một chân | **407 / 278** (reason: `ENTRY_FILL` 292/182 · `TIME` 56/66 · `ABANDONED_REFUND` 52/17 · `STOP` 7/13) |
| `ABANDONED_REFUND` **tổng** mỗi chân | **995 / 960** trên ~5.600 lệnh mua ⇒ **~17% lệnh vào bị BỎ** |
| `holding_id` dùng chung | **546** · chỉ có ở chân 1: **1.437** · chỉ chân 2: **1.418** ⇒ **chỉ 16% vị thế là chung** |
| phiên có SỐ LƯỢNG lệnh mua khác nhau | 184 / 1.127 |
| lệnh mua nằm trong `[100k, 200k)` (vùng R-a cắn) | 82 / 79 trên 5.681 ⇒ **1,4%** |
| lệnh mua NHỎ NHẤT | 104.500 VND (cả 2 chân) — **sát rail 100k** |

Đối chứng quyết định — **D @3,5% vs D @4,0%**, chỉ khác một hằng số 0,5pp:

| | tầng1 vs tầng2 | flat 3,5% vs 4,0% |
|---|---|---|
| TX chỉ một chân | 407 / 278 | 267 / 331 |
| `holding_id` chung | 546 | 1.006 |
| phiên khác số lệnh mua | 184 | 134 |

**Cùng một cỡ độ phân kỳ.** Đổi tầng proxy không đặc biệt gì cả — nó chỉ là một cách nhích tiền.

### 14.4 Phân loại theo yêu cầu: (i) threshold artefact vá được, hay (ii) cố hữu?

**Trả lời: chủ yếu (ii), phần (i) có thật nhưng nhỏ VÀ không vá được mà không đổi hành vi anchor.**

- **R-a (min-ticket 100k) = (i) threshold artefact.** 100.000 VND là hằng số tuyệt đối trên sổ 50
  **tỷ** (= 2 phần triệu NAV) và vô nghĩa khi `shares` là số thực. *Patch đề xuất (KHÔNG merge):* bỏ
  hẳn ngưỡng, hoặc đổi thành tỉ lệ NAV. **Nhưng nó KHÔNG phải patch trung tính**: 82/5.681 lệnh nằm
  trong vùng nó cắn và lệnh nhỏ nhất là 104.500 VND ⇒ vá là **đổi fill của anchor**, tức phải
  re-pin. Và vì chỉ 1,4% lệnh dính, vá xong **sàn nhiễu gần như không giảm**. Chi phí cao, lợi ích
  thấp — **đề xuất KHÔNG vá**.
- **R-b + R-c = (ii) tính chất cố hữu của mô phỏng rời rạc.** Chuỗi nhân quả: tiền lệch → `cur_nav`
  lệch → `target_value = cur_nav/max_positions` lệch → `fill_pct` lệch → cán ngưỡng 0,30/0,95 →
  **vị thế khác hẳn** (thành position vs `ABANDONED_REFUND`) → occupancy slot số nguyên khác →
  **tín hiệu kế tiếp được nạp khác** → tiền khác nhiều hơn → lặp lại. Đây là **bản đồ hỗn loạn có
  hồi tiếp dương**, không phải một bug ở một dòng. Với 17% lệnh vào đi qua nhánh bỏ-lệnh, engine có
  hàng nghìn cơ hội rẽ nhánh mỗi lượt chạy. Bằng chứng khoá chặt nhất: cùng một vị thế
  `LAG|DIC` 16.784,502927628666 cp **thoát bằng `ABANDONED_REFUND` ngày 2015-08-14 ở chân tầng 1**,
  nhưng ở chân tầng 2 nó được giữ thêm **một tháng** rồi thoát bằng `TIME` ngày **2015-09-16**. Không
  ngưỡng nào bị "vá sai" ở đây — hai chân chỉ đơn giản ở hai phía của cùng một biên quyết định.
- **Không thể vá được theo nghĩa nào?** Bỏ ngưỡng 0,30 thì mọi lệnh khớp dở đều thành vị thế (đổi
  chiến lược, không phải sửa lỗi). Bỏ đếm slot thì bỏ luôn trần tập trung. Cả hai đều là **luật
  chiến lược**, không phải chi tiết cài đặt. **Không có patch nào giữ nguyên hành vi anchor mà hạ
  được sàn nhiễu.**

**Hệ quả cho MỌI A/B ±0,3pp đã làm trong quá khứ trên engine này** (đây là câu hỏi quan trọng nhất
của W2b, trả lời thẳng): với chân có nhiều tiền nhàn rỗi, **±0,3pp CAGR hoặc ±0,05 E[Calmar] KHÔNG
đọc được** — sàn nhiễu ở chân D là 1,57pp / 0,178. Với chân đã park gần hết tiền (A) sàn thấp hơn
nhiều (0,46pp / 0,047) nhưng vẫn lớn hơn 0,3pp. **Bất kỳ kết luận cũ nào dựa trên một lần chạy
duy nhất mỗi cấu hình và khoảng cách dưới ~0,5pp CAGR đều phải coi là CHƯA KẾT LUẬN**, không phải
sai — chỉ là không có sức phân giải. Việc rà soát lại các A/B cũ theo tiêu chí này chưa làm, và
**không** thuộc phạm vi W2b.

## 15. META `cash_identity` + selfcheck R2/R5 (recommended_reruns #4, #5)

**META `cash_identity` — ĐÃ SỬA trong worktree** (`pt_v23_audit_2014.py`, branch
`research/c30v-w2-idlecarry-2709`). Trước đó mọi chân carry vẫn ghi *"No other cash flows exist
(deposit interest = 0, no margin)"* — sai theo nghĩa nặng nhất: ai đó dựng lại cash **chỉ từ TX** sẽ
thấy không khớp và không biết vì sao. Text mới, chỉ ở chân có carry, nói rõ có khoản lãi mutate cash
KHÔNG có dòng TX, kèm chính chỗ engine tự cộng nó lại (`_resid = dcash − f_full − interest`) và mức
lãi thật của chân (FLAT %/năm hay tier proxy). Chân `off` giữ nguyên nguyên văn cũ ⇒ **anchor không
đổi** (xác nhận bằng md5 ở §16).

**Selfcheck R2/R5 — KHÔNG có baseline nào để refresh, đây là chẩn đoán khác với giả định của dispatch.**
Baseline không phải file số mà là **một module dựng từ git ref**
(`basket_return_leg_oshares_selfcheck.py:82-83` `git show {BASKET_RETLEG_PREREF}:./custom_basket.py`).
Module tiền-sửa đó **không có knob `BASKET_OSHARES_STEP`** (knob sinh ra cùng bản vá exdate,
`custom_basket.py:148,216`) ⇒ nó CHỈ biết bước OShares theo QUÝ ⇒ *"regen baseline sang exdate"* là
việc **không thể thực hiện**, không phải việc chưa làm. Bằng chứng cơ học, 3 log cùng TZ/interpreter/
WORKDIR khác nhau đúng một biến env (`research/postmerge_haukiem_20260927/selfchecks/`):
`…PREREF2c_STEPQUARTER…` **PASS toàn bộ**, R5 `max|Δlevel| = 0.000000e+00`; `…PREREF2c_EXDATE…` và
`…PREREF…` **FAIL 2**, cùng cặp md5, cùng `9.223644e+01`. Nguyên nhân: R2/R5 được viết để chứng minh
knob `BASKET_RETURN_OSHARES` không đổi đường weight, nhưng sau khi exdate thành mặc định thì phép so
ấy **gộp hai thay đổi độc lập vào một assertion** và fail vì thay đổi thứ hai.
**Đề xuất (KHÔNG merge, không chạm `custom_basket.py`)**: pin `BASKET_OSHARES_STEP=quarter` trong
`run()` của selfcheck cho cả 3 chân R2/R5, **kèm cùng lượt** một R6 kiểu positive-control khẳng định
`exdate` PHẢI đổi weight — nếu chỉ làm nửa đầu thì đường exdate mất hẳn lớp phủ. Patch + rủi ro:
`w2b_retleg_R2R5.proposed.md`.

## 16. Cổng bắt buộc của W2b + tái lập

| Cổng | Kết quả |
|---|---|
| **Control leg tái lập anchor SAU khi vá code W2b** | xem §16.1 — **PASS ở `w2bn_ctrl3` và `w2bn_ctrl5`**, và một **FAIL THẬT bị bắt ở `w2bn_ctrl4`** |
| **Self-check 0 VND** | **PASS 11/11 chân W2b mới** (8 flat + 3 control/meta): BAL + LAG cash-flow identity, final-NAV identity, borrow-audit — kể cả chân FLAT carry |
| **Mutual-exclusion knob** | `IDLE_CARRY_FLAT` + `IDLE_CARRY_TIER` cùng lúc ⇒ `ValueError`, không có chân nào được có hai nguồn carry |
| **Filename tag (§8)** | `_idleflat300/350/400/450` — trục mới đổi số ⇒ đổi tên file, không chân nào ghi vào tên canonical |
| **Look-ahead trên chân flat** | không thể có, **theo cấu tạo**: hằng số không mang thông tin thời gian |

### 16.1 Cổng control đã BẮT một lỗi thật của chính W2b — ghi lại vì nó là bài học, không phải thủ tục

Bản vá META `cash_identity` **lần 1** viết lại câu cho chân `off` theo thứ tự clause khác (nội dung y
nguyên về nghĩa). Chân `w2bn_ctrl4` cho md5 **`55e9f15f`** ≠ anchor `4707bcbe`. `diff` ra **đúng 1
dòng**: dòng META đó, chỉ khác THỨ TỰ CLAUSE.

Đã sửa: chân `off` phát ra chuỗi **NGUYÊN VĂN BYTE-FOR-BYTE** như cũ, nhánh carry mới có chuỗi khác.
`w2bn_ctrl5` (sau khi sửa) → md5 **`4707bcbe…`** ✓.

Bài học đáng ghi: **ledger được băm toàn file, nên một dòng tài liệu cũng là một phần của anchor.**
"Chỉ sửa comment/text, không đổi số" **không** đủ để khỏi cần chạy lại cổng control. Nếu W2b bỏ qua
cổng này vì "chỉ đổi chữ", nó sẽ âm thầm làm mọi so sánh với anchor sau này lệch nền.

### 16.2 Tái lập W2b

```bash
WT=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-w2q2-2709/WorkingClaude   # branch research/c30v-w2-idlecarry-2709
R=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/c30v_w2_q2_20260927
# 8 chan san nhieu (FLAT carry, khong proxy):
for r in 0.030 0.035 0.040 0.045; do
  $R/run_leg.sh w2bn_d$(python3 -c "print(int($r*10000))") BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.0 IDLE_CARRY_FLAT=$r
  $R/run_leg.sh w2bn_a$(python3 -c "print(int($r*10000))") BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_FLAT=$r
done
$R/run_leg.sh w2bn_ctrl5 BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=off   # cong control -> md5 4707bcbe
$DNA_PYEXE $R/w2b_overlay.py   # §12 overlay PREREG §3(3)   -> w2b_overlay.json
$DNA_PYEXE $R/w2b_noise.py     # §13 san nhieu duong di     -> w2b_noise.json
$DNA_PYEXE $R/w2b_trace.py     # §14.1 phan ky lien tuc     -> w2b_trace.json
$DNA_PYEXE $R/w2b_trace2.py    # §14.1 phan ky ROI RAC      -> w2b_trace2.json
$DNA_PYEXE $R/w2b_trace3.py    # §14.3 dem theo rail        -> w2b_trace3.json
```

Artifact W2b: `w2b_overlay.py|json` · `w2b_noise.py|json` · `w2b_trace{,2,3}.py|json` ·
`w2b_mde.json` · `w2b_retleg_R2R5.proposed.md` · `logs/w2bn_*.log` (11 chân) ·
`logs/w2b_{overlay,noise,trace,trace2,trace3,mde}.log`.

## 17. KẾT LUẬN SAU W2b

### 17.1 Có xếp hạng được phương tiện không? **KHÔNG.**

Không phải "chưa đủ bằng chứng để chọn A hay C6" — là **engine không có sức phân giải để trả lời câu
hỏi này ở kích cỡ hiệu ứng đang tồn tại.** Ba phép đo độc lập cùng chỉ một chỗ:

1. **Overlay (§12)**: khi chỉ có carry đổi mà đường giao dịch KHÔNG đổi, **không có đảo dấu nào** —
   E[Calmar] cho D > A ở cả hai tầng, CAGR cho A > D ở cả hai tầng, mỗi tiêu chí nhất quán.
2. **Sàn nhiễu (§13)**: nhích một hằng số lãi vô nghĩa 0,5pp làm `P(A>D)` chạy từ **0,258 đến 0,588**
   và CAGR chân D nhảy **1,57pp**. Dải "đảo dấu" của W2 (`P(A>D)` 0,192 → 0,610) nằm gọn trong đó.
3. **Truy vết (§14)**: cơ chế đã xác định, đọc thẳng từ code — ngưỡng `fill_pct` 0,30/0,95 +
   `ABANDONED_REFUND` (17% lệnh vào) + đếm slot số nguyên, có hồi tiếp dương. Chỉ **16% vị thế** là
   chung giữa hai chân chỉ khác nhau chuỗi lãi.

Vì vậy §2/§3 của W2 **không đọc được**, và §11 rút lại 3 tuyên bố diễn giải. Kết luận "không ứng viên
nào đạt tiêu chí PREREG" **vẫn đúng** nhưng lý do đổi hẳn: **không đo được**, không phải "đo được rồi
thấy không robust".

### 17.2 Cần chính xác những gì để trả lời được Q2

**(a) Kích cỡ hiệu ứng TỐI THIỂU đọc được, ở thiết kế một-chân-một-cấu-hình như W2** (§13.3):

| chân | CAGR | E[Calmar] | MaxDD |
|---|---|---|---|
| có nhiều tiền nhàn rỗi (D, park 0,0 — 57,6% NAV là cash) | **≥ 1,7pp** | **≥ 0,23** | ≥ 0,6pp |
| đã park (A, park 0,3 — 46,4%) | ≥ 0,4pp | ≥ 0,04 | ≥ 0,08pp |

So sánh park-vs-không-park luôn có chân D trong đó ⇒ **ngưỡng ràng buộc là dòng trên: 1,7pp CAGR /
0,23 E[Calmar]**. Khoảng cách phương tiện thật đo được là 0,05–0,25 E[Calmar] ⇒ nhỏ hơn 1 bậc.
**Không hy vọng đọc được bằng cách đo cẩn thận hơn cùng một cách.**

**(b) Hai đường ra, cả hai đều tốn kém — và đây là chỗ cần user/Mike quyết, W2b không tự quyết:**

| đường | việc phải làm | chi phí | rủi ro |
|---|---|---|---|
| **ENSEMBLE** (khuyến nghị) | mỗi phương tiện chạy **~16-19 chân** với nhiễu tiền mặt độc lập (mức lãi flat rải rác / seed), so **TRUNG BÌNH** phương tiện chứ không so một chân. §13.3 tính từ `sd` thật. | 16-19 chân × 5 phương tiện × 2 tầng ≈ **160-190 chân engine**, mỗi chân ~7-10 phút | 4 mức của W2b chưa chắc độc lập (D có dấu hiệu 2 cụm: 3,0/3,5 vs 4,0/4,5) ⇒ `sd` n=4 có thể **ước thấp**, số chân thật có thể cao hơn |
| **SỬA ENGINE** | không phải vá ngưỡng — phải đổi bản chất: thực thi liên tục thay vì lệnh rời rạc, hoặc trung bình hoá nội bộ nhiều đường thực thi | Bản viết lại `simulate()` | **Đổi engine = đổi cả anchor và toàn bộ lịch sử pin.** Và R-b/R-c là **luật chiến lược** (trần tập trung, bỏ lệnh khớp dở), không phải chi tiết cài đặt ⇒ sửa chúng là đổi chiến lược, không phải sửa đo lường |

**(c) Không nên làm:** siết proxy lãi tiền nhàn rỗi để "chắc số hơn" (đó là ưu tiên W3 cũ, §11-R3
rút lại). Proxy chính xác tuyệt đối cũng không hạ được sàn nhiễu một chút nào.

### 17.3 Ranh giới — W2b KHÔNG kết luận gì về custom30V

**Không kết luận giữ/bỏ custom30V.** W2b không cung cấp thêm bằng chứng nào cho quyết định đó theo
CHIỀU NÀO — nó chỉ chứng minh rằng **bằng chứng ủng hộ VÀ bằng chứng phản đối trong W2 đều dưới sàn
nhiễu**. Cụ thể, W2b **không** nói custom30V tốt, **không** nói custom30V tệ, và **không** nói
"không park" tốt hơn. Ai đọc §13.2 rồi kết luận "D thắng ở lãi cao" là đang đọc chính cái nhiễu vừa
được đo. Quyết định vẫn là của user (Q3/W3) và phải dựa trên căn cứ khác — ví dụ lý do vận hành /
thanh khoản / tập trung — chứ không phải trên xếp hạng E[Calmar] của W2.

**Một điểm vẫn đứng và có thể dùng** (không bị nhiễu phá vì nó không so hai chân engine): dưới quy
ước cũ **lãi tiền nhàn rỗi = 0%/năm**, parking "mua" được +1,25pp CAGR mà phần lớn chỉ là hệ quả của
việc engine trả 0% cho tiền không park (§2, chân tham chiếu). Overlay §12 định lượng phần đó: cho
tiền nhàn rỗi ăn lãi thật ở tầng 1 thì chân KHÔNG park được **+2,96pp** còn chân park chỉ **+2,40pp**
— tức **lợi thế biểu kiến của parking co lại ~0,56pp** chỉ vì bỏ giả định 0%. Con số đó là **hiệu ứng
số học trực tiếp**, không đi qua đường giao dịch, nên nó đọc được. Nó không xếp hạng phương tiện,
nhưng nó nói rõ: **mọi kết quả backtest parking đã pin dưới quy ước 0%/năm đều thiên vị có lợi cho
parking**, và cỡ thiên vị là bậc nửa điểm phần trăm CAGR.
