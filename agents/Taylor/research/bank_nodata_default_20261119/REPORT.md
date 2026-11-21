# bank-nodata: mặc định LIVE 3 → 4 (fail-closed) — job Taylor_20261119_095521, 19/11/2026

## Kết luận (đọc trước)

1. **Đã sửa xong trong worktree, CHƯA merge.** Nhánh `session/bank-nodata-fail-closed-20261119`,
   worktree sparse `/home/trido/thanhdt/WorkingClaude/wt-bank-nodata-20261119` (repo gốc `/home/trido/thanhdt`).
   `rating_8l.py:420` `return 3, "bank-nodata"` → `return 4, "bank-nodata"` (+4 dòng comment). Thêm
   selfcheck `rating_8l_bank_nodata_selfcheck.py`. **Commit `d0a14445e`** (+135/−1).
2. **Tái sinh A/B (code cũ vs mới, CÙNG input, ra /tmp): ĐÚNG 9 mã đổi, chỉ cột `rating`, 3→4**:
   ABB, BAB, BVB, NVB, PCB, PGB, SGB, VAB, VBB. 773/773 dòng khớp ở mọi cột khác. ĐẠT điều kiện.
3. **⚠️ Thay đổi này KHÔNG chạm đường tiền LAG / BAL / custom30V.** Cả ba (và cổng tầng ORDER
   `filter_lag_rating_orders`) đọc `tav2_bq.fa_ratings_8l` (do `rating_8l_history.py` sinh), KHÔNG đọc
   `data/rating_8l.csv`. Mà `rating_8l_history.override_current_bank_aq` ĐÃ loại mọi dòng live có nhãn
   `bank-nodata` từ 09-27 (khớp CHUỖI, không theo số) ⇒ `fa_ratings_8l` giữ nguyên proxy ROE.
   **Hệ quả user cần biết:** trong `fa_ratings_8l` hôm nay **ABB=3, PCB=3, VAB=3, VBB=3, KLB=2** (qua
   cổng ≤3), BAB/BVB/PGB=4, NVB/SGB=5. Tức là sau khi merge, ABB/PCB/VAB/VBB/KLB VẪN mua được qua
   LAG/BAL/custom30V — nhưng bằng hạng proxy ROE từ `ticker_financial` (số thật), không phải số 3 bịa.
   Nếu user muốn đường tiền cũng fail-closed cho bank thiếu lens ⇒ đó là **một quyết định riêng**
   (đổi `rating_8l_history`), chưa làm, chưa được duyệt.
4. **Vị thế thật: 0/9 mã đang giữ** ở cả SpaceX và ZaloPay (dnse_raw 18/11, lọc theo account). 0 plan
   tháng 11 nào chứa 9 mã. ⇒ không có lệnh/vị thế nào bị ảnh hưởng ngay.
5. Ai thực sự đổi hành vi sau merge (đều display/discretionary, không đặt lệnh tự động): discretionary
   funnel (`RATING_MAX=3`), `rating_8l_screener.csv` (rớt ABB/BVB/NVB/VAB), cột R Telegram, sector lens.

## 1. Thay đổi code

```
WorkingClaude/rating_8l.py | 6 +++++-   (git diff --stat trong worktree)
-    if not b: return 3, "bank-nodata"
+    # FAIL-CLOSED 2026-11-19 (user duyệt, job Taylor_20261119_095521): ... (4 dòng comment)
+    if not b: return 4, "bank-nodata"
```
- Nhãn `"bank-nodata"` giữ NGUYÊN chuỗi — `rating_8l_history.py:552` (`NODATA_NOTES`) khớp theo chuỗi này.
- `"bank-noROE"` (ROE null) **chưa đổi** — ngoài phạm vi duyệt. Hôm nay 0 mã dính nhãn này (A/B run).
- Lưu ý fail mode: nếu `data/bank_lens_v3.csv` không đọc được (`rating_8l.py:551-556`), `BANKD` rỗng ⇒
  MỌI mã BANK thành 4 (trước: 3). Đây là chiều an toàn, nhưng đáng biết khi đọc log "bank lens load fail".

## 2. Rà mọi chỗ dùng nhánh / nhãn (GNU grep, không srcwalk)

Lệnh: `grep -rn "bank-nodata\|bank_nodata" --include=*.py --include=*.sh /home/trido/thanhdt/WorkingClaude`
(bỏ `wt-*`, `research/`, archive) + `grep -rnE "nodata|noROE"` trong `mike/bin`, `mike/trading_bot`.

