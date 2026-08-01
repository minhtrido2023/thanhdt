# FSCORE làm ENHANCER cho custom30V (yieldcombo) — NO-GO

**Job**: `Taylor_20260801_131833` (attempt 2/2 — attempt 1 bị cắt sau khi đã chạy xong 11/17 leg;
6 leg còn lại vẫn chạy nền và về đích, không có gì phải làm lại)
**Ngày**: 2026-08-01 · **Tác giả**: Taylor (Quant/Algo)
**Quy trình**: `.claude/skills/quant-research/SKILL.md` (checklist đầy đủ, §1-16)
**Artifacts**: `data/fscore_c30v_20260801/` (17 log engine + 11 log basket + CSV + script)

---

## 0. Kết luận một dòng

**KHÔNG biến thể nào thắng cả IS lẫn OOS ở mức phân biệt được với nhiễu.** Hai biến thể duy nhất
dương ở cả hai nửa (`blend_w010` IS +0,018pp / OOS +0,250pp; `wtilt_t030` IS +0,068 / OOS +0,082)
là hai biến thể **liều nhỏ nhất** — biên độ 0,02–0,08pp, tức **0,1–0,3 lần độ lệch chuẩn của
placebo** (hoán vị ngẫu nhiên cùng chỗ). Đó là chữ ký của "không có hiệu ứng", không phải của
một tín hiệu nhỏ. **Khuyến nghị: KHÔNG wire. Giữ nguyên custom30V = yieldcombo rating-blind.**

Vì khuyến nghị là "không đổi gì", theo skill §12 **DSR/PBO không áp dụng** (không có config nào
được chọn để deploy) và theo §14 **không bắt buộc quant-skeptic**. Vẫn khai báo **N_trials = 11**
biến thể thật (3 tiebreak + 5 blend + 3 wtilt), cộng 4 leg placebo + 1 leg ctrl lặp lại.

---

## 1. Scope — đọc code thật trước (skill §1)

`custom30V` = `BASKET_SELECT=yieldcombo` trong `custom_basket.py` (`build_pit()`), engine
`pt_v23_audit_2014.py`. Xác nhận trực tiếp trong code (không tin mô tả):

- Chọn mã: `score[t] = rank_pct(1/PE) + rank_pct(1/PCF)` trên pool đã qua gate custom30
  (thanh khoản/chất lượng/forensic-exclude), sort giảm dần, cắt `top_n=30`.
- Trọng số: `BASKET_WT=namecap`, `name_cap=0.10`, water-fill trên base `mcap_yesterday * qmult`.
- **Rating-blind & FSCORE-blind hoàn toàn** ở bước chọn mã (`quality` không bật ở cấu hình pin).
- Rebalance: 48 kỳ trong 2014-01-02 → 2026-06-19 (theo quý).

Vai trò trong V2.4: **xe đậu tiền NEUTRAL** — đậu 70% phần idle cash khi state=3. Đo trên leg
ctrl: rổ chiếm trung bình **26,1% NAV** toàn kỳ (**33,0% trong IS**, **19,8% trong OOS**), có
1.768/3.107 phiên với tỷ trọng >1%. **Con số này quan trọng cho phần 6.**

## 2. Nguồn dữ liệu (skill §2)

FSCORE lấy từ `tav2_bq.ticker_financial` — CANONICAL theo
`mike/kb/data_registry/fundamentals/ticker_financial.md`. Join **point-in-time theo
`Release_Date`** (fallback `time + 45d`) — đúng convention mà block `BASKET_QFLOOR` sẵn có trong
chính `custom_basket.py` đang dùng, không tự chế convention mới.

Universe/regime: giữ nguyên cấu hình pin (`universe_pit` cho custom30V qua `ETF_LIQ=custompitg`,
state = `tav2_bq.vnindex_5state_dt5g_live`) — không đổi gì ngoài enhancer.

## 3. Môi trường pin (skill §3)

