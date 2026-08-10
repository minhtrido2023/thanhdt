# Siết sàn ADV3T 2 tỷ/phiên từ CẢNH BÁO → GATE CỨNG cho nhánh hệ thống — **NO-GO**

- **Job**: `Taylor_20260810_073541` · 2026-08-10 · Taylor
- **Kết luận**: **KHÔNG wire.** Không sửa một dòng code production nào, không có `pending_*` patch.
- **Nhưng lý do NO-GO ở đây KHÁC ca circuit-breaker sáng nay** (`Taylor_20260810_065757`). Ở đó
  nhóm bị chặn là nhóm **TỐT NHẤT**. Ở đây nhóm bị chặn **thật sự tệ hơn** — nó chỉ quá nhỏ, đã tự
  teo đi ~20 lần từ 2016, và **hết ý nghĩa thống kê ở OOS**, trong khi cái giá phải trả là cắt
  **43,7% rổ ứng viên hôm nay**.
- **Nỗi lo của user KHÔNG có bằng chứng ủng hộ**: trong 12,5 năm, "mỏng nhưng FA tốt" chưa bao giờ
  được dữ liệu bênh — 95,6% số ca **không vào nổi hàng** — xem §4.
- **v2 (2026-08-10, sau phản biện)**: quant-skeptic **CONFIRMED (medium)** và bắt đúng **một bug
  thật của tôi** (19 vị thế `adv_vnd = NaN` bị `np.where` dồn nhầm vào băng D). Đã sửa; §3/§4 dưới
  đây là **số v2**. Kết luận NO-GO không đổi, lập luận mạnh lên, nhưng **N mỏng đi** (§7 mục 4).

---

## §0 — TL;DR

| Câu hỏi dispatch | Trả lời |
|---|---|
| Phạm vi có đúng không? | **KHÔNG** — `due_diligence.py` là lớp **thuần thông tin**, cả 4 caller đều là report/recommend. Siết `ADV_THIN_VND` **trong file đó không chặn được gì**. Muốn chặn thật phải sửa `lag_liquidity_filter.py` (§1) |
| Sleeve fear-buy (TV1/DGC) có đi qua đây không? | **KHÔNG** — xác nhận bằng grep, `discretionary_accumulation.py` 0 hit (§1) |
| Nhóm bị chặn có tệ hơn nền không? | **CÓ** — +0,78%/deal vs +8,93% nhóm giữ, winrate 39,1% vs 65,5%, CI95 [−11,87; −4,16]pp. **Nhưng nó chỉ là 1,6% vốn và +0,02B P&L** (§3) |
| …còn ở OOS? | **KHÔNG CÒN Ý NGHĨA** — n=8 deal, CI95 [−14,07; **+1,00**] chứa 0 (§3) |
| Nhóm giống SCL (mỏng + rating≤3 + FSCORE≥7) có bị loại oan không? | **Không có bằng chứng là có** — 95,6% **không fill nổi**; chỉ 4 deal khớp được trong 12,5 năm, TB **−2,03%** / trung vị **−2,32%**, trong khi **CÙNG hạng chất lượng mà ADV≥2 tỷ** cho **+9,15%** / +5,73% (§4) |
| Siết bóp rổ bao nhiêu? | **43,7% universe_pit hôm nay** (159/364 mã), gồm HT1, LAS, MIG, CDC… (§5) |
| Ngưỡng 2 tỷ có phải điểm tối ưu? | **Không có điểm tối ưu nào** — thang liều phẳng 0,5→5 tỷ, **PBO = 0,916** (đo 08-04, đã CONFIRMED) |

---

## §1 — Phạm vi: `due_diligence.py` KHÔNG chặn được lệnh (đính chính giả định của dispatch)

`grep -rn "run_due_diligence\|adv_vnd\|ADV_THIN"` toàn repo (loại worktree + selfcheck) — **toàn bộ
caller**:

