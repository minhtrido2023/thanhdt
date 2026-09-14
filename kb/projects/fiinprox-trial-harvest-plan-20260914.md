# FiinPro-X trial — kế hoạch khai thác + đối chiếu lấp lỗ hổng dữ liệu (mở 2026-09-14)

**Hạn cứng: trial hết 2026-09-28.** Sau đó không gọi lại được FiinXMCP trừ khi mua.
**Ràng buộc kỹ thuật (ĐÍNH CHÍNH 2026-09-14 22:3x):** headless `claude -p` CŨNG gọi được FiinXMCP (connector
claude.ai của account, test thật) ⇒ harvest cơ khí chạy TỰ ĐỘNG qua cron (§2c); Mike chỉ dựng CSV/đối chiếu.
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

## 2b. Chống giới hạn tải (user duyệt plan 2026-09-14 kèm yêu cầu này)
FiinX không công bố hạn mức ⇒ giả định có trần theo lượt + dung lượng, và trial "hạn chế tải
file excel". Luật:
1. **Tuần tự, không song song** — 1 lệnh MCP một lúc.
2. **Chunk ≤10 năm / lệnh**, filter + `fields` server-side (vd CPI: lọc 4 `type_name` thay 11 nhóm).
3. **Không tải lại**: CSV đã có trong `data/fiinprox_*` ⇒ bỏ qua; ghi CSV NGAY sau mỗi chunk
   (atomic) để dừng giữa chừng không mất.
4. **Gặp lỗi quota/429/"limit" ⇒ DỪNG pha đó ngay**, ghi mốc dừng vào mục 5 dưới, sang ngày.
5. Ưu tiên tool trực tiếp (`get_economy`, `fetch_trading_data`) hơn `execute_api` (sandbox FiinX
   từng hết đĩa `[Errno 28]` 14/09). Không tải Excel/ảnh qua web UI.
6. Chuỗi ngày dài (khối ngoại, outstanding_share) ⇒ lấy theo năm; outstanding_share lưu event-only.

## 2c. Harvest tự động (user yêu cầu 2026-09-14 22:28, không nhập tay)
- Cron `7,27,47 * * * *` → `bin/fiinprox_harvest_tick.sh tick`: mỗi tick 1 task trong `state/fiinprox_harvest/queue.json`.
- Headless `claude -p --model sonnet --allowedTools mcp__claude_ai_FiinXMCP__execute_api --output-format stream-json`;
  dữ liệu đọc NGUYÊN VĂN từ tool_result (model không chép số) → validate → ghi raw atomic.
- Hàng đợi hiện tại: 30 lô OShares (20 mã/lô, từ index 70) + 15 năm tỷ giá USD tháng 2012-2026.
- Luật: 429 → cooldown 65′; [Errno 28] → thử lại tick sau (tối đa 3 lần gọi/tick, không làm failed); 504 → tách
  lô; lỗi khác ≥6 → failed + báo; usage ≥85% → bỏ tick; tự dừng sau 2026-09-27. Báo `vn_macro_watch` khi xong nhóm/failed.
- Chi phí đo: ~0,13 USD/tick (5 turn). Thêm task mới: sửa `cmd_init` rồi `fiinprox_harvest_tick.py init` (idempotent).
- Việc KHÔNG tự động: dựng CSV/đối chiếu/registry (cần phán đoán) — Mike làm khi được báo.

## 5. Nhật ký tiến độ
- **P1 CPI ✅ 14/09** — `data/fiinprox_cpi_monthly_20260914.csv` (224 tháng, 2 lệnh), registry
  `macro/fiinprox_cpi_monthly.md` DERIVED. T2 nội suy `cpi_vn.py` lệch tới 2,51pp (2019-09),
  T3 backfill tới 3,01pp (2009-10); `NSO_CPI_YOY_AVG_REAL` thực chất là lạm phát cơ bản.
- **P1 tín dụng/M2 ✅ 14/09** — `data/fiinprox_money_credit_monthly_20260914.csv` (161 tháng, 2 lệnh). Tín dụng
  cuối năm khớp NHNN. Bẫy: tiền gửi TCKT/dân cư gãy chuỗi 10/2025 (đổi phân loại).
- **P1 GDP danh nghĩa ✅ 14/09** — `data/fiinprox_gdp_nominal_quarterly_20260914.csv` (4 lệnh, 1/quý vì provider
  không cross-join year×quarter). Tổng năm khớp GSO; gãy chuỗi 2020→2021 (đánh giá lại GDP).
