# SIP — ADDENDUM bước 3c: 5F tầng (b) + moat trong mô hình (07/11/2026, job Taylor_20261107_130211)

Bổ sung cho `REPORT_r2.md` (05/11), không thay nó. **Kết luận: moat NARROW · LOCATION/REGULATORY, KHÔNG bền. Mô hình hiện hành KHÔNG nhất quán với luật 3c** (RONIC mảng vận hành = ROE5Y 29,7% > Ke, biên TTM giữ vĩnh viễn). Hiện hành: tâm **54.230** · P10 43.784 · P50 53.086 · P90 68.713 (sau CK 5 tỷ). **BẢN CHẶT-3C (headline, quy ước chờ Mike/user duyệt): tâm 49.253 (−9,2%) · P10 38.904 · P50 48.119 · P90 63.762; nhãn TRONG vùng giữ nguyên** (giá 49.000 ≈ tâm, −0,5%; không ở ranh giới P10/P90).
Số: `5F/sip_moat_sens.py` → `5F/sip_moat_sens_out.txt/json` (exec nguyên phần khai báo `calc/model_sip_r2.py`, tái lập đúng 54.230; chạy 2 lần, lần 2 `env -u TZ`, md5 out trùng `1eeb8b19…`; bản sửa r2 sau skeptic, bản cũ `*_r1`). ROIC/GPM: BQ `ticker_financial` truy vấn 07/11/2026, file `../SZL/5F/bq_fin_peers_20261107.csv` (dòng SIP). Quy ước BQ: `GPM_P0` = TTM ⇒ dòng Q4 = GPM cả năm; `Revenue_P0` = quý.

## 1. Vị thế & lợi thế cạnh tranh (5F)
**Làm MỚI đầy đủ:** SIP không có dòng trong `data/moat_tags.csv`; DD 01/11 (`kb/projects/sip-dd-20261101.md`, `dd_SIP_20261101/REPORT.md`) không có mục 5F ⇒ chưa có audit 5F nào.
**Loại hình DN:** chủ đầu tư 5 KCN (3.205 ha, 2.441 ha thương phẩm, còn **937 ha** chưa thuê, lấp đầy 61,6% [AR25]) + **bán lẻ điện nước trong KCN** (9T26: 82% DT, biên gộp 8,7%, LN gộp 497 tỷ +13% YoY [REPORT §2]). Tiền thuê thu trước, ghi nhận phân bổ (DT chưa thực hiện 15.077 tỷ). Ngành tầng (a) — Bobby: ADMIN_GATED .40 / CYCLICAL .40 (`sector_read_kcn_cho_thue_dat_20261101.md`).

| Lực | Mức | Cơ chế + bằng chứng (nguồn) |
|---|---|---|
| Rào cản gia nhập | 🟡 TB | KCN cần quy hoạch + giao đất + GPMB (đền bù Phước Đông GĐ3 đã tạm ứng 2.421 tỷ, >90% [CBTT]) ⇒ rào cản vốn/hành chính, nhưng Tây Ninh/Đồng Nai có nhiều KCN mới (BCM/KBC/IDC/SZC cùng vùng). Không độc quyền đất. |
| Nhà cung cấp | 🔴 Cao | Nhà nước (đất, bảng giá đất ⇒ đền bù tăng — Bobby) và **EVN** (giá mua điện đầu vào; phải trả Điện lực Tây Ninh 168,7 tỷ [REPORT §2]). Biên điện nước do chênh biểu giá quy định, không do SIP định giá. |
| Người mua | 🟢 Thấp–TB | Khách thuê ký hợp đồng dài, trả trước; điện nước trong KCN là kênh **captive** (switching cost cao sau khi ký). Tập trung khách top-10: **cần kiểm chứng**. |
| Sản phẩm thay thế | 🟡 TB | Đất: KCN lân cận (Tây Ninh giá −6,8% YoY, lấp đầy 61% — Bobby). Điện: khả năng khách mua điện trực tiếp/tự sản xuất (DPPA, điện mặt trời mái nhà) theo khung luật điện mới — **cần kiểm chứng** mức ảnh hưởng tới kênh bán lẻ trong KCN. |
| Cạnh tranh nội ngành | 🟡 TB | ROIC_Min5Y SIP **11,0%** vs trung vị 11 peer KCN nội địa **4,0%** (SZL 5F stats, cùng file BQ) ⇒ ổn định hơn peer nhờ dòng tiện ích. Cho thuê chậm: 2025 **28,6 ha** vs KH 45 [AR25]; 72% quỹ đất còn lại ở Phước Đông B (Tây Ninh, vệ tinh) lấp 25%. |
| **Lực thứ 6** | 🔴 | (a) **Đồng hồ quỹ đất**: 937 ha ≈ 22 năm ở tốc độ cơ sở ~43 ha/năm (REPORT_r2 §7); đất lõi còn ít (LMX3 97,7 ha, Đông Nam 21,5, Lộc An-Bình Sơn 115,5). (b) **Thời hạn KCN/giấy phép bán lẻ điện**: chưa đọc QĐ — **cần kiểm chứng**. (c) Chính sách: TT99/2025 (SIP đã phân bổ từ trước — không gãy), biểu giá điện/cơ chế mua bán điện trực tiếp, tiền thuê đất trả Nhà nước (G16 chưa có số). |

