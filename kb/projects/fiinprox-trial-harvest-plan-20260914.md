# FiinPro-X trial — kế hoạch khai thác + đối chiếu lấp lỗ hổng dữ liệu (mở 2026-09-14)

**Hạn cứng: trial hết 2026-09-28.** Sau đó không gọi lại được FiinXMCP trừ khi mua.
**Ràng buộc kỹ thuật:** MCP tool CHỈ gọi được trong phiên Mike tương tác (OAuth), KHÔNG qua
`bin/dispatch.sh` headless ⇒ Mike tự harvest; Taylor đối chiếu trên CSV đã lưu.
**Phạm vi:** chỉ lấy dữ liệu + đối chiếu + đăng ký `kb/data_registry/`. KHÔNG wire production trong
kế hoạch này — mọi thay đổi consumer (rating_8l, DT5G, deposit tilt...) là quyết định riêng sau,
qua quant-skeptic như thường lệ.

## 1. Kiểm kê lỗ hổng (Explore agent, 21 gap) × độ phủ FiinPro-X (dò thật 2026-09-14)

| # | Lỗ hổng hiện có | Sev | FiinPro-X (đã dò thật) | Phủ |
|---|---|---|---|---|
| 1 | Bank ratios: `bank_lens_v3` NPL/CAR/coverage/CASA = NaN, OCR tay 9/18 NH; BQ không có cột NH | HIGH | NPL(3-5)/NIM **theo quý từ ≥2010**; CASA đã verify khớp OCR 12/13; CAR theo năm (CapitalAdequacyReport) | ✅ ĐỦ |
| 2 | Khối ngoại: VNDirect chỉ từ 2018-08-30, không tách khớp lệnh/thỏa thuận (méo Vinhomes 2018) | HIGH | `fetch_trading_data` fb/fs/fn **ngày từ ≥2009-06** (2007 = 0); `value_by_investor` **tách matched/deal + tự doanh + tổ chức trong nước từ ≥2014** | ✅ ĐỦ (+ lấp luôn gap tự doanh) |
| 3 | `ticker_financial.OShares` RESTATE, không PIT | HIGH | `get_market_statistics freefloat.outstanding_share` **chuỗi ngày, đổi đúng ngày sự kiện** (MBB 1,600→1,631 tỷ cp ngày 2016-03-21); có từ **≥2013** (2010 null) | 🟡 MỘT PHẦN (2013+, cần verify PIT) |
| 4 | CPI: 2011-01→2025-05 nội suy tuyến tính ~36 điểm; 2007-10 ước CEIC | HIGH | CPI YoY **thật theo tháng từ ≥2011**, 11 nhóm hàng + lạm phát cơ bản (từ 2015-06) + chỉ số giá vàng + USD | ✅ ĐỦ (2011+) |
| 5 | Lãi suất huy động: 26 mốc bậc thang dựng 1 ngày, không PIT | HIGH | `deposit_lending_movement` (bình quân NHNN) **chỉ 12 tháng** (2025-08→2026-07); `other_bank_interest_rates` (từng NH, theo ngày) CHƯA dò | 🟡 CHƯA RÕ |
| 6 | SBV refi rate hardcode, trước 2011 lệch ±1-2 tháng | HIGH | Không thấy trong `state_bank_interest_rates` (đó là LS thị trường bình quân) | ❌ CHƯA THẤY |
| 7 | Lợi suất TPCP: 26 số trung bình năm ước tay | HIGH | Discovery không trả chuỗi TPCP; `get_bonds` là TPDN | ❌ CHƯA THẤY |
| 8 | Giá ngày GDKHQ copy giá cũ im lặng | HIGH | OHLCV adjusted/unadjusted = nguồn đối chiếu thứ 2 | 🟡 ĐỐI CHIẾU |
| 9 | Tín dụng/M2 không có chuỗi | MED | M2/dư nợ YoY theo tháng: tổng từ ≥2012, tách ngành từ ≥2018 | ✅ ĐỦ |
| 10 | USD/VND `macro_usdvnd.csv` dừng 2026-04-29 | LOW→MED | Tỷ giá trung tâm + VCB **theo ngày từ ≥2012** | ✅ ĐỦ |
| 11 | Margin debt / tỷ trọng cá nhân | MED | `value_by_investor.localIndividual*` = null năm 2014, năm gần chưa dò | 🟡 CHƯA RÕ |
| 12 | Giá vàng (không có chuỗi) | LOW | Chỉ số giá vàng trong CPI theo tháng (KHÔNG phải premium SJC) | 🟡 MỘT PHẦN |
| 13 | TPDN BĐS — lead indicator "vi phạm TPDN BĐS 12m" của `vn-realestate-structural-risk` đang không có số | MED | `get_bonds` late_payments / outstanding theo ngành | 🟡 CHƯA DÒ (khả năng cao có) |
| 14 | GDP danh nghĩa; VNINDEX_PE 2007-2016; corp-action `exercise_ratio` NULL 42% | MED | Chưa dò | ⚪ CHƯA DÒ |

