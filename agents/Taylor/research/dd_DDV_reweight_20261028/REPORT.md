# DDV — TÁI TRỌNG SỐ kịch bản theo đọc mù ngành của Bobby · 2026-10-28 · job `Taylor_20261028_031824`

> READ-ONLY, không sửa code/config/KB. Không phải khuyến nghị mua; user quyết. Cập nhật `dd_DDV_20261026/REPORT.md` (DD gốc).
> Nhãn: **[BCTC]** = BCTC Q3/2026 DDV (`dd_DDV_20261026/src/en_p1.txt`) · **[BQ]** = `tav2_bq.ticker_financial AS t` / `tav2_bq.ticker AS t` (`comps_fin.csv`, giá 27/10) ·
> **[Bobby]** = `kb/data_registry/market-state/sector_read_fertilizer_dap_20261028.md` (blind, loại B 70/30) · **(ước lượng)** = giả định/suy luận của tôi, KHÔNG phải số đo.
> Phép tính: `model.py` → `out.txt` (chạy lại được, `/home/trido/thanhdt/wc_venv/bin/python model.py`).

## 0. Kết luận

| | DD 26/10 | **Tái trọng số 28/10** |
|---|---|---|
| Trọng số Bear / Base / Bull | 30 / 45 / 25 | **45 / 40 / 15** (ước lượng, §2) |
| Giá trị kỳ vọng/cp (net cash 7.583) | ~18.000 | **~14.500** (dải 12.300–17.300 theo độ dốc biên, §3) |
| Giá trị kỳ vọng/cp (net cash stress ~5.950) | — | **~12.900** (dải 10.700–15.700) |
| Giá tham chiếu | 17.700 (23/10) | **16.700 (27/10)** [BQ] ⇒ **cao hơn EV 15% (NC 7.583) … 30% (NC stress)** |
| Đợt 1 / Đợt 2 | ≤~13.000 / ≤~11.500 | **≤~12.000 / ≤~10.500** |
| Catalyst "S<500 & GPM quý ≥8%" | Q4/26 hoặc Q1/27 | **Không khả thi về thời điểm** (§5); đổi cổng dẫn dắt + dời cổng xác nhận sang BCTC Q2/27 |
| Verdict | NON | **NON, nghiêng xấu đi** (đáy lợi nhuận lùi tới Q2/27 sớm nhất) |

Lý do chính: base cũ giả định S CFR về **400–500 USD/t trong H1/27**; theo Bobby, trung vị hợp đồng Qatar chỉ **~650 (T1/27) → ~580 (T4/27)**, và do tồn kho/độ trễ ~51–62 ngày, giá vốn H1/27 phản ánh S mua từ **T11–T3**, tức vẫn cao hơn nữa.

## 1. Biên gộp QUÝ từ BCTC (không dùng GPM_P0/NPM_P0 của BQ — là TTM) [BCTC, tính từ GP/DT thuần]

| Kỳ | DT thuần (tỷ) | LN gộp (tỷ) | Biên gộp |
|---|---|---|---|
| Q3/25 | 1.396,6 | 305,5 | **21,88%** |
| 9T/25 | 4.153,8 | 731,6 | 17,61% |
| H1/26 (= 9T − Q3) | 3.626,2 | 399,6 | **11,02%** |
| **Q3/26** | 1.290,3 | 47,7 | **3,69%** |
| 9T/26 | 4.916,5 | 447,3 | 9,10% |

Độ trễ tồn kho (đo): tồn kho 836,6 tỷ ÷ COGS/ngày = **51,1 ngày** (COGS 9T/273d) hoặc **61,9 ngày** (COGS Q3/92d); riêng NVL 617,3 tỷ = **45,7 ngày** COGS Q3. Khớp mức ~53 ngày Mike nêu. Hệ quả: COGS Q4/26 gánh S mua T8–T10 (Qatar 835 / KPC 820 / ADNOC 890, giảm chỉ 5–10% từ đỉnh [Bobby]); COGS Q1/27 gánh S mua T11–T12.

