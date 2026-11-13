# Luồng A4 — phân rã −0,48pp (bq → pit) + chạy lại pin trên mã đã merge

Job `Taylor_20261113_034625` (attempt 2). ⚠️ PAPER, không đổi production/`trading_rules.json`/neo −25,2%. Chưa qua quant-skeptic.
Mọi số đo trong job này: `logs/`, `ledgers/`, script `decomp*.py`, `noise.py`. Nguồn dữ liệu: cache `bq_cache_asof20260729_postrestate` (+ `tav2_bq.ticker`).

## 1. Kết luận
1. **Δ −0,48pp ở pin0% là hiệu ứng THẬT, xác định (deterministic), KHÔNG phải nhiễu.** 10 seed tie-break × {bq, pit}: sd mỗi cấu hình 0,170 / 0,179pp, nhưng **Δ ghép cặp theo seed = −0,482pp, sd 0,014, 10/10 seed âm (min −0,50, max −0,46), t = −110**. Câu A3 "≈2,8 sd, vượt nhiễu" dùng sd không-ghép-cặp (0,17) nên đánh giá thấp độ chắc chắn; tie-break gây dao động CHUNG cho cả hai nhánh, còn nguồn ADV gây lệch riêng.
2. **Cơ chế = khác ĐỊNH NGHĨA cửa sổ, không phải NULL.** BQ `Volume_3M_P50`(t) = trung vị 60 phiên GỒM t (khớp `pit(t+1)` 98,65%; chỉ khớp cửa sổ t-60..t-1 55,15%, n=1.616.155 dòng). Engine tra ADV ở NGÀY FILL (T+1) ⇒ bản bq cộng cả khối lượng ngày fill (nhìn trước 1 phiên); pit dùng t-60..t-1 × giá t-1.
3. **pit đúng hơn bq so với live**: live (`due_diligence.py`, `Volume_3M_P50` × Price của `data_date` = phiên đóng cửa gần nhất) tra ADV vào sáng ngày đặt lệnh, tức dòng t-1 = cửa sổ t-60..t-1 = đúng khoá pit(t). bq backtest dùng dòng t+? lệch 1 phiên so với live. Đây là suy luận từ code + tỉ lệ khớp 98,65%, chưa đối chiếu lệnh live cụ thể.
4. **Việc 2: chạy lại trên mã merge TRÙNG BYTE**: pin0% `80f509ec3dbbd55233412913407e6f53`, pin1M `e2de0ac45c7c265827fc53ac0a750675` (= ladderA3-L3P). Self-check 0 VND (BAL & LAG, cash-flow + final NAV) cả hai.

## 2. Phân rã Δ −0,48pp (pin0%, L3 bq 23,39 → L3P pit 22,91)
(a) **Theo năm** (`logs/decomp_year.log`): Σ dlogNAV = −0,0483 = log NAV cuối. Đóng góp lớn: 2021 −0,0093 (−2,0pp), 2024 −0,0117 (−1,4pp), 2016 −0,0095, 2015 −0,0063, 2022 −0,0072; 2018 +0,0038. Nặng nhất 2021–2024, **không** tập trung ở 2015 (−0,7pp). BAL: 992 mua/393 bán, **giao dịch BAL trùng 100%** (1385/1385) ⇒ toàn bộ Δ nằm ở book LAG.
(b) **Theo deal LAG** (`logs/decomp_deal.log`): mua 7198→7094, Σ mua 9.527→8.958B (−6,0%). 1866 vị thế chung, 1609 khác size >0,5%; chỉ-bq 75 (cost 108B, pnl +3,1B), chỉ-pit 60 (92,6B, −0,35B). Σ pnl LAG 480,4B → 439,2B (**−41B**): ~−38B từ vị thế chung bị giảm size, ~−3,4B từ khác tập mã. Top xấu: HAH 2024-11 −3,1B, VIX 2025-04 −3,0B, VIX 2025-07 −2,7B, GVR 2024-02 −2,2B. Top tốt: GEE 2026-05 +4,0B (bq mua, pit không).
(c) **ADV bq vs pit** (`logs/decomp_adv.log`): log(bq/pit) trung vị 0,000, p5/p95 −0,09/+0,10 (29% dòng |r|<1%); bq NULL 144/7419 (mã,ngày) mua, bq≤0 6, pit≤0 11 ⇒ NULL là phần phụ. Trên 5549 cặp đổi size, tương quan(log ADV bq/pit, log size pit/bq) = −0,34, **94,7%** đúng chiều (ADV pit nhỏ ⇒ size nhỏ); Σ size cặp chung pit/bq −4,6%, lệch tăng dần: 2014 −0,3% … 2024 −5,1%, 2025 −6,8%, 2026 −6,2% (khối lượng tăng theo thời gian ⇒ cửa sổ có ngày fill chênh nhiều hơn). Thứ tự/tie-break: không tham gia (Δ ghép seed 0,014).
(d) **Tách 2 trục** (mặc định tie-break, 1 lần/chân): bq 23,39 → `fill` (chỉ vá NULL, giữ định nghĩa BQ) **23,19 (−0,20pp)** → pit 22,91 (**−0,28pp**, đổi cửa sổ+giá). md5 fill `369dd7cc…`. Chưa lặp seed cho fill nên −0,20/−0,28 chỉ gợi ý (nhiễu chân đơn ~0,17, nhưng ghép cặp rất chặt).

## 3. Nhiễu (N độc lập)
N = 10 seed tie-break (thực thi độc lập, cùng dữ liệu) × 2 cấu hình; chuỗi NAV 12,5 năm chung nên N hiệu dụng về thời gian không tăng. Bảng (CAGR FULL %): bq mean 23,39 sd 0,170 [23,02–23,63]; pit mean 22,91 sd 0,179 [22,52–23,16]; Δ ghép cặp −0,482 sd 0,014 se 0,004. (`noise.py`, ledger `ledgers/*TB{bq,pit}_s*`; không pin.)

## 4. Việc 2 — dải trên mã merged (`logs/exp_A4_M_pin0.log`, `exp_A4_R_pin1M.log`, `boot2_pins.log`, `metrics_pins.log`)
Mã `7f25febc1`, không env override ngoài các knob cố định của sandbox; bootstrap circular L=21, B=4000, seed 12345.

| Đầu | md5 | CAGR | Sharpe | MaxDD | IS / OOS | Boot CAGR5 | **DD5** | P(DD<−30%) |
|---|---|---|---|---|---|---|---|---|
| pin0% (sàn) | 80f509ec | 22,91% | 1,78 | −17,1% | 16,47 / 29,12 | 14,72% | **−27,89%** | 2,73% |
| pin1M (trần) | e2de0ac4 | 26,61% | 2,04 | −14,8% | 19,80 / 33,20 | 18,13% | **−24,96%** | 0,80% |

**Dải: 22,91% (pin0%, sàn) … 26,61% (pin1M, trần); DD5 −27,89% … −24,96%.** Neo sizing lấy đầu sàn: −27,89% sâu hơn −25,2% là 2,69pp (chỉ báo, user quyết).

## 5. Không kết luận được
- Chưa đo lệnh LAG live thật (ADV lúc đặt lệnh so với số backtest) ⇒ "pit đúng hơn live" là suy luận cấu trúc, không phải đối chiếu fill.
- Đóng góp riêng của 2 trục (NULL vs cửa sổ) chỉ 1 lần chạy/chân.
- Đây là Δ trên 1 đường lịch sử; không nói gì về out-of-sample.
