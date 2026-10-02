# Charter — AlphaLens Paper (FPT/ACB/MBB/HDB vs VNINDEX) (`alphalens`)

> File TỰ SINH từ `mike/kb/paper_programs_registry.json` bởi
> `mike/bin/paper_programs_daily_report.py`. **Đừng sửa tay** — sửa registry rồi chạy lại
> report. Đây là nơi giữ mục đích/phương pháp/tiêu chí nghiệm thu ĐẦY ĐỦ để báo cáo hàng
> ngày chỉ link tới, không paste lại mỗi ngày. (registry v3)

- **Người phụ trách (owner):** DollarBill
- **Trạng thái:** review-done 2026-10-01 — chờ user quyết bước kế (KHÔNG tự wire live)
- **Bắt đầu:** 2026-07-01 · **Kết thúc dự kiến:** 2026-09-30

## 🎯 Mục đích

4 tên Tier-1 chọn bằng lens định giá (PE vs PE_MA1Y; PB vs Gordon justified-PB) có beat VNINDEX qua 3 tháng không? Buy-and-hold, equal-weight 25%/tên.

## 📅 Nghiệm thu / mốc kết thúc

2026-09-30 (audit: Taylor)

## ✅ Tiêu chí GO/NO-GO

- ✅ (pass) Excess return dương vs VNINDEX qua full window 3 tháng — AUDIT 2026-10-01 (job Taylor_20261001_004002), tái lập ĐỘC LẬP từ tav2_bq.ticker Close (không chỉ đọc probe): FPT −1,28% · ACB −6,84% · MBB −2,63% (terp) · HDB +6,38% ⇒ EW −1,09% vs VNINDEX −4,91% (1860,01→1768,62) ⇒ excess +3,82pp; accrue-only (bỏ quyền MBB) +2,80pp. Khớp từng chữ số với probe báo cáo 10-01. Leave-one-out đều dương (+1,33…+5,74). Giá vào 06-30 close KHÔNG giao dịch được (DollarBill chốt 22:15 ICT 06-30) ⇒ vào 07-01 open +3,65pp, 07-01 close +2,01pp (accrue-only +1,00pp; bỏ HDB ở biến thể này −0,21pp) — dương ở MỌI quy ước, nhưng biên mỏng ~1pp ở ca xấu nhất. Control cùng cửa sổ: EW top-30 ADV −7,28%, EW 13 ngân hàng thanh khoản (ngoài ACB/MBB/HDB) −7,48%. Hệ số FPT nay ổn định (Close/Price 0,90912 tại 06-30, min 0,90904) ⇒ KHÔNG còn là chặn dưới. quant-skeptic CONFIRMED/high. Script+output: mike/agents/Taylor/research/alphalens_audit_20261001/
- ✅ (pass) Exit conditions per-name không bị vi phạm sớm (PE > PE_MA1Y / PB > justPB) — AUDIT 2026-10-01: 63 phiên 07-01→09-30, 0 vi phạm. FPT PE 10,80–12,95 vs PE_MA1Y point-in-time theo Release_Date (18,69 tới 2026Q2 công bố 07-28, sau đó 16,33) ⇒ max PE/PE_MA1Y 0,782. Ngân hàng PB vs justPB=(ROE5Y−0,05)/0,08 đúng entry_condition (ACB 2,249 / MBB 2,211 / HDB 2,345) ⇒ max PB/justPB 0,621 / 0,633 / 0,711. Biên rộng, không nhạy với lựa chọn PIT.
- ✅ (pass) Audit độc lập bởi Taylor tại 2026-09-30 — Audit Taylor 2026-10-01 (trễ 1 ngày, dữ liệu chốt close 09-30), quant-skeptic CONFIRMED/high. Ex-ante xác nhận: bus DollarBill 2026-06-30T15:15Z (kb/archive/2026-W26-W27-raw-events.md) liệt kê đúng 4 mã + giá trước phiên 07-01 (data/alphalens_paper.json bị gitignore nên không chứng minh bằng git được).

## ℹ️ Ghi chú vận hành

Giá MTM từ BQ cache (close phiên gần nhất đã sync) — trong phiên sẽ trễ 1 ngày, đúng thiết kế EOD.

## 🔍 Nguồn dữ liệu kiểm chứng

- `data/alphalens_paper.json`
- `data/bq_cache/ticker_1m.parquet (Close + VNINDEX, sync 23:45 ICT)`
