# PHẦN 3 — TIỀN ĐĂNG KÝ (viết TRƯỚC khi nhìn bất kỳ số treatment nào)
job `Taylor_20260909_100425` · 2026-09-09 17:5x ICT

## Giả thuyết duy nhất được chạy
**H-EY: nghiêng bộ chọn BAL về earnings yield (1/PE).**
Cơ chế: `BAL_CFO_BLEND=λ` + `BAL_YIELD_METRIC=pe` — knob **đã có sẵn trong production**
(`pt_v23_audit_2014.py`, mặc định 0 = tắt, byte-identical). Nó cộng `λ·40·(rank_pct(ey) − 0.5)`
vào `ta` (khoá SẮP XẾP trong-tier của engine) cho các dòng BAL mua được. Không đổi ngưỡng tier,
không đổi DT5G, không đổi allocator, không đổi CAPIT, không đổi custom30V.

**Căn cứ (Phần 2):** `ey` là indicator DUY NHẤT qua BH ở OOS (IC OOS +0,0747, t 4,81,
p_BH < 0,0001), dương ở CẢ hai regime, và **mạnh lên** 2025-2026 — đúng ngược chiều họ momentum.

## Vì sao KHÔNG chạy các hướng khác
- **prox52 / idiovol / mọi indicator kỹ thuật**: trượt cổng OOS sau BH (Phần 2 §3.2/§4).
  Chạy chúng chỉ nâng N_trials và nâng ngưỡng DSR mà không có tiên nghiệm.
- **Nới gate `state ∈ {4,5}` / sửa hold 45 phiên**: đây là hướng đúng theo cơ chế Phần 1, nhưng
  N thật = **10 cửa sổ regime**; mọi tham số mới sẽ được chọn trên chính 10 sự kiện đó. Ghi làm
  KHUYẾN NGHỊ thiết kế cho vòng sau (cần dữ liệu ngoài mẫu / tiền đăng ký riêng), KHÔNG chạy ở đây.

## N_trials = 3 (λ = 0,25 / 0,50 / 1,00). Không có trial nào khác trên trục này trong job này.

## Chân control
Đã chạy TRƯỚC: `run_ctrl.log`, CAGR 28,86% / Sharpe 1,90 / MaxDD −17,8% / Calmar 1,62 /
Final NAV 1.178,01B; self-check **0 VND** cả 2 sổ; CSV md5 **7d053e6201c9d107685ff4d1dd9d2d2a**
= **TRÙNG BYTE** artifact pin R3 2026-08-03.

## Tiêu chí GO — phải đạt TẤT CẢ, thiếu 1 là NO-GO
| # | Tiêu chí | Ngưỡng |
|---|---|---|
| C1 | ΔCAGR (full period) | **> +0,385pp** (sàn nhiễu của chính harness này, tái dùng từ CCS Phase 2) |
| C2 | Calmar không xấu đi | Calmar_treat ≥ Calmar_ctrl |
| C3 | Walk-forward | ΔCAGR **IS(2014-19) và OOS(2020+) CÙNG DẤU DƯƠNG** |
| C4 | Leave-one-year-out | không năm nào chiếm > 50% tổng delta; giữ dấu ≥ 11/13 năm |
| C5a | DSR (N_trials=3) | **> 0,95** |
| C5b | PBO (CSCV) | < 0,5 |
| C6 | Dose-response | ΔCAGR đơn điệu theo λ (không phải răng cưa) |
| C7 | Self-check | 0 VND cả 2 sổ, mọi chân |

## Hạn chế đã biết, khai báo TRƯỚC
`data/bal_open_pcf.csv` (nguồn PE cho knob) có **vintage 2026-06-16**, khác vintage snapshot pin
(`bq_cache_asof20260729_postrestate`), và dừng ở **2026-06-15** (thiếu 2 phiên cuối cửa sổ audit).
Dòng thiếu được fill rank 0,5 (trung tính) trong code production. Đây là **điểm yếu thật**: nếu
kết quả GO, phải chạy lại với PE cùng vintage TRƯỚC khi đề xuất wire.
