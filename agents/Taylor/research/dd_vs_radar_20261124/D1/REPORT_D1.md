# D1 — Phương pháp DD có thiên lệch hệ thống về phía "đắt" không?

Job `Taylor_20261123_170315` · 24/11/2026 · Chỉ là nghiên cứu/chẩn đoán: KHÔNG wire, KHÔNG đổi quy tắc DD, KHÔNG đặt lệnh.
Mọi số trong báo cáo đo trong phiên này. File nguồn ở `calc/`, md5 khoá ở `calc/MD5SUMS.txt`. Chạy `proxy.py` 2 lần (threads=1), md5 gộp của output trùng nhau: `340c0621…`.

## Kết luận (đọc phần này trước)

**Có thiên lệch, nhưng là thiên lệch MỨC do thước đo, chứ không phải thị trường đang đắt.**

Proxy cơ học áp đúng quy ước DD (r 13,5% gắn lãi huy động, terminal RONIC=Ke, không NPV>0) và chưa trừ haircut nào. Qua 10 năm, cổ phiếu thanh khoản điển hình luôn giao dịch ở **giá/proxy-tâm trung vị 1,38**, dải p10–p90 là 1,11–1,73. Hôm nay con số này là **1,28, ở phân vị 35%**. Nghĩa là theo chính thước của DD, thị trường hôm nay **rẻ hơn mức thường lệ**, không đắt.

Vậy câu "giá/tâm 1,085, chỉ 19% đạt luật 4" chủ yếu phản ánh ba thứ:
- Thước DD **luôn** đặt giá trị dưới giá. Theo proxy, tỷ lệ mã đạt ≤0,85×tâm có trung vị lịch sử 25,6%, hôm nay 28,6%.
- DD còn trừ thêm một chuỗi mô-đun **một chiều**.
- Phần còn lại là trường hợp riêng từng mã.

| Giả thuyết | Hướng | Độ lớn (đo) | Tin cậy |
|---|---|---|---|
| G1 chọn mẫu | **Ngược chiều giả thuyết.** Đo bằng cùng một thước, mẫu DD RẺ hơn thị trường | proxy giá/tâm: DD 0,70 so với 80 mã ngẫu nhiên PIT 1,28 (MWU p<0,001). Theo giá ref/tâm DD: nhóm LAG 1,44 (n=7), nhóm user yêu cầu 1,36 (n=3), nhóm fear-buy 0,96 (n=9) | trung bình (nhãn G1 phần lớn conf=low) |
| G2 mô-đun haircut | **Thật, nghiêng xuống.** 7 họ mô-đun chỉ giảm. Upside chỉ nằm ở độ nhạy | chuỗi trung vị −11,5% (N=19 mã); đây là CẬN DƯỚI vì "raw" đã chứa haircut. Tâm DD / proxy thô = 0,71 (N=35) | trung bình |
| G3 mức lịch sử | **Hôm nay rẻ hơn lịch sử** | phân vị 35% (r gắn lãi), 23% (r cố định), 19% (fade), P/B 9% | khá (N tháng = 120, 1 mặt cắt/tháng) |
| G3 dự báo | Gợi ý, **không vững** | IC 0,082 NW t=2,97, nhưng IS 2014–19 chỉ 0,025 (t=0,81). Q1−Q5 không chồng lấn t=1,33, p=0,21 (N=12 năm) | thấp |
| G4 skeptic | Bất đối xứng ở khâu **SINH** phản đối, không ở khâu chấp nhận | too_high 212 so với too_low 72 (2,9×). Tỷ lệ áp vào base: too_high 33% so với too_low 50% | thấp–trung bình (gán tay bởi 1 sub-agent) |
| G5 P/E ngụ ý | **Tâm DD ngụ ý P/E rất thấp** | P/E ngụ ý trung vị 5,75 so với P/E ngành trung vị 10 năm 9,93 (tỷ lệ 0,60; cùng mặt bằng lãi 0,68). 33/36 mã dưới P/E ngành | trung bình (EPS TTM đỉnh chu kỳ kéo P/E ngụ ý xuống) |

