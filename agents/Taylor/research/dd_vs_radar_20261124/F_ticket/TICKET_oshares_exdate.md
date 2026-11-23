# TICKET — `tav2_bq.ticker.OShares` bước nhảy lệch ex-date

Job `Winston_20261123_174708` · 2026-11-24 · CHỈ ĐỌC (không ghi BQ, không sửa code).
Nguồn đề bài: quant-skeptic R1 mục 8 (599 sự kiện lệch >3 ngày). Tra `kb/data_registry/` trước:
`price-volume/corporate_action_bq.md` (Bẫy 1: exright vs AIS effective LỆCH XA), `fundamentals/valuation_pe_pb_pcf_ps.md`,
`price-volume/shares_outstanding_live.md`. SQL tái lập: `oshares_steps_match.sql`, `oshares_error_windows.sql` (cùng thư mục).

## 0. Kết luận (dòng đầu)
**Không có consumer chạm tiền nào bị ảnh hưởng đáng kể bởi lỗi này.** Đường tiền (custom30V weight → `compute_park_trim.py`) đọc
`ticker_financial.OShares` đã bước tại ex-date từ 2026-09-27 (`BASKET_OSHARES_STEP=exdate`, Taylor đo +0,04pp CAGR, rebal 2026-08-05 không đổi),
KHÔNG đọc `ticker.OShares`. Consumer đọc `ticker.OShares` thật: `value_radar.py` (display-only), `universe_scan.py`/`score_live_signals.py`
(`cf_yield`), `rating_8l.py` (`ps`, đã có `_reconcile_oshares`), `dna_card.py`. Ảnh hưởng đo được nhỏ và theo từng sự kiện (§3).
Hai điểm đề bài KHÔNG tái lập đúng như phát biểu: SIP (§1) và "TCB mcap ×2" chỉ đúng với cột `ticker.OShares`, không đúng `ticker_financial`.

## 1. Tái lập 3 ca (truy vấn trực tiếp BQ, 2026-11-24)
| Ca | `ticker.OShares` bước | Close/Price quanh bước | corporate_action | Lệch |
|---|---|---|---|---|
| **TCB** | 2024-05-20→05-21: 3.522.510.811 → 7.045.021.622 (×2,00); `PE` 8,87→16,86 trong 1 phiên | Price 49.700→47.200 (không đổi cấu trúc) ; Price chỉ giảm một nửa tại 2024-06-20 (48.300→24.800) | ISS "Cổ phiếu thưởng" ratio 1,0, **exright 2024-06-20**, record 06-21, public 06-13; AIS effective **2024-08-06** (7.045.021.622) | Bước **SỚM 30 ngày** so ex-date (22 phiên mcap ×2, PE ×2). `ID_Release` không đổi (1472) |
| **KLB** | 2025-07-31: 361.481.878 → 578.370.526 (×1,60) | Price 23.000 (chưa đổi) | ISS "Trả cổ tức bằng CP" ratio 0,6, **exright 2025-09-24**; AIS effective 2025-10-30 (582.170.526) | Bước **SỚM 55 ngày**. Bước thứ hai 2026-07-03 (×1,295) **đúng ex-date** (ISS 2026-07-03) |
| **SIP** | 2025-07-14: 212.064.323 → 242.113.413 (+14,2%) = **đúng ex-date** ISS 2025-07-14 (0,15) | — | OShares hôm nay 242.112.943 = AIS 2025-08-20 `shares_total_after` | **KHÔNG tái lập lệch OShares.** Không có sự kiện đổi số CP nào năm 2026 (chỉ DIV tiền mặt 4.000 ex 05-14, 4.500 ex 11-19). Hypothesis CHƯA kiểm: mcap "thấp ~10%" có thể là cổ tức 4.500 (≈10% giá) chứ không phải OShares |

Ghi chú đối chiếu Taylor 27/09 (`oshares_weight_exdate_20260927/README.md`): họ báo "TCB 2024-05-21 không tái lập" — đúng với **`ticker_financial.OShares`** (bước ở 2024-07-22, TRỄ 32 ngày). Bước 2024-05-21 nằm ở cột **`ticker.OShares`**, một chuỗi KHÁC. Hai chuỗi có cơ chế khác nhau; ticket 27/09 chỉ sửa chuỗi thứ nhất.

