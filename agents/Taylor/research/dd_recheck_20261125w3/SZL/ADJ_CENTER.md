# SZL — Tâm kỳ vọng điều chỉnh (E17 / V9) · 25/11/2026 · job Taylor_20261125_053004 (resume Taylor_20261125_032446) — v2 sau skeptic r1

**Tâm kỳ vọng điều chỉnh: 27.782 đ/cp (dải 25.975–29.277; +6,10% so với tâm base 26.183, cỡ 5 tỷ sau CK 4,12%); căn cứ 5 hạng mục bậc A/B/C+ (1 A, 3 B, 1 C+)**

- Lý do áp V9: sổ đang `REFUTED_OPEN` (skeptic r4 vòng cuối INCONCLUSIVE, hạng mục CHƯA áp), chưa có tâm điều chỉnh.
- Phương pháp khoá trước: `PREREG_adj.md` (md5 `ef5157cb3f762d58623ed550ebc214c7`) + `PREREG_adj_v2.md` (md5 `835dfc1e07f9c67ac7f6c3028b529d13`); kiểm kê mã này `ADJ_PREREG_SZL.md` (md5 `c43c1873…`, commit `ba6ebbec8` trước lần chạy đầu) + phụ lục đính chính `ADJ_PREREG_SZL_v2.md` (md5 `fdddf36d…`, commit `a2fac9b65` trước lần chạy v2; mỗi điểm truy về `skeptic/r1_raw.md`). Assert md5 cả hai trong code.
- **Lịch sử:** v1 (`calc/calc_adj.py`, out `calc_adj_v1_out.json`) = 28.506 (+8,87%) → skeptic DD_GENERAL `skeptic/r1.json` **INCONCLUSIVE medium** (1,30 USD): E17 cộng tài sản chọn lọc mà không nêu luật vốn lưu động; người mua trả trước 14,54 trên mặt BCĐKT bị ghi "chưa đọc"; tồn kho Tam An không có kiểm NRV. v2 áp đính chính: nêu luật "chỉ khoản t=0 phi vận hành" (vốn lưu động vận hành ngoài cả hai phía; skeptic tự tính ròng ≈ −0,4%), S1 hạ A → B, thêm S5. Δ v1 → v2 = −2,54% (< 5%), nhãn không đổi ⇒ xác nhận cơ học, không chạy B2.
- Tính v2: `calc/calc_adj_v2.py` — mọi hạng mục chạy QUA mô hình rev5 (khoản t=0 qua `add_extra`; S4 dịch trục `NCS` giữ trọng số 0,25/0,5/0,25). CONTROL: stdout `model_rev5.py` md5 = `model_rev5_out.txt` (`f9f1a8a2…`); tâm base 26.183 assert. Hai lần chạy trùng byte (`calc/adj_v2_run1.txt` = `adj_v2_run2.txt`, md5 `34e93b08…`). |Σ| = 6,10% > 5% ⇒ tổ hợp chạy qua mô hình (+6,104% vs cộng tuyến tính +6,105%).
- MÙ GIÁ: không đọc giá thị trường khi dựng. Kiểm chéo: S4 m = −4,52% khớp ước lượng độc lập skeptic r4 (−4,5%); S5 m = −1,1% khớp skeptic r1.

## Hạng mục vào tâm
| # | Hạng mục | Hướng | Bậc | Đầu vào (tỷ) [dải] | m % tâm | p [dải] | p×m | Nguồn |
|---|---|---|---|---|---|---|---|---|
| S1 | Tồn kho BĐS khu dân cư Tam An: dở dang 76,21 (san lấp, xây dựng KDC Tam An) + thành phẩm BĐS 40,37; không đổi so đầu năm; luật "dự án mới = sổ sách"; chưa có kiểm NRV/chi phí hoàn thành/thuế khi bán | lên | B (số BCTC, giá trị thu hồi chưa có bằng chứng bán) | +116,58 tại t=0 | +8,86% | 0,50 [0,25; 0,75] | **+4,43%** | TM7 tr.18 (`q3_p22`); skeptic r4 MI-1, r1 FU#3 |
| S2 | Trả trước nhà thầu tăng 58,39 trong 9T (Phúc Hiếu 34,34; SEEN 16,80; Tu Sa 10,24), cùng kỳ XDCB nhà xưởng 3,83→39,25 và Long Phước 295,86→344,66 ⇒ ứng trước capex, tài sản theo giá vốn | lên | B (bản chất suy từ tên nhà thầu) | +58,39 [58,39; 72,61] tại t=0 | +4,44% | 0,50 [0,25; 0,75] | **+2,22%** | TM4 tr.15 (`q3_p19`), TM8 tr.18 (`q3_p22`) |
| S3 | Cổ tức dự thu từ bên liên quan (ghi nhận tại 30/09 ⇒ GDKHQ trước 06/11; DT tài chính đã loại khỏi N0) | lên | A | +23,264 tại t=0 | +1,77% | 0,90 [0,75; 1,00] | **+1,59%** | TM5 c tr.16 (`q3_p20`) |
| S4 | Trục nc trung bình 10% < sàn phân bổ đều DTCTH: 762,16 ÷ 27 năm × 0,8 = 22,58 tỷ/năm ≈ 17% N0 | xuống | C+ (cận bảo thủ phân bổ đều tới 2053) | nc +7pp [+7pp; +13pp ước lượng, thời hạn BQ 20 năm] | −4,52% | 0,35 [0,15; 0,55] (quan sát ngược có số: DTCTH +81,23 trong 9T/26; CF_OA/LNST ≈1,8× 2025 và 9T/26) | **−1,58%** | TM19 tr.24 (`q3_p28`); skeptic r4 MI-2 |
| S5 | Người mua trả trước NH 2,95 + DH 11,58 = 14,54 (mặt BCĐKT tr.3); nếu gắn Tam An thì giảm S1 | xuống | B (liên kết Tam An chưa kiểm) | −14,54 [−2,95; −14,54] tại t=0 | −1,10% | 0,50 [0,25; 0,75] | **−0,55%** | BCĐKT tr.3; skeptic r1 FU#1 |
| | **Σ (qua mô hình)** | | | | | | **+6,10%** | |