**Phân rã "DD đắt":**
- **(i) Chọn mẫu: gần như KHÔNG giải thích được mức.** Mẫu DD thực ra rẻ hơn thị trường theo cùng thước. Chọn mẫu chỉ giải thích **thành phần**: nhóm LAG và nhóm user yêu cầu có giá/tâm 1,36–1,44, còn fear-buy 0,96.
- **(ii) Thiên lệch phương pháp THẬT: phần chính.** Gồm (a) độ lệch mức cấu trúc của quy ước: giá thường lệ ≈1,3–1,4× giá trị kiểu DD, và (b) các mô-đun một chiều trừ thêm 11–29%.
  - r 13,5% nằm trên đầu dải Ke nội địa 12,3–13,4%. Riêng phần này trừ 5–20% tâm (VCB −18,5%, PNJ −19,7%, DCM −5,3%). Ở các mã nhóm B, dùng Ke 12,3% cho tâm cao hơn +5…+16%.
- **(iii) Đúng sự thật: phần nhỏ, theo từng mã.** Thứ nhất, ROE TTM đang ở đỉnh chu kỳ (LLM 48%, VLB 56%, SAS 48%, BSR 33%, TV1 33%), nên DD chuẩn hoá xuống là có cơ sở. Thứ hai, có các khoản riêng có cơ sở dữ liệu: CST với KTPL −58,9% (số kiểm toán), SCL với chia NLĐ (BCTC).

## G1 — Chọn mẫu

**Nguồn chọn của 36 mã** (`calc/g1_provenance.csv`, sub-agent truy từ PROMPT/brief/bus/kb):

| Nhóm | Số mã | Mã |
|---|---|---|
| post_BCTC | 15 | 11/15 conf=low (suy từ mùa BCTC Q3) |
| fear_buy | 9 | |
| LAG_candidate | 7 | 4 high: BSR, CSV, GAS, MSB |
| user_request | 3 | DBC, QTP, TTA |
| held_position | 1 | DRI |
| other | 1 | PAT |

**So với mẫu ngẫu nhiên PIT** (`calc/proxy.py`, `g1_dd_vs_proxy.csv`, `g1_random80.csv`):
- Ngày 2026-11-20, universe_pit (ruleset 1) có 297 mã. Lấy 80 mã ngẫu nhiên, seed 20261124.
- Trung vị proxy giá/tâm: 80 mã ngẫu nhiên **1,280**, toàn universe **1,281**, 35 mã DD có proxy **0,703**. MWU p<0,001. HHS không có proxy vì ROE≈0.
- Theo nhóm, ba chỉ số lần lượt là: giá ref/tâm DD, proxy giá/tâm, tâm DD/proxy.

| Nhóm | n | giá ref/tâm DD | proxy giá/tâm | tâm DD/proxy |
|---|---|---|---|---|
| LAG | 7 | 1,435 | 0,984 | 0,707 |
| user_request | 3 | 1,358 | 0,973 | 0,782 |
| post_BCTC | 14 | 1,078 | 0,767 | 0,750 |
| fear_buy | 9 | 0,955 | 0,560 | 0,587 |
| CONFIRMED | 17 | 0,925 | 0,703 | 0,778 |
| REFUTED_OPEN | 18 | 1,390 | 0,715 | 0,522 |

- **Đọc kết quả:** nhóm REFUTED_OPEN "đắt" (1,39) không phải vì giá các mã này cao hơn theo thước khách quan. Proxy giá/tâm của hai nhóm như nhau (0,72 so với 0,70). Khác biệt nằm ở chỗ tâm REFUTED_OPEN chỉ bằng **0,52× proxy**, so với 0,78× ở CONFIRMED. Tức là các bản dựng lại ngày 23/11 haircut nặng hơn.
- Đây là chẩn đoán mạnh nhất của D1: **đợt dựng lại ngày 23/11 kéo tâm xuống**. Giá không đổi.

## G2 — Bảng thác mô-đun (N=19 mã có chuỗi tách được)

Nguồn: `calc/g2_waterfall_A.csv` (9 mã), `g2_waterfall_B.csv` (10 mã), tổng hợp ở `g2_module_summary.csv` (`g2_aggregate.py`). Bước % tính bằng Δ bước / giá trị trước bước.

