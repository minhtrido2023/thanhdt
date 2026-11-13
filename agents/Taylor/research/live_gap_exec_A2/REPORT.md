# Luồng A vòng 2: đo lại LIQ_ZERO_BLOCK=lag sau khi bịt lỗ NULL `Volume_3M_P50`

Job `Taylor_20261112_181209`. Brief: `brief.md`. ⚠️ Đây là bản PAPER. **KHÔNG merge, KHÔNG đổi production, `trading_rules.json` hay neo sizing −25,2%.**
Mọi số dưới đây đều đo trong job này (log ở `logs/`, ledger ở `ledgers/`). Chưa qua quant-skeptic.

## 1. Kết luận

1. **Lỗ NULL KHÔNG phải nguyên nhân làm L2 tụt năm 2015.** Bịt lỗ NULL thì L2 gần như không đổi:
   - Năm 2015: pin0% 5,7% → 5,4% (fill) / 5,1% (pit); pin1M 8,7% → 8,3% / 8,1%.
   - CAGR FULL: pin0% 23,44% → 23,38% / 23,32%; pin1M 27,11% → 27,02% / 26,85%.
   - DD5 bootstrap: pin0% −27,7% → −27,7% / −27,7%; pin1M −25,2% → −25,1% / −25,3%.

   Mọi Δ đều nằm trong biên nhiễu tie-break của Luồng A (sd CAGR 0,17pp ở pin0%, 0,26pp ở pin1M).
2. **Gần hết chênh L1→L2 đến từ các mã có `Volume_3M_P50` ≤ 0**, tức trung vị khối lượng 60 phiên bằng 0. Ở chế độ `off`, các mã này được mua TRỌN size trong 1 phiên. Trên cả kỳ ở pin0%, `logs/decomp_full.log` cho thấy:
   - Có 255 holding LAG ở L1 bị L2 chặn vì ADV ≤ 0, tổng mua 3.757 tỷ.
   - Chỉ 16 holding bị chặn vì NULL, tổng mua 74 tỷ.

   Cửa sổ 2015H2–2016H1: 18 holding ≤0 (89,8 tỷ mua) so với 10 holding NULL (45,9 tỷ). Ngay cả khi đã bịt NULL, 8 holding NULL được mua lại ở L2F cũng chỉ mua được 6,5 tỷ thay vì 36,2 tỷ, vì bị trần 20% ADV × ≤5 phiên. Lãi của chúng vì thế còn 0,42 tỷ thay vì 3,78 tỷ. **Khoản "lãi 2015" của L1 là fill ảo (capacity-infeasible), không phải lãi đánh mất.**

   > **Đính chính 13/11 (Luồng A3, job `Taylor_20261113_021435`, theo quant-skeptic):** cơ chế 2015 là fill ảo KHÔNG TRẦN của **CẢ HAI** loại ngày mà `off` cho mua trọn size trong 1 phiên — (i) mã có `Volume_3M_P50` ≤ 0 và (ii) ngày `Volume_3M_P50` NULL — chứ không chỉ ADV ≤ 0. Riêng cửa sổ 2015H2–2016H1, loại NULL không nhỏ: 10 holding / 45,9 tỷ mua so với 18 holding / 89,8 tỷ của loại ≤ 0, và về **lãi** loại NULL còn LỚN HƠN: 5,56 tỷ so với 2,74 tỷ (pin0%; pin1M 13 holding NULL 5,89 tỷ vs 20 holding ≤0 3,03 tỷ — `logs/decomp_2015.log`). Câu "gần hết chênh L1→L2 đến từ ADV ≤ 0" ở đầu mục này đúng cho TOÀN KỲ (3.757 so với 74 tỷ), KHÔNG đúng cho riêng 2015.
3. **Ở chế độ `off`, lỗ NULL thổi phồng L1.** So L1 (bq) với bản không NULL: pin0% 22,31% → 21,74% (fill) / 21,77% (pit); pin1M 25,87% → 25,28% / 25,05%. Lý do: ngày NULL không có trần nên lệnh fill trọn size.
4. **Phân rã L1(bq)→L2(bq)**, tổng +1,13pp ở pin0% và +1,24pp ở pin1M, theo chuỗi pit:

   | Thành phần | pin0% | pin1M |
   |---|---|---|
   | Lỗ NULL dưới `off` (L1→L1P) | −0,54pp | −0,82pp |
   | Chặn ADV≤0 trên ADV sạch, tức phần khớp live (L1P→L2P) | +1,55pp | +1,80pp |
   | Hiện vật NULL còn lại trong L2 (L2P→L2) | +0,12pp | +0,26pp |

   Dịch chuyển IS→OOS vẫn còn nguyên trên ADV sạch: IS 19,25→16,38%, OOS 24,08→30,04% (pin0%). Nghĩa là dịch chuyển này thuộc phần khớp live, không phải hiện vật NULL.
