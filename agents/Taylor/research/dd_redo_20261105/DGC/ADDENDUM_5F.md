> **QUY ƯỚC CUỐI (user chốt 08/11/2026 10:50 ICT):** KHÔNG áp luật 3c chặt. Moat chỉ được THÊM vào định giá khi bền; NARROW/NONE = không thưởng nhưng KHÔNG trừ. **Headline = mô hình cơ sở hiện hành (tâm 44.767 theo báo cáo gốc)**; mọi 'bản chặt-3c / headline mới / chờ duyệt' bên dưới chỉ còn là **độ nhạy rủi ro** ('nếu về trung bình ngành'), KHÔNG phải kết luận định giá. Các sửa lỗi dữ liệu/công thức/peer trong tài liệu này vẫn có hiệu lực. Không mã nào trong 20 mã có moat bền ⇒ không thêm tham số moat.

# DGC — ADDENDUM bước 3c: 5F tầng (b) + moat trong mô hình (07/11/2026, r3 job `Taylor_20261107_124453`; r2 = `ADDENDUM_5F_r2.md`)

Bổ sung cho `REPORT_r2.md` (05/11). Mọi phần khác của REPORT_r2 giữ nguyên (dẫn nguồn đó). **Mô hình hiện hành LỆCH luật 3c** (RONIC 20% > Ke + biên riêng DGC giữ vĩnh viễn) ⇒ báo các bản chặt song song; số hiện hành không bị sửa. Số: `calc_5f/moat_sens_5f_out.json` (`$DNA_PYEXE -B moat_sens_5f.py`, chạy 2 lần trùng md5 `069c58de…` txt / `b7eb8dac…` json; chân đối chứng assert = pin r2 44.767 / 32.518 / 57.101; `calc/` không bị ghi). GPM/EBITM: `calc_5f/ttm.py` → `ttm_out.txt` (md5 `6e62c0f3…`, 2 lần trùng; BQ `ticker_financial`, `calc_5f/ttm_bq.csv`). ROIC nhiều cửa sổ: `calc_5f/dgc_roic_bq.csv`.

**Sửa r3:** (1) GPM_P0/EBITM_P0 trong BQ là **TTM** (đính chính Mike 07/11 19:50) ⇒ dùng thẳng dòng Q4 mỗi năm; hoàn lại cách tính r2 (Σ GPM_Pi×DT_i — sai, là trung bình của TTM chồng lấn). (2) Thêm bản **CAP MỘT CHIỀU** min(riêng, ngành). (3) ROIC_Min10Y/ROIC5Y 2016–20 gắn "cần kiểm chứng". (4) Khai trường dừng bỏ khỏi căn cứ đồng hồ (đã nằm trong trục quặng 0,5). (5) Dòng moat_tags giữ entry=M.

## 1. Vị thế & lợi thế cạnh tranh (5F)
**Tái dùng** tag `data/moat_tags.csv` dòng DGC: **NARROW · COST/LOCATION**, asof **2026-06-05**, src `5f_validated_compet` (5 tháng < 12 tháng ⇒ không làm lại, luật tần suất 06/11). Không có audit 5F khác trong `kb/projects/dgc-dd-*.md`. Dưới đây là kiểm nhanh bằng số đang có.

**Loại hình DN:** nhà sản xuất hoá chất hàng hoá (P4 vàng, H3PO4, phân bón), xuất khẩu, **chấp nhận giá** P4 thế giới (TQ định giá); lợi thế ở phía CHI PHÍ (quặng apatit tự khai + quy mô).

**GPM/EBITM:** BQ `GPM_P0`/`EBITM_P0` = **TTM** (4 quý trượt); `Revenue_P0` = quý. Năm = dòng Q4 của GPM_P0 (2026 = dòng 2026Q3, TTM Q4/25–Q3/26). Biên QUÝ thật lấy từ BCTC.

