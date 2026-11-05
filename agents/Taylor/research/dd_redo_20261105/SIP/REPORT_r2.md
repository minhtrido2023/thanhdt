# SIP — DD redo VÒNG 2 · giá 04/11/2026 · job `Taylor_20261105_020018`

> Chỉ nghiên cứu, trung dung, không phải khuyến nghị. Theo `STANDARD_r2.md` (12 điều). Số: `calc/model_sip_r2_out.txt|json` (`$DNA_PYEXE -I calc/model_sip_r2.py`); khoá `calc/LOCK_r2_md5.txt`; tất định: `_common_g2r2/selfcheck_r2.sh` (chạy 2 lần, có `env -u TZ`, trùng byte). Hàm giá trị, số BCTC = vòng 1 (`REPORT.md`, nguồn TM ở `calc/model_sip.py`). Vòng 1 giữ nguyên: `REPORT.md`, `SUMMARY_r1.json`.

## 0. Kết luận

| Ba con số (điều 4) | Sau CK thanh khoản 1,37% @5 tỷ |
|---|---|
| **Tâm** = kỳ vọng trọng số của lưới | **54.230** |
| **P50** kết cục | 53.086 |
| Giá trị tại tham số trung tâm | 55.421 |
| **P10 / P90 kết cục** | **43.784 / 68.713** (min 34.356, max 81.487; n = 2.916 kết cục) |

- Giá **49.000** (04/11): −9,6% so tâm; **33,0% trọng số kết cục nằm dưới giá** ⇒ **TRONG vùng**, nghiêng dưới tâm. Nhãn không đổi so vòng 1, và không phải do đổi định nghĩa vùng (cả hai vòng đều P10–P90).
- P10 do nhánh đất XẤU quyết định (95% trọng số quanh P10). P90 do riêng nhánh đất TỐT (trọng số 0,20).
- So vòng 1 (tâm 53.175; P10–P90 34.501–73.949): tâm +2,0%; vùng hẹp lại vì đổi cấu trúc lưới (§7).

## 1. Đổi so vòng 1 — rà theo 12 điều
| Điều | Vòng 1 | Vòng 2 |
|---|---|---|
| 1 phân vị | CDF bậc thang tự viết, n=27 | `_shared/wpct.py` mid-block trên 2.916 kết cục |
| 2 đối xứng | lỗ tín dụng, NCI cao, thu hồi 60%, thuế ×1,2 chỉ có ở nhánh xấu (một chiều, tương quan hoàn toàn) | 8 trục độc lập (§7). Trục một phía chỉ ở chỗ sổ sách là cận trên (lỗ tín dụng ≥0, thu hồi ≤100%), có ghi rõ |
| 3 base | không có khoản lệch sổ sách không nguồn | giữ; liệt kê `base_adjustments` |
| 5 WARNING | thiếu cách đọc thứ hai TM4b, payout 111%, lệch phân loại tạm ứng, nhân sự | bổ sung (§6) |
| 6 thanh khoản | chỉ ADV120 @1/5/10 tỷ | thêm ADV250/60 và cỡ sleeve 10–40 triệu (§5) |
| 9 LOCK | không có | `LOCK_r2_md5.txt`: script, lib, giá BQ, SQL, wpct, `ddg2`, `deposit_rate_vn` + `cctg_rate_vn` + 2 CSV sự kiện lãi suất |
| 10 Gordon | không có | hai biến thể (§7) |

## 2–4. Chất lượng LN, bảng cân đối, ghi nhận DT
Không đổi so vòng 1 (`REPORT.md` §2–§4). Không có BCTC mới sau Q3/2026.

## 5. Thanh khoản (điều 6)
| Cỡ | ADV trung vị | Q/ADV | Số phiên @10% ADV | CK |
|---|---|---|---|---|
| **5 tỷ (tham chiếu)** | 120 phiên 3,93 tỷ | 127% | 12,7 | **1,37%** |
| 5 tỷ | 250 phiên 10,37 tỷ | 48% | 4,8 | 0,92% |
| 5 tỷ | 60 phiên 3,16 tỷ | 158% | 15,8 | 1,50% |
| **Sleeve thật 10 / 20 / 40 triệu** | 120 phiên | 0,3–1,0% | <0,1 | **0,26% / 0,28% / 0,31%** |

- ⚠️ Cỡ tham chiếu 5 tỷ = 127% ADV120: **ngoài vùng hiệu chỉnh của luật căn bậc hai** (giả định 0,1–30% ADV/phiên, ước lượng) ⇒ 1,37% là ngoại suy. Cỡ sleeve (NAV SpaceX ≈ 0,94 tỷ) nằm trong vùng.
- ADV250 gấp 2,6 lần ADV120: thanh khoản đã sụt từ 2025 (GAPS G6).
- Nhãn tính ở cỡ 5 tỷ. Ở cỡ sleeve, tâm sau CK 54.811 (= tâm trước CK 54.981 × (1 − 0,31%)); nhãn không đổi.