- **P1 tỷ giá ⏸ HOÃN** — `get_economy` exchange_rate chỉ trả ~2 tháng/lệnh (14 năm = ~85 lệnh, quá tốn);
  `execute_api` (có `time_frequency=Monthly`, 12 điểm/năm) chạy được 1 lần rồi lỗi `[Errno 28]` hết đĩa
  sandbox FiinX 3 lần liên tiếp. Thử lại execute_api 1 lệnh/năm vào 15/09; nếu vẫn lỗi ⇒ bỏ (gap LOW,
  đã có `vcb_fx_feed.py`). Bonus nếu lấy được: giá USD thị trường tự do từ 2013.
- **P2 ngân hàng theo quý ✅ 14/09** — `data/fiinprox_bank_ratios_quarterly_20260914.csv` (27 mã, 1.392 dòng,
  6 lệnh `execute_api` 4-7 mã/lệnh; 1 lần lỗi `[Errno 28]` ở lô 7 mã → chia nhỏ là qua). Coverage khớp OCR
  8/9 mã; NPL cao hơn OCR +1-2% tương đối. CAR theo quý không có (chỉ năm). Registry
  `fundamentals/fiinprox_bank_ratios_quarterly.md`. Kỹ thuật rút ra: `get_fundamental_data` trả JSON
  ~150 token/dòng ⇒ dùng sandbox in CSV nén (~12 token/dòng).
- **P3 (b) ✅ 14/09 19:4x** — `data/fiinprox_vnindex_investor_flow_daily_20260914.csv` (3.165 phiên, 2014→2026-09-14,
  13 lệnh 1 năm/lệnh, ~50% lệnh lỗi `[Errno 28]` → thử lại là qua). Ngoại ròng khớp VNDirect 2024-2025 median
  1,9 tỷ/phiên; FiinPro lấp các phiên VNDirect trả 0. Registry `feeds/fiinprox_vnindex_investor_flow_daily.md`.
- **P3 (a) ✅ 14/09 22:0x** — `data/fiinprox_foreign_flow_index_daily_20260914.csv` 2.313 phiên 2009-06→2018-08
  (VNINDEX mua/bán tới 2015, HNX ròng tới 2018-08). Nhất quán nội bộ 2014-2015 495/495 ≤1 tỷ. **P3 ĐÓNG.**
- **P4 ⏸ 14/09 22:4x — CHẠM HẠN MỨC GIỜ** — `get_freefloat` (`client.PriceStatistics()`) cho 655 mã có ≥250 phiên
  `universe_pit` từ 2013 (danh sách `data/fiinprox_oshares_raw/tickers.txt`, sắp mã còn sống trước). Đã lưu **70/655**
  (`data/fiinprox_oshares_raw/b000..b050.txt`, chỉ mốc đổi số CP, đã lọc 'nháy' ≤5 phiên quay về giá trị cũ).
  Lỗi thật đo được: lô 30 mã → 504 gateway timeout; lô 20 mã chạy được; sau ~6 lô thành công →
  **429 'You have reached the hourly request limit'** trên `apigw.fiingroup.vn/FXMA/TradingData/...`. Nguyên nhân khả dĩ:
  API phân trang theo từng mã × trang (13 năm/mã) ⇒ mỗi lô 20 mã = hàng chục request. Theo luật 2b.4: DỪNG ngay.
  Tiếp tục 15/09: ≤4 lô/giờ (80 mã/giờ), giãn cách; còn 585 mã ≈ 7-8 giờ đồng hồ trải qua 2 ngày. Có thể cần thu hẹp
  về 448 mã còn niêm yết 2026 nếu hạn mức chặt.

## 3. Phân vai
- **Mike:** gọi MCP + lưu CSV + registry UNVERIFIED (chỉ phiên này làm được).
- **Taylor (dispatch):** đối chiếu trên CSV đã lưu, nâng/hạ status, viết finding.
- **quant-skeptic:** CHỈ khi sau này đề xuất wire nguồn mới vào consumer production.

## 4. Không lấp được bằng FiinPro-X (tới lúc dò)
SBV refi rate (#6), lợi suất TPCP (#7) — giữ workaround hiện tại, P5 retry 1 lần rồi chốt.