| Lực | Đánh giá (số + nguồn) |
|---|---|
| Cạnh tranh trong ngành | P4/H3PO4 hàng đồng nhất, giá theo TQ. "56% công suất P4 quốc gia" chỉ có trong tag 06/2026 ⇒ **cần kiểm chứng**; đối thủ P4 thật (Vân Nam/Quý Châu) **không có dữ liệu biên trong BQ**. Mạnh. |
| Người mua | Xuất khẩu nhiều thị trường; **tập trung khách hàng: cần kiểm chứng** (REPORT §4 không có số). |
| Đầu vào | Lợi thế chính = quặng tự chủ. **GPM TTM (dòng Q4) TB 2017–25: DGC 30,65% vs trung vị 4 peer 19,17%** (TB peer 19,85%) ⇒ gap TB **+11,5pp, DGC > peer 8/9 năm** (2017 −9,6pp; 2021–25 +13,6…+29,7pp). EBITM TTM gap TB +15,1pp, 8/9 năm. GPM **TTM 33,4% (Q3/25) → 21,9% (Q3/26)**; biên **quý** thật **31,1% → 20,5%** (BCTC, theo Mike 07/11) ≈ mức ngành. |
| Gia nhập mới | Rào cản = mỏ apatit + vốn + công nghệ P4 (điện lớn). Giấy phép/thời hạn mỏ: **cần kiểm chứng**. |
| Sản phẩm thay thế | P4 nhiệt điện vs axit ướt cho một số ứng dụng; độ thay thế **cần kiểm chứng**. |
| **Lực thứ 6 (đồng hồ cắt hào)** | (a) trữ lượng Field-25 / tuổi mỏ — **cần kiểm chứng** số năm (tag 06/2026); (b) hạn ngạch xuất P4 của TQ = gió thuận ngoại sinh, đảo được. *Khai trường 25 dừng (REPORT_r2 §5) KHÔNG tính ở đây*: đã vào mô hình qua trục quặng [UL] 0,5 — tính thêm làm đồng hồ là đếm hai lần. |

**Peer:** CSV/DDV/LAS/HVT = hoá chất cơ bản/phân lân **nội địa**, KHÔNG phải đối thủ P4 trực tiếp. Loại PAT (công ty con, đã hợp nhất). VAF (GPM TTM 2017 53,5% bất thường), BFC/SFG (NPK phối trộn, biên thấp), DPM/DCM (urê khí) chỉ ở bản nhạy; CSV một mình là cận trên.

**Lợi nhuận siêu ngạch qua chu kỳ (Ke 13,5%), CẢ HAI phía:** thuận — ROIC_Min5Y **17,7%** (2025/26), ROIC10Y **21,4%**, ROIC5Y 29,4%, ROIC_Trailing ≥ **22,8%** mọi quý Q4 từ 2015 (89–93% Q4 2018–20). Ngược — ROIC_Min10Y **4,4%**, ROIC_Min5Y 4,4% 2016–20, ROIC5Y **10,8–13,4% < Ke ở 2018–20** ⇒ **cần kiểm chứng**: các số này mâu thuẫn ROIC_Trailing cùng kỳ và cửa sổ của chúng phủ đoạn DT quý **gãy 2017Q4–2018Q2 (276/164/126 tỷ/quý** vs ~950 trước, ~1.500 sau; `dgc_roic_bq.csv`) — nghi lỗi dữ liệu/hợp nhất, chưa dùng làm bằng chứng phản bác. ROE (riêng, không thay ROIC): ROE_Trailing ≥ 17,1%/năm 2014–25, ROE_Min5Y 17,4–23,9%, ROE TTM 2026Q3 **13,4%** < Ke.

**Kết luận:** **moat_tier NARROW · moat_type COST/LOCATION (giữ tag 06/2026).** **Rủi ro số 1:** nguồn quặng tự chủ (tuổi mỏ chưa kiểm chứng; khai trường 25 đang dừng — đã mô hình hoá qua trục quặng) — chính là cơ chế hào. Kiểm nhanh từ 06/2026: biên quý về ngang ngành khi dùng quặng mua ngoài; tier không đổi.