| Nơi | Vai trò | Cần sửa? |
|---|---|---|
| `rating_8l.py:420` | nhánh được đổi | ĐÃ sửa |
| `rating_8l_history.py:536-557` | override bank AQ, loại nhãn nodata/noROE | Không — khớp chuỗi, rating 4 vẫn bị loại (selfcheck mục 4) |
| `rating_8l_history_bank_aq_selfcheck.py:194-241` | test override với rating=3 | Không — PASS nguyên trạng |
| `release_8l*/`, `8l_package/` | bản đóng gói đã phát hành | Không đụng (artifact lịch sử) |
| `deploy_golive_dt5g_v4/golive_recommend_v23.py:781-799` | BAL weak flag, đọc `fa_ratings_8l` | Không ảnh hưởng |
| `lag_rating_filter.py:62` | gate LAG tầng tín hiệu, `fa_ratings_8l` | Không ảnh hưởng |
| `custom_basket.py:729`, `custom30_history.py:36` | custom30V gate ≤3, `fa_ratings_8l` | Không ảnh hưởng |
| `mike/bin/discretionary_candidate_funnel.py:177,450,811,1156` | đọc `rating_8l.csv`, `rating<=3` | Đổi hành vi (đúng ý fail-closed) |
| `mike/bin/sector_valuation_lens.py`, `telegram_run_daily.sh`, screener | hiển thị | Đổi hiển thị |
| `dna_report*` | grep 0 hit `bank-nodata`/`rating_8l.csv` (chỉ `nodata` của dòng thanh khoản — khái niệm khác) | Không |

Không có chỗ nào so sánh "rating==3 và nodata" ngoài override history ⇒ không lệch live vs history.

## 3. Selfcheck (2 TZ)

| Lệnh | Kết quả |
|---|---|
| `env -u TZ ... rating_8l_bank_nodata_selfcheck.py` (MỚI) | PASS 14 ok / 0 fail |
| `TZ=Asia/Tokyo ... rating_8l_bank_nodata_selfcheck.py` | PASS 14 ok / 0 fail |
| `rating_8l_history_bank_aq_selfcheck.py --all-tz` (có sẵn) | no TZ / UTC / America/New_York: PASS rc=0 cả 3 |

Selfcheck mới kiểm: (1) mã vắng lens ⇒ `(4,"bank-nodata")`, >3; (2) 6 ca tổng hợp nhánh có dữ liệu
(1/2/3/4/5/noROE=3) y hệt bản đóng băng HEAD; (3) **18 mã của `bank_lens_v3.csv` thật: kết quả mới ==
HEAD, 0 khác**; (4) override history vẫn loại dòng live 4/bank-nodata, vẫn áp dòng có lens; (5) mutation
trả nhánh nodata về 3 ⇒ test 1 bắt được. Chạy với `PYTHONPATH=/home/trido/thanhdt/WorkingClaude`
(module phụ không có trong sparse) và `$DNA_PYEXE`. Selfcheck `rating8l_eff_guard`/`rating8l_icb_pit`
KHÔNG chạy — chỉ kiểm `rating_8l_history.py`, file không đổi (§23 theo phạm vi).

## 4. Tái sinh ra file tạm — so từng dòng

Cách: 2 WORKDIR tạm `/tmp/r8l_ab_20261119/{old,new}` (copy `moat_tags`, `forensic_flags`,
`bank_lens_v3`, `power_lens`), code cũ = `git show HEAD:WorkingClaude/rating_8l.py`, cùng chạy
`WORKDIR_8L=<tmp> OSHARES_RECONCILE=0 $DNA_PYEXE rating_8l.py` (cả hai chân tắt đối soát OShares để
không ghi `data/oshares_reconcile_log.csv` thật; OShares chỉ nuôi `ps`, không nuôi rating).
`data/rating_8l.csv` thật KHÔNG bị ghi (mtime vẫn 18/11 19:20).

- old vs new: 773 vs 773 dòng, 0 mã thêm/bớt; cột khác duy nhất = `rating`, đúng 9 mã trên, 3→4.
- `rating_8l_buynow.csv`, `rating_8l_top30.csv`: giống hệt byte. `rating_8l_screener.csv`: 100 → 96 dòng (rớt ABB, BVB, NVB, VAB).
- new vs bản live 18/11 (794 dòng, input BQ khác ngày): 10 mã khác rating = 9 mã trên + **FIR** (5→4,
  RE asset-play). FIR khác ở CẢ chân old ⇒ là trôi dữ liệu 18→19/11, không do thay đổi này.

