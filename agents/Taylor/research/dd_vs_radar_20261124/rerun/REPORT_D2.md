# D2 — chạy lại D1 cho NHẤT QUÁN (theo QUANT_SKEPTIC_D1)

Job `Taylor_20261123_174703` · 24/11/2026 · mặt cắt 2026-11-20 · NGHIÊN CỨU/CHẨN ĐOÁN — không đổi sổ DD/radar/skill/luật (mù giá, V1/V4/NPV0), không wire, không email.
Script `rerun/D2/proxy_d2.py` (import hàm `vbv_dd`/`vbv_fade` của D1, không sửa file D1, không ghi gì vào D1) + `rerun/D2/g2_labels_d2.py`. Số đọc từ `D2/out/d2_results.json` và các CSV cùng thư mục.
Chạy 2 lần, threads=1: md5 output trùng (`D2/OUTPUTS.md5`). Đầu vào khoá ở `rerun/INPUTS.md5`. Parity với D1 (cơ sở lãi cũ, ROE TTM): giá/proxy hôm nay 1,281 · trung vị 10Y 1,381 · p35 · DD/proxy 0,707 · REFUTED_OPEN vs CONFIRMED p=0,058. **Tái lập từng chữ số.**

## Số cũ → số mới nhất quán

| Mục | D1 (cũ) | D2 (nhất quán) | Ghi chú |
|---|---|---|---|
| Cơ sở lãi huy động | effective (CCTG từ 2026-09-30, neo 7,4) | **Big-4 12M thuần**, neo r 13,5% tại 6,8% | backfill CCTG hằng chênh ≡ Big-4 thuần (R2 §3) |
| G3 phân vị hôm nay, biến thể DD (ROE TTM giữ 5Y) | p35 (trung vị 10Y 1,381) | **p22,5** (trung vị 10Y 1,451) | skeptic: 35→23 ✓ |
| G3 phân vị hôm nay, mọi cơ sở ROE × [fade, hold] | p19–35 | **p13–75** | ROE TB5Y theo mã: p13–35 · khử đỉnh đồng loạt: p31–75 |
| Tâm DD / proxy | **0,71** (một số) | dải [fade, hold]: ROE TTM **0,71–0,92** · ROE TB5Y theo mã **0,85–0,95** · khử đỉnh **0,95–1,03** · ÷1,584 **1,16–1,28** | bao: 0,71–1,28 |
| "Haircut DD 29%, −11,5% chỉ là cận dưới" | khẳng định | **bỏ**. Với ROE chuẩn hoá theo mã, tâm DD thấp hơn proxy 5–15%, cùng cỡ chuỗi −11,5% (N=19) | |
| G1 DD vs ngẫu nhiên (proxy, ROE TTM) | 0,70 vs 1,28, p<0,001 | mẫu ngẫu nhiên **loại 33 mã DD**: 0,70 vs 1,54 (hold) · 0,85 vs 1,10 (fade, p=0,016) · ROE TB5Y: 0,92 vs 1,11 (p=0,054) / 1,07 vs 1,09 (**p=0,72**) | "DD rẻ hơn thị trường" **không bền** khi chuẩn hoá ROE |
| G1 so P/B | — | DD 1,18 vs ngẫu nhiên 1,06, **p=0,61** | không khác |
| G1 mẫu DD là gì | "chọn mẫu không giải thích mức" | **P/E 5,98 vs 11,06; ROE TTM 19,8% vs 10,5%** ⇒ mẫu DD = nhóm lãi đỉnh/P/E thấp | câu D1 (i) bỏ |
| REFUTED_OPEN vs CONFIRMED (tâm/proxy) | 0,52 vs 0,78, "chẩn đoán mạnh nhất" | 0,52 vs 0,78, **p=0,058** (không ý nghĩa ở 5%) | bỏ "mạnh nhất" |
| — phản thực tâm rev1 | — | **0,615 vs 0,855** (p=0,35). Khoảng cách đã có sẵn ở rev1: **82%** (ROE TTM), **40–82%** qua các cơ sở | skeptic: 0,615 vs 0,812 (định nghĩa rev1 khác, xem G1) |
| — đổi tâm rev1→cuối | — | REFUTED_OPEN **−8,2%**, CONFIRMED **−4,2%** (trung vị) | skeptic −8,8/−2,9 |
| — giá ref/tâm | 1,39 vs 0,93 | cuối 1,36 vs 0,92 · **rev1 1,06 vs 1,03** | khoảng cách giá/tâm do đợt dựng lại tạo ra |
| G2 nhãn r | "một chiều" | **two_way** (19/19 dòng r trong CSV) | 3/3 bước quan sát đi xuống vì neo 13,5% > dải Ke 12,3–13,4%: đó là trạng thái hiện tại, không phải thiết kế |
| G5 P/E ngụ ý ÷ ngành 10Y | 0,60 ⇒ "xác nhận tâm DD thấp hệ thống" | P/E ngụ ý ÷ **P/E thị trường của chính mã = 0,95** (53% mã dưới 1). Bản thân P/E thị trường của các mã này ÷ ngành = 0,63 | **bỏ câu "xác nhận tâm DD thấp hệ thống"** |
| G5 P/E ngụ ý trên EPS chuẩn hoá | — | TB5Y theo mã **7,22** (thị trường cùng cơ sở 7,21) · khử đỉnh 7,14 · ÷1,584 **9,10** (vs ngành 10Y 10,08: 0,71–0,90) | |
| Nhãn "so với lịch sử" cho DD | giá/proxy, trung vị 1,38 | **thước DD-tương-đương** = giá/(k×proxy). Trung vị 10Y **1,13–2,05**; sổ DD 1,085 ở **p0–33** | xem §6; chỉ đề xuất |