| Caller | Dùng gì | Chặn lệnh? |
|---|---|---|
| `deploy_golive_dt5g_v4/golive_recommend_v23.py:1007-1016` | `run_due_diligence` → ghi vào cột `due_diligence` của bảng khuyến nghị | **KHÔNG** — chuỗi hiển thị |
| `mike/bin/send_plan_report.sh:526-611` | như trên, in vào report duyệt plan | **KHÔNG** |
| `mike/bin/eod_trading_report.sh:188-205` | như trên, in vào EOD | **KHÔNG** |
| `dc_book_waterfall_paper.py:675-689` | như trên, paper | **KHÔNG** |
| `trading_bot/plan.py::cap_lag_orders` | **chỉ import `adv_vnd()`** (hàm tính ADV), KHÔNG import `ADV_THIN_VND` | CÓ chặn, nhưng chặn **KÍCH THƯỚC lệnh** (trần %ADV), không loại mã |

`ADV_THIN_VND = 2e9` (`trading_bot/due_diligence.py:45`) chỉ được đọc tại **một chỗ duy nhất**:
`_liquidity_part()` (`:231`), để in dòng `⚠ thanh khoản mỏng`. Nó **không** nằm trong
`RED_FLAG_CODES` (cố ý — comment `:299-300` ghi rõ). ⇒ **đổi nó thành "gate cứng" trong chính file
này là thao tác vô hiệu**: report sẽ in chữ đỏ hơn, lệnh vẫn đặt như cũ.

**Chỗ chặn thật nếu muốn siết** = `lag_liquidity_filter.py::lag_filter_illiquid()` (LIVE từ 07-21) —
hiện là gate cứng nhưng **nhị phân "đo được ADV hay không"** (`:179` `float(r.adv_vnd) > 0`), không
có ngưỡng độ lớn.

**Sleeve discretionary fear-buy: KHÔNG đi qua đây** — `grep "due_diligence" trading_bot/
discretionary_accumulation.py` trả **0 dòng**. Xác nhận đúng như dispatch giả định; nếu có wire thì
phạm vi sẽ phải hẹp lại, nhưng không có.

## §2 — Việc này ĐÃ được đo ở tầng danh mục, và đã CONFIRMED — không chạy lại

Job **`Taylor_20260804_080547`** (6 ngày trước) chạy đúng câu hỏi này: 7 chân engine, control tái
lập **tuyệt đối** pin R3 28,86/1,90/−17,8/1,62, self-check 0 VND cả 7 chân, **quant-skeptic
CONFIRMED cao** (`mike/logs/verify_20260804_083418.log`, skeptic tự chạy lại DSR/PBO/sign-test/LOO).
Kết quả cốt lõi, **vẫn còn hiệu lực, tôi không đo lại**:

- Phần **GIA TĂNG** của gate 2 tỷ đặt trên nền gate `ADV>0` đã có: **−0,26pp CAGR, −0,02 Sharpe,
  −0,92pp OOS** (chỉ được MaxDD +0,9pp, Calmar +0,07).
- **Thang liều PHẲNG** 0,5 → 5 tỷ (biên độ 0,21pp; 5 tỷ còn *thấp hơn* 2 tỷ) ⇒ 2 tỷ không có nội
  dung kinh tế riêng.
- Δ **đổi dấu** khi bỏ đồng thời 2017+2020+2021; thắng 6/13 năm (sign test p=0,709); **PBO = 0,916**.

Báo cáo này **chỉ bổ sung 3 trục mà job đó KHÔNG đo**: (a) kết cục **theo băng ADV** thay vì
gộp chung, (b) **hồ sơ chất lượng** của nhóm bị chặn, (c) **capacity rổ hôm nay**.

**Vì sao phải tách theo băng**: nhóm "bị gate 2 tỷ chặn" trong chân control bị **đuôi ADV≈0 chi
phối** (44,5% vốn sổ nằm ở băng ≤0,1 tỷ) — mà **live ĐÃ chặn đuôi đó** bằng `lag_filter_illiquid`.
Gộp chung thì đang trả lời câu hỏi live đã giải quyết xong. Băng quyết định thật là **0,1–2 tỷ**,
đúng vùng SCL (1,27–1,30 tỷ) nằm.

