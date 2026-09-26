# Đề xuất khai thác dữ liệu FiinPro-X vào ARIA — 2026-09-26

> Người viết: Mike (trả lời user, topic 1540662920889761883). Bối cảnh: harvest tự động kết thúc
> 26/09 21:27 ICT — **74/74 task xong, 0 failed** (OShares 655 mã + tỷ giá 15 năm), cộng P1-P3 đã
> lấy tay 14/09. Trial hết hạn **28/09** ⇒ sau đó KHÔNG refresh được; mọi đề xuất dưới đây phải
> tự trả lời "sau 28/09 nguồn sống là gì". Khuyến nghị mua/không mua giữ nguyên: **KHÔNG mua ở AUM
> hiện tại** (xem §4).
> Trạng thái: ĐỀ XUẤT, chưa dispatch nghiên cứu nào. Ràng buộc chung cho MỌI hướng: paper-only,
> prereg trước backtest, N = số sự kiện độc lập (không phải số dòng), quant-skeptic trước khi wire,
> kỳ vọng ΔCAGR≈0 cho mọi thứ mang tính CỔNG/CHẨN ĐOÁN (`amh-adaptivity-review-20260910.md` §4).

## 0. Kết luận 1 đoạn

Bộ dữ liệu này có giá trị **chủ yếu ở phần LỊCH SỬ** (2009-2026) — thứ ARIA đang thiếu hoặc đang
ngoại suy — chứ không phải ở việc nuôi feed sống. 3 việc đáng làm ngay vì thay dữ liệu XẤU bằng
dữ liệu TỐT cho consumer đã có (không cần alpha mới): **(1) NPL/LLR 27 ngân hàng → route BANK của
8L đang NaN 9/18 mã; (2) CPI thật → thay tầng nội suy lệch tới 3pp trong `cpi_vn.py`; (3) OShares
đúng ngày sự kiện → đóng TRAP `ticker_financial.OShares`.** 2 câu hỏi nghiên cứu từng bị chặn vì
thiếu dữ liệu nay mở khoá được: **cú bán 2018 (khối ngoại khớp lệnh từ 2014)** và **proxy sinh thái
retail cho AMH G4 (dòng tiền cá nhân/tự doanh/tổ chức từ 2016)**. Còn lại (tín dụng/M2, tỷ giá tự
do, GDP) là chỉ báo XÁC NHẬN MUỘN — đưa vào registry của Bobby, không làm cổng.

## 1. Kiểm kê — có gì, tin được tới đâu, sau 28/09 sống bằng gì

| # | Bộ dữ liệu | Độ phủ | Status registry | Sau 28/09 |
|---|---|---|---|---|
| A | NPL(3-5)/NIM/CASA/LLR **27 NH theo quý** | 2010Q1→2026Q2, 1.392 dòng | DERIVED (LLR khớp OCR 8/9 ≤0,1pp; NPL +1-2% tương đối có hệ thống) | Lịch sử: vĩnh viễn. Sống: OCR BCTC quý cho mã đang giữ (quy trình `bank_npl_coverage_primary` đã có) |
| B | CPI headline/lõi/vàng/USD **tháng** | 2008-01→2026-08, 224 tháng | DERIVED (khớp NSO 13/13) | GSO công bố tháng — nối tiếp bằng T1 `cpi_vn.py` hiện có |
| C | M2/tín dụng/tín dụng XD/tiền gửi **YoY tháng** | 2013→2026-07 | DERIVED tín dụng tổng; còn lại UNVERIFIED; **gãy chuỗi tiền gửi 10/2025** | NHNN công bố tháng, chưa có scraper — tần suất thấp, làm tay được |
| D | GDP danh nghĩa **quý** + BĐS/XD/tài chính | 2018Q1→2026Q2 | DERIVED, gãy 2020→2021 (đánh giá lại GDP) | GSO quý |
| E | Dòng tiền **5 nhóm NĐT** VNINDEX ngày (ngoại khớp/thoả thuận, tự doanh, tổ chức, cá nhân) | 2014→2026-09-14, 3.165 phiên; đủ 5 nhóm từ 2016-04 | DERIVED ngoại (khớp VNDirect median 1,9 tỷ); 3 nhóm nội UNVERIFIED | **KHÔNG có nguồn thay thế trong tay** cho tự doanh/tổ chức/cá nhân — duy nhất trong repo |
| F | Khối ngoại mua/bán VNINDEX + ròng HNX ngày | 2009-06→2018-08, 2.313 phiên | UNVERIFIED nguồn ngoài (không có nguồn nào khác trước 2018-08) | Lịch sử thuần — không cần refresh |
| G | **OShares theo ngày đổi số** (event-only, đã lọc nháy ≤5 phiên) | 655 mã `universe_pit`, 2013→2026 | **CHƯA registry** (raw `data/fiinprox_oshares_raw/*.txt`) | Live đã đúng (kết luận 09-08) — chỉ cần lịch sử |
| H | Tỷ giá USD **tháng**: trung tâm, VCB mua/bán, tự do, NHNN | 2012→2026, 15 năm | **CHƯA registry** (raw `data/fiinprox_fx_raw/usd_YYYY.txt`) | VCB: `vcb_fx_feed.py` có sẵn; **tự do: không có nguồn** |
| I | Bank ratios theo NĂM 9 mã + CAR | 2018-2025 | DERIVED | như A |