## Kết luận (đã sửa, KHÔNG thêm kết luận mới)

1. **Thị trường hôm nay rẻ hơn lịch sử theo thước DD: chỉ ĐỨNG một phần.**
   - Đứng khi ROE giữ TTM (p16–23) hoặc chuẩn hoá theo từng mã (ROE TB5Y: p13–35).
   - **Đổi chiều** khi khử đỉnh lợi nhuận đồng loạt theo hệ số rổ radar rồi giữ 5 năm (p73–75).
   - Hệ số rổ bị Vingroup/BSR chi phối (R2: trung vị theo mã chỉ 1,36), nên biến thể đồng loạt có khả năng quá tay với nhóm vốn hoá vừa. Dù vậy, hướng "rẻ" **không bền mọi giả định**.
2. **Tâm DD so với proxy cơ học phụ thuộc hoàn toàn vào ROE proxy giả định: 0,71–1,28.**
   - Con số 0,71 (haircut 29%) chỉ đúng khi proxy giữ ROE đỉnh 5 năm.
   - Với ROE TB5Y của chính mã, tâm DD thấp hơn proxy 5–15%. Mức này khớp chuỗi haircut đo trực tiếp −11,5% (N=19).
3. **Mẫu DD là nhóm lãi đỉnh/P/E thấp** (P/E 6,0 vs 11,1). Trên P/B, mẫu DD không khác ngẫu nhiên (p=0,61). Với ROE chuẩn hoá theo mã, "DD rẻ hơn thị trường" mất ý nghĩa (p=0,054/0,72).
4. **REFUTED_OPEN vs CONFIRMED**: p=0,058.
   - Phần lớn khoảng cách tâm/proxy đã có từ rev1 (82% ở cơ sở D1; 40–82% qua các cơ sở). Đợt dựng lại thêm −8,2% so với −4,2%.
   - Khoảng cách **giá/tâm** (1,36 vs 0,92) gần như hoàn toàn do đợt dựng lại (rev1: 1,06 vs 1,03).
5. **G5**: P/E ngụ ý thấp vì **chính các mã này** đang giao dịch ở P/E thấp (0,63× ngành). Tâm DD xấp xỉ P/E thị trường của chính mã (0,95×). Câu "xác nhận tâm DD thấp hệ thống" **không còn đứng**.
6. **Không đổi**: G2 chuỗi −11,5% (N=19); G3 dự báo "không vững" (IS t=0,81); G4 bất đối xứng ở khâu SINH (2,9×). Không chạy lại vì ngoài phạm vi; số D1 giữ nguyên.

## G3 — mức hôm nay so với 10Y (cơ sở Big-4 thuần; 120 tháng; `g3_level_monthly_d2.csv`)

| ROE proxy | biến thể | hôm nay | trung vị 10Y | p10–p90 | phân vị hôm nay | tháng giá<proxy (/120) |
|---|---|---|---|---|---|---|
| TTM (như D1) | hold 5Y | 1,281 | 1,451 | 1,18–1,84 | **22,5** | 2 |
| TTM | fade 10Y | 1,077 | 1,189 | 1,05–1,37 | 15,8 | 9 |
| TB5Y theo mã (ROE5Y) | hold | 1,160 | 1,219 | 1,03–1,43 | 35,0 | 10 |
| TB5Y theo mã | fade | 1,027 | 1,150 | 0,96–1,32 | 13,3 | 14 |
| khử đỉnh đồng loạt | hold | 1,650 | 1,468 | 1,14–1,77 | **75,0** | 5 |
| khử đỉnh đồng loạt | fade | 1,131 | 1,192 | 1,01–1,35 | 30,8 | 12 |
| ÷ tỷ lệ rổ (1,584 nay) | hold | 2,147 | 1,933 | 1,52–2,31 | 73,3 | 0 |
| ÷ tỷ lệ rổ | fade | 1,235 | 1,308 | 1,13–1,49 | 25,0 | 1 |
| (P/B thô) | | 0,983 | 1,152 | 0,98–1,37 | 10,8 | |
| *(D1 parity: TTM, lãi effective)* | hold | 1,281 | 1,381 | 1,11–1,73 | 35,0 | 5 |