**moat_tier = NARROW · moat_type = LOCATION/REGULATORY · rủi ro số 1 = tốc độ & giá thực thu 937 ha (72% ở Phước Đông B vệ tinh, 2025 chỉ 28,6 ha) — quỹ đất là đồng hồ của mảng đất; kênh điện nước captive phụ thuộc biểu giá EVN/chính sách mua điện trực tiếp.** (Cờ quản trị/tín dụng 6.016 tỷ + tạm ứng 635,6 tỷ: WARNING ở REPORT_r2 §6, không dùng trong 5F.)

## 2. Moat trong mô hình
| Điều kiện BỀN | KQ | Bằng chứng (BQ 2026Q3; Ke = r 13,5%) |
|---|---|---|
| (i) siêu ngạch nhiều chu kỳ | ❌ (hỗn hợp) | **Phía thuận:** ROIC5Y **15,7%**, ROIC10Y **15,9%** > Ke; ROIC5Y 2020–24 16,2–19,9%. **Phía nghịch:** ROIC_Min5Y **11,0%** < Ke; ROIC3Y **12,3%** < Ke và giảm dần (22,0% 2021 → 12,3%); (ROIC_Min10Y 1,0% **không dùng** — cột đóng băng đến 2025Q3, cùng loại artifact với ROIC_Trailing 100% / _v1 44,8% mâu thuẫn ROIC5Y ⇒ cả hai loại bỏ đối xứng; ROIC_Min5Y 11,0% < Ke vẫn đứng độc lập). Lưu ý ROIC_xY chỉ cập nhật ở dòng Q4 (dòng 2026Q3 = số FY2025). **ROE riêng:** ROE_Trailing 26,9%, ROE_Min5Y 27,9% — bị đẩy bởi vốn chiếm dụng (DT chưa thực hiện 15.077 tỷ không lãi + tiền gửi 7.188 tỷ sinh lãi), không thay được ROIC. |
| (ii) cơ chế gọi tên được | ✅ | LOCATION (quỹ đất KCN đã giao) + REGULATORY (kênh phân phối điện nước captive trong KCN của mình). |
| (iii) không đồng hồ | ❌ | Quỹ đất 937 ha hữu hạn (~22 năm cơ sở); thời hạn KCN/giấy phép điện chưa kiểm chứng; rủi ro chính sách mua điện trực tiếp. |

