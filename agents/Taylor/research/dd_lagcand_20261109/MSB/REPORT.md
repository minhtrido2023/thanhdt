# DD — MSB (NHTMCP Hàng Hải Việt Nam) · r2 (áp errata skeptic) · as-of 09/11/2026 · job `Taylor_20261109_083128` (r1: `REPORT_r1.md`, job `Taylor_20261109_073606`)

> NGHIÊN CỨU, trung dung. Không phải khuyến nghị, không đặt lệnh. Khung NGÂN HÀNG (RI/P/B-ROE; không net cash/GPM).
> Đã qua fundamental-skeptic r1 (CONFIRMED medium); r2 áp 7 đính chính — xem Phụ lục E.
>
> **Nguồn GỐC (đã lấy được BCTC Q3/2026)**: tải từ msb.com.vn (trang IR, AJAX `msb_financial_report_load`), PDF scan, render pymupdf, đọc ảnh:
> **[HN-Q3]** BCTC hợp nhất Q3/2026 (ký 29/10/2026) · **[RL-Q3]** BCTC riêng Q3/2026 · **[SX6T]** BCTC hợp nhất 6T/2026 soát xét KPMG (14/08/2026) ·
> **[IR-Q3]** tài liệu cập nhật KQKD Q3/2026 (05/11/2026, có text) · đã tải nhưng chưa đọc: HN Q2/26, Q1/26, Q4/25, Q3/25, KT 2025, giải trình Q3/25 (`src/`).
> **[BQ]** `tav2_bq.ticker`/`ticker_financial` tới 06/11/2026 · **[NGÀNH]** `kb/data_registry/market-state/sector_read_ngan_hang_20261031.md` (Bobby, mù) ·
> **[VĨ MÔ]** `macro_snapshot_20261109.md` (DISPLAY-ONLY) · **[WEB]** thứ cấp (ghi trong `calc/notes_read.md`).
> Sổ đọc ảnh: `calc/notes_read.md` (số + trang). Tính: `calc/bank_metrics.py`, `calc/model.py`, `calc/peers_xcheck.py`; khoá `calc/LOCK_prerun.txt` / `LOCK_post.txt`;
> **assumptions_md5 `3f3ba648f097295e3c72ebfae7243d18`** (`calc/assumptions.json`). Đơn vị tỷ đồng; giả định tương lai = **(ước lượng)**.

## 1. Kết luận

- **Giá trị nội tại (mù giá) — tâm 13.018 đ/cp sau chiết khấu thanh khoản (13.068 trước), P10 9.675 / P50 12.962 / P90 16.373** (r1: 12.739 / 8.652 / 16.373).
  Vùng tham chiếu **9.700–16.400, tâm ~13.000** (lưu ý: tâm nhạy với độ đối xứng kịch bản XẤU — r1 bất đối xứng cho 12.739; nêu cả hai: 12.700–13.000).
  Giá 16.350 (06/11) **TRONG vùng, biên trên, không phân biệt được với TRÊN**: cách P90 16.373 chỉ 0,1% (đóng cửa 04–05/11 = 16.450 > P90);
  **86% trọng số giá trị < giá** (phân vị ~86–92 tuỳ quy ước); giá cao hơn tâm **+26%**. Luật 4 (giá ≤ 0,85×tâm = 11.065) **không đạt**.
- **Vì sao không rẻ:** ROE MSB là ROE **trung bình** (trailing 13,7–14,1% suốt 10 quý; ROE_Min5Y 14,2%; ROE10Y 11,4%) — xấp xỉ Ke 13,5%.
  Ngân hàng có ROE ≈ Ke thì P/B hợp lý ≈ 1,0–1,1x; giá đang P/B **1,31x** (BVPS 12.515). Ở tương quan ngành, MSB **đắt hơn** các NH
  ROE cao hơn: hồi quy P/B~ROE_Min3Y 18 NH cho 1,13x (14.193 đ), trung vị P/B 1,15x (14.384 đ) [BQ 06/11; `peers_xcheck_out.txt`].
