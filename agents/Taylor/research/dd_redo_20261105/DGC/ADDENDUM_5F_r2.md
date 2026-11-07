# DGC — ADDENDUM bước 3c: 5F tầng (b) + moat trong mô hình (07/11/2026, job `Taylor_20261107_123131`)

Bổ sung cho `REPORT_r2.md` (05/11). Mọi phần khác của REPORT_r2 giữ nguyên (dẫn nguồn đó). **Mô hình hiện hành LỆCH luật 3c** (RONIC terminal 20% > Ke + biên riêng DGC giữ vĩnh viễn) ⇒ báo **bản chặt-3c song song**; số hiện hành không bị sửa. Số: `calc_5f/moat_sens_5f_out.json` (`$DNA_PYEXE -B moat_sens_5f.py`, 2 lần trùng md5 `b6b83ed1…`; chân đối chứng assert = pin r2 44.767 / 32.518 / 57.101; `calc/` không bị ghi). GPM/EBITM TTM: `calc_5f/ttm.py` → `ttm_out.txt` (BQ `ticker_financial`, `calc_5f/ttm_bq.csv`).

## 1. Vị thế & lợi thế cạnh tranh (5F)
**Tái dùng** tag `data/moat_tags.csv` dòng DGC: **NARROW · COST/LOCATION**, asof **2026-06-05**, src `5f_validated_compet` (5 tháng < 12 tháng ⇒ không làm lại, luật tần suất 06/11). Không có audit 5F nào khác trong `kb/projects/dgc-dd-*.md` (grep moat/5F rỗng). Dưới đây là kiểm nhanh bằng số đang có.

**Loại hình DN:** nhà sản xuất hoá chất hàng hoá (P4 vàng, H3PO4 thực phẩm/kỹ thuật, phân bón), xuất khẩu, **chấp nhận giá** P4 thế giới (Trung Quốc định giá); lợi thế nằm ở phía CHI PHÍ (quặng apatit tự khai thác + quy mô).

**Cách tính GPM/EBITM:** BQ `GPM_Pi`, `EBITM_P0`, `Revenue_Pi` là giá trị MỘT QUÝ ⇒ TTM = Σ(biên quý × DT quý)/Σ DT quý, 4 quý, lấy dòng Q4 (năm 2026 = dòng 2026Q3, TTM Q4/25–Q3/26). Không dùng GPM_P0 làm "biên năm".

| Lực | Đánh giá (số + nguồn) |
|---|---|
| Cạnh tranh trong ngành | P4/H3PO4 là hàng đồng nhất, giá theo TQ. Thị phần **"56% công suất P4 quốc gia"** chỉ có trong tag 06/2026 ⇒ **cần kiểm chứng**; đối thủ P4 thật là nhà sản xuất Vân Nam/Quý Châu — **không có dữ liệu biên trong BQ**. Mạnh. |
| Người mua | Xuất khẩu nhiều thị trường; **tập trung khách hàng: cần kiểm chứng** (REPORT §4 không có số). |
| Đầu vào | Lợi thế chính = quặng tự chủ. **GPM TTM TB 2017–25: DGC 28,95% vs TB chu kỳ ngành 19,47% (trung vị CSV/DDV/LAS/HVT) / 19,62% (TB)** ⇒ gap TB +9,48pp, DGC > peer **7/9 năm** (2017 −11,4pp, 2018 −1,6pp; 2021–25 +14,5…+22,1pp). EBITM TTM gap TB +13,72pp, 8/9 năm. Khi khai trường 25 dừng (dùng quặng mua ngoài) GPM quý rơi **33,4% (Q3/25) → 21,9% (Q3/26)** ≈ mức ngành ⇒ biên vượt ngành gắn với quặng tự chủ. |
| Gia nhập mới | Rào cản = mỏ apatit + vốn + công nghệ P4 (điện lớn). Giấy phép/thời hạn mỏ: **cần kiểm chứng**. |
| Sản phẩm thay thế | P4 nhiệt điện vs axit ướt (wet-process) cho một số ứng dụng; độ thay thế **cần kiểm chứng**. |
| **Lực thứ 6 (đồng hồ cắt hào)** | (a) **Khai trường 25 đã DỪNG** phục vụ điều tra (REPORT_r2 §5) — nguồn hào đang bị cắt *thực tế*, mở lại là trục [UL] 0,5; (b) cạn trữ lượng Field-25 (tag 06/2026, **cần kiểm chứng** số năm); (c) hạn ngạch xuất P4 của TQ là gió thuận ngoại sinh, đảo được. |

