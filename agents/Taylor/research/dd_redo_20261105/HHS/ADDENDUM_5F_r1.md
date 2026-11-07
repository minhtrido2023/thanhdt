# HHS — ADDENDUM bước 3c: 5F tầng (b) + moat trong mô hình (07/11/2026, job Taylor_20261107_130213)

Bổ sung cho `REPORT_r2.md` (05/11/2026), không thay nó. **Kết luận: moat NONE / loại LOCATION (asset-play quỹ đất CRV Hải Phòng), KHÔNG bền — (i) trượt mọi cửa sổ ROIC/ROE, (iii) có đồng hồ (quỹ đất tự cạn). Mô hình hiện hành gần như nhất quán luật 3c: biên quỹ đất cũ kỳ vọng ≈ TB peer, P/E ô tô < 1/Ke, không terminal. Một lệch nhỏ: trục I.14 (dự án mới) có kỳ vọng thặng dư +6,25% (cắt một chiều −15/+40). BẢN CHẶT-3C (I.14 đối xứng, kỳ vọng 0): tâm 10.387 → 10.346 (−0,4%), nhãn TRONG giữ — quy ước chờ Mike/user duyệt; mức lệch không trọng yếu.**
Số: `5F/moat_sens_5f.py` (hằng số + `fv2` chép nguyên văn `calc/hhs_r2.py`, assert tái lập tâm/P10 REPORT_r2; chạy 2 lần trùng byte md5 `2ce48bf4…`) → `5F/moat_sens_5f_out.txt`; BQ `tav2_bq.ticker_financial` truy vấn 07/11/2026 → `5F/bq_annual.csv`, `5F/peer_stats_out.txt`.

## 1. Vị thế & lợi thế cạnh tranh (5F)
**Tái dùng hay làm mới: LÀM MỚI** — `data/moat_tags.csv` không có dòng HHS (cũng không có CRV/TCH); `kb/projects/hhs-dd-20261101.md`, `dd_HHS_20261101/{REPORT,SKEPTIC,GAPS*}.md`, REPORT/REPORT_r2 không có mục 5F/moat ⇒ chưa từng audit. Làm từ dữ liệu đang có trong thư mục + BQ; không nghiên cứu mới.

**Loại hình DN:** HOLDING — giá trị chủ yếu là 51,15% lợi ích CRV (BĐS nhà ở Hải Phòng, quỹ đất mua từ trước theo giá gốc; NC-II đã bán trước 3.099 tỷ) + đại lý xe tải Dongfeng (LNST 25/35/50 tỷ × P/E 5/6/8 ≈ 0,5k đ/cp, nhỏ) + tiền mẹ/Pruksa. Khung 5F = BĐS (bẫy: quỹ đất giá gốc ≠ hào) + phân phối ô tô.