- **Giá ngụ ý Ke 11,7%** (≈ lãi huy động 12T 5,6%, thấp hơn mức thực 7,4% ~2pp) **hoặc** kịch bản TỐT (ROE quay về 16%) là kịch bản trung tâm.
- **LAG chọn vì:** LNST Q3 **1.649 tỷ (+29,4% YoY, +31,9% QoQ)**; 9T +16,9%; TTM +16,1%. Động lực = **NII +607 tỷ** (khối lượng + TNEX);
  phần lớn **bền** (PPOP +17,7%), nhưng có phần kém chất lượng: **dự phòng Q3 giảm 12,5% YoY trong khi NPL/nhóm 2 tăng, bao phủ 47%**.
- **Điểm yếu lớn nhất: chất lượng tài sản + tài sản treo.** NPL BCTC hợp nhất **2,70%** (IR công bố 1,96% — lệch chưa giải thích; bao phủ 47,17% = 2.964/6.284 nên IR cũng dùng mẫu số 2,70%, 1,96% không nhất quán; NPL tuyệt đối riêng lẻ 5.173→5.487, +6% YTD — không phải "nợ xấu giảm"; giữ 2,70%), nhóm 2 **+66% YTD**,
  bao phủ **47,2%**; TNEX (CTTC số) dư nợ ×2,6 YTD với **NPL 8,0%**; **phải thu bán nợ (RRTD) 4.101 tỷ tại 30/09 (4.001 tại 31/12/25 và 30/06; +100 tỷ trong Q3; ~8,8% VCSH)**; DP 38 tỷ là dự phòng rủi ro khác chung, không riêng khoản này.
- **Room tín dụng — ĐÃ QUAN SÁT (không phải giả định):** dư nợ ngân hàng mẹ +10,69% YTD (201.404→222.925) so room NHNN 10,45% [IR-Q3 p7]; LC mua đứt miễn truy đòi 2.383→9.229 (kênh CV 9608 trừ vào room). Hệ quả: Q4/26 tăng trưởng ~0 nếu không cấp thêm room ⇒ kịch bản TỐT và Q4 CƠ SỞ 1.700 kém chắc. Hướng giảm tối đa ~1–2% tâm **(chưa định lượng, không vào model)**; trigger nâng ở mục 6.
- **Cờ tự động "Gordon P/B 1,31 vs 1,53 CHEAP" là NHIỄU** (mục 7): 1,53x đến từ ROE5Y 17,2% (gồm đỉnh 2021–22); dùng ROE bền 14,1–14,2% ⇒ 1,08–1,09x.
- **Pháp lý:** không tìm thấy vụ việc (1 lượt tìm) ⇒ không WARNING. KPMG soát xét 6T/2026 **chấp nhận toàn phần**; đổi kiểm toán viên 2026.
- **Thanh khoản không ràng buộc** khẩu phần sleeve (40 triệu = 0,04% ADV250; CK 0,03%). Ràng buộc là **định giá**, không phải thanh khoản.

## 2. Q1 — Vì sao LAG chọn: surprise, bền hay một lần, nền so sánh

| Chỉ tiêu (HN) | Q3/26 | Q3/25 | YoY | 9T26 | 9T25 | YoY |
|---|---|---|---|---|---|---|
| NII | 3.422 | 2.815 | +21,6% | 9.621 | 7.904 | +21,7% |
| Dịch vụ thuần | 302 | 200 | +51% | 846 | 1.108 | −23,7% |
| Ngoại hối | 130 | 285 | −54% | 214 | 786 | −72,7% |
| CK đầu tư | −25 | −37 | | −162 | +30 | |
| HĐ khác thuần | 156 | 140 | | 510 | 369 | +38% |
| OPEX | −1.539 | −1.326 | +16,1% | −4.124 | −3.864 | +6,7% |
| PPOP | 2.446 | 2.077 | +17,7% | 6.906 | 6.333 | +9,1% |
| Dự phòng | −429 | −490 | −12,5% | −1.466 | −1.572 | −6,7% |
| LNTT | 2.017 | 1.587 | **+27,1%** | 5.440 | 4.760 | +14,3% |
| LNST | 1.649 | 1.274 | **+29,4%** | 4.414 | 3.777 | +16,9% |

