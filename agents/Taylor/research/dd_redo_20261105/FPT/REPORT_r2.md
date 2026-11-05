# DD REDO VÒNG 2 — FPT · 05/11/2026 · job `Taylor_20261105_020013`

> NGHIÊN CỨU, trung dung. Không phải khuyến nghị. Áp `STANDARD_r2.md`. Phần mô hình (BCTC gốc Q3/2026 HN, DCF FCFE lõi + SOTP) **chép nguyên** vòng 1 (`calc/fpt_redo.py` dòng 2–56); vòng 2 đổi tầng lưới/kết cục/base FRT/thanh khoản/báo cáo.
> **Tái lập:** `$DNA_PYEXE -I calc/fpt_r2.py > calc/fpt_r2_out.txt` — 2 lần trùng byte (`calc/LOCK_r2_outputs_md5.txt`). Số dưới đây từ `calc/fpt_r2_out.txt` / `SUMMARY.json` (vòng 1: `SUMMARY_r1.json`, `REPORT.md`).
> Giả thuyết, chất lượng LN, cổ đông: giữ `REPORT.md` §2–§4. Giá 04/11 còn quyền cổ tức 1.000 đ (chốt 30/11).

## 1. Kết luận

| Chỉ số (sau CK @5 tỷ) | Vòng 2 | Vòng 1 |
|---|---|---|
| Giá 04/11/2026 | **53.900** | 53.900 |
| r | 13,50% (một r mọi kịch bản) | 13,50% |
| **Tâm** (kỳ vọng lưới kết cục) | **54.203** | 52.183 |
| P10 / P50 / P90 (mức kết cục, `wpct`) | **32.389 / 55.182 / 74.557** | 30.520 / 53.699 / 72.235 |
| n kết cục · % trọng số dưới giá · min | **540 · 47,5% · 25.463** | 45 · — · — |
| Giá vs tâm | **−0,6%** | +3,3% |
| **Nhãn** | **TRONG vùng** (giữa vùng; ≈ tâm) | TRONG vùng |

Định nghĩa vùng không đổi (P10–P90) ⇒ nhãn không đổi do định nghĩa (điều 7). Phân phối gần như chia đôi quanh giá (47,5% trọng số dưới giá): giá đang phản ánh đúng kỳ vọng của khung này.

## 2. Ba con số (điều 4)
- **Tâm 54.203** · **P50 55.182** · **giá trị tại tham số trung tâm** (CƠ SỞ, Δconv 0, Δg 0, FRT thị giá, liên kết khác theo sổ) **58.579**.
- Tham số trung tâm cao hơn tâm 4,4k vì nhánh XẤU (w 0,35; conv 0,40, g1 3%) kéo kỳ vọng xuống. **P10 do riêng nhánh XẤU quyết định** (100% trọng số kết cục quanh P10 ±5% thuộc XẤU) — P10 ≈ "XẤU thành hiện thực", không phải đuôi trơn. **P90 do TỐT 68,6% / CƠ SỞ 31,4%.**

## 3. Lưới kết cục (điều 1, 2)
Ô tất định ⇒ kết cục = ô. n = 3 × 5 × 3 × 3 × 4 = **540**. File `calc/grid_fpt_r2.csv`.

| Trục | Điểm (trọng số) | Chiều |
|---|---|---|
| Kịch bản | XẤU 0,35 / CƠ SỞ 0,45 / TỐT 0,20 (g1 3/9/14%, conv 0,40/0,75/0,85, g_T 3/4/4%, CK FTEL 30/15/0%) | hai chiều |
| Δconv (FCFE/LN) | −0,20 / −0,10 / 0 / +0,10 / +0,20 (sàn 0,10) | hai chiều |
| Δg dài hạn | −1 / 0 / +1 pp | hai chiều |
| **FRT quanh thị giá (MỚI)** | +20% 0,25 / 0 0,50 / −20% 0,25 [UL] | đối xứng |
| **Liên kết khác + TPB/FTS lệch sổ (MỚI)** | −1.300 0,20 / 0 0,30 / +1.100 0,30 / +2.600 0,20 đ/cp [UL; SKEPTIC_20261101 T6a lãi LK ~600 tỷ/năm × PE 8; T6b SOTP TPB/FTS −1,3k…+2,4k] | hai chiều, lệch lên |

Vòng 1 bỏ ngoài lưới trục "liên kết khác" chỉ vì nó lệch lên — vi phạm điều 2; vòng 2 đưa vào (tâm +588 đ/cp so bản không trục).

| Bản song song | n | Tâm | P10 | P50 | P90 | % dưới giá |
|---|---|---|---|---|---|---|
| **Chính** | 540 | 54.203 | 32.389 | 55.182 | 74.557 | 47,5% |
| Không trục FRT | 180 | 54.203 | 32.300 | 55.081 | 74.546 | 47,3% |
| Không trục liên kết khác | 135 | 53.615 | 31.622 | 54.968 | 73.503 | 49,2% |
| Thêm trục r ±1pp (0,25/0,5/0,25 [UL]) | 1.620 | 54.384 | 32.289 | 55.163 | 75.477 | 47,5% |
| Lưới vòng 1 (FRT −20%, không trục LK) tính lại bằng `wpct` | 45 | 52.346 | 30.520 | 53.699 | 72.235 | 50,0% |