| Mô-đun | Số bước | Trung vị % | Khoảng | Xuống / lên | Tỷ lệ [UL] |
|---|---|---|---|---|---|
| r_cost_of_equity (13,5% so với Ke 12,3%) | 3 | −18,5 | −19,7…−5,3 | 3/0 | 100% |
| earnings_fade | 2 | −15,4 | −21,9…−8,8 | 2/0 | 50% |
| KTPL/ESOP/NCI | 5 | −10,2 | −58,9…−0,8 | 5/0 | 0% (số kiểm toán) |
| capex tuân thủ V4 | 4 | −8,7 | −15,2…−2,5 | 4/0 | 50% |
| quản trị | 1 | −7,6 | | 1/0 | 0% |
| trần g_T | 3 | −5,3 | −15,3…−0,4 | 3/0 | 33% |
| CK thanh khoản | 15 | −1,7 | −10…0 | 13/0 | 7% |
| trọng số kịch bản | 12 | −0,5 | −48,8…+9,2 | 7/5 | 100% |
| other | 14 | −0,3 | −31,5…+32,0 | 7/7 | 50% |
| npv0 dự án mới | 1 | +32,6 (HPG) | | 0/1 | 100% |
| CK holding | 1 | +2,6 | | 0/1 | 100% |

- **Mô-đun MỘT CHIỀU** (chỉ giảm theo thiết kế): r (V1 cố định 13,5%), fade/chuẩn hoá, KTPL/NCI, capex tuân thủ, quản trị, trần g_T, CK thanh khoản.
- **Mô-đun hai chiều:** trọng số kịch bản (nhưng 100% [UL]), npv0, khối "other" (APV, khấu hao giữa kỳ, hạn giấy phép…).
- **Có cơ sở dữ liệu độc lập:** KTPL/NCI (BCTC kiểm toán), một phần capex tuân thủ (QCVN), CK thanh khoản (BQ ADV). **Tham số tự đặt [UL]:** r neo 13,5%, trọng số kịch bản, phần lớn fade và trần g_T.
- **Upside "quá thấp" chỉ nằm ở độ nhạy, KHÔNG vào base:** 27 dòng. Ví dụ QTP Cvlp +32,4%, CST rò KTPL +53,5%, BSR tuân thủ=0 +11,4%, MBB RONIC>Ke, MSB g 6% +5,5%.
- **Chuỗi tổng** raw→tâm có trung vị **−11,5%**, khoảng −56,9% (QTP) đến +31,0% (HPG). Đây là **cận dưới** của tổng haircut, vì "raw" của báo cáo đã chứa sẵn chuẩn hoá. Đo bằng proxy thô cho ra tâm DD = 0,71× (G1).
- **Giới hạn:** không mã nào có dòng "trước mọi haircut". 4 mã (HPG, FPT, MBB, TV2) chỉ có cầu nối r2→r3. Một số raw là DERIVED, đã ghi nhãn trong note.

## G3 — Proxy cơ học + kiểm chuẩn lịch sử

**Proxy** (`calc/proxy.py`):
- Residual income trên mỗi đồng sổ sách. ROE_ttm = PB/PE, cả hai trên Price thô nên PIT theo `valuation_pe_pb_pcf_ps.md`. Giữ ROE 5 năm (V5), tái đầu tư 0,5 [UL]. Terminal: RI phẳng (RONIC=Ke, tức không NPV>0).
- r = 13,5% + (lãi huy động hiệu dụng − 7,4%), β=1.
- Universe: `tav2_mike.universe_pit`, cuối mỗi tháng từ 2011 đến 2026-11-20. Lợi suất kỳ sau tính từ Close adj của **mọi** mã, không chỉ trong universe; tỷ lệ thiếu dữ liệu forward 0,2%.

**(a, b) Mức:** trung vị cắt ngang giá/proxy-tâm (`g3_level_monthly.csv`).

| Biến thể | Hôm nay | Trung vị 10Y | p10–p90 10Y | Phân vị hôm nay |
|---|---|---|---|---|
| DD (r gắn lãi) | 1,281 | 1,381 | 1,11–1,73 | 35% |
| r cố định 13,5% | 1,281 | 1,535 | 1,19–2,15 | 23% |
| ROE fade 10 năm | 1,078 | 1,192 | 1,03–1,35 | 19% |
| P/B thô | 1,036 | 1,205 | 1,05–1,43 | 9% |

