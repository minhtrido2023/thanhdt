# Có dấu hiệu kỹ thuật nào báo trước đợt bật tăng 1–5 phiên? (18/11/2026)

Job `Taylor_20261118_122819` · PAPER-ONLY, không wire, không sửa production · PREREG `PREREG.md` md5 **ef70c866**, khoá
trước khi chạy · self-check **PASS** · **chưa qua quant-skeptic**.

## Kết luận
1. **NO-GO.** Không tín hiệu nào báo trước đợt tăng 1–5 phiên. Trong 24 tín hiệu × 2 ngưỡng = 48 trial, **0/48 có lãi sau
   phí** và **0/48 đạt "GO paper"**. Nhìn theo đợt tăng: tỉ lệ một tín hiệu xuất hiện trong T0−5..T0−1 của các đợt run-up
   **xấp xỉ** tỉ lệ nó xuất hiện trong một cửa sổ 5 phiên bất kỳ không có run-up. Ở ngưỡng 20%, tỉ số này là 0,39–1,18 cho
   cả 24 tín hiệu, tức không có dấu hiệu nào xuất hiện trước đợt tăng nhiều hơn rõ rệt so với lúc bình thường.
2. **Có 15 trial "có thông tin" (8 tín hiệu), nhưng đều là tín hiệu TRỄ, không phải báo trước.** Đó là ngày trần, gap-up,
   2 ngày trần trong 5 phiên, đột biến khối lượng 3–5×, phá đỉnh 52 tuần, khối lượng tăng/giảm, nhảy hạng thanh khoản. Chúng
   cho lift 1,6–4,6× (OOS, CI loại 1, qua BH-FDR, placebo p=0,005), nghĩa là đợt tăng **đã bắt đầu**. Mua theo chúng
   (vào mở cửa phiên sau, giữ 10 phiên) thì excess trung bình gộp −0,5…+0,9%, sau phí và slippage ÂM (−0,2% … −2,5%/lệnh).
   Khoảng 12% ngày trần không mua được vì phiên sau mở cửa trần.
3. **Các mẫu "nén chặt / base chặt / VCP" là phản tín hiệu.** Lift chỉ 0,21–0,71 so với base rate cùng thanh khoản: sau
   nền chặt, xác suất bật ≥20% THẤP hơn bình thường. Bộ tín hiệu VCP có trước T0 lặp lại ở **3.556 cụm OOS, chỉ 38 cụm
   chạy (1,1%)**.
4. Cảm giác "có rất nhiều trường hợp" là **đúng về số đếm nhưng sai về suy luận**. Mỗi năm có khoảng 480 đợt run-up ≥20%
   (3.275 đợt trong 6,8 năm OOS), nên ví dụ không bao giờ thiếu. Nhưng base rate chỉ 3,2% mã-ngày, và cứ mỗi mẫu "trông
   giống TV1/VCP trước khi chạy" thì có hàng chục mẫu y hệt mà không chạy. Ta nhớ mẫu chạy và quên các mẫu không chạy: đó là
   P(X | tăng) ≠ P(tăng | X).

## 1. Thiết kế (tóm tắt PREREG)
- **Universe**: `universe_pit` in_universe (TV1, VCP đều nằm trong). Dữ liệu `tav2_bq.ticker` (cache) tới 17/11. OHLC đã
  back-adjust cùng cơ sở với `Close`: đo 100% dòng thoả Low≤Close≤High ở 114.655 dòng có hệ số <0,9. Khối lượng dùng
  TV=Price×Volume. Không dùng `profit_*`/`PC1W..`/`Open_1D`.
- **Nhãn**: run-up = excess so với VNINDEX đạt ≥20% (hoặc ≥30%) trong 10 phiên tới. Đợt mới khi cách ngày run-up trước ≥20
  phiên. **N độc lập = 4.764 đợt (20%) / 1.975 đợt (30%)** giai đoạn 2014–11/2026. Mẫu chính bỏ các dòng đã tăng >15% trong 5
  phiên trước (chống đuổi giá, 23.997 dòng).