## 2. FOB Trung Đông vs proxy TE CNY — vì sao base cũ quá lạc quan

- TE `sulfur` (5.714 CNY/t, −38% từ đỉnh tháng) là **giá nội địa TQ**, giảm vì TQ huỷ cầu; DDV nhập CFR Đông Nam Á ≈ **ME FOB + cước** [Bobby]. ME FOB T10 chỉ thấp hơn đỉnh 5–10% ⇒ chi phí biên thật của DDV giảm **ít hơn nhiều** so với đường TE gợi ý. DD cũ tham chiếu "S về 400–500" theo hướng TE.
- Forecast khoá của Bobby: QSP T1/27 trung vị ~650 (P<835 = 0,75; P<600 = 0,40); T4/27 ~580; P(TE ≤3.000 vào 31/07/27) = 0,25 [Bobby]. ⇒ P(S ≤500 FOB trong H1/27) **~0,15–0,20 (ước lượng, suy từ K2 p=0,30 × nửa đuôi dưới; Bobby không công bố con số này)**, trong khi base+bull cũ ngầm giả định S ≤500 với xác suất 70%.
- Hợp đồng dài hạn: nếu DDV mua theo hợp đồng giá trễ 1–2 quý (Bobby mục 7.3), độ trễ còn dài hơn 53 ngày — chưa xác minh được từ BCTC (hỏi IR: cơ cấu hợp đồng S/NH3).
- **Trọng số mới (ước lượng, suy từ phân phối Bobby):** Bear = hợp của {QSP T4/27 ≥835: 0,25} và {DAP WB T1/27 ≤720: 0,25}, trừ chồng lấn giả định 0,05 ⇒ **0,45**. Bull (S ≤~350 vào cuối 2027 và DAP ≥750) ~ P(K2 sâu) × P(DAP≥750) ⇒ **0,15** (làm tròn lên một chút). Base = phần còn lại **0,40**. Trọng số là ước lượng chủ quan; kết quả nhạy với chúng (xem EV w_old ở §3).

## 3. Bảng kịch bản mới (biên gộp mô hình hoá theo quý, ước lượng)

Hiệu chuẩn (ước lượng): biên gộp Q3/25 21,88% (S ~175 USD/t FOB) và Q3/26 3,69% (S hiệu dụng ~920 sau độ trễ) ⇒ độ dốc **2,44 điểm% biên gộp / mỗi +100 USD/t S** (lẫn tác động DAP, NH3 ⇒ chạy thêm 2,0 và 3,0). Điều chỉnh DAP: 0,067 điểm%/USD so với 800 (ước lượng). DT 2027 = 5.500 tỷ (ước lượng; Q3 chạy 5.160, 9T chạy 6.555), chi phí BH+QLDN = 52 tỷ/quý (Q3/26 thật), thuế 20%.

| Kịch bản | S hiệu dụng Q1→Q4/27 (USD/t) | DAP (USD/t) | Biên gộp quý (độ dốc 2,44) | LN hoạt động sau thuế 2027 (tỷ) | Giá trị/cp (NC 7.583 / NC stress 5.950) |
|---|---|---|---|---|---|
| **Bear 45%** (S ≥835 kéo dài **hoặc** TQ xuất DAP sớm) | 850/800/740/700 | 740/700/680/670 | 1,4/−0,1/0,0/0,4% | **−185** | **10.830 / 9.197** |
| **Base 40%** (trung vị Bobby) | 750/680/600/550 | 770/745/725/710 | 5,8/5,9/6,5/6,7% | **+107** | **14.545 / 12.912** |
| **Bull 15%** (K2 sạch, S ~300 vào Q4) | 700/500/350/300 | 775/765/755/750 | 7,4/11,6/14,6/15,5% | **+373** | **25.456 / 23.823** |
| **EV w_mới 45/40/15** | | | | | **14.510 / 12.877** |
| EV w_cũ 30/45/25 (cùng mô hình) | | | | | 16.158 / 14.525 |

