# Checkpoint paper-program `vol_scale_chase_cap` — kiểm bằng dữ liệu thật

- **Job**: `Taylor_20260804_091700` · **Ngày**: 2026-08-04 · **Owner**: Taylor
- **Chương trình**: Vol-scale buy chase-cap (patch#3) — `cap_pct = clamp(k·rvol_20d, static 1,5%, ceil 4,0%)`, k=2,0
- **Trạng thái sau kiểm**: gate 1-3 **PASS**, gate 4 **BỊ CHẶN CẤU TRÚC**, gate 5 (user sign-off) chờ user.
- **KHÔNG bật live. KHÔNG đổi production.** (`git diff` chỉ chạm registry + charter, đều thuộc `mike/kb/`.)

## 0. Tiến độ evidence — mốc ĐÃ ĐỦ

| | |
|---|---|
| Mục tiêu | 10 phiên evidence (executor chạy thật trên paper main), đếm từ 2026-07-07 |
| Thực tế | **13 phiên có lệnh BUY thật**: 07-07, 07-10, 07-13→07-17, 07-20→07-24, 07-27 |
| Tổng lệnh BUY | **80 lệnh** (6-7 lệnh/phiên, rổ ACB/FPT/HDB/HPG/MBB/VNM) |
| Phiên có journal nhưng 0 BUY | 07-08, 07-09, 07-30, 07-31, 08-04 |

⚠️ **Luồng evidence ĐÃ DỪNG từ 2026-07-28**: probe harness bật netting nội bộ — log
`run_bot_main_*.log` từ 07-28 trở đi cho `NET <mã> (INTERNAL_ONLY): mua = bán → 0 lệnh ra broker`.
Từ đó **0 lệnh BUY chạm executor**, nên chương trình này (và `fill_timing`, cùng phụ thuộc lệnh BUY
paper main) không tích luỹ thêm bằng chứng được nữa. Đây là phát hiện phụ, cần Winston/Mike xử lý
nếu muốn giữ luồng evidence sống.

## 1. Gate 1 — Executor-path stress → **PASS** (chạy lại hôm nay)

Không tin báo cáo cũ; chạy lại `mike/agents/Taylor/stress_vol_scale_chase_cap.py` trên code hiện tại:
`RESULT: PASS` — 14 assert (config wiring 4 · WIDEN clamp-to-ceil 2 · MONOTONE 1 · FAIL-SAFE
rvol absent/0/<0 3 · LIMIT-PRICE 2 · NEG-control live 2). Lần chạy này **đi thật qua nhánh fail-safe**
(`gap_adaptive: no chunks in data/bq_cache/ticker_prune — fail-safe`) rồi vẫn trả static.

*(Ghi chú: registry cũ ghi "15/15"; đếm thật trên output hôm nay là 14 assert. Kết quả PASS không đổi,
chỉ chỉnh lại con số cho đúng.)*

## 2. Gate 2 — "Paper sạch: wiring đúng trên quote thật + fail-safe khi thiếu rvol cache" → **PASS**

Tái dựng đúng đường code `Executor._load_gap_ref_data` (đọc `data/bq_cache/ticker_prune/*.parquet`,
`Close` < plan_date, `tail(22)` → std 20 return) rồi so giá đặt thật trong journal với hai chân trần:

| Chỉ số | Kết quả |
|---|---|
| Lệnh BUY đo được | 80 / 80 (khớp `parent_id` với `plan_main_<date>.json`) |
| `rvol_20d` nạp thành công | **80/80** (0 lần rơi fail-safe) |
| `volcap` luôn trong `[1,5% ; 4,0%]` | ✅ mọi lệnh (dải quan sát 1,61% → 3,74%) |
| Chase% cao nhất quan sát | **+1,95%** (< ceil 4,0%) |
| Trần thực sự chạm | 3/80 lệnh |

→ Wiring sống và đúng trên quote thật, monotone-safe, chưa lần nào chạm ceil.

**Caveat trung thực**: nhánh *fail-safe khi thiếu rvol cache* **chưa từng xảy ra trên paper** (cache
luôn đủ dữ liệu). Bằng chứng cho nửa này đến từ stress harness (chạy qua `Executor` thật), không
phải từ một phiên paper. Không thể ép nó xảy ra trên paper mà không cố tình phá cache — không làm.

## 3. Gate 3 — "Không can thiệp NORMAL-path ngày non-gap" → **PASS (có caveat, chờ user phân xử)**

**(a) Cô lập code**: `grep -rn "_buy_chase_pct" trading_bot/ bin/ mike/bin/` → đúng **1 call-site**
(`trading_bot/executor.py:426`, nhánh BUY của `_limit_price`). Sell-path, dip/cross adaptive,
gap-adaptive, EXTREME-regime: không chạm.

**(b) Đo thực nghiệm** — so giá đặt thật vs giá mà chân static (1,5%) sẽ cho:

- **77/80 lệnh (96,3%) giống hệt chân static.**
- 3 lệnh lệch:

| Ngày | Mã | ref | giá đặt | giá static-cap | lệch | trần vol có bind? |
|---|---|---|---|---|---|---|
| 2026-07-07 | MBB | 25.300 | 25.700 | 25.650 | **+50đ (+0,19%)** | có (clip đúng vol-cap) |
| 2026-07-07 | HDB | 27.200 | 27.650 | 27.600 | **+50đ (+0,18%)** | có (clip đúng vol-cap) |
| 2026-07-16 | ACB | 23.100 | 23.550 | 23.400 | **+150đ (+0,64%)** | không — cross ở ask, ask nằm giữa static-cap và vol-cap (23.600) |

Bối cảnh 3 ngày đó (giá điều chỉnh, `ticker_prune`):

| | gap mở cửa | lợi suất cả phiên |
|---|---|---|
| MBB 07-07 | +0,37% | **+1,77%** |
| HDB 07-07 | −0,37% | **+1,84%** |
| ACB 07-16 | −0,65% | **+2,81%** |

→ Trần chỉ nới **khi giá thật đã chạy quá +1,5% trong phiên**; **không có ca nào lệch trong ngày giá
nằm gọn trong ±1,5%**. Chi phí trường hợp xấu nhất quan sát được = +0,64% giá vào, có ceiling 4% chặn.

⚠️ **Điểm cần user phân xử**: chữ trong tiêu chí là *"ngày non-gap"*. Cả 3 ngày trên **không** gap ở
mở cửa (gap −0,65%..+0,37%) mà chạy trong phiên. Đọc theo **nghĩa đen** → 3 ca này là "can thiệp trên
ngày non-gap" ⇒ gate FAIL. Đọc theo **ý đồ** (patch chỉ được đổi hành vi khi trần thực sự liên quan)
⇒ PASS. Tôi ghi **pass** kèm nguyên số liệu; user chỉ cần nói một câu là tôi lật lại thành fail.

## 4. Gate 4 — "Skeptic rerun REAL-fill vs min(open,L) proxy trên correlated gap-up @NAV target" → **BỊ CHẶN CẤU TRÚC**

Đây là `recommended_reruns[0]` của quant-skeptic (2026-07-01, verdict CONFIRMED): đo **giá khớp THẬT**
so với mô hình proxy `min(open, L)`, đặc biệt trên sáng gap-up tương quan rộng **ở quy mô NAV target**.
Ba lý do độc lập khiến harness paper hiện tại không bao giờ đóng được tiêu chí này:

1. **Fill là mô phỏng, không phải fill thật.** 80/80 lệnh BUY khớp **đúng bằng giá limit đã đặt**
   (`FILL.price == PLACE.price`, sai lệch 0/80) — `broker=paper` (PaperBroker). Zero dữ liệu về
   giá khớp thật ⇒ không có gì để so với proxy.
2. **Sai quy mô 2 bậc.** Gross ~343tr/phiên vs NAV target 50B ≈ **0,7%**. Chính "zero size-impact"
   là *killer objection* quant-skeptic nêu; size này không kiểm được nó.
3. **Sự kiện cần đo gần như không xuất hiện.** Base-rate sáng gap-up **tương quan rộng** (≥50% rổ 6
   mã có `open > prev_close × 1,015`): **10/642 phiên** (2024-01-01 → 2026-08-04) = **1,56%**,
   ~1 lần / 64 phiên ≈ 3 tháng. Trong 20 phiên cửa sổ evidence: **0 lần**
   (chỉ 1 phiên có ≥1 mã gap-up binding). Các ngày broad thật: 2025-04-10/11, 2025-08-15/25/27,
   2025-10-06, 2026-03-10/24, 2026-04-01, 2026-04-08.

Kể cả chờ thêm 6 tháng và sửa được netting, (1) vẫn đứng nguyên: **paper không sinh ra fill thật**.

## 5. Gate 5 — user sign-off → **pending** (phụ thuộc quyết định ở §6)

## 6. Khuyến nghị — cần user chọn 1 trong 3, tôi KHÔNG tự quyết

| | Hướng | Nội dung | Đánh đổi |
|---|---|---|---|
| **A** | **Re-scope gate 4 rồi đóng chương trình** | Chấp nhận bộ bằng chứng hiện có (backtest daily-proxy đã CONFIRMED + stress qua Executor thật + 13 phiên wiring sạch trên quote thật) và ghi nhận rủi ro size-impact còn treo. Cơ sở: patch là **bảo hiểm fill**, NET trung bình ~0 (t=1,26, không ý nghĩa), monotone-safe, fail-safe, ceiling 4% chặn cứng đuôi xấu; chi phí thường ngày đo được trên quote thật = **+0,64% ở ca xấu nhất, 3/80 lệnh**. | Chấp nhận không bao giờ có dữ liệu fill thật trước khi bật. |
| **B** | **Live pilot size nhỏ** | Bật flag trên 1 account live (ZaloPay cash-only, lệnh nhỏ) — con đường DUY NHẤT lấy fill thật. Vẫn không đo được size-impact @50B. | Chạm tiền thật; cần user duyệt tường minh; vẫn phải chờ ~3 tháng mới gặp 1 sáng gap-up tương quan. |
| **C** | **Park chương trình** | Giữ `chase_cap_vol_scale_enabled=False` ở live, đóng luồng paper, mở lại khi có dữ liệu intraday rộng hơn / harness sinh fill thật. | Mất luôn phần bảo hiểm đã trả tiền nghiên cứu. |

**Ý kiến của tôi (không phải quyết định)**: **A**. Gate 4 như đang viết là bài toán không giải được
bằng paper — không phải "chưa đủ thời gian" mà là sai công cụ đo. Nếu user muốn giữ chuẩn "phải có
fill thật" thì đúng đường là **B** với size nhỏ, không phải chờ tiếp trên paper.

**Việc phụ cần ai đó xử lý (không thuộc chương trình này)**: netting nội bộ của probe harness từ
2026-07-28 đã cắt đứt luồng lệnh BUY paper main — ảnh hưởng cả `fill_timing`. Cần quyết giữ netting
(và chấp nhận 2 chương trình đứng bánh) hay tách 1 nhánh probe không netting.

## 7. Tái lập

```bash
# audit 80 lệnh BUY vs 2 chân trần (script tạm, dựng lại theo mô tả §2)
/home/trido/thanhdt/wc_venv/bin/python mike/agents/Taylor/chase_cap_paper_audit_20260804.py
# stress harness
cd /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor
/home/trido/thanhdt/wc_venv/bin/python stress_vol_scale_chase_cap.py
```

Nguồn: `data/execution_logs/exec_main_*_journal.csv` · `data/trade_plans/plan_main_*.json` ·
`data/bq_cache/ticker_prune/*.parquet` · `secrets/trading_bot_accounts.json` ·
`mike/logs/run_bot_main_*.log` · `trading_bot/executor.py:401-449, 799-845`.