Nguồn: [HN-Q3] p7. Phân rã ΔLNTT Q3 +430: NII +607, DV +103, FX −155, CKĐT +11, khác +16, OPEX −213, DP +61 (`bank_metrics_out.txt`).

- **Nền so sánh:** KHÔNG thấp bất thường — LNST Q3/25 1.274 ngang Q2/25 1.237 và Q1/25 1.266 [BQ]. Q2/26 chỉ +1% YoY ⇒ Q3 là
  quý tăng tốc, không phải xu hướng đều. KH 2026 LNTT 8.000; 9T đạt 68% [IR-Q3 p19].
- **Bền:** NII tăng nhờ khối lượng (CV KH +13,5% YTD; TNEX dư nợ 3.805 → 10.021) và lợi suất (TN lãi +51,5%) bù chi phí lãi (+83,3%).
  NIM tự tính 9T26 **3,26%** (IR: NIM TTM 3,20%, Q2 3,17%) — đi ngang, không mở rộng.
- **Kém chất lượng/một lần:** (i) DP giảm khi NPL tăng — nếu DP Q3 giữ mức Q3/25 thì LNTT Q3 1.956 (+23,2%), vẫn tăng mạnh; (ii) phí DV Q3 tăng
  từ nền 9T giảm 24%; (iii) FX giảm là kéo xuống, không phải đẩy lên. **Kết luận: surprise phần lớn là PPOP thật (bền), ~4pp đến từ dự phòng thấp.**

## 3. Chất lượng tài sản, vốn, nguồn vốn (khung Bobby §7)

| Chỉ tiêu | 30/09/26 | 31/12/25 | Ghi chú |
|---|---|---|---|
| NPL HN (nhóm 3–5) | 6.285 (**2,70%**) | 5.520 (2,69%) | [HN-Q3 p31]. IR công bố HN 1,96% / riêng 1,64% — **lệch ~0,7–0,8pp, cần hỏi IR** |
| NPL riêng lẻ | 5.487 (2,46%) | 5.173 (2,57%) | [RL-Q3 p30] |
| Nhóm 2 HN | 3.904 (1,68%) | 2.347 (1,14%) | **+66% YTD** — cờ Bobby (>+20%) |
| Bao phủ (DP/NPL) | **47,2%** | 51,6% | DP 2.964 (chung 1.720, cụ thể 1.245) [p33]; cờ Bobby <70% |
| Hình thành NPL 9T | ΔNPL 764 + xoá 1.351 = 2.116 | | **1,29%/năm** dư nợ BQ; chi phí tín dụng 9T **0,89%** < tốc độ hình thành |
| TNEX (HN−riêng) | dư nợ 10.021, NPL **8,0%**, nhóm 2 7,1% | 3.805, NPL 9,1% | ×2,6 YTD; CTTC ngành NPL 7,2% (Bobby) |
| Lãi phí phải thu / TTS | 12.329 / **2,80%** | 10.203 | cờ Bobby >2%; lãi tín dụng phải thu 30/06 +19% vs dư nợ +12,3% (6T; dư nợ 30/06 230.420 theo [IR-Q3 p9]) |
| Phải thu bán nợ cho đối tác (RRTD) | **4.101** | 4.001 | **+100 tỷ trong Q3 (4.001 chỉ đúng tới 30/06), ~8,8% VCSH**, xếp "có rủi ro tín dụng" [SX6T p45; HN-Q3 p36] |
| Mua hẳn miễn truy đòi LC | 9.229 (30/06) | 2.383 | ×3,9 trong 6T = 4,0% dư nợ — đúng kênh CV 9608 trừ khỏi room |
| Đặt cọc thuê văn phòng | 3.300 (30/06) | 3.310 | 7,0% VCSH — lớn bất thường cho tiền cọc |
| Phải thu khác (tổng) | 18.501 | 6.599 | ×2,8; Q3 không tách (+4.720 so 30/06) |
| KKH / TG KH | **20,4%** | 28,1% | KKH −10.938 tỷ (−19,8%); IR: CASA 21,73% "mùa vụ" |
| CAR HN | 11,67% | 12,49% | [IR-Q3 p15]; CET1/TT14 chưa có |
| LDR riêng (quy định) | 64,9% | 62,0% | [IR-Q3]; CV/TG KH thô 107% |