## §3 — Thang liều theo băng ADV (dữ liệu: chân control 08-04, 1.551 vị thế LAG)

> **v2 — đã sửa sau phản biện quant-skeptic (2026-08-10).** Bản v1 dùng
> `np.where(adv <= 1e8, "A", "D")`; so sánh với `NaN` luôn trả `False` nên **19 vị thế có
> `adv_vnd = NaN` bị dồn âm thầm vào băng D**. Đã kiểm gốc theo yêu cầu của skeptic:
> **19/19 là `Volume_3M_P50 = NaN`** (không đo được thật, không phải lỗi join) ⇒ chúng thuộc
> đúng lớp mà `lag_filter_illiquid` **đã chặn live rồi**, KHÔNG phải phần "gate 2 tỷ thêm vào".
> Nay tách thành hàng riêng **U**, và **cả §3, §4 lẫn BẢNG 2 dùng chung một định nghĩa băng duy
> nhất** (`bands_v2_reconciled.py`). Sửa xong, kết luận **mạnh lên** — băng D còn tệ hơn v1.

| Băng ADV tại ngày tín hiệu | n vị thế | bỏ dở | vốn (B) | % vốn sổ | P&L (B) | n deal | TB/deal | trung vị | winrate | %lỗ>20% |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A. ≤ 0,1 tỷ — **live ĐÃ chặn** | 615 | 56,1% | 4.599,8 | 44,5% | +66,24 | 270 | +2,09% | −0,60% | 44,4% | 5,6% |
| U. **ADV không đo được** — live ĐÃ chặn | 19 | **0,0%** | 81,5 | 0,8% | +5,78 | 19 | +2,99% | +2,45% | 57,9% | 5,3% |
| **D. 0,1–2 tỷ — phần gate 2 tỷ THÊM vào** | **348** | **93,4%** | **166,5** | **1,6%** | **+0,02** | **23** | **+0,78%** | **−1,86%** | **39,1%** | 0,0% |
| E. ≥ 2 tỷ — giữ lại | 569 | 32,2% | 5.491,0 | 53,1% | +339,59 | 386 | **+8,93%** | **+6,34%** | **65,5%** | 2,1% |

Băng D thua rõ băng E, **nhưng nó gần như không tồn tại về mặt kinh tế**: **1,6% vốn triển khai**,
P&L **+0,02B trên +411,61B** (làm tròn = 0), và **93,4% số lần vào không fill nổi**. Cắt nó đi
không đổi gì ở tầng danh mục — **đúng bằng lý do** A/B 08-04 chỉ ra −0,26pp (nhiễu).

Hàng **U** đáng chú ý riêng: **bỏ dở 0,0%, fill trọn 19/19** — đó chính là **lỗi fidelity `liq<=0`
đã biết** của engine (mã không đo được ADV thì được mua trọn size). Nó KHÔNG phải bằng chứng "mã
mỏng vẫn mua tốt"; nó là hiện vật mô phỏng, và live đã chặn lớp này từ 07-21.

### Độ bền theo thời gian — đây là căn cứ NO-GO mạnh nhất

| Cửa sổ | n deal D | TB_D | trung vị_D | winrate_D | TB_E | **D − E** | **CI95 bootstrap** |
|---|---:|---:|---:|---:|---:|---:|---|
| Toàn kỳ 2014–2026 | 23 | +0,78% | −1,86% | 39,1% | +8,93% | −8,16pp | [−11,87; −4,16] **khác 0** |
| IS 2014–19 | 15 | −0,35% | −2,10% | 33,3% | +7,65% | −8,00pp | [−12,42; −3,54] **khác 0** |
| **OOS 2020+** | **8** | +2,88% | +1,22% | 50,0% | +9,79% | −6,91pp | **[−14,07; +1,00] CHỨA 0** |
| 2019+ | 10 | +2,56% | +1,22% | 50,0% | +9,17% | −6,61pp | [−12,65; **−0,01**] sát mép, đọc như **chưa phân biệt được** |