- **Lift chuẩn hoá** = số hit / số hit kỳ vọng theo base rate cùng năm × tercile ADV thực (mốc IS 2,17 / 11,37 tỷ). CI là
  block bootstrap theo tháng. IS 2014–19, OOS 2020+.
- **Giao dịch**: vào Open(t+1), ra Close(t+10), phí 0,1%/chiều, slippage/chiều 0,1–1,5% theo ADV (`ước lượng`, chốt trước).

## 2. Base rate (mẫu đủ điều kiện, `base_freq.csv`)
| | 2014–19 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|
| P(run-up ≥20% /10 phiên) | 1,9–4,2% | 4,5% | **7,7%** | 3,9% | 2,2% | 1,7% | 2,4% | 2,0% |
| Số đợt ≥20% | 183–336/năm | 424 | 862 | 826 | 344 | 267 | 347 | 205 |

## 3. Kết quả 48 trial (OOS 2020–11/2026; đầy đủ ở `results.csv`, hình `heatmap.png`)
| Tín hiệu (X=20%) | n dòng | Precision | Lift [CI95] | Lift IS | FP cụm/năm | Excess gộp | Excess ròng [CI] | Cap trung vị |
|---|---|---|---|---|---|---|---|---|
| S20 gap-up ≥2% giữ giá | 4.279 | 13,1% | **3,49** [2,55–4,89] | 3,62 | 459 | +0,9% | −0,4% [−2,2; +1,8] | 0,6 tỷ |
| S18 đóng trần hôm nay | 10.941 | 12,1% | **3,30** [2,71–4,10] | 4,23 | 1.015 | 0,0% | −1,0% [−2,1; +0,4] | 1,2 tỷ |
| S19 ≥2 trần/5 phiên | 4.965 | 12,5% | **3,21** [2,39–4,36] | 5,74 | 235 | +0,8% | −0,2% [−1,7; +1,4] | 1,2 tỷ |
| S08 đột biến TV ≥5× | 3.851 | 7,1% | 2,11 [1,75–2,52] | 1,64 | 448 | +0,1% | −1,8% [−2,5; −1,0] | 0,2 tỷ |
| S15 phá đỉnh 52 tuần + vol | 4.878 | 7,5% | 1,87 [1,59–2,23] | 2,47 | 413 | +0,5% | −0,4% [−1,2; +0,4] | 1,7 tỷ |
| S07 đột biến TV ≥3× | 13.469 | 6,3% | 1,87 [1,63–2,13] | 1,79 | 1.313 | +0,1% | −1,5% [−2,2; −0,9] | 0,3 tỷ |
| S21 nhảy hạng thanh khoản | 4.574 | 6,1% | 1,71 [1,44–2,01] | 1,66 | 410 | −0,5% | −2,5% [−3,1; −1,8] | 0,2 tỷ |
| S11 vol tăng/giảm ≥2 (X=30%) | 116.828 | 1,9% | 1,57 [1,31–1,84] | 1,54 | 1.584 | +0,6% | −0,8% [−1,3; −0,2] | 0,6 tỷ |
| S04 nền chặt 20 phiên ≤10% | 131.501 | 0,8% | **0,30** [0,25–0,35] | 0,30 | 989 | 0,0% | −1,8% | 0,3 tỷ |
| S05 VCP co hẹp dần | 35.760 | 1,0% | **0,34** [0,27–0,42] | 0,41 | 976 | +0,3% | −1,2% | 0,4 tỷ |
| S01 ATR% thấp nhất 10% | 91.246 | 1,9% | **0,70** [0,57–0,83] | 0,69 | 1.038 | 0,0% | −1,6% | 0,3 tỷ |
| S06 cạn cung | 89.663 | 2,6% | 0,86 [0,60–1,17] | 0,86 | 787 | −0,3% | −2,4% | 0,1 tỷ |
| S09 cạn cung → đột biến | 1.865 | 4,3% | 1,41 [0,97–1,86] | 1,65 | 218 | −0,4% | −2,7% | 0,1 tỷ |
Base rate OOS: 3,2% (X=20%), 1,1% (X=30%). Tổng hợp cổng: G1 17/48 · BH 21/48 · LOYO 18/48 · "có thông tin" **15/48** ·
**lãi ròng 0/48** · DSR max 0,00 · **GO 0/48**. 18/48 trial có MDE >1,5, tức không đủ sức kiểm định, chủ yếu combo và X=30%.