Trục loại: **r** (luật 03/11; bản song song ở trên, nhãn không đổi); **tiền khách ứng trước 2.370 tỷ** (học phí + người mua trả trước) — float theo mùa, không trừ; nếu trừ toàn bộ: −1.257 đ/cp (đối chiếu, vẫn TRONG vùng).

## 4. Base so với sổ sách / thị giá (điều 3)
| Khoản | Ảnh hưởng base | Cơ sở dữ liệu · nguồn |
|---|---|---|
| FTEL (FOX 45,66%) | CK 30/15/0% theo kịch bản (CƠ SỞ −15% = **−1.495 đ/cp**, `SUMMARY.json` base_adjustments) | free float FOX ≤ ~4,2%; Nhà nước (Bộ Công an) ~50,16% kiểm soát; CV 1906 18/03/2026 thôi hợp nhất — `dd_FPT_20261101/REPORT.md` §6, Q3HN p14. Là kịch bản có xác suất, có dữ liệu quan sát. |
| **FRT 46,54%** | **0** (thị giá 04/11 = 11.984 tỷ ≈ 6.355 đ/cp) | Vòng 1 trừ 20% (−1.271 đ/cp) **không có dòng cơ sở dữ liệu** ⇒ vi phạm điều 3 ⇒ bỏ khỏi base, chuyển thành trục đối xứng ±20%. |
| XDCB dở dang khuôn viên GD 760 tỷ | 0 (giá sổ = NPV 0) | Q3HN p37 |
| Liên kết khác 1.500 tỷ | 0 (theo sổ, **ước lượng** — BCTC không tách) | lệch sổ nằm ở trục §3 |
| TPBank 494,4 / FPTS 451,1 tỷ | 0 (giá gốc) | Q3HN p32; thị giá chưa đo (số CP nắm giữ chưa có) — trong trục §3 |

## 5. Thanh khoản (điều 6)
| | ADV 250 phiên | ADV 60 phiên |
|---|---|---|
| ADV trung vị | 566,1 tỷ | 346,0 tỷ |
| CK @ **5 tỷ** (tham chiếu) | **0,187%** | 0,214% |
| CK @ sleeve 10 / 40 triệu | 0,0083% / 0,0167% | — |

5 tỷ = 0,88% ADV250 (trong vùng hiệu chỉnh ~0,1–20%, ước lượng). Sleeve 10–40 triệu = 0,002–0,007% ADV: **dưới vùng hiệu chỉnh**, CK thật ≈ nửa spread (chưa đo). Nhãn ở cỡ 5 tỷ.

## 6. Đối chiếu Gordon (điều 10) — kịch bản cơ sở, conv 0,75, trước CK
| Biến thể | g 4% | g 5% |
|---|---|---|
| A — LN lõi vận hành (KHÔNG lãi tiền gửi) + tiền ròng + cổ phần | 52.205 | 55.954 |
| B — LN lõi + lãi tiền gửi ròng sau thuế vốn hoá, KHÔNG cộng tiền ròng | 49.029 | 53.203 |
B thấp hơn A vì vốn hoá lãi tiền gửi ở r 13,5% định giá tiền mặt dưới mệnh giá. Cả hai bao giá 53.900.

## 7. Tham số tự đặt [UL]
Trọng số kịch bản 0,35/0,45/0,20; g1, conv, g_T, CK FTEL từng kịch bản; Δconv ±0,20, Δg ±1pp trọng số đều; **trục FRT ±20% (0,25/0,5/0,25)**; **trục liên kết khác (điểm từ skeptic, trọng số 0,2/0,3/0,3/0,2)**; liên kết khác theo sổ 1.500 tỷ; lãi LK Q4/25 600 tỷ; LN lõi trừ lãi ròng × 0,85; free float 80%; trục r ±1pp (song song); Y = 1.

## 8. Mốc HAI chiều + HARD ABANDON (điều 8)
Giữ mốc DD 01/11 (`REPORT.md` §7):
- **Nâng** (⇒ w 0,25/0,45/0,30): CFO 2026 ≥ 6.000 tỷ (conv ≥ 0,6) và dở dang < 1.200; ký mới NN luỹ kế ≥ +20% và ≥ 2 HĐ > 10 triệu USD; Mỹ ≥ +10%, APAC hết âm; cổ tức FTEL ≥ 2.000 đ/cp; lãi huy động −100bp.
- **Hạ** (⇒ w 0,45/0,40/0,15): CFO 2026 < 3.400 (conv < 0,2) hoặc dở dang + phải thu tiếp tục tăng; ký mới < +15%; Nhật (JPY) < +15%; FTEL pha loãng / FOX mất tư cách đại chúng; lãi huy động +100bp.
- **HARD ABANDON**: kiểm toán ngoại trừ/từ chối; công bố khoản "chi phí phát triển khách hàng" 618,8 tỷ là chi phí không thu hồi lớn hơn mức hiện ghi; FTEL bị thu hồi/chuyển giao cổ phần ngoài giá thị trường; CFO 2026 âm cả năm.
- Ngưỡng nhãn: DƯỚI vùng < 32.389; TRÊN vùng > 74.557.
- **Không đủ điều kiện sleeve fear-buy §2.5** (không có trạng thái sợ hãi/scandal; giá ≈ tâm).

