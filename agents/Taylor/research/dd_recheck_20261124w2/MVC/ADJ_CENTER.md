# MVC — Tâm kỳ vọng điều chỉnh (E17, 24/11/2026, job Taylor_20261124_131351)

- **Phương pháp:** `dd_adjcenter_20261124/PREREG_adj.md` (md5 `ef5157cb…`) + `PREREG_adj_v2.md` (md5 `835dfc1e…`).
- **Kiểm kê khoá trước khi tính:** `INVENTORY_adj_MVC.md` (md5 `efee3d67…`). `calc_adj.py` assert cả 3 md5.
- **Tái lập:** chạy 2 lần, `adj_run1.txt` = `adj_run2.txt` (md5 `ae941803…`). Output: `adj.json`.
- **Mù giá.** Tâm gốc = 16.241 đ/cp (LEDGER_PROPOSAL rev10 = sổ rev9; recheck không đổi tâm). `skeptic_final` = REFUTED_OPEN (r1 REFUTED medium).

## Kết luận
**Tâm kỳ vọng điều chỉnh: 15.684 đ/cp (Σ p×m = −3,43%). Dải theo cực trị (p, m): 14.727–16.093.** Căn cứ: 1 hạng mục C+ (trích quỹ 11% LNST) + truyền dẫn adj NNC qua 44,07%.
- Cổ tức: cổ tức 2025 600 đ (60 tỷ) đã trừ trong tiền ròng (cổ tức phải trả V.19). Cổ tức 2026 do ĐHĐCĐ 2027 quyết ⇒ không có quyền tiền chưa chốt.
- Dải lệch hẳn về phía dưới tâm base: mọi hạng mục đo được đều chiều xuống; chiều lên (biên Tân Lập 38%, mỏ mới kịch bản tốt) không có số ⇒ bậc C.
- **Rủi ro lớn nhất KHÔNG nằm trong tâm:** cụm công nghiệp ≤500 tỷ (NPV 0 theo luật 03/11) và CK holding 20% [LUẬT].

## 1. Hạng mục vào tâm
| # | Hạng mục | Hướng | m (% tâm) [khoảng] | Bậc | p [thấp; cao] | p×m |
|---|---|---|---|---|---|---|
| 1 | Trích quỹ 11% LNST hằng năm (KTPL 7% + HĐQT/BKS 2% + BĐH 2%) | ↓ | −4,02 [−6,10; −4,02] | C+ | 0,50 [0,25; 0,75] | −2,01 |
| 2 | Truyền dẫn adj NNC qua stake (bỏ #4 chân MVC) | ↓ | −1,42 [−4,75; +0,09] | kế thừa | 1,0 | −1,42 |
| | **Σ** | | | | | **−3,43** |

Cơ sở #1 (áp skeptic r1 điểm 1 + điểm 3 chiều rẻ):
- Dấu chắc chắn: NQ ĐHĐCĐ 2026 thông qua 100% (NQ:767-785); năm 2025 đã trích 10% trên LNST riêng 122,52 tỷ (NQ:725-745).
- **Cận bảo thủ (vào tâm):** 11% × LNST riêng 2025 122,52 tỷ, phẳng, trả 9 lần 2027–2035 (trục GP Tân Lập ngắn nhất), chiết khấu 13,5% (annuity 5,04), × hệ số sở hữu chéo 1,04755 ⇒ **−4,02%**. Dùng LNST riêng (sau khấu hao, sau lãi vay, chỉ có cổ tức NNC chuyển về) đúng như skeptic chỉ ra; LNST riêng 9T/26 ex-hoàn nhập ~180,7 tỷ cao hơn mức 2025 ⇒ thật sự bảo thủ.
- **Cận cao:** 11% trên dòng tiền hoạt động + LNST 9T/26 = −6,10% (đúng dải "≈−5…−7%" skeptic ước). KHÔNG dùng −10,13% (cơ sở gồm lãi liên kết).
- Một kỳ báo cáo có số (2025) ⇒ thang B1.

Cơ sở #2: số đo bằng engine r3 (`calc/calc_items.py` → `nnc_flow`), đầu vào `dd_adjcenter_20261124/NNC/adj.json` (md5 `6beb796c…`) trừ hạng mục #4 của NNC (chân MVC trong NNC — engine MVC r3 tự giải sở hữu chéo). p đã nằm trong adj NNC ⇒ p = 1. Không trùng #1: quỹ của chính NNC nằm trong adj NNC; #1 chỉ trên LNST riêng MVC.

## 2. Chỉ độ nhạy (không vào Σ)
| Hạng mục | Bậc | Độ nhạy | Vì sao không vào tâm |
|---|---|---|---|
| Cụm công nghiệp ≤500 tỷ | C | mỗi 10% hao hụt NPV trên 500 tỷ ⇒ −2,96% | Luật 03/11: dự án mới base = sổ sách/NPV 0, cấm suy "đầu tư mới ⇒ giảm giá trị" khi thiếu cơ sở độc lập. r4 −8…−13% không có dữ kiện mới (skeptic điểm 2 — ghi nhận, giữ C). |
| Ký quỹ PHMT/đóng mỏ | C | NNC 4,50 tỷ ⇒ −0,27% (cận trên) | chưa đọc thuyết minh MVC |
| Biên Tân Lập 38% / mỏ mới tốt / upside 2034 | C ↑ | không định lượng | không có dữ kiện mới |
| [LUẬT] CK holding 20% | luật | −7,26% trước CK (6%: −388 đ; 15%: −967 đ) | base 0% = đầu dải user chốt 24/11 |
| [LUẬT] r vs dải Ke (E15) | luật | Ke 12,3% ⇒ 16.761 (+3,20%) | tham số luật, không vào Σ |

## 3. Bảng điều kiện đổi số
| Sự kiện | Khi | Hướng | Δ tâm |
|---|---|---|---|
| BCTC riêng 2026 + NQ ĐHĐCĐ 2027 phân phối LNST 2026 | 03–04/2027 | ↓ | #1 C+→A (p 0,9): −1,61% (cận bảo thủ) … −3,48% (cận cao); tỷ lệ về 10% ⇒ |m|×10/11 |
| Kế hoạch vốn/tiến độ/giá thuê cụm công nghiệp ≤500 tỷ | ĐHĐCĐ 2027 / CBTT | ↕ | mỗi 10% hao hụt −2,96%; có cơ sở độc lập ⇒ C→B, rev mới |
| Thuyết minh ký quỹ PHMT | BCTC năm 2026 | ↓ | ≤ −0,27% |
| adj NNC cập nhật | khi có | ↕ | đọc lại #2 (dải −4,75…+0,09%) |
| Hạn GP Tân Lập (2035/2040/2045) | khi tra | ↕ | đổi trọng số trục ⇒ rev mới |
| GP 2 mỏ mới cấp/từ chối | khi có | ↕ | nhánh lưới ⇒ rev mới |
| Lãi huy động 12T ±50bp (V1) | liên tục | ↕ | +50bp −1,24%; −50bp +1,29% |
| Pháp lý (Điều 195 LDN; quét sau 05/11) | khi có | — | chỉ WARNING |

Caveat: cộng tuyến tính (|Σ| ≤ 5%, PREREG v2 §5 không yêu cầu chạy tổ hợp).
