# DD REDO VÒNG 2 — HPG · 05/11/2026 · job `Taylor_20261105_020013`

> NGHIÊN CỨU, trung dung. Không phải khuyến nghị. Áp `STANDARD_r2.md`. Mô hình RI (BCTC gốc HN-Q3, đường LN kịch bản v3 31/10) **chép nguyên** vòng 1 (`calc/hpg_redo.py` dòng 2–49).
> **Tái lập:** `$DNA_PYEXE -I calc/hpg_r2.py > calc/hpg_r2_out.txt` — 2 lần trùng byte (`calc/LOCK_r2_outputs_md5.txt`). Số từ `calc/hpg_r2_out.txt` / `SUMMARY.json` (vòng 1: `SUMMARY_r1.json`, `REPORT.md`).
> Giả thuyết, chất lượng LN, dòng tiền: giữ `REPORT.md` §2–§4.

## 1. Kết luận

| Chỉ số (sau CK @5 tỷ) | Vòng 2 | Vòng 1 |
|---|---|---|
| Giá 04/11/2026 | **21.700** (P/B 1,23x BVPS 17.624) | 21.700 |
| r | 13,50% | 13,50% |
| **Tâm** (kỳ vọng lưới kết cục) | **16.286** | 16.337 |
| P10 / P50 / P90 (mức kết cục, `wpct`) | **8.942 / 16.343 / 23.520** | 9.261 / 16.706 / 23.577 |
| n kết cục · % trọng số dưới giá · min | **675 · 83,6% · 5.846** | 45 · — · — |
| Giá vs tâm | **+33,2%** | +32,8% |
| **Nhãn** | **TRONG vùng — sát mép trên** (giá thấp hơn P90 7,7%) | TRONG vùng (phần trên) |

Định nghĩa vùng không đổi ⇒ nhãn không đổi do định nghĩa (điều 7). Nói thẳng: **83,6% trọng số kết cục nằm dưới giá**; nhãn "TRONG vùng" chỉ vì vùng P10–P90 rộng. Giá ngụ ý r ≈ **11,32%** (tâm lưới sau CK = giá).

## 2. Ba con số (điều 4)
- **Tâm 16.286** · **P50 16.343** · **giá trị tại tham số trung tâm** (TRUNG LẬP, hệ số LN 1,0, Δg 0, dốc 0, TLSH NPV 0) **16.706**.
- **P10 do riêng nhánh XẤU** (100% trọng số kết cục quanh P10 ±5%); **P90 do TỐT 62,6% / TRUNG LẬP 37,4%**.

## 3. Lưới kết cục (điều 1, 2)
Ô tất định ⇒ kết cục = ô. n = 3 × 5 × 3 × 3 × 5 = **675**. File `calc/grid_hpg_r2.csv`.

| Trục | Điểm (trọng số) | Chiều |
|---|---|---|
| Kịch bản | XẤU 0,25 / TRUNG LẬP 0,50 / TỐT 0,25 (v3 31/10, skeptic CONFIRMED) | hai chiều |
| Hệ số đường LNST Q4/26–2029 | 0,8 / 0,9 / 1,0 / 1,1 / 1,2 | hai chiều |
| Δg terminal | −1 / 0 / +1 pp | hai chiều |
| **Dốc LN 2028–29 (MỚI)** | −5 / 0 / +5 %/năm (đều) [UL] — đáp SKEPTIC N2 "không kịch bản nào tăng dù DQ2 ~85% công suất" | hai chiều |
| **TLSH (MỚI)** — tỷ lệ mất giá trị khoản 9.915 tỷ (100% = 1.174 đ/cp) | −25% (lãi) 0,10 / 0 0,50 / 25% 0,20 / 50% 0,12 / 100% 0,08 [UL] | hai chiều, lệch xuống |

Vòng 1 để đuôi TLSH ngoài lưới (chỉ lệch xuống) — vi phạm điều 2; vòng 2 đưa vào (tâm −193 đ/cp so bản không trục).