## 2. Kế hoạch 5 pha (thứ tự = giá trị × dễ lấy; mỗi pha tự đứng được nếu dừng giữa chừng)

**Kỹ thuật chung:** dùng `execute_api` (sandbox) để in CSV GỌN — chỉ cột cần, chỉ dòng có thay đổi
(event-only cho OShares) — tránh JSON thô chiếm context. Lưu `data/fiinprox_<tên>_<YYYYMMDD>.csv`
(tên không canonical, §8) + 1 entry `kb/data_registry/` mỗi nguồn, status khởi điểm UNVERIFIED.

**P1 — Vĩ mô nhỏ (15-16/09, ~2h).** CPI tháng full + nhóm + lõi (#4), M2/tín dụng tháng (#9), tỷ giá
trung tâm ngày (#10), GDP danh nghĩa quý (#14).
- Đối chiếu: CPI vs 13 điểm NSO thật 2025-06→2026-06 trong `cpi_vn.py` (khớp ⇒ nâng DERIVED);
  USD/VND vs `vcb_fx_feed.py` phần chồng lấn.
- Mở khoá: bỏ tầng nội suy Tier-2 CPI 2011-2025 (quyết định riêng sau).

**P2 — Ngân hàng theo quý (16-19/09, ~3h).** Toàn bộ `BANKS_L2` niêm yết × quý 2010Q1→2026Q2:
NPL(3-5), NIM, CASA, LLR coverage; CAR theo năm. Mở rộng file 9 mã hiện có.
- Đối chiếu: NPL/coverage vs 9 NH OCR tay trong `bank_lens_v3`; CASA đã verify.
- Mở khoá: NaN của route BANK trong `rating_8l` (#1).

**P3 — Dòng tiền theo nhà đầu tư cấp chỉ số (19-23/09, ~3h).** VNINDEX + HNXINDEX: fb/fs/fn ngày
2008→2026; `value_by_investor` 2014→2026 (khớp lệnh vs thỏa thuận, tự doanh, tổ chức, cá nhân).
- Đối chiếu: vs feed VNDirect phần chồng lấn 2018-08→2026; tách deal kiểm tra lại ngày Vinhomes 2018.
- Mở khoá: câu hỏi mở "thử được cú bán 2018 không" (`production_mechanism_2009_2018_20260830.md` B.1)
  + gap tự doanh (#2).

**P4 — OShares PIT (23-26/09, ~3h).** `outstanding_share` cho mã `universe_pit` 2013→2026, chỉ lưu
ngày thay đổi.
- Đối chiếu: vs `tav2_bq.corporate_action` (ngày sự kiện) + 2.667 dòng restate đã biết của
  `ticker_financial.OShares`. PIT thật = ngày đổi khớp ngày GDKHQ/niêm yết bổ sung, không khớp
  ngày BCTC.
- Mở khoá: `oshares_live.py` bớt trả rỗng (#3). Per-ticker khối ngoại chỉ làm nếu P1-P4 xong sớm.

**P5 — Dò nốt + TPDN (26-27/09, ~1h).** `get_bonds` late_payments/outstanding ngành BĐS (#13, nuôi
review tháng BĐS); `other_bank_interest_rates` độ sâu (#5); retry TPCP/refi rate 1 lần với top_k lớn
(#6, #7); VNINDEX P/E lịch sử (#14); `localIndividual` năm gần (#11).

**28/09:** đệm + tổng kết: bảng "đã lấy / đã verify / còn thiếu" + khuyến nghị mua/không mua cập nhật.

## 3. Phân vai
- **Mike:** gọi MCP + lưu CSV + registry UNVERIFIED (chỉ phiên này làm được).
- **Taylor (dispatch):** đối chiếu trên CSV đã lưu, nâng/hạ status, viết finding.
- **quant-skeptic:** CHỈ khi sau này đề xuất wire nguồn mới vào consumer production.

## 4. Không lấp được bằng FiinPro-X (tới lúc dò)
SBV refi rate (#6), lợi suất TPCP (#7) — giữ workaround hiện tại, P5 retry 1 lần rồi chốt.