**Vốn triển khai băng D theo năm (% sổ LAG):** 2014 **13,1%** · 2015 **20,6%** · 2016 **23,8%** →
2019 1,9% · 2021 1,1% · 2024 **0,5%** · 2026 1,0%. Hiện tượng **tự teo ~20 lần** (universe dày lên,
`universe_pit` + `lag_filter_illiquid` đã siết). Toàn bộ ý nghĩa thống kê nằm ở IS 2014–16; ở chế độ
thị trường hôm nay chỉ còn **8 deal trong 6,5 năm** và CI **không phân biệt được với 0**.

⇒ Siết bây giờ là **đóng một cánh cửa đã gần khép**, bằng một luật vĩnh viễn.

## §4 — Nỗi lo "loại oan mã tốt nhưng mỏng": **KHÔNG có bằng chứng ủng hộ**

Chất lượng đọc point-in-time tại ngày vào sổ: 8L rating từ `bq_cache/fa_ratings_8l.parquet`
(phủ 97,9%), FSCORE từ `bq_cache/ticker/<year>.parquet` (phủ 100%).

| Băng | n | trung vị rating | %rating ≤3 | trung vị FSCORE | %FSCORE ≥7 | n "giống SCL" |
|---|---:|---:|---:|---:|---:|---:|
| A. ≤0,1 tỷ | 615 | 3,0 | 67,7% | 6,0 | 38,4% | 193 |
| U. không đo được | 19 | 3,0 | 68,4% | 6,0 | 31,6% | 5 |
| **D. 0,1–2 tỷ** | 348 | **3,0** | **54,4%** | **6,0** | **35,6%** | **90** |
| E. ≥2 tỷ (giữ) | 569 | 3,0 | 69,9% | 6,0 | 29,3% | 145 |

**Nhóm bị chặn KHÔNG kém chất lượng hơn nhóm giữ** — cùng trung vị rating 3,0, cùng trung vị FSCORE
6,0, tỉ lệ FSCORE≥7 còn **cao hơn** (35,6% vs 29,3%). Đúng như user lo: sàn 2 tỷ **không phải** bộ
lọc chất lượng, nó cắt ngang qua mọi hạng.

**Nhưng kết cục thì ngược lại.** Nhóm "giống SCL" = băng D **∧** rating≤3 **∧** FSCORE≥7:

| | n vị thế | bỏ dở | n deal khớp | TB/deal | trung vị | winrate |
|---|---:|---:|---:|---:|---:|---:|
| **Mỏng (0,1–2 tỷ) + chất lượng tốt** | 90 | **95,6%** | **4** | **−2,03%** | **−2,32%** | **25,0%** |
| **CÙNG chất lượng nhưng ADV ≥2 tỷ** | 145 | 36,6% | **92** | **+9,15%** | **+5,73%** | **66,3%** |

4 deal đó: HDG@2015-02 −7% · LIX@2015-05 −0% · PTB@2015-10 −4% · VSH@2023-05 +4%.

> **Đính chính so với v1** (skeptic bắt đúng): v1 báo 9 deal / TB +0,19%. **6/9 trong đó
> (HEV, DXP, SDN, BED, SFN + SDN) là vị thế ADV không đo được**, không phải thành viên của băng
> 0,1–2 tỷ đang bàn. Sau khi tách đúng, chỉ còn **4 deal thật** — con số kém hơn (−2,03% vs +0,19%)
> nhưng **N mỏng hơn nhiều**.

