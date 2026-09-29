# A/B trên R3 — chân WEIGHT `OShares` bước tại EX-DATE

Job `Taylor_20260927_043542` (vòng 1) + `Taylor_20260927_052432` (vòng 2, sau quant-skeptic).
**Bản này là số của VÒNG 2** — vòng 1 giữ lại nguyên văn ở `AB_R3_v1_superseded.md` vì mục
"thay đổi theo năm" của nó **sai cơ chế** (xem §"Vì sao năm 2021 lệch −3pp", phần viết lại).

Môi trường pin nguyên văn (`run_leg.sh`): `BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate`,
`BQ_CACHE_THREADS=1`, `$DNA_PYEXE`, `AUDIT_END=2026-06-19`, `NAV_TOTAL_B=50 ETF_LIQ=custompitg
BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7"`, engine `v23a none postbull 0 edge`,
`BASKET_CA_SNAPSHOT=data/snapshots/corp_action_share_20260927.parquet`.
Engine chạy qua `run_wt_leg.py` để nạp `custom_basket.py` CỦA WORKTREE (bẫy `sys.path` hardcode).

| Leg | `BASKET_OSHARES_STEP` | CAGR | Sharpe | MaxDD | Calmar | Final NAV | IS 14-19 | OOS 20+ | self-check | CSV md5 |
|---|---|---|---|---|---|---|---|---|---|---|
| `wexd2_ctl_quarter` control | `quarter` (tiền-sửa) | 24,38% | 1,69 | −18,8% | 1,30 | 757,61B | 19,26% | 29,24% | 0 VND BAL+LAG | `3f836927c0df82915c4cfb973d8f4af3` |
| `wexd2_new_exdate` | `exdate` (mặc định mới) | **24,42%** | **1,69** | **−18,8%** | **1,30** | **761,11B** | **19,31%** | **29,29%** | 0 VND BAL+LAG | `2f9c3702524391f5538d262edb17515d` |
| Δ (mới − control) | | **+0,04pp** | 0,00 | 0,0pp | 0,00 | +3,50B (+0,46%) | **+0,05pp** | **+0,05pp** | | 16.809 dòng cả hai |

IS/OOS **tính lại độc lập** bằng `extract_peryear.py` trên chính 2 CSV, không đọc từ log.

## Control leg là bằng chứng, không phải lời hứa
md5 chân control (`3f836927c0df82915c4cfb973d8f4af3`) **trùng khít md5 bản pin R3 hiện hành** ghi
trong `data/results_registry.md` § "2026-09-27 — ⭐ RE-PIN R3 — SỬA CHUỖI RETURN custom30V" ⇒ môi
trường tái lập đúng bản pin ở mức từng byte của ledger, nên Δ đọc được là do đúng một biến.

## Vòng 2 đổi gì so với vòng 1
Hai lỗi quant-skeptic nêu đã sửa (commit `d77f1123`): header nói ngược code về taxonomy ISS, và
cổng PIT 1 được mô tả như một đẳng thức. Cộng thêm **cổng PIT 3 mới** (`share_date` clamp về
`max(share_date, public_date)`; 34/764 bước khớp trước đó rơi vào ngày TRƯỚC khi sự kiện được công
bố, 1-15 ngày, median 3). **Tác động lên R3: KHÔNG có ở mức 2 chữ số thập phân** — cả 5 metric và
IS/OOS y nguyên vòng 1; chỉ md5 ledger đổi (`80fc59f9…` → `2f9c3702…`).
Trên đường publish, cổng 3 đổi đúng **một** rebal so với vòng 1: `2025-08-05`, TCB **−0,0244pp**
(ESOP exright 2025-08-04 nhưng `public_date` 2025-08-07 ⇒ tới ngày chốt weight TCB vẫn mang số CP
cũ). Các rebal khác byte-identical.

## Đọc con số thế nào
* **+0,04pp CAGR là mức NHIỄU, không phải edge.** Sharpe, MaxDD, Calmar không đổi tới 2 chữ số
  thập phân. Đúng như kỳ vọng tiên nghiệm: weight bị chặn bởi trần 10% mỗi tên và chỉ được chốt
  lại mỗi quý, nên một cửa sổ lệch median 42 ngày trên một tên chỉ đổi tỷ trọng vài chục bps.
* **Dấu nhất quán IS/OOS** (+0,05 / +0,05pp) — không có chân nào âm, nên không có dấu hiệu bản sửa
  "mua" lợi nhuận ở một chế độ thị trường.
* Đây là **bản sửa ĐÚNG-SAI (measurement fix)**: bỏ các bước look-ahead và các bước lệch ngày khỏi
  chân weight. Giá trị **không** nằm ở +0,04pp. Không được bán như một cải thiện lợi nhuận.
* **Trùng khớp độc lập**: nghiệm thu H3 FiinProX (job `Taylor_20260926_164113`) đo chân đối chứng
  cơ học `OSHARES_PIT_SCOPE=flat` và cũng ra **+0,04pp** cho phần "chỉ dời NGÀY bước nhảy". Hai
  đường đo khác nhau (nguồn FiinProX vs `corporate_action`) cho cùng một cỡ ảnh hưởng.

## Vì sao năm 2021 lệch −3pp — VIẾT LẠI (vòng 1 sai cơ chế)
Vòng 1 viết: *"2021 +116% → +113% (−3pp) … khớp với rebal `2021-11-05` là rebal đổi weight nặng
nhất (sum|Δw| 2,748pp)"*. **Sai**: `2021-11-05` là rebal của **RỔ** (đường publish), còn con số
theo năm là của **NAV hai book**, đi qua allocator. Gán cái này cho cái kia là suy nhân quả từ
trùng hợp thời gian. Ba phép đo dưới đây (script `yearly_attribution.py`, `basket_level_yearly.py`,
log kèm theo) cho cơ chế thật:

**(1) Lệch nằm TRỌN ở book BAL, không ở rổ.** Tách lợi nhuận theo năm của từng book từ chính ledger
2 chân (`nav_bal_ref` / `nav_lag_ref`):

| năm | BAL Δ | LAG Δ | NAV Δ |
|---|---|---|---|
| 2021 | **−8,55pp** | +0,07pp | −3,17pp |
| 2025 | **+2,56pp** | +0,02pp | +1,32pp |
| 2022 | **+1,41pp** | −0,00pp | +0,77pp |
| max mọi năm | 8,55pp (2021) | **0,22pp** (2015) | 3,17pp (2021) |

**Cả hai** book đều park vào custom30V (đo trên ledger: `bal_etf_ref` khác 0 ở 1.963 dòng,
`lag_etf_ref` ở 1.843 dòng, đỉnh 313B) ⇒ weight rổ đổi thì CẢ HAI đều nhận. Vậy mà Δ của LAG
**≤0,22pp mọi năm** còn BAL ăn 8,55pp trong một năm: bất đối xứng đó không giải thích được bằng cỡ
lệch weight — nó chỉ giải thích được bằng một khác biệt về ĐƯỜNG ĐI, và (3) chỉ ra đúng nó.

**(2) Cỡ lệch của CHÍNH CHUỖI RỔ nhỏ hơn hẳn, và 2021 lệch DƯƠNG.** Dựng lại `build_pit` đúng như
engine gọi (`ETF_LIQ=custompitg`) trên cache đã ghim, chỉ đổi `BASKET_OSHARES_STEP`:
lợi nhuận theo năm của chuỗi rổ lệch **max 2,19pp (năm 2020)**, còn **2021 = +0,27pp** — *ngược
dấu* với −3,17pp của NAV. CAGR chuỗi rổ 16,90% → 17,02% (+0,12pp).
⇒ không thể có đường nào để một rổ lệch +0,27pp sinh ra −3,17pp NAV trong cùng năm bằng cỡ lệch.

**(3) Cơ chế thật = PATH-DEPENDENCE của allocator.** Trong 12,46 năm, hai chân có **đúng một** ngày
rebal khác nhau: control rebal `2021-11-01`, chân mới rebal `2021-10-28` (mọi ngày rebal còn lại
trùng nhau, 39 ngày mỗi chân). Lệch weight vài bps đẩy chỉ số band của allocator qua ngưỡng sớm
**2 phiên**, và trong một năm +115% thì 2 phiên đó đáng 8,55pp trên book BAL. Đó là nhiễu thực thi
theo lịch — **không** phải bản sửa "làm mất" lợi nhuận 2021, và cũng **không** phải bằng chứng bản
sửa tốt hơn ở 2025 (+2,56pp cùng một cơ chế, dấu ngược).
Hệ quả khi đọc bảng: **chỉ tin con số FULL/IS/OOS**; một năm đơn lẻ trong A/B này không đo được
điều gì về bản sửa.

## Nếu merge thì phải làm gì tiếp
1. **Re-pin R3 sang 24,42% / 1,69 / −18,8% / 1,30 / 761,11B** (IS 19,31 / OOS 29,29) — hoặc quyết
   định giữ 24,38% và ghi rõ bản sửa này chưa vào pin. KHÔNG để hai con số cùng tồn tại không nhãn.
2. `bootstrap_nav.py` + `dsr_pbo_annex.py` **vẫn đang STALE từ JOB C** (khoản nợ đã biết, không
   phải mới). +0,04pp không làm nó xấu thêm nhưng lần chạy lại phải chạy trên bản CUỐI sau merge,
   không chạy hai lần. Nhớ FAIL-F (`yrs = N/252` thay vì theo lịch) phải sửa TRƯỚC khi chạy lại,
   nếu không số mới vẫn cao giả +0,30pp.
3. `custom30_history.py` chạy lại → `tav2_bq.custom30v_8l` đổi weight ở **17/49 rebal lịch sử**
   (32 byte-identical); rebal đang hiệu lực `2026-08-05` **không đổi một tên nào** ⇒
   `compute_park_trim.py` không sinh lệnh mới vì bản sửa này.

## Đường publish — vintage đã ghim, tái lập được
Vòng 1 chạy `custom30_history.py` đọc corp-action **LIVE BQ** ("4466 dòng"), mà `corporate_action`
bị UPSERT in-place ⇒ claim "0/30 tên đổi ở 2026-08-05" không tái lập được sau này. Vòng 2 truyền
`BASKET_CA_SNAPSHOT=data/snapshots/corp_action_share_20260927.parquet` (`run_publish_leg.sh`):

| leg | CSV md5 | ghi chú |
|---|---|---|
| `quarter` (control) | `8eb19acfd3c18392da23eaca6a5404dd` | 1.470 dòng / 49 rebal |
| `exdate` | `518651bf3c6b86fe814acc68daab14d6` | 1.470 dòng / 49 rebal |

**Chạy lại lần thứ hai trên HEAD đã commit `d77f1123`** (`run_publish_leg_v3.sh exdate`,
`publish3_exdate.log`) ra **cùng md5 `518651bf…`** ⇒ số publish ở đây là của code đã commit, không
phải của một working tree trung gian. Kiểm lại trực tiếp từ 2 CSV: **0 dòng lệch thành viên**,
**17/49 rebal đổi weight**, `2026-08-05` **0/30 tên đổi, max |dw| = 0,0000pp**.
Khác vòng 1 (đọc live): 783 bước được dời thay vì 781 — nguồn corp-action khác vintage + cổng PIT 3.
