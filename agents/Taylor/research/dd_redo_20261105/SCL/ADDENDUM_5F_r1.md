# ADDENDUM 5F — SCL · 07/11/2026 · job `Taylor_20261107_123141`

> Đây là phần bổ sung bước 3c cho `REPORT_r2.md` (05/11). DD **không làm lại**; mọi phần khác của REPORT_r2 giữ nguyên.
> - Tái lập: `$DNA_PYEXE -I calc/scl_5f.py` → `calc/scl_5f_out.txt`. Chạy 2 lần, md5 trùng `376113da…`. `model_scl_r2_out.json` không bị chạm (md5 `116156ab…` trước = sau).
> - Chân đối chứng WIDE (lưới r2 chép nguyên văn) cho tâm **22.769**, khớp REPORT_r2 (lệch 0 đ).
> - Số ROIC/ROE/GPM/NPM lấy từ `bq query tav2_bq.ticker_financial` ngày 07/11/2026, **có 2026Q3**.
>   - GPM: trung bình 4 quý có trọng số doanh thu, gọi là "GPM TTM".
>   - NPM năm = NP 4 quý / DT 4 quý.
>   - GPM_P0 chỉ là giá trị MỘT quý, nên không dùng làm số năm.
> - 5F dựa trên kiến thức LLM, non-point-in-time ⇒ CHỈ dùng cho DD sống, cấm đưa vào backtest.

## 1. Vị thế & lợi thế cạnh tranh (5F) — **LÀM MỚI**
**Vì sao làm mới:** `data/moat_tags.csv` không có dòng SCL. `REPORT_r1_20261029`, `SKEPTIC_R2_20261103` và `kb/projects/scl-dd-*.md` đều không có audit 5F. Chưa từng audit ⇒ làm đầy đủ theo `5F.md`.

**Loại hình DN:** SCL sản xuất VLXD không nung/nhẹ (AAC, ALC, vữa, keo, tro bay, thạch cao), nguyên liệu đầu vào là tro xỉ nhiệt điện.
- BCTC không có doanh thu theo mảng [REPORT_r1 §3].
- Ngành theo sector read của Bobby 29/10 (`kb/data_registry/market-state/sector_read_vlxd_nhe_aac_20261029.md`): **quyền định giá thấp**, CYCLICAL 0,5.
- **Không phải** bẫy doanh thu-không-lợi-nhuận: biên ròng TTM 12,7%.