**Peer:** CSV/DDV/LAS/HVT = hoá chất cơ bản/phân lân **nội địa**, KHÔNG phải đối thủ P4 trực tiếp. Loại PAT (công ty con, đã hợp nhất). BFC/SFG (NPK phối trộn, biên thấp), DPM/DCM (urê khí), VAF (lân nung chảy) chỉ đưa vào bản nhạy; CSV một mình là cận trên (biên ~ngang DGC).

**Lợi nhuận siêu ngạch qua chu kỳ (Ke = 13,5%), CẢ HAI phía:** thuận — ROIC_Min5Y **17,7%** (2025/26), ROIC10Y **21,4%**, ROIC5Y 29,4%; ngược — **ROIC_Min10Y 4,4%**, ROIC_Min5Y **4,4% suốt 2016–20**, **ROIC5Y 10,8–13,4% < Ke ở 2018–20**. ROE (riêng, không thay ROIC): ROE_Trailing ≥17,1%/năm 2014–25, ROE_Min5Y 17,4–23,9% (bị đẩy bởi ~9,8 nghìn tỷ tiền gửi), ROE TTM 2026Q3 **13,4%** < Ke. ⇒ siêu ngạch chỉ chắc chắn trong cửa sổ 2021–25 (chu kỳ P4); cửa sổ 2016–20 trượt.

**Kết luận:** **moat_tier NARROW · moat_type COST/LOCATION (giữ tag 06/2026).** **Rủi ro số 1:** nguồn quặng tự chủ (khai trường 25 dừng/không mở lại) — chính là cơ chế hào. **Kiểm nhanh đổi hào từ 06/2026:** hào hẹp đi (khai trường dừng → GPM quý về ngang ngành); tier không đổi.

## 2. Moat trong mô hình
Ba điều kiện bền: (i) **TRƯỢT một phần** (ROIC5Y < Ke 2018–20, ROIC_Min10Y 4,4%); (ii) **ĐẠT** — cơ chế gọi tên được: quặng apatit tự khai + P4 quy mô; (iii) **TRƯỢT** — khai trường dừng, trữ lượng chưa kiểm chứng ⇒ **moat_durable = false ⇒ luật 3c: RONIC = Ke VÀ biên về TB chu kỳ NGÀNH.**

**Kiểm mô hình hiện hành (`calc/model_r2.py` + `model.py`) — KHÔNG nhất quán 3c, có 2 kênh thưởng moat:**
1. **RONIC = 20% > Ke 13,5%** trong terminal (reinv = 1 − g/RONIC = 85% giữ lại ⇒ 15% tái đầu tư; với RONIC=Ke phải giữ lại 22,2%). Ghi chú trong code: "NOPAT/vốn hoạt động ~40%, dùng mức thận trọng" — đây là thưởng moat không qua 3 điều kiện.
2. **Biên terminal riêng DGC giữ vĩnh viễn:** GPM terminal nhánh dừng 15,0/17,5/19,0% (kịch bản) — *dưới* ngành 19,5%; nhánh mở lại +1.000 tỷ LN gộp ⇒ **27,2–28,2%** — *trên* ngành ~8,5pp. Bình quân trọng số mô hình ≈ trên ngành.

**Bản chặt-3c (quy ước CHỜ Mike/user duyệt):** RONIC terminal = Ke; GPM terminal = TB chu kỳ ngành **áp ĐỐI XỨNG mọi nhánh** (nhánh dừng được NÂNG lên 19,5%, nhánh mở lại bị HẠ xuống); EBIT_term = (GPM_ngành × DT 2028 kịch bản − opex 520 tỷ) × m. 2027–28 tường minh giữ nguyên (kể cả reinv cũ); quy ước năm chiết khấu giữ như model_r2 (Q4 0,125; 2027 0,75; 2028 1,75; TV 2,25 từ 30/09/26). Không đếm hai lần: mô hình không có trục pháp lý trong base, không có bội số premium; vụ án không dùng để ép biên (WARNING giữ như REPORT_r2 §5).