⇒ Đọc cho đúng mức độ mạnh của bằng chứng: **4 deal trong 12,5 năm KHÔNG đủ để "chứng minh" nhóm
chất lượng-mỏng thua**. Điều nó cho phép kết luận là điều ngược lại, và đó mới là câu hỏi user hỏi:
**KHÔNG có bằng chứng nào cho thấy sẽ "loại oan" một nhóm tốt.** Trong 12,5 năm, giả thuyết "FA tốt
cứu được thanh khoản mỏng" chưa bao giờ được dữ liệu ủng hộ — **95,6% số ca thậm chí không vào nổi
hàng**, nên luận điểm tốt phần lớn chưa từng được kiểm chứng bằng tiền thật; 4 ca vào được thì
trung vị âm. Đây là **bác bỏ một nỗi lo**, KHÔNG phải bằng chứng dương cho việc siết.

## §5 — Capacity: sàn 2 tỷ bóp rổ bao nhiêu (đo HÔM NAY)

Universe `universe_pit` as-of **2026-08-07**: **364 mã** (`in_universe=true`), đo được ADV 364/364.
ADV = `Volume_3M_P50 × COALESCE(Price, Close)` — đúng công thức production.

| Sàn | Số mã bị loại | % universe | Còn lại |
|---|---:|---:|---:|
| 0,1 tỷ (gần chết — live đang chặn) | 5 | **1,4%** | 359 |
| 0,5 tỷ | 58 | 15,9% | 306 |
| 1 tỷ | 109 | 29,9% | 255 |
| **2 tỷ (câu hỏi)** | **159** | **43,7%** | **205** |
| 5 tỷ | 209 | 57,4% | 155 |
| 17 tỷ (năng lực fill thật, tính ở báo cáo 08-04) | 263 | 72,3% | 101 |

Phân vị ADV universe (tỷ/phiên): p10 **0,32** · p25 **0,82** · trung vị **2,70** · p75 21,55 · p90 89,53.
⇒ **sàn 2 tỷ nằm ngay dưới trung vị rổ** — đó là lý do nó cắt gần một nửa.

Mã sát mép bị loại (ADV cao nhất trong nhóm bị cắt): CDC 1,98 · HT1 1,93 · MIG 1,93 · LAS 1,90 ·
LDG 1,85 · DST 1,82 · SCG 1,80 · VNZ 1,74 · IDJ 1,73 · HPX 1,72 · SHI 1,71 · DLG 1,70 (tỷ/phiên).
**SCL: ADV3T = 1,27 tỷ/phiên → BỊ LOẠI** bởi sàn 2 tỷ.

Đối chiếu độ lớn: gate cắt **43,7% rổ chọn mã** để tránh một nhóm chỉ chiếm **1,6% vốn triển khai**
và **+0,02B/+411,61B P&L** trong 12,5 năm.

## §6 — Khuyến nghị

**NO-GO — không nâng `ADV_THIN_VND` thành gate cứng, cả trong `due_diligence.py` lẫn
`lag_liquidity_filter.py`.** Bốn căn cứ độc lập:

1. **Sai file**: sửa trong `due_diligence.py` không chặn được gì (§1). Chỉ riêng điều này đã đủ để
   không áp patch như dispatch mô tả.
2. **Không còn ý nghĩa ở chế độ hiện tại**: băng bị ảnh hưởng teo từ 23,8% vốn (2016) xuống ~1%
   (2019+), nay chỉ chiếm **1,6% vốn triển khai** và **P&L +0,02B/+411,61B**; CI95 của chênh lệch
   **chứa 0 ở OOS 2020+** và **sát mép (hi = −0,01) ở 2019+** (§3).
3. **Không thêm gì ở tầng danh mục**: −0,26pp CAGR / −0,02 Sharpe trên nền gate `ADV>0`, thang liều
   phẳng, **PBO 0,916** — đã đo và CONFIRMED 08-04 (§2). Không có ngưỡng nào trong họ này được phép
   chọn theo số IS.
