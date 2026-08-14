---
kind: derived-file
status: DERIVED — cả 2 chân. LDR verify chéo 5/5; CASA đọc từ BCTC GỐC, 13/13 mã, 3 chân verify độc lập
source: data/bank_casa_ldr_<YYYYMMDD>.csv (LDR) · data/bank_casa_primary_<YYYYMMDD>.csv (CASA)
group: fundamentals
writer: mike/agents/Taylor/build_bank_casa_ldr.py (LDR) · mike/agents/Taylor/build_bank_casa_primary.py (CASA) — chạy TAY, KHÔNG có cron
upstream: vnstock 4.0.4 → VCI `finance.balance_sheet` (LDR) · thuyết minh BCTC hợp nhất Q2/2026 gốc, PDF từ kho công bố thông tin HOSE (CASA)
created: 2026-08-14 (job Taylor_20260813_172358)
updated: 2026-08-14 (job Taylor_20260814_002041 — chân CASA UNVERIFIED→DERIVED, 10/13→13/13 mã)
---

# `bank_casa_ldr` — CASA + LDR rổ ngân hàng đang nắm giữ (13 mã)

| Chân | Cách có | Status | Phủ |
|---|---|---|---|
| **LDR** | TỰ TÍNH từ 2 dòng bảng cân đối | **DERIVED** — đối soát chéo 5/5 lệch ≤0,13% | 13/13 mã × 4 quý |
| **CASA** | Đọc thuyết minh BCTC **GỐC** (OCR/text) | **DERIVED** — 3 chân verify độc lập, xem dưới | 13/13 mã × **1 quý** |

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

## Chân CASA — đã đóng bằng NGUỒN SƠ CẤP (2026-08-14, job `Taylor_20260814_002041`)

`casa_source = "BCTC_PRIMARY_2026Q2"`. Số đọc thẳng từ thuyết minh **"Tiền gửi của khách hàng"**
trong BCTC hợp nhất Q2/2026 của từng ngân hàng — không còn chép báo chí.

**Định nghĩa đã CHỐT** (trước đây là điều mơ hồ nhất): chuỗi báo chí = **(Tiền gửi không kỳ hạn +
Tiền gửi ký quỹ) / Tổng tiền gửi khách hàng**. Không phải suy đoán — dựng lại công thức này từ
BCTC gốc khớp báo chí **10/10 mã trong phạm vi ±0,03pp** (mức làm tròn). ⇒ mô tả của vietnambiz
ĐÚNG, mô tả của mekongasean (`không kỳ hạn / tiền gửi KH`) SAI. Giới hạn (2) của bản cũ đã đóng.

CSV xuất **3 cột tỉ lệ**, chọn đúng cột theo việc — đừng trộn:

| Cột | Công thức | Dùng khi |
|---|---|---|
| `casa_strict_pct` | (không kỳ hạn **+ tiết kiệm không kỳ hạn**) / tổng | **mặc định** — sát nghĩa kinh tế "tiền rẻ, rút bất kỳ lúc nào" |
| `casa_narrow_pct` | chỉ dòng "không kỳ hạn" / tổng | khi cần khớp đúng 1 dòng BCTC |
| `casa_pressdef_pct` | (không kỳ hạn + ký quỹ) / tổng | **chỉ** khi đối chiếu số báo chí/broker |

⚠️ Chỉ **ACB** có chênh giữa `strict` và `narrow` (21,41% vs 20,03%) vì ACB tách riêng dòng
"Tiền gửi tiết kiệm không kỳ hạn". 12 mã còn lại hai cột bằng nhau. Tiền ký quỹ đẩy TPB lệch
nhiều nhất: 18,32% (strict) → 20,97% (định nghĩa báo chí), **+2,65pp** — nên trích nhầm cột ở
TPB là sai thật, không phải làm tròn.

### Ba chân verify ĐỘC LẬP (đây là cái nâng status, không phải "trông hợp lý")

1. **Bất biến số học nội bộ, 13/13 PASS.** Mỗi mã qua 2 kiểm tra: (A) mỗi nhóm == Σ thành phần
   VND + ngoại tệ; (B) tổng cộng == Σ các nhóm, so với **dòng tổng in sẵn trong bảng**. Một chữ
   số OCR sai gần như chắc chắn phá vỡ ít nhất một bất biến.
2. **Mẫu số vs nguồn hoàn toàn khác đường: 13/13 khớp TUYỆT ĐỐI (0,0000%).** Tổng tiền gửi đọc
   từ PDF gốc == `cust_deposit_vnd` lấy qua vnstock/VCI. Hai đường dữ liệu không chung khâu nào.
3. **Tỉ lệ vs báo chí: 10/10 mã, |lệch| ≤ 0,03pp** dưới đúng định nghĩa đã chốt ở trên.

### Phủ 13/13 — và 3 mã bổ sung KHÔNG ngẫu nhiên