Định giá: Base/Bull = net cash + LN hoạt động × bội số (Base 9,5x, Bull 7x; DD cũ dùng 9–10x và 6x), Bear = net cash − lỗ + 0,72 × (book vận hành − lỗ), book vận hành 7.530 đ/cp (VCSH 2.208,2 − net cash 1.108,0 tỷ) [BCTC]. Bội số giữ nguyên DD cũ để cô lập hiệu ứng kịch bản.

Độ nhạy theo độ dốc biên (EV w_mới, NC 7.583 / NC stress): dốc 2,0 ⇒ **12.296 / 10.663**; 2,44 ⇒ **14.510 / 12.877**; 3,0 ⇒ **17.320 / 15.687**. Ngay cả đầu cao nhất (dốc 3,0, NC 7.583) cũng ≈ giá hiện tại (+4%), không có biên an toàn.

Nhắc: mô hình chỉ hai điểm hiệu chuẩn, DT 2027 và thuế đều giả định ⇒ coi là bậc độ lớn, không phải dự báo LN.

### Stress net cash khi vốn lưu động về bình thường
Net cash 7.583 đ/cp = 1.108,0 tỷ [BCTC] **được thổi bởi vốn lưu động Q3**: phải trả người bán 120 → 569 tỷ (+449), phải thu KH 9,3 → 219,4 tỷ (+210, gần hết là Liven Nutrients 217 tỷ) [DD cũ, BCTC]. CFO Q3 +236,6 tỷ chủ yếu do khoản phải trả này.
- Hoàn trả toàn bộ phải trả (−449) và thu hết phải thu (+210): net cash = **~870 tỷ = ~5.950 đ/cp** (đo).
- Chỉ hoàn 60% cả hai: **~6.600 đ/cp** (đo). ⇒ dải stress **~6.000–6.500 đ/cp** khớp yêu cầu; dùng 5.950 làm đầu xấu.
- Nhạy cảm: nếu **không** thu được Liven (217 tỷ) mà vẫn phải trả hết: ~4.510 đ/cp (đo) — là tình huống HARD ABANDON #2 (§6).
- Chưa tính: rủi ro trích lập giảm giá tồn kho khi S giảm (NVL 617 tỷ mua giá cao; BCTC chưa trích lập); cổ tức (đã trả 248,4 tỷ 9T/26).

## 4. Comps [BQ, `ticker_financial` + giá `ticker` 27/10/2026]

PE chuẩn hoá = vốn hoá ÷ LN trung bình 2018–2025 (cộng 4 quý/năm). Q3/26 của DPM/DCM/BFC chưa có trong BQ (dữ liệu quý gần nhất 2026Q2).

| Mã | Giá | PB | PE TTM (BQ) | PE chuẩn hoá (TB 18–25 / trung vị) | PB lịch sử min / trung vị | Ghi chú |
|---|---|---|---|---|---|---|
| **DDV** | 16.700 | **1,10** (1,21 loại trừ net cash) | 6,2 | **11,9 / 13,6** | 0,66 / 1,15 | S + NH3 nhập khẩu |
| DPM | 21.350 | 1,26 | 8,2 | 9,2 / 20,8 (nhiễu) | 0,60 / 1,13 | Đạm khí, chi phí khí không dính S |
| DCM | 34.650 | 1,60 | 7,0 | 11,8 / 14,5 | 0,49 / 1,51 | Đạm khí |
| LAS | 11.900 | 0,95 | 15,3 | 13,9 / 12,6 | 0,51 / 1,09 | Lân/NPK, cũng dùng axit sunfuric ⇒ cùng cú sốc S |
| BFC | 56.000 | 1,78 | 12,3 | 16,2 / 18,6 | 0,56 / 1,18 | NPK |