| Bản song song | n | Tâm | P10 | P50 | P90 | % dưới giá |
|---|---|---|---|---|---|---|
| **Chính** | 675 | 16.286 | 8.942 | 16.343 | 23.520 | 83,6% |
| Không trục dốc | 225 | 16.205 | 9.000 | 16.560 | 23.149 | 86,1% |
| Không trục TLSH | 135 | 16.479 | 9.237 | 16.551 | 23.759 | 82,8% |
| Thêm trục r ±1pp (0,25/0,5/0,25 [UL]) | 2.025 | 16.400 | 8.960 | 16.265 | 24.219 | 82,9% |
| Lưới vòng 1 tính lại bằng `wpct` | 45 | 16.398 | 9.261 | 16.706 | 23.577 | 85,0% |

**Trục loại khỏi lưới chính, có lý do:**
- **r / β riêng mã**: luật 03/11 dùng r 13,5% đồng nhất. Đối chiếu (KHÔNG phải luật hiện hành; CAPM bản cũ rf 6,75% + β × ERP 5,55%): β 0,84 ⇒ r 11,41% ⇒ tâm **21.388**; β 0,93 ⇒ 11,91% ⇒ 19.848; β 1,0 ⇒ 12,30% ⇒ 18.816. **Đây là trục quyết định nhãn của HPG** — câu hỏi mở cho Mike/user (giữ từ vòng 1).
- 26,55% BĐS HP còn lại + liên danh BT sông Hồng: không có số để lượng hoá (nghĩa vụ góp vốn/bảo lãnh chưa thuyết minh) ⇒ WARNING §9.
- EV/EBITDA 5x: đối chiếu, không comp ⇒ không vào tâm (vòng 1 §6).

## 4. Base so với sổ sách (điều 3)
| Khoản | Base | Cơ sở · nguồn |
|---|---|---|
| TLSH 9.915 tỷ | 0 (sổ sách, NPV 0) | HN-Q3; lệch chỉ ở trục §3 |
| Dự án đang đầu tư (XDCB 16.113, cam kết ~19.472, DQ2) | 0 (BV0 theo giá sổ, capex tương lai không trừ = NPV 0) | HN-Q3 |
| Terminal: ROE_T < r ⇒ RI không tăng | quy ước NPV 0 vốn mới (luật 03/11) | — |
| **Thuế terminal 20%** (TAXF 0,80/0,88) — lệch khỏi ETR hiện hành ~12% | có trong base | **Cơ sở:** thuế suất TNDN phổ thông 20% khi hết ưu đãi; ETR thép 6T/26 6,5%; thời hạn ưu đãi chưa công bố [dd_HPG_20261031 GAPS §2/§7, GAPS2:148–158]. Là giả định thuế pháp định, không phải nhận định. |

## 5. Thanh khoản (điều 6)
| | ADV 250 phiên | ADV 60 phiên |
|---|---|---|
| ADV trung vị | 602,1 tỷ | 371,2 tỷ |
| CK @ **5 tỷ** | **0,150%** | 0,177% |
| CK @ sleeve 10 / 40 triệu | 0,0067% / 0,0134% | — |

5 tỷ = 0,83% ADV250 (trong vùng hiệu chỉnh, ước lượng). Sleeve **dưới vùng hiệu chỉnh** (nửa spread, chưa đo). GTGD giảm mạnh so 02/2026 (ADV60 thấp hơn ADV250 38%).

## 6. Đối chiếu Gordon (điều 10)
P/B = (ROE − g)/(r − g), BVPS 17.624: ROE 2027 TRUNG LẬP 17,5% ⇒ 24.995 (g 4%) / 25.862 (g 5%); ROE lõi 9T26 × 4/3 (LNST lõi 9T ≈ 19.200 tỷ, SKEPTIC/vòng 1 §2) ⇒ 24.496 / 25.305. Gordon cao hơn tâm RI 8,2–9,6k vì giữ ROE hiện tại vĩnh viễn với thuế hiện hành; RI dùng đường LN kịch bản (giảm dần), thuế terminal 20% và terminal NPV 0 khi ROE_T < r. Không có biến thể "bỏ lãi tiền gửi" có nghĩa (nợ ròng 59.608 tỷ, lãi tiền gửi không phải nguồn LN trọng yếu).