## 6. Pháp lý / quản trị — ⚠️ WARNING (mang đủ cờ chưa đóng từ `dd_SIP_20261101/SKEPTIC_20261101.md` + `GAPS.md`)
1. **Tín dụng phi ngân hàng 6.016 tỷ = 116% VCSH mẹ** [TM4a/4b]. TM4b có hai cách đọc:
   - (a) không có TS bảo đảm, chỉ có thoả thuận quản lý dòng tiền;
   - (b) "bên thứ ba" là ngân hàng cho SIP vay tín chấp, tức một cấu trúc vay-cho-vay.

   Vòng 2 đưa rủi ro này vào lưới thành trục lỗ 0/10/30%.
2. **Tạm ứng 635,6 tỷ cho HĐQT/BGĐ/BKS/quản lý chủ chốt** [TM40; KT25 635,2]: tồn tại ≥2 năm, mục đích ghi "tìm hiểu và mua đất". BCĐ/TM7 xếp dài hạn, TM40 xếp ngắn hạn. Bản song song mất trọn với p0,15 [UL]: tâm 53.842, P10 43.334, P90 68.257.
3. Vay ngân hàng tín chấp 4.374 tỷ [TM23] chạy song song khoản cho vay CTCK.
4. Cổ tức 2025 = 111% LNST riêng, có hoàn nhập quỹ ĐTPT ~329 tỷ; kế hoạch 2026 chỉ tối thiểu 10%. Lợi suất 10,3% là quá khứ, khó lặp lại.
5. Nhân sự (dữ liệu, không phải vi phạm):
   - Chủ tịch chuyển 3,7 triệu cp cho người thân (06/2026);
   - miễn nhiệm 1 PTGĐ (21/05/2026) và 1 thành viên BKS (21/04/2026).