## 2. Cơ chế và độ phổ biến
- Đo bước `ticker.OShares` (|Δ| ≥ 5%) 2008-2026: 3.832 bước; khớp một ISS đã thực hiện (tỉ lệ khớp ±2%, cửa sổ ±150 ngày) = 2.194.
  Từ 2014: **1.857 khớp, 1.462 (78,7%) trong ±3 ngày ex-date**; 395 lệch >3 ngày (198 SỚM, 197 TRỄ), |lệch| min/p25/median/p75/max = 4/12/26/57/145 ngày.
  (599 của skeptic dùng định nghĩa/ngưỡng khác — không đối chiếu từng dòng; hướng và bậc độ lớn nhất quán.)
- **Theo thời kỳ**: 2008-2012 gần như TOÀN BỘ trễ ~75-93 ngày (chuỗi nhảy theo quý; 3-4/43-90 trong ±3 ngày); 2013 chuyển tiếp; từ 2014 chuyển sang bước theo ex-date. Tỉ lệ lệch >3 ngày/năm từ 2014 dao động 6-27%, **không giảm**: 2025 = 54/201, 2026 = 56/214.
- **Cụm ngày**: nhiều bước SỚM rơi 20-31/07 (và tương tự cuối quý) — vd 2026-07-31: TRC (×4,0, ex 09-15), NVL (×1,33, ex 09-30), HBC, BVB; khớp ngày công bố BCTC quý.
  Giả thuyết cơ chế (CHƯA kiểm bằng code ETL): cột lấy số CP từ BCTC quý (kỳ báo cáo đã mang số CP của đợt phát hành chưa đến ex-date) hoặc ngày đăng ký/thực hiện của vendor, rồi nhảy tại ngày cập nhật đó thay vì ex-date. `ticker_financial.OShares` còn được **restate** về sau (registry `oshares_live.py`: 2.667 dòng/576 mã mang số của AIS đến SAU, 626 dòng từ 2024-01).
  **TCB 2024-05-21 không giải thích được bằng giả thuyết này** (không có dòng quý nào đổi ngày đó, `ID_Release` giữ nguyên) ⇒ nguồn bước đó chưa xác định — cần chủ ETL (bq_admin) trả lời.
- Writer của `ticker.OShares` nằm NGOÀI repo Mike (như `corporate_action`); fleet không sửa được tại gốc.

## 3. Ảnh hưởng thực tế (cửa sổ lệch giữa ngày bước và ex-date, 2014-2026, 395 sự kiện)
Stock-ngày bị sai mcap (và PE/PS/PB phái sinh) = số phiên giữa ngày bước và ex-date: 18→1.293/năm (2025: 1.293 trong 58 sự kiện; 2026: 919 trong 57).
Trong đó thuộc top-100 mcap cùng ngày: 2015 416 · 2018 153 · 2021 145 · 2024 123 · **2025 355** · **2026 184** (≈1-1,5% số stock-ngày top-100/năm). Top-30: 2025 68, 2026 51.
Ca lớn còn trong top-30 từ 2023 (|lệch| ≥20 ngày): SHB 2026-02-02 (×1,10, ex 04-03, 38 phiên), SSI 2025-07-18 (×1,05, 30), FOX 2025-04-25 (×1,5, 28), TCB 2024-05-21 (×2,0, 22), GAS 2023-08-29 (×1,2, 16).
2026 trong top-100, lệch ≥10 ngày: NVL (×1,33, 40 phiên, hạng tốt nhất 43), BVB (×1,5), NVB (×1,52, 19 phiên). **Hôm nay (2026-11-23) không có cửa sổ lệch đang mở** trong top-100.
Phần theo consumer:
| Consumer | Đọc | Mức ảnh hưởng | Chạm tiền? |
|---|---|---|---|
| custom30V weight / `compute_park_trim.py` | `ticker_financial.OShares` (đã ex-date) | Taylor A/B: +0,04pp, nhiễu | Có, nhưng KHÔNG dính cột này |
| `value_radar.py` (`Price*OShares` trọng số top-100, cap 10%) | `ticker.OShares` | quant-skeptic: 10Y chỉ 2 tháng đổi >1%; trước 2014 tới 11%; hôm nay p không đổi | Không (display-only) |
| `rating_8l.py` `ps` | `ticker.OShares` + `_reconcile_oshares` | đã đối soát corp-action, fail-safe | Gián tiếp (gate LAG) — không đo thêm |
| `universe_scan.py`, `score_live_signals.py` `cf_yield = CF_OA_5Y/OShares/Close` | `ticker.OShares` | cf_yield sai tỉ lệ nghịch đúng `ratio` trong cửa sổ (TCB ×2 ⇒ cf_yield ÷2) | Signal chấm điểm live, không trực tiếp sizing — **chưa đo tác động xếp hạng** |
| `dna_card.py` dilution | `OShares` quý | bước lệch ngày → "pha loãng" lệch kỳ | Không |
| `universe_pit` | không đọc OShares (thanh khoản) | — | — |
Chưa đo: tác động lên điểm `score_live_signals` của các mã trong cửa sổ lệch (cần chạy lại bảng điểm theo OShares PIT).