## 2. Moat trong mô hình
Ba điều kiện bền: (i) **CHƯA KIỂM CHỨNG** — chuỗi thuận (ROIC_Min5Y 17,7%, ROIC_Trailing) vs chuỗi ngược nghi lỗi (ROIC_Min10Y 4,4%, ROIC5Y 2018–20); (ii) **ĐẠT** — cơ chế: quặng apatit tự khai + P4 quy mô; (iii) **chưa loại trừ** — tuổi mỏ chưa kiểm chứng. ⇒ **moat_durable = false, căn cứ = (i) chưa kiểm chứng + trữ lượng chưa kiểm chứng** (không dùng khai trường dừng) ⇒ luật 3c: RONIC = Ke VÀ biên về TB chu kỳ NGÀNH.

**Mô hình hiện hành (`calc/model_r2.py` + `model.py`) KHÔNG nhất quán 3c, 2 kênh thưởng moat:** (1) RONIC 20% > Ke trong terminal VÀ trong 2027–28 (`moat_sens_5f.py:31-32`, reinv = 1 − g/20%); (2) biên terminal riêng: nhánh dừng GPM 15,0/17,5/19,0%, nhánh mở lại 27,2–28,2% (> ngành ~8–9pp).

**Hai cách áp "biên → ngành" (quy ước CHỜ Mike/user duyệt):**
- **Đối xứng** (r2): GPM_term = ngành mọi nhánh ⇒ NÂNG nhánh dừng (EBIT terminal kịch bản xấu **713 → 1.055 tỷ**, +48%; với trung vị r2 19,47% là 1.080, +51%) = **thưởng cho kịch bản mất hào** — không chặt.
- **CAP một chiều**: EBIT_term = min(riêng, ngành) — chỉ hạ nhánh trên ngành, nhánh dừng giữ nguyên. Thêm biến thể 2027–28 tái đầu tư theo Ke.
Quy ước năm chiết khấu giữ như model_r2 (Q4 0,125; 2027 0,75; 2028 1,75; TV 2,25 từ 30/09/26). Không đếm hai lần: base không có trục pháp lý, không bội số premium; vụ án = WARNING (REPORT_r2 §5).

## 3. Độ nhạy (lưới 810 kết cục, sau CK 5 tỷ 0,71%, giá 33.450 ngày 04/11; ngành = trung vị 4 peer TTM đúng 19,17% trừ khi ghi khác)
| Bản | Tâm | Δ tâm | P10 / P50 / P90 | % dưới giá | Nhãn |
|---|---|---|---|---|---|
| **Hiện hành** (RONIC 20%, biên riêng) | **44.767** | 0 | 32.518 / 44.633 / 57.101 | 12,2% | TRONG |
| WIDE [UL minh hoạ] RONIC 25% | 45.489 | +722 | 32.949 / 45.467 / 58.196 | 11,1% | TRONG |
| chỉ RONIC=Ke (biên giữ) | 43.028 | −1.739 | 31.762 / 42.981 / 54.622 | 14,8% | TRONG |
| chỉ biên → ngành đối xứng (RONIC 20%) | 40.698 | −4.069 | 33.179 / 40.646 / 47.800 | 10,5% | TRONG |
| NARROW½ (RONIC=Ke, nửa gap, đối xứng) | 41.167 | −3.600 | 32.658 / 41.168 / 49.936 | 12,2% | TRONG |
| Đối xứng, RONIC=Ke (r2 = 39.634 @19,47%) | 39.306 | −5.461 | 32.005 / 39.337 / 46.111 | 14,9% | TRONG |
| Đối xứng + 2027–28 theo Ke | 39.008 | −5.759 | 31.749 / 39.075 / 45.756 | 15,7% | TRONG |
| CAP, RONIC=Ke @19,47% (tái lập số Mike) | 38.377 | −6.390 | 30.635 / 38.468 / 46.092 | 20,9% | TRONG |
| CAP, RONIC=Ke @19,17% | 38.213 | −6.554 | 30.574 / 38.280 / 45.700 | 21,7% | TRONG |
| **CAP + 2027–28 theo Ke @19,17%** | **37.916** | **−6.851** | **30.400 / 37.983 / 45.315** | 22,6% | **TRONG** |
| CAP, TB 4 peer 19,85% | 38.588 | −6.179 | 30.727 / 38.678 / 46.458 | 20,4% | TRONG |
| CAP, +VAF 21,12% / +DPM_DCM 20,36% | 39.288 / 38.866 | | P10 30.994 / 30.809 | 18,6% / 19,5% | TRONG |
| CAP, +BFC/SFG 15,56% | 35.242 | −9.525 | 28.326 / 35.442 / 41.434 | 34,5% | TRONG |
| CAP, CSV một mình 27,20% | 42.458 | −2.309 | 31.762 / 42.276 / 54.006 | 15,0% | TRONG |
| Đối xứng: +VAF / +DPM_DCM / +BFC_SFG / CSV | 41.456 / 40.611 / 35.323 / 48.157 | | P10 33.855 / 33.103 / 28.361 / 39.669 | | DƯỚI / TRONG / TRONG / DƯỚI |