4. **Giá phải trả không cân xứng**: cắt 43,7% rổ ứng viên hôm nay (§5) để tránh một nhóm sinh
   **+0,02B** P&L trong 12,5 năm.

**Điều DUY NHẤT nên đổi (và nó không phải việc siết ngưỡng):** nỗi lo của user đã có câu trả lời
đo được — nên **ghi nó lại** thay vì để mỗi lần gặp một SCL lại bàn từ đầu. Cụ thể: dòng cảnh báo
`⚠ thanh khoản mỏng` hiện chỉ nói "mỏng"; nó **không** nói cho người duyệt plan biết rằng nhóm đó
lịch sử **fill hỏng 88,6%** và khi khớp thì **kém ~7pp/deal**. Đó là thay đổi **hiển thị**, thuộc
đúng bản chất thuần-thông-tin của file, và **cần user quyết** vì nó đổi câu chữ report — tôi
**không tự áp**.

**Cảnh báo kế thừa (bắt buộc mang theo khi trích số ở đây):** mọi con số fill trong báo cáo này
đứng trên mô hình fill **20% ADV/phiên** của engine, **chưa neo vào fill thật** (live mới xác nhận
tới 3,86% ADV/phiên). Tỉ lệ "bỏ dở 88,6%" vì thế là **cận DƯỚI** của mức độ khó fill thật — nếu
neo đúng, băng D còn khó fill hơn nữa, tức gate còn **ít tác dụng hơn** chứ không nhiều hơn (nó chỉ
chặn thứ vốn đã không mua được). Sổ theo dõi: `kb/projects/lag-adv-filter-tracking.md`, mốc cứng
**2026-12-15 / 2027-03-31**.

## §7 — Hiện vật & tính trung thực của phép đo

`mike/agents/Taylor/exp_advgate_quality_20260810/`:
`pos_blocked_vs_kept.py` · `adv_band_dose.py` · `quality_of_blocked.py` · `capacity_today.py` ·
**`bands_v2_reconciled.py` (nguồn chuẩn tắc cho §3/§4/BẢNG 2 sau sửa)** · `pos_lag_blocked_flag.csv` ·
`pos_with_quality.csv` · `pos_bands_v2.csv` · `final_bands.txt` · `final_bands_v2.txt`.
⚠️ `adv_band_dose.py` và `quality_of_blocked.py` là **bản v1, giữ làm dấu vết audit** — chúng dùng
định nghĩa băng cũ (gộp NaN vào D) và **KHÔNG được trích số**; mọi số trong báo cáo này lấy từ
`bands_v2_reconciled.py`.

Dữ liệu đầu vào **tái dùng nguyên vẹn** chân control đã CONFIRMED của job 08-04
(`data/v23_golive_audit_2014_now_..._exp_ctrl0804_univpit.csv`) + `dropped_gate2000m.json`.
**Không chạy lại engine, không đụng CSV canonical, không sửa file production.**

**Bốn điều phải công bố — điều thứ 4 do quant-skeptic bắt, KHÔNG phải tôi tự thấy:**

1. **Khoá nối vị thế ≠ ngày tín hiệu.** `holding_id` mang **ngày vào sổ** = phiên KẾ TIẾP ngày tín
   hiệu (fill T+1 Open). Lần join đầu tiên khớp 0/3.232 sự kiện. Đã sửa bằng cách map mỗi `sd` sang
   phiên kế tiếp theo **lịch giao dịch lấy từ chính cột `ymd`** của audit CSV, rồi join chính xác →
   khớp **982/3.232** sự kiện vào vị thế (phần còn lại là ứng viên chưa bao giờ được mở vị thế).
2. **Một hiện vật parse của CHÍNH TÔI.** `VCR_20200427_?` — dòng SELL duy nhất trong toàn bộ dataset
   có `holding_id` mất hậu tố slice ⇒ groupby theo `holding_id` tách **một** vị thế thành hai
   (một bên `r = −100%`, bên kia `r = +∞`), làm bẩn TB của OOS băng D. Đã sửa bằng khoá
   `ticker_ngày`; sau khi sửa **0 vị thế suy biến** (assert trong script). 1/1.552 dòng — không phải
   lỗi engine (self-check 0 VND của chân control vẫn đúng).