6. **Chưa thấy tin xử phạt/khởi tố** SIP. Tra WebSearch ngày 05/11/2026 ([doanhnhan.baophapluat.vn](https://doanhnhan.baophapluat.vn/dau-tu-sai-gon-vrg-sip-mien-nhiem-mot-pho-tong-giam-doc-lai-quy-i-giam-nhe.html), [dnse.com.vn](https://www.dnse.com.vn/senses/tin-tuc/chu-tich-dau-tu-sai-gon-vrg-sang-tay-37-trieu-co-phieu-sip-cho-con-35236541)); kết quả mới nhất tới 07/2026. WebSearch không phải CBTT sàn, nên "không thấy" ≠ không có. Chưa thấy NQ HĐQT/ĐHĐCĐ mới sau 01/11 để đưa vào mô hình.
7. Không có chiết khấu quản trị trong tâm. Nếu áp 10% như DD cũ thì tâm 48.807 (= 54.230 × 0,9), chỉ là độ nhạy.

## 7. Định giá
**Khung (giữ nguyên vòng 1):** SOTP gồm:
- mảng vận hành × PE nội tại (1 − g/RONIC)/(r − g), RONIC = ROE5Y 29,7%;
- cộng tài sản tài chính ròng (mẹ + con × (1 − NCI)) − quỹ KTPL;
- trừ lỗ tín dụng và PV thuế trên DT chưa thực hiện;
- cộng PV 937 ha và thu hồi chi phí đã chi.

r = **13,5%**, tại lãi huy động 12T hiệu dụng 7,40% (CCTG 12M 02/11; neo 03/11 = 7,40%; β = 1).

**Lưới — 8 trục độc lập** (xác suất [UL] trừ khi ghi nguồn; chi tiết `SUMMARY.json.axes_included`):
| Trục | Giá trị (xác suất) | Hai chiều? |
|---|---|---|
| Thị trường đất (tỷ/ha toàn phần, năm bán hết 937 ha) | tốt 18/15 (0,20) · cơ sở 12/22 (0,50) · xấu 6/30 (0,30) — nghiêng xuống vì 2025 chỉ đạt 28,6 ha so KH 45 [AR25] | có |
| Tỷ/ha trong kịch bản | ×0,75 / 1 / 1,25 (đều) | có |
| g mảng vận hành | 2 / 3 / 4% (0,25/0,5/0,25) | có |
| Lỗ tín dụng không bảo đảm | 0% (0,60) · 10% (0,25) · 30% (0,15) | 0% = sổ sách (EY chấp nhận toàn phần, chưa dự phòng) là cận trên: không thể thu quá gốc |
| NCI hiệu dụng ở con | 8,5 / 20 / 31% (0,25/0,5/0,25) | có |
| Thu hồi chi phí đã chi cho quỹ đất | 100% (0,75) · 60% (0,25) | 100% = giá vốn (luật NPV=0) là cận; phần đất tăng giá đã nằm trong trục tỷ/ha |
| PV thuế tương lai trên DT chưa thực hiện | ×0,8 / 1 / 1,2 | có |
| Tỷ lệ trích quỹ KTPL | 7,25% (thực 2025) / 9,04% (ước 9T26) | có |

**Trục loại khỏi lưới (điều 2):**
- Tạm ứng bên liên quan: là WARNING; đã báo bản song song (§6.2).
- "Thuế đã nộp khi thu tiền": BCĐ bác bỏ (không có TS thuế hoãn lại; thuế hiện hành 19,9% LNTT). Chiều xuống tương ứng đã nằm ở trục thuế ×1,2.
- Tiền thuê đất trả Nhà nước (G16): chưa có số, không định lượng được ở chiều nào.
- Chiết khấu quản trị: là WARNING.

**`base_adjustments`** (đ/cp, theo sổ):

| Khoản | Đ/cp | Nguồn |
|---|---|---|
| Nghĩa vụ hạ tầng | −13.476 | TM20 |
| Quỹ KTPL | −2.638 | mã 323 |
| PV thuế tương lai ×1 | −1.915 | TM21; luật thuế 20% |
| NCI 20% trên tài sản ròng ở con | −3.527 | trung điểm 8,5% và 31% |

Không còn khoản lệch sổ sách nào thiếu nguồn.

**Bản song song (điều 2):**
| Biến thể | Tâm | P10 | P90 |
|---|---|---|---|
| Chính (8 trục) | 54.230 | 43.784 | 68.713 |
| + tạm ứng 635,6 mất trọn p0,15 | 53.842 | 43.334 | 68.257 |
| Trọng số đất đối xứng 25/50/25 | 55.416 | 44.319 | 70.560 |
| Lưới vòng 1 (tương quan hoàn toàn) + wpct | 53.265 | 35.041 | 73.949 |

Giả định các trục **độc lập** làm hẹp hai đuôi. Thực tế tín dụng và thị trường đất có thể cùng xấu theo chu kỳ BĐS. Bản lưới vòng 1 chính là giới hạn tương quan hoàn toàn; ở cả hai bản, giá đều TRONG vùng.

**Gordon/ROE (điều 10, g 3%, trước CK):**
- Có lãi tiền gửi (ROE TTM 24,2%): **43.263**.
- Không lãi tiền gửi (ROE vận hành 41,3% + tài sản tài chính ròng theo sổ): **39.050**.

Cả hai thấp hơn SOTP vì Gordon trên LN TTM không đếm 937 ha chưa cho thuê và tiền thuê đã thu trước. Đây là cận dưới tham chiếu, không phải số thay thế.

**Độ nhạy r (tâm sau CK):**
| Lãi huy động | −100bp | −50bp | 0 | +50bp | +100bp |
|---|---|---|---|---|---|
| β=1 | 57.753 (+6,5%) | 55.914 (+3,1%) | 54.230 | 52.681 (−2,9%) | 51.251 (−5,5%) |
| β=0,5 | 55.914 | 55.054 | 54.230 | 53.440 | 52.681 |

## 8. Mốc đổi nhận định (hai chiều) + HARD ABANDON
| Mốc | LÊN nếu | XUỐNG nếu |
|---|---|---|
| BCTC Q4/2026 (~30/01/2027) | DT chưa thực hiện tăng >500 tỷ trong quý; LNST mẹ Q4 ≥ 321 | LNST mẹ Q4 < 300 trong khi lãi vay tăng; tạm ứng/đền bù tăng mà không có HĐ thuê đi kèm |
| BCTC 2026 kiểm toán (~31/03/2027) | EY sạch về TM4; cho vay CTCK < 3.000 hoặc công bố bên vay + TSĐB | có dự phòng / ngoại trừ / nhấn mạnh về cho vay-TP; TP T&T bị gia hạn |
| Diện tích cho thuê 2026 (AR26) | ≥ 60 ha | ≤ 30 ha lần thứ hai |
| Lãi huy động 12T | −50bp ⇒ +3,1% | +50bp ⇒ −2,9% |

- Ngưỡng nhãn: **DƯỚI vùng** khi giá < 43.784; **TRÊN vùng** khi giá > 68.713.
- **HARD ABANDON** (bỏ hồ sơ, dựng lại từ đầu) nếu có một trong các sự kiện:
  - kiểm toán ngoại trừ / từ chối ý kiến về khoản cho vay CTCK hoặc TP;
  - khởi tố pháp nhân hoặc lãnh đạo liên quan khoản tạm ứng 635,6 tỷ;
  - dự phòng tín dụng > 30% phần không bảo đảm.
- **Không đủ điều kiện sleeve fear-buy §2.5** (DD trung dung, không phải trạng thái sợ hãi) ⇒ không áp tranche.
