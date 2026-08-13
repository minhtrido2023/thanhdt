---
kind: derived-file
status: MIXED — chân LDR DERIVED (verify chéo 5/5), chân CASA UNVERIFIED (báo chí, 10/13 mã)
source: data/bank_casa_ldr_<YYYYMMDD>.csv
group: fundamentals
writer: mike/agents/Taylor/build_bank_casa_ldr.py (chạy TAY, KHÔNG có cron)
upstream: vnstock 4.0.4 → VCI `finance.balance_sheet` (LDR) · báo chí tổng hợp BCTC Q2/2026 (CASA)
created: 2026-08-14 (job Taylor_20260813_172358)
---

# `bank_casa_ldr` — CASA + LDR rổ ngân hàng đang nắm giữ (13 mã)

**Đọc trước: file này có HAI CHÂN, độ tin cậy KHÁC HẲN NHAU.** Trích một chân bằng lời lẽ dành
cho chân kia là cách sai duy nhất đáng lo ở đây.

| Chân | Cách có | Status | Phủ |
|---|---|---|---|
| **LDR** | TỰ TÍNH từ 2 dòng bảng cân đối | **DERIVED** — đối soát chéo 5/5 lệch ≤0,13% | 13/13 mã × 4 quý |
| **CASA** | CHÉP từ báo chí tổng hợp BCTC | **UNVERIFIED** — chưa đối soát thuyết minh gốc | 10/13 mã × **1 quý** |

## Vì sao tồn tại

BigQuery **không trả lời được** câu hỏi cơ cấu vốn ngân hàng: quét toàn bộ `bigquery_dictionary.json`
không có cột nào về `NIM`/`CASA`/`deposit`/`loan`/`LDR`, và `ticker_financial` với mã ngân hàng còn
trả `StLiab_P0 = LtLiab_P0 = StDebt_P0 = LtDebt_P0 = CR_P0 = FinLev_P0 = 0` (schema doanh nghiệp
phi tài chính, không map được bảng cân đối ngân hàng). Đó là [GAP] §1a của
`agents/Taylor/research/sbv_meeting_note_impact_20260813.md`.

Rổ 13 mã = **vị thế THẬT** đọc từ `dnse_raw_2026-08-13.jsonl` (SpaceX ∪ ZaloPay), không phải
universe ngân hàng VN: ACB BID CTG HDB LPB MBB MSB SHB TCB TPB VCB VIB VPB.

## Chân LDR — dùng được

`ldr_pure = Cho vay khách hàng (GỘP, trước dự phòng) / Tiền gửi của khách hàng`, cả hai đọc thẳng
từ bảng cân đối VCI. **Không phải LDR quy định** (Thông tư 22/2019, trần 85%) — công thức đó có
mẫu số rộng hơn và loại trừ một số khoản; mọi giá trị ở đây >100% là bình thường và **không** đọc
là "vi phạm trần".

Hai self-check chạy sẵn trong script, cả hai PASS ngày 2026-08-14:
1. **Bất biến kế toán** `gộp == ròng + dự phòng`: **52/52** kỳ khớp (sai lệch <1tr VND).
2. **Đối soát chéo nguồn độc lập** (báo chí đọc thẳng BCTC gốc — đường dữ liệu KHÔNG qua VCI):
   **5/5 khớp**, lệch tối đa **0,13%** — CTG tiền gửi +0,04% / CTG dư nợ +0,13% / MBB +0,00% /
   TCB +0,00% / VPB −0,02%. Đây là cái nâng chân này từ "trông hợp lý" lên DERIVED.

⚠️ Một lệch ĐÃ BIẾT, không phải lỗi: TCB dư nợ ta đọc 847,3k tỷ, báo chí nói "dư nợ tín dụng"
835,8k tỷ (−1,4%). Hai khái niệm khác nhau (cho vay khách hàng hợp nhất vs dư nợ tín dụng) — nên
`loan_gross` KHÔNG đối soát được bằng tin "tăng trưởng tín dụng", chỉ đối soát bằng đúng dòng BCTC.

## Chân CASA — CHƯA dùng được cho quyết định

`casa_source = "PRESS_UNVERIFIED_2026Q2"`. Bốn giới hạn, tất cả đều đủ để chặn một quyết định tiền:

1. **KHÔNG phải 2 nguồn độc lập.** Hai bài (vietnambiz, mekongasean) khớp tới 2 chữ số thập phân
   ⇒ gần như chắc chắn **cùng một bảng tổng hợp gốc**. Đếm là MỘT nguồn.
2. **Hai bài định nghĩa KHÁC NHAU cho cùng con số**: vietnambiz ghi
   `(không kỳ hạn + ký quỹ)/tiền gửi KH`, mekongasean ghi `không kỳ hạn/tiền gửi KH`. Số giống
   nhau ⇒ **ít nhất một mô tả sai**, chưa biết cái nào. Tiền ký quỹ ở NH lớn cỡ 1–3pp ⇒ sai số
   đúng cỡ đó.