5. **Số L2 sạch NULL**, dùng chuỗi pit vì nó khớp định nghĩa live (§3):
   - **pin0% (sàn): CAGR 23,32%, DD5 −27,7%.**
   - **pin1M (trần): CAGR 26,85%, DD5 −25,3%.**

   Với neo sizing, DD5 sàn vẫn là **−27,7%**, sâu hơn neo hiện hành −25,2% là 2,5pp. **Đây chỉ là số báo cáo, KHÔNG đổi neo.** Số này áp cho L2 (LAG data vintage 10-29). L3 (adj v2) chưa chạy lại với ADV sạch.
6. **Có nên lấy `LAG_ADV_SRC=pit` làm mặc định? Nên, nhưng có điều kiện** (§5). Trong job này KHÔNG đổi mặc định.

## 2. Đường ADV thay thế: bước 1 (`adv_validate.py`, `logs/adv_validate.log`)

Dữ liệu đo: cache `bq_cache_asof20260729_postrestate`, 2014-01-01 → 2026-06-19, 3,47 triệu dòng, 1.291 mã.

| Biến thể (trung vị `Volume`) | n | khớp chính xác | \|rel\| p50 | p90 | p99 | trong ±5% |
|---|---|---|---|---|---|---|
| 60 dòng GỒM ngày t | 2.315.643 | **98,31%** | 0,0000 | 0,0000 | 0,085 | 98,77% |
| 60 dòng TRƯỚC t | 2.310.128 | 49,04% | 0,0026 | 0,100 | 0,600 | 80,18% |
| 63 dòng gồm t | 2.299.868 | 12,67% | 0,026 | 0,158 | 0,939 | 67,65% |

Từ bảng này rút ra hai điều:
- **`Volume_3M_P50` thực chất là trung vị 60 dòng, GỒM ngày t.** Engine tra ADV ở ngày FILL (T+1), nên khối lượng của chính ngày fill lọt vào ADV. Đây là look-ahead trong ngày, nhỏ: biến thể pit bỏ ngày fill ra thì chỉ lệch 0,06pp (pin0%) và 0,17pp (pin1M) so với fill, trong biên nhiễu.
- **Về độ phủ:** từ 2014 đến 06-19 có 52.155 dòng có giao dịch mà NULL, rải trên 1.140 mã. Riêng 2015Q4 chiếm 15.953 dòng; 2016Q1–Q2 thêm 8.169 dòng. Bản tự tính phủ được 39.165 dòng trong số đó (35.025 dòng > 0); phần còn lại là mã mới niêm yết chưa đủ 20 phiên. Tỷ lệ NULL trên dòng có giao dịch từ 2022: 0,57% / 0,25% / 0,34% / 0,20% / 0,21% (2022→2026).

**Knob `LAG_ADV_SRC`** (commit `4f7609c34` cho họ pin0%, `770393ce2` cho họ pin1M; chỉ chạm book LAG):
- `bq`: mặc định, byte-identical (§4).
- `fill`: `COALESCE(Volume_3M_P50, trung vị 60 dòng gồm t) × PxAdv(t)`. Chỉ bịt lỗ, giữ nguyên định nghĩa BQ.
- `pit`: `trung vị Volume 60 dòng t−60..t−1 × PxAdv(t−1)`. Không dùng cột BQ và không gồm ngày fill.

Cả hai biến thể tự tính dùng `min_periods=20` (`LAG_ADV_MINP`). Tên file mang tag `_advsrc{fill,pit}`. Số key ADV tăng từ 2.132.258 lên 2.170.899 (fill) / 2.170.535 (pit).

## 3. Ladder

Điều kiện chạy: FULL 2014-01-02 → 2026-06-19, NAV 50B, park 0, AUDIT_END 06-19, threads=1, mergesort, LAG data vintage 10-29. Các số lấy từ `logs/metrics_L1.log`, `logs/metrics_L2.log` và `logs/bootstrap.log` (circular, L=21, B=4000, seed 12345). Script `metrics.py` tái lập đúng engine trên L2 cũ (23,44 / 16,85 / 29,80).