⇒ **moat_durable = false ⇒ luật 3c: RONIC = Ke VÀ biên về TB chu kỳ.** Rà `calc/model_sip_r2.py` — **KHÔNG nhất quán**, hai kênh:
- **(R) RONIC:** `pe = (1 − g/ROE5Y)/(r − g)`, ROE5Y = **29,7%** (ROE, không phải ROIC; > cả ROIC5Y 15,7%) ⇒ thưởng moat ngầm vĩnh viễn trên g 2–4%. Ở g 3%: PE lõi 8,562 → RONIC=Ke **7,407 (−13,5%)**. Bản chặt: RONIC = r của TỪNG ô, áp **đối xứng** mọi g {2,3,4}% và mọi r trong độ nhạy (không cắt một chiều). Quy ước năm 1 giữ nguyên model (E năm 1 = E hiện hành × payout, không nhân (1+g)) — kiểm H.
- **(M) Biên:** LN lõi = LN gộp 9T26 ×4/3 (ex-đất) giữ vĩnh viễn, GPM TTM Q3/26 **15,47%** > TB 2019–25 của chính SIP **14,63%** (GPM năm = dòng Q4: 13,96/13,56/16,36/14,93/13,94/14,04/15,63%). **Bất định TB 2019–25:** GPM 2021 Q3 và Q4 trùng 10 chữ số (0,1636053468) ⇒ nghi giá trị Q4 chép tiếp từ Q3 (không phải số năm thật); nếu sai, TB 14,63% lệch và (M) 78,2 tỷ đổi theo — **cần kiểm chứng** với BCTC 2021 (không hiệu chỉnh ở đây). Bản chặt: trừ (15,47−14,63)pp × DT TTM 9.286 tỷ = **78,2 tỷ/năm LN gộp (−7,0% LN gộp lõi 1.115)** [UL: BH/QLDN giữ nguyên; GPM tổng có lẫn mảng đất ⇒ proxy]. Đối xứng: nếu GPM TTM < TB chu kỳ thì nâng lõi (code `sip_moat_sens.py:32` không còn `max(dgp,0)`); ở SIP dgp>0 nên hạ, số không đổi.
- **"TB chu kỳ NGÀNH" — KHÔNG dùng peer KCN:** GPM peer KCN (nội địa) tính theo định nghĩa khác hẳn (số peer không nêu: nguồn SZL 5F stats coi GPM_P0 là quý rồi trọng số lại TTM, sai quy ước BQ) — (SIP 82% DT là bán lại điện biên 8,7%) và nên không so được và không có cơ sở nâng lõi. Peer đúng nghĩa (bán lẻ điện nước KCN: IDC một phần) chưa có số tách mảng — **cần kiểm chứng**. Dùng TB riêng SIP là lệch khỏi chữ luật ⇒ chờ Mike duyệt (cùng quy ước SZL).
- **Đúng luật, CÓ caveat mảng BĐS:** 937 ha định giá theo giá thực thu thị trường (trục tỷ/ha), không thưởng moat; chi phí đã chi thu hồi ≤100% giá vốn (NPV 0); không bội số premium; PE trung vị peer chỉ là tham chiếu. Pháp lý/tín dụng: WARNING + trục lỗ tín dụng sổ sách, không dùng ép biên ⇒ không đếm hai lần.
- **Caveat mảng bán BĐS (`re`):** LN gộp 43,3 tỷ/9T là dự án hữu hạn, lumpy, nhưng đang vào lõi và được vốn hoá như perpetuity (×PE lõi). Bỏ hẳn khỏi lõi vĩnh viễn: **chặt-3c 48.082** (P10 37.722 · P50 46.949 · P90 62.602 · 59,6% dưới giá · TRONG) — cận dưới hiệu ứng, −1.171 (−2,4%) so 49.253.

## 3. Độ nhạy WIDE / NARROW / NONE (lưới khoá 2.916 kết cục, trọng số giữ nguyên; sau CK 5 tỷ 1,37%; giá 49.000)
| Moat giả định | Ánh xạ | Tâm | P10 | P50 | P90 | % dưới giá | Nhãn 5 tỷ | Nhãn 40 tr (tâm; P10/P90) |
|---|---|---|---|---|---|---|---|---|
| WIDE (= hiện hành REPORT_r2) | RONIC = ROE5Y 29,7%, biên TTM, vĩnh viễn | **54.230** | 43.784 | 53.086 | 68.713 | 33,0% | **TRONG** | TRONG (54.810; 44.252/69.447) |
| WIDE theo ROIC | RONIC = ROIC5Y 15,7% | 51.698 | 41.351 | 50.569 | 66.205 | 42,7% | TRONG | TRONG |
| chỉ (R) RONIC=Ke | | 50.841 | 40.483 | 49.751 | 65.354 | 46,3% | TRONG | TRONG |
| chỉ (M) biên TB chu kỳ SIP | | 52.390 | 41.942 | 51.262 | 66.891 | 39,9% | TRONG | TRONG |
| **CHẶT-3C NARROW** *(headline, chờ duyệt)* | (R)+(M), vĩnh viễn | **49.253** | **38.904** | **48.119** | **63.762** | 54,5% | **TRONG** | TRONG (49.780; 39.320/64.444) |
| NONE *(annuity 30 năm sửa: (1−(1+r)^−N)/r)* | chặt-3c + lõi chỉ 30 năm (ước lượng) | **48.812** | 38.464 | 47.696 | 63.324 | 57,0% | TRONG | TRONG (49.333; 38.876/64.002) |
| chặt-3c, bỏ hẳn mảng BĐS | chặt-3c − LN gộp `re` 43,3 tỷ/9T khỏi lõi | 48.082 | 37.722 | 46.949 | 62.602 | 59,6% | TRONG | TRONG (48.596; 38.126/63.271) |