## 5. Tác động tiền

**Vị thế thật** (`data/execution_logs/dnse_raw_2026-11-18.jsonl`, bản `positions` cuối, lọc
`account_no`): SpaceX = FPT, HT1, MBB, MCH, NNC, VGS, VIB, VPB; ZaloPay = thêm DGC. **0/9 mã**.
`grep` 9 mã trong `data/trade_plans/plan_*_2026-11-*.json`: 0 file.

**Cổng tầng ORDER** `trading_bot/plan.py:845 filter_lag_rating_orders`:
- Chỉ xét lệnh `book=="LAG" and side=="buy"` (`plan.py:879-880`, lọc ở `:882`, loại ở `:910`). Lệnh
  BÁN và lệnh book khác đi thẳng qua ⇒ đang giữ mã rating 4 thì **không bị ép bán, không bị chặn bán**.
- Nguồn rating = `lag_filter_low_rating` → `tav2_bq.fa_ratings_8l` (`lag_rating_filter.py:62`,
  `time <= asof`, dòng mới nhất). **Không đọc `rating_8l.csv`** ⇒ đổi live 3→4 không đổi kết quả cổng.
- custom30V: `custom_basket.py:729` đọc `fa_ratings_8l`, `gate_rating=3` (`custom30_history.py:36`).
  Park/JIT-unpark (`mike/bin/compute_jit_unpark.py:107`) không tự đọc rating, dựa vào các cổng trên.
- BAL weak-flag: `golive_recommend_v23.py:781` đọc `fa_ratings_8l`.

`fa_ratings_8l` hiện hành (bq, `time <= 2026-11-19`, dòng mới nhất):
ABB 3 · BAB 4 · BVB 4 · KLB 2 · NVB 5 · PCB 3 · PGB 4 · SGB 5 · VAB 3 · VBB 3.

## 6. ΔNAV mô tả trên ledger pin R3 (KHÔNG phải backtest wire)

Ledger: `data/pinned_ledgers/2026-09-28__R3-anchor-pin0pct-sexies__4707bcbe.csv.gz` (pin0%, sàn) và
`2026-09-28__R3-pin1M-dau-TRAN-dai__bcd0469f.csv.gz` (pin1M, trần). Lợi suất holding = (tiền bán − phí)/(tiền mua + phí) − 1.

| Quy ước | Holding | Lợi suất TB | Tổng P&L | Chi tiết |
|---|---|---|---|---|
| pin0% | 3 (17 lệnh TX) | −2,26% | −1,003 tỷ | NVB LAG 10/2021 +4,25% · PGB LAG 10/2022 +1,45% (bỏ dở) · BVB BAL 01/2026 −12,48% |
| pin1M | 4 (20 lệnh TX) | −1,10% | −0,701 tỷ | như trên + ABB BAL 08/2025 +2,38% |

ABB còn là thành viên custom30V ở 3 kỳ (2021-07, 2021-10, 2026-01; `rating=2` trong ledger).
**ΔNAV do thay đổi này trên ledger = 0**: mọi lệnh trên được cấp phép bởi `fa_ratings_8l`, nguồn mà
thay đổi live không chạm (mục 5). Bảng trên chỉ cho biết quy mô lịch sử của 9 mã trong R3 (nhỏ: tổng
P&L ≈ ±0,2% NAV mỗi holding), không phải hiệu ứng của việc đổi mặc định.

## 7. Còn treo / cho Mike + arch-reviewer

- Commit trong worktree sparse dùng `PRE_COMMIT_ALLOW_NO_CONFIG=1` ⇒ **gate pre-commit KHÔNG chạy**.
  Cần chạy lại pre-commit khi merge.
- Quyết định riêng (chưa làm): có muốn `fa_ratings_8l` cũng fail-closed (≥4) cho bank vắng
  `bank_lens_v3` không — hiện ABB/PCB/VAB/VBB=3, KLB=2 vẫn qua cổng tiền bằng proxy ROE.
- `bank-noROE` vẫn trả 3 — 0 mã hôm nay; có muốn đồng bộ về 4 không.