**Vì sao "có thông tin" mà không kiếm được tiền (post-hoc, `posthoc_vol.csv`, KHÔNG tiền-đăng-ký):**
- Các tín hiệu trần/gap tăng **cả hai đuôi**. Lift chiều xuống (excess ≤−20%) của chúng là 1,37–2,60.
- Khi chuẩn hoá theo biến động 20 phiên thay vì theo thanh khoản, lift trần/gap giảm từ 3,2–3,5 xuống 1,8–2,2.
- Phân phối lợi nhuận kiểu xổ số: excess gộp trung vị −0,6% … −1,6%, trung bình ≈0.
- Riêng đột biến khối lượng S07/S08 lệch về chiều lên (lift lên ~2, lift xuống ~1,0), nhưng chỉ có ở mã nhỏ (capacity
  0,2–0,3 tỷ) và vẫn âm sau phí.

## 4. Hai chiều (`event_view.csv`, X=20%, 3.275 đợt OOS)
| | P(X trong T0−5..T0−1 | tăng) | P(X | cửa sổ không tăng) | Tỉ số |
|---|---|---|---|
| Tốt nhất: S06 cạn cung | 20,1% | 17,0% | 1,18 |
| S07 đột biến ≥3× | 9,4% | 9,6% | 0,98 |
| S18 ngày trần | 7,3% | 8,0% | 0,91 |
| S04 nền chặt | 9,3% | 23,9% | 0,39 |
Tại chính T0, mọi tỉ số đều <1,2. Ở X=30%, tỉ số cao nhất là 1,64 (S20 gap-up, nhưng chỉ 6,6% số đợt có nó, so với 4,0% ở cửa sổ không tăng). Các tín hiệu "có thông tin" ở §3 chỉ bật **sau** T0, khi đợt tăng đang diễn ra.

## 5. Bối cảnh (mô tả, `strata.csv`)
Lift của tín hiệu trần/gap thấp nhất khi DT5G = BEAR (1,7–2,0) và cao nhất khi CRISIS (4,3–4,9). Theo breadth thì không có
khác biệt rõ. Khi chỉ giữ mã có ADV ≥10 tỷ (capacity ≥1 tỷ), lift vẫn tương đương (3,0–3,5 cho S18/S19/S20), nhưng excess
ròng vẫn không dương.

## 6. Case study (sau kết quả toàn universe, `case_study.md`)
- **VCP** (T0 = 19/10; nhảy +13,3% ngày 26/10, T0+5): suốt T0−10..T0 chỉ bật các tín hiệu NÉN (S01, S02, S04, có lúc S03/S05),
  với TV 0,03–0,6 tỷ/phiên. Đây đúng là nhóm phản tín hiệu ở §3. Chỉ đến chính ngày 26/10 mới bật S07/S08/S18 (trễ). Trước đó
  không có đột biến khối lượng nào. Capacity 10% ADV: khoảng 0,02–0,05 tỷ, tức không vào được quy mô có ý nghĩa.