Đọc: DDV không rẻ nổi bật theo PE chuẩn hoá (11,9x ≈ DCM 11,8x, thấp hơn LAS/BFC). Lợi thế duy nhất là net cash 43% vốn hoá. Chỉ comps cùng cú sốc S (LAS) có PB 0,95 < DDV 1,10 dù LAS gánh nợ ròng 490 tỷ [BQ Cash−Debt, thô]. Cảnh báo BQ: `Cash_P0` bỏ sót tiền gửi HTM (DDV: BQ 114 tỷ vs thật 1.322 tỷ), nên **không dùng net cash BQ của comps** để chuẩn hoá PB — chỉ PB/PE thô và chuẩn hoá cùng cách. Net cash của comps: chưa đo (cần BCTC từng mã).

## 5. Vùng giá + catalyst

**Vùng giá (đề xuất chỉnh):**
- **Đợt 1 ≤ ~12.000** (PB 0,79; thấp hơn EV stress 12.880 ~7%, thấp hơn EV 14.510 ~17%).
- **Đợt 2 ≤ ~10.500** (PB 0,69 ≈ đáy PB 2020 0,68 / 2023 0,71 [DD cũ]; ≤ giá trị Bear NC 7.583 = 10.830) — tức là giá đã phản ánh Bear, upside đến từ Base/Bull.
- Giá 16.700 cần −28% tới Đợt 1. Lý do hạ từ 13.000/11.500: EV hạ ~3.500 đ (từ 18.000 xuống 14.510) và NC thực có thể thấp hơn 1.600 đ.

**Catalyst cũ — "S <500 USD/t FOB & GPM quý ≥8%, giá ≤~16.000" (BCTC Q4/26 ≈ 20/01/27 hoặc Q1/27 ≈ 20/04/27):**
- *GPM quý ≥8% ở Q4/26–Q1/27:* mô hình cho Base Q1/27 **5,8%**, Bull **7,4%** (dốc 2,44); chỉ dốc 3,0 + Bull mới ≥8% (8,6%). Xác suất **<5% (ước lượng)**. Lý do: độ trễ ~51–62 ngày + S T10 vẫn 820–890.
- *S <500 FOB:* P ~0,15–0,20 vào H1/27 (ước lượng).
- ⇒ Điều kiện **gần như không khả thi trong cửa sổ cũ**; nghịch lý: khi S spot đã <500 thì BCTC chưa phản ánh vì độ trễ (cổng xác nhận đến muộn hơn cổng dẫn dắt ≥1–2 quý).