- "Khử đỉnh" = ROE_ttm ÷ (tỷ lệ EPS_ttm/TB5Y của rổ ÷ trung vị 10Y nhân quả của nó). "÷1,584" = đúng chữ dispatch; nó chứa cả kéo tụt do tăng trưởng nên là **cận dưới** của ROE.
- ROE5Y là cột BQ (TB ROE 5 năm), độ phủ ≥99% mọi năm. PIT theo cách join của `ticker_financial`, chưa kiểm độc lập.

## G1 — mẫu DD vs mẫu ngẫu nhiên PIT (`g1_dd_vs_proxy_d2.csv`, `g1_random80_exdd.csv`)

- Universe 2026-11-20 có 338 mã, trong đó 33 mã DD. Pool sau khi loại DD còn 305 mã; lấy 80 mã, seed 20261124. **Không còn mã trùng.**
- Sổ DD: bản D1 đã đọc `inputs/dd_price_zones_e547cd7fc.json` (md5 9e4cab03…). Bản R1 `da6018d95` có cùng tâm 36 mã (assert), chỉ khác nhãn PAT/TCH/VGS.

| ROE proxy | biến thể | DD trung vị giá/proxy | ngẫu nhiên | MWU p | **tâm DD/proxy** | tâm rev1/proxy |
|---|---|---|---|---|---|---|
| TTM | hold | 0,703 | 1,542 | <0,001 | **0,707** | 0,763 |
| TTM | fade | 0,849 | 1,103 | 0,016 | **0,923** | 0,971 |
| TB5Y theo mã | hold | 0,915 | 1,107 | 0,054 | **0,847** | 0,899 |
| TB5Y theo mã | fade | 1,074 | 1,088 | 0,72 | **0,954** | 1,033 |
| khử đỉnh | hold / fade | 0,93 / 0,94 | 2,00 / 1,22 | <0,001 / 0,039 | **0,951 / 1,032** | 1,02 / 1,11 |
| ÷1,584 | hold / fade | 1,24 / 1,10 | 2,64 / 1,37 | <0,001 / 0,11 | **1,282 / 1,160** | 1,39 / 1,20 |

- Ở các dòng khử đỉnh và ÷1,584, hệ số rổ được áp lên MỌI mã. Mã ROE thấp bị đẩy xuống dưới r, nên proxy của mẫu ngẫu nhiên phồng lên. So sánh DD với ngẫu nhiên ở hai dòng này **không diễn giải được**; chỉ cột tâm DD/proxy có nghĩa.
- **REFUTED_OPEN (19) vs CONFIRMED (17)**, nhãn bản e547cd7fc:
  - Cơ sở D1: 0,522 vs 0,778, p=0,058. Rev1: 0,615 vs 0,855, p=0,35.
  - Khoảng cách log đã có ở rev1: 82%. Qua 8 tổ hợp cơ sở: 40–82%; p bản cuối 0,010–0,18.
  - Nhãn bản da6018d95 (16 RO): p=0,031 (cơ sở D1).
  - ⇒ Độ lớn "RO bị haircut nặng hơn" **không ổn định theo nhãn và cơ sở**, không gọi là chẩn đoán mạnh.
- "Rev1" ở đây = rev nhỏ nhất **có tâm** trong cùng `dd_date` với bản cuối. Skeptic ra CF 0,812 (định nghĩa rev1 khác, có thể lấy cả `dd_date` cũ hơn với DRI/NNC/TV2).

## G2 — nhãn hướng (`g2_module_summary_d2.csv`, lấy từ cột `direction` của waterfall D1)

- r_cost_of_equity = **two_way**. Theo V1, r gắn lãi huy động với β=1, nên đi được cả hai chiều. Cả 3 bước quan sát đều giảm vì neo 13,5% đang trên dải Ke 12,3–13,4%.
- Một chiều theo CSV: KTPL/ESOP/NCI, capex V4, quản trị, trần g_T, CK thanh khoản. earnings_fade và scenario_weighting ghi lẫn down/two_way. Số trung vị từng bước giữ nguyên D1.

## G5 — P/E ngụ ý (`g5_implied_pe_d2.csv`, N=36)

