# DD REDO — TCH (Hoàng Huy, HOSE) · mùa BCTC Q3/2026 · job `Taylor_20261105_014133` · 05/11/2026

> Chỉ NGHIÊN CỨU, không khuyến nghị. Số định giá: `calc/model.py` → `calc/model_out.txt/json`; `SUMMARY.json` sinh từ đó (`_common/summary.py`).
> **Nguồn BCTC**: KHÔNG tải lại. BCTC hợp nhất + riêng 01/04–30/09/2026 (Q2 năm tài chính = quý lịch 7–9/2026, **chưa soát xét**, ký 29/10/2026) đã đọc từ ảnh ở `../../dd_TCH_20261031/src/` + `calc/notes_read.md`; DD v2 đó đã qua fundamental-skeptic (REFUTED → đã áp). Mọi số BCTC dưới đây lấy từ v2, mục tham chiếu [v2 §x].
> Đọc ngành: `kb/data_registry/market-state/sector_read_bds_nha_o_do_thi_phia_bac_20261031.md` (Bobby, mù).
> **Giá 12.750 đ, đóng cửa 04/11/2026** [BQ `tav2_bq.ticker`]. Đơn vị tỷ đồng trừ khi ghi khác.

## 0. Kết luận

| | đ/cp |
|---|---|
| Tâm TRƯỚC chiết khấu thanh khoản (kỳ vọng trọng số 25/50/25) | **13.488** |
| Chiết khấu thanh khoản (vị thế 5 tỷ) | 0,64% |
| **Tâm SAU chiết khấu thanh khoản** | **13.401** |
| P10 / P50 / P90 SAU (lưới n=81) | **12.559 / 13.387 / 14.205** |
| P10 / P90 TRƯỚC | 12.641 / 14.297 |
| Giá 12.750 so tâm / P10 / P90 | −4,9% / +1,5% / −10,2% ⇒ **TRONG vùng (nửa dưới)** |

Tâm cũ (31/10) 12.650 ⇒ tâm mới **+5,9%** (lệch < 10%). Nguyên nhân chính: bỏ chiết khấu quản trị khỏi base (luật pháp lý/quản trị = WARNING), bù một phần bởi quỹ đất mới về NPV=0.

## 1. Giả thuyết (kiểm bằng số BCTC) [v2 §1, §3]
- "Lãi đột biến Q3 là thật": **ĐÚNG** — LNST hợp nhất quý 7–9/2026 750,5 tỷ, **phần mẹ 537,7** (BQ `NP_P0` 2026Q3 = 537,7, khớp), từ đợt bàn giao đầu NC-II (Thủy Nguyên). Biên gộp BĐS 6T 51,9%.
- "Là nền lợi nhuận mới": **SAI** — LN mẹ TTM ~796 vẫn dưới FY24 (855); NMTT NC-II −1.033 trong quý, ở nhịp này còn ~3 quý. Đây là chu kỳ bàn giao, không phải annuity.

## 2. Chất lượng lợi nhuận [v2 §3]
- Phần lớn LN đến từ ghi nhận bàn giao NC-II (qua CRV, TCH hưởng 68,02%) ⇒ LN mẹ riêng chỉ ~40 tỷ, hợp nhất 750.
- Một lần/dồn: đợt bàn giao lớn đầu tiên; LN chuẩn hoá cho ROE ~6% (EPS chuẩn hoá 675–775 đ, ước lượng v2).

## 3. Bảng cân đối / net cash thật [v2 §5a]
- Tiền + HTM hợp nhất 3.296,3 (3.285 đ/cp); phần mẹ ~2.960. **Vay 0, trái phiếu 0**.
- Trừ nợ tài chính khác 1.086,8 + thuế phải nộp 198,8 ⇒ **~2.010 tỷ (~2.000 đ/cp)**. NMTT 5.600 phải trả bằng nhà/đất; chi phí hoàn thành còn lại không công bố.
- Tiền + HTM giảm 2.910 trong 6T: **2.992,9 tiền sử dụng đất** cho 2 quỹ đất mới (I.14 1.326; 150 Tô Hiệu 1.667) — tiền chuyển thành đất, không mất.
- CFO hợp nhất âm (BQ `CF_OA_P0` 2026Q3 −1.483) — do nộp tiền đất, nhất quán.