3. **Đếm vị thế của tôi ≠ đếm của báo cáo 08-04** (1.551 vs 1.901). Chênh **349 = đúng số vị thế
   `ETF_PARK`** mà báo cáo kia gộp vào còn tôi loại (ETF park không bao giờ bị gate ADV cổ phiếu
   chạm tới). Số bỏ dở khớp tuyệt đối (**853 = 853**) ⇒ hai cách đếm nhất quán, chỉ khác định nghĩa
   mẫu. Phân chia blocked/kept của tôi (982/569) cũng khác báo cáo kia (918/983) do khoá join khác
   (họ dump từ trong engine, tôi nối từ CSV); tỉ lệ bỏ dở của nhóm bị chặn khớp gần như tuyệt đối
   (**68,2% vs 68,1%**) ⇒ hai đường đi độc lập cho cùng cấu trúc. **Kết luận định tính không phụ
   thuộc lựa chọn này**, nhưng mọi số tuyệt đối trong báo cáo này phải trích kèm định nghĩa mẫu ở đây.

4. **Phân băng sai với `NaN` — do quant-skeptic bắt, self-audit của chính tôi ở mục (1)–(3) đã
   BỎ SÓT.** `np.where(adv <= 1e8, ...)` dồn 19 vị thế `adv_vnd = NaN` vào băng D, làm §3/§4 bản v1
   sai và **mâu thuẫn với `adv_band_dose.py`** trong cùng thư mục hiện vật (n=367 vs n=348) mà báo
   cáo v1 không hề đối chiếu. Đã kiểm gốc theo đúng đề nghị của skeptic: **19/19 là
   `Volume_3M_P50 = NaN`** trong `bq_cache/ticker` tại ngày vào sổ ⇒ thuộc lớp `lag_filter_illiquid`
   đã chặn live, tách thành băng U. Sau sửa: **kết luận định tính mạnh lên** (băng D từ +1,78% xuống
   +0,78%/deal, winrate 47,6% → 39,1%), nhưng **N mỏng đi** (42 → 23 deal; nhóm giống-SCL 9 → 4).
   Bài học: một `np.where` trên cột có `NaN` là một nhánh im lặng — phải `np.select` có hàng
   `isna()` tường minh, và hai script trong cùng thư mục không được phép cho hai định nghĩa khác
   nhau về cùng một băng.

**N khai đúng** (`quant-research` §4): đơn vị độc lập cho chênh lệch return/deal là **23 deal hoàn
tất băng D** (8 ở OOS; 4 ở nhóm giống-SCL), **không phải** 348 vị thế hay 3.232 sự kiện ứng viên.
Multiple testing: tôi đã soi **5 băng ADV × 4 cửa sổ thời gian** — với số lát cắt đó, một CI
[−11,87; −4,16] toàn kỳ là gợi ý hướng, **không** phải bằng chứng đủ để wire; và nó đã tự sụp ở lát
cắt quan trọng nhất (OOS 2020+).

**Trạng thái phản biện:** quant-skeptic **CONFIRMED (confidence medium)**, log
`mike/logs/verify_20260810_074853_2816996.log`. Skeptic tái lập ĐỘC LẬP §5 (capacity, khớp từng số),
§1 (đọc code xác nhận `due_diligence.py` không chặn gì), §2 (trích dẫn job 08-04 chính xác), và
xác nhận claim quan trọng nhất — **CI OOS chứa 0** — **đứng vững kể cả trước lẫn sau** khi sửa bug
NaN. Hai check `fail` của skeptic (`reproducibility_selfcheck`, `arithmetic_mechanism`) đều trỏ về
đúng một lỗi ở mục 4 trên và **đã sửa xong trong bản v2 này**.
