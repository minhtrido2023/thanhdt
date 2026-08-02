---
kind: bigquery-column
status: CANONICAL
source: PE / PB / PCF / PS (cột trong ticker + ticker_financial)
group: fundamentals
note: công thức đã verify bằng tính tay (job Winston_20260717_063633); cơ sở giá = Price THÔ cho MỌI cột (PE/PB/PCF/EVEB/DY/PS/PEG), xác nhận 2007-2026 job Taylor_20260802_083624 — xem Bẫy (4)(6)(7)
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
  chưa nhiễm; nhưng **bất kỳ lần rebuild lịch sử nào từ `tav2_bq.ticker` sẽ nhiễm**. ✅ **ĐÃ SỬA
  2026-08-02** (gỡ `_pe_adj_factor`, commit `beec96c`, quant-skeptic CONFIRMED high) — lỗi đã ĐÓNG.
- `custom_basket.py::_yield_piv` đọc thẳng `AVG(1/PE)` **KHÔNG nhân hệ số — ĐÚNG**, đừng "sửa".
- Job `Taylor_20260802_042110` (`value_regime_crosssectional_20260802.md` §5) kết luận ngược lại
  (nói `PE` có look-ahead) — **§5 của file đó ĐÃ BỊ BÁC BỎ**; các số "đã sửa" +0,096 / +0,034 là số
  ĐÃ NHIỄM, số đúng là +0,125 (toàn universe) / +0,088 (trong cổng production).

**(5) `ps` tự tính trong `rating_8l.py` dùng `Close × OShares / Revenue_ttm`** — `Close` là chuỗi ĐÃ
điều chỉnh còn `OShares` là số cổ phiếu **của kỳ báo cáo hiện hành** ⇒ market-cap hàm ý sai ở dữ liệu
lịch sử (cùng họ vấn đề với (4), chiều ngược lại). Live không ảnh hưởng. ✅ **ĐÃ SỬA 2026-08-02**
(sang cơ sở `Price`, commit `6ea466f`, quant-skeptic CONFIRMED high): trước khi sửa, trung vị
`sales_yield` lệch 47,5-56,7%, Spearman 0,889-0,909, 10-15/30 tên rẻ-nhất-theo-PS bị đổi.

**(6) ✅ RÀ SOÁT MỞ RỘNG 2026-08-02 (job `Taylor_20260802_083624`) — TẤT CẢ cột định giá lưu sẵn đều
trên cơ sở `Price` thô, xác nhận liên tục 2007→2026.** Đóng lỗ hổng "chưa kiểm trước 2014" mà
quant-skeptic nêu. Báo cáo đầy đủ + bằng chứng:
`mike/agents/Taylor/research/pe_pb_basis_broad_audit_20260802.md` (SQL thô: `WorkingClaude/exp_basis_audit/`).
- **PE = `Price`/EPS_ttm tái lập 100,0% MỖI NĂM 2007-2026** (n≈2,9tr dòng; cơ sở `Close` 1,1-67%).
- **PB = `Price`/BVPS** (trong-kỳ 96,7% pre-2014 / 95,0% sau, vs `Close` 5,7%/19,2%).
- **PCF** trong-kỳ 84,8%/88,8% vs `Close` 18,2%/24,0% (phủ dày chỉ từ 2013).
- **EVEB = (`Price`×OShares + NetDebt)/`EBITDA_P0`** — phép thử ĐỘ DỐC (EVEB affine theo giá nên
  tỉ-số-hằng-số KHÔNG áp dụng): `dEVEB/dPrice` khớp `OShares/EBITDA_P0` ở **95,6%/95,4%** kỳ, sai số
  tương đối trung vị **0,00000**; `Close` chỉ 4,8%/19,0%.
- **DY = `Dividend_1Y` / `Price`, là PHÂN SỐ không phải %** — tái lập **100,0% mỗi năm 2008-2026**
  (VNM 2012-05-02: DY×Price = 4.000 VND tròn; DY×Close = 578,6 vô nghĩa).