## 4. Ghi nhận doanh thu, backlog [v2 §4]
Ghi nhận khi bàn giao (không POC). Backlog = NMTT: NC-II 3.099, Green River 1.838, H2 618. Kế hoạch FY26 LNST HN 2.000: cần H2-FY26 ~1.086.

## 5. Cổ đông, room, thanh khoản [v2 §6b; `_common/liq.py`]
- Nhóm ông Đỗ Hữu Hạ + HH Finance 35,99%; nước ngoài 10,51%/room 51%; Dragon Capital rời nhóm cổ đông lớn 06/2026.
- **ADV trung vị 87,1 tỷ/phiên** (250 phiên 03/11/2025–04/11/2026, BQ `ticker` Price×Volume), σ ngày 2,69%. Vị thế 5 tỷ = 0,3–0,6 phiên ở mức tham gia 20–10% ⇒ chiết khấu thanh khoản 0,6% (1 tỷ 0,3%, 10 tỷ 0,9%; công thức Y·σ·√(Q/ADV), Y=1; Y 0,5/1,5 trong `model_out.json`). Thanh khoản không phải ràng buộc.

## 6. ⚠️ WARNING pháp lý/quản trị — TRUNG BÌNH (không loại, không trừ vào base) [v2 §6d]
QĐ 1020/QĐ-XPHC 03/04/2026 (Thuế Hải Phòng, khai sai TNDN, 20,21 tỷ); QĐ 1357/QĐ-XPHC 12/2024 (UBCKNN, CBTT/bên liên quan, 295 tr); nhóm kiểm soát chiếm 71,2% phiếu ĐHĐCĐ; Trưởng BKS kiêm KTT công ty con; CRV free float ~3%. Không có khởi tố/kiểm toán ngoại trừ. **Độ nhạy (không trong base)**: nếu thị trường áp chiết khấu quản trị 5/10/15% ⇒ tâm sau CK 12.731 / 12.061 / 11.391.

## 7. Định giá — NAV dự án
**Chi phí vốn**: r = 13,5% + β·(lãi huy động 12T hiệu dụng − 7,40%), β=1 (giả định). Lãi huy động hiệu dụng 04/11/2026 = **7,40%** (`deposit_rate_vn.effective_deposit_rate`, nguồn CCTG 12M 02/11/2026; Big-4 6,8%) = điểm neo ⇒ **r = 13,5%**. Ke nội địa, không CRP.

NAV = VCSH mẹ trực tiếp 5.958,6 + VCSH mẹ qua con 6.200,5 + lãi backlog (NMTT ex-VAT × biên ròng × phần sở hữu × PV) + thặng dư HTK đất cũ × PV 4 năm − chiết khấu holding (chỉ phần qua công ty con).
**Dự án mới (luật 03/11)**: 150 Tô Hiệu (mẹ, HTK 1.677,5) và I.14 (Đại Lộc/CRV, 1.328,8) — đất vừa mua 6T, **base NPV = 0** (giá sổ). Lý do không cộng thặng dư: chưa có giá bán/hợp đồng đầu ra kiểm được. Độ nhạy thặng dư quỹ đất mới −10/+10/+25% ⇒ tâm 13.258/13.545/13.760.
**Khoản giảm trừ trong base và cơ sở dữ liệu**: chiết khấu holding 20% phần qua con — cơ sở: 2 tầng niêm yết, CRV free float ~3% / khớp 24/62 phiên (DNSE, v2 §8d), dòng tiền NC-II lên TCH phải qua cổ tức CRV. Không có khoản giảm trừ nào khác.

| Kịch bản (ước lượng) | P | Biên ròng backlog | Thặng dư đất cũ | CK holding | Trước CK TK | Sau CK TK |
|---|---|---|---|---|---|---|
| Xấu | 0,25 | 30% | 25% | 30% | 12.060 | 11.983 |
| Cơ sở | 0,50 | 33,5% | 40% | 20% | 13.474 | 13.387 |
| Tốt | 0,25 | 36% | 55% | 10% | 14.945 | 14.848 |
| **Kỳ vọng** | | | | | **13.488** | **13.401** |