| Lực | Mức | Cơ chế + bằng chứng (nguồn) |
|---|---|---|
| Rào cản gia nhập | 🟡 TB | BĐS: cần quỹ đất + pháp lý dự án. Lợi thế CRV là đất mua sớm giá gốc (biên NC-II ex-PPA 52,2% — `dd_HHS_20261101/REPORT.md` C7), nhưng dự án mới I.14 phải mua đất ~1.066 tỷ theo giá hiện hành (REPORT §5 TM18) ⇒ lợi thế không tái tạo. Xe tải: hợp đồng đại lý không có chữ "độc quyền" (REPORT_r2 §9.13). |
| Nhà cung cấp | 🔴 Cao | Nhà nước (tiền SDĐ: TB 2124/TB-TTCP N01 bổ sung 7,87 tỷ; KL 08 Pruksa điều chỉnh giá — §9.3–4). Dongfeng: phải trả 364,01 tỷ, HHS là đại lý (§9.10). |
| Người mua | 🟡 TB | Người mua nhà phân tán; NC-II đã thu trước 3.099,2 tỷ (cầu hiện tốt). NƠXH bị cơ quan nhà nước ép giá theo quyết toán (KL 08). Xe tải: khách doanh nghiệp vận tải, sản phẩm dễ so giá — biên gộp peer ô tô TB 2016–25 **6,6%** (HAX 5,7 · SVC 6,5 · TMT 7,6). |
| Sản phẩm thay thế | 🟡 TB | Dự án khác tại Hải Phòng (VHM có mặt — thị phần **cần kiểm chứng**); xe tải thương hiệu khác. |
| Cạnh tranh nội ngành | 🔴 Cao | 14 CĐT niêm yết nội địa (không phải đối thủ trực tiếp tại HP trừ TCH cùng nhóm): ROIC5Y trung vị **6,2%** (VHM 14,0 · HDG 12,6 · NTL 22,9 … NVL 0,8 · SCR −0,9) < Ke 13,5% ⇒ ngành không giữ được siêu ngạch. |
| **Lực thứ 6** | 🔴 | (a) **Quỹ đất tự cạn**: HTK CRV còn lại 7.338,8 tỷ (gồm I.14) bán hết trong ~4 năm (mô hình PV4) ⇒ "hào" giá gốc hết khi bán xong. (b) Cấu trúc holding/quản trị: kiểm soát CRV phụ thuộc uỷ quyền 7,53%, biên >50% chỉ 1,15đ% (§9.2). (c) Vay 390 tỷ CRV đáo hạn 18/11/2026 (§9.10). Pháp lý = WARNING, không dùng ép biên (luật 27/09). |

**moat_tier = NONE · moat_type = LOCATION (asset-play quỹ đất giá gốc, không phải rào cản tái tạo) · rủi ro số 1 = thực hiện thặng dư quỹ đất CRV còn lại (biên 24–47% theo kịch bản) + dòng tiền lên HHS qua 2 tầng holding (CK holding là trục quyết định nhãn — REPORT_r2 §3).**

## 2. Moat trong mô hình
| Điều kiện moat BỀN | KQ | Bằng chứng (BQ `ticker_financial` 07/11/2026, dòng Q4 = năm; Ke = r 13,5%) |
|---|---|---|
| (i) siêu ngạch nhiều chu kỳ | ❌ | **HHS phía trượt:** ROIC_Min5Y 0,0–2,0% (2016–24), −0,4% (2025–26Q3); ROIC5Y 0,3–2,6% (2019–26Q3); ROIC_Min10Y 0,0/−0,4%. ROE riêng (`ROE_Trailing` Q4): 2016 4,7 · 2017 2,9 · 2018 6,1 · 2019 6,1 · 2020 7,9 · 2021 6,0 · 2022 5,5 · 2023 8,0 · 2024 7,8 ⇒ < Ke 9/9 năm; ROE_Min5Y 5,3%. **Phía thuận (ghi đủ):** ROE 2025 22,1% và ROE5Y 15,7% — do lãi đánh giá lại khi hợp nhất CRV 3.488,72 tỷ (kế toán, không kinh tế — REPORT.md:94); ROIC5Y 330–335% (2015–18) và ROIC10Y 165–335% (đến 2023) = artifact dữ liệu (lệch 2 bậc so ROE cùng năm), không dùng. **CRV: không có trong BQ ⇒ cần kiểm chứng**; proxy TCH (cùng nhóm, HP): ROIC5Y 5,6–12,6% · ROIC_Min5Y 1,0–4,5% · ROIC10Y 7,0–11,9% · ROE_Trailing TB 2016–25 8,8% (min 3,1) ⇒ < Ke mọi cửa sổ. Dương duy nhất: biên NC-II 52,2% — MỘT dự án, đất giá gốc. |
| (ii) cơ chế rào cản gọi tên được | ⚠️ yếu | LOCATION = quỹ đất mua sớm; không tái tạo (I.14 mua giá thị trường); xe tải không độc quyền. |
| (iii) không có đồng hồ cắt hào | ❌ | Quỹ đất tự cạn ~4 năm (lực 6a). |

