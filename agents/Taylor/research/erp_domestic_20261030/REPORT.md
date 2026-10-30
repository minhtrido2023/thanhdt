# ERP nội địa cho DCF của fleet: chọn ERP nào khi không cộng rủi ro quốc gia?
Job `Taylor_20261030_034654` · 30/10/2026 · chỉ nghiên cứu (không wire, không sửa code production, không đặt lệnh).
PREREG `f4a6cce0c` (commit trước khi tính số) · tất định ở 2 múi giờ, tái lập DGC lệch 0 đồng — xem `SELFCHECK.md`.
Số liệu: `run_stdout.txt` và `out_*.csv`. Nhãn: [BQ] đo trong phiên từ BigQuery (cache `data/`), [SRC] có nguồn, [UL] ước lượng.

## Kết luận trước

1. **ERP nội địa (so với rf VND chuẩn hoá 6,75%): trung tâm 5,0%, dải 3,4–6,5%.** Đây là kết quả của luật PREREG
   (trung vị của bốn ước lượng nội địa D1–D4, xem mục 4). Damodaran không nằm trong trung vị. Sàn 4,23% (ERP thị trường trưởng thành) không bị chạm.
   - **Ke vùng (rf 6,75 + β × ERP):**
     - β 1,0: **11,8%** (10,1–13,3)
     - β 1,1: **12,3%** (10,5–14,0)
     - β 1,2: **12,8%** (10,8–14,6)
   - Ke 15,8% của nghiên cứu 29/10 (Damodaran 8,13%) nằm **trên** đầu cao của dải nội địa. Nên dán nhãn nó là "góc nhìn nước ngoài, USD".
2. **User đúng ở (1) và (2). Ở (3), user đúng một nửa.**
   - (1) CRP: đúng như user nói. Xem lập luận ở mục 6.
   - (2) Phép thử "justify" xác nhận: ở Ke 15%, **78%** mã phi ngân hàng có PE cao hơn PE hàm ý, và **64%** cao gấp hơn 1,5 lần (`out_justify_grid.csv`).
   - (3) PE VNINDEX **không** bị méo ở cấp tổng hợp. E/P tính bằng tổng lợi nhuận / tổng vốn hoá trên universe_pit gần như trùng PE chính thức: chênh trung vị **−0,05pp** qua 52 quý 2014–2026.
     Phần méo thật nằm ở **trọng số**:
     - Trung vị E/P cao hơn PE chính thức **+1,32pp** (trung vị lịch sử; hôm nay +0,69pp).
     - Bỏ top-10 vốn hoá: **+0,73pp** (hôm nay +1,07pp).
     - Nhưng bỏ ngân hàng làm thị trường **đắt hơn** (E/P 8,35 → 6,83). Ngân hàng là nhóm rẻ, nên chúng kéo PE chính thức xuống chứ không đẩy lên.
3. **Không có Ke nào hợp lý làm "đa số mã justify được giá".** Theo công thức value-driver (dùng ROE5Y, g 5,5%), mức Ke làm 50% số mã phi ngân hàng hợp giá là **≈9,3%**
   (trung vị ICC; trọng số vốn hoá 9,75%). Mức này thấp hơn sàn rf + ERP trưởng thành = 10,98%.
   - Vậy phép thử chỉ cho được **cận trên**: Ke ≥ 15% là lệch.
   - Phép thử **không** chốt được điểm trung tâm. Một lý do là thị trường đang định giá ROE tương lai cao hơn ROE5Y 10,7% (trung vị). Đây là chỗ vòng tròn: xem mục 5.
4. **DGC tầng A ở Ke trung tâm 12,35% (β 1,11):**
   - DCF **24.044 / 37.324 / 48.024**, so với gốc 21.407 / 32.925 / 41.779 (tái lập lệch 0 đồng).
   - EV blend **31.724**, so với 29.817 (+1.907 đ/cp, +6,4%).
   - Cả dải ERP (Ke 10,5–14,0%) cho EV 33.896–30.385.
5. **Đổi Ke trong `dcf_valuation.py` mà không đổi g_T là nguy hiểm.**
   - Hôm nay: r = 7,4 + 6,5 = 13,9% và g_T = min(CPI + GDP thực, rf = lãi huy động) = 7,4%, nên r − g = 6,5pp.
   - Nếu chỉ thay r = 6,75 + 5,05 = 11,8% và g_T vẫn bị cắt ở rf 6,75%: r − g = 5,05pp. Bội số terminal tăng từ 15,4× lên 19,8× (**+29%**, tính tay).
   - Nếu đổi đồng thời g_T = π + 1,25 = 5,5%: r − g = 6,3pp, bội số 15,9× (+3%).
   - **Phải đổi cả hai cùng lúc**, xem mục 7.