| Chân | LIQ | ADV | đầu | CAGR | Sharpe | MaxDD | IS / OOS | 2015 | LAG 2015Q4 | Boot CAGR5 | **DD5** | P(DD<−30%) | md5 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C_L1 (=L1 cũ) | off | bq | pin0% | 22,31% | 1,94 | −16,2% | 20,08 / 24,33 | 19,4% | 21,8B | 15,1% | −23,6% | 0,5% | `2f7739b5` |
| L1F | off | fill | pin0% | 21,74% | 1,89 | −16,2% | 18,97 / 24,30 | 18,4% | 21,6B | 14,5% | −24,1% | 0,6% | `21fb1fd6` |
| L1P | off | pit | pin0% | 21,77% | 1,89 | −16,2% | 19,25 / 24,08 | 17,2% | 21,6B | 14,5% | −24,2% | 0,7% | `3a134bf1` |
| C_L2 (=L2 cũ) | lag | bq | pin0% | 23,44% | 1,82 | −16,3% | 16,85 / 29,80 | 5,7% | 14,2B | 15,2% | −27,7% | 2,5% | `5ae929c6` |
| L2F | lag | fill | pin0% | 23,38% | 1,81 | −16,3% | 16,66 / 29,87 | 5,4% | 16,6B | 15,1% | −27,7% | 2,5% | `be578fee` |
| **L2P** | lag | pit | pin0% | **23,32%** | 1,81 | −16,6% | 16,38 / 30,04 | 5,1% | 16,4B | 15,1% | **−27,7%** | 2,6% | `87834e98` |
| C_L1 (=L1 cũ) | off | bq | pin1M | 25,87% | 2,21 | −13,7% | 23,42 / 28,11 | 22,9% | 22,9B | 18,5% | −20,6% | 0,1% | `fe398133` |
| L1F | off | fill | pin1M | 25,28% | 2,17 | −13,7% | 22,29 / 28,04 | 21,7% | 22,7B | 17,9% | −21,0% | 0,1% | `7b13caf9` |
| L1P | off | pit | pin1M | 25,05% | 2,15 | −13,8% | 21,96 / 27,92 | 20,6% | 22,2B | 17,6% | −21,3% | 0,2% | `8cdc5018` |
| C_L2 (=L2 cũ) | lag | bq | pin1M | 27,11% | 2,06 | −15,2% | 20,12 / 33,88 | 8,7% | 14,4B | 18,6% | −25,2% | 0,8% | `52b39597` |
| L2F | lag | fill | pin1M | 27,02% | 2,05 | −15,2% | 19,84 / 33,99 | 8,3% | 17,4B | 18,5% | −25,1% | 0,9% | `f1947843` |
| **L2P** | lag | pit | pin1M | **26,85%** | 2,04 | −15,7% | 19,80 / 33,69 | 8,1% | 17,2B | 18,4% | **−25,3%** | 1,0% | `6646c65f` |

Ghi chú:
- **Lỗ NULL bịt được phần lớn exposure nhưng gần như không bù được lợi suất.** Exposure LAG 2015Q4 hồi từ 14,2B lên 16,4–16,6B, tức khoảng 1/3 khoảng cách tới 21,8B của L1. Lợi suất năm 2015 thì không hồi.
- **Bootstrap chỉ in 1 chữ số thập phân.** Vì vậy |ΔDD5| < 0,1pp không đọc được.

## 4. Selfcheck và control

- **Control trùng byte (4/4):** code mới với `LAG_ADV_SRC=bq` cho `2f7739b5`, `fe398133`, `5ae929c6`, `52b39597`, đúng bằng L1/L2 cũ. Tức knob ở mặc định không đổi một byte nào.
- **Selfcheck 0 VND (12/12 chân):** mọi chân in `[selfcheck LAG] cash-flow identity max err = 0 VND; final NAV identity err = 0 VND`, EXIT=0.
- **Tài nguyên:** RSS tối đa 4,37G mỗi chân, chạy 4 chân song song, swap 0.
- **Số phép thử:** 8 cấu hình mới + 4 control. Trục do brief định trước, KHÔNG chọn lựa theo kết quả. Không đọc Δ nào thành edge.

## 5. Có dùng làm mặc định được không

**Đề xuất: `LAG_ADV_SRC=pit`, mặc định đi cùng `LIQ_ZERO_BLOCK=lag`.** Lý do:
- **pit khớp định nghĩa live.** `trading_bot/due_diligence.py::adv_vnd`, được `cap_lag_orders` (`trading_bot/plan.py:586`) gọi, lấy `Volume_3M_P50 × COALESCE(Price, Close)` của dòng MỚI NHẤT ≤ asof, tức dòng t−1. Đó chính là trung vị 60 dòng t−60..t−1 × giá t−1, đúng công thức pit. Bản `bq` hiện tại thì gồm cả ngày fill.
- **pit không phụ thuộc lỗ NULL lịch sử của BQ.**