## 7. Tham số tự đặt [UL]
Trọng số kịch bản 0,25/0,50/0,25 và đường LN từng kịch bản; g_T 3/5/5%; payout 20%; hệ số LN ±20%, Δg ±1pp (đều); **dốc ±5%/năm (đều)**; **trục TLSH điểm và trọng số 0,10/0,50/0,20/0,12/0,08**; free float 64,5%; trục r ±1pp (song song); Y = 1.

## 8. Mốc HAI chiều + HARD ABANDON (điều 8)
Giữ H1–H10 khoá 31/10 (`REPORT.md` §7).
- **LÊN** (⇒ w 0,15/0,50/0,35): ≥ 2 trong {H1 biên gộp Q4 ≥ 18%, H2 LNST lõi Q4 ≥ 8.000, H5 biên Q1/27 ↑} và H4 (AD HRC) không xấu; H7 + H9 thuyết minh TLSH/liên danh rõ ⇒ trục TLSH dồn về 0; lãi huy động −100bp.
- **XUỐNG** (⇒ w 0,35/0,50/0,15): H1 và H5 cùng xấu (2 quý biên thấp hơn cùng kỳ) hoặc H4 xấu; H7/H9/H10 xấu ⇒ trục TLSH dồn về 50–100%; lãi huy động +100bp.
- **HARD ABANDON**: công bố bên mua 2 công ty BĐS (lãi 4.929 tỷ) là bên liên quan của nhóm kiểm soát với giá bất lợi; HPG phát sinh bảo lãnh/góp vốn cho hệ Đại Quang Minh–TLSH > 10.000 tỷ; ngoại trừ kiểm toán; truy thu ưu đãi thuế DQ2 > 5.000 tỷ.
- Ngưỡng nhãn: TRÊN vùng nếu giá > 23.520 (+8,4% từ giá 04/11); DƯỚI vùng nếu < 8.942.
- **Không đủ điều kiện sleeve fear-buy §2.5** (giá trên tâm; không trạng thái sợ hãi).