## 4. Đề xuất vá (CHỈ ĐỀ XUẤT — chưa làm)
1. **Detector forward-only (rẻ nhất, Winston)**: kiểm hằng ngày mọi bước `ticker.OShares` ≥5% không nằm ±3 phiên một ISS/AIS đã thực hiện ⇒ ghi cờ vào bus/`ops_health_check`. Chi phí ~1 truy vấn/ngày (<1 GB), rủi ro 0 (đọc). Không sửa số, nhưng cho thấy ca TCB-type khi nó xảy ra.
2. **PIT-hoá ở lớp consumer** bằng `oshares_pit`/`oshares_reconciled` (đã wired, `rating_8l`, `custom30_core_select_audit`): consumer cần mcap/PE đúng ngày thì lấy số từ đó, không từ `ticker.OShares`. Chi phí: sửa từng consumer (value_radar, cf_yield); rủi ro: `oshares_at` từ chối ~33% mã tại 2014-07 (availability bias) — cần fallback; mọi thay đổi đổi số pin ⇒ re-pin (quy tắc §8c).
3. **Lớp hiệu chỉnh trong BQ** (view `ticker_oshares_pit` = `ticker` + OShares theo ex-date từ `corporate_action`): chi phí cao nhất (ghi BQ, quyền bq_admin, phụ thuộc `corporate_action` UPSERT + 2 bẫy exright/AIS) ⇒ **không khuyến nghị** khi ảnh hưởng đo được chỉ ~1-1,5% stock-ngày top-100.
4. **Sửa tại gốc**: hỏi bq_admin/chủ ETL: (a) nguồn của bước TCB 2024-05-21; (b) quy tắc ngày bước của `ticker.OShares` (BCTC quý vs ngày đăng ký vs ex-date). Đây là việc duy nhất sửa được cho mọi consumer cùng lúc.
**Khuyến nghị**: làm (1) + (4) trước; (2) chỉ cho `score_live_signals.cf_yield` nếu Taylor thấy cần sau khi đo tác động xếp hạng; không đụng custom30V.

## 5. Hạn chế
- Chỉ khớp được sự kiện ISS (tỉ lệ khớp ±2%); không khớp AIS/DIV/quyền mua ⇒ 36% bước ≥5% chưa phân loại (nhiều bước là phát hành riêng lẻ/ESOP không có ISS).
- "Lệch" đo trên ngày bước của `ticker.OShares` vs `exright_date` ISS; `corporate_action` UPSERT-in-place (registry Bẫy 2b), kết quả có thể đổi theo vintage.
- SQL đã chạy ngày 2026-11-24 00:5x ICT trên BQ live (không qua cache). Không có `confidence:` từ srcwalk — chỉ dùng grep/bq.