- Trung vị lịch sử ≈1,3–1,4, nên giá/tâm 1,085 của sổ DD **không** phải mức đắt so với lịch sử. Proxy ở phân vị 35% cao hơn P/B (9%) vì r hôm nay (13,5%) cao hơn r giai đoạn 2020–25 (10,8–11,8%; lãi huy động hiệu dụng 7,4% so với ~5%). Khoảng chênh còn lại là **phần do r**. Điều này khớp với R1: mâu thuẫn radar–DD chủ yếu do thước đo r.

**(c) Dự báo** (`g3_ic_fwd6.csv`, `g3_ic_fwd12.csv`). Mỗi tháng một mặt cắt. Dùng Newey-West lag h−1 và thêm mẫu không chồng lấn.

| | IC −giá/proxy → fwd12 | NW t | Q1−Q5 fwd12 | t không chồng lấn (N) |
|---|---|---|---|---|
| Toàn kỳ 2014–2025 | 0,082 | 2,97 | +10,4% | 1,33 (12), p=0,21 |
| IS 2014–19 | 0,025 | 0,81 | +4,1% | 0,08 (6) |
| OOS 2020+ | 0,141 | 4,46 | +16,9% | 1,54 (6) |
| (đối chứng 1/P/B) | 0,035 | 0,85 | | |

- fwd6 OOS: Q1−Q5 không chồng lấn p=0,014 (N=13). Tuy vậy IS bằng 0 nên tín hiệu **không ổn định theo chế độ**. Theo quy chuẩn (edge phải tồn tại ở cả IS lẫn OOS), kết quả này **chưa đạt**: chỉ là gợi ý, không phải bằng chứng. Proxy vẫn tốt hơn 1/P/B thô.
- **Mức thị trường** so với fwd12 trung vị: Spearman −0,44 trên mẫu không chồng lấn, N=12, p=0,15. Không có ý nghĩa thống kê.
- **Kiểm look-ahead:**
  - PE/PB tính trên Price thô (PIT theo registry); universe_pit là PIT; không dùng cột `profit_*`.
  - **Caveat 1:** chuỗi lãi huy động có 26 mốc neo hồi tố (2026-06-19), không PIT thật cho quá khứ.
  - **Caveat 2:** BVPS/EPS phụ thuộc `OShares` của ticker_financial (TRAP restate). Có vài PB hôm nay nghi lệch do cổ phiếu thưởng, ví dụ PNJ PB 0,52.
  - Không có kiểm định DSR/PBO vì không chọn tham số nào; mọi tham số đều khai trước.

## G4 — Skeptic đối xứng

Nguồn: `calc/g4_skeptic_findings.csv`, `g4_summary.md`. Phạm vi: 73 vòng, 21 mã, N=328 finding. Các finding cùng mã không độc lập, nên số đơn vị gần-độc-lập chỉ khoảng 21.

| Hướng | Số finding | Áp vào base (bỏ vòng cuối) | Chỉ độ nhạy | Bác bỏ | Trung vị độ lớn |
|---|---|---|---|---|---|
| too_high | 212 | 53/160 = 33% | 59 | 27 | 7,3% |
| too_low | 72 | 28/56 = 50% | 21 | 5 | 10,4% |

- Bất đối xứng nằm ở khâu **sinh** phản đối: skeptic nêu chiều đắt nhiều gấp 2,9 lần chiều rẻ. Khâu chấp nhận thì không bất đối xứng.
- Ngoại lệ là các hạng mục khoá bởi luật user (r 13,5%). Phản đối too_low về Ke đều bị bác hoặc chỉ đưa vào độ nhạy (ví dụ MSB r2: "Ke 13,5% nằm ngoài dải nội địa 12,3–13,4%: +1,2..+16%" → 0 ở base).
- Theo số tuyệt đối, phản biện vẫn hạ tâm nhiều hơn nâng: 53 so với 28 lần áp.
- **Giới hạn:** hướng do sub-agent gán tay, sai số ước ±10–15%. Đã spot-check 5 dòng và thấy khớp; chưa kiểm chéo đầy đủ.

## G5 — P/E ngụ ý