## 9. WARNING pháp lý / quản trị — đầy đủ (điều 5)
Nguồn rà: `dd_HPG_20261031/{SKEPTIC_20261031,GAPS,GAPS2,REPORT,REPORT_v1,REPORT_v2}.md`, vòng 1.
1. **TLSH (hệ Đại Quang Minh)**: hoán đổi 778,4 triệu CP BĐS HP lấy 799,5 triệu CP TLSH (7.995 tỷ); NQ 10/NQHP-2026 (22/07) định giá 32.000 đ/cp → NQ 13/NQHP-2026 (30/09) khớp ~10.271 đ/cp; lý do đổi + tổ chức thẩm định không công bố; rủi ro chuyển giá trị 0 – ~12.660 tỷ. TLSH là bên liên quan (VAS 26) nhưng không thuyết minh. **Nghị quyết HĐQT = dữ liệu đã đưa vào mô hình qua trục TLSH.** Thẩm quyền: dưới ngưỡng 35% tổng tài sản (Điều lệ 2026 Đ.46) ⇒ HĐQT đủ thẩm quyền (ĐÓNG). Rủi ro: MỞ, WARNING nặng.
2. Bên mua 2 công ty con BĐS (Mỹ Hào 99,9%, Đô thị xanh 70%; thu 9.800,8 tỷ; lãi 4.929 ≈ 21% LNTT 9T) không nêu tên. MỞ (H10, 15/04/2027).
3. Liên danh BT Đại lộ cảnh quan sông Hồng (cùng Đại Quang Minh, THACO; 1.600 tỷ chuyển đối tác) — nghĩa vụ tương lai chưa thuyết minh. MỞ.
4. Dòng tiền góp vốn chưa truy ~1.370–1.870 tỷ (GAPS2, giả thuyết đếm trùng chưa xác nhận). MỞ.
5. CP HPG của cá nhân dùng bảo đảm vay công ty (KT25 TM23): số lượng/cá nhân/covenant không công bố. MỞ.
6. Ưu đãi thuế DQ2: CV 377/TCT-CS (30/01/2024) đòi xác định dự án mới/mở rộng — kết quả không tìm được; thuyết minh thuế KT25 chưa đọc. MỞ (thuế terminal 20% đã vào base).
7. Phòng vệ thương mại: QĐ 1902 rà soát chưa có hạn kết luận; QĐ 1917/QĐ-BCT chống lẩn tránh 27,83% hiệu lực 28/07/2026; CBAM; vụ AD tôn mạ Mỹ/EU/Úc/Đài Loan chưa rà. MỞ.
8. Giao dịch nội bộ: Trần Vũ Minh mua 33,3 triệu + đăng ký 50 triệu CP (07/10–05/11/2026); Doãn Thị Bích Ngọc bán 350 nghìn; TV độc lập Đặng Ngọc Khánh đăng ký bán 100 nghìn (04/11–03/12). Thù lao HĐQT 2024 244,7 / 2025 83,2 / 6T26 207,7 tỷ. Hạ cấp, mang theo.
9. Cổ tức "15%" là của 2025 hay kế hoạch 2026 — chưa đối chiếu TM28. MỞ.
10. EBITDA lệch slide 361 tỷ; thu nhập khác Q3 485,6 chưa bóc khỏi lõi (tối đa −1%). MỞ.
11. Tiền gửi cầm cố 8.294 tỷ; ~90% vay ngắn hạn có bảo đảm (đã vào nợ ròng/EBITDA 1,54–1,62x). ĐÓNG.
12. Kiểm toán KPMG → Deloitte 2025 (lý do không công bố), ý kiến sạch. Hạ cấp.
13. **Xử phạt**: QĐ 244/QĐ-XPHC 11/05/2022 phạt 125 triệu (thiếu TV HĐQT độc lập) — lịch sử. **"Không tìm thấy khởi tố/xử phạt 2025–26"**: nguồn = DD 31/10/2026 (`dd_HPG_20261031/GAPS.md`:243, `REPORT.md`:230); **chưa tra ssc.gov.vn/gdt.gov.vn; chưa quét tin 31/10–05/11**.

## 10. LOCK md5 (điều 9)
Dòng `LOCK` trong `calc/hpg_r2_out.txt`: `hpg_r2.py`, `hpg_redo.py`, `_common_014125/{common.py,r2common.py,bq_px_liq_20261104.csv}`, `_shared/wpct.py`, `deposit_rate_vn.py`, `cctg_rate_vn.py`, `data/deposit_rate_vn_events.csv`, `data/cctg_rate_vn_events.csv`, `kb/dd_price_zones.json` (chỉ đọc).

## 11. Thay đổi so vòng 1 và lý do
| Mục | Vòng 1 | Vòng 2 | Lý do |
|---|---|---|---|
| TLSH | đuôi −587 đ/cp ngoài lưới | trục 5 điểm | điều 2 — tâm −193 |
| Dốc LN 2028–29 | không có | trục ±5%/năm | điều 2 (SKEPTIC N2) — tâm +81 |
| Phân vị | 45 ô, `common.wq` | 675 kết cục, `wpct` | điều 1 |
| Tâm | 16.337 (kỳ vọng kịch bản @ tham số trung tâm) | 16.286 | điều 4 + 2 trục mới |
| P10 / P90 | 9.261 / 23.577 | 8.942 / 23.520 | trục TLSH kéo đuôi dưới |
| Nhãn | TRONG vùng (phần trên) | TRONG vùng, sát mép trên; 83,6% trọng số dưới giá | không đổi |

Chưa qua fundamental-skeptic vòng 2. Không sửa `dd_price_zones.json`, không PDF/email.