**Việc bắt buộc trước 28/09 (§9 coding_guidelines):** G và H chưa có entry `kb/data_registry/`.
Dựng 2 CSV hợp nhất + 2 entry, ghi rõ `upstream: FiinPro-X trial ENDED 2026-09-28, NO refresh` và
cột "nguồn nối tiếp". Riêng G phải qua **tiêu chí nghiệm thu P4** chưa làm: ngày đổi số CP khớp
`tav2_bq.corporate_action` (`corp_action_lib.pricing_events`, KHÔNG `events()`) chứ không khớp ngày
BCTC — đó mới là bằng chứng PIT.

## 2. Hướng đề xuất — xếp theo (giá trị cho ARIA × chắc chắn) ÷ chi phí

### H1. NPL/LLR 27 ngân hàng → route BANK của `rating_8l.py` / `bank_lens_v3.py`  — **ƯU TIÊN 1**
- **Lỗ hổng đang có:** `rate_bank()` NaN NPL/coverage 9/18 mã ⇒ Tier-1 sector của book (MBB/ACB/HDB)
  được chấm bằng dữ liệu thiếu; lịch sử 2010-2026 chưa từng có để backtest route này.
- **Việc:** Taylor A/B `rating_8l` route BANK: (a) hiện trạng vs (b) NPL/LLR FiinPro, trễ công bố
  ≥45 ngày sau quý (Q4 ≥90) để PIT. Đo: thay đổi rating của từng NH theo quý, ổn định thứ hạng,
  và — quan trọng nhất — **có đổi quyết định nào của V2.4 trong 2014-2026 không** (gate nhị phân
  ≤3 chỉ đổi kết quả khi có NH nhảy qua ngưỡng).
- **Bẫy phải mang theo:** NPL FiinPro cao hơn OCR +1-2% tương đối (khác mẫu số) ⇒ dùng cho THỨ
  HẠNG/gate nhị phân, không dùng ngưỡng tuyệt đối tinh; NIM là luỹ kế quy năm; SHB 2012Q3 13,8%,
  STB 2015-17, NVB 2022-24 là nhảy thật. Không phải PIT theo ngày công bố.
- **Kỳ vọng:** ΔCAGR ≈ 0 (đây là sửa dữ liệu, không phải factor mới). GO nếu ranking ổn định +
  quant-skeptic CONFIRMED; wire = thay NaN, không đổi công thức.
- **Sống sau 28/09:** OCR quý cho mã đang giữ như hiện nay — chỉ cần lịch sử.

### H2. CPI thật → thay tầng nội suy T2/T3 của `cpi_vn.py`  — **ƯU TIÊN 2 (sửa đúng/sai)**
- **Lỗ hổng:** 2011-2025 là đường thẳng nối ~36 điểm, lệch tới **2,51pp**, hướng 3 tháng sai
  **22,5%** số tháng; đáy 2009 sai (−0,02% vs thật 1,97%). Consumer: `macro_confidence_regime.py`,
  `dcf_valuation.py` (lãi suất thực/chiết khấu), nghiên cứu khủng hoảng 2009 đã dùng số sai.
- **Việc:** chạy lại `macro_confidence_regime` với CPI thật, đếm số tháng đổi nhãn regime; chạy
  lại DCF cho rổ đang giữ, đo Δ giá trị. Nếu nhãn regime đổi ở đúng các episode Bobby đã phân
  loại (2011 lạm phát 2 chữ số, 2022) ⇒ càng củng cố. Đồng thời đổi tên `NSO_CPI_YOY_AVG_REAL`
  (thực chất là lõi).
