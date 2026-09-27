# Hậu kiểm sau merge `a808a613` — re-pin R3 custom30V (job `Taylor_20260927_043541`, 2026-09-27)

Nguồn chuẩn tắc của MỌI số trong file này: `data/results_registry.md` mục
**"2026-09-27 (bis) — HẬU KIỂM SAU MERGE `a808a613`"** (§1-§7). File này chỉ là chỉ mục artifact.

| Bước | Kết quả | Artifact |
|---|---|---|
| 1. Selfcheck trên main, 3 TZ | `retleg` **PASS 5/5 × 3 TZ** (PREREF=`d04251f0`) · `price_basis` **PASS × 3 TZ** | `sc_retleg_main_TZ_*.log`, `sc_pricebasis_main_TZ_*.log` |
| 2. Tái lập pin R3 trên main | **24,38% / 1,69 / −18,8% / 1,30 / 757,61B · md5 `3f836927` · diff vs `c30vnew` = 0 dòng · self-check 0 VND** | `run_main.sh`, `c30vmain.log` |
| 3. Bootstrap | 5th-pct **CAGR 15,6% / MaxDD −30,4%** (control 19,4% / −28,1%) | `bootstrap_c30vmain.log`, `bootstrap_c30vctl.log` |
| 4. DSR / PBO | **DSR 1,0000** (qua cổng) · **PBO 0,3993** (cũ 0,2088) — tăng do HỌ nở 80→477, KHÔNG do bug | `dsr_pbo_newR3.log`, `dsr_pbo_asis_oldR3.log` |
| 5. Parking NEUTRAL | **+7,4pp → +2,01pp CAGR**; parking làm XẤU Sharpe/DD/Calmar | `c30vnopark2.log`, `c30vnoparkleg.log` |
| 6. Registry | §6 bảng SUPERSEDED cũ→mới; 3 dòng kiểm kê ở section trước đổi từ STALE sang ĐÃ CHẠY LẠI | `data/results_registry.md` |
| 7. Park-fraction 70/80/85% | ⚠️ **Calmar đơn điệu GIẢM; "đỉnh 80%" không còn tồn tại** — knob LIVE, CHỜ USER | `c30vpark80.log`, `c30vpark85.log` |

## Ba thứ phát sinh, đều là phát hiện riêng (không phải hệ quả của re-pin)

1. **`dsr_pbo_annex.py` không tái lập được số đã pin** — họ trial là `glob` động ⇒ mỗi backtest R&D
   mới tự nhập họ (80 → 477 CSV, PBO 0,209 → 0,399); và `R3_CSV` từng hardcode vào một file cũng đã
   bị ghi lại 2026-07-14 (ann-SR "cùng pin cũ" trôi 1,829 → 1,771 mà không ai đổi dòng nào). Đã thêm
   env `DSR_R3_CSV`; **đề xuất pin `family_manifest`** — CHƯA LÀM.
2. **No-op im lặng của `run_leg.sh`/`run_main.sh` (§29)** — `PARK_STATES="3:0.7"` nằm trong khối pin
   SAU `env "$@"`, nên mọi override của caller bị ghi đè. Lần chạy no-park đầu ra số y hệt `c30vmain`;
   chỉ bắt được vì log echo `parking policy {3: 0.7}`. Đã tách `run_main2.sh` (`"$@"` đứng CUỐI).
3. **Quyết định park=80% (08-04) mất căn cứ** — nó dựa vào đỉnh Calmar 1,63 với biên 0,01 trên chân
   return lỗi; ở chuỗi đúng Calmar giảm đơn điệu theo park%. **Không tự đổi config.**

## Thay đổi code của hậu kiểm
`dsr_pbo_annex.py`: thêm `os.environ.get("DSR_R3_CSV", <mặc định cũ>)` — không đổi phép tính nào.