- **TV1** (T0 = 29/10): T0−10..T0 có S11 (vol tăng/giảm) liên tục, S06 cạn cung (15/10, 23/10), S03 (27/10), S17 (28/10).
  Cùng bộ đó ở OOS: **611 cụm, 7 cụm chạy (1,1%), 604 cụm không chạy**. Đột biến khối lượng (S07/S08) chỉ bật ngày 05/11, sau
  khi giá đã rời nền.
- **Catalyst**: `ticker_financial` ghi Release_Date BCTC Q3/2026 của cả hai mã là **02/11**. Đợt +14% của TV1 ngày 12/11 nằm
  SAU mốc đó. Ngày 08/10 TV1 có tin sáp nhập công ty con. `stock_news` (PARTIAL) chỉ phủ tới 16/10, nên **không xác định được
  tin tại T0**. Không gán công cho kỹ thuật, cũng không loại trừ.

## 7. Câu hỏi đối xứng: dấu hiệu kết thúc đợt (mô tả, `climax.csv`)
Xét các dòng đang trong đợt tăng (C/min 20 phiên ≥+30%, n=33.834 OOS). Nhãn là excess giảm ≤−15% trong 10 phiên, base 11,6%.
| Cờ | P(giảm) OOS | Lift |
|---|---|---|
| K2 C/MA20 ≥+25% | 20,7% [16,9–24,5] | 1,78 |
| K3 ≥5/6 phiên tăng, +20%/6 phiên | 16,4% | 1,41 |
| K1 vol đỉnh 60 phiên + nến đóng thấp | 15,8% [9,7–22,4] | 1,35 (CI chứa base) |
| K4 ngày sàn (đã là trễ) | 30,9% | 2,65 |
**VCP** bật K2+K3 liên tục từ 10/11 đến 17/11 (C/MA20 +35…+48%). Ngày 18/11 (theo số Mike gửi, cache chưa có) giảm −15,5% so
với 44.000, tức chạm sàn UPCoM (K4). **TV1** đến 17/11 chưa bật cờ nào (C/MA20 +23%). Ngay cả với K2, khoảng 79% trường hợp KHÔNG
giảm ≥15% trong 10 phiên. Đây chỉ là mô tả, không phải khuyến nghị bán.

## 8. Hạn chế
- Cache không có cột sàn giao dịch, nên biên độ trần được suy causal. VCP bị coi là HOSE 7% cho tới 26/10, do 250 phiên trước
  đó chưa tăng quá 7,5%. Sai lệch này chỉ ảnh hưởng S18/S19.
- Excess giao dịch đo stock từ Open(t+1) nhưng VNI từ Close(t).
- Slippage là `ước lượng`.
- Control leg: 300.454 so với 300.438 pin của job 14/11. Chênh 54 dòng, ở 3 mã, do cache được làm mới (`control_leg.json`).
- Chưa qua quant-skeptic.

## 9. Đề xuất
Đóng hướng "tín hiệu kỹ thuật báo trước run-up" vào `ta-schools-vn` NO-GO, cùng nhánh với phân kỳ RSI 14/11. Không đề xuất
thử nghiệm paper, vì không trial nào qua cổng GO. Phần đáng giữ:
- (a) Base rate thật: khoảng 480 đợt/năm, 3,2% mã-ngày.
- (b) "Nền chặt" là phản tín hiệu.
- (c) Ngày trần/gap/đột biến khối lượng có thông tin về **biến động sắp tới** (cả hai chiều), không phải chiều đi. Nếu cần,
  có thể dùng làm cờ rủi ro/độ biến động cho sizing. Đó là câu hỏi khác và cần PREREG riêng.

Tệp: `PREREG.md(.md5)` · `lib.py engine.py analyze.py selfcheck.py case.py posthoc_vol.py` · `results.csv` (md5 f50e2695) ·
`results_unfiltered.csv event_view.csv base_freq.csv strata.csv climax.csv posthoc_vol.csv` · `case_study.md case_news.csv` ·
`heatmap.png` · `selfcheck.json control_leg.json` · `RESULTS.md5`.