- **Kỳ vọng:** thay đổi nhãn ít, nhưng DCF của một số mã có thể lệch vài % — đây là sửa lỗi,
  không phải tối ưu. quant-skeptic bắt buộc vì `macro_confidence_regime` là input production.
- **Sống sau 28/09:** GSO tháng (T1 đã có).

### H3. OShares PIT → đóng TRAP `ticker_financial.OShares`  — **ƯU TIÊN 3 (vệ sinh, không alpha)**
- **Lỗ hổng:** `OShares` là RESTATE (2.667 dòng đã biết), nuôi nhánh `sales_yield` (1/PS) của
  composite v3 và `oshares_live.py` hay trả rỗng. Kết luận 09-08: live đã đúng, vấn đề CHỈ ở cửa
  sổ lịch sử — bộ G chính là cửa sổ lịch sử đó.
- **Việc:** (1) nghiệm thu PIT: ngày đổi vs `corporate_action` pricing_events + list restate; (2)
  dựng bảng `oshares_pit` (ticker, date, shares) từ event-list; (3) re-pin R3 chân control với PS
  dùng OShares PIT — **kỳ vọng đổi ≈0** (user đã chốt không wire overlay vì PS chỉ là 1/3 nhánh).
  Giá trị thật = backtest từ nay không còn look-ahead nhánh PS, và `oshares_live` có fallback.
- **Kỳ vọng:** ΔCAGR ≈ 0. Nếu khác 0 đáng kể ⇒ đó là phát hiện, phải quant-skeptic.

### H4. Khối ngoại KHỚP LỆNH 2014+ → chỉ báo vá điểm mù 2018  — **mở khoá câu hỏi đã chặn**
- **Lỗ hổng:** `production_mechanism_2009_2018_20260830.md` §B.1 kết luận chỉ báo "bán ròng khối
  ngoại khớp lệnh" **KHÔNG khả thi** vì VNDirect chỉ từ 2018-08-30 — sau cú bán 04-07/2018. Bộ E
  có khớp lệnh tách thoả thuận từ 2014, bộ F có gross từ 2009 (lấp luôn 2009 rally bị bỏ lỡ).
- **Việc (BLIND, đúng mandate 08-25):** Bobby phân loại episode TRƯỚC; Taylor dựng chỉ báo trên
  `foreign_matched_net_bn` (loại ngày thoả thuận lớn: Vinhomes 2018-05-18 +28.571 tỷ), prereg
  ngưỡng; kiểm (a) có fire trước/đúng 04/2018 không, (b) **fire nhầm bao nhiêu lần 2014-2017 và
  2019-2025** — đây là câu hỏi quyết định, không phải (a). Vai trò nếu sống: cap DT5G tầng 3
  (phòng thủ), không phải tín hiệu mua.
- **N thật:** 1-2 sự kiện độc lập (2018, có thể 2021-22). Dùng causal + judgment, không p-value.
  Kỳ vọng ΔCAGR ≈ 0 hoặc âm nhẹ (bảo hiểm).
- **Sống sau 28/09:** VNDirect từ 2018-08 KHÔNG tách khớp/thoả thuận — nếu chỉ báo sống, cần
  nguồn tách deal (chưa có) hoặc chấp nhận gross + lọc ngày deal thủ công.

### H5. Dòng tiền cá nhân/tự doanh/tổ chức → proxy sinh thái AMH (G4) + chỉ báo overreaction
- **Lỗ hổng:** `amh-adaptivity-review` G4 ghi "tỷ lệ retail, margin, tài khoản mới — KHÔNG có nguồn
  chuỗi nào"; job C đã đo hiệu quả thị trường mà thiếu trục ecology. Bộ E là chuỗi retail duy nhất.