- **PS = `Price`×OShares/Rev_ttm 100,0% mỗi năm 2007-2026** · **PEG = PE/(g×100) 100,0% mỗi năm** ⇒
  PEG kế thừa cơ sở của PE, tự động đúng.
- **`Dividend_Min3Y` là VND danh nghĩa THÔ** ⇒ `rating_8l` `div_yield = Dividend_Min3Y/Price` ĐÚNG.
- Sức phân giải phép thử đã đo trước khi tin: `Close/Price` đổi trong kỳ ở 94,2% kỳ (2007-2013) /
  80,8% (2014-2026); trung vị `Close/Price` 0,219 (2007) → 1,000 (2026) ⇒ **pre-2014 là vùng phân
  giải MẠNH NHẤT**, không phải vùng mù. **Trước 2007 KHÔNG kiểm định được** (PE/PB/PCF/EVEB toàn NULL).
- Ghi nhận riêng (KHÔNG phải lỗi cơ sở giá): **`PB` tái lập chỉ 59-69% ở 2015-2017 ở CẢ 2 bảng** —
  lệch **vintage `BVPS`**, đáng mở ticket riêng.

**(7) ⚠️ CƠ SỞ ĐÚNG CHO THANH KHOẢN/VỐN HOÁ TỰ TÍNH = `Price`, KHÔNG PHẢI `Close` — lỗi cùng họ CÒN MỞ
trong CODE (chưa sửa, phát hiện 2026-08-02).** `Trading_Value = Volume × Price` khớp **100,0% mỗi năm
2010-2026** (`Volume × Close` chỉ 1-70%) ⇒ `Volume` là số cổ phiếu THÔ, và `OShares` cũng là PIT thô.
Vì vậy `Volume_3M_P50 * Close` và `Close * OShares` là **biểu thức TRỘN CƠ SỞ**, mang look-ahead
(hệ số `Close/Price` phụ thuộc cổ tức/thưởng xảy ra SAU ngày t, khác nhau giữa các mã).
- **`custom_basket.py` (PRODUCTION, custom30V)**: chọn rổ `AVG(Volume_3M_P50*Close)` (dòng 163/249) và
  trọng số `mcap = Close*OShares` (183/1077/716). Đo được: **8,46/30 tên rổ đổi (2008-2013), 5,04/30
  (2014-2026)**; lệch trọng số TB 1,62pp / max 8,59pp, Spearman 0,762 (pre-2014).
  ⚠️ **KHÔNG "sửa" bằng cách thay `Close`→`Price` toàn file** — chuỗi *lợi suất*
  `mcap_t/mcap_{t-1}` BẮT BUỘC giữ `Close` (nếu không, ngày chốt quyền thành LỖ giả). Bản sửa đúng =
  tách vai: trọng số/sàng lọc dùng `Price`, lợi suất giữ `Close`. **Cần kế hoạch riêng + A/B backtest +
  quant-skeptic** (đổi số R3 đã pin). Cùng dòng 175 của chính file này đã dùng `COALESCE(Price,Close)*Volume`
  cho ADV — file tự mâu thuẫn.
- `lag_liquidity_filter.py:100` (wired production) + `score_live_signals.py:157/411`: cùng lỗi nhưng
  **live impact = 0** (đọc as-of hôm nay, `Price==Close`) — sửa vệ sinh, không khẩn.
- ~22 script nghiên cứu (`test_fa_*` với `smoothed_EY = NP_ttm/OShares/Close`, `sim_*`, `test_round*`,
  `lag_dnpr_harness.py`, `converge_fullharness_test.py`) kế thừa lỗi ⇒ **kết luận IC lịch sử của chúng
  chưa tin cậy**, đặc biệt `test_fa_ic_2007_2013_crisis.py` / `test_fa_ic_regime_2008_2026.py`.
- `value_radar.py` (`Price*OShares`) và `dcf_valuation.py` (`Price`) **ĐÚNG — đừng "sửa"**.