| | trung vị |
|---|---|
| P/E ngụ ý của tâm (tâm/EPS TTM) | 5,75 |
| P/E thị trường của chính mã | 5,98 |
| **ngụ ý ÷ thị trường chính mã** | **0,95** (19/36 dưới 1) |
| P/E thị trường chính mã ÷ ngành 10Y | 0,63 |
| ngụ ý ÷ ngành 10Y | 0,57 |
| ngụ ý trên EPS TB5Y theo mã (thị trường cùng cơ sở) | **7,22 (7,21)** ⇒ ÷ ngành 0,71 |
| ngụ ý trên EPS khử đỉnh / ÷1,584 | 7,14 / **9,10** ⇒ ÷ ngành 0,71 / 0,90 |

Đọc: 0,57 = 0,63 (mã/ngành, tức chọn mẫu) × 0,95 (tâm/giá). Tâm DD thấp so với ngành là do **mẫu**, không phải do phương pháp.

## 6. Đề xuất nhãn "so với lịch sử" cho DD — hiệu chuẩn bằng thước DD-tương-đương (CHỈ ĐỀ XUẤT)

- Thước DD-tương-đương của một mã = k × proxy, với k = trung vị tâm DD/proxy đo trên mẫu hôm nay.
- Phân phối lịch sử của giá/(k×proxy) là phân phối giá/proxy của universe PIT chia cho k. Dùng thước này thay cho giá/proxy thô (vốn sai thước: so DD với proxy chưa haircut).

| ROE proxy / biến thể | k | trung vị 10Y giá/DD-tđ | p25–p75 | thị trường nay (phân vị) | sổ DD 1,085 → phân vị |
|---|---|---|---|---|---|
| TTM hold | 0,707 | 2,05 | 1,82–2,39 | 1,81 (p22,5) | p0 |
| TTM fade | 0,923 | 1,29 | 1,20–1,39 | 1,17 (p15,8) | p7,5 |
| TB5Y hold | 0,847 | 1,44 | 1,32–1,58 | 1,37 (p35) | p2,5 |
| TB5Y fade | 0,954 | 1,21 | 1,12–1,29 | 1,08 (p13,3) | p13,3 |
| khử đỉnh hold | 0,951 | 1,54 | 1,38–1,73 | 1,73 (p75) | p5 |
| khử đỉnh fade | 1,032 | 1,16 | 1,09–1,23 | 1,10 (p30,8) | p25 |
| ÷1,584 fade | 1,160 | 1,13 | 1,07–1,19 | 1,06 (p25) | p32,5 |

- Đọc: theo MỌI thước DD-tương-đương, giá/tâm trung vị 1,085 của sổ DD nằm ở **p0–33** lịch sử. Nghĩa là "19% đạt luật 4" **không** phải dấu hiệu thị trường đắt bất thường theo thước DD. Kết luận này khớp MEMO mục 1.
- Đề xuất hiển thị: nhãn = phân vị giá/tâm của mã trên phân phối giá/(k×proxy), báo **dải [fade, hold]** của MỘT cơ sở ROE chọn trước (khuyến nghị: TB5Y theo mã, cơ sở đặc thù mã duy nhất). Không gán nhãn nếu dải vắt qua ngưỡng. Chỉ HIỂN THỊ, không vào luật 4, không chạm giá trị nội tại (giữ mù giá).
- Giới hạn: k đo trên **một mặt cắt** (35–36 mã, 20/11/2026) và **giả định k bất biến theo thời gian**. Giả định này không kiểm được nếu chưa có sổ DD lịch sử. Bản thân mẫu là nhóm P/E thấp, nên k có thể không đại diện universe. Cần user quyết trước khi làm.

## N độc lập & điều KHÔNG kết luận được

- G3: 120 mặt cắt tháng, chuỗi mức tự tương quan cao ⇒ N độc lập **ước lượng 3–5 chu kỳ**. Phân vị là mô tả, không kiểm định.
- G1/G5: một mặt cắt; 36 mã DD (không độc lập hoàn toàn: cùng mùa BCTC, cùng ngành). MWU p chỉ mang tính tham khảo. 80 mã ngẫu nhiên là một lần rút (seed cố định).
- **Không kết luận được**: (a) mức "rẻ hôm nay" của thị trường theo thước DD khi chuẩn hoá ROE (p13–75 tuỳ cách); (b) haircut ròng của DD (tâm/proxy 0,71–1,28); (c) RO bị haircut nặng hơn CF (p 0,01–0,45 tuỳ cơ sở/nhãn/rev); (d) tính ổn định thời gian của k cho nhãn §6.
- Caveat dữ liệu giữ nguyên D1: chuỗi lãi Big-4 có 26 mốc neo hồi tố (2026-06-19), không PIT thật cho quá khứ; OShares/BVPS lệch ex-date (ticket F); ROE5Y chưa kiểm PIT độc lập.