⇒ **moat_durable = false ⇒ luật 3c: RONIC = Ke VÀ biên về TB chu kỳ ngành.** Rà mô hình hiện hành (`calc/hhs_r2.py`, chép `hhs_redo.py`):
- **Không có terminal/RONIC**: NAV hữu hạn (backlog PV1, HTK cũ PV4); không có giá trị cuối kỳ ⇒ chặt hơn RONIC=Ke.
- **Biên quỹ đất cũ:** thặng dư s 15/40/55% (p 0,30/0,50/0,20), Δ±15pp đối xứng ⇒ E[s] 35,5% ⇔ biên gộp ~**37,7%** (quy đổi `g=(s+0,08)/(s+0,8)`, `dd_HHS_20261101/calc/valuation_v2.py:44`) = **TB peer 37,7% / trung vị 37,9%** (14 CĐT, GPM Q4 TB 2016–25; dòng Q4 GPM_P0 = cả năm, theo bài học A). Thấp hơn biên riêng NC-II 52,2% ⇒ **không giữ biên riêng trên TB ngành** ✔. Nhưng **cao hơn TB TCH 29,9%** (đối thủ trực tiếp duy nhất tại HP, cùng nhóm) ⇒ phụ thuộc chọn peer, ghi khoảng ở §3.
- **Backlog NC-II** (m 30/33,5/36% ròng × PV1): doanh thu ĐÃ KÝ/ĐÃ THU 3.099,2 tỷ, biên quan sát trên cùng dự án ⇒ dữ kiện hợp đồng, không phải giả định moat; ghi stress ở §3, không vào bản chặt.
- **Ô tô P/E:** E[P/E] = 6,1 < 1/Ke = 7,4 (giá trị không tăng trưởng, RONIC=Ke) ⇒ không thưởng ✔.
- **LỆCH 3c (nhỏ): I.14** (dự án mới) −15/0/+40% (0,25/0,50/0,25) ⇒ kỳ vọng **+6,25%** — thưởng NPV>0 cho dự án mới không có cơ sở moat. Bản chặt: I.14 đối xứng ±15% (kỳ vọng 0), giữ trọng số; kiểm thêm ±40% đối xứng — cùng tâm.
- BĐSĐT (chênh sổ HHS vs TCH, cận dưới) = giá trị tài sản hiện hữu, không phải moat ⇒ giữ. CK quản trị/pháp lý: WARNING, đã ở trục riêng, không đếm trùng; không dùng ép biên (bài học E).
- Quy ước năm 1/chiết khấu (bài học H): addendum dùng nguyên `pv(1)`/`pv(4)` @13,5% của mô hình, không chiết khấu lại.

## 3. Độ nhạy WIDE / NARROW / NONE (sau CK 5 tỷ; giá 9.550, 04/11/2026)
| Moat giả định | Ánh xạ | Tâm | P10 | P50 | P90 | % dưới giá | Nhãn 5 tỷ / 40tr / 10tr |
|---|---|---|---|---|---|---|---|
| WIDE | biên quỹ đất cũ = NC-II 52,2% (E[s] 70,6%), I.14 +40% chắc chắn | 11.648 | 9.276 | 11.417 | 14.365 | 13,7% | TRONG / TRONG / TRONG |
| NARROW | biên giữa 45,0% (E[s] 50,8%), I.14 như hiện hành | 10.840 | 8.614 | 10.638 | 13.379 | 26,1% | TRONG ×3 |
| Hiện hành (REPORT_r2) | E[s] 35,5% (~37,7%), I.14 +6,25% | 10.387 | 8.252 | 10.194 | 12.827 | 35,2% | TRONG ×3 |
| **BẢN CHẶT-3C** *(chờ duyệt)* | như hiện hành, I.14 ±15% đối xứng | **10.346** | **8.218** | **10.152** | **12.769** | 36,0% | TRONG ×3 |
| — biên = trung vị peer 37,9% | | 10.359 | 8.229 | 10.165 | 12.785 | 35,6% | TRONG ×3 |
| — biên = TB peer 37,7% | | 10.348 | 8.220 | 10.154 | 12.772 | 35,9% | TRONG ×3 |
| NONE-sàn: biên = TB TCH 29,9% (E[s] 22,7%) | đối thủ HP trực tiếp | 9.999 | 7.960 | 9.811 | 12.317 | 43,4% | TRONG ×3 |
| Stress backlog m × 37,7/52,2 | ngoài 3c (hợp đồng đã ký) | 10.198 | 8.108 | 10.011 | 12.591 | 38,8% | TRONG ×3 |

