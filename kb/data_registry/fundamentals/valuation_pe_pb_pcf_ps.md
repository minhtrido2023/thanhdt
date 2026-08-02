---
kind: bigquery-column
status: CANONICAL
source: PE / PB / PCF / PS (cột trong ticker + ticker_financial)
group: fundamentals
note: công thức đã verify bằng tính tay (job Winston_20260717_063633); cơ sở giá = Price THÔ, re-verify quy mô universe job Taylor_20260802_054825 — xem Bẫy (4)
writer: Ingest ETL, cùng cadence ticker_financial
---

# PE / PB / PCF / PS (cột trong `ticker` + `ticker_financial`)

**Status: CANONICAL — công thức đã verify**

## Là gì
Định giá "tự tính từ tài chính thô" (bq_admin đổi từ nguồn bên-thứ-3 sang self-computed, ~2026-07).
**Công thức xác nhận bằng tính tay** (job Winston_20260717_063633): **PE = Price / EPS_ttm** (EPS_ttm =
Σ(NP_P0..P3)/OShares, 4 quý trailing) · **PB = Price / BVPS** · **PCF = Price / CF_ttm** · PS =
Price/Rev_ttm. Nhất quán giữa `ticker` daily và `ticker_financial` quarterly; ngân hàng dùng cùng công
thức NP-based. VNM/MBB khớp tới 4 chữ số.

## Ai ghi / cadence
Ingest ETL, cùng cadence `ticker_financial`.

## Bẫy
**(1) KHÔNG hồi tố** — verify toàn universe (~1260 mã × 2 ngày lịch sử 2023-06-01/2024-01-15) so
snapshot pre-change `bq_cache/ticker/*.parquet` (June-25) vs BQ live: PE/PB/PCF/BVPS + PE_MA5Y/PB_SD5Y
**giống hệt >99.7%** (0 PB đổi, ≤2 PE, ≤3 PCF>1% toàn mã illiquid); `ticker_financial` PE/PB/PS/PCF
100% identical July-8 vs July-16. → **mọi backtest đã pin + rating_8l an toàn, lịch sử KHÔNG bị viết
lại**. **(2) Negative PE/PCF là bình thường & PRE-EXISTING** — mã lỗ → PE âm (52/797 mã), CF hoạt động
âm → PCF âm (236/797); KHÔNG NULL-hóa (rating_8l đã tự guard: `cfo_yield` chỉ 1/PCF khi PCF>0). **(3)
`bigquery_dictionary.json` STALE**: ghi range "0..Inf" cho PE/PB/PCF nhưng thực tế có âm; và KHÔNG ghi
provenance self-computed — cần cập nhật (non-blocking).

**(4) ⚠️ CƠ SỞ GIÁ = `Price` THÔ (point-in-time ĐÚNG) — TUYỆT ĐỐI KHÔNG nhân thêm `Price/Close`.**
`PE`/`PB`/`PCF` trong `tav2_bq.ticker` được tính trên **`Price` (giá thô của CHÍNH ngày đó)**, KHÔNG
phải trên `Close` (chuỗi đã điều chỉnh cổ tức/split về hiện tại). Vì vậy `1/PE` đọc thẳng từ bảng **đã là
earnings-yield point-in-time đúng, KHÔNG có look-ahead** — dùng trực tiếp cho xếp hạng cross-sectional
lịch sử.

*Bằng chứng (job `Taylor_20260802_054825`, verify quy mô universe 2014–2021, 1.419.351 dòng /
23.067 cặp (ticker × kỳ báo cáo `ID_Release`)):* trong mỗi kỳ báo cáo, `PE/Price` **hằng số** ở
**93,1%** số kỳ (trung bình 1,22 giá trị khác nhau — phần dư là do `OShares` đổi giữa kỳ), còn
`PE/Close` chỉ hằng số ở **11,0%** (trung bình 17,8 giá trị). Đối chiếu tay: VNM 2015-06-30
`Price`=113.000, `PE`=18,116 → EPS hàm ý 6.237,5 = **đúng** `Σ(NP_P0..P3)/OShares` = 6.237,5 (từ
`ticker_financial` 2015Q1); tính từ `Close`=32.510 sẽ ra EPS 1.795 — vô lý. FPT 2015-06-30 khớp
tương tự (46.400/10,900 = 4.256,9 = NP_ttm/OShares). Cùng phép thử cho **`PB`: 94,6% vs 12,6%** và
**`PCF`: 86,9% vs 20,3%** (17.944 kỳ / 1.104.345 dòng) ⇒ cả 3 cột cùng một cơ sở giá thô.
⚠️ **`tav2_bq.ticker` KHÔNG có cột `PS`** (dù `CLAUDE.md` liệt kê) — `PS` chỉ tồn tại ở
`tav2_bq.ticker_financial`; script nào cần sales-yield lịch sử phải tự tính, xem (5).

*Bẫy ngược — lỗi đã xảy ra thật 2 lần:* vì `Price/Close` **trông giống** hệ số điều chỉnh tích luỹ
tới hôm nay (trung vị 2,31 ở 2014 → 1,00 ở 2026), rất dễ kết luận nhầm rằng `PE` "bị điều chỉnh" và
phải chia lại. **Nhân `PE` với `Price/Close` là ĐƯA look-ahead VÀO**, không phải khử: hệ số đó phụ
thuộc các sự kiện chia cổ tức/thưởng **XẢY RA SAU** ngày t, khác nhau giữa các mã ⇒ bóp méo thứ hạng
cross-sectional lịch sử bằng thông tin tương lai.
- `rating_8l.py` (dòng ~521–524, `_pe_adj_factor`) **đang làm đúng phép nhân sai này**, kèm comment
  sai "PE_stored = Close_adj/EPS". Tác động LIVE ≈ 0 (hôm nay `Price≈Close` ⇒ hệ số ≈1) và bảng
  lịch sử `fa_ratings_8l` là snapshot **ghi nối tiếp từng ngày** (mỗi dòng viết lúc hệ số ≈1) nên
  chưa nhiễm; nhưng **bất kỳ lần rebuild lịch sử nào từ `tav2_bq.ticker` sẽ nhiễm**. Đây là lỗi
  MỞ, chưa sửa (sửa `rating_8l.py` = chạm production, cần user duyệt + quant-skeptic).
- `custom_basket.py::_yield_piv` đọc thẳng `AVG(1/PE)` **KHÔNG nhân hệ số — ĐÚNG**, đừng "sửa".
- Job `Taylor_20260802_042110` (`value_regime_crosssectional_20260802.md` §5) kết luận ngược lại
  (nói `PE` có look-ahead) — **§5 của file đó ĐÃ BỊ BÁC BỎ**; các số "đã sửa" +0,096 / +0,034 là số
  ĐÃ NHIỄM, số đúng là +0,125 (toàn universe) / +0,088 (trong cổng production).

**(5) `ps` tự tính trong `rating_8l.py` dùng `Close × OShares / Revenue_ttm`** — `Close` là chuỗi ĐÃ
điều chỉnh còn `OShares` là số cổ phiếu **của kỳ báo cáo hiện hành** ⇒ market-cap hàm ý sai ở dữ liệu
lịch sử (cùng họ vấn đề với (4), chiều ngược lại). Live không ảnh hưởng. Chưa đo tác động — ghi ra
đây để lần sau không phải phát hiện lại.
