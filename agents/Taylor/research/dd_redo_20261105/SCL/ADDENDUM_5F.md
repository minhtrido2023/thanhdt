# ADDENDUM 5F — SCL · r2 07/11/2026 · job `Taylor_20261107_125218` (r1: `ADDENDUM_5F_r1.md`, job `_123141`)

> Bổ sung bước 3c cho `REPORT_r2.md` (05/11). DD **không làm lại**; mọi phần khác của REPORT_r2 giữ nguyên.
> - Tái lập: `$DNA_PYEXE -I calc/scl_5f.py` → `calc/scl_5f_out.txt`. Chạy 2 lần trùng byte (md5 txt `b2659c1a…`, json `94e3353b…`). `model_scl_r2_out.json` không bị chạm (md5 `116156ab…` trước = sau).
> - **r2 sửa lỗi GPM** (skeptic): `GPM_P0` của BQ là **TTM 4 quý trượt**, không phải quý (BCTC Q3/26 biên quý 41,2% vs BQ 38,67%). GPM năm = giá trị **Q4** của `GPM_P0`; TTM = 2026Q3. Không lấy TB/trọng số lại chuỗi `GPM_P0`.
>   - Lỗi này nằm ở lõi `calc/scl_r3_core.py:41` (TB 4 số TTM chồng lấn) ⇒ `GM_GAP` (:57) 0,36pp, đúng **3,27pp** ⇒ trục norm "GM-gap" (1/3 trọng số) 12,44% → **10,11%**. Sửa trong **bản sao** `calc/scl_r3_core_5Ffix.py` (chỉ dòng :41, ghi `model_r3_5Ffix_out.*`); lõi gốc không đổi. **Việc của REPORT_r2 — chờ Mike** (chênh: §5).
>   - Chân đối chứng WIDE dùng lõi GỐC tái lập **22.769** (lệch 0 đ so với REPORT_r2); mọi biến thể khác dùng lõi sửa.
> - Số ROIC/ROE/GPM/NPM: `bq query tav2_bq.ticker_financial` 07/11/2026, có 2026Q3. NPM năm = NP 4 quý / DT 4 quý (Revenue_P0/NP_P0 là số QUÝ).
> - 5F dựa trên kiến thức LLM, non-point-in-time ⇒ CHỈ dùng cho DD sống, cấm đưa vào backtest.

## 1. Vị thế & lợi thế cạnh tranh (5F) — **LÀM MỚI**
**Vì sao làm mới:** `data/moat_tags.csv` không có dòng SCL; `REPORT_r1_20261029`, `SKEPTIC_R2_20261103`, `kb/projects/scl-dd-*.md` không có audit 5F.

**Loại hình DN:** VLXD không nung/nhẹ (AAC, ALC, vữa, keo, tro bay, thạch cao), đầu vào tro xỉ nhiệt điện. BCTC không tách DT theo mảng [REPORT_r1 §3]. Sector read Bobby 29/10 (`kb/data_registry/market-state/sector_read_vlxd_nhe_aac_20261029.md`): **quyền định giá thấp**, CYCLICAL 0,5. Không phải bẫy DT-không-lãi: biên ròng TTM 12,7%.