| Lực | Mức | Bằng chứng định lượng · nguồn |
|---|---|---|
| Cạnh tranh nội ngành | 🔴 | **ROIC thấp hơn Ke 13,5% ở mọi cửa sổ** (§2). **GPM TTM 36,8%**, cao hơn peer A (gạch/ốp lát nội địa) trung vị 13,3%, trung bình 16,1% (VGC 29,5 · VHL 17,0 · VIT 13,3 · CVT 10,5 [Q2] · TCR 10,0). Nhưng **phần vượt đang mòn**: GPM năm 63,0% (2020) → 54,8 → 49,1 → 40,0 → **33,2% (2024)** → 34,8 → 36,8% TTM. Sector read: AAC phân mảnh, hàng đồng nhất |
| Đối thủ mới | 🟡 | Capex một dây chuyền AAC "vài chục đến >100 tỷ", thiết bị TQ chào bán sẵn [Bobby §2a]. Chính SCL đang xây Phả Lại với tổng vốn 262,9 tỷ (thiết bị Anhui Keda) [BCTC Q3, REPORT_r1 §2] ⇒ rào cản là vốn, không phải công nghệ |
| Quyền lực người mua | 🔴 | **Một tập đoàn BĐS = 58,5% phải thu KH** (67,9/116,0 tỷ) [BCTC HN Q3]. Báo chí nói Vingroup ~25% DT, *cần kiểm chứng*. Phía cầu: 4 CĐT ≈ 43% nguồn cung căn hộ mới H1/26 [VARS qua Bobby] |
| Quyền lực nhà cung cấp | 🟡 | Tro/thạch cao FGD bán qua **đấu giá của nhà máy điện**, hợp đồng thường 3 năm. Tro "cháy hàng" (Tuổi Trẻ 02/10/26). Đợt Thái Bình 2 năm 2023 trúng **gấp đôi giá khởi điểm** [Bobby §2b]. Hợp đồng tro của SCL (giá, thời hạn): *cần kiểm chứng* [REPORT_r1 #8] |
| Sản phẩm thay thế | 🔴 | Gạch tuynel **không bị cấm**; block xi măng rẻ hơn. VLKN thực tế ~28% so với mục tiêu 35–40% năm 2025 [Bobby §1b] |
| **Lực thứ 6** | 🟡 | (a) Quyền tiếp cận tro là tài sản hành chính, phải đấu giá lại theo chu kỳ hợp đồng ⇒ **đồng hồ tái đấu giá**. (b) Lộ trình giảm nhiệt điện than sẽ thu hẹp nguồn tro dài hạn; thời điểm cho Phả Lại *cần kiểm chứng*. (c) NĐ 209/2026 ưu đãi vật liệu nhẹ = lực đẩy chậm, không bắt buộc. (d) Thuế XK clinker có thể từ 5% về 10% sau 31/12/2026 ⇒ xi măng xuôi chuỗi sang vữa |

**moat_tier = NONE** · **moat_type = NONE** (ứng viên COST/LOCATION: tiếp cận tro sát nhà máy; chưa chứng minh được) · **entry = L**.
**Rủi ro số 1:** biên đang ở đỉnh 7 năm trong một ngành không có quyền định giá. Nếu khách BĐS tập trung chậm trả, hoặc tro bị đấu giá lại với giá cao hơn, biên về mức chu kỳ (TB 2020–TTM 8,3%).

## 2. Ba điều kiện moat BỀN (Ke = r = 13,5%)
| ĐK | KQ | Bằng chứng (hai phía) · BQ 2026Q3 |
|---|---|---|
| (i) Siêu ngạch nhiều chu kỳ | **TRƯỢT** | **ROIC:** ROIC3Y 11,7% · ROIC5Y **8,4%** · ROIC10Y **5,6%** · ROIC_Min3Y 7,0% · ROIC_Min5Y **−1,2%** · ROIC_Min10Y −1,2%. Không cửa sổ nào vượt Ke. Phía thuận chiều: ROIC3Y tăng từ 4,7% (2023Q3) lên 11,7%, nhưng vẫn dưới Ke. **ROE** (tách riêng, không thay cho ROIC): ROE TTM 24,4% (năm đỉnh) · ROE5Y 13,8% ≈ Ke · ROE_Min5Y 8,2% · ROE_Min10Y −8,7%. Cột `ROIC_Trailing` = 1,21 là bất thường nên **không dùng** (*cần kiểm chứng* định nghĩa) |
| (ii) Cơ chế gọi tên được | YẾU | GPM cao hơn peer là có thật, nhưng không chuyển thành ROIC > Ke. Hợp đồng tro chưa kiểm được |
| (iii) Không đồng hồ cắt hào | **TRƯỢT** | Tái đấu giá tro; giảm nhiệt điện than (lực 6) |

⇒ **moat_durable = false**. Không thưởng moat: RONIC = Ke, biên về TB chu kỳ ngành.

## 3. Moat trong mô hình — REPORT_r2 **ĐANG NGẦM thưởng moat** ⇒ KHÔNG nhất quán với 3c
- **Kênh RONIC.** Trục ROE 15/20% đều > Ke, nên bội số (1−g/ROE)/(r−g) ở g = 4% là **7,72 / 8,42**, so với 1/r = **7,41** khi RONIC = Ke.
  - Áp RONIC = Ke **đối xứng** cho mọi ô. Cả hai ô đều nằm trên Ke nên không có ô nào bị kéo lên.
  - Hệ quả: g hết ảnh hưởng tới giá trị.
- **Kênh biên.** Nhánh STRUCTURAL (w 0,2) giữ biên TTM 12,7%, là đỉnh 7 năm, **mãi mãi**. ADMIN_GATED giữ một nửa phần vượt.
  - Ngay cả CYCLICAL cũng chỉ quay về TB **của chính mã** (8,3–9,7%), cao hơn hẳn TB ngành.
  - TB chu kỳ ngành = trung bình NPM năm 2020..2025 + TTM của từng peer, rồi lấy trung vị/trung bình qua các peer:

    | Peer set | Trung vị | Trung bình |
    |---|---|---|
    | A (VGC, CVT, VIT, VHL, TCR) | 2,78% | 3,20% |
    | B (A + xi măng HT1, BTS, HOM, VCX) | 2,32% | 2,33% |
    | A bỏ VGC | — | 1,53% |
    | Riêng VGC | 9,89% (gồm KCN) | |

  - Tất cả peer là **nội địa, không phải đối thủ AAC trực tiếp**; đối thủ AAC phần lớn chưa niêm yết.
- **Fade tuyến tính** từ biên của từng ô lưới về m_ind: NONE N = 2 năm, NARROW N = 5 năm.
  - Năm 1 chiết khấu 1 kỳ, nhất quán với mô hình hiện hành (bội số áp lên E_TTM như E năm tới).
  - Trục phải thu, phần cộng lại lãi dự án và CK thanh khoản giữ nguyên.
- **Không đếm hai lần:** mô hình không có giảm trừ pháp lý (cờ pháp lý chỉ là WARNING); trục phải thu là rủi ro tín dụng, không phải moat; không dùng bội số premium.

## 4. Kết quả & độ nhạy
Đơn vị đ/cp CUM, sau CK 4,50% @5 tỷ. Giá cum 30.000. Lưới 324 ô.

| Phương án | Tâm | P10 | P50 | P90 | % dưới giá | Nhãn | Sleeve 40tr | Sau quyền (TERP 27.659) |
|---|---|---|---|---|---|---|---|---|
| WIDE (= REPORT_r2) | 22.769 | 17.348 | 23.312 | 27.119 | 98,4% | TRÊN | 23.640 | 21.319 · TRÊN |
| Chỉ RONIC = Ke | 20.848 | 16.109 | 22.011 | 24.934 | 100% | TRÊN | 21.646 | 19.656 · TRÊN |
| Chỉ biên → peer A trung vị (N5) | 11.264 | 9.765 | 11.384 | 12.619 | 100% | TRÊN | 11.696 | 11.354 · TRÊN |
| **HEADLINE — NONE chặt-3c** (RONIC = Ke + biên → A trung vị, N2) *(quy ước chờ Mike/user duyệt)* | **8.730** | 7.891 | 8.769 | 9.581 | 100% | **TRÊN** | 9.064 | 9.159 · TRÊN |
| NONE N2, A trung bình / B trung vị / A bỏ VGC | 9.343 / 8.078 / 6.935 | | | 10.214 / 8.909 / 7.731 | 100% | TRÊN | | |
| NARROW N5 (A trung vị; khoảng theo peer 9.180–11.200) | 10.685 | 9.217 | 10.893 | 12.019 | 100% | TRÊN | 11.095 | 10.853 · TRÊN |
| Cận dưới N0 (A trung vị) | 6.224 | | | 6.458 | 100% | TRÊN | | |
| Tham chiếu: RONIC = Ke + biên về TB **của chính mã** (mọi nhánh CYCLICAL) | 19.053 | 15.495 | 18.208 | 23.759 | 100% | TRÊN | | |
| Tham chiếu: biên → riêng VGC, NARROW N5 | 19.280 | | | 20.876 | 100% | TRÊN | | |

**Tách phần chênh WIDE → headline (−14.039):**
- RONIC = Ke chiếm **−1.920 (−8,4%)**.
- Phần còn lại đến từ **biên về TB ngành**.
- Hai kênh không cộng tuyến tính (biên × bội số); đo riêng: chỉ biên (N5) −11.504, chỉ RONIC −1.920.

⚠️ **Bẫy so sánh peer (phải đọc cùng headline).** SCL giữ biên ròng ≥ 4,7% mọi năm 2020–2025 (thấp nhất 2022), trong khi trung vị peer A là 2,8%. Biên ròng không so sánh được trực tiếp khi mảng kinh doanh và vòng quay tài sản khác nhau (SCL có tro bay/phụ gia, GPM 37% so với peer 10–30%).
- Biên peer A trung vị kéo ROE về ~**6,4%** (E 33,9 tỷ / VCSH 531,6), tức **dưới Ke vĩnh viễn**. Đó là giả định phá huỷ giá trị chứ không phải "RONIC = Ke".
- Bản dùng biên TB của chính mã + RONIC = Ke ⇒ **19.053**. ROE ngầm theo từng cách chuẩn hoá biên: 2020–TTM ~16,0% · 2023–TTM 18,5% · GM-gap 23,2% (DT TTM 925 tỷ).
- Hai cách chuẩn hoá sau vẫn cho ROE > Ke ⇒ bản này chưa chặt; nó là cận trên của nhánh "không thưởng".
- Headline vẫn theo **đúng chữ luật 3c**. Mike/user chọn neo: TB ngành (8.730) hay TB chu kỳ của mã (19.053).

## 5. Thay đổi so với báo cáo hiện hành
**Có đổi giá trị, KHÔNG đổi nhãn: TRÊN vùng (>P90) ở MỌI phương án, mọi peer set, cả cỡ 5 tỷ lẫn sleeve 10–40 triệu, cả CUM lẫn TERP.** Nhãn không nằm sát ranh giới: P90 lớn nhất 27.119 < giá 30.000.

| | Tâm | P10 | P50 | P90 |
|---|---|---|---|---|
| REPORT_r2 | 22.769 | 17.348 | 23.312 | 27.119 |
| Headline chặt-3c | **8.730 (−61,7%)** | 7.891 | 8.769 | 9.581 |
| Bản kinh tế nhất quán | 19.053 (−16,3%) | 15.495 | 18.208 | 23.759 |

- Ngưỡng về TRONG vùng hạ từ 27.119 xuống **9.581** (headline) hoặc 23.759 (bản nhất quán).
- Không ghi `dd_price_zones`, không sửa REPORT_r2/SUMMARY.json. Không đụng candidate/plan/lệnh.

## 6. Đề xuất dòng `data/moat_tags.csv` (chỉ đề xuất, không ghi)
`SCL,NONE,NONE,L,"ROIC never > Ke through cycle (ROIC5Y 8.4%, ROIC10Y 5.6%, ROIC_Min5Y -1.2% vs Ke 13.5%); TTM ROE 24% = peak-margin year (NPM 12.7% vs 2020-TTM avg 8.3%); GPM premium vs domestic VLXD peers eroding (63%->37% 2020->TTM); AAC fragmented, tuynel not banned; fly-ash input via ~3y power-plant auctions (re-auction clock); 58.5% trade AR one RE group",2026-11-07,5f,N`

## 7. Cần kiểm chứng
- Hợp đồng tro/thạch cao của SCL: nhà máy, giá, thời hạn.
- Lộ trình vận hành nhiệt điện Phả Lại.
- Doanh thu theo mảng.
- Thị phần AAC theo vùng.
- Tỷ trọng Vingroup trong DT.
- Định nghĩa cột `ROIC_Trailing`.
- Peer AAC trực tiếp (chưa niêm yết).
- Neo "TB chu kỳ ngành" khi biên không so sánh được giữa các mảng.
