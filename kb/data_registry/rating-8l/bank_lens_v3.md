---
kind: script-output
status: PARTIAL
source: data/bank_lens_v3.csv
group: rating-8l
note: migrated off broken finance.ratio() 2026-08-28 (job Taylor_20260828_084735) — ROE/NIM/CIR/loanG/PB refreshed real; NPL/NPL_4q/NPL_slope/CAR/coverage/CASA structurally unavailable (need BCTC thuyet minh, not in vnstock balance_sheet/income_statement); KBS-source cross-check 2026-08-28 (job Taylor_20260828_092753) confirms self-calc correct, KBS vendor ROE unreliable for loss-quarter banks — kept self-calc, question closed
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

## Follow-up 2026-08-28 (job Taylor_20260828_092753) — đã thử `vnstock.api.financial.Finance(source="KBS")`, KHÔNG đổi công thức

Job trước chỉ thử `source="VCI"` cho `finance.ratio()` (chết `KeyError lengthReport`). Class MỚI
`vnstock.api.financial.Finance` nhận `source` là **'VCI' hoặc 'KBS'** — job này thử KBS.

**KBS `Finance(symbol, source="KBS").ratio(period="quarter")` CHẠY ĐƯỢC**, trả 32 chỉ tiêu
vendor-computed, gồm cả ROE/NIM/CIR (khác `ratio()` cũ đã chết). Nhưng script `exp_bank_kbs_
crosscheck.py` (`agents/Taylor/`) cross-check 18 mã bank lộ ra:

- **ROE lệch NẶNG ở 3/18 mã — STB −35,5pp (self 4,9% vs KBS 40,4%), SSB −10,4pp (7,1% vs 17,5%),
  EIB −9,9pp (1,9% vs 11,8%)**. Điều tra sâu (đọc thẳng `income_statement` từng quý) xác nhận cả
  3 mã đều có **1 quý (2025-Q4) lợi nhuận âm/rất yếu** trong 4 quý trailing (STB NPAT-to-parent
  2025-Q4 = **−2.752 tỷ**, EIB = **−472 tỷ**, SSB = **+104 tỷ** so với ~780-1.100 tỷ các quý
  khác) — self-calc CỘNG ĐÚNG cả quý lỗ đó vào trailing-4Q, KBS's `roe_trailling` thì KHÔNG (số
  ra cao hơn nhiều, như thể bỏ qua/làm mượt quý lỗ). Tự tay cộng 4 quý NPAT/equity mới nhất khớp
  CHÍNH XÁC với self-calc CSV cho cả 3 mã (STB 4,90%, EIB 1,86%, SSB 7,08%) — self-calc ĐÚNG,
  KBS's ROE trailing KHÔNG đáng tin (phương pháp khác/dữ liệu lỗi, không rõ nguyên nhân chính
  xác, KHÔNG điều tra thêm — ngoài phạm vi). 15/18 mã còn lại lệch nhỏ (đa số <2pp, ACB −4,1pp).
- **Bằng chứng độc lập KBS có bug chất lượng dữ liệu**: `ratio()` trả 4 cột kỳ nhưng nhãn/tên
  KHÔNG theo thứ tự thời gian (`['2026-Q2','2025-Q4','2026-Q1','2025-Q4_1']`) và cột
  `'2025-Q4_1'` **TRÙNG Y HỆT** cột `'2026-Q2'` ở nhiều dòng đầu (rows 0-9) rồi lệch dần — dấu
  hiệu lỗi pivot/duplicate ở phía thư viện, không phải lỗi đọc của mình.
- **NIM/CIR lệch nhỏ hơn nhưng KHÔNG apples-to-apples**: KBS chỉ có giá trị **1 quý** cho
  NIM/CIR (không có biến thể trailing như ROE) — so với self-calc là **trailing-4Q**. Đã thử quy
  đổi thô (NIM quý ×4) vẫn còn lệch <0,7pp đa số mã nhưng phương pháp khác hẳn, không phải cross-
  check thật.

**KẾT LUẬN: KHÔNG đổi ROE/NIM/CIR sang KBS.** Self-calc (trailing-4Q NPAT/NIM/CIR từ
`balance_sheet`+`income_statement`) vẫn là nguồn — đã trace đúng tới raw statement, đối chiếu tay
khớp tuyệt đối cho 3 ca lệch lớn nhất. Việc self-calc gate STB/EIB/SSB vào `AVOID` (ROE<8%) là
**ĐÚNG hành vi mong muốn** (phản ánh đúng 1 quý lỗ gần nhất), không phải bug cần "sửa" bằng số
KBS êm hơn.

**4 chỉ tiêu KBS có sẵn, CHƯA wire — để dành nếu cần sau** (đọc trực tiếp từ `ratio()` cột mới
nhất, KHÔNG cần tính tay, nhưng NHỚ bug duplicate-column ở trên trước khi tin mù):
`outstanding_loans_customer_deposits` (LDR — Dư nợ cho vay/Tổng vốn huy động),
`equity_deposits_from_customers` (Vốn chủ sở hữu/Tổng vốn huy động),
`equity_total_assets` (Vốn chủ sở hữu/Tổng tài sản),
`loan_loss_provision_ratio` (Dự phòng rủi ro tín dụng/Tổng dư nợ — KHÔNG PHẢI NPL, đây là dự
phòng/dư nợ, khác NPL/coverage đang thiếu ở trên).

**Xác nhận đóng dứt điểm câu hỏi "vnstock có nguồn NPL/CAR/CASA nào không":** đã thử CẢ
`balance_sheet`/`income_statement` (VCI, migration chính) LẪN `Finance(source="KBS").ratio()`
(32 chỉ tiêu, liệt kê đầy đủ ở trên) — **KHÔNG mã nào có NPL/NPL_4q/NPL_slope/CAR/coverage/CASA**
trực tiếp. Đừng điều tra lại lần 3 trong vnstock; muốn 6 cột này phải scrape thuyết minh BCTC
(nguồn khác hẳn).

Script cross-check (R&D, không canonical): `agents/Taylor/exp_bank_kbs_crosscheck.py` +
`agents/Taylor/exp_bank_kbs_crosscheck.csv` (18 mã, đủ cột self vs KBS + diff pp).