| Lực | Mức | Bằng chứng định lượng · nguồn |
|---|---|---|
| Cạnh tranh nội ngành | 🔴 | **ROIC5Y/ROIC10Y < Ke 13,5%** (§2). **GPM TTM 38,7%** (2026Q3) vs peer nội địa GPM_P0 mới nhất: VGC 30,7 · VHL 17,6 · VIT 16,0 · TCR 12,0 · CVT 10,3 [2026Q2] ⇒ **trung vị 16,0%, TB 17,3%**; SCL ≈ **2,4×** trung vị. GPM năm (Q4): 62,8 (2020) → 53,4 → 49,0 → 35,4 → **32,2 (2024)** → 35,3 (2025) → **38,7 TTM**: phần vượt **mòn 2020→2024 rồi HỒI qua 7 quý** (32,2% 2024Q4 → 38,7% 2026Q3; không đơn điệu: 2025Q4–2026Q1 chững ~35%). Sector read: AAC phân mảnh, hàng đồng nhất |
| Đối thủ mới | 🟡 | Capex 1 dây chuyền AAC "vài chục đến >100 tỷ", thiết bị TQ sẵn [Bobby §2a]. Chính SCL xây Phả Lại 262,9 tỷ (Anhui Keda) [BCTC Q3, REPORT_r1 §2] ⇒ rào cản là vốn, không phải công nghệ |
| Quyền lực người mua | 🔴 | **Một tập đoàn BĐS = 58,5% phải thu KH** (67,9/116,0 tỷ) [BCTC HN Q3]. Vingroup ~25% DT: *cần kiểm chứng*. 4 CĐT ≈ 43% nguồn cung căn hộ mới H1/26 [VARS qua Bobby] |
| Quyền lực nhà cung cấp | 🟡 | Tro/thạch cao FGD qua **đấu giá của nhà máy điện**, HĐ thường 3 năm; tro "cháy hàng" (Tuổi Trẻ 02/10/26); Thái Bình 2 (2023) trúng **gấp đôi giá khởi điểm** [Bobby §2b]. HĐ tro của SCL: *cần kiểm chứng* [REPORT_r1 #8] |
| Sản phẩm thay thế | 🔴 | Gạch tuynel **không bị cấm**; block xi măng rẻ hơn. VLKN ~28% vs mục tiêu 35–40% năm 2025 [Bobby §1b] |
| **Lực thứ 6** | 🟡 | (a) Quyền tiếp cận tro = tài sản hành chính, tái đấu giá theo chu kỳ HĐ ⇒ **đồng hồ tái đấu giá**. (b) Giảm nhiệt điện than thu hẹp nguồn tro dài hạn (thời điểm Phả Lại *cần kiểm chứng*). (c) NĐ 209/2026 ưu đãi vật liệu nhẹ = lực đẩy chậm. (d) Thuế XK clinker có thể 5%→10% sau 31/12/2026 |

**moat_tier = NONE** · **moat_type = NONE** (ứng viên COST/LOCATION: tro sát nhà máy, bán kính kinh tế 150–300 km [Bobby]; chưa chứng minh thành ROIC>Ke nhiều chu kỳ) · **entry = L**.
**Rủi ro số 1:** biên ròng TTM 12,7% là đỉnh 7 năm trong ngành không có quyền định giá; khách BĐS tập trung chậm trả hoặc tro bị tái đấu giá giá cao ⇒ biên về chu kỳ (TB 2020–TTM 8,3%).

## 2. Ba điều kiện moat BỀN (Ke = r = 13,5%)
| ĐK | KQ | Bằng chứng (hai phía) · BQ 2026Q3 |
|---|---|---|
| (i) Siêu ngạch nhiều chu kỳ | **TRƯỢT** | **Phía chống:** ROIC5Y **8,4%** · ROIC10Y **5,6%** · ROIC3Y 11,7% — đều < Ke. ROE năm TB 2020–25 ≈ **13,8% ≈ Ke** (15,0/11,1/8,6/19,1/9,9/19,3). **Phía thuận:** ROIC TTM *ước tính* ~**15,7%** (NOPAT ~134 tỷ = NP TTM 117,7 + lãi vay sau thuế ~16,5 / IC ~855 tỷ; ~20% nếu bỏ 205,5 tỷ XDCB dở dang) > Ke — *ước tính, chưa đối chiếu BCTC*; nhưng là **một năm ở đỉnh biên**. ROE TTM 24,4% cũng là năm đỉnh. Các cột `ROIC_xY` **chỉ cập nhật theo năm** (2026Q1–Q3 = giá trị 2025Q4) ⇒ chưa phản ánh 9T/26. **Sàn dùng:** ROIC5Y 8,4%/ROIC10Y 5,6% và ROE năm thấp nhất **8,6%** (2022). `ROIC_Min5Y` −1,2% **không dùng — cần kiểm chứng** (nghi artifact: NP năm dương mọi năm 2020–25, biên ròng năm thấp nhất 4,66%, ROE năm thấp nhất 8,6%; NOPAT ≥ NP > 0 ⇒ ROIC năm không thể âm; cùng họ với `ROIC_Trailing` 1,21 bất thường đã loại) |
| (ii) Cơ chế gọi tên được | YẾU | GPM ≈ 2,4× trung vị peer là thật (tro bay/phụ gia tự có, bán kính vận chuyển 150–300 km), nhưng chưa thành ROIC5Y > Ke. So sánh `data/moat_tags.csv`: GMD (nhượng quyền cảng nước sâu), BWE (độc quyền cấp nước tỉnh), HTI (BOT tới ~2032), NTC (đất KCN cấp phép) được NARROW dù lợi nhuận mỏng vì có **nhượng quyền/giấy phép dài hạn** (thời hạn cụ thể từng mã: *cần kiểm chứng*). Hào của SCL là **HĐ đấu giá tro ~3 năm** — ngắn hơn nhiều, tái đấu giá được ⇒ không đủ để coi là cơ chế bền |
| (iii) Không đồng hồ cắt hào | **TRƯỢT** | Tái đấu giá tro ~3 năm; giảm nhiệt điện than (lực 6) |

⇒ **moat_durable = false**. Không thưởng moat: RONIC = Ke, biên/ROE về mức chu kỳ.

## 3. Moat trong mô hình — REPORT_r2 **ĐANG NGẦM thưởng moat** ⇒ KHÔNG nhất quán với 3c
- **Kênh RONIC.** Trục ROE 15/20% đều > Ke ⇒ bội số (1−g/ROE)/(r−g) ở g = 4% là **7,72 / 8,42** vs 1/r = **7,41** khi RONIC = Ke. Áp RONIC = Ke đối xứng mọi ô (cả hai ô > Ke nên không ô nào bị kéo lên); g hết ảnh hưởng.
- **Kênh biên.** STRUCTURAL (w 0,2) giữ biên TTM 12,7% (đỉnh 7 năm) **mãi mãi**; ADMIN_GATED giữ nửa phần vượt; CYCLICAL về TB **của chính mã** (8,3% / 9,7% / GM-gap 10,1% sau sửa).
- **Neo "không thưởng" — hai cách, chọn cách đối xứng làm headline:**
  - (a) **ROE → Ke** (headline r2): E năm đích = Ke × VCSH mẹ 531,6 = **71,8 tỷ** ⇒ V = sổ sách (**13.688 đ/cp** trước CK). Fade tuyến tính E ô lưới → E đích trong N năm. Đúng định nghĩa NONE (ROIC fade → Ke), **không** ép SCL xuống biên peer chưa từng thấy.
  - (b) **Biên → TB chu kỳ ngành peer** (headline r1, nay là **cận dưới**): m_ind = TB NPM năm 2020..TTM từng peer, trung vị/TB qua peer (A: VGC, CVT, VIT, VHL, TCR trung vị 2,78%, TB 3,20%; B = A + HT1/BTS/HOM/VCX trung vị 2,32%). Ép ROE ≈ **6,4% < Ke vĩnh viễn** (E 33,9 tỷ / 531,6) trong khi biên ròng năm thấp nhất của SCL là 4,7% ⇒ **vi phạm vế đối xứng** (đó là giả định phá huỷ giá trị, không phải RONIC = Ke). Peer là VLXD nội địa, không phải đối thủ AAC trực tiếp (chưa niêm yết).
- Fade: NONE N = 2, NARROW N = 5, N0 = tức thời. Năm 1 chiết khấu 1 kỳ, nhất quán mô hình hiện hành (bội số áp lên E_TTM như E năm tới). Trục phải thu, cộng lại lãi dự án, CK thanh khoản giữ nguyên.
- **Không đếm hai lần:** không có giảm trừ pháp lý (chỉ WARNING); trục phải thu là rủi ro tín dụng, không phải moat; không dùng bội số premium.

## 4. Kết quả & độ nhạy (lõi đã sửa GPM)
Đơn vị đ/cp CUM, sau CK 4,50% @5 tỷ. Giá cum 30.000. Lưới 324 ô.

| Phương án | Tâm | P10 | P50 | P90 | % dưới giá | Nhãn | Sleeve 40tr | Sau quyền (TERP 27.659) |
|---|---|---|---|---|---|---|---|---|
| Đối chứng WIDE = REPORT_r2 (lõi gốc) | 22.769 | 17.348 | 23.312 | 27.119 | 98,4% | TRÊN | 23.640 | 21.319 · TRÊN |
| WIDE (lõi sửa GPM) | 21.813 | 17.348 | 21.445 | 26.672 | 98,4% | TRÊN | 22.648 | 20.491 · TRÊN |
| Chỉ RONIC = Ke | 19.973 | 16.109 | 19.595 | 24.819 | 100% | TRÊN | 20.737 | 18.897 · TRÊN |
| Cận trên: RONIC = Ke + biên TB **của chính mã** (mọi nhánh CYCLICAL) | 17.705 | 15.495 | 17.935 | 19.595 | 100% | TRÊN | | |
| **HEADLINE — NONE: ROE → Ke, N2** *(quy ước chờ Mike/user duyệt)* | **14.183** | 13.487 | 14.124 | 14.761 | 100% | **TRÊN** | 14.726 | 13.882 · TRÊN |
| ROE → Ke N0 / N5 | 12.986 / 15.117 | 12.805 / 13.813 | | 13.072 / 16.221 | 100% | TRÊN | | |
| Cận dưới: biên → peer A trung vị, N2 | 8.580 | 7.891 | 8.590 | 9.225 | 100% | TRÊN | 8.909 | 9.029 · TRÊN |
| ↳ A TB / B trung vị / A bỏ VGC (N2) | 9.193 / 7.928 / 6.785 | | | 9.857 / 8.553 / 7.375 | 100% | TRÊN | | |
| NARROW N5 (biên → A trung vị; khoảng peer 8.913–10.933) | 10.418 | 9.217 | 10.256 | 11.623 | 100% | TRÊN | 10.817 | 10.622 · TRÊN |
| Tham chiếu: biên → riêng VGC (gồm KCN), NONE N2 | 18.828 | | | 19.786 | 100% | TRÊN | | |

**Tách chênh WIDE (sửa) → headline (−7.630, −35,0%):** chỉ RONIC = Ke **−1.840**; phần còn lại do ROE/biên về Ke. So với REPORT_r2 22.769: **−37,7%** (trong đó sửa GPM −956).
- ROE ngầm theo cách chuẩn hoá biên của mã (DT TTM 925 tỷ): 2020–TTM 16,0% · 2023–TTM 18,5% · GM-gap **19,1%** (sau sửa; r1 ghi 23,2% là sai) — đều > Ke ⇒ bản "TB của chính mã" chưa chặt, chỉ là cận trên.
- Đối chiếu skeptic: khớp đến đồng ở WIDE 21.813 (P90 26.672), RONIC 19.973, own-cycle 17.705 (P90 19.595), NONE-peer 8.580, NARROW 10.418, N0 12.986. **Lệch** ở ROE→Ke N2 14.183 vs 14.333 (P10 khớp 13.487; P90 14.761 vs 15.062) và N5 15.117 vs 15.384 — phần vượt E-đích của tôi = skeptic ÷1,125 ở cả N2 lẫn N5 ⇒ khác quy ước chiết khấu/trọng số fade (tôi giữ quy ước r1 mà skeptic đã tái lập đúng ở 8.580). Chênh ≤1,8%, **không ảnh hưởng nhãn**; Mike chốt quy ước.

## 5. Thay đổi so với báo cáo hiện hành
**Có đổi giá trị, KHÔNG đổi nhãn:** TRÊN vùng (>P90) ở MỌI phương án, mọi peer set, cả cỡ 5 tỷ lẫn sleeve 10–40 triệu, cả CUM lẫn TERP. Không sát ranh giới: P90 cao nhất (lõi sửa) **26.672** < giá ~30.000 (kể cả lõi gốc 27.119).

| | Tâm | P10 | P50 | P90 |
|---|---|---|---|---|
| REPORT_r2 | 22.769 | 17.348 | 23.312 | 27.119 |
| REPORT_r2 nếu sửa GPM (WIDE lõi sửa) — *việc của REPORT_r2, chờ Mike* | 21.813 (−4,2%) | 17.348 | 21.445 | 26.672 |
| Lõi r3 riêng (trước CK, `model_r3_out.txt` vs `model_r3_5Ffix_out.txt`) | cum 23.933 → 22.932 · post 22.403 → 21.536 | | | |
| **Headline NONE ROE→Ke N2** | **14.183 (−37,7% vs r2; −35,0% vs WIDE sửa)** | 13.487 | 14.124 | 14.761 |
| Hai cận: biên peer N2 / biên TB của mã | 8.580 / 17.705 | 7.891 / 15.495 | | 9.225 / 19.595 |

- Khoảng NONE hợp lý: **~13–15 nghìn** (N0–N5); 8.580 và 17.705 là hai cận. r1 ghi headline 8.730 (−61,7%) — **rút lại**: neo đó mâu thuẫn định nghĩa NONE (§3b).
- Không ghi `dd_price_zones`, không sửa REPORT_r2/SUMMARY.json/`scl_r3_core.py`. Không đụng candidate/plan/lệnh.

## 6. Đề xuất dòng `data/moat_tags.csv` (chỉ đề xuất, không ghi)
`SCL,NONE,NONE,L,"ROIC5Y 8.4% / ROIC10Y 5.6% < Ke 13.5% (ROIC_Min5Y -1.2% suspect artifact, unverified); ROIC5Y < Ke despite TTM ROIC ~16% (est.) at peak margin; TTM ROE 24% = peak year, 2020-25 avg ROE ~13.8% = Ke; GPM 63%->32% (2020->2024), recovered to 39% TTM, ~2.4x domestic peer median 16%; AAC fragmented, tuynel not banned; fly-ash via ~3y power-plant auctions (re-auction clock, far shorter than concessions/licences behind GMD/BWE/HTI/NTC NARROW); 58.5% trade AR one RE group",2026-11-07,5f,N`

## 7. Cần kiểm chứng
- HĐ tro/thạch cao của SCL (nhà máy, giá, thời hạn); lộ trình nhiệt điện Phả Lại.
- `ROIC_Min5Y` −1,2% và `ROIC_Trailing` 1,21 (định nghĩa/artifact BQ).
- ROIC TTM ~15,7% (IC ~855 tỷ): đối chiếu BCTC (tiền mặt, nợ thuê TC).
- DT theo mảng; thị phần AAC theo vùng; tỷ trọng Vingroup; peer AAC trực tiếp (chưa niêm yết).
- Quy ước fade ROE→Ke (lệch ≤1,8% với skeptic, §4).