**Luật vốn lưu động t=0 (v2):** E17 chỉ đưa khoản t=0 PHI VẬN HÀNH (tồn kho dự án đứng yên, ứng trước capex, cổ tức dự thu, nợ gắn với chúng). Vốn lưu động vận hành (phải thu/phải trả người bán, thuế, lương, VAT, chi phí trả trước, thuế hoãn lại) nằm ngoài cả hai phía — skeptic r1: nợ ≈ 63,7 vs tài sản ≈ 58,4 ⇒ ròng ≈ −0,4% (C8).
Dải 25.975–29.277 = tổ hợp chạy qua mô hình, mỗi hạng mục ở cực trị (p, m). Đóng góp cực trị: S1 [+2,21%; +6,64%], S2 [+1,11%; +4,14%], S3 [+1,33%; +1,77%], S4 [−4,62%; −0,68%], S5 [−0,83%; −0,06%].

## Chỉ độ nhạy (bậc C — KHÔNG vào tâm)
- C1 Tiền thuê thu trước MỚI định kỳ (CF_OA ≈ 1,8× LNST) chưa được ghi có (lên) — phụ thuộc quỹ đất còn lại.
- C2 Capex duy trì vs KH (hai chiều) — trục rev5 ±6.482 (≈ ±24,8%).
- C3 Ý kiến kiểm toán FY2025 (xuống) — không có văn bản; soát xét H1/2026 chấp nhận toàn phần.
- C4 Long Phước vượt tổng mức 920 (xuống) — độ nhạy rev5 −2.041.
- C5 Liên kết Bình Thuận 80 + An Bình 24,5 theo giá gốc, chưa kiểm suy giảm (xuống).
- C6 Số dư/bảo lãnh với SNZ (xuống) — chưa đọc.
- C8 Vốn lưu động vận hành ròng ≈ −5,3 tỷ (≈ −0,4%, số skeptic r1) — ngoài luật t=0.
- Pháp lý: truy thu/phạt thuế ~14 tỷ; vụ SNZ — WARNING, không vào tâm.

## Tham số luật (KHÔNG vào Σ)
- L1 r 13,5% > dải Ke: Tâm @ Ke 12,3% = 27.233 (+4,01%) — dòng E15 ở REPORT_recheck §0.
- L2 RONIC = Ke; holdco 0% base (CK holding v5 hiển thị 0…+20%).
- Cổ tức SZL: tiền 25% đã ghi phải trả 70,36 tại 30/09 (đã trừ trong net debt); thưởng 70% đã vào mẫu số ⇒ một dòng tâm.

## Bảng điều kiện đổi số (Δ so với tâm điều chỉnh 27.782)
| Sự kiện / dữ kiện | Ngày dự kiến | Hướng | Δ tâm điều chỉnh |
|---|---|---|---|
| Có bằng chứng bán/NRV ≥ giá gốc cho Tam An (S1 lên A, p 0,90) | BCTC năm 2026 (~03/2027) | lên | +3,34% (≈ +928 đ) |
| Tồn kho Tam An suy giảm 50% (dự phòng / bán dưới giá vốn) | khi có | xuống | −2,09% (≈ −580 đ) |
| Thuyết minh xác nhận trả trước là ứng capex (S2 lên A, p 0,90) | BCTC năm | lên | +1,67% (≈ +465 đ) |
| Trả trước là vốn lưu động vận hành (S2 = 0) | BCTC năm | xuống | −2,09% (≈ −581 đ) |
| TM19 kỳ sau: phân bổ DTCTH thực ≈ 17% N0 (S4 lên A, p 0,90) | BCTC Q4/2026 31/01/2027 | xuống | −2,34% (≈ −651 đ) |
| — phân bổ thực ≈ 23% N0 (thời hạn BQ ~20 năm), p 0,90 | như trên | xuống | −5,63% (≈ −1.563 đ) |
| Thu trước mới ≥ phân bổ bền vững (S4 đóng, nc giữ 10%) | BCTC năm + LCTT | lên | +1,49% (≈ +414 đ) |
| Người mua trả trước không thuộc Tam An (S5 = 0) / thuộc Tam An (p 0,90) | thuyết minh năm | lên / xuống | +0,52% (≈ +145 đ) / −0,42% (≈ −116 đ) |
| Thuế truy thu ~14 tỷ xác nhận chưa hạch toán | khi có | xuống | −1,00% (≈ −278 đ) |
| LCTT năm tách capex duy trì (C2 lên B/A) | 31/03/2027 | hai chiều | chạy lại trục capex (rev mới); ±45 tỷ/năm ⇒ ±24,8% |
| Ý kiến kiểm toán FY2025 ngoại trừ (C3) | khi đọc được | xuống | mốc đổi nhận định (ngoài lưới) |

Nhãn `skeptic_final` = REFUTED_OPEN là trạng thái phản biện, KHÔNG phải quan điểm đầu tư. Tâm điều chỉnh KHÔNG thay tâm base trong sổ/luật 0,85×tâm/luật 4; watch chỉ dùng để SIẾT đáy.