**Đọc:** cùng pha "sớm–giữa xấu đi" của Bobby: tầng sớm (nhóm 2, lãi dự thu, phải thu) xấu đi, bao phủ thấp hơn hẳn ngành (~80%). MSB có đệm vốn
(VCSH/TTS 10,7%, LDR thấp) nhưng **đệm dự phòng mỏng**: đưa bao phủ lên 80% cần 2.064 tỷ trước thuế (≈ 1 năm chi phí tín dụng hiện tại).

## 4. Vị thế & lợi thế cạnh tranh (5F tầng b) — làm MỚI (chưa có dòng MSB trong `data/moat_tags.csv`, chưa có DD cũ)

- **Loại hình:** NHTM tư nhân cỡ trung (TTS 440 nghìn tỷ; VĐL top 10 [IR]), thiên doanh nghiệp (TCKT 66,6% dư nợ), bán lẻ + CTTC số TNEX đang mở.
- **Ngành (tầng a, Bobby):** ADMIN_GATED 0,45 / CYCLICAL 0,35 / STRUCTURAL 0,20; NIM ngành đi ngang–giảm; chu kỳ tài sản xấu đi.
- **5 lực + lực thứ 6:** (1) cạnh tranh nội ngành cao — tư nhân trả premium 1–1,6pp huy động (Bobby §3); (2) khách hàng vay có quyền mặc cả
  (CV 9608 ép giảm lãi ưu tiên); (3) nhà cung cấp vốn = người gửi tiền: lợi thế CASA cũ của MSB **đã mất phần lớn** (28,1% → 20,4%);
  (4) thay thế: fintech/CTTC — MSB tự chơi qua TNEX; (5) gia nhập: giấy phép là rào cản ngành chung, không riêng MSB; (6) **lực thứ 6 =
  NHNN**: room tín dụng (MSB được cấp 10,45%; đã dùng 10,69% YTD cấp mẹ [IR p7]), chế tài CV 9608 với kênh LC miễn truy đòi mà MSB đang dùng mạnh.
- **Bằng chứng định lượng:** ROE − Ke: trailing ≈ +0,5pp; ROE_Min5Y +0,7pp (đạt mỏng), ROE10Y 11,4% < Ke (gồm tái cơ cấu 2016–19) ⇒ **không có siêu ngạch rộng, bền nhiều chu kỳ**;
  CASA top 3–4 2021–25 (~30%) là cơ chế gọi tên được (ii) nhưng đang suy yếu; (iii) đồng hồ: room/CV 9608.
- **moat_tier = NONE** — nhãn r2: *NARROW-ứng viên không bền*. Điều kiện (i) ĐẠT mỏng: ROE_Min5Y 14,2% > Ke 13,5% (+0,7pp; r1 dựa ROE10Y 11,4% là chưa đủ); NONE đứng nhờ (ii) CASA 28,1%→20,4% suy yếu và (iii) đồng hồ room/CV 9608; moat_type: —; **rủi ro số 1:** chất lượng tài sản (bao phủ 47% + tài sản treo 4.101).
- **Tham số moat trong mô hình:** KHÔNG thưởng (RONIC terminal = Ke). KHÔNG trừ: ROE cơ sở giữ ở mức dữ liệu 14% (không ép về Ke).
  Độ nhạy "ROE hội tụ nửa đường về Ke" (thông tin rủi ro): 12.598 (−3,2%) — moat ít tác động vì ROE vốn đã ≈ Ke.
  Nếu giả định WIDE (RONIC = ROE_T, g 6%): 13.608 (+4,5%).