**Đề xuất catalyst mới (tách dẫn dắt/xác nhận):**
1. *Dẫn dắt (cổng Bobby #2):* Qatar QSP ≤600 USD/t **hai tháng liền**, **và** DAP WB ≥700, **và** Hormuz theo chỉ báo #1 của Bobby. Khi đạt: cập nhật trọng số về ~Bear 20 / Base 45 / Bull 35 ⇒ EV ≈ **17.600** (NC 7.583) / **16.000** (NC stress) — cho phép vào ở mức **≤~14.000** (biên ~12–15% dưới EV có điều kiện), không phải ≤16.000.
2. *Xác nhận:* biên gộp quý **≥8% trên BCTC Q2/27 (≈ 20/07/2027)** (hoặc 2 quý liền biên tăng ≥3 điểm%), thay cho Q4/26–Q1/27.
3. Giữ điều kiện Đợt 1/Đợt 2 theo giá độc lập với catalyst (giá ≤12.000/≤10.500 không cần catalyst).

## 6. HARD ABANDON, %NAV, time stop (khung `calculated_fear_state_backstop.md` §3)

**Quy mô: tổng ≤ 2% NAV** (trần cho cả sleeve DDV), chia theo tranche, không dồn một lần:
- Đợt 1 (≤~12.000): ≤0,8% NAV · Đợt 2 (≤~10.500): ≤0,8% NAV · tranche catalyst (≤~14.000 sau cổng dẫn dắt): ≤0,4% NAV. Tổng tối đa 2,0% NAV.
- Thanh khoản UPCOM ~5–14 tỷ/ngày [DD cũ]; mỗi ngày không mua quá ~10% thanh khoản (≈0,5–1,4 tỷ) ⇒ dựng vị thế nhiều phiên. Quy ra % NAV tuyệt đối: chưa tính (không đọc NAV trong job này).

**HARD ABANDON — cắt bất kể giá (bất kỳ điều nào), cụ thể cho DDV:**
1. **Phải thu Liven Nutrients PTE (217,0 tỷ, 9,8% VCSH) không thu về hoặc bị trích lập** ở BCTC Q4/26 (≈ 20/01/27) — luận điểm "lõi còn tiền" gãy (tương ứng #2 backstop; net cash ~4.510 đ/cp nếu vẫn phải trả hết nợ nhà cung cấp).
2. **Net cash < 600 tỷ** (~4.100 đ/cp) trên BCTC quý (DD cũ đã đặt) **hoặc** DDV dùng tiền gửi cho đầu tư ngoài ngành / cho vay bên liên quan.
3. **Backstop Vinachem gãy:** Vinachem (64%) ép rút giá trị bất lợi cổ đông thiểu số (giá chuyển giao apatit, nhận tiền gửi nội bộ…) **hoặc** cổ tức đã hứa bị huỷ trong khi net cash còn >1 nghìn tỷ.
4. **Biên gộp quý âm hai quý liền ĐỒNG THỜI** QSP không giảm (≥800) — luận điểm chu kỳ gãy (DD cũ).
5. Đình chỉ/huỷ niêm yết thành hiện thực (UPCOM); scandal chuyển từ cá nhân sang pháp nhân/tài sản lõi (hiện chưa có: DD cũ §7 chỉ WARNING).
6. **Gián đoạn công suất do bãi thạch cao/môi trường** (đình chỉ nhà máy Đình Vũ) — nút thắt đã nêu ở DD cũ §7.

**Time stop:** không có catalyst xác nhận (biên gộp quý ≥8% **hoặc** QSP ≤600 hai tháng liền) trong **12 tháng từ ngày vào lệnh đầu tiên**, hoặc hết 18 tháng nếu giá tiếp tục lập đáy thấp hơn đáy đã vào ⇒ thoát toàn bộ (khung §3: recovery quan sát được đều gom trong 6–18 tháng). Mốc kiểm: BCTC Q4/26 (~20/01/27), Q1/27 (~20/04/27), **Q2/27 (~20/07/27, cổng xác nhận chính)**.

**Exit chốt lời:** giữ theo DD cũ — PB chuẩn hoá ~1,5–2,0x và dấu hiệu đỉnh chu kỳ (S về đáy, biên ≥17%); không chốt sớm +30–40%.

## 7. Điều mới cần theo dõi / giới hạn
- Giá S hợp đồng ME **tháng 11/2026** (SMM/Argus đầu T11) — cổng dẫn dắt #2; DDV: hỏi IR cơ cấu hợp đồng S/NH3 (giá trễ?) và mức tồn kho NVL theo loại.
- Bobby: **NH3** — TTF +63% từ T8; chuỗi NH3 không có trong BQ; chưa đo chi phí NH3 của DDV (DD cũ: NH3 +74% YoY theo VNDirect). Có thể kéo biên thấp hơn mô hình (mô hình chỉ gom NH3 vào độ dốc).
- Mô hình biên hai điểm (độ dốc 2,0–3,0) chưa kiểm out-of-sample; chưa gọi fundamental-skeptic (theo chỉ đạo job). **Khuyến nghị: gọi fundamental-skeptic trước khi cập nhật trading_rules/DD chính thức.**
- Bobby ghi rõ "không phải khuyến nghị mua/bán"; đây cũng vậy.