Thặng dư 40% ở cơ sở: dưới biên lịch sử (51,9% gộp ⇔ s≈70%) vì NC-II còn lại gồm cao tầng HH1–HH4 (ước lượng; lệch thận trọng nhẹ, giữ từ v2).
**Lưới P10–P90** (n=81): biên ròng {30; 33,5; 36}% × thặng dư đất cũ {25; 40; 55}% × holding {30; 20; 10}% × r {12,5; 13,5; 14,5}%, trọng số 1/4–1/2–1/4 mỗi biến, phân vị có trọng số.

## 8. Độ nhạy r theo lãi huy động (tâm trước CK) — PV ngắn nên nhạy thấp
| Δ lãi huy động | β=1,0 | β=0,5 |
|---|---|---|
| −100bp | +68 đ (+0,5%) | +34 đ (+0,2%) |
| −50bp | +34 đ (+0,2%) | +17 đ (+0,1%) |
| +50bp | −33 đ (−0,2%) | −17 đ (−0,1%) |
| +100bp | −65 đ (−0,5%) | −33 đ (−0,2%) |

## 9. Mốc khoá trước + điều kiện đổi nhận định (hai chiều; P ước lượng)
| Mốc | Ngày chấm | Lên | Xuống |
|---|---|---|---|
| BCTC soát xét 6T FY26 (AASC) | 30/11/2026 | LN mẹ 6T trong ±5% của 663,1, không ngoại trừ ⇒ giữ | điều chỉnh >5% / ngoại trừ ⇒ hạ tâm ~1.000, nâng WARNING |
| Quý 10–12/2026 (Q3FY26) | ~31/01/2027 | LN mẹ ≥ 400 + NMTT NC-II bổ sung (HH1–HH4 mở bán) ⇒ đẩy biên/thặng dư lên nhánh tốt (~14.800) | NMTT giảm tiếp mà không bổ sung, biên gộp < 40% ⇒ nhánh xấu (~12.000) |
| Quỹ đất mới có giá bán/đặt cọc công bố | 2027 | biên gộp ≥ 35% có số ⇒ cộng thặng dư quỹ đất mới (+150–360 đ) | vượt dự toán/chậm pháp lý có tín hiệu ⇒ kịch bản âm |
| Sử dụng vốn 865,5 tỷ đúng mục đích | 31/03/2027 | giữ | đổi sang cho công ty con vay ⇒ nâng WARNING |

## 10. Ngành → doanh nghiệp
Đọc ngành BĐS nhà ở đô thị phía Bắc (Bobby 31/10) đã đối chiếu ở v2 §10; không đổi.

## Phụ lục — cái gì ĐỔI so với DD 31/10 (v2) và vì sao
| Mục | v2 31/10 | Redo 05/11 | Lý do |
|---|---|---|---|
| r / Ke | 12,85% (tâm 12,3–13,4%) | **13,5%** (neo lãi huy động 7,40%) | luật 03/11 |
| Chiết khấu quản trị | 15/10/5% trong kịch bản | **0 trong base**, chỉ độ nhạy | pháp lý/quản trị = WARNING |
| Quỹ đất mới 3.006 tỷ | gộp vào thặng dư 40% | **NPV 0** mọi điểm | luật dự án mới 03/11 |
| Thặng dư kịch bản xấu | 15% | 25% | lưới đối xứng quanh 40% |
| Chiết khấu thanh khoản | không | 0,64% (5 tỷ) | luật 03/11 |
| Vùng | 10.150–15.050, tâm 12.650 (min/max kịch bản) | P10–P90 12.559–14.205, tâm 13.401 | P10/P90 từ lưới, không dùng min/max |
| Giá | 11.850 (30/10) | 12.750 (04/11) | |
Tâm lệch +5,9% (<10%). Vùng hẹp lại vì bỏ chiết khấu quản trị (biến nhạy nhất v2) khỏi lưới; rủi ro đó nằm ở WARNING + độ nhạy §6.

Giới hạn: mọi tham số NAV là ước lượng; BCTC chưa soát xét; chưa qua fundamental-skeptic cho bản redo (Mike chạy).