- **Đề xuất dòng `moat_tags.csv`** (human-curated, KHÔNG tự sửa): `MSB,NONE,,—,"Asset quality: coverage 47%, 4.1T debt-sale receivable (+100bn in Q3), TNEX NPL 8%; CASA edge eroded 28%->20%",2026-11-09,dd_lagcand_20261109,N`.

## 5. Q2 — Giá trị nội tại (RI, mù giá)

**Phương pháp:** RI 3 năm tường minh 2027–29 + terminal RONIC=Ke (`TV = (ROE_T − Ke)·BV_N / Ke`), BV đầu = VCSH 30/09 46.857 + LNST Q4/26 kịch bản,
**có quyền mua 936 tr CP @10.000** (cộng 9.360 vào BV, trừ PV tiền nộp, chia cho 3.744 tr CP hiện tại); payout tiền 0 (MSB trả CP thưởng).
**r = Ke 13,5%** = 13,5% + 1,0×(7,40% − 7,40%) (lãi huy động 12T hiệu dụng = CCTG 12M 7,40% ngày 02/11, `deposit_rate_vn`).

| Kịch bản (w) | Q4/26 LNST | ROE 2027/28/29 → T | Giá trị (trước CK) | P/B ngụ ý |
|---|---|---|---|---|
| XẤU (0,275) | 1.350 | 10,0 / 10,5 / 11,0 → **12%** (r1: 11%) | 9.931 (r1: 8.899) | 0,79x |
| CƠ SỞ (0,45) | 1.700 | 12,5 / 13,5 / 14,0 → 14% | 13.230 | 1,06x |
| TỐT (0,275) | 1.950 | 14,0 / 15,5 / 16,0 → 16% | 16.435 | 1,31x |

Cơ sở ROE: trailing 13,7–14,1% (10 quý), ROE_Min5Y 14,2%; CƠ SỞ 2027 12,5% do VCSH +20% từ quyền mua. XẤU = chi phí tín dụng lên + NIM nén (CASA);
TỐT = TNEX mở rộng + về vùng ROE5Y. Tất cả **(ước lượng)**. Trọng số đối xứng (tiền lệ MBB/FPT). **r2:** ROE_T XẤU nâng 11%→12% để đối xứng quanh CƠ SỞ 14% (TỐT +2pp ↔ XẤU −2pp; ROE_Min5Y 14,2%; 11% từng dựa ROE10Y gồm tái cơ cấu 2016–19); path 2027–29 XẤU giữ nguyên (chưa có cơ sở riêng).
Lưới 27 = kịch bản × dịch ROE ±1pp (0,25/0,5/0,25) × haircut phải thu bán nợ 4.101 tỷ 0/25/50% (0,5/0,3/0,2) [UL — rủi ro cụ thể quan sát được, nên là kịch bản có xác suất, không vào tâm tham số].

| | Tâm | P10 | P25 | P50 | P75 | P90 |
|---|---|---|---|---|---|---|
| Trước CK thanh khoản | 13.068 | 9.712 | 11.289 | 13.011 | 14.799 | 16.435 |
| **Sau CK (5 tỷ, 0,38%)** | **13.018** | **9.675** | 11.247 | 12.962 | 14.743 | **16.373** |
| Sau CK (40 triệu, 0,03%) | 13.063 | 9.709 | | | | 16.430 |

Giá trị ở tham số trung tâm (CƠ SỞ, không haircut) sau CK: 13.180.

*Quyền mua:* "624 triệu cp" = cổ phiếu thưởng 20% (GDKHQ 28/08) đã nằm trong 3.744 triệu cp / BVPS 12.515 — không pha loãng giá trị thêm; pha loãng thật = quyền mua 936 triệu cp @10.000 (BVPS sau ~12.012), model xử lý cum-rights. Độ dài PV tiền nộp: 52/365 năm (r1 ghi 0,5 năm ở assumptions — đã sửa, không đổi số).