```
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate   BQ_CACHE_THREADS=1
NAV_TOTAL_B=50  ETF_LIQ=custompitg  BASKET_WT=namecap  BASKET_SELECT=yieldcombo
PARK_STATES="3:0.7"  AUDIT_END=2026-06-19
$DNA_PYEXE data/fscore_c30v_20260801/engine_fsx.py v23a none postbull 0 edge
```
= **đúng lệnh pin R3 hiện hành** (`data/results_registry.md`, mục "2026-07-29 RE-PIN R3 SAU
RESTATE DT5G"), chỉ thêm `EXP_TAG`/`AUDIT_EXP_TAG` để mọi output rơi vào tên file
**non-canonical** (coding_guidelines §8 — không có leg nào ghi đè được CSV pin).

Snapshot BQ: `bq_cache_asof20260729_postrestate` — **cùng vintage với số pin R3**, nên mọi delta
trong báo cáo này so được trực tiếp với nhau và với số pin.

## 4. Thiết kế — 3 họ enhancer + 1 họ placebo

Enhancer là block **AUDIT-ONLY**, sinh bằng `patch_fsx.py` từ `custom_basket.py` production ra
bản sao `custom_basket_fsx.py` (skill §13 — **không bao giờ sửa file production**). Mặc định
`BASKET_FS_MODE` rỗng ⇒ OFF ⇒ hành vi y hệt production.

| Họ | Cơ chế | Biến thể |
|---|---|---|
| **(a) tiebreak** | Sau khi sort yieldcombo, **trước** khi cắt top-30: hoán vị các mã **có FSCORE** trong dải bao quanh đường cắt (rank `30-K+1` … `30+K`) theo FSCORE giảm dần, vào đúng các slot chúng đang chiếm. Mã thiếu FSCORE giữ nguyên chỗ (fail-open). Mirror **nguyên văn** `_dy_reorder` (arm A4 đã có sẵn trong file) — chỉ khác khoá sắp xếp. | K=5, 10, 20 |
| **(b) blend** | `score[t] += w * rank_pct(FSCORE)`, cộng trên **cùng thang [0,2]** mà yieldcombo đang sống (`pe_r + pcf_r`) ⇒ `w` đọc thẳng ra được "tỷ trọng FSCORE = w/(2+w)". Thiếu FSCORE → mid-rank 0.5 (đúng convention thiếu-yield sẵn có). | w=0.1, 0.2, 0.4, 0.8, 2.0 (≈4,8% → 50% tỷ trọng) |
| **(c) wtilt** | **Thành viên rổ KHÔNG đổi** (cắt top-30 thuần yieldcombo). Chỉ đổi trọng số: `qmult *= 1 + T*2*(rank_pct(FSCORE)-0.5)`, rank tính **trong rổ 30 mã**. | T=0.3, 0.6, 0.9 |
| **(d) placebo** | **Null-distribution control cho (a)**: cùng dải K=10, cùng số mã bị dời, chỉ khác là hoán vị **NGẪU NHIÊN** thay vì theo FSCORE. Seed theo `(SEED, ordinal(date))` ⇒ mỗi kỳ rút độc lập nhưng cả đường 48 kỳ replay được. | seed 1, 2, 3, 4 |

FSCORE là **số nguyên 0–9** ⇒ hoà điểm rất phổ biến; tie phá theo thứ hạng yieldcombo sẵn có, tức
**hoà = không đổi gì** — enhancer chỉ tác động ở chỗ FSCORE thực sự phân biệt được.

## 5. Self-check & tính hợp lệ của harness (skill §7)

| Kiểm tra | Kết quả |
|---|---|
| **Ctrl tái lập số pin R3** | `fsctrl`: **CAGR 27,600% · Sharpe 1,843 · MaxDD −17,463% · Calmar 1,580** vs pin **27,60/1,84/−17,5/1,58** → **khớp tuyệt đối**. |
| **Self-check 0 VND** | **17/17 leg**, mỗi leg 2 dòng (BAL + LAG): `cash-flow identity max err = 0 VND; final NAV identity err = 0 VND`. |
| **Module OFF == production** | `[1] OFF == production: members_identical=True levels_max_abs_diff=0.0 → PASS` (leg `prod_off` build bằng `custom_basket_fsx` với mode rỗng, so từng thành viên + từng mức chỉ số với `custom_basket.py` thật). |
| **Tái lập sau khi vá thêm placebo** | `fsctrl2` (chạy lại ctrl bằng module **đã** thêm nhánh `placebo_tieb`) = **27,600/1,843/−17,463/1,580**, delta 0,000 mọi cột, per-year trùng từng năm ⇒ 11 leg chạy trước bản vá vẫn hợp lệ. |
| **PIT audit (skill §8)** | 1.440 ô `(rebal_date, ticker)`, 1.438 có FSCORE đã công bố: `rows_effective_after_d=0`, `stale_pick=0` → **PASS**. Coverage FSCORE của rổ ctrl = **99,9%**. |
| **Sanity churn** | blend churn đơn điệu theo w `[31, 52, 116, 220, 465]` mã bị đổi/48 kỳ; tiebreak churn không giảm theo K `[107, 223, 459]`; wtilt swaps = **0** (đúng thiết kế) với `max_qmult_dev` = T. |
| **Recompute độc lập** | `extract_peryear.py` trên CSV audit của `fsctrl`/`tieb_k10`/`blend_w080` khớp bảng dưới tới 2 chữ số. |
| **Production sạch (§13)** | `git status` sạch trên `custom_basket.py`, `pt_v23_audit_2014.py`, `rating_8l.py`. |

## 6. Kết quả — TIER 2 (full engine, NAV danh mục). OOS là trọng tài.

Delta CAGR (pp) so với ctrl. **Đây là bảng quyết định.**

| leg | Full | **IS 2014-19** | **OOS 2020+** | ΔSharpe | ΔOOS Sharpe | ΔMaxDD | thắng cả 2 nửa? |
|---|---:|---:|---:|---:|---:|---:|:--|
| tieb_k05 | −0,223 | −0,523 | +0,073 | −0,002 | −0,005 | +0,42 | không |
| **tieb_k10** | +0,066 | **−0,592** | **+0,718** | +0,028 | +0,035 | +0,25 | không |
| tieb_k20 | +0,087 | −0,441 | +0,613 | +0,030 | +0,034 | −2,06 | không |
| blend_w010 | +0,135 | **+0,018** | **+0,250** | +0,010 | +0,018 | −0,09 | *có (biên độ ~0)* |
| blend_w020 | −0,030 | +0,015 | −0,075 | +0,002 | −0,001 | +0,07 | không |
| blend_w040 | −0,028 | −0,424 | +0,363 | −0,003 | +0,015 | +0,08 | không |
| **blend_w080** | +0,064 | **−0,828** | **+0,955** | +0,025 | +0,043 | −0,23 | không |
| blend_w200 | −0,569 | −1,381 | +0,240 | −0,006 | +0,002 | −3,30 | không |
| wtilt_t030 | +0,075 | **+0,068** | **+0,082** | +0,005 | +0,005 | +0,12 | *có (biên độ ~0)* |
| wtilt_t060 | −0,189 | +0,199 | −0,562 | −0,010 | −0,028 | +0,27 | không |
| wtilt_t090 | −0,108 | +0,314 | −0,512 | −0,006 | −0,026 | +0,43 | không |
| *plac_k10_s1..s4* | *−1,09 / −0,53 / −0,79 / +0,03* | *−0,59 / −0,35 / −0,87 / −0,26* | *−1,59 / −0,71 / −0,71 / +0,33* | | | | *(null)* |

**Placebo null** (hoán vị ngẫu nhiên cùng dải K=10, n=4 seed):

| chỉ tiêu | placebo mean | placebo sd | tieb_k10 (FSCORE thật) | z | hạng | p một phía (n=4) |
|---|---:|---:|---:|---:|:--|---:|
| Δ Full CAGR | −0,595 | 0,479 | +0,066 | +1,38 | 1/5 | ≥0,20 |
| **Δ IS CAGR** | −0,520 | 0,272 | **−0,592** | **−0,27** | **3/5** | **≥0,60** |
| Δ OOS CAGR | −0,668 | 0,784 | +0,718 | +1,77 | 1/5 | ≥0,20 |
| Δ OOS Sharpe | −0,047 | 0,044 | +0,035 | +1,85 | 1/5 | ≥0,20 |

Đọc đúng: **trong IS, sắp xếp theo FSCORE thật làm y hệt một hoán vị ngẫu nhiên** (z = −0,27,
hạng 3/5 — tức 2 trong 4 seed ngẫu nhiên còn *tốt hơn* FSCORE). Trong OOS, FSCORE tốt hơn cả 4
seed nhưng với n=4 thì p không thể nhỏ hơn 0,20; z≈1,8 chưa phải bằng chứng.

## 7. Bốn lý do độc lập nói "đây là nhiễu, không phải tín hiệu"

**(1) Dose-response ngược dấu và triệt tiêu nhau giữa hai nửa (skill §9).**

```
blend, theo w tăng dần:   IS  +0,02  +0,02  −0,42  −0,83  −1,38     (đơn điệu GIẢM)
                          OOS +0,25  −0,07  +0,36  +0,95  +0,24     (không đơn điệu)
wtilt, theo T tăng dần:   IS  +0,07  +0,20  +0,31                    (đơn điệu TĂNG)
                          OOS +0,08  −0,56  −0,51                    (đơn điệu GIẢM)
tiebreak, theo K tăng:    IS  −0,52  −0,59  −0,44                    (âm, phẳng)
                          OOS +0,07  +0,72  +0,61                    (dương, không đơn điệu)
```
Cấu trúc đơn điệu **duy nhất** xuất hiện nhất quán trong cả 3 họ là: **cho FSCORE tác động mạnh
hơn thì một nửa tốt lên và nửa kia xấu đi, độ lớn xấp xỉ bù trừ**. Một tín hiệu thật cho
dose-response **cùng dấu** ở cả hai nửa; một nhiễu-không-thông-tin cho đúng hình dạng này.

**(2) Hai biến thể "thắng cả 2 nửa" chính là hai biến thể gần control nhất.** `blend_w010` đổi
0,65 mã/kỳ (31 mã trên 48 kỳ); `wtilt_t030` **không đổi thành viên nào**, chỉ nghiêng trọng số
±30%. Delta IS của chúng (+0,018 và +0,068pp) = **0,07 và 0,25 lần sd placebo IS**. Nói cách
khác: càng làm ít thì càng "an toàn", đúng như khi enhancer không mang thông tin gì.

**(3) Hiệu ứng đi ngược với mức phơi nhiễm của chính cái xe được cải tiến.** Rổ chiếm **33,0% NAV
trong IS** nhưng chỉ **19,8% trong OOS**. Nếu FSCORE thật sự làm rổ tốt hơn, hiệu ứng phải **lớn
hơn ở IS**. Quan sát ngược lại: IS âm (−0,59pp với tieb_k10), OOS dương (+0,72pp). Không có cơ
chế nào giải thích được chiều này ngoài đường-đi/tái-triển-khai vốn (path noise).

**(4) Tier vị thế và tier engine mâu thuẫn dấu, và phân rã swap giết luôn câu chuyện nhân quả
(skill §6, §10).** Ở tier rổ, `tieb_k10` **thắng cả hai nửa** (basket CAGR +1,88pp Full, IS +1,15
/ OOS +2,66). Nhưng qua engine thì IS lật sang **−0,59pp**. Và phân rã kept-vs-swapped — so lợi
suất quý tới của **các mã ĐƯỢC THÊM** vs **các mã BỊ LOẠI**, kích thước rổ luôn = 30 nên **không
có hiệu ứng cô đặc**:

| leg | n_events | mean diff (pp) | t | hit% | IS diff / hit | **OOS diff / hit** |
|---|---:|---:|---:|---:|---:|---:|
| tieb_k05 | 46 | +3,69 | 1,63 | 58,7% | +4,73 / 63,6% | +2,74 / 54,2% |
| **tieb_k10** | 47 | +1,46 | 0,92 | 55,3% | +4,53 / 72,7% | **−1,24 / 40,0%** |
| tieb_k20 | 47 | +1,21 | 0,93 | 46,8% | +3,93 / 59,1% | −1,18 / 36,0% |
| blend_w080 | 47 | +1,35 | 0,78 | 53,2% | +3,23 / 68,2% | −0,30 / 40,0% |

Ở **OOS** — đúng cái nửa mà engine bảo `tieb_k10` lời +0,72pp — **các mã FSCORE thêm vào lại chạy
KÉM hơn các mã nó loại ra** (−1,24pp, hit 40%). Lợi nhuận OOS ở engine **không đến từ việc chọn
mã tốt hơn**. Không có t nào trong bảng vượt 1,7; N = 46–47 kỳ rebalance (skill §4: **đơn vị độc
lập là 48 kỳ rebalance**, không phải 1.440 ô hay 3.107 phiên).

Thêm: `blend_w080` có OOS +0,955pp trông đẹp nhất bảng, nhưng **toàn bộ đến từ riêng năm 2021**
(+14,71pp năm đó; bỏ 2021 ra → trung bình OOS **−0,70pp**). Đây đúng kiểu 1-năm-cân-hết-edge mà
KNOWLEDGE §8 đã bắt trong ca Wave1/H8a.

## 8. Đối chiếu với finding liền kề (skill §11) — vì sao IC +0,037 không chảy vào được NAV

Sáng nay (`Taylor_20260801_082823`) chính tôi đo `fs_pts` marginal IC **+0,037 (t=6,72, hit 78%,
N=36.816 obs/49 quý)** trên scope COMPOUNDER+CYCLICAL, và IC PANEL 8L 06-21 cho +0,031 pooled.
Hai kết quả **không mâu thuẫn** với NO-GO hôm nay; chúng đo hai thứ khác nhau:

1. **Mặt cắt rộng vs biên của một lát cắt hẹp.** IC đo trên toàn bộ mặt cắt vài trăm mã. custom30V
   chỉ quyết định "30 mã nào trong pool đã lọc" — tiebreak chỉ tác động ở dải quanh đường cắt,
   nơi các mã đã gần như tương đương về yieldcombo và **phương sai FSCORE còn lại rất nhỏ**.
2. **FSCORE là số nguyên 0–9.** Trong một dải 20 mã, rất nhiều mã cùng điểm; tie = không đổi gì.
   Số cặp mà FSCORE thực sự phân biệt được nhỏ hơn nhiều so với "20 mã trong dải".
3. **Pha loãng ~4 lần.** Rổ chỉ chiếm 26% NAV trung bình ⇒ một edge tier-rổ +1,9pp co lại còn
   ~+0,5pp ở NAV *trước khi* tính chi phí.
4. **Phí đảo danh mục ăn hết phần còn lại.** Placebo cho thấy **đảo ngẫu nhiên ở đường cắt tốn
   ~−0,60pp Full CAGR**. FSCORE phải trả cái phí đó trước. So với placebo, `tieb_k10` +0,66pp
   Full/+1,39pp OOS — tức FSCORE **có** hơn ngẫu nhiên một chút; nhưng so với lựa chọn thật là
   **không làm gì**, nó chỉ còn +0,07pp Full. Câu đúng là: *FSCORE mang một chút thông tin, nhưng
   không đủ để bù chi phí hành động lên thông tin đó trong cỗ xe này.*

Đây cũng là lý do giữ FSCORE ở nơi nó đang có ích — trục 2/12 trong `core_score()` và gate
`FSCORE>=6` trong `capit_basket()` (đã tái xác nhận GIỮ NGUYÊN sáng nay) — nơi nó hoạt động như
gate/scoring trên mặt cắt rộng, **không** phải như bộ chọn biên trong một rổ 30 mã.

## 9. Bẫy v3latest — đã tránh được, và tránh cả chiều ngược lại

Cảnh báo trong dispatch (thread (b) đóng 2026-06-22): `v3latest` FULL +0,27pp nhưng IS +1,40 /
OOS −0,78 → dồn hết vào IS. Ở đây **không lặp lỗi đó**, và cũng không rơi vào bản đối xứng của
nó: `tieb_k10`/`blend_w080` có hình dạng **ngược** (IS âm, OOS dương). Cám dỗ là gọi cái đó là
"đã qua OOS". Nó **không phải** — một biến thể chỉ thắng ở một nửa vẫn là một biến thể có delta
đổi dấu theo mẫu, dù nửa nào thắng. Trọng tài OOS dùng để **loại** thứ chỉ đẹp ở IS, chứ không
phải để **phong** thứ chỉ đẹp ở OOS. Cộng thêm 4 kiểm tra ở §7, kết luận không đổi.

## 10. Khuyến nghị

1. **KHÔNG wire bất kỳ biến thể nào.** custom30V giữ nguyên yieldcombo rating-blind/FSCORE-blind.
2. **Đóng lead "FSCORE ứng viên enhancer selection"** trong IC PANEL 8L (`results_registry.md`
   mục 6) — đã test đúng bài, kết quả âm ở tier quyết định (NAV). Không cần mở lại trừ khi cơ chế
   đổi (ví dụ custom30V tăng tỷ trọng NAV mạnh, hoặc rổ nới ra nhiều hơn 30 mã).
3. Không sửa production, không tạo cron mới, không đổi `trading_rules.json`.
4. Không cần quant-skeptic (kết quả âm, không đề xuất đổi production) — nhưng **artifact đầy đủ
   ở `data/fscore_c30v_20260801/`** nếu ai muốn phản biện: mọi log giữ nguyên self-check và cấu
   hình đầy đủ ở dòng `EXIT=` cuối file.

## 11. Hạn chế phải nói ra

- **n=4 seed placebo** là ít; p một phía không thể nhỏ hơn 0,20. Placebo dùng để đo **sàn nhiễu**
  (sd ≈ 0,5–0,8pp), không dùng để "chứng minh FSCORE vô dụng" — kết luận NO-GO dựa vào 4 lý do
  độc lập ở §7, không dựa vào riêng p-value nào.
- Chỉ test **một** dạng PIT cho FSCORE (as-of `Release_Date`). Không test FSCORE_P1, không test
  delta FSCORE (P0 − P1) — một trục khác về nguyên tắc có thể khác; nằm ngoài scope job này.
- Vintage `bq_cache_asof20260729_postrestate`; số so trực tiếp được với pin R3 hiện hành, **không**
  so trực tiếp được với các số pin trước restate DT5G 07-29.
- Kết quả là về **custom30V ở NAV=50B với PARK_STATES=3:0.7**. Nếu tỷ trọng đậu tiền hoặc số
  trạng thái đậu thay đổi lớn, độ pha loãng ở §8 điểm 3 đổi theo và bài test cần chạy lại.