- Tách chênh hiện hành → chặt (−4.977, −9,2%): (R) đứng riêng −3.389, (M) đứng riêng −1.840 (cộng −5.229 > −4.977 do tương tác: hạ biên làm nhỏ phần RONIC tác động). RONIC là kênh chính (~2/3).
- **Nhãn KHÔNG nhạy với moat**: mọi biến thể WIDE→NONE đều TRONG vùng ở cả 5 tỷ và 40 tr; giá 49.000 cách P10 chặt +26%, cách P90 −23%. Biên độ giá trị do moat sai: **~5.400 đ/cp (−10%) từ WIDE-ROE tới NONE (54.230→48.812)**, nhỏ hơn biên do trục đất (P10–P90 ~25k).
- Độ nhạy r của bản chặt (β=1, RONIC=Ke theo r): −100bp 51.731 · −50bp 50.451 · 0 49.253 · +50bp 48.130 · +100bp 47.075 (−4,4…+5,0%; dải hẹp hơn hiện hành ±2,9–6,5% vì PE lõi RONIC=Ke = 1/r).

## 4. Thay đổi so với báo cáo hiện hành
**Có đổi giá trị, KHÔNG đổi nhãn (nếu duyệt quy ước chặt-3c).** REPORT_r2/SUMMARY.json giữ nguyên; KHÔNG ghi `dd_price_zones`. Theo luật 3c: tâm **54.230 → 49.253 (−9,2%)**, P10 43.784 → 38.904, P50 53.086 → 48.119, P90 68.713 → 63.762; % trọng số dưới giá 33,0% → 54,5%; giá/tâm −9,6% → −0,5% ⇒ từ "nghiêng dưới tâm" thành "ngang tâm". Nhãn TRONG giữ ở 5 tỷ và 40 tr. Quy ước chờ Mike/user: (1) TB chu kỳ dùng của riêng SIP (peer KCN khác định nghĩa GPM); (2) RONIC=Ke áp cả g ≈ lạm phát. Ngưỡng nhãn mới (chặt): DƯỚI < 38.904, TRÊN > 63.762.

## 5. Đề xuất dòng moat_tags.csv (KHÔNG tự sửa file)
entry = M (cấu trúc ngành KCN: Bobby ADMIN_GATED/CYCLICAL, cùng mức IDC/SZL; `moat_5f.py:33` theo NGÀNH, không theo tier); `moat_upgrade` = N (không có chủ ý nâng — Mike quyết):
```
SIP,NARROW,LOCATION/REGULATORY,M,"5 IPs (937ha unleased, 72% at satellite Phuoc Dong B, 2025 leased only 28.6ha vs plan 45) + captive in-IP power/water resale (82% rev, 8.7% GPM, EVN-tariff-bound); NOT durable: (i) ROIC_Min5Y 11.0% / ROIC3Y 12.3% < Ke 13.5% (ROIC5Y 15.7%; ROE 27-30% flattered by 15tn prepaid-lease float + deposits), (iii) finite land bank ~22yr, IP/power-retail licence terms unverified, direct-power-purchase policy risk. #1 risk: lease pace & realised price on Phuoc Dong B. WARNING: 6.0tn unsecured lending to securities cos/bonds (116% equity), 635.6bn advances to insiders",2026-11-07,5f,N
```

## 6. Mở
Top khách thuê; thời hạn QĐ KCN + giấy phép bán lẻ điện; tách GPM theo mảng nhiều năm (để có "TB chu kỳ" đúng nghĩa cho điện nước và peer cùng định nghĩa, vd IDC); tác động DPPA/điện mái nhà lên kênh captive. **Quỹ đất 937 ha — giá 12 tỷ/ha ròng (kịch bản cơ sở, trọng số 0,50) là điểm dễ vỡ nhất:** theo brief Mike chiếm ~13.000 đ/cp ≈ 27% giá trị (ước lượng, chưa đo lại ở addendum) và dựa giá thực hiện '[báo]' chưa kiểm ⇒ **cần kiểm chứng**: giá ròng/ha từ DT chờ ghi nhận (15.077 tỷ) ÷ diện tích đã bán/hợp đồng, khi có số theo KCN. Không có số trong thư mục ⇒ không kiểm được ở vòng này. Chưa qua fundamental-skeptic (Mike chạy).

*Phân tích, không phải khuyến nghị đầu tư. 5F dùng kiến thức non-point-in-time ⇒ chỉ cho DD sống, cấm đưa vào backtest. Pháp lý: chỉ WARNING (luật 27/09).*