Nguồn: `calc/g5_implied_pe.csv`. P/E ngụ ý = tâm / EPS TTM. P/E ngành là trung vị cắt ngang theo ICB 4 số, PE>0, trong universe.
- P/E ngụ ý trung vị **5,75**, so với P/E ngành trung vị 10 năm **9,93**: tỷ lệ 0,60. Nếu chỉ lấy các tháng có r trong ±1pp so với hôm nay (13,5%) thì tỷ lệ là 0,68.
- 33/36 mã có P/E ngụ ý dưới P/E ngành 10 năm. Mức thấp nhất: LLM 1,7, TV1 2,4, QTP 2,3, PNJ 2,2, BSR 3,0.
- Một phần hợp lý vì EPS TTM đang ở đỉnh chu kỳ (DD chuẩn hoá xuống). Dù vậy, mức P/E ~6 trên diện rộng chỉ thấy ở các đáy lịch sử của thị trường VN. Điều này xác nhận **mức tâm DD thấp một cách hệ thống**.

## Đề xuất khắc phục (chỉ ĐỀ XUẤT, KHÔNG áp; xếp theo lợi/chi phí)

**1. (S5 + S1) Hai nhãn hiển thị:** nhãn "nội tại mù giá" giữ nguyên, và thêm nhãn "so với lịch sử".
- Nhãn thứ hai là phân vị của giá/tâm so với phân phối lịch sử giá/proxy-tâm của universe PIT (trung vị 1,38, p25≈1,2 ước lượng, chưa đo).
- Chi phí: thấp (proxy đã có).
- Circularity: không có, vì không chảy vào giá trị nội tại. Look-ahead: phân phối chỉ dùng dữ liệu ≤ ngày DD.
- Cần user quyết: thêm nhãn và quyết luật 4 đọc nhãn nào.
- Cách kiểm: walk-forward IC của nhãn (hiện IS yếu, nên chỉ HIỂN THỊ).

**2. Siết đối xứng skeptic:** brief DD_GENERAL bắt buộc liệt kê số kiểm too_low ngang số kiểm too_high (đòn 8).
- Chi phí: rất thấp. Rủi ro: thấp.
- Cần user quyết: không, chỉ cần Mike duyệt brief.
- Cách kiểm: tỷ lệ sinh too_high/too_low ở 10 DD tới.

**3. (S4) r theo bằng chứng ERP:** đưa r về trong dải Ke 12,3–13,4% khi có ERP ngụ ý từ lịch sử (dữ liệu R1).
- Tác động: +5…+20% tâm.
- Chi phí: trung bình.
- Rủi ro: chỉnh r để tâm "trông hợp lý" là circular. Phải khoá ERP trước, từ dữ liệu ≤ ngày neo.
- Cần user quyết: sửa luật V1 (luật user).
- Cách kiểm: so P/E ngụ ý với P/E ngành cùng mặt bằng lãi.

**4. (S2) Kỳ vọng có trọng số gồm cả upside đã định lượng:** những hạng mục "quá thấp" có cơ sở dữ liệu thì đưa vào kịch bản tăng có xác suất, thay vì chỉ để ở độ nhạy.
- Chi phí: trung bình. Rủi ro: lạc quan hoá; cần skeptic hai chiều.
- Cần user quyết: có.
- Cách kiểm: tâm/proxy của bản mới so với bản cũ, cùng tỷ lệ skeptic REFUTED.

**5. (S3) NPV>0 có điều kiện** cho franchise có ROIC-spread bền, đo PIT ≥5 năm.
- Chi phí: cao. Rủi ro: overfit, và 5F non-PIT.
- Cần user quyết: sửa V4/V5.
- Cách kiểm: backtest spread persistence trên universe_pit.

**Không đề xuất:** dùng giá để chỉnh giá trị nội tại (vi phạm luật mù giá).

## Hạn chế

- Proxy không phải DD đầy đủ: không có kịch bản, KTPL, thanh khoản, và giữ ROE TTM nên lạc quan cho mã ở đỉnh chu kỳ.
- G1, G2 và G4 do sub-agent (Sonnet) trích và gán; độ tin ghi theo từng file.
- Giá ref trong sổ là giá cũ (06–23/11). Bảng dùng cả giá ref lẫn giá ngày 2026-11-20.
- quant-skeptic CHƯA chạy trên D1.
