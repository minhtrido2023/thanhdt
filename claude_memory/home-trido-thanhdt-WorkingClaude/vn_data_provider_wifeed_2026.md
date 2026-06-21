---
name: vn-data-provider-wifeed-2026
description: Khảo sát nhà cung cấp dữ liệu CK VN cho 8L + audit độ phủ WiFeed
metadata: 
  node_type: memory
  type: project
  originSessionId: 3610ea38-a57f-4356-8567-36b7b6105fa5
---

Nghiên cứu [REDACTED]14: tìm nguồn API dữ liệu tài chính VN giá hợp lý nhất cấp đủ dữ liệu 8L cần.

**Kết luận: WiFeed (WiGroup, wifeed.vn — nhánh API của WiChart/WiData) = tốt nhất về giá/độ-phủ.**
- API JSON thuần, 1.700+ DN, ~20 năm lịch sử, nguồn HOSE/HNX/SBV, mua theo gói nhỏ (rẻ hơn FiinPro 1-2 bậc).
- Đối thủ: FiinPro-X = 9tr/ID/tháng (~108tr/năm) + API Datafeed enterprise → quá đắt, và 8L KHÔNG cần phần "tính sẵn". Vietstock DataFeed = tầm trung, phải xin quote. SSI FastConnect = MIỄN PHÍ nhưng chỉ giá realtime, KHÔNG có BCTC. vnstock/TCBS = free nhưng scraping, dễ vỡ.
- Ba cả ba (WiFeed/Vietstock/FiinPro) đều KHÔNG public giá API → phải xin quote. WiFeed ☎1900 3109 / tuvan@wigroup.vn.

**Insight then chốt:** 8L chỉ cần mua 3 NGUỒN THÔ (OHLCV + BCTC quý thô + vĩ mô), rồi pipeline tự dựng ~190 cột phái sinh (ROIC5Y, FSCORE, PE_MA5Y, PB_z...). Không cần feed "đủ 200 cột tính sẵn" = phần đắt nhất.

**Kiến trúc đề xuất:** WiFeed (trả phí, lõi BCTC+giá+vĩ mô) + SSI FastConnect (free, realtime intraday) + vnstock (free, fallback). Bỏ FiinPro/Vietstock trừ khi cần bond/ownership chuyên sâu.

**Công cụ audit:** `wifeed_coverage_audit.py` đối chiếu schema WiFeed ↔ 170 cột `ticker_financial`. Offline chạy ngay (không cần key); `--probe` gọi WiFeed thật khi có WIFEED_APIKEY → xuất `wifeed_coverage_report.csv`.
- Kết quả: RAW 20.6% + DERIVABLE 68.2% = **WiFeed phủ ~89%**. GAP 11% (19 cột): `AdvCust_P0..P7` + `UnearnRev_P0..P7` (dòng CĐKT chi tiết, có thể bị gộp) + `Dividend_Min3Y/1Y/3Y` (cần lịch sử cổ tức). Các GAP đều là field PHỤ, không nằm trong golden signal/quality gate/FSCORE → lõi chiến lược vẫn dựng được; nếu thiếu thì giữ vnstock cho 3 nhóm này.
- Khi có key: cần chỉnh `WIFEED_ENDPOINTS` (path best-guess WiFeed v3) + tên raw field tiếng Việt trong `COVERAGE_MAP` cho khớp tài liệu thật.

**⚠️ NGÀNH (taxonomy) = rủi ro lớn nhất, CHƯA xác minh:** 8L dùng `ICB_Code` = mã FTSE-ICB 4 chữ số (VNM=3577, FPT=9537, HPG=1757, VCB=8355, GAS=7573; 75 mã ngành con, chuẩn HOSE/HNX). Cột này ở bảng `ticker` KHÔNG phải `ticker_financial` nên audit 89% ban đầu BỎ SÓT. WiFeed quảng cáo "150+ ngành cấp 1-4" (cấu trúc ICB) nhưng vendor VN hay dùng HỆ NGÀNH RIÊNG → nếu WiFeed trả mã không phải ICB 4 chữ số thì cần BẢNG CROSSWALK (WiFeed-sector→ICB_Code). Script đã thêm `check_industry_taxonomy()` + arg `--expect-icb` để so trực tiếp khi probe. Ngoài ra **nhóm 8L (bank/cyclical/compounder/power) KHÔNG vendor nào có** — tự dựng từ ICB + moat_tags.csv. Lệnh verify: `python wifeed_coverage_audit.py --probe --ticker VNM --expect-icb 3577`.

Liên quan: [[dnse-api-wrapper-2026]], [[phs-flex-api-wrapper-2026]], [[ticker-ingest-lag-ticker1m-switch]], [[moat-5f-8l-bridge-2026]].