- **Tách kênh:** RONIC −1.739; biên đối xứng −4.069; bản đối xứng nâng P10 (nhánh dừng được nâng), bản CAP hạ P10 ~1,6k vì không nâng.
- **Nhãn:** mọi bản CAP = **TRONG**, P10 thấp hơn giá 5–15% (lõi 19,17%: −9,1%) ⇒ không sát ranh giới DƯỚI. Chỉ bản đối xứng với peer rộng (+VAF, CSV) ra DƯỚI — chính là kênh thưởng kịch bản mất hào ⇒ không dùng.
- **Cỡ sleeve 10/20/40 triệu:** CAP+Ke tâm 38.176/38.171/38.163, P10 30.609/30.605/30.599 — TRONG; đối xứng 39.575–39.562 — TRONG; hiện hành 45.074–45.059 — TRONG.
- WIDE không có cơ sở ((i) chưa kiểm chứng) — chỉ minh hoạ: RONIC 20%→25% thêm +1,6%.

## 4. Thay đổi so với báo cáo hiện hành
Số hiện hành **không bị sửa** (REPORT_r2/SUMMARY giữ nguyên, không ghi `dd_price_zones`). Mô hình hiện hành ngầm thưởng moat bền (RONIC 20% kể cả 2027–28 + biên mở-lại ~28% vĩnh viễn) trong khi tag NARROW/không bền ⇒ theo luật 3c, **headline = KHOẢNG tâm ~37.900–39.300** (CAP + 2027–28 Ke 37.916 … đối xứng 39.306; r2 ghi 39.634 là do trung vị peer tính sai phương pháp), P10 30.400–32.005, P90 45.315–46.111, % dưới giá 22,6%–14,9%; **nhãn TRONG → TRONG** (giá giữa P10 và P50, không sát ranh giới). Đầu dưới (CAP) là bản chặt đúng chữ; Δ so hiện hành −6.851 (−15,3%) … −5.461 (−12,2%). **Quy ước chờ Mike/user duyệt.** moat_tier/durable không đổi (căn cứ durable chuyển sang (i)+trữ lượng). 5F non-PIT ⇒ chỉ DD sống, không backtest. Không đụng candidate/plan/lệnh.

## 5. Đề xuất dòng `data/moat_tags.csv` (KHÔNG tự sửa)
`entry` giữ **M** (không có tin mới về cấu trúc ngành để đổi). `moat_upgrade` giữ **Y**; chỉ đổi **N** nếu Mike coi khai trường 25 dừng (sau asof 06/2026) là cơ sở mới.
```
DGC,NARROW,COST/LOCATION,M,"Commodity P4/H3PO4 price-taker vs China; cost edge from captive apatite (TTM GPM Q4-rows 2017-25 30.65% vs domestic chem peer median 19.17%, above 8/9 yrs); TTM GPM 21.9%; quarterly margin Q3/26 20.5% (BCTC) ~ industry while on purchased ore; ROIC_Min10Y 4.4%/ROIC5Y<Ke 2018-20 conflict ROIC_Trailing (data break 2017Q4-18Q2) -> unverified; reserve life + 56% P4 share unverified => not durable (rule 3c: RONIC=Ke, margin capped at industry); Mine-25 halt modelled via ore axis; legal case = WARNING",2026-11-07,5f_quickcheck_reuse_20260605,Y
```