## Điểm yếu của chính nghiên cứu (hai chiều)

**Có thể đang làm ERP THẤP quá:**
- D1 (value-driver) dùng ROE5Y trung vị 10,7%. Nếu ROE tương lai cao hơn ROE5Y (chưa đo), Ke ngầm định sẽ cao hơn. D1 = 3,38 là số thấp nhất và kéo trung vị xuống.
- Chân lịch sử theo lãi huy động chỉ có từ 2011 (`deposit_rate_vn` không có 2008–2010). Nếu tính từ 2008 thì có thêm cú sụp 2008: chân TPCP 2008→ cho ERP hình học **−0,3%**, bỏ tái định giá 4,0%.
- Big-4 12M thấp hơn lãi mà nhà đầu tư cá nhân thực nhận (CCTG 7,4%). Phần này tác động lên ERP-so-với-lãi-huy-động, nhưng phép quy về rf_c (mục 4) bù lại phần lớn.

**Có thể đang làm ERP CAO quá:**
- D2 (E/P + π) giả định RONIC = Ke. Với ROE trung vị 10,7% < Ke, giả định này lạc quan, nên D2 = 6,54 có thể cao.
- D4 (2014→) bắt đầu sau khủng hoảng 2011–13, rơi vào 12 năm thuận lợi.
- Cửa sổ 2016-07→ cho ERP bỏ tái định giá **7,15%**. Nếu dùng cửa sổ này cho D3 (đúng như PREREG dự kiến trong ngoặc), trung tâm thành **6,08%** (Ke β 1,1 = 13,4%).
  **Chỉ riêng lựa chọn cửa sổ đã làm điểm trung tâm dịch khoảng 1pp.**

**Bất định chung:**
- Bootstrap khối, CI 90% của ERP số học: 2011→ **−2,1…13,1%**; 2014→ **0,1…16,0%** (`out_erp_history.csv`). Lịch sử VN quá ngắn để chốt ERP chính xác hơn ±5pp. N độc lập ≈ 12–16 năm.
- Chuỗi TPCP 10Y theo năm có **9/16 điểm chưa kiểm chứng** (trí nhớ mô hình). 2008 và 2010 là [UL]; 2009 = 9,7% [SRC VietnamPlus]. Mọi số ở chân TPCP vì thế chỉ là minh hoạ.
- Cổ tức trước 2014 = 3,69%/năm, ngoại suy từ TB 2014–16 [UL]. Kiểm ±1pp: ERP 2011→ dịch ±0,19pp.
- Bốn ước lượng D1–D4 có thiên lệch khác nhau. Trung vị của chúng là quy ước, không phải ước lượng tối ưu.
- Lệch PREREG: VNINDEX_PE trên BQ **có từ 2007-12-03** (đã backfill; trước đây NULL trước 2016-07). Vì vậy "cửa sổ dài nhất đo được" của D3 là **2011→** chứ không phải 2016-07→ như PREREG dự kiến. Điều này được báo, và độ nhạy đã nêu ở trên.

## 1. E/P robust với vốn hoá lớn (asof 29/10/2026, universe_pit 336 mã, 334 có PE, 16 mã lỗ) [BQ]

| Ước lượng | N | E/P % | PE tương đương | Ke M-a (E/P + π 4,25) | Ke M-b (value-driver, g 5,5) | ERP M-a | ERP M-b |
|---|---|---|---|---|---|---|---|
| E1 VNINDEX_PE chính thức | — | 8,35 | 11,97 | 12,60 | 9,77 | 5,85 | 3,02 |
| E2 aggregate Σlãi/Σvốn hoá | 334 | 8,29 | 12,06 | 12,54 | 9,74 | 5,79 | 2,99 |
| E3 equal-weight mean (winsor 1%) | 334 | 10,07 | 9,93 | 14,32 | 10,66 | 7,57 | 3,91 |
| E4 trung vị | 334 | 9,04 | 11,06 | 13,29 | 10,13 | 6,54 | 3,38 |
| E5 aggregate bỏ top-5 | 329 | 9,37 | 10,67 | 13,62 | 10,25 | 6,87 | 3,50 |
| E6 aggregate bỏ top-10 | 324 | 9,42 | 10,61 | 13,67 | 10,16 | 6,92 | 3,41 |
| E7 bỏ ngân hàng | 310 | 6,83 | 14,65 | 11,08 | 8,71 | 4,33 | 1,96 |
| E8 bỏ BĐS | 280 | 9,74 | 10,27 | 13,99 | 10,88 | 7,24 | 4,13 |
| E9 bỏ NH + BĐS | 256 | 8,15 | 12,28 | 12,40 | 9,67 | 5,65 | 2,92 |
| E10 trung vị bỏ NH + BĐS | 256 | 9,18 | 10,89 | 13,43 | 10,20 | 6,68 | 3,45 |