Đọc: WIDE↔NONE-sàn = 9.999–11.648 (−3,7% / +12,1% so hiện hành); theo chọn peer (TB/trung vị 14 CĐT ↔ TCH) tâm chặt **9.999–10.359**. Giá 9.550 nằm giữa P10 và P90 ở MỌI biến thể và mọi cỡ ⇒ **nhãn không nhạy theo moat**, không phải ca ranh giới (P10 cao nhất 9.276 vẫn < giá). Luật 4 (giá ≤ 0,85×tâm) không đạt ở mọi biến thể (cần tâm ≥ 11.235; chỉ WIDE vượt). Biến số lớn hơn moat nhiều: CK holding (NAV thuần 13.506 — REPORT_r2 §3).

## 4. Thay đổi so với báo cáo hiện hành
REPORT_r2/SUMMARY.json **giữ nguyên, không sửa; không ghi `dd_price_zones`**. Theo luật 3c đúng nghĩa, headline là **BẢN CHẶT-3C: tâm 10.387 → 10.346 (−41, −0,4%), P10 8.252 → 8.218, P50 10.194 → 10.152, P90 12.827 → 12.769, % dưới giá 35,2% → 36,0%; nhãn TRONG → TRONG** — chênh 100% do trục I.14 (RONIC dự án mới = Ke); biên đã ở TB ngành nên phần biên đóng góp 0. **Quy ước chờ Mike/user duyệt**; mức lệch không trọng yếu, có thể giữ REPORT_r2 nguyên trạng. Rủi ro moat-sai chính là phía DƯỚI nếu chuẩn đúng là TCH (−3,7% tâm), không phải phía trên.

## 5. Đề xuất dòng moat_tags.csv (KHÔNG tự sửa — chỉ đề xuất)
entry = L (cấu trúc NGÀNH: CĐT nội địa ROIC5Y trung vị 6,2% < Ke; phân phối ô tô GPM ~6,6%; `moat_5f.py:33`) — lưu ý dòng VHM hiện ghi entry H cho cùng ngành, Mike rà nhất quán; moat_upgrade = N.
```
HHS,NONE,LOCATION,L,"Holding (51.15% CRV Hai Phong residential + Dongfeng truck dealer, non-exclusive). Never earned above Ke: ROE_Trailing 2.9-8.0% 2016-24 (2025 22.1% = 3,488bn consolidation revaluation, non-economic), ROIC5Y 0.3-2.6% 2019-26, ROIC_Min5Y ~0; 2015-23 ROIC5Y/10Y 165-335% = data artifact. CRV not in BQ (verify); proxy TCH ROIC5Y 5.6-12.6%, ROE avg 8.8%. Only edge = land bank at historical cost (NC-II ex-PPA GPM 52.2%) - self-depleting ~4y, new I.14 land bought at market. #1 risk: realising remaining CRV land-bank surplus + cash upstreaming through 2-tier holding (holding discount axis decides label); CRV control via 7.53% proxy votes; 390bn CRV loan due 2026-11-18",2026-11-07,5f_full_dd_redo,N
```

*Phân tích, không phải khuyến nghị đầu tư. 5F dùng kiến thức non-point-in-time ⇒ chỉ cho DD sống, cấm đưa vào backtest. Pháp lý/quản trị: chỉ WARNING (luật 27/09). Chưa qua fundamental-skeptic (Mike chạy).*