## 9. WARNING pháp lý / quản trị — đầy đủ (điều 5)
Nguồn rà: `dd_FPT_20261101/{SKEPTIC_20261101,GAPS,REPORT,REPORT_v1}.md`, vòng 1.
1. **FTEL**: đại diện vốn Nhà nước chuyển SCIC → Bộ Công an; FPT thôi hợp nhất từ 01/01/2026 (CV 1906, 18/03/2026); FOX free float ≤ ~4,2%, rủi ro tư cách đại chúng. Trong kịch bản (CK 30/15/0%). MỞ.
2. Khoản "chi phí phát triển khách hàng" 618,77 tỷ (trùng khoản vay 17,5 triệu GBP) chưa thuyết minh — câu hỏi IR. MỞ.
3. **Vay ngoại tệ 30/09 trùng từng đồng với 30/06** (JPY 6.003.607.117.212; EUR 432.483.911) — nghi chưa đánh giá lại tỷ giá kỳ Q3 [SKEPTIC; GAPS G15]. MỞ (MỚI mang theo vòng 2).
4. **Giao dịch bên liên quan 9T**: mua từ Synnex FPT 663 tỷ (cùng kỳ 308), bán FRT 386, bán/mua FTEL 115/211 [Q3HN p47–48] — < 2% DT, hạ cấp, nhưng mang theo. 
5. **Báo cáo quản trị 6T/2026 (89 trang scan) chưa đọc** (giao dịch bên liên quan ngoài tập đoàn, thù lao HĐQT) [GAPS G7]. MỞ.
6. Nghị quyết ĐHĐCĐ/HĐQT: thưởng CP 10:1 (21/09/2026, đã có trong SH), ESOP 10,82 triệu CP (26/06, đã phát hành), tạm ứng cổ tức 1.000 đ chốt 30/11 (giá còn quyền) — đều đã phản ánh trong số CP/giá; không có nghị quyết nâng ngưỡng/M&A mới được ghi nhận.
7. ETR 11,1% → 15,2%: chưa rõ do thuế tối thiểu toàn cầu hay hết ưu đãi [GAPS G11]. MỞ.
8. Phạt/truy thu thuế QĐ 1053/QĐ-DNL 24/06/2026: 243,98 triệu đ, đã nộp 01/07 — không trọng yếu. ĐÓNG.
9. Thanh tra Sở TT&TT Bình Dương về chi nhánh FTEL (IPTV/OTT 2022–24) — kết luận cũ, không trọng yếu. Hạ cấp.
10. **"Chưa thấy xử phạt/kết luận thanh tra mới"**: nguồn = WebSearch 01/11/2026 cho 10/2026 (`dd_FPT_20261101/REPORT.md` §6); **chưa quét 02–05/11, chưa tra trực tiếp ssc.gov.vn/gdt.gov.vn**.
11. Thiếu dữ liệu: lãi liên kết theo công ty, conv 2021–23 cùng định nghĩa, backlog/định nghĩa "ký mới", MW trung tâm dữ liệu, phải thu khu vực công theo tuổi nợ.

## 10. LOCK md5 (điều 9)
Dòng `LOCK` trong `calc/fpt_r2_out.txt`: `fpt_r2.py`, `fpt_redo.py`, `assoc_px_20261104.csv` (FOX/FRT), `_common_014125/{common.py,r2common.py,bq_px_liq_20261104.csv}`, `_shared/wpct.py`, `deposit_rate_vn.py`, `cctg_rate_vn.py`, `data/deposit_rate_vn_events.csv`, `data/cctg_rate_vn_events.csv`, `kb/dd_price_zones.json` (chỉ đọc).

## 11. Thay đổi so vòng 1 và lý do
| Mục | Vòng 1 | Vòng 2 | Lý do |
|---|---|---|---|
| FRT | thị giá × 0,8 | thị giá; ±20% là trục | điều 3 (haircut không có cơ sở) — +1.271 đ/cp |
| Liên kết khác/TPB/FTS | theo sổ, upside chỉ ghi chú | trục 4 điểm | điều 2 — +588 đ/cp |
| Phân vị | 45 ô, `common.wq` | 540 kết cục, `wpct` | điều 1 |
| Tâm | 52.183 | 54.203 (+2.020) | FRT +1.271, trục LK +588, lồi lưới ~+160 |
| Nhãn | TRONG vùng (+3,3% vs tâm) | TRONG vùng (−0,6%) | không đổi |

Chưa qua fundamental-skeptic vòng 2. Không sửa `dd_price_zones.json`, không PDF/email.