- Top-10 vốn hoá (VIC, VHM, VCB, BID, CTG, VGI, VPB, MBB, GAS, MCH) chiếm **47,5%** vốn hoá rổ nhưng chỉ **40,3%** lợi nhuận.
  PE tổng hợp top-10 = **14,2** so với phần còn lại **10,6** [BQ]. Phần đắt nằm ở nhóm phi ngân hàng của top-10 (PE tổng hợp 22,3; VIC 87,8, MCH 24,7, VGI 18,9);
  5 ngân hàng top-10 có PE tổng hợp chỉ 8,0.
- **Độ chênh giữa các cách tính:** E/P 6,83–10,07% (3,2pp). Tập robust {E2, E4, E6, E9, E10} hẹp hơn nhiều: 8,15–9,42% (1,3pp).
- Lịch sử quý 2014Q1–2026-10 (`out_ep_history_quarterly.csv`), chênh so với E1:

  | Ước lượng | Trung vị | Khoảng |
  |---|---|---|
  | E2 | −0,05pp | −0,86…+0,87 |
  | E4 | +1,32pp | −2,46…+4,83 |
  | E6 | +0,73pp | −1,19…+3,54 |
  | E9 | −0,21pp | −3,17…+2,50 |

  ⇒ PE chính thức ≈ PE tổng hợp. "Méo do vốn hoá lớn" có thật nhưng nhỏ (≈0,7–1,3pp E/P) và đổi dấu theo thời kỳ.
- **M-a và M-b khác nhau khoảng 3pp Ke.** Đây là bất định lớn nhất của cách tiếp cận ngầm định, lớn hơn mọi khác biệt giữa các rổ.
  - M-a giả định tăng trưởng không tạo giá trị (RONIC = Ke).
  - M-b phạt tăng trưởng vì ROE 10,7% < Ke.

**D1** (M-b, trung vị tập robust) = **3,38** · **D2** (M-a) = **6,54**.

## 2. ERP thực nghiệm lịch sử (`out_erp_history.csv`)
TR = `vnindex_tr_daily.csv` `tr_gross` từ 2013-12-31 [BQ, CANONICAL]. Trước đó dùng chỉ số giá [BQ] cộng cổ tức 3,69%/năm [UL].
Chân rf:
- Big-4 12M: cộng dồn theo ngày, từ 2011.
- TPCP 10Y: lợi suất TB năm, giữ đến hạn ≈ lợi suất lúc mua; đây không phải TR trái phiếu, và chuỗi chưa kiểm chứng.

| Cửa sổ | Chân rf | TR CAGR | rf TB | ERP hình học | ERP số học | Tái định giá/năm | ERP bỏ tái định giá | CI 90% (số học) |
|---|---|---|---|---|---|---|---|---|
| 2008→ | TPCP | 6,33 | 6,64 | −0,29 | 3,47 | −4,25 | 3,96 | −6,3…12,4 |
| 2011→ | Big-4 | 11,25 | 7,24 | 3,73 | 5,51 | −0,25 | **3,98** | −2,1…13,1 |
| 2011→ | TPCP | 11,25 | 5,77 | 5,18 | 6,90 | −0,25 | 5,42 | −0,6…14,5 |
| 2014→ | Big-4 | 12,75 | 6,18 | **6,19** | 8,04 | −0,50 | 6,69 | 0,1…16,0 |
| 2014→ | TPCP | 12,75 | 4,58 | 7,82 | 9,56 | −0,50 | 8,31 | 1,7…17,5 |
| 2016-07→ | Big-4 | 12,44 | 6,19 | 5,89 | 7,83 | −1,83 | 7,72 | −1,8…17,4 |
| 2008–2013 | TPCP | −6,22 | 11,19 | −15,66 | −9,76 | −12,29 | −3,36 | — |
| 2014–2019 | Big-4 | 14,71 | 6,53 | 7,67 | 8,71 | +3,46 | 4,22 | — |
| 2020–2026 | Big-4 | 11,07 | 5,87 | 4,91 | 7,46 | −3,97 | 8,88 | — |