Điều kiện trước khi đổi:
1. **quant-skeptic CONFIRMED** trên job này, nhất là phép phân rã ở §1.4 và kết luận "fill ảo của L1".
2. **Merge cùng lúc với nhánh A** (`feat/live-gap-exec-A-20261112`, chưa merge) và thêm 1 commit knob vào nhánh đó. Rollback `LAG_ADV_SRC=bq` đã chứng minh trùng byte.
3. **Khai báo lệch còn lại so với live.**
   - Ở ngày `Volume_3M_P50` NULL, live CHẶN (`adv_vnd` trả "thiếu Volume_3M_P50"), còn engine pit vẫn có ADV. Live hiện có tỷ lệ NULL 0,21% (2026), nên phần này không đáng kể.
   - Live có thêm cổng stale `LAG_ADV_MAX_STALE_DAYS`; engine không mô phỏng cổng này.
4. **Chưa đo:** độ nhạy `min_periods` (20, chưa sweep). ADV của book BAL/ETF (`liq_map`, `pt_v23_audit_2014.py` khoảng dòng 1057) vẫn dùng cột BQ, không đổi.
5. **Neo sizing do user quyết riêng.** Đổi mặc định không làm DD5 sàn đổi (−27,7% cả 3 nguồn ADV).

## 6. Đính chính blast radius (REPORT Luồng A §5)

Câu cũ ở REPORT Luồng A: "`pt_v22_dt5g.py` … không có knob ⇒ không đổi hành vi (vẫn kiểu off)". **Câu này SAI.**
- **pt_v22 đã chặn kiểu `lag` từ 10/11.** `pt_v22_dt5g.py:489` hardcode `"liquidity_require_positive": True` cho LAG từ commit `32d65bbf6` (2026-11-10, user duyệt). Mặc định của A vì thế không đổi hành vi pt_v22; nó vốn đã chặn ADV ≤0 hoặc thiếu.
- **pt_v22 chạy trong cron.** Nó là bước [12] của `papertrade_daily.sh` (cron 15:30 ICT), paper forward từ 2026-06-11.
- **Lỗ NULL 2015–16 không chạm tới pt_v22.** pt_v22 dùng `Volume_3M_P50` có `ffill(limit=5)` (`:394`). Tỷ lệ NULL năm 2026 là 0,21% số dòng có giao dịch, và `ffill` còn giảm thêm.

Đã ghi chú đính chính vào REPORT Luồng A §5.

## 7. Tái lập

```bash
A2=mike/agents/Taylor/research/live_gap_exec_A2
# worktree (sparse, không data/): /home/trido/thanhdt/wt-livegapA2-1113 (nhánh feat/live-gap-exec-A2-20261113 = main f210c726b + 4f7609c34)
#                                 /home/trido/thanhdt/wt-livegapA2-1113-r (research/live-gap-A2-r-20261113 = 49cd913ae + 770393ce2, có IDLE_CARRY_TIER)
$DNA_PYEXE $A2/adv_validate.py                       # bước 1
cd $A2 && xargs -P4 -L1 ./run_leg.sh < batch.txt     # 12 chân; sb/m, sb/r dựng như make_sandboxes.sh Luồng A (vintage 10-29)
$DNA_PYEXE metrics.py ledgers/*.csv
$DNA_PYEXE decomp.py ledgers/*_exp_C_L1_off_* ledgers/*_exp_L2P_off_* [2015-07-01 2016-06-30]
cd /home/trido/thanhdt/WorkingClaude && $DNA_PYEXE bootstrap_nav.py <ledger.csv>
```

Env cố định nằm trong `run_leg.sh`: cache `asof20260729_postrestate`, `BQ_CACHE_THREADS=1`, NAV 50B, `ETF_LIQ=custompitg`, CA snapshot 0927, namecap/yieldcombo, `PARK_STATES=3:0.0`. Dòng `EXIT=… MD5=… CODE=…@sha` nằm cuối mỗi `logs/<TAG>.log`.

md5 của script: `adv_validate.py` c60f4c3b · `patch_advsrc.py` 78309928 · `metrics.py` 553913a5 · `decomp.py` 5fdb92cb · `run_leg.sh` 31ae0bb6.

**Chưa làm:**
- Chưa pin vào `data/pinned_ledgers/`, chưa ghi `results_registry.md` (cần duyệt).
- Chưa chạy L3 (adj v2) với ADV sạch.
- Chưa có DSR/PBO riêng cho job này.
- Hai worktree và các commit research chưa merge.
