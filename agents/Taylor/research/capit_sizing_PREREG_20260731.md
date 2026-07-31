# PRE-REGISTRATION — CAPIT sizing base A/B (job Taylor_20260731_085810)

Ghi TRƯỚC khi xem bất kỳ kết quả leg nào (3 leg đầu vẫn đang chạy, chưa có dòng metric).

## Câu hỏi
CAPIT sizing nên tính trên cơ sở nào: tiền mặt rảnh (spec đã backtest & pin R3), NAV sổ LAG
(công thức LIVE đang chạy), hay % NAV tổng cố định?

## N_trials khai báo trước = 6
| # | `CAPIT_SIZE_BASE` | Ý nghĩa |
|---|---|---|
| 1 | `cash` | **BASELINE** = spec production đã backtest (size × tiền mặt rảnh của từng sổ) |
| 2 | `idle` | size × (tiền mặt + custom30V đang gửi) — "được bán parking để tài trợ, không giới hạn" |
| 3 | `booknav` | **CÔNG THỨC LIVE** = size × NAV sổ LAG, chỉ sổ LAG |
| 4 | `nav:0.10` | cố định 10% NAV mỗi sổ (= 10% NAV tổng) |
| 5 | `nav:0.20` | cố định 20% NAV mỗi sổ (= 20% NAV tổng) |
| 6 | `idlecap:0.30` | size × idle, trần 30% NAV sổ |

KHÔNG sweep thêm. Nếu muốn thử cấu hình thứ 7 → phải khai lại N_trials và nói rõ.

## Tiêu chí quyết định (chốt trước)
- Chỉ tiêu chính: **Calmar** và **MaxDD** (đây là câu hỏi phân bổ vốn/rủi ro, không phải tìm CAGR cao nhất).
- Một biến thể chỉ được coi là "đáng đề xuất thay production" nếu: Calmar ≥ baseline VÀ MaxDD không
  tệ hơn baseline quá 1,0pp VÀ giữ dấu ở cả IS(2014-19)/OOS(2020+).
- Bất kỳ đề xuất wire nào ⇒ bắt buộc `bin/verify_finding.sh` (quant-skeptic) trước khi trình user.

## Điều kiện chạy (đóng cứng, giống nhau mọi leg)
`BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate`, `NAV_TOTAL_B=50`, `ETF_LIQ=custompitg`,
`BASKET_WT=namecap`, `BASKET_SELECT=yieldcombo`, `PARK_STATES=3:0.7`, `AUDIT_END=2026-06-19`,
`threads=1`, `$DNA_PYEXE`. Đây là snapshot đã dùng cho lần re-pin R3 2026-07-29 ⇒ so sánh cùng vintage.

## Giới hạn đã biết TRƯỚC khi chạy
- Engine cộng CAPIT arm vào **CẢ HAI** sổ (BAL `tag="B"` + LAG `tag="L"`, dòng 1840/1899), trong khi
  LIVE chỉ tài trợ từ sổ LAG ⇒ leg `booknav` cố ý ép `wt=0` cho sổ BAL để khớp live, các leg khác giữ
  nguyên hành vi 2 sổ của spec gốc. Đây là khác biệt cấu trúc, không phải bug.
- Backtest **không** mô hình hoá tài sản off-book (Trứng vàng) — nguồn vốn thật của đợt 07-21.
