# `rating_8l.py` lens `ps`: đổi cơ sở giá `Close` → `Price` (PIT)

**Job** `Taylor_20260802_081308` · 2026-08-02 · Taylor
**Phần 2 của saga** `kb/incidents/2026-08/2026-08-02-pe-price-close-adjustment-saga.md`
(phần 1 = gỡ `_pe_adj_factor`, commit `beec96c`, job `Taylor_20260802_063752`).
**Bằng chứng**: `mike/agents/Taylor/exp_ps_basis/` (script + CSV + log, tự chạy lại trong job này).
**Interpreter**: `/home/trido/thanhdt/wc_venv/bin/python` (pandas 3.0.2 — đúng pin registry).

## Tóm tắt

Lens `ps` tự tính vốn hoá bằng `Close` (giá **đã điều chỉnh** hồi tố) nhân `OShares` (số cổ phiếu
**PIT** của chính quý đó) — **trộn 2 cơ sở**. Đúng phải là `Price` (giá thô, PIT). Đây là cùng họ
lỗi với `_pe_adj_factor` nhưng **ngược chiều**: `PE` vốn ĐÃ ở cơ sở `Price` nên nhân thêm
`Price/Close` là sai; còn `ps` **tự dựng** vốn hoá nên phải tự chọn đúng cơ sở.

**Tác động LIVE = 0** (hôm nay `Price == Close` cho 859/859 mã — hệ số điều chỉnh ≡ 1 ở ngày mới
nhất). Tác động chỉ có khi tính lùi lịch sử. Không đụng rating 8L (1-5), không đụng bảng
`fa_ratings_8l`, không đụng bất kỳ selector giao dịch nào ⇒ **ZERO NAV impact**.

## Bước 1 — Code + khảo cổ git

`rating_8l.py:530-535` (trước sửa):
```python
_ttm_rev = out[[f"Revenue_P{i}" for i in range(4)]].sum(axis=1, min_count=1)
out["ps"] = np.where((_ttm_rev > 0) & out["OShares"].notna() & out["Close"].notna(),
                     (out["Close"] * out["OShares"] / _ttm_rev), np.nan)
out["sales_yield"] = np.where(out["ps"] > 0, (1.0 / out["ps"]).round(4), np.nan)
```

Pickaxe `git log -S'out["ps"] = np.where' -- rating_8l.py` → **chỉ 1 commit**: `c9cc670`
(2026-06-21, "Checkpoint: code + docs baseline before data/secrets reorg") ⇒ lens `ps` ra đời
trước mốc checkpoint đó, **không có commit nào giải thích ý đồ chọn `Close`**. Khác phần 1: ở đó
có comment SAI khẳng định `PE_stored = Close_adj/EPS`; ở đây comment gốc chỉ nói *"current-price PS
= mktcap/TTM-revenue"* — tức ý đồ ĐÚNG (giá hiện hành = giá thô), chỉ **chọn nhầm cột**.

### Phạm vi lan toả (grep toàn repo)

| Đường | Có đi qua `ps` không | Bằng chứng |
|---|---|---|
| Rating 8L (1-5) trong `rating_8l.py` | **KHÔNG** | `rate_row`/`core_score`/`moat_tag`/`redflag`/`rate_bank`/`rate_securities`/`rate_insurance` (dòng 187-429) **0 tham chiếu** `ps`/`sales_yield`/`PS`; hơn nữa `out["ps"]` gán ở dòng **545**, sau khi `rate_row` đã apply ở dòng **500** ⇒ bất khả về mặt cấu trúc |
| BQ `tav2_bq.fa_ratings_8l` | **KHÔNG** | writer là `rating_8l_history.py` (`CREATE OR REPLACE`, dòng 320) — nó có `rate_row` **bản sao riêng** (dòng 252), **không import** `rating_8l.py`, và chỉ ghi `ticker/time/route/rating/tier` (không có cột value nào) |
| BQ `tav2_bq.fa_ratings` | **KHÔNG** | writer `refresh_fa_ratings.py` không tính `ps` (grep 0 hit) |
| `sales_yield` / `value_score_v3` ở script khác | **KHÔNG** | grep toàn repo: chỉ `rating_8l.py` (+ thư mục thực nghiệm của chính Taylor) |
| Screener human-facing (`value_score`/`zone`/top30/buynow) | **CÓ** (qua `ps_pct` → `value_score_v3`) | dòng 749, 793, 813, 885 |

⇒ Nhiễm chỉ ở **màn hình lọc human-facing của chính ngày chạy** — giống hệt kết luận phần 1.

## Bước 2 — Phép sửa

Đổi `Close` → `Price` (cả trong guard `.notna()` lẫn công thức), thêm comment cảnh báo **ngược
chiều** dẫn số liệu + job + file bằng chứng. `git diff` = đúng 2 dòng code + 12 dòng comment,
không chạm gì khác.

Kiểm coverage trước khi đổi (chống rủi ro "sửa đúng nhưng mất dữ liệu"): trên `ticker_1m@MAX(time)`
`Price` non-null **859/859**, `Close` non-null 859/859, `Close IS NOT NULL AND Price IS NULL` = **0**
⇒ không mất mã nào. (`div_yield` dòng 544 vốn đã dùng `Price` — nhất quán nội bộ file.)

## Bước 3 — Self-check 2 chiều (+ 2 negative control)

Sandbox `WORKDIR_8L=/tmp/r8l_ps_sbx_8JkT/{BEFORE,AFTER,PERTURB,PERTURB2}`, mỗi leg copy đủ 4 CSV
input (`moat_tags`, `forensic_flags`, `bank_lens_v3`, `power_lens`). Production **không bị chạm**:
`data/rating_8l{,_top30,_buynow,_screener}.csv` giữ nguyên mtime `2026-07-30 19:20`; `git status`
chỉ có `rating_8l.py`.