## 3. Độ nhạy (lưới 810 kết cục, sau CK 5 tỷ 0,71%, giá 33.450 ngày 04/11)
| Bản | Tâm | Δ tâm | P10 / P50 / P90 | % dưới giá | Nhãn |
|---|---|---|---|---|---|
| **Hiện hành** (RONIC 20%, biên riêng) | **44.767** | 0 | 32.518 / 44.633 / 57.101 | 12,2% | TRONG |
| WIDE [UL minh hoạ] RONIC 25% | 45.489 | +722 (+1,6%) | 32.949 / 45.467 / 58.196 | 11,1% | TRONG |
| chỉ RONIC=Ke (biên giữ) | 43.028 | −1.739 (−3,9%) | 31.762 / 42.981 / 54.622 | 14,8% | TRONG |
| chỉ biên → ngành (RONIC 20%) | 41.057 | −3.710 (−8,3%) | 33.509 / 41.046 / 48.196 | 9,6% | DƯỚI (ranh giới: P10 +0,2% trên giá) |
| NARROW½ (RONIC=Ke, nửa gap biên) | 41.331 | −3.436 (−7,7%) | 32.783 / 41.335 / 50.141 | 11,7% | TRONG |
| **Chặt-3c / NONE** (trung vị 4 peer 19,47%) | **39.634** | **−5.133 (−11,5%)** | **32.277 / 39.631 / 46.514** | 13,6% | **TRONG (sát P10, giá +3,6%)** |
| Chặt-3c, TB 4 peer 19,62% | 39.795 | −4.972 | 32.411 / 39.767 / 46.700 | 13,1% | TRONG |
| Chặt-3c, +VAF (20,90%) | 41.208 | −3.559 | 33.644 / 41.184 / 48.323 | 9,2% | DƯỚI (ranh giới, P10 +0,6%) |
| Chặt-3c, +DPM/DCM (20,99%) | 41.309 | −3.458 | 33.735 / 41.294 / 48.438 | 8,8% | DƯỚI (ranh giới, P10 +0,9%) |
| Chặt-3c, +BFC/SFG (15,60%) | 35.368 | −9.399 | 28.397 / 35.619 / 41.486 | 32,8% | TRONG |
| Chặt-3c, CSV một mình (27,41%) | 48.386 | +3.619 | 39.859 / 48.231 / 57.086 | 0,6% | DƯỚI |

- **Tách kênh:** RONIC −1.739; biên −3.710 (riêng); gộp −5.133. Bản chỉ-biên làm P10 TĂNG vì fade đối xứng nâng nhánh dừng và co phân phối (P90 −8,9k).
- **Khoảng theo cách chọn peer (chặt-3c):** 35.368 … 41.309 nếu loại cận CSV-một-mình (48.386). Nhãn **TRONG với peer lõi, DƯỚI-ranh-giới với peer rộng** (P10 lệch giá <1%) ⇒ ghi **ranh giới TRONG/DƯỚI**, không khẳng định đổi nhãn.
- **Cỡ sleeve thật 10/20/40 triệu** (CK 0,03–0,06%): chặt-3c tâm 39.905/39.900/39.893, P10 32.498/32.494/32.488 ⇒ vẫn TRONG; hiện hành 45.074–45.059, TRONG.
- WIDE không có cơ sở (iii trượt) — chỉ minh hoạ hiện hành đã gần mức "WIDE": RONIC 20%→25% chỉ thêm +1,6%.

## 4. Thay đổi so với báo cáo hiện hành
Số hiện hành **không bị sửa** (REPORT_r2/SUMMARY giữ nguyên, không ghi `dd_price_zones`). Nhưng mô hình hiện hành ngầm thưởng moat bền (RONIC 20% + biên mở-lại ~28% vĩnh viễn) trong khi tag NARROW/không bền ⇒ **theo luật 3c đúng chữ, headline là chặt-3c: tâm 44.767 → 39.634 (−11,5%), P10 32.518 → 32.277, P50 44.633 → 39.631, P90 57.101 → 46.514; nhãn TRONG → TRONG (sát P10; ranh giới DƯỚI theo peer)**, % dưới giá 12,2% → 13,6%. Phần chênh: ~1/3 RONIC, ~2/3 biên (chủ yếu hạ nhánh mở lại khai trường). **Quy ước chờ Mike/user duyệt.** 5F non-PIT ⇒ chỉ DD sống, không backtest. Không đụng candidate/plan/lệnh.

## 5. Đề xuất dòng `data/moat_tags.csv` (KHÔNG tự sửa)
`entry` = độ hấp dẫn cấu trúc NGÀNH (moat_5f.py:33): hoá chất hàng hoá, price-taker theo TQ ⇒ **L** (dòng 06/2026 để M). `moat_upgrade`: dòng 06/2026 là Y; moat không bền ⇒ đề xuất **N** (có chủ ý, Mike xác nhận).
```
DGC,NARROW,COST/LOCATION,L,"Commodity P4/H3PO4 price-taker vs China; cost edge from captive apatite (GPM TTM 2017-25 28.95% vs domestic chem peer median 19.47%, above 7/9 yrs) but ROIC5Y<Ke 2018-20, ROIC_Min10Y 4.4%; Mine-25 halted (investigation) -> Q3-26 quarterly GPM 21.9% ~ industry => moat clock running, not durable (rule 3c: RONIC=Ke, margin to industry mean); 56% P4 share + reserve life unverified; legal case = WARNING",2026-11-07,5f_quickcheck_reuse_20260605,N
```