**Độ nhạy lãi huy động (β=1):** −100bp 14.740 (+13,2%) · −50bp 13.844 (+6,3%) · +50bp 12.255 (−5,9%) · +100bp 11.549 (−11,3%);
β=0,5: −100bp 13.844, +100bp 12.255. **Ke ngụ ý bởi giá = 11,70%** (lãi huy động 12T ngụ ý 5,60%).

**Độ nhạy khác (tâm sau CK):** không quyền mua 12.940 (−0,6%: quyền mua ~trung tính vì ROE ≈ Ke) · bao phủ 80% 12.573 (−3,4%) ·
terminal tăng trưởng g 6% 13.608 (+4,5%) · ROE hội tụ nửa đường về Ke 12.598 (−3,2%).

**Đối chiếu tương đối (không vào headline):** hồi quy P/B~ROE_Min3Y (18 NH, R² 0,19) 14.193; P/B~ROE5Y 13.987; trung vị P/B 14.384.
Cả 3 đều < giá 16.350 và > tâm RI ~10–13% — nhóm NH đang được định giá ở Ke ngụ ý thấp hơn 13,5%.

## 6. Q3 — Rủi ro lớn nhất & điều làm nhận định đổi theo CẢ HAI chiều

**Rủi ro số 1:** chu kỳ chất lượng tài sản gặp đệm dự phòng mỏng (bao phủ 47%, hình thành NPL 1,29%/năm > chi phí tín dụng 0,89%) + tài sản treo
(phải thu bán nợ 4.101, LC miễn truy đòi tăng ×3,9). Nếu buộc xây lại bao phủ, ROE 2027 về vùng XẤU.

| Chiều | Điều kiện (mốc kiểm) | Tác động |
|---|---|---|
| ↑ tích cực | Lãi huy động 12T giảm ≥100bp (CCTG Big-4 ≤ 6,4%) bền | tâm ~14.700 (+13%) |
| ↑ | BCTC Q4/26: nhóm 2 giảm QoQ **và** bao phủ ≥ 60% **và** phải thu bán nợ 4.101 thu hồi/giảm | dịch trọng số sang CƠ SỞ/TỐT, bỏ haircut ⇒ ~13.300–14.500 |
| ↑ | ROE TTM ≥ 16% hai quý liền sau khi đã phát hành quyền mua (TNEX đóng góp) | TỐT thành trung tâm ⇒ ~16.000 (≈ giá) |
| ↓ tiêu cực | Nhóm 2 + NPL Q4/26 tiếp tục > +20% QoQ, hoặc DP Q4 < 400 khi NPL tăng | XẤU chiếm ưu thế ⇒ ~9.900 (giá trị kịch bản XẤU r2, tham số trung tâm) |
| ↓ | IR không giải thích được lệch NPL 2,70% vs 1,96% / phải thu 4.101 bị trích lập | −440 đ/cp mỗi 50% haircut; −445 cho bao phủ 80% |
| ↓ | Lãi huy động +100bp; NHNN hạ room 2027 cho NH dùng kênh LC | 11.500 hoặc thấp hơn |
| ↓ (r2) | Room 2026 không được cấp thêm (đã dùng 10,69% vs 10,45% được giao) ⇒ Q4/26 tăng trưởng ~0; LNST Q4 < 1.700 | chưa định lượng; ước lượng ≤ −1–2% tâm |

Mốc kiểm: BCTC Q4/2026 (cuối 01/2027); kết quả chào bán 25%; NHNN giao room 2027.

## 7. Q4 — Cờ tự động của hệ: thật hay nhiễu