**(3a) Parity ngày gần đây — PASS.** Snapshot `ticker_1m` = 2026-07-31, `Price == Close` **859/859**,
`max|Price/Close − 1| = 0.000000`.

| File | Cột khác BEFORE vs AFTER |
|---|---|
| `rating_8l.csv` (859×39) | **IDENTICAL — 0 cột, 0 mã** |
| `rating_8l_top30.csv` (30×43) | **IDENTICAL** |
| `rating_8l_buynow.csv` (72×41) | **IDENTICAL** |
| `rating_8l_screener.csv` (104×28) | **IDENTICAL** |

(So sánh dùng sentinel `<NA>` cho cột chuỗi — bài học phương pháp của job 063752: pandas 3
StringDtype trả `pd.NA` khi `astype(str)` và `pd.NA != pd.NA` ⇒ đếm nhầm là "khác".)

**⚠️ "Identical 100%" cũng đúng khi harness hỏng — nên phải bác bỏ khả năng đó.** 2 negative control:

| Nhiễu loạn (thay cho phép sửa thật) | Kết quả | Ý nghĩa |
|---|---|---|
| NC1: `ps × 1.5` (đều tay) | `sales_yield` khác **816/859** (max 21.42); screener IDENTICAL | Harness BẮT ĐƯỢC diff thật. Screener không đổi là **đúng kỳ vọng**: nhân vô hướng đều tay bảo toàn thứ hạng chéo ⇒ `ps_pct` không đổi |
| NC2: `ps × (1 + 1.5·i/n)` (đổi hạng) | `ps_pct` 59, `value_score_v3` 39, `value_score` 25, `value_pct` 58, **`zone` 2 mã (DHC, MBB)**; `rating` **vẫn IDENTICAL** | Harness bắt được cả đường `ps → ps_pct → value_score → zone`, và xác nhận **thực nghiệm** rằng `rating` miễn nhiễm với `ps` |

⇒ Kết quả "0 khác" của phép sửa thật là **thật**, không phải harness mù.

**(3b) Positive control dữ liệu cũ — PASS (tự đo lại từ BQ, không copy số job trước).**
Script `exp_ps_basis/measure_ps_basis.py`.

*Phép định danh* — `PS` lưu trong `ticker_financial` nằm ở cơ sở nào? (2014-01-01 → 2016-12-31,
`ticker_financial ⋈ ticker` theo `(ticker,time)`, `n = 7.377`):

```
Price·OShares/Rev_ttm khớp PS lưu (sai số <2%):  98,9%   | sai số tương đối trung vị: 0,0000
Close·OShares/Rev_ttm khớp PS lưu (sai số <2%):  11,8%   | sai số tương đối trung vị: 0,5261
```

*Tái lập đúng công thức `rating_8l` trên 3 ngày cắt* (`ticker` ⋈ báo cáo tài chính as-of gần nhất):

| Ngày | n | F=Price/Close (trung vị) | \|sales_yield lệch\| trung vị | Spearman(fix,bug) | Top-30 rẻ nhất đổi |
|---|---|---|---|---|---|
| 2014-06-30 | 589 | 2,308 | **56,7%** | 0,889 | **15/30** |
| 2015-06-30 | 620 | 2,074 | 51,8% | 0,907 | 10/30 |
| 2016-06-30 | 702 | 1,906 | 47,5% | 0,909 | 13/30 |

⇒ Trên dữ liệu cũ, cơ sở sai bóp méo trục PS tới mức **đảo 1/3 danh sách rẻ nhất**. Sửa xong ≈0
hôm nay **không phải** vì sửa vào chỗ vô hại.

> **Đối chiếu với job trước (không mâu thuẫn):** job `Taylor_20260802_063752` báo lệch
> **90,6-131,3%** — đó là `sy_bug/sy_fix − 1 = F − 1`; số ở đây là `|sy_fix/sy_bug − 1| = 1 − 1/F`.
> Cùng một sự kiện, khác mẫu số. Kiểm: F=2,308 ⇒ F−1 = 130,8% ≈ 131,3% ✓ và 1−1/F = 56,7% ✓.
> Chênh lệch nhỏ còn lại (98,9% vs 99,7%; n 7.377 vs 7.321; 10-15/30 vs 11-15/30) là do bộ lọc
> khác nhau vài dòng (job này thêm điều kiện `Price > 0`), **không đổi kết luận**.

**(3c) `rate_row()` / `fa_ratings_8l` — KHÔNG bị ảnh hưởng** (kiểm riêng cho `ps`, không giả định
giống PE): 3 lớp bằng chứng độc lập — (i) AST: 7 hàm rating dòng 187-429 có **0** tham chiếu
`ps`/`sales_yield`/`PS`; (ii) cấu trúc: `out["ps"]` gán dòng 545 > `rate_row` apply dòng 500;
(iii) thực nghiệm: cột `rating` IDENTICAL cả ở phép sửa thật **lẫn** ở NC2 (nhiễu loạn đổi hạng
mạnh). Bảng `fa_ratings_8l` do `rating_8l_history.py` dựng bằng `rate_row` bản sao riêng và chỉ
ghi `ticker/time/route/rating/tier` ⇒ không có đường nào cho `ps` vào.

## Bước 4 — Quant-skeptic

Xem event `verification` cùng `trace_id=Taylor_20260802_081308` trên bus.

## Số không đổi

Không wire gì mới, không đổi selector/gate nào ⇒ **không khai N-trials/DSR/PBO**. `1/PE` IC
**+0,125**, R3 **27,60%** giữ nguyên (không nằm trên đường tính của `ps`).
