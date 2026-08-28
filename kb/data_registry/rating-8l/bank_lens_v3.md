---
kind: script-output
status: PARTIAL
source: data/bank_lens_v3.csv
group: rating-8l
note: migrated off broken finance.ratio() 2026-08-28 (job Taylor_20260828_084735) — ROE/NIM/CIR/loanG/PB refreshed real; NPL/NPL_4q/NPL_slope/CAR/coverage/CASA structurally unavailable (need BCTC thuyet minh, not in vnstock balance_sheet/income_statement)
writer: bank_lens_v3.py (repo root) — pull vnstock balance_sheet+income_statement+company.overview per ticker, ad-hoc chạy tay
---

# data/bank_lens_v3.csv (+ bank_lens_v3.md — cùng builder, cùng lần chạy)

**Status: PARTIAL (real data, refreshed 2026-08-28, nhưng 6/11 cột gốc không tái lập được)**

## Là gì
Sector lens 18 mã bank (VCB BID CTG TCB MBB ACB VPB VIB HDB STB SHB TPB MSB OCB LPB EIB NAB SSB) —
ROE/NIM/CIR/loanG/PB thật, gate ROE-only (AVOID ROE<8%, else DATA_GAP). Feed vào `rating_8l.py`
route BANK (dòng ~528) qua `rate_bank()`: ROE là trục CHÍNH, NPL/coverage chỉ là differentiator
KHI CÓ — route BANK verify KHÔNG crash khi các cột đó NaN (fail-safe by design, `rate_bank()`
đã `pd.isna()`-guard sẵn trước khi dùng NPL/coverage).

## Ai ghi / cadence
`bank_lens_v3.py` (repo root, executable) — `Vnstock().stock(...).finance.balance_sheet(period=
"quarter")` + `.finance.income_statement(...)` + `.company.overview()`. Ad-hoc, không cron.
Guest tier rate-limit 20 req/phút → script cần ~12s sleep/mã (3 request/mã) + 30s cooldown khi
retry; full run 18 mã mất ~5-8 phút thực đo 2026-08-28.

## MIGRATION 2026-08-28 (job Taylor_20260828_084735) — root cause ĐÃ VÁ, không hoàn toàn
`finance.ratio()` (nguồn CŨ của cả 11 cột) bị vnstock deprecate 31/08/2025, 100% mã trả
`KeyError('lengthReport')` (xem lịch sử BLOCKED-STALE cũ ở git log file này). Đã chuyển sang
`finance.balance_sheet()`/`finance.income_statement()`/`company.overview()` — endpoint KHÁC,
không bị lỗi shape đó. Verify sanity 2026-08-28: VCB self-calc ROE 16.76%/NIM 2.81% khớp ballpark
với con số narrative trong `company.overview()['company_profile']` (ROE 16.73%/NIM 2.63% năm
2025) — phương pháp hợp lý dù không phải cùng công thức tuyệt đối.

**5 cột PHỤC HỒI được** (công thức + module docstring trong `bank_lens_v3.py`):
- `ROE` = trailing-4Q NPAT-to-parent / equity mới nhất
- `NIM` = trailing-4Q thu nhập lãi thuần / avg(loans+securities+interbank) — XẤP XỈ, không phải
  NIM chuẩn (thiếu average daily earning assets, community edition chỉ cho 4 quý)
- `CIR` = trailing-4Q |chi phí QLDN| / trailing-4Q tổng thu nhập hoạt động
- `loanG` = QoQ (không phải YoY — 4-quý cap của community edition khiến "mã cũ nhất" chỉ cách
  ~3 quý, không đủ 4 quý cho YoY thật); xem cột `loanG_basis` trong CSV để biết đúng 2 kỳ so sánh
- `PB` = current_price (company.overview) / (equity / issue_share)

**6 cột KHÔNG PHỤC HỒI được — để NaN, KHÔNG suy đoán** (`data_gap` col trong CSV giải thích):
`NPL`, `NPL_4q`, `NPL_slope`, `CAR`, `coverage`, `CASA`. Lý do: không nằm trong
`balance_sheet`/`income_statement` main line items — NPL/coverage cần breakdown dư nợ theo NHÓM
(nhóm 3-5, nằm ở thuyết minh BCTC), CAR là tỷ lệ vốn quy định (cần risk-weighted-assets, không có
trong BCTC công khai qua vnstock), CASA cần breakdown loại tiền gửi (cùng giới hạn
`build_bank_casa_ldr.py` đã ghi 2026-08-14 cho CASA — nay xác nhận áp dụng luôn cho NPL/CAR/
coverage). `company.overview()['company_profile']` CÓ narrative NPL/NIM/ROE cho năm gần nhất ở
MỘT SỐ mã (vd VCB) nhưng CỐ Ý KHÔNG parse: prose không đảm bảo format nhất quán 18 mã, chỉ có
theo NĂM (không có trend quý cho NPL_slope), và parse prose thành input cho hard-gate là đúng loại
"đoán số có hình dạng dữ liệu" mà §1/§9 CLAUDE.md cảnh báo.

**Gate đổi theo** (KHÔNG còn dùng AVOID/WATCH/CLEAN cũ dựa NPL/coverage/CAR — các input đó NaN,
nếu giữ nguyên `gate()` cũ thì mọi so sánh `NaN>0.03` trả `False` ⇒ MỌI bank sẽ rơi vào nhánh
`else: CLEAN` — một bug fail-OPEN nghiêm trọng, không phải giả thuyết): gate mới
`AVOID(ROE<8%) else DATA_GAP`. Xem docstring `bank_lens_v3.py` để hiểu đầy đủ lý do.

## Bẫy
- `gate` column giờ chỉ phản ánh ROE (AVOID/DATA_GAP), KHÔNG còn là asset-quality gate đầy đủ —
  đọc `NPL`/`CAR`/`coverage`/`CASA` = NaN, đừng suy diễn "sạch" hay "bẩn" từ đó.
- `loanG` là QoQ chứ không phải YoY — đổi ý nghĩa so với bản gốc (bản gốc lấy trực tiếp từ
  `ratio()`'s "Loans Growth" mà không rõ kỳ hạn nội bộ; bản mới minh bạch bằng `loanG_basis`).
- Refresh lại: nếu vnstock lại đổi shape `balance_sheet`/`income_statement`, cùng lớp lỗi
  `KeyError`/thiếu cột sẽ tái diễn — kiểm tra bằng chạy thử 1 mã trước khi tin cả 18.
- Muốn khôi phục NPL/CAR/coverage/CASA đầy đủ: cần scrape thuyết minh BCTC (khác nguồn hẳn
  vnstock's structured endpoints) — việc lớn hơn phạm vi migration này, CHƯA làm.