**Cảnh báo chế độ:**
- 2008–13 là khủng hoảng tín dụng/lạm phát, lãi huy động 12–14% và TPCP > 10%. Thời kỳ này cho ERP âm sâu.
- 2020–26 là thời kỳ kìm lãi suất: TPCP 2–4% thấp hơn cả lãi huy động. Vì vậy chân TPCP thổi phồng ERP khoảng 1,5–3pp so với chân lãi huy động cùng kỳ.
- "Bỏ tái định giá" = ERP − ln(PE cuối/PE đầu)/năm. Số này loại phần PE co giãn nhưng giữ lại tăng trưởng lợi nhuận thực hiện. 2020–26 cao (8,9) vì lợi nhuận tăng mạnh trong khi PE co lại.

**D3** (2011→, bỏ tái định giá, quy về rf_c) = 3,98 + (7,24 − 6,75) = **4,47** · **D4** (2014→) = 6,19 + (6,18 − 6,75) = **5,62**.
Độ nhạy (không vào luật): D3 ở cửa sổ 2016-07→ = **7,15**.

## 3. Khung proxy vĩ mô cho rf (`out_rf_proxies.csv`)

| Proxy | % | Nguồn |
|---|---|---|
| Building-block (π mục tiêu 4,0–4,5 + lãi thực 2–3) | 6,00 / **6,75** / 7,50 | [UL], thừa kế 29/10 |
| TPCP 10Y hiện tại | 4,47 | [SRC] ADB 28/10/2026 |
| TPCP 10Y TB 2016–25 | 3,95 | 9/16 điểm chưa kiểm chứng |
| Big-4 12M hôm nay / TB 10 năm / TB 2011→ | 6,80 / 6,01 / 6,99 | `deposit_rate_vn` (mốc neo có hindsight) |
| CCTG 12M | 7,40 | `cctg_rate_vn` 2026-10-12 |
| NHNN TB huy động kỳ hạn >12T, 08/2026 thấp/cao | 6,10 / 7,60 | [SRC-PIT] FiinPro snapshot |
| Lãi cho vay TB | 8,3–10,7 | [SRC thứ cấp] [VNF 21/09/2026](https://vietnamfinance.vn/lai-suat-cho-vay-trung-binh-len-107-nam-thuc-te-khach-vay-cham-dinh-18-d150849.html): TB 08/2026 10,7%; nhóm NHTM 8,3–10,5% (07/2026) |

- **rf_c 6,75 nằm giữa TPCP 10Y (4,47) và lãi cho vay (8,3–10,7): ĐẠT.** rf_c cũng sát lãi huy động dài hạn NHNN (6,1–7,6) và TB Big-4 15 năm (6,99).
- Lãi cho vay là mốc **trần tự nhiên của chi phí nợ**. Ke ở β 1,0 = 11,8% cao hơn lãi vay TB 10,7% khoảng 1,1pp. Ke < lãi vay sẽ vô lý, nên ràng buộc này cho **sàn mềm Ke ≈ 11%** với β 1.

## 4. Luật chọn ERP (PREREG §4) → `out_erp_choice.csv`

| | D1 ngầm định M-b | D2 ngầm định M-a | D3 lịch sử bỏ tái định giá 2011→ | D4 lịch sử 2014→ | **Trung vị** | Dải |
|---|---|---|---|---|---|---|
| ERP so với rf_c 6,75 | 3,38 | 6,54 | 4,47 | 5,62 | **5,05** | 3,38–6,54 |

So với các mốc tham chiếu: sàn Damodaran trưởng thành 4,23 không chạm; Damodaran tổng 8,13 nằm ngoài dải (trên).

## 5. Phép thử "justify" (`out_justify_grid.csv`, `out_icc.csv`)
Rổ: 294 mã phi ngân hàng có PE > 0, cộng 24 ngân hàng xếp riêng. PE hàm ý = (1 − g/ROE5Y)(1+g)/(Ke − g), g = 5,5%.

| Ke | % mã đắt (đếm) | % vốn hoá đắt | % đắt > 1,5× | PE hàm ý trung vị |
|---|---|---|---|---|
| 9,5 | 52,0 | 58,8 | 39,5 | 12,8 |
| 11,0 | 60,9 | 70,4 | 48,3 | 9,3 |
| 12,0 | 65,6 | 72,3 | 53,4 | 7,9 |
| 12,5 | 68,0 | 74,0 | 55,1 | 7,3 |
| 14,0 | 74,8 | 80,9 | 60,9 | 6,0 |
| 15,0 | **78,2** | 84,9 | **64,3** | 5,4 |
| 16,0 | 81,3 | 87,7 | 68,0 | 4,9 |

**Kết quả theo nhóm:**
- **Ngân hàng** (N = 24): ở Ke 13% có 33% mã đắt; ở 15% có 54%. Ngân hàng "justify" được tới Ke ≈ 14,5%.
- **Phi ngân hàng:** ICC trung vị là **9,29%** (IQR 6,95–14,01; g 4,25 → 9,18; g 6,75 → 9,77).

**Cách đọc đúng:**
- **Vòng tròn.** ICC giả định giá thị trường đúng, nên chỉ dùng để **hiệu chỉnh vùng** Ke, không dùng để kết luận rẻ hay đắt.
- Kết quả "đa số mã đắt ở mọi Ke ≥ 11%" có hai cách giải thích, và dữ liệu ở đây **không phân biệt được** hai cách này:
  - (a) Thị trường kỳ vọng ROE tương lai cao hơn ROE5Y, hoặc lợi nhuận trailing đang ở đáy.
  - (b) Thị trường đắt so với nền tảng quá khứ.
- **Điều chắc chắn:** Ke ≥ 15% áp đồng loạt làm gần 4/5 số mã "đắt" và 2/3 "đắt vô lý". Đó là dấu hiệu Ke lệch, đúng như user nghi.
- **Điều không chắc chắn:** không thể hạ Ke tới mức ICC 9,3%. Mức đó dưới sàn rf + ERP trưởng thành (10,98%) và dưới lãi vay TB.

## 6. Đề xuất

- **ERP nội địa: trung tâm 5,0%, dải 3,4–6,5%.** Báo kèm độ nhạy cửa sổ: 6,1% nếu D3 lấy 2016-07→.
  Đề xuất **làm tròn quy ước fleet thành 5,0%**, với β 1,0 → Ke 11,8%.
- **Ke vùng (rf 6,75):**

  | β | Thấp | Trung tâm | Cao |
  |---|---|---|---|
  | 1,0 | 10,1 | **11,8** | 13,3 |
  | 1,1 | 10,5 | **12,3** | 14,0 |
  | 1,2 | 10,8 | **12,8** | 14,6 |

  Ba mốc đọc nên báo:
  - Trung tâm nội địa 12,3% (β 1,1).
  - Đầu cao nội địa 14,0%.
  - "Góc nhìn nước ngoài" 15,8% (Damodaran), chỉ để tham chiếu.
- **CRP — phần nào còn đáng giữ:**
  - (i) Rủi ro tiền tệ/lạm phát đã nằm trong rf VND: π mục tiêu 4,25 cộng lãi thực 2,5 (kiểm chéo 29/10: rf theo chênh lệch lạm phát với UST = 6,97).
  - (ii) Phần biến động/thanh khoản/quản trị mà NĐT nội chịu đã nằm trong **ERP đo ở VN** (D1–D4). Cộng thêm CRP là tính đôi.
  - (iii) Rủi ro **đặc thù** (pháp lý như vụ án DGC, chính sách, xuất khẩu) phải vào **dòng tiền/kịch bản/xác suất** hoặc g, **không vào Ke**. Nếu đưa vào Ke, chiết khấu sẽ tăng vô hạn theo thời gian cho một rủi ro thường là một lần.
  - (iv) Nhà đầu tư USD (khối ngoại) vẫn dùng Ke 15,8%. Chênh khoảng 3,5pp này là một lý do cấu trúc khiến khối ngoại thường thấy VN "không rẻ".
- **Ràng buộc đi kèm (bắt buộc khi hạ Ke):**
  - g_T ≤ π + tăng trưởng thực có pha loãng: khoảng **5–5,5%**, không phải rf 6,75.
  - RONIC ≥ Ke thì mới cho g cộng giá trị.
  - Không nâng g đồng thời.
  - Ke(β 1) ≥ lãi vay TB khoảng 10,7%.

## 7. DGC + ảnh hưởng tới code (chỉ liệt kê, KHÔNG sửa)

**DGC tầng A r7** (`out_dgc_ke.csv`; tái lập 21.407 / 32.925 / 41.779 / EV 29.817, lệch 0 đồng):

| Ke | DCF nghịch / cơ sở / thuận | EV blend |
|---|---|---|
| 14,90 (r7 hiện hành) | 21.407 / 32.925 / 41.779 | 29.817 |
| 10,50 (ERP thấp, β 1,11) | 27.068 / 42.368 / 55.186 | 33.896 |
| **12,35 (trung tâm, β 1,11)** | **24.044 / 37.324 / 48.024** | **31.724** |
| 14,01 (ERP cao, β 1,11) | 22.190 / 34.231 / 43.633 | 30.385 |
| 15,77 (Damodaran, nước ngoài) | 20.746 / 31.823 / 40.213 | 29.336 |

**Cảnh báo DGC:**
- Ở Ke 12,35%, RONIC 12% [UL] của r7 ≈ Ke, nên g = 3% gần như trung tính. Không được nâng g.
- Dải EV do Ke (33.896 − 30.385 = 3.511 đ/cp) vẫn nhỏ hơn bất định dự phòng R1/R2 (6.065).
- **Ke vẫn không phải biến quyết định cho DGC.**

**Code và consumer bị ảnh hưởng nếu user duyệt** (grep 30/10, bỏ worktree/research/selfcheck):
- `dcf_valuation.py`:
  - `ERP = 6.5` hiện đo **so với lãi huy động** (7,4) ⇒ r 13,9%.
  - Đề xuất là đổi **cả hai chân** thành rf_c 6,75 + 5,0 = 11,75%.
  - Đổi `terminal_growth_mode("cap_rf")` từ min(CPI + GDP, lãi huy động) sang cận ~5,5%. Nếu chỉ đổi r, bội số terminal +29% (mục kết luận 5).
  - `discount_rate()` hiện ghép lãi huy động hôm nay. Khung mới tách r (dài hạn, ổn định) khỏi `consumer_deposit_rate()` (chi phí cơ hội ngắn hạn, GIỮ cho rating_8l/custom30).
- Consumer trực tiếp của `fair_value`/`classify_dcf`/`ERP`:
  - `trading_bot/strategies.py` (dòng 54–56, `fair_value`): **đường tiền, cần review riêng**.
  - `custom_basket.py` (`fair_value` + `classify_dcf`: nhãn custom30V).
  - `dcf_refresh_gate.py` (đọc ERP/chân deposit để tính delta).
  - `sector_lens_monitor.py`, `alt_valuation_lens.py`, `converge_report.py`, `dcf_fv_sens_cache.py`, `alphalens_report.py`, `dc_book_waterfall_paper.py`.
  - `mike/bin/sector_valuation_lens.py` (lens "DCF (dcf_valuation)").
  - `mike/bin/eod_trading_report.sh` (chỉ `DCF_DISCLAIMER`).
  - Nghiên cứu: `dcf_backtest.py`, `dcf_rate_robustness.py`, `dcf_earning_power.py`.
  - Nhắc lại từ 07/2026: IC margin-of-safety phẳng theo mức g_T, vì đổi mức đồng loạt ít đổi xếp hạng. Còn **ngưỡng tuyệt đối** "rẻ/đắt" (%cheap của universe, nhãn custom30V) thì **sẽ đổi**. **Chưa đo.**
- Skill `due-diligence` SKILL.md dòng 30: thay "trung tâm Ke quanh 13,1–14,9%" bằng vùng mục 6. Giữ 15,8% là nhãn nước ngoài.
- DD đã phát hành (DGC r12/investor report v2, DRI v3): không tự đổi. DRI dùng khung thực có thời hạn, nên không thuộc phạm vi.

## Nguồn
- BQ: `tav2_mike.universe_pit`, `tav2_bq.ticker` (cache `data/snap_universe_pit_qe.csv`, `data/vnindex_daily.csv`).
- `data/benchmark/vnindex_tr_daily.csv` (copy `data/`).
- `deposit_rate_vn.py`, `cctg_rate_vn.py`.
- FiinPro snapshot NHNN 2011–2026.
- Damodaran ctryprem 01/2026.
- ADB AsianBondsOnline 28/10/2026.
- VietnamPlus 26/09/2019 (TPCP 2009 9,7%).
- VNF 21/09/2026 (lãi cho vay).
- Nghiên cứu 29/10 `../dgc_discount_rate_20261029/`.