| Cờ | Kết luận | Lý do (số) |
|---|---|---|
| Gordon P/B 1,31 vs hợp lý 1,53 → CHEAP | **NHIỄU** | 1,53x = ROE5Y 17,2% @Ke ~13,3%, g 6%. ROE5Y gồm 2021–22 (đỉnh); ROE trailing 14,1% / ROE_Min5Y 14,2% @Ke 13,5% ⇒ 1,08–1,09x = 13.500–13.700 đ < giá. Phản đề: ở Ke 12,3% thì 1,28–1,30x ≈ giá |
| FSCORE 3 | thật nhưng ít ý nghĩa | Piotroski cho DN phi tài chính; với NH xem mục 3 |
| D/E 8,39 | bình thường | VCSH/TTS 10,7%, CAR 11,67% |
| LAG_LO, ADV3T 134 tỷ | khớp bậc | ADV trung vị 60 phiên 124 tỷ; 20 phiên 152; 250 phiên 90 |
| Gợi ý kiểm (NPL/nhóm 2/LLCR, CASA, NIM, LN Q3 một lần, CAR) | đã kiểm | mục 2–3: NPL 2,70%, bao phủ 47%, CASA 20,4%, NIM 3,26% đi ngang, ~4pp LN Q3 từ DP thấp, CAR 11,67% |

## 8. Q5 — Thanh khoản & sizing

- ADV trung vị 250 phiên **90,2 tỷ**, 60 phiên 124,2, 20 phiên 151,8; σ ngày 1,61% [BQ 04/11/2025–06/11/2026].
- CK (σ·√(Q/ADV250)): 5 tỷ **0,38%** (5,5% ADV, 0,37 phiên ở 15% ADV); 40 triệu 0,03%; 10 triệu 0,02%.
- Khẩu phần sleeve LAG (vài chục triệu–vài trăm triệu) **không bị ràng buộc thanh khoản**. Lưu ý cung: quyền mua 936 tr CP (25%) + cổ đông nhà nước
  muốn thoái (nhiều lần bất thành) [WEB] — overhang khi pha loãng; giá đã +56% YTD [IR-Q3, chỉ ghi nhận].
- **Nhận xét sizing (đề xuất, không phải luật):** giá ở P90 của phân phối giá trị ⇒ nếu LAG vẫn mua theo luật hệ thống, giữ ở mức khẩu phần tối thiểu,
  không tăng tỷ trọng discretionary; quyền mua 25% @10.000 sẽ đòi tiền nộp thêm ≈ 25% × số CP × 10.000 (ước lượng 2.500 đ/cp nắm giữ).

## 9. Kiểm số Mike/hệ & nguồn

| Số | BCTC gốc | Kết quả |
|---|---|---|
| D/E 8,39 | Nợ/VCSH 393.103/46.857 = 8,39 | ĐÚNG |
| P/B 1,31 | 16.350 / BVPS 12.515 (VCSH 46.857 / 3.744 tr CP sau thưởng) | ĐÚNG |
| ROE5Y 17,2% (BQ) | trailing BCTC: LNST TTM 6.265 / VCSH BQ ≈ 14% | số BQ đúng định nghĩa, nhưng không phải ROE bền |
| BQ `ticker_financial` 2026Q3 NP_P0 1.649 | HN-Q3 p7 1.649,2 | ĐÚNG |

## 10. Phụ lục — Thay đổi / chưa làm
- Chưa đọc: BCTC KT 2025 (tách thu nợ ngoại bảng, bancas trả trước, bên liên quan), Q2/26 BS chi tiết (NIM theo quý tự tính), Basel/CAR TT14.
- Câu hỏi IR: (1) lệch NPL công bố vs thuyết minh 9.1; (2) bản chất + lịch thu phải thu bán nợ 4.101 và chênh +100 tỷ so 4.001; (3) phải thu khác 30/09 tách; (4) giá/lịch chào bán 25%; (5) room tín dụng đã dùng vs được cấp (gồm LC mua đứt).
- **Chưa kiểm:** cho vay xây dựng +36,7% YTD (19.801→27.074, 11,6% dư nợ); TPDN nắm giữ; CET1; thanh tra NHNN gần nhất. Nguồn mỏng: tin thoái vốn nhà nước thiếu tên cổ đông/tỷ lệ/ngày; giá chào 10.000đ chỉ 1 nguồn thứ cấp (IR chưa nêu).