- **Việc:** dựng series tháng `retail_net_share` (|cá nhân ròng| / tổng |5 nhóm|) và `retail
  capitulation` (cá nhân bán ròng z-score 20 phiên). Test **chỉ như BIẾN ĐIỀU KIỆN** (ecology
  làm tín hiệu hướng đã REFUTED 07-13): IC momentum/value theo tercile retail-share (khớp trục 2
  mặc định breadth-tercile PIT 08-22); và như ứng viên **điều kiện 3 của margin Loại-2** ("≥1 chỉ
  báo overreaction") bên cạnh VIX/breadth.
- **Bẫy:** 5 nhóm không cộng về 0 (đừng suy phần dư); cá nhân âm khổng lồ ngày deal (phía bán
  của lô thoả thuận); tổ chức có thể gồm tự doanh; 2026-09 provisional.
- **Sống sau 28/09:** **đây là bộ duy nhất không có nguồn thay thế.** Nếu H5 cho thấy giá trị điều
  kiện thật ⇒ đó là lý do DUY NHẤT đáng mở lại câu hỏi mua gói rẻ nhất. Chưa có kết quả thì không.

### H6. Tín dụng/M2 + tỷ giá tự do → registry lead-indicator của Bobby (XÁC NHẬN, không cổng)
- `vn-realestate-structural-risk` §88 đã kết luận chuỗi chính thức là "xác nhận muộn" — vì vậy
  không dựng cổng từ C/H. Việc đúng: nạp `credit_yoy`, `m2_yoy`, `fx_free_premium` (tự do − trung
  tâm) vào bảng lead-indicator + `vn_macro_regime_history` để phân loại lại 2009-2012 (tín dụng
  30%+ = Loại 1 cấu trúc) vs 2020/2022 (Loại 2) bằng SỐ thay vì hồi ức. Review quý 11-26 dùng luôn.
- Tỷ giá tự do 2012-2026: kiểm premium có spike TRƯỚC 2022-11 và 2024 không — nếu có, đó là ứng
  viên "market-based early warning" §88 nhắc tới; N≈3 episode ⇒ chẩn đoán, không luật.
- Bẫy: tiền gửi gãy 10/2025; tỷ giá tự do không có nguồn sống sau trial.

### H7. GDP danh nghĩa → Value Radar (DISPLAY-ONLY)  — thấp
Vốn hoá/GDP làm dòng tham chiếu trong Value Radar; lịch sử 8 năm + gãy 2021 ⇒ chưa đủ cho bất kỳ
kết luận nào. Không dispatch riêng; ghép vào lần sửa radar kế tiếp nếu có.

## 3. Thứ tự thực thi đề xuất + phân vai

| Bước | Việc | Ai | Khi | Cổng |
|---|---|---|---|---|
| 0 | Hợp nhất G/H thành CSV + registry + nghiệm thu PIT OShares vs corp-action | Mike | trước 28/09 | §9 |
| 1 | H1 bank route 8L A/B | Taylor (dispatch, opus/high) | tuần 28/09 | quant-skeptic → user |
| 2 | H2 CPI vào macro_confidence_regime + DCF | Taylor | cùng tuần | quant-skeptic → user |
| 3 | H4 chỉ báo 2018 (Bobby BLIND trước) | Bobby → Taylor | tuần 05/10 | causal + judgment |
| 4 | H5 retail ecology | Taylor | tuần 05/10 | chỉ điều kiện, không hướng |
| 5 | H3 OShares PIT re-pin | Taylor | khi rảnh | ΔR3≈0 là PASS |
| 6 | H6 nạp Bobby registry | Bobby | trước review 11-26 | — |

Bước 1-2 gộp được thành **1 dispatch** (2 bước đã biết trước, không cần Mike phán đoán giữa chừng —
quy tắc cost-opt #3). Bước 3-4 KHÔNG gộp: 4 phụ thuộc cách đọc kết quả 3.

## 4. Mua hay không mua — cập nhật sau harvest

Không mua. Lý do bằng số: 7/9 bộ có nguồn nối tiếp miễn phí (GSO/NHNN/OCR/VCB) hoặc chỉ cần lịch
sử; 2 bộ không có nguồn thay thế (dòng tiền nội địa theo nhóm, tỷ giá tự do) chưa chứng minh được
giá trị cho ARIA. Điều kiện mở lại câu hỏi: H5 cho kết quả điều kiện hoá có ý nghĩa qua
quant-skeptic. Khi đó mới hỏi giá gói thấp nhất — và vẫn so với chi phí OCR/scrape thay thế.

## 5. Không lấp được (giữ nguyên workaround)
SBV refi rate, lợi suất TPCP, lãi suất huy động từng NH theo ngày, TPDN BĐS late-payment (P5 chưa
kịp dò trước khi trần ngày ăn hết quota). Không đưa vào đề xuất.