HDB, SHB, VPB (trước đây trống ở mọi nguồn báo chí) nay đã có, và **cả ba rơi vào nhóm 4 mã CASA
thấp nhất**: SHB 7,77% · HDB 10,81% · VPB 11,48%. ⇒ khoảng trống dữ liệu cũ **lệch có hệ thống về
phía các mã yếu nhất**; lấp bằng "mã nào báo chí có" sẽ cho bức tranh lạc quan giả. Đây là lý do
cụ thể để không dùng độ phủ báo chí làm mẫu.

**Vẫn còn đúng giới hạn (4) cũ**: chỉ **1 kỳ (30/6/2026)**, KHÔNG có chuỗi lịch sử — không kéo
ngang sang kỳ khác. Chuỗi lịch sử phải OCR thêm BCTC từng quý.

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

## Bẫy (3) — ĐÃ GIẢI. Cách lấy BCTC gốc + 3 cái bẫy thật khi OCR

Bản cũ ghi "máy không OCR được" — **hết hiệu lực từ 2026-08-14**: Mike đã cài `tesseract 4.1.1`
(`~/.local/bin/tesseract`, ngôn ngữ `eng`/`vie`/`osd`). Không có `pdftoppm`; rasterize bằng
**PyMuPDF** `page.get_pixmap(dpi=...)` rồi `tesseract <png> stdout -l vie --psm 6`.
Toàn bộ 13 mã (~660 trang) OCR xong trong **~2 phút** (6 luồng, tuần tự từng PDF — chạy 10 PDF
song song mỗi cái 6 luồng thì thrash, chậm hơn hẳn).

**Nguồn PDF có hệ thống** (không phải mò từng trang IR): kho công bố thông tin HOSE mirror trên
Vietstock —
`https://static2.vietstock.vn/data/HOSE/2026/BCTC/VN/QUY%202/<TICKER>_Baocaotaichinh_Q2_2026_Hopnhat.pdf`
→ trúng **11/13** mã ngay lần đầu. Ngoại lệ: **LPB** bỏ hậu tố (`..._Q2_2026.pdf`), **VPB** không
có trên kho này, phải lấy từ IR VPBank (bản **"tra cứu"** = text-based sạch).

### (3a) "Có text layer" ≠ "đọc được" — ca HDB
`PyMuPDF` trích **94.112 ký tự** từ BCTC HDB ⇒ mọi phép thử `chars > ngưỡng` đều kết luận
"text-based, khỏi OCR". Nhưng CMap của font **HỎNG**, text ra mojibake:
`"NGAN HANG THUoNG MAr c6 eHAN IHAT TRrdN"` (= "NGÂN HÀNG THƯƠNG MẠI CỔ PHẦN PHÁT TRIỂN"), và
**chữ số cũng hỏng** (`"2.71O.773"` — chữ O thay số 0). ⇒ đừng phân loại text/scan bằng số ký tự;
kiểm bằng việc **có khớp được một từ khoá tiếng Việt có dấu** không. HDB phải OCR như scan.

### (3b) "Tiền gửi không kỳ hạn" xuất hiện ở NHIỀU thuyết minh
Cụm này có cả trong note **tiền gửi tại/của các TCTD khác** (liên ngân hàng) lẫn note **tiền gửi
của khách hàng**. Lấy khớp đầu tiên ⇒ ra số liên ngân hàng, sai hoàn toàn và **không có gì báo
lỗi**. Phải neo vào tiêu đề note "TIỀN GỬI CỦA KHÁCH HÀNG" rồi mới đọc dòng.

### (3c) OCR đọc sai số THẬT — và bất biến (B) chốt lại được giá trị đúng
Không phải rủi ro lý thuyết, **3 ca đã xảy ra** ở 300 dpi:

| Mã | OCR đọc | Giá trị ĐÚNG (do dòng tổng chốt) | Kiểu lỗi |
|---|---|---|---|
| MSB | ký quỹ `4.900.330` | `1.900.330` | 1→4 |
| TPB | ký quỹ `1.649.049` | `7.649.049` | 7→1 |
| LPB | không kỳ hạn `22.291.930`, ký quỹ `221.996` | `22.292.930`, `227.996` | nhiều chữ số |

Cách chốt: nhóm nào Σ thành phần ≠ tổng nhóm, HOẶC Σ nhóm ≠ dòng tổng in trong bảng, thì có ít
nhất 1 số sai; hệ 2 phương trình thường **định lại duy nhất** giá trị đúng. **Nâng dpi KHÔNG đủ**
— LPB đọc sai ở cả 300 lẫn 500 dpi theo hai kiểu khác nhau; chỉ ràng buộc số học mới chốt được.
⇒ **Không bao giờ nhận một con số OCR chưa qua ít nhất 1 bất biến cộng.** TPB vẫn còn 1 thành
phần con (VND của dòng không kỳ hạn) đọc lệch không tự chốt được, nhưng **tổng nhóm** — thứ CASA
thật sự cần — thì đã được dòng tổng xác nhận.

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