## Phụ lục E — Đính chính theo ERRATA_r1_skeptic (fundamental-skeptic r1: CONFIRMED medium; kết luận đứng)

r1 lưu ở `REPORT_r1.md` / `SUMMARY_r1.json` / `calc/*_r1.*`. Nhãn KHÔNG đảo (TRONG vùng); luật 4 vẫn KHÔNG đạt.

| # | Errata | Xử lý r2 | Tác động tâm / P10 / P90 (5 tỷ, sau CK) |
|---|---|---|---|
| 1 | Room tín dụng là dữ kiện đã quan sát (+10,69% vs 10,45%; LC 2.383→9.229) | Nâng lên dữ kiện (mục 1, 6); thêm trigger ↓. **Không đưa vào model** — chưa định lượng được | 0 (ghi hướng giảm tối đa ~1–2% tâm, ước lượng, chưa đo) |
| 2 | Phải thu RRTD 4.101.159 tại 30/09 (4.001.159 tại 31/12; xác nhận lại `notes_read.md` p36) | `base_amount_bn` 4.001,159→4.101,159; sửa mọi chỗ 4.001 (ngoại trừ mốc 31/12/25, 30/06); DP 38 tỷ ghi là dự phòng chung | 12.739→12.735 (−4) / P10 8.652→8.647 / P90 không đổi |
| 3 | NPL: bao phủ 47,17% = 2.964/6.284 ⇒ IR không nhất quán với 1,96%; NPL riêng lẻ +6% YTD | Giữ 2,70%; sửa câu "nợ xấu giảm" (nếu có) → ghi +6% YTD | 0 (câu chữ) |
| 4 | Kịch bản XẤU bất đối xứng (ROE_T XẤU 11% = −3pp vs TỐT +2pp) | ROE_T XẤU 11%→12% (cơ sở dữ liệu: ROE_Min5Y 14,2%; ROE10Y 11,4% gồm tái cơ cấu 2016–19). Path 2027–29 XẤU giữ nguyên | 12.735→13.018 (+2,2%) / P10 8.647→9.675 / P90 16.373 (không đổi) |
| 5 | Moat điều kiện (i): ROE_Min5Y 14,2% > Ke ⇒ đạt mỏng | Nhãn "NARROW-ứng viên không bền"; NONE đứng nhờ (ii) CASA + (iii) room/CV 9608 | 0 (định giá không đổi) |
| 6 | Nguồn mỏng; "624 triệu cp" là cổ phiếu thưởng; `rights.t_years` 0,5 vs 52 ngày | Ghi rõ nguồn mỏng (thoái vốn, giá chào 10.000 chỉ 1 nguồn thứ cấp); sửa `t_years`=52/365 (model.py không dùng giá trị này) | 0 |
| 7 | Nhãn sát P90; mục chưa kiểm | Nhãn "TRONG vùng, biên trên, không phân biệt được với TRÊN"; liệt kê chưa kiểm (xây dựng +36,7% YTD, TPDN, CET1, thanh tra NHNN) + 2 câu hỏi IR | 0 |

**Tổng (5 tỷ, sau CK):** tâm 12.739→**13.018** (+2,2%), P10 8.652→**9.675**, P90 16.373→**16.373**; ngưỡng luật 4 10.828→11.065; giá/tâm +28,3%→+25,6%.
Biên độ thay đổi nằm trong ±2–3% theo chỉ đạo; do thay đổi chủ yếu đến từ #4 (đối xứng), báo cáo nêu khoảng 12.700–13.000.
`assumptions_md5` mới `3f3ba648f097295e3c72ebfae7243d18` (r1 `cec24f792b9df467907b9ef716f8ff5a`); khoá `calc/LOCK_prerun.txt`/`LOCK_post.txt` (r1: `*_r1.txt`).

