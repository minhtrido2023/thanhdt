# A/B trên R3 — chân WEIGHT `OShares` bước tại EX-DATE

Job `Taylor_20260927_043542` · 2026-09-27. Môi trường pin nguyên văn (`run_leg.sh`):
`BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate`, `BQ_CACHE_THREADS=1`, `$DNA_PYEXE`,
`AUDIT_END=2026-06-19`, `NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap
BASKET_SELECT=yieldcombo PARK_STATES="3:0.7"`, engine `v23a none postbull 0 edge`,
`BASKET_CA_SNAPSHOT=data/snapshots/corp_action_share_20260927.parquet`.
Engine chạy qua `run_wt_leg.py` để nạp `custom_basket.py` CỦA WORKTREE (bẫy `sys.path` hardcode).

| Leg | `BASKET_OSHARES_STEP` | CAGR | Sharpe | MaxDD | Calmar | Final NAV | IS 14-19 | OOS 20+ | self-check | CSV md5 |
|---|---|---|---|---|---|---|---|---|---|---|
| `wexd_ctl_quarter` control | `quarter` (tiền-sửa) | 24,38% | 1,69 | −18,8% | 1,30 | 757,61B | 19,26% | 29,24% | 0 VND BAL+LAG | `3f836927c0df82915c4cfb973d8f4af3` |
| `wexd_new_exdate` | `exdate` (mặc định mới) | **24,42%** | **1,69** | **−18,8%** | **1,30** | **761,11B** | **19,31%** | **29,29%** | 0 VND BAL+LAG | `80fc59f9476b280225063bd02136c75d` |
| Δ (mới − control) | | **+0,04pp** | 0,00 | 0,0pp | 0,00 | +3,50B (+0,46%) | **+0,05pp** | **+0,05pp** | | 16.810 vs 16.819 dòng |

## Control leg là bằng chứng, không phải lời hứa
md5 của chân control (`3f836927c0df82915c4cfb973d8f4af3`) **trùng khít md5 của bản pin R3 hiện
hành** ghi trong `data/results_registry.md` § "2026-09-27 — ⭐ RE-PIN R3 — SỬA CHUỖI RETURN
custom30V". ⇒ môi trường tái lập đúng bản pin ở mức từng byte của ledger, nên Δ đọc được là do
đúng một biến. (Điều này cũng trả lời lo ngại `[forensic exclude] none` trong log worktree —
`data/forensic_flags.csv` không tồn tại trong worktree, nhưng chân control vẫn tái lập md5 pin nên
nó không tác động tới kết quả ở cấu hình này.)

## Đọc con số thế nào
* **+0,04pp CAGR là mức NHIỄU, không phải edge.** Sharpe, MaxDD, Calmar không đổi tới 2 chữ số
  thập phân. Đúng như kỳ vọng tiên nghiệm: weight bị chặn bởi trần 10% mỗi tên và chỉ được chốt
  lại mỗi quý, nên một cửa sổ lệch median 42 ngày trên một tên chỉ đổi tỷ trọng vài chục bps.
* **Dấu nhất quán IS/OOS** (+0,05 / +0,05pp) — không có chân nào âm, nên không có dấu hiệu bản sửa
  "mua" lợi nhuận ở một chế độ thị trường.
* Đây là **bản sửa ĐÚNG-SAI (measurement fix)**, giá trị nằm ở chỗ bỏ **73 bước look-ahead** và
  **663 bước lệch ngày** khỏi chân weight, **không** ở +0,04pp. Không được bán như một cải thiện
  lợi nhuận.
* **Trùng khớp độc lập**: nghiệm thu H3 FiinProX (job `Taylor_20260926_164113`) đo chân đối chứng
  cơ học `OSHARES_PIT_SCOPE=flat` và cũng ra **+0,04pp** cho phần "chỉ dời NGÀY bước nhảy". Hai
  đường đo khác nhau (nguồn FiinProX vs `corporate_action`) cho cùng một cỡ ảnh hưởng.
* Thay đổi theo năm lớn nhất: **2021 +116% → +113%** (−3pp) và 2022 −9% → −8% (+1pp), khớp với
  rebal `2021-11-05` là rebal đổi weight nặng nhất (sum|Δw| 2,748pp).

## Nếu merge thì phải làm gì tiếp
1. **Re-pin R3 sang 24,42% / 1,69 / −18,8% / 1,30 / 761,11B** (IS 19,31 / OOS 29,29) — hoặc quyết
   định giữ 24,38% và ghi rõ bản sửa này chưa vào pin. KHÔNG để hai con số cùng tồn tại không nhãn.
2. `bootstrap_nav.py` + `dsr_pbo_annex.py` **vẫn đang STALE từ JOB C** (khoản nợ đã biết, không
   phải mới). +0,04pp không làm nó xấu thêm nhưng lần chạy lại phải chạy trên bản CUỐI sau merge,
   không chạy hai lần.
3. `custom30_history.py` chạy lại → `tav2_bq.custom30v_8l` sẽ đổi weight ở **16/49 rebal lịch sử**;
   rebal đang hiệu lực `2026-08-05` **không đổi** ⇒ `compute_park_trim.py` không sinh lệnh mới vì
   bản sửa này.