3. **Bình quân hệ thống không khớp giữa nguồn**: 14,7% (vietnambiz) vs 17,19% (nguoiquansat) —
   chênh 2,5pp ⇒ rổ mẫu hoặc định nghĩa khác nhau.
4. **Chỉ 1 kỳ (30/6/2026), không có chuỗi lịch sử**, và **thiếu 3/13 mã: HDB, SHB, VPB**
   (không tìm thấy ở nguồn nào đã quét — để TRỐNG, script cố ý KHÔNG suy đoán, KHÔNG kéo ngang
   sang kỳ khác).

## Bẫy (1) — `vnstock finance.ratio()` trả CASA/LDR của **2018**, không phải kỳ mới

Đo thật 2026-08-14 trên vnstock 4.0.4, mã CTG. Endpoint `finance.ratio()` **có đúng** 2 chỉ tiêu
`Tỷ lệ CASA` / `LDR (%)` — trông như đúng thứ cần. Nhưng dưới **community edition** (giới hạn 4 kỳ)
nó trả về **4 quý của năm 2018**, trong khi `finance.balance_sheet()` cùng lúc trả đúng 4 quý gần
nhất (2025Q3–2026Q2). `period="year"` chỉ lặp lại đúng 4 quý 2018 đó 4 lần (16 cột).

Tệ hơn: **nhãn cột hỏng** — mọi cột đều tên `"2018"`. Kỳ THẬT chỉ đọc được ở 2 dòng dữ liệu
`Năm`/`Quý`, không đọc được ở header. ⇒ Ai lấy `CASA Ratio` từ đây cho phân tích hôm nay đang dùng
số **8 năm trước** và **không có gì báo lỗi**.

**Liên đới:** `bank_lens_v2.py` / `bank_lens_v3.py` (repo root) đọc đúng cột này (`C_CASA`,
`C_NIM`). Hiện chúng **crash trước** ở `df["lengthReport"]` (vnstock đã đổi shape trả về), nên
chưa từng in ra số 2018 — nhưng **"sửa" chúng một cách ngây thơ sẽ TẠO RA đúng bug đó**. Đừng vá
`lengthReport` mà không xử lý kỳ.

## Bẫy (2) — dòng `Cho vay khách hàng` xuất hiện HAI LẦN

Bảng cân đối trả 2 dòng cùng tên: bản **ròng** (đã trừ dự phòng) và bản **gộp**. Script lấy `max`
= gộp. Lấy nhầm bản ròng làm LDR thấp đi ~1,5–2% một cách âm thầm. Tương tự `Chứng khoán kinh
doanh`, `Tài sản Có khác` cũng trùng tên.

## Bẫy (3) — thuyết minh BCTC gốc là PDF SCAN, máy này không OCR được

Đường "chuẩn" nhất cho CASA là thuyết minh "Tiền gửi của khách hàng — phân theo loại tiền gửi"
trong BCTC hợp nhất. Đã thử với CTG (`investor.vietinbank.vn`, BCTC HN Q2/2026, 6,4MB): **61 trang,
`PyMuPDF` trích ra 0 ký tự** — ảnh scan thuần. Máy hiện tại **không có** `pdftotext`/`tesseract`.
⇒ Muốn đóng chân CASA đúng cách phải cài OCR hoặc tìm bank phát hành PDF text-based. Đây là lý do
kỹ thuật cụ thể, không phải "chưa làm".

## Cách dùng

```bash
python3 mike/agents/Taylor/build_bank_casa_ldr.py     # ~1 phút, sleep 3s/mã
# → data/bank_casa_ldr_<YYYYMMDD>.csv (tên KHÔNG canonical, §8 coding_guidelines)
```
Không cron, không consumer production. Cột: `ldr_pure`, `ldr_source`, `casa`, `casa_source`,
`loan_gross_vnd`, `loan_net_vnd`, `provision_vnd`, `cust_deposit_vnd`, `total_asset_vnd`,
`cds_issued_vnd`, `interbank_funding_vnd`, `selfcheck_loan_resid_vnd`.

**LUÔN đọc `casa_source`/`ldr_source` trước khi trích một ô.** Đó là lý do 2 cột đó tồn tại.

## Điều kiện để nâng status

- Chân LDR → CANONICAL: cần một consumer thật + tái lập ở kỳ BCTC sau (Q3/2026, ~cuối 10/2026).
- Chân CASA → DERIVED: cần đối soát ≥1 mã với **thuyết minh gốc** (OCR hoặc PDF text-based), và
  chốt được định nghĩa (có/không cộng tiền ký quỹ).

↩ [Về nhóm fundamentals](index.md) · [Về index tổng](../index.md)
